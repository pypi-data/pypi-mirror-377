from pyspark.sql import functions as f
from pyspark.sql.types import StringType
from cryptography.fernet import Fernet
import random
import json


class Data_masking:
    def __init__(self, gooddf, config, spark1):
        self.gooddf = gooddf
        self.config = config
        self.schema = self.config["schema"]
        self.spark = spark1
        self.sc = self.spark.sparkContext
        self.FNT_ID = self.config["file_read_configs"]["FNT_Id"]
        self.schema_df = self.spark.read.json(
            self.sc.parallelize([json.dumps(self.schema)])
        )
        self.dbutils = self.get_dbutils()

        self.mask_func1 = f.udf(Data_masking.mask_token_func, StringType())
        self.mask_encrypt = f.udf(Data_masking.mask_encrypt_func, StringType())
        self.mask_scrumble = f.udf(Data_masking.mask_scrumbling, StringType())

    def get_dbutils(self):
        try:
            from pyspark.dbutils import DBUtils

            dbutils = DBUtils(self.spark)
        except ImportError:
            import IPython

            dbutils = IPython.get_ipython().user_ns["dbutils"]
        return dbutils

    @staticmethod
    def mask_token_func(colVal):
        charList = list(colVal)
        charList[2:8] = "x" * 6
        return "".join(charList)

    @staticmethod
    def mask_encrypt_func(clear_text, MASTER_KEY):
        f = Fernet(MASTER_KEY)
        clear_text_b = bytes(clear_text, "utf-8")
        cipher_text = f.encrypt(clear_text_b)
        cipher_text = str(cipher_text.decode("ascii"))
        return cipher_text

    @staticmethod
    def mask_scrumbling(colval):
        strlist = list(colval)
        random.shuffle(strlist)
        return "".join(strlist)

    def data_mask(self):
        
        mask_dict = (
            self.schema_df.filter("Is_Maskable=1")
            .select("Expected_Columnname", "Mask_value")
            .rdd.collectAsMap()
        )
        column = (
            self.schema_df.filter("Is_Maskable=1")
            .select("Expected_Columnname")
            .rdd.flatMap(lambda x: x)
            .collect()
        )
        print(column)
        
        # print(mask_dict)
        df1 = self.gooddf
        for columns, maskval in mask_dict.items():
            df = df1.select(f.col("id"), f.col(columns))
            display(df)  # noqa: F821
            if maskval == "Token":
               
                df_masked = df.withColumn("masked_column", self.mask_func1(df[columns]))
                # df_masked.show()
                df_masked = df_masked.drop(columns).withColumnRenamed(
                    "masked_column", columns
                )
                display(df_masked)  # noqa: F821
            elif maskval == "Encryption":

                fernetkey = "fernet-key-" + self.FNT_ID
                encryptionKey = self.dbutils.preview.secret.get(
                    scope="fof-prd-scope", key=fernetkey
                )

                
                df_masked = df.withColumn(
                    "masked_column",
                    self.mask_encrypt(df[columns], f.lit(encryptionKey)),
                )
                df_masked = df_masked.drop(columns).withColumnRenamed(
                    "masked_column", columns
                )
            elif maskval == "Shuffling":
                df_masked = df.withColumn(
                    "masked_column", self.mask_scrumble(df[columns])
                )
                df_masked = df_masked.drop(columns).withColumnRenamed(
                    "masked_column", columns
                )

            else:
                
                # print('else-loop')
                df_masked = df.withColumn(
                    "masked_columns", f.lit(maskval).cast(StringType())
                )
                df_masked = df_masked.drop(columns).withColumnRenamed(
                    "masked_columns", columns
                )
                
                # print("Masked")
            df1 = df1.drop(columns)
            df1 = df1.join(df_masked, df1.id == df_masked.id, "left_outer").drop(
                df_masked.id
            )
        df1.show()
        return df1

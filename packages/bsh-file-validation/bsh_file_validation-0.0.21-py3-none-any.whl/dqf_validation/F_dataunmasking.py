from pyspark.sql.types import StringType
from cryptography.fernet import Fernet
import json


class Data_unmasking:
    def __init__(self, config, spark1):
        self.config = config
        self.schema = self.config["schema"]
        self.spark = spark1
        self.sc = self.spark.sparkContext
        self.FNT_ID = self.config["file_read_configs"]["FNT_Id"]
        self.schema_df = self.spark.read.json(
            self.sc.parallelize([json.dumps(self.schema)])
        )
        self.dbutils = self.get_dbutils()
        self.databasename = config["deltalake_configs"]["DbName"]
        print(self.databasename)
        self.tablename = config["deltalake_configs"]["TabelName"]
        print(self.tablename)
        

    def get_dbutils(self):
        try:
            from pyspark.dbutils import DBUtils

            dbutils = DBUtils(self.spark)
        except ImportError:
            import IPython

            dbutils = IPython.get_ipython().user_ns["dbutils"]
        return dbutils

    @staticmethod
    def decrypt_val(cipher_text, MASTER_KEY):
        f = Fernet(MASTER_KEY)
        clear_val = f.decrypt(cipher_text.encode()).decode()
        return clear_val

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
        for columns, maskval in mask_dict.items():
            if maskval == "Encryption":
                
                fernetkey = "fernet-key-" + self.FNT_ID
                encryptionKey = self.dbutils.preview.secret.get(
                    scope="fof-prd-scope", key=fernetkey
                )
                print(encryptionKey)

                sqlContext.udf.register(  # noqa: F821
                    "decrypt", Data_unmasking.decrypt_val, StringType()
                )
                decrypt_df = spark.sql(  # noqa: F821
                    "select m.*,decrypt(df['columns'], '"
                    + encryptionKey
                    + "')as '"
                    + columns
                    + "' from  '"
                    + self.databasename
                    + "'.'"
                    + self.tablename
                    + "' m"
                )
                decrypt_df.createOrReplaceTempView("decryptedtable")

        return decrypt_df

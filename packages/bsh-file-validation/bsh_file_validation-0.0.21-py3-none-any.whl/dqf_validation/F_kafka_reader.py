import json
from .F_kafka_schema import kafkaschema
from pyspark.sql.functions import udf, col


def str_to_dict(string_rep):
    return json.loads(string_rep)


class datareader:
    def __init__(self, spark, kafka_meta, FNT_ID):
        self.spark = spark
        self.kafka_meta = kafka_meta
        self.sc = self.spark.sparkContext
        self.FNT_ID = FNT_ID
        self.kafka_obj = kafkaschema(self.spark, self.FNT_ID)

    def streamreader(self):
        if self.FNT_ID == "172":
            df = self.kafkadatareader_1()
        elif self.FNT_ID == "215":
            df = self.kafkadatareader_2()

        return df

    def kafkadatareader_1(self):
        df = (
            self.spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", self.kafka_meta["bootstrap"])
            .option("subscribe", self.kafka_meta["subscribe"])
            .option("startingOffsets", self.kafka_meta["startingOffsets"])
            .load()
        )
        df = df.selectExpr("CAST(value AS STRING)")
        schema = self.kafka_obj.get_kafka_schema()

        udf_page = udf(str_to_dict, schema)
        df = df.withColumn("data", udf_page(col("value")))

        df = df.select("data.*")
        return df

    def kafkadatareader_2(self):
        
        return self.kafkadatareader_1()

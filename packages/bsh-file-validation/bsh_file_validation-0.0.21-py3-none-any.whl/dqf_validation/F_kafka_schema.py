from pyspark.sql.types import (
    StructField,
    StructType,
    StringType,
    BooleanType,
    LongType
)


class kafkaschema:
    def __init__(self, spark, fnt_id):
        self.spark = spark
        self.sc = self.spark.sparkContext
        self.fnt_id = fnt_id

    def get_kafka_schema(self):
        if self.fnt_id == "172":
            Schema = self.get_schemas_172()
            return Schema
        if self.fnt_id == "215":
            Schema = self.getschemas_215()
            return Schema

    def get_schemas_172(self):
        schema = StructType(
            [
                StructField("DOB", StringType(), True),
                StructField("address", StringType(), True),
                StructField("currency_code", StringType(), True),
                StructField("date_time", StringType(), True),
                StructField("email", StringType(), True),
                StructField("firstname", StringType(), True),
                StructField("iseligible", BooleanType(), True),
                StructField("job", StringType(), True),
                StructField("lastname", StringType(), True),
                StructField("phoneno", StringType(), True),
                StructField("randomdata", LongType(), True),
                StructField("ssn", StringType(), True),
                StructField("state", StringType(), True),
                StructField("website", StringType(), True),
            ]
        )
        return schema

    def get_schemas_215(self):
        
        return self.get_schemas_172()

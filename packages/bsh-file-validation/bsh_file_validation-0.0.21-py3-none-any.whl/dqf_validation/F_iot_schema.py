from pyspark.sql import functions as f
from pyspark.sql.types import StructType
import json


class iotschema:
    def __init__(self, spark, fnt_id, fschema):
        self.spark = spark
        self.sc = self.spark.sparkContext
        self.fnt_id = fnt_id
        self.fileschema = fschema

    def get_iot_schema(self):
        if self.fnt_id == "32":
            dataset, body = self.get_schemas_32()
            return dataset, body
        elif self.fnt_id == "57":
            schema = self.get_schemas_57()
            return schema
        elif self.fnt_id == "67" or self.fnt_id == "66":
            schema = self.get_schemas_67()
            return schema
        else:
            schema = self.get_schemas_68()
            return schema

    def get_schemas_32(self):
        vals = (
            self.sc.wholeTextFiles(
                "dbfs:/FileStore/shared_uploads/bandinaveen@fofdlm.onmicrosoft.com/ProductionEvents_202301030447.json"
            )
            .values()
            .flatMap(
                lambda a: [
                    '{"EnqueuedTimeUtc":' + val if i > 0 else val
                    for i, val in enumerate(a.split('\r\n{"EnqueuedTimeUtc":'))
                ]
            )
        )
        df = self.spark.read.json(vals)
        df = df.withColumn("current_timestamp", (f.current_timestamp()))
        dataset_schema = df.schema

        vals = (
            self.sc.wholeTextFiles(
                "dbfs:/FileStore/shared_uploads/bandinaveen@fofdlm.onmicrosoft.com/ProductionEvents_202301030447.json"
            )
            .values()
            .flatMap(
                lambda a: [
                    '{"EnqueuedTimeUtc":' + val if i > 0 else val
                    for i, val in enumerate(a.split('\r\n{"EnqueuedTimeUtc":'))
                ]
            )
        )
        df = self.spark.read.json(vals).select(
            f.col("Body.DMC"),
            f.col("Body.EventName"),
            f.col("Body.Eventid"),
            f.col("Body.Identifier"),
            f.col("Body.Result_State"),
            f.col("Body.batch_no"),
            f.col("Body.line_no"),
            f.col("Body.part_no"),
            f.col("Body.plant"),
            f.col("Body.process_no"),
            f.col("Body.product_family"),
            f.col("Body.station_no"),
            f.col("Body.timestamp"),
            f.col("Body.timezone"),
        )
        body_schema = df.schema
        return dataset_schema, body_schema

    def get_schemas_57(self):
        schema = "timestamp timestamp, deviceId string, temperature double, humidity double, \
            windspeed double, winddirection string, rpm double, angle double"
        return schema

    def get_schemas_67(self):
        with open(self.fileschema, "r") as f:
            schema_json = f.read()
        schema_dict = json.loads(schema_json)
        schema = StructType.fromJson(schema_dict)
        return schema


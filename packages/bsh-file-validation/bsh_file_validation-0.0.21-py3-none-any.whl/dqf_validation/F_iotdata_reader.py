from pyspark.sql import functions as f
from .F_iot_schema import iotschema

class datareader:

    def __init__(self, spark, iotdata, FNT_ID, fileschema):
        self.spark = spark
        self.iotdata = iotdata
        self.sc = self.spark.sparkContext
        self.FNT_ID = FNT_ID
        self.fschema = fileschema
        self.iot_obj = iotschema(self.spark, self.FNT_ID, self.fschema)
        self.EVENTHUBS_CONNECTION_STRING = "eventhubs.connectionString"
        self.EVENTHUBS_CONSUMER_GROUP = "eventhubs.consumerGroup"
        self.READING_ALL_COLUMNS = "reading.*"

    def streamreader(self):
        if self.FNT_ID == "32":
            df = self.iotdatareader_32()
            return df
        elif self.FNT_ID == "57":
            df = self.iotdatareader_57()
            return df
        elif self.FNT_ID == "67" or self.FNT_ID == "68":
            df = self.iotdatareader_67()
            return df
        elif self.FNT_ID == "66":
            df = self.iotdatareader_66()
            return df

    @staticmethod
    def convertCase(encr_val):
        x = "".join(chr(i) for i in encr_val)
        return x

    def iotdatareader_32(self):
        self.dataset_schema, self.body_schema = self.iot_obj.get_iot_schema()
        ehConf = {
            self.EVENTHUBS_CONNECTION_STRING : self.iotdata["connectionString"],
            "ehName": self.iotdata["eventhubname"],
        }
        ehConf[
            self.EVENTHUBS_CONNECTION_STRING
        ] = self.sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(
            self.iotdata["connectionString"]
        )
        ehConf[self.EVENTHUBS_CONSUMER_GROUP] = self.iotdata["consumergroup"]
        df = (
            self.spark.readStream.format("eventhubs")
            .options(**ehConf)
            .schema(self.dataset_schema)
            .option("rowsPerBatch", 10)
            .load()
            .withColumn(
                "Body", f.from_json(f.col("Body").cast("string"), self.body_schema)
            )
            .withColumn(
                "timestamp2",
                f.from_unixtime(
                    f.unix_timestamp(f.col("Body.timestamp"), "M/d/yyyy hh:mm:ss a"),
                    "yyyy-MM-dd'T'HH:mm:ss",
                ),
            )
            .select(
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
                f.col("SystemProperties.iothub-connection-device-id"),
            )
            .alias("leftpart")
            .filter(f.col("iothub-connection-device-id") == self.iotdata["DeviceId"])
            .drop(f.col("iothub-connection-device-id"))
        )

        return df

    def iotdatareader_57(self):
        ehConf = {
            self.EVENTHUBS_CONNECTION_STRING: self.iotdata["connectionString"],
            "ehName": self.iotdata["eventhubname"],
        }
        ehConf[
            self.EVENTHUBS_CONNECTION_STRING
        ] = self.sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(
            self.iotdata["connectionString"]
        )
        ehConf[self.EVENTHUBS_CONSUMER_GROUP] = self.iotdata["consumergroup"]
        schema = self.iot_obj.get_iot_schema()
        iot_stream = (
            self.spark.readStream.format("eventhubs")
            .options(**ehConf)
            .load()
            .withColumn("reading", f.from_json(f.col("body").cast("string"), schema))
            .select("reading.deviceId", "reading.temperature", "reading.humidity")
        )
        print("Printing schema from IOT source  ")
        iot_stream.printSchema()
        return iot_stream

    def iotdatareader_67(self):
        ehConf = {
            self.EVENTHUBS_CONNECTION_STRING: self.iotdata["connectionString"],
            "ehName": self.iotdata["eventhubname"],
        }
        ehConf[
            self.EVENTHUBS_CONNECTION_STRING
        ] = self.sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(
            self.iotdata["connectionString"]
        )
        ehConf[self.EVENTHUBS_CONSUMER_GROUP] = self.iotdata["consumergroup"]
        schema = self.iot_obj.get_iot_schema()
        iot_stream = (
            self.spark.readStream.format("eventhubs")
            .options(**ehConf)
            .option("rowsPerBatch", 500)
            .load()
            .withColumn("reading", f.from_json(f.col("body").cast("string"), schema))
            .select(READING_ALL_COLUMNS)
        )

        return iot_stream

    def iotdatareader_66(self):
        convertUDF = f.udf(lambda z: datareader.convertCase(z))
        ehConf = {
            self.EVENTHUBS_CONNECTION_STRING: self.iotdata["connectionString"],
            "ehName": self.iotdata["eventhubname"],
        }
        ehConf[
            self.EVENTHUBS_CONNECTION_STRING
        ] = self.sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(
            self.iotdata["connectionString"]
        )
        ehConf[self.EVENTHUBS_CONSUMER_GROUP] = self.iotdata["consumergroup"]
        schema = self.iot_obj.get_iot_schema()
        df_stream_in = (
            self.spark.readStream.format("eventhubs")
            .options(**ehConf)
            .option("rowsPerBatch", 500)
            .load()
            .withColumn("convereted", convertUDF(f.col("Body")))
        )
        df = df_stream_in.withColumn(
            "reading", f.from_json(f.col("convereted").cast("string"), schema)
        )
        df1 = df.select(READING_ALL_COLUMNS)

        return df1

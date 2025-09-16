# Databricks notebook source
import pyspark
import os
import shutil
import time
from pathlib import Path
from pyspark.sql.functions import count, col, lit
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
    LongType,
    DecimalType,
    DateType,
    TimestampType,
    FloatType,
    BooleanType,
    ArrayType,
)
from pyspark.sql.streaming import StreamingQueryListener


# COMMAND ----------

from pyspark.sql.streaming import StreamingQueryListener

durschema = StructType(
    [
        StructField("addBatch", StringType()),
        StructField("getBatch", StringType()),
        StructField("getOffset", StringType()),
        StructField("queryPlanning", StringType()),
        StructField("triggerExecution", StringType()),
        StructField("walCommit", StringType()),
    ]
)

metschema_sub = StructType(
    [StructField("cnt", StringType()), StructField("malformed", StringType())]
)

metschema_main = StructType([StructField("metric", metschema_sub)])


usage_schema = StructType(
    [
        StructField("id", StringType()),
        StructField("runId", StringType()),
        StructField("name", StringType()),
        StructField("batchId", StringType()),
        StructField("numInputRows", StringType()),
        StructField("inputRowsPerSecond", StringType()),
        StructField("processedRowsPerSecond", StringType()),
        StructField("timestamp", StringType()),
        StructField("durationMs", durschema),
        StructField("stateOperators", ArrayType(StringType())),
        StructField("sources", ArrayType(StringType())),
        StructField("sink", StringType()),
        StructField("observedMetrics", StructType(metschema_main)),
    ]
)


# Define my listener.
class MyListener(StreamingQueryListener):
    def onQueryStarted(self, event):
        print(f"'{event.name}' [{event.id}] got started now!")

    def onQueryProgress(self, event):
        print(event.progress.json)
        df = spark.read.json(
            sc.parallelize([str(event.progress.json)]), schema=usage_schema
        )
        df2 = df.select(
            col("id"),
            col("runId"),
            col("name"),
            col("timestamp"),
            col("batchId"),
            col("numInputRows"),
            col("inputRowsPerSecond"),
            col("processedRowsPerSecond"),
            col("observedMetrics.metric.cnt").alias("cnt"),
            col("observedMetrics.metric.malformed").alias("malformed"),
        )

        df2.write.mode("append").format("delta").saveAsTable("stream_logs")

    def onOtherEvent(self, event):
        if isinstance(event, SparkListenerBatchCompleted):
            print(
                "-------------------------------------------------------------------------------"
            )
            print("Batch completed", event)

    def onQueryTerminated(self, event):
        print(f"{event.id} got terminated!")
        spark.streams.removeListener(self)


# Add my listener.


# COMMAND ----------

my_listener = MyListener()
spark.streams.addListener(my_listener)

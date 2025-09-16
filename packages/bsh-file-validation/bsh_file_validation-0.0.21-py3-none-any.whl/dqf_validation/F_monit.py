import pyspark
import os
import shutil
import time
from pathlib import Path

from pyspark.sql.functions import col, lit
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
    TimestampType,
    ArrayType,
)
from pyspark.sql.streaming import StreamingQueryListener
import os
import sys
import shutil
import time
from pathlib import Path
import json
from pyspark.sql.functions import count, col, lit
from pyspark.sql.streaming import StreamingQueryListener
from pyspark.streaming import StreamingContext

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
        StructField("timestamp", TimestampType()),
        StructField("durationMs", durschema),
        StructField("stateOperators", ArrayType(StringType())),
        StructField("sources", ArrayType(StringType())),
        StructField("sink", StringType()),
        StructField("observedMetrics", StructType(metschema_main)),
    ]
)


# Define my listener.
class MyListener(StreamingQueryListener):
    def __init__(
        self,
        spark1,
        json1,
        dbwriter,
        source_dl_layer,
        pipeline_run_id,
        job_run_id,
        json2,
        act_to_dl_layer_path,
        dest_dl_layer,
    ):
        self.spark1 = spark1
        self.sc = self.spark1.sparkContext
        self.json1 = json1
        self.dbwriter = dbwriter
        self.source_dl_layer = source_dl_layer
        self.pipeline_run_id = pipeline_run_id
        self.job_run_id = job_run_id
        self.json2 = json2
        self.act_to_dl_layer_path = act_to_dl_layer_path
        self.dest_dl_layer = dest_dl_layer

    def onQueryStarted(self, event):
        print(f"'{event.name}' [{event.id}] got started now!")
        print("json", self.json1)
        self.dbwriter.fn_insert_delta_logs(
            file=self.json1,
            job_id=self.job_run_id,
            pipeline_run_id=self.pipeline_run_id,
            from_dl_layer=self.source_dl_layer,
            ref_tracking_ids=self.job_run_id,
        )

    def onQueryProgress(self, event):
        
        # print(f"{row.cnt} rows processed!")
        # print(event.progress.json)
        df = self.spark.read.json(
            self.sc.parallelize([str(event.progress.json)]), schema=usage_schema
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
        # .write.mode("append").format("delta").saveAsTable('stream_logs')
        df2 = df2.withColumn("tracking_id", lit(self.job_run_id))
        df2.write.mode("append").format("delta").saveAsTable(
            "devicesimulator.stream_logs"
        )


    #     if isinstance(event, SparkListenerBatchCompleted):
    #         print(
    #             "-------------------------------------------------------------------------------"
    #         )
    #         print("Batch completed", event)

    def onQueryTerminated(self, event):
        print(f"{event.id} got terminated!")
        print("on query terminated", event)
        self.dbwriter.fn_update_delta_logs_new(
            file=self.json2,
            job_id=self.job_run_id,
            to_dl_layer=self.dest_dl_layer,
            to_dl_layer_path=self.act_to_dl_layer_path,
            validation_status="completed",
            copy_activity_status="completed",
            ref_tracking_ids=self.job_run_id,
        )
        self.spark.streams.removeListener(self)


# Add my listener.

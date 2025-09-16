# Databricks notebook source
spark.conf.set("ignoreDeletes", "true")

# COMMAND ----------

spark.conf.set(
    "spark.sql.streaming.stateStore.providerClass",
    "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider",
)

# COMMAND ----------

from pyspark.sql import functions as f
from .F_stream_powerbi import *

# COMMAND ----------

streamlog = spark.readStream.format("delta").table("default.stream_logs")

err_df = spark.readStream.format("delta").table("devicesimulator.errorreasondata1")

err_df = err_df.withColumnRenamed("id", "index")
df = streamlog.join(err_df, on=["tracking_id", "batchId"])

df = df.select(
    "batchId",
    "name",
    "timestamp",
    "numInputRows",
    "inputRowsPerSecond",
    "processedRowsPerSecond",
    "index",
    "column",
    "Validationtype",
)

stream = stream_powerbi()


# COMMAND ----------

df.writeStream.outputMode("append").option(
    "checkpointLocation", "/mnt/landing/checkpoints/stp10/"
).foreachBatch(stream.fn_post).start().awaitTermination()

# COMMAND ----------

df.writeStream.outputMode("append").trigger(processingTime="60 seconds").option(
    "checkpointLocation", "/mnt/landing/checkpoints/stp/"
).foreachBatch(stream.fn_post).start().awaitTermination()

# COMMAND ----------

streamlog = spark.readStream.format("delta").table("default.stream_logs")

err_df = spark.readStream.format("delta").table("devicesimulator.errorreasondata")

err_df = err_df.withColumnRenamed("id", "index")
df = streamlog.join(err_df, on=["tracking_id", "batchId"])

df = df.select(
    "batchId",
    "name",
    "timestamp",
    "numInputRows",
    "inputRowsPerSecond",
    "processedRowsPerSecond",
    "index",
    "column",
    "Validationtype",
)
stream = stream_powerbi()

# COMMAND ----------

streamlog = spark.read.format("delta").table("default.stream_logs")

err_df = spark.read.format("delta").table("devicesimulator.errorreasondata")

bad_df = spark.read.format("delta").table("devicesimulator.baddfdata")
bad_df = bad_df.withColumnRenamed("batch_id", "batchId")
err_df = err_df.withColumnRenamed("id", "index")
df = streamlog.join(err_df, on=["tracking_id", "batchId"])
df.createOrReplaceTempView("df1")
df2 = spark.sql(
    "select tracking_id,name,batchId,Validationtype,column,count(distinct index),max(numInputRows) from df1 group by name,batchId,tracking_id,Validationtype,column"
)
df3 = spark.sql(
    "select tracking_id,name,batchId,count(distinct index),max(numInputRows) from df1 group by name,batchId,tracking_id"
)

display(df3)

# COMMAND ----------

# MAGIC %sql
# MAGIC alter view  vw_streamlogs as
# MAGIC select a.tracking_id,name,a.batchId,cast(max(a.timestamp)  as timestamp) timestamp,max(numInputRows) as numInputrows,max(inputRowsPerSecond) as inputrowspersecond,max(processedRowsPerSecond) as processedrowspersecond,count(distinct b.id) as badrows,(max(numInputRows)- count(distinct b.id)) as goodrows from stream_logs a inner join devicesimulator.errorreasondata b where a.tracking_id=b.tracking_id and a.batchId=b.batchId  group by name,a.batchId,a.tracking_id
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(distinct id) from devicesimulator.errorreasondata

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from stream_logs where batchid=2

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(1) from devicesimulator.baddfdata where batch_id=3

# COMMAND ----------

streamlog = spark.read.format("delta").table("default.stream_logs")

err_df = spark.read.format("delta").table("devicesimulator.errorreasondata")

bad_df = spark.read.format("delta").table("devicesimulator.baddfdata")
bad_df = bad_df.withColumnRenamed("batch_id", "batchId")
err_df = err_df.withColumnRenamed("id", "index")
df = streamlog.join(err_df, on=["tracking_id", "batchId"])

df.createOrReplaceTempView("df1")
df2 = spark.sql(
    "select tracking_id,name,batchId,Validationtype,column,count(distinct index),max(numInputRows) from df1 group by name,batchId,tracking_id,Validationtype,column"
)
df3 = spark.sql(
    "select tracking_id,name,batchId,count(distinct index),max(numInputRows) from df1 group by name,batchId,tracking_id"
)

display(df3)

# COMMAND ----------

streamlog = spark.readStream.format("delta").table("default.stream_logs")

err_df = spark.readStream.format("delta").table("devicesimulator.errorreasondata1")

err_df = err_df.withColumnRenamed("id", "index")
df = streamlog.alias("a").join(
    err_df.alias("b"),
    f.expr("""a.tracking_id=b.tracking_id and a.batchid=b.batchid"""),
    "inner",
)

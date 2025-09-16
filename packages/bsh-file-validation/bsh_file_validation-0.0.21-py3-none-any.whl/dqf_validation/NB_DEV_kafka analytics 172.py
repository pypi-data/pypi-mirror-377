# Databricks notebook source
# MAGIC %sql
# MAGIC SET spark.sql.legacy.timeParserPolicy=LEGACY

# COMMAND ----------

import json
import time

def func1(df, id):
    try:
        print("inside func1")
        df.persist()
        baddf = None
        gooddf = None
        print("DATAFRAME COUNT", df.count())
        df1 = uf.fn_addindex(df)
        print(df1.printSchema)
        batch_id = id
        endtime = "20:00:00"
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        if current_time > endtime:
            dbwriter.fn_update_delta_logs_new(
                file=json2,
                job_id=job_run_id,
                to_dl_layer=dest_dl_layer,
                to_dl_layer_path=act_to_dl_layer_path,
                validation_status="completed",
                copy_activity_status="completed",
                ref_tracking_ids=job_run_id,
            )
            dbutils.notebook.exit

        if dqf_needed == 0:
            gooddf = df
            gooddf_count = gooddf.count()
            error_df_count = 0
            baddf_count = 0
        else:
            baddf, gooddf, error_df = av.fn_getattributesValidation(df1)
            print("GOOD DATAFRAME COUNT", gooddf.count())
            print("error_df__________")

            gooddf_count = gooddf.rdd.count()

            baddf_count = baddf.rdd.count()
            print("BAD DATAFRAME COUNT", baddf.count())
            badrows_df = baddf.withColumn("batch_id", lit(str(id)))
            error_df_count = error_df.count()
            print(badrows_df)
        if error_df_count > 0:
            error_df = error_df.withColumn("tracking_id", lit(job_run_id))
            error_df = error_df.withColumn("batchId", lit(batch_id))
            error_df = error_df.withColumn("timestamp", f.current_timestamp())
            error_df.write.mode("append").format("delta").saveAsTable(
                "devicesimulator.errorreasondata3"
            )
        if baddf_count > 0:
            fn_move_baddf_silver(badrows_df, path, file_template, uf)
        if gooddf_count > 0:
            print("GOOD DATAFRAME COUNT", gooddf.count())
            act_target_path = path["Silver-Success"]
            targetpath = act_target_path + file_template
            print("targetpath ", targetpath)
            print("calling the delta lake function here")
            deltaload = DeltaTableLoad(config_dict, targetpath, gooddf, spark1)
            deltaload.table_load()
    except Exception as e:
        print(e)


def fn_move_baddf_silver(badrows_df, path, file_template, uf):
    errpath = path["Silver-Error"]
    folder_date = uf.fn_put_datepartition()
    path1 = errpath + file_template
    badrows_df = badrows_df.coalesce(1)
    badrows_df.write.format("delta").mode("append").option("path", path1).saveAsTable(
        dbname + "." + tablename + "_baddfdata"
    )


# COMMAND ----------

from pyspark.sql import SparkSession
from F_monit import MyListener

spark1 = SparkSession.builder.appName("monitor-tests").getOrCreate()
sc = spark1.sparkContext

# COMMAND ----------

# Import required modules<br>

from pyspark.sql import functions as f
from pyspark.sql.types import StringType, StructType, StructField, IntegerType, DoubleType, LongType, TimestampType, BooleanType, ArrayType
from delta.tables import DeltaTable
from pyspark.sql.functions import rand, when, array_remove, collect_set, count, col, lit
from pyspark.streaming import StreamingContext
import json
import msal
import pathlib
import random
import functools
import ast
import time
from datetime import datetime
from multiprocessing.pool import ThreadPool

# COMMAND ----------

from F_UtilityFunctions import utilityfunction as utf

# from Dbconnection import *
from F_Dbreader import Dbreader
from F_Dbwriters import Dbwriters
from F_Dbconfigreader import Dbconfigreaders
from F_delta_table_load import DeltaTableLoad
from F_Movefiles import Movefiles
from commonfunc.F_databaseconnect import DBconnection
from commonfunc.F_logs import commonlogs
from F_AttributeValidator2 import AttributeValidator
from F_filereader import masterdata
from F_iot_schema import iotschema
from F_iotdata_reader import datareader
from F_AttributeValidator4 import AttributeValidator
from F_filereader2 import masterdata
from F_datamasking import Data_masking
from F_kafka_reader import datareader

# COMMAND ----------


import uuid

# Input is passed from azure data factory pipelines
job_run_id = dbutils.widgets.get("jobRunId")
pipeline_run_id = dbutils.widgets.get("pipielineRunId")
SourceSystem = dbutils.widgets.get("SourceSystem")
file_template = dbutils.widgets.get("FileName_Template")
IOTFlag = dbutils.widgets.get("IS_IOT")
FNT_ID = dbutils.widgets.get("FNT_Id")
HierarchyFlag = dbutils.widgets.get("IS_Hierarchical")
curr_try = dbutils.widgets.get("curr_try")
# HierarchyFlag='True'


# COMMAND ----------

server = dbutils.secrets.get(scope="eda-dev-adb-scope", key="EDA-SQLDB-ServerName")
database = dbutils.secrets.get(scope="eda-dev-adb-scope", key="EDA-SQLDB-DBName")
spark1 = (
    SparkSession.builder.appName("streaming-tests")
    .config("spark.sql.broadcastTimeout", "50000")
    .getOrCreate()
)
source_dl_layer = "Bronze"
dest_dl_layer = "Silver"

dbasecon = DBconnection(database=database, server=server, spark1=spark1)
con = dbasecon.fn_get_connection()
dbread = Dbreader(con)
dbwrite = Dbwriters(con)

dbwriter = commonlogs(
    dbasecon,
    sourceName=SourceSystem,
    dest_dl_layer=dest_dl_layer,
    key="DQFValidation",
    FNT_ID=FNT_ID,
    job_run_id=job_run_id,
    HierarchyFlag=HierarchyFlag,
    file_template=file_template,
    spark1=spark1,
)

configreader = Dbconfigreaders(
    con, FNT_ID, source_dl_layer, dest_dl_layer, SourceSystem
)
config_dict = configreader.getall_configs()

uf = utf(con, source_dl_layer, dest_dl_layer, SourceSystem)
path = config_dict["path"]
print("Path", path)
mv = Movefiles(
    dbwrite,
    uf,
    config_dict,
    source_dl_layer,
    dest_dl_layer,
    path,
    file_template,
    spark1,
    FNT_ID,
    dbwriter,
    SourceSystem,
)
iotdata = config_dict["iot"]
kafkadata = config_dict["kafka_configs"][0]
schema = config_dict["schema"]
loadtype = kafkadata["load_type"]
fileschema = config_dict["file_read_configs"]["Expected_Schema"]
dbname = config_dict["deltalake_configs"]["DbName"]
tablename = config_dict["deltalake_configs"]["TabelName"]

schema_df = spark.read.json(sc.parallelize([json.dumps(schema)]))
columns = (
    schema_df.filter("operation='column'")
    .rdd.map(lambda a: a["Expected_Columnname"])
    .collect()
)

act_temp_file_path = path["Bronze-Cache"]
act_from_dl_layer_path = path["Bronze-Success"]
act_to_dl_layer_path = path["Silver-Success"]
key = FNT_ID
dqf_needed = config_dict["dqf_needed"]["DQF_Needed"]


av = AttributeValidator(
    config=config_dict,
    temp_file_path=act_temp_file_path,
    temp_file_name=job_run_id + "_" + key,
    spark=spark1,
    job_run_id=job_run_id,
)
data_obj = datareader(spark1, kafkadata, FNT_ID)
data = data_obj.streamreader()

# COMMAND ----------

json1 = {"file_id": 0, "filepath": act_from_dl_layer_path, "fnt_id": key}
json2 = {"file_id": 0, "filepath": act_to_dl_layer_path, "fnt_id": key}

# COMMAND ----------

# MAGIC %scala
# MAGIC spark.conf.set("spark.sql.shuffle.partitions",30)

# COMMAND ----------

my_listener = MyListener(
    spark1,
    json1,
    dbwriter,
    source_dl_layer,
    pipeline_run_id,
    job_run_id,
    json2,
    act_to_dl_layer_path,
    dest_dl_layer,
)
spark.streams.addListener(my_listener)
my_observed_csv = data.observe("metric", (count(lit(1))).alias("cnt"))

# COMMAND ----------

my_query = (
    my_observed_csv.writeStream.outputMode("append")
    .foreachBatch(func1)
    .start()
    .awaitTermination()
)


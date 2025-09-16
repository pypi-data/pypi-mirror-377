# Databricks notebook source
from pyspark.sql import SparkSession
from .F_monit import *
spark1 = SparkSession.builder.appName('mor-tests').getOrCreate()
print(spark1.__dict__)

# COMMAND ----------

# MAGIC %sql
# MAGIC SET spark.sql.legacy.timeParserPolicy=LEGACY
# MAGIC

# COMMAND ----------

# Import required modules<br>
from datetime import datetime
import base64
import random
import multiprocessing as mp
import functools
import ast
from multiprocessing.pool import ThreadPool
import pathlib
import msal
import json

from pyspark.sql import functions as f
from pyspark.sql.types import StringType, StructType, StructField, LongType, DecimalType, DateType, TimestampType, FloatType, BooleanType
from pyspark.sql.functions import rand, when, array_remove, collect_set, count, col, lit
from functools import reduce
from pyspark.sql import DataFrame
import operator



# COMMAND ----------

from .F_UtilityFunctions import utilityfunction as utf
#from Dbconnection import *
from .F_Dbreader import Dbreader
from .F_Dbwriters import Dbwriters
from .F_Dbconfigreader import Dbconfigreaders
from .F_delta_table_load import DeltaTableLoad
from .F_Movefiles import Movefiles
from commonfunc.F_databaseconnect import DBconnection
from commonfunc.F_logs import commonlogs
from .F_AttributeValidator2 import AttributeValidator
from .F_filereader import masterdata
from .F_iot_schema import iotschema
from .F_iotdata_reader import datareader
from .F_AttributeValidator4 import AttributeValidator
from .F_filereader2 import masterdata
from .F_datamasking import Data_masking

# COMMAND ----------

'''
import uuid
job_run_id='6F73706F-5A07-4482-866D-76C0B8B6D2323-12'
print(job_run_id)
pipeline_run_id=str(uuid.uuid4())

SourceSystem='Simulatordata'
IOTFlag='True'
HierarchyFlag='True'
FNT_ID='68'
FileTemplate='Sim_Quality_check'
'''
'''
#T_raspberrypi_'
SourceSystem='TestData'
IOTFlag='True'
HierarchyFlag='True'
FNT_ID='57'
FileTemplate='T_raspberrypi'
'''


# COMMAND ----------


import uuid

#Input is passed from azure data factory pipelines
job_run_id=dbutils.widgets.get('jobRunId')
pipeline_run_id=dbutils.widgets.get('pipielineRunId')
SourceSystem=dbutils.widgets.get('SourceSystem')
FileTemplate=dbutils.widgets.get('FileName_Template')
IOTFlag=dbutils.widgets.get('IS_IOT')
FNT_ID=dbutils.widgets.get('FNT_Id')
HierarchyFlag=dbutils.widgets.get('IS_Hierarchical')
curr_try=dbutils.widgets.get('curr_try')



# COMMAND ----------

server = dbutils.secrets.get(scope="fof-prd-scope",key="sqlSever")
database = dbutils.secrets.get(scope="fof-prd-scope",key="sqlDB")
spark1 = SparkSession.builder.appName('streaming-tests').getOrCreate() 
source_dl_layer='Bronze'
dest_dl_layer='Silver'
dbasecon=DBconnection(database=database,server=server,spark1=spark1)
con=dbasecon.fn_get_connection()
dbread=Dbreader(con)
dbwrite=Dbwriters(con)
dbwriter=commonlogs(dbasecon,sourceName=SourceSystem         ,dest_dl_layer=dest_dl_layer,key='DQFValidation',FNT_ID=FNT_ID,job_run_id=job_run_id,HierarchyFlag=HierarchyFlag,FileTemplate=FileTemplate,spark1=spark1)
configreader=Dbconfigreaders(con,FNT_ID,source_dl_layer,dest_dl_layer,SourceSystem)
config_dict=configreader.getall_configs()
uf=utf(con,source_dl_layer,dest_dl_layer,SourceSystem)
path=config_dict['path']
mv=Movefiles(dbwrite,uf,config_dict,source_dl_layer,dest_dl_layer,path,FileTemplate,spark1,FNT_ID,dbwriter,SourceSystem)
iotdata=config_dict['iot']
schema=config_dict['schema']
print(config_dict)
schema_df=spark.read.json(sc.parallelize([json.dumps(schema)]))
columns=schema_df.filter("operation='column'").rdd.map(lambda a:a['Expected_Columnname']).collect()
act_temp_file_path=path['Bronze-Cache']
act_from_dl_layer_path=path['Bronze-Success']
act_to_dl_layer_path=path['Silver-Success']
key=FNT_ID
av=AttributeValidator(config=config_dict,\
                            temp_file_path=act_temp_file_path,\
                            temp_file_name=job_run_id+'_'+key,spark=spark1,job_run_id=job_run_id)
data_obj=datareader(spark1,iotdata,FNT_ID)
data=data_obj.streamreader()


# COMMAND ----------

display(data)

# COMMAND ----------

json1={'file_id':0,'filepath':act_from_dl_layer_path,'fnt_id':key}
json2={'file_id':0,'filepath':act_to_dl_layer_path,'fnt_id':key}

# COMMAND ----------

my_listener = MyListener(spark1,json1,dbwriter,source_dl_layer,pipeline_run_id,job_run_id,json2,act_to_dl_layer_path,dest_dl_layer)
spark.streams.addListener(my_listener)
my_observed_csv = data.observe(
    "metric",
    (count(lit(1))).alias("cnt"))
my_query=my_observed_csv.writeStream\
  .outputMode(iotdata['load_type'])\
  .queryName(iotdata['queryname'])\
  .option("checkpointLocation",iotdata['checkpointlocation'])\
  .foreachBatch(func1)\
  .start().awaitTermination()

# COMMAND ----------

import json
def func1(df,id):
    df.persist()
    bbaddf=None
    gooddf=None
    print('DATAFRAME COUNT',df.count())
    df1=uf.fn_addindex(df)
    #df1.show()
    print(df1.printSchema)
    batch_id=id
    baddf,gooddf,error_df=av.fn_getattributesValidation(df1)
    print('GOOD DATAFRAME COUNT',gooddf.count())
    print('error_df__________')
    #error_df.show()
    gooddf=gooddf.withColumn('batch_id',lit(str(id)))
    gooddf=gooddf.withColumn('tracking_id',lit(job_run_id))
    gooddf_count=gooddf.rdd.count()

    baddf_count=baddf.rdd.count()
    print('BAD DATAFRAME COUNT',baddf.count())
    badrows_df=baddf.withColumn('batch_id',lit(str(id)))
    #baddf_count=baddf.rdd.count()
    print(badrows_df)
    if error_df.count()>0:
        error_df=error_df.withColumn('tracking_id',lit(job_run_id))
        error_df=error_df.withColumn('batchId',lit(batch_id))
        error_df.write.mode('append').format('delta').saveAsTable('devicesimulator.errorreasondata')
    if baddf_count>0:
        fn_move_baddf_silver(badrows_df,path,FileTemplate,uf)
    if gooddf_count>0:
        act_target_path=path['Silver-Success']
        targetpath=act_target_path+FileTemplate
        print("targetpath ",targetpath)
        print('calling the delta lake function here')
        deltaload=DeltaTableLoad(config_dict,targetpath,gooddf,spark1)
        deltaload.table_load() 
    df.unpersist()
    
def fn_move_baddf_silver(badrows_df,path,FileTemplate,uf):
        errpath=path['Silver-Error']
        folder_date=uf.fn_put_datepartition()
        path1=errpath+FileTemplate+folder_date
        badrows_df=badrows_df.coalesce(1)
        badrows_df.write.format("delta").mode("append").option('path',path1).saveAsTable(SourceSystem+'.baddfdata')
        
    

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from devicesimulator.errorreasondata
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC select *from stream_logs

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from stream_logs  order by batchId desc

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) from testdata.t_raspberrypi_ where id=43
# MAGIC

# COMMAND ----------

df=spark.sql('select * from devicesimulator.production_events')
display(df)

# COMMAND ----------

cols=[c.name for c in badrows_df.schema.fields if isinstance(c.dataType, BooleanType)]
        columns=[c.name for c in badrows_df.schema.fields if not isinstance(c.dataType, BooleanType)]
        columns.remove('id')
        badrows_df2= badrows_df.withColumn("Values",concat_ws(",",array(*columns))).drop(*columns)
        badrowcount_df= badrows_df2.select("id","Values",func.explode(func.array(list(map(lambda col:struct(func.lit(col).alias("Features"),func.col(col).alias("value")),cols)))).alias("v")).selectExpr("id","Values" ,"v.*")
        badrowcount_df1 = badrowcount_df.groupBy("id","Features").agg(func.count(func.when(func.col("value")==False,1)).alias("Row_Count"))
        badrow_df=badrowcount_df.filter(col('value')==False)
        badrowcount_df1.write.format("delta").mode("append").saveAsTable("testdata.T_errorcount")
        badrow_df.write.format("delta").mode("append").saveAsTable("testdata.T_badrows")

# COMMAND ----------

my_listener = MyListener(spark1)
spark.streams.addListener(my_listener)
my_observed_csv = data.observe(
    "metric",
    count(lit(1)).alias("cnt"),  # number of processed rows
    count(col(iotdata['uniquecol'])).alias("malformed"))
my_query=my_observed_csv.writeStream\
  .outputMode(iotdata['load_type'])\
  .queryName(iotdata['queryname'])\
  .option("checkpointLocation",'/mnt/landing/checkpoints/navi11/')\
  .foreachBatch(func1)\
  .start().awaitTermination()

# COMMAND ----------

.option("overwriteSchema", "true")
.filter(f.col('deviceid')==self.iotdata['DeviceId'])

# COMMAND ----------

HostName=fof-iot-2-prd-eus.azure-devices.net;DeviceId=raspberriPI;SharedAccessKey=cpf4lkrk8QlNSnv7mF7IeYznzyj+wb8QpCn87v/RH5w=

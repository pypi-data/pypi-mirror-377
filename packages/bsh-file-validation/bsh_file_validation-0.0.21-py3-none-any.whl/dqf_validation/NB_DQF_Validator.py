# Databricks notebook source
# MAGIC %reload_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------


import uuid

# job_run_id=str(uuid.uuid4())
# print(job_run_id)
# pipeline_run_id=str(uuid.uuid4())
# print(pipeline_run_id)
# SourceSystem='AdventureWorksSales'
# HierarchyFlag='False'
# IOTFlag='False'
# FNT_ID='121'
# FileTemplate= 'F_emp_data'

# job_run_id=str(uuid.uuid4())
# print(job_run_id)
# pipeline_run_id=str(uuid.uuid4())
# #pipeline_run_id='18ecc52a-61b4-423d-a105-5bba7e68843d'
# SourceSystem='OrganisationData'
# HierarchyFlag='False'
# IOTFlag='False'
# FNT_ID='241'
# FileTemplate='Employee_salary_data'
# curr_try=1

# job_run_id=str(uuid.uuid4())
# print(job_run_id)
# pipeline_run_id=str(uuid.uuid4())
# SourceSystem='TestData'
# HierarchyFlag='False'
# IOTFlag='False'
# FNT_ID='58'
# FileTemplate='T_employee_data'


# job_run_id=str(uuid.uuid4())
# print(job_run_id)
# pipeline_run_id=str(uuid.uuid4())
# # #pipeline_run_id='18ecc52a-61b4-423d-a105-5bba7e68843d'
# SourceSystem='Persondetails'
# HierarchyFlag='False'
# IOTFlag='False'
# FNT_ID='96'
# FileTemplate='T_person_data'
# curr_try=1


# import uuid

# job_run_id=str(uuid.uuid4())
# print(job_run_id)
# pipeline_run_id=str(uuid.uuid4())
# print(pipeline_run_id)
# SourceSystem='AWS_MYSQL'
# HierarchyFlag='False'
# IOTFlag='False'
# FNT_ID='238'
# FileTemplate= 'T_AWS_employee'
'''
import uuid
job_run_id=str(uuid.uuid4())
print(job_run_id)
pipeline_run_id=str(uuid.uuid4())
SourceSystem='TestData'
HierarchyFlag='False'
IOTFlag='False'
FNT_ID='246'
FileTemplate='T_Orders'
'''

# import uuid


job_run_id=str(uuid.uuid4())
print(job_run_id)
pipeline_run_id=str(uuid.uuid4())
print(pipeline_run_id)
SourceSystem='APIMetadata'
HierarchyFlag='False'
IOTFlag='False'
FNT_ID='112'
FileTemplate= 'API_3'


# job_run_id=str(uuid.uuid4())
# print(job_run_id)
# pipeline_run_id=str(uuid.uuid4())
# #pipeline_run_id='18ecc52a-61b4-423d-a105-5bba7e68843d'
# SourceSystem='Source1'
# HierarchyFlag='False'
# IOTFlag='False'
# FNT_ID='242'
# FileTemplate='Department_data'
# curr_try=1
# '''

# COMMAND ----------


# import uuid

# #Input is passed from azure data factory pipelines
# job_run_id=dbutils.widgets.get('jobRunId')
# pipeline_run_id=dbutils.widgets.get('pipielineRunId')
# SourceSystem=dbutils.widgets.get('SourceSystem')
# FileTemplate=dbutils.widgets.get('FileName_Template')
# IOTFlag=dbutils.widgets.get('IS_IOT')
# FNT_ID=dbutils.widgets.get('FNT_Id')
# HierarchyFlag=dbutils.widgets.get('IS_Hierarchical')
# curr_try=dbutils.widgets.get('curr_try')



# COMMAND ----------

import os
import shutil
import time
import datetime
import msal
import json
import pathlib
import pandas as pd
import multiprocessing as mp
import functools
from datetime import datetime
from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.sql import functions as f
from pyspark.sql.types import StringType, StructField, StructType, LongType, DecimalType, DateType, TimestampType, FloatType, BooleanType
from pyspark.sql.functions  import spark_partition_id, asc, desc, monotonically_increasing_id,sum,lit,current_timestamp
from functools import reduce
from multiprocessing.pool import ThreadPool
from pyspark.sql import DataFrame
import operator
import ast
from pyspark.sql import SparkSession


del sum 

# COMMAND ----------

from F_UtilityFunctions import utilityfunction as utf
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

# COMMAND ----------

from pyspark.sql import SparkSession


bbaddf=None
gooddf=None
attributes=None
spark.conf.set("spark.sql.legacy.timeParserPolicy","EXCEPTION")
spark.conf.set("spark.sql.shuffle.partitions",'auto')
server = dbutils.secrets.get(scope="fof-prd-scope",key="EDA-SQLDB-ServerName")
database = dbutils.secrets.get(scope="fof-prd-scope",key="EDA-SQLDB-DBName")
sqlusername = dbutils.secrets.get(scope="fof-prd-scope",key="EDA-SQLDB-SQLusername")
sqlPassword = dbutils.secrets.get(scope="fof-prd-scope",key="EDA-SQLDB-DBPassword")
url=f"jdbc:sqlserver://{server};databaseName={database}"
spark1 = SparkSession.builder.appName('integrity-tests').config("spark.sql.legacy.timeParserPolicy","EXCEPTION").getOrCreate()
source_dl_layer='Bronze'
dest_dl_layer='Silver'
dbasecon=DBconnection(database=database,server=server,spark1=spark1)
con=dbasecon.fn_get_connection()
dbread=Dbreader(con)
dbwrite=Dbwriters(con)
dbwriter=commonlogs(dbasecon,sourceName=SourceSystem,dest_dl_layer=dest_dl_layer,key='DQFValidation',FNT_ID=FNT_ID,job_run_id=job_run_id,HierarchyFlag=HierarchyFlag,FileTemplate=FileTemplate,spark1=spark1)

list_of_batches=dbread.fn_get_files_for_dqf(FNT_ID)
print("list_of_batches " ,list_of_batches)
configreader=Dbconfigreaders(con,FNT_ID,source_dl_layer,dest_dl_layer,SourceSystem)
config_dict=configreader.getall_configs()
uf=utf(con,source_dl_layer,dest_dl_layer,SourceSystem)
path=config_dict['path']
badrowscount=0
print('configs are-----------------------',config_dict)
mv=Movefiles(dbwrite,uf,config_dict,source_dl_layer,dest_dl_layer,path,FileTemplate,spark1,FNT_ID,dbwriter,SourceSystem)

if len(list_of_batches)>0:
    
    batches_files=pd.DataFrame.from_records(list_of_batches).groupby(['FNT_Id'])['File_Id','To_DL_Layer'].apply(lambda g: g.values.tolist()).to_dict()
    ref_tracking_ids_temp=pd.DataFrame.from_records(list_of_batches).groupby(['FNT_Id'])['Tracking_Id'].apply(lambda g: set(g.values.tolist())).to_dict()
    ref_tracking_ids={a:'|'.join([c for c in b]) for a,b in ref_tracking_ids_temp.items()}
    print('ref tracking ids are',ref_tracking_ids)
else:
    batches_files={}
print("batches_files",batches_files)
for key,value in batches_files.items():
    print('key is',key)
    print('value is',value)
    check=config_dict['dqf_needed']
    DQF_Check=check['DQF_Needed']
    Duplicate_Check=check['Duplicatecheck_Needed']
    act_from_dl_layer_path=path['Bronze-Success']
    json1={'file_id':0,'filepath':act_from_dl_layer_path,'fnt_id':key}
    
    dbwriter.fn_insert_delta_logs(file=json1,job_id=job_run_id,pipeline_run_id=pipeline_run_id,from_dl_layer=source_dl_layer,\
                                     ref_tracking_ids=ref_tracking_ids[key])
    
    print("DQF_Needed value is ",DQF_Check)
    fnt_info=config_dict['file_read_configs']
    File_Type=fnt_info['File_Type']
    print('File_type is',File_Type)
    if File_Type=='csv' or File_Type=='txt' or File_Type=='json'  or File_Type=='xml' or File_Type=='parquet':
        act_temp_file_path=path['Bronze-Cache']
        print("temp_file_path ",act_temp_file_path)
        track_id=job_run_id+'-'+key
        print('DQF tracking id',track_id)
        av=AttributeValidator(config=config_dict,\
                            temp_file_path=act_temp_file_path,\
                            temp_file_name=job_run_id+'_'+key,spark=spark1,job_run_id=job_run_id)
        msdata=masterdata(dbwrite,dbread,job_run_id,ref_tracking_ids[key],config_dict,\
                               value,IOTFlag,spark1,mv,track_id) 
        data=msdata.fn_readFiles()
        display(data)
        
        data.printSchema()
        display(data)
        print('final df in dqf notebook')
        
    if data is None:
        act_to_dl_layer_path=path['Bronze-Error']
        
        json3={'file_id':0,'filepath':act_to_dl_layer_path,'fnt_id':key}
        dbwriter.fn_update_delta_logs_new(file=json3,job_id=job_run_id,to_dl_layer=source_dl_layer,\
                                     to_dl_layer_path=act_to_dl_layer_path,validation_status='completed',\
                                     ref_tracking_ids=ref_tracking_ids[key])
        print("Delta logs are updated for error file")
        gooddf_count=0
        baddf_count=0
        error_df_count=0
        
    elif  not DQF_Check:
        print('dqf not needed')
        print('after repartition')
        gooddf_count=data.count()
        print('good data count',gooddf_count)
        print('adding index column to df')
        data1=uf.fn_addindex(data)
        gooddf=data1
        baddf_count=0
        error_df_count=0
        badrowscount=0
        print('last stmt of elif loop')
    else:
        data=uf.fn_addindex(data)
        print('data')
        print('count of data')
        print('schema of data is',data.schema)
        baddf,gooddf,error_df=av.fn_getattributesValidation(data)
        from pyspark.sql.functions import spark_partition_id, asc, desc
        
        gooddf.printSchema()
        gooddf_count=gooddf.count()
        print('count of gooddf is ',gooddf_count)
        
        baddf_count=baddf.count()
        error_df_count=error_df.count()
        print('count of badddf is ',baddf_count)
        
        
    if error_df_count>0:
        print('error data count is greater than 0')
        error_df=error_df.withColumn('tracking_id',lit(job_run_id))
        error_df=error_df.withColumn('batchId',lit(-1))
        error_df=error_df.withColumn('curr_time',current_timestamp())
        error_df.write.format('jdbc').option('url',url).option('dbtable','T_LOG_error_reason_data').option('user',sqlusername).option('password',sqlPassword).mode('append').save()
    if baddf_count>0:
        print('baddf count is grrater than 0')
        display(baddf)
        mv.fn_move_baddf_silver(baddf,path,FileTemplate,uf)
        keycolumn=config_dict['deltalake_configs']['KeyColumns']
        dbwriter.fn_add_alerts(key,'DQF_FAILURE_RECORDS','',job_run_id+'-'+FNT_ID,'')
    if gooddf_count>0:
        print('gooddf count is greater than 0')
        act_target_path=path['Silver-Success']
        targetpath=act_target_path+FileTemplate
        print("targetpath ",targetpath)
        print('calling the delta lake function here')
        print('masking obj is created')
        maskdf=gooddf
        print('masking completed')
        deltaload=DeltaTableLoad(config_dict,targetpath,maskdf,spark1)
        print('obj for deltaload created and calling table_load func')
        deltaload.table_load()
    act_to_dl_layer_path=path['Silver-Success']
    json2={'file_id':0,'filepath':act_to_dl_layer_path,'fnt_id':key}
    dbwriter.fn_update_delta_logs_new(file=json2,job_id=job_run_id,to_dl_layer=dest_dl_layer,\
                                   to_dl_layer_path=act_to_dl_layer_path,validation_status='completed',\
                                   copy_activity_status='completed',ref_tracking_ids=ref_tracking_ids[key])
    print("updated status for good df")
                #For reconciliation logs
    expected_rows=dbread.fn_get_no_rows(ref_tracking_ids[key],key)
    print ("expected_rows",expected_rows)
    print(badrowscount)
    dbwrite.fn_insert_delta_summary_logs(ref_tracking_ids[key],expected_rows,gooddf_count,baddf_count,track_id)
     

# COMMAND ----------

# MAGIC %md
# MAGIC from pyspark.sql.types import StructType    
# MAGIC import json
# MAGIC
# MAGIC # Save schema from the original DataFrame into json:
# MAGIC schema_json = '{"fields":[{"metadata":{},"name":"Eventid","nullable":true,"type":"string"},{"metadata":{},"name":"Identifier","nullable":true,"type":"string"},{"metadata":{},"name":"EventName","nullable":true,"type":"string"},{"metadata":{},"name":"timestamp","nullable":true,"type":"string"},{"metadata":{},"name":"timezone","nullable":true,"type":"string"},{"metadata":{},"name":"plant","nullable":true,"type":"string"},{"metadata":{},"name":"line_no","nullable":true,"type":"string"},{"metadata":{},"name":"station_no","nullable":true,"type":"string"},{"metadata":{},"name":"process_no","nullable":true,"type":"string"},{"metadata":{},"name":"batch_no","nullable":true,"type":"string"},{"metadata":{},"name":"part_no","nullable":true,"type":"string"},{"metadata":{},"name":"product_family","nullable":true,"type":"string"},{"metadata":{},"name":"DMC","nullable":true,"type":"string"},{"metadata":{},"name":"Result_State","nullable":true,"type":"string"},{"metadata":{},"name":"_corrupt_record","nullable":true,"type":"string"},{"metadata":{},"name":"Source_file","nullable":true,"type":"string"},{"metadata":{},"name":"Tracking_Id","nullable":true,"type":"string"}],"type":"struct"}'
# MAGIC # Restore schema from json:

# COMMAND ----------

# MAGIC %md
# MAGIC new_schema = StructType.fromJson(json.loads(schema_json))
# MAGIC
# MAGIC plain=spark.read.csv('/mnt/bronze/DeviceSimulator/Cache/IN//AE90138F-1C7A-452B-BB44-EA136C494EF2-105_40',header=True)
# MAGIC newdata=plain.select([c for c in plain.columns if c not in {'Sequence within Line'}])
# MAGIC newdata.write.csv('/mnt/bronze/DeviceSimulator/Cache/IN//6FA028D5-DB54-4D57-99C1-D4B6E14E5D1E_3222345678')
# MAGIC print('count of data is',plain.count())
# MAGIC final_data=spark.read.schema(new_schema).option('mode','PERMISSIVE')\
# MAGIC                              .csv('/mnt/bronze/DeviceSimulator/Cache/IN/6FA028D5-DB54-4D57-99C1-D4B6E14E5D1E_3222345678',header=True)

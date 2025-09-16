import uuid
import pandas as pd
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp

#delete below imports
# from .f_utilityfunctions import utilityfunction as utf
# from .f_dbreader import Dbreader
# from .f_dbwriters import Dbwriters
# from .f_dbconfigreader import Dbconfigreaders
# from .f_delta_table_load import DeltaTableLoad
# from .f_movefiles import Movefiles
# from .f_attributevalidator4 import AttributeValidator
# from .f_filereader2 import masterdata
# from .f_datamasking import Data_masking
# from .commonfunc.f_databaseconnect import DBconnection
# from .commonfunc.f_logs import commonlogs

from .F_UtilityFunctions import utilityfunction as utf
from .F_Dbreader import Dbreader
from .F_Dbwriters import Dbwriters
from .F_Dbconfigreader import Dbconfigreaders
from .F_delta_table_load import DeltaTableLoad
from .F_Movefiles import Movefiles
from .F_AttributeValidator4 import AttributeValidator
from .F_filereader2 import masterdata
from .F_datamasking import Data_masking
from .F_databaseconnect import DBconnection
from .F_logs import commonlogs


class DQFValidator:

    def __init__(self, SourceSystem, HierarchyFlag, IOTFlag, FNT_ID, FileTemplate) -> None:
        self.SourceSystem = SourceSystem
        self.HierarchyFlag = HierarchyFlag
        self.IOTFlag = IOTFlag
        self.FNT_ID = FNT_ID
        self.FileTemplate = FileTemplate

    def validate(self):
        job_run_id = str(uuid.uuid4())
        pipeline_run_id = str(uuid.uuid4())

        # Start Spark session
        spark1 = SparkSession.builder.appName("dqf-validator").getOrCreate()
        spark1.conf.set("spark.sql.legacy.timeParserPolicy", "EXCEPTION")
        spark1.conf.set("spark.sql.shuffle.partitions", "auto")

        # Get DB connection details from secrets
        # server = spark1._jvm.dbutils.secrets.get("fof-prd-scope", "EDA-SQLDB-ServerName")
        # database = spark1._jvm.dbutils.secrets.get("fof-prd-scope", "EDA-SQLDB-DBName")
        # sqlusername = spark1._jvm.dbutils.secrets.get("fof-prd-scope", "EDA-SQLDB-SQLusername")
        # sqlPassword = spark1._jvm.dbutils.secrets.get("fof-prd-scope", "EDA-SQLDB-DBPassword")
        from . import get_sparkutils
        utils = get_sparkutils.getsparkutils(spark1)
        dbutils = utils.dbutils

        server = dbutils.secrets.get(scope="fof-prd-scope", key="EDA-SQLDB-ServerName")
        database = dbutils.secrets.get(scope="fof-prd-scope", key="EDA-SQLDB-DBName")
        sqlusername = dbutils.secrets.get(scope="fof-prd-scope", key="EDA-SQLDB-SQLusername")
        sqlPassword = dbutils.secrets.get(scope="fof-prd-scope", key="EDA-SQLDB-DBPassword")
        url = f"jdbc:sqlserver://{server};databaseName={database}"

        source_dl_layer = "Bronze"
        dest_dl_layer = "Silver"

        # DB connection and readers/writers
        dbasecon = DBconnection(database=database, server=server, spark1=spark1)
        con = dbasecon.fn_get_connection()
        dbread = Dbreader(con)
        dbwrite = Dbwriters(con)

        dbwriter = commonlogs(
            dbasecon,
            sourceName=self.SourceSystem,
            dest_dl_layer=dest_dl_layer,
            key="DQFValidation",
            FNT_ID=self.FNT_ID,
            job_run_id=job_run_id,
            HierarchyFlag=self.HierarchyFlag,
            FileTemplate=self.FileTemplate,
            spark1=spark1,
        )

        # Get list of files for DQF validation
        list_of_batches = dbread.fn_get_files_for_dqf(self.FNT_ID)
        configreader = Dbconfigreaders(con, self.FNT_ID, source_dl_layer, dest_dl_layer, self.SourceSystem)
        config_dict = configreader.getall_configs()
        uf = utf(con, source_dl_layer, dest_dl_layer, self.SourceSystem)
        path = config_dict["path"]
        mv = Movefiles(dbwrite, uf, config_dict, source_dl_layer, dest_dl_layer, path, self.FileTemplate, spark1, self.FNT_ID, dbwriter, self.SourceSystem)

        if len(list_of_batches) > 0:
            batches_files = (
                pd.DataFrame.from_records(list_of_batches)
                .groupby(["FNT_Id"])[["File_Id", "To_DL_Layer"]]
                .apply(lambda g: g.values.tolist())
                .to_dict()
            )
            ref_tracking_ids_temp = (
                pd.DataFrame.from_records(list_of_batches)
                .groupby(["FNT_Id"])["Tracking_Id"]
                .apply(lambda g: set(g.values.tolist()))
                .to_dict()
            )
            ref_tracking_ids = {a: "|".join([c for c in b]) for a, b in ref_tracking_ids_temp.items()}
        else:
            batches_files = {}

        for key, value in batches_files.items():
            check = config_dict["dqf_needed"]
            DQF_Check = check["DQF_Needed"]

            act_from_dl_layer_path = path["Bronze-Success"]
            json1 = {"file_id": 0, "filepath": act_from_dl_layer_path, "fnt_id": key}
            dbwriter.fn_insert_delta_logs(
                file=json1,
                job_id=job_run_id,
                pipeline_run_id=pipeline_run_id,
                from_dl_layer=source_dl_layer,
                ref_tracking_ids=ref_tracking_ids[key],
            )

            fnt_info = config_dict["file_read_configs"]
            File_Type = fnt_info["File_Type"]

            if File_Type in ["csv", "txt", "json", "xml", "parquet"]:
                act_temp_file_path = path["Bronze-Cache"]
                track_id = job_run_id + "-" + key
                av = AttributeValidator(
                    config=config_dict,
                    temp_file_path=act_temp_file_path,
                    temp_file_name=job_run_id + "_" + key,
                    spark=spark1,
                    job_run_id=job_run_id,
                )
                msdata = masterdata(
                    dbwrite,
                    dbread,
                    job_run_id,
                    ref_tracking_ids[key],
                    config_dict,
                    value,
                    self.IOTFlag,
                    spark1,
                    mv,
                    track_id,
                )
                data = msdata.fn_readFiles()
            else:
                data = None

            if data is None:
                act_to_dl_layer_path = path["Bronze-Error"]
                json3 = {"file_id": 0, "filepath": act_to_dl_layer_path, "fnt_id": key}
                dbwriter.fn_update_delta_logs_new(
                    file=json3,
                    job_id=job_run_id,
                    to_dl_layer=source_dl_layer,
                    to_dl_layer_path=act_to_dl_layer_path,
                    validation_status="completed",
                    ref_tracking_ids=ref_tracking_ids[key],
                )
                gooddf_count = baddf_count = error_df_count = 0

            elif not DQF_Check:
                gooddf_count = data.count()
                gooddf = uf.fn_addindex(data)
                baddf_count = error_df_count = 0

            else:
                data = uf.fn_addindex(data)
                baddf, gooddf, error_df = av.fn_getattributesValidation(data)
                gooddf_count = gooddf.count()
                baddf_count = baddf.count()
                error_df_count = error_df.count()

            if error_df_count > 0:
                error_df = error_df.withColumn("tracking_id", lit(job_run_id))
                error_df = error_df.withColumn("batchId", lit(-1))
                error_df = error_df.withColumn("curr_time", current_timestamp())
                error_df.write.format("jdbc").option("url", url).option(
                    "dbtable", "T_LOG_error_reason_data"
                ).option("user", sqlusername).option("password", sqlPassword).mode("append").save()

            if baddf_count > 0:
                mv.fn_move_baddf_silver(baddf, path, self.FileTemplate, uf)
                keycolumn = config_dict["deltalake_configs"]["KeyColumns"]
                dbwriter.fn_add_alerts(key, "DQF_FAILURE_RECORDS", "", job_run_id + "-" + self.FNT_ID, "")

            if gooddf_count > 0:
                act_target_path = path["Silver-Success"]
                targetpath = act_target_path + self.FileTemplate
                maskdf = Data_masking(gooddf, config_dict, spark1).data_mask()
                deltaload = DeltaTableLoad(config_dict, targetpath, maskdf, spark1)
                deltaload.table_load()

            act_to_dl_layer_path = path["Silver-Success"]
            json2 = {"file_id": 0, "filepath": act_to_dl_layer_path, "fnt_id": key}
            dbwriter.fn_update_delta_logs_new(
                file=json2,
                job_id=job_run_id,
                to_dl_layer=dest_dl_layer,
                to_dl_layer_path=act_to_dl_layer_path,
                validation_status="completed",
                copy_activity_status="completed",
                ref_tracking_ids=ref_tracking_ids[key],
            )

            expected_rows = dbread.fn_get_no_rows(ref_tracking_ids[key], key)
            dbwrite.fn_insert_delta_summary_logs(
                ref_tracking_ids[key], expected_rows, gooddf_count, baddf_count, job_run_id + "-" + key
            )

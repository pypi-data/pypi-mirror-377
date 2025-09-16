from delta.tables import DeltaTable
import pyspark.sql.functions as F
from pyspark.sql import Window
from pyspark.sql.functions import spark_partition_id, asc, desc
from pyspark.sql import SparkSession



class DeltaTableLoad:
    def __init__(self, config, targetpath, gooddf, spark):
        self.targetpath = targetpath
        # self.databasename = "silver." + config["deltalake_configs"]["DbName"]
        # print(self.databasename)
        # self.tablename = config["deltalake_configs"]["TabelName"]
        # print(self.tablename)

        self.databasename = "data_nexus_dev.silver"
        print(self.databasename)
        self.tablename =config["deltalake_configs"]["DbName"]+ "_" +config["deltalake_configs"]["TabelName"]
        print(self.tablename)

        # print ("self.partition is ",self.partition)
        self.mod_df = gooddf.withColumn("current_time", F.current_timestamp())
        self.DbLoadType = config["deltalake_configs"]["DbLoadType"]
        self.Duplicate_Check = config["dqf_needed"]["Duplicatecheck_Needed"]
        print("Duplicate check value ", self.Duplicate_Check)
        self.spark = spark
        self.configs = config["deltalake_configs"]
        self.fnt_id = config["file_read_configs"]["FNT_Id"]
        self.scd_enabled = config["file_read_configs"]["SCD_Enabled"]
        if self.configs["KeyColumns"] is not None and self.configs["KeyColumns"] != "":
            self.key = self.configs["KeyColumns"].split(",")
        else:
            self.key = None
        if (
            self.configs["PartitionColumns"] is not None
            and self.configs["PartitionColumns"] != ""
        ):
            self.partitioncolumn = self.configs["PartitionColumns"].split(",")
        else:
            self.partitioncolumn = None
            print("partitioncolumn is ", self.partitioncolumn)
        if (
            self.configs["WaterMarkColumns"] is not None
            and self.configs["WaterMarkColumns"] != ""
        ):
            self.WaterMarkColumns = self.configs["WaterMarkColumns"].split(",")
        else:
            self.WaterMarkColumns = None
        if self.configs["SCD_Column"] is not None and self.configs["SCD_Column"] != "":
            self.scdcolumn = self.configs["SCD_Column"].split(",")
        else:
            self.scdcolumn = None

    def fn_get_key(self):
        Key = ""
        for i in range(len(self.key)):
            if len(self.key) == 1 or i == len(self.key) - 1:
                Key += "d." + self.key[i] + " = " + "dt." + self.key[i]
            else:
                Key += "d." + self.key[i] + " = " + "dt." + self.key[i] + " and "
        print(Key)
        return Key

    def fn_get_scd_key(self):
        Key = ""
        for i in range(len(self.scdcolumn)):
            if len(self.scdcolumn) == 1 or i == len(self.scdcolumn) - 1:
                Key += "d." + self.scdcolumn[i] + " != " + "dt." + self.scdcolumn[i]
            else:
                Key += (
                    "d."
                    + self.scdcolumn[i]
                    + " != "
                    + "dt."
                    + self.scdcolumn[i]
                    + " or "
                )
        print(Key)
        return "(" + Key + ")"


    def fn_delta_load_append(self):
        cols = ["Source_file", "Tracking_Id", "Id", "column_success", "current_time"]
        self.mod_df = self.mod_df.drop(*cols)
        if self.partitioncolumn is None:
            print("append load without partioning is to be done")
            print("insde  append load")
            self.mod_df.write.format("delta").mode("append").option(
                "path", self.targetpath
            ).saveAsTable(self.databasename + "." + self.tablename)
        else:
            print("append load with partioning is to be done")

            self.mod_df.repartition(*self.partitioncolumn).write.format(
                "delta"
            ).partitionBy(self.partitioncolumn).mode("append").option(
                "path", self.targetpath
            ).saveAsTable(
                self.databasename + "." + self.tablename
            )

        # print("delta table appended successfully")
        loadStats = self.fn_get_stats()
        return loadStats

    def fn_delta_load_full(self):
        cols = ["Source_file", "Tracking_Id", "id", "column_success", "current_time"]
        self.mod_df = self.mod_df.drop(*cols)
        print("insde full load")
        if self.partitioncolumn is None:
            print("Full load without partioning is to be done")
            self.mod_df.write.format("delta").mode("overwrite").saveAsTable(
                self.databasename + "." + self.tablename
            )
        else:
            print("Full load with partioning is to be done")
            self.mod_df.repartition(*self.partitioncolumn).write.format(
                "delta"
            ).partitionBy(self.partitioncolumn).mode("overwrite").saveAsTable(
                self.databasename + "." + self.tablename
            )
        """
        self.mod_df.repartition('state','currency_code').write.format("delta").partitionBy('state','currency_code').mode("overwrite")\
                            .option("path",self.targetpath).saveAsTable(self.databasename+'.'+self.tablename)
        """
        loadStats = self.fn_get_stats()
        return loadStats

    def fn_delta_load_merge(self):
        Key = self.fn_get_key()

        temp_table = "newtesttable" + self.fnt_id
        self.mod_df.createOrReplaceGlobalTempView(temp_table)
        app = SparkSession.builder.getOrCreate()  # noqa: F821
        print(app.__dict__)
        # self.mod_df.show()
        self.spark.sql("show tables in  default").show()

        # df.show()
        col_query = f"show columns from {self.databasename}.{self.tablename}"
        df_cols = self.spark.sql(col_query)
        pyLst = df_cols.select("col_name").toPandas()["col_name"].tolist()
        print("pyLst is ", pyLst)
        # pyLst.remove('current_time')
        update_qry = ",".join(
            [
                f"d.{a}=dt.{a}"
                for a in pyLst
                if a
                not in [
                    "created_time",
                    "modified_time",
                    "start_date",
                    "end_date",
                    "current_status",
                ]
            ]
        )

        print("update_qry ", update_qry)
        insert_qry_colpart = ",".join(
            [
                f"{a}"
                for a in pyLst
                if a
                not in [
                    "created_time",
                    "modified_time",
                    "start_date",
                    "end_date",
                    "current_status",
                ]
            ]
        )
        insert_qry_colpart = (
            insert_qry_colpart
            + ","
            + "start_date"
            + ","
            + "end_date"
            + ","
            + "current_status"
        )
        insert_qry_valpart = ",".join(
            [
                f"dt.{a}"
                for a in pyLst
                if a
                not in [
                    "created_time",
                    "modified_time",
                    "start_date",
                    "end_date",
                    "current_status",
                ]
            ]
        )
        insert_qry_valpart = (
            insert_qry_valpart + "," + "current_timestamp()" + "," + "null" + "," + "1"
        )
        update_scd_qry = "d.end_date=current_timestamp(),current_status=0"

        unique_key = self.key[0]
        print(self.scd_enabled)
        if self.scd_enabled == 1:
            scd_Key = self.fn_get_scd_key()
            full_qry = f"MERGE INTO {self.databasename}.{self.tablename} d USING \
                ( select {unique_key} as mergekey,* from global_temp.{temp_table} \
                     union all\
                     select null as mergekey,d.* from  global_temp.{temp_table} d \
                        join {self.databasename}.{self.tablename} dt on {Key} and {scd_Key} and\
                     current_status=1)dt \
                        ON d.{unique_key}=dt.mergekey \
                        WHEN MATCHED AND {scd_Key} then\
                        update set {update_scd_qry}\
                        WHEN MATCHED AND CURRENT_STATUS=1 THEN \
                          UPDATE SET {update_qry} \
                        WHEN NOT MATCHED \
                          THEN INSERT ({insert_qry_colpart}) VALUES ({insert_qry_valpart}) \
                        "
        else:
            full_qry = f"MERGE INTO {self.databasename}.{self.tablename} d USING global_temp.{temp_table} dt \
                        ON {Key} \
                        WHEN MATCHED THEN \
                          UPDATE SET {update_qry} \
                        WHEN NOT MATCHED \
                          THEN INSERT ({insert_qry_colpart}) VALUES ({insert_qry_valpart}) \
                        "

        print("complete qry is", full_qry)
        self.spark.sql(full_qry)
        loadStats = self.fn_get_stats()
        return loadStats

    def fn_delta_load(self):
        print("inside inc load")
        self.spark.sql("SET spark.databricks.delta.schema.autoMerge.enabled=true")

        if self.DbLoadType == "append":
            print("calliing append function")
            deltaLoad_apped = self.fn_delta_load_append()
            print("completed apped load type")
        elif self.DbLoadType == "full":
            deltaLoad_full = self.fn_delta_load_full()
        else:
            deltaLoad_merge = self.fn_delta_load_merge()
            print(deltaLoad_merge)
            print("Delta table incremental load completed")

    def table_load(self):
        # self.fn_retain_latest_of_duplicates()
        print(
            "does table exist",
            self.spark._jsparkSession.catalog().tableExists(
                self.databasename + "." + self.tablename
            ),
        )
        if self.spark._jsparkSession.catalog().tableExists(
            self.databasename + "." + self.tablename
        ):
            self.fn_delta_load()
        else:
            print("Delta Table does not exist")

    def fn_get_stats(self):
        print(f"inside merge stats {self.databasename}.{self.tablename}")

        deltatable = DeltaTable.forName(
            self.spark, f"{self.databasename}.{self.tablename}"
        )

        stats = deltatable.history(1)
        ls = stats.select(F.col("operationMetrics")).collect()

        
        # print(s)
        print("listrr-----", ls)
        return {
            a: b.strip()
            for a, b in ls[0][0].items()
            if a
            in [
                "numOutputRows",
                "numTargetRowsInserted",
                "numTargetRowsUpdated",
                "numTargetRowsDeleted",
            ]
        }
        # self.fn_one_time_load()

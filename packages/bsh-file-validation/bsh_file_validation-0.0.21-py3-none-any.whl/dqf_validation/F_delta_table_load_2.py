from delta.tables import DeltaTable
import pyspark.sql.functions as F


class DeltaTableLoad:
    def __init__(self, config, targetpath, gooddf, spark):
        self.targetpath = targetpath
        self.databasename = config["deltalake_configs"]["DbName"]
        print(self.databasename)
        self.tablename = config["deltalake_configs"]["TabelName"]
        print(self.tablename)

        # print ("self.partition is ",self.partition)
        self.mod_df = gooddf.withColumn("current_time", F.current_timestamp())
        self.DbLoadType = config["deltalake_configs"]["DbLoadType"]
        self.Duplicate_Check = config["dqf_needed"]["Duplicatecheck_Needed"]
        print("Duplicate check value ", self.Duplicate_Check)
        self.spark = spark
        self.configs = config["deltalake_configs"]
        self.fnt_id = config["file_read_configs"]["FNT_Id"]
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

    """
    def fn_one_time_load(self):
         try:
            create_stat="create database if not exists " + self.databasename
            print(create_stat)
            spark.sql(create_stat)
            if self.partition is None:
                print('insode one time')
                self.new_df.write.format("delta").mode("overwrite")\
                .option("path",self.targetpath).saveAsTable(self.databasename+'.'+self.tablename)
            else :
            self.new_df.write.format("delta").partitionBy(self.partition).mode("overwrite").option("path",self.targetpath).saveAsTable(self.databasename+'.'+self.tablename)
            print("Delta table is created")
        return True
         except Exception as e:
             print('error is',e)
"""

    def fn_get_key(self):
        Key = ""
        for i in range(len(self.key)):
            if len(self.key) == 1 or i == len(self.key) - 1:
                Key += "d." + self.key[i] + " = " + "dt." + self.key[i]
            else:
                Key += "d." + self.key[i] + " = " + "dt." + self.key[i] + " and "
        print(Key)
        return Key

    def fn_delta_load_append(self):
        print("inside delta load append function")
        self.mod_df.write.format("delta").mode("append").saveAsTable(
            self.databasename + "." + self.tablename
        )
        print("delta table appended successfully")
        loadStats = self.fn_get_stats()
        return loadStats

    def fn_delta_load_full(self):
        if self.partitioncolumn is None:
            print("Full load without partioning is to be done")
            self.mod_df.write.format("delta").mode("overwrite").option(
                "path", self.targetpath
            ).saveAsTable(self.databasename + "." + self.tablename)
        else:
            print("Full load with partioning is to be done")
            self.mod_df.write.format("delta").partitionBy(self.partitioncolumn).mode(
                "overwrite"
            ).option("path", self.targetpath).saveAsTable(
                self.databasename + "." + self.tablename
            )
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
        # print("mod_df count",self.mod_df.count())
        # df=self.spark.sql("select * from global_temp.newtesttable")
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
                if a not in ["created_time", "modified_time"]
            ]
        )
        # update_qry=update_qry+",d.modified_time=current_timestamp()"
        print("update_qry ", update_qry)
        insert_qry_colpart = ",".join(
            [f"{a}" for a in pyLst if a not in ["created_time", "modified_time"]]
        )
        # insert_qry_colpart=insert_qry_colpart+','+'created_time'+','+'modified_time'
        insert_qry_valpart = ",".join(
            [f"dt.{a}" for a in pyLst if a not in ["created_time", "modified_time"]]
        )
        # insert_qry_valpart=insert_qry_valpart+','+'current_timestamp()'+','+'current_timestamp()'
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

        deltaTable = DeltaTable.forPath(self.spark, self.targetpath)
        print(deltaTable)
        if self.DbLoadType == "append":
            print("calling delta append fuction")
            deltaLoad = self.fn_delta_load_append()
            print("data appended successfully")
        elif self.DbLoadType == "full":
            deltaLoad = self.fn_delta_load_full()

        else:
            deltaLoad = self.fn_delta_load_merge()
            print(deltaLoad)
            print("Delta table incremental load completed")

    """
    def fn_retain_latest_of_duplicates(self):
        print('insode dup fn')
        print(self.key)
    #ls_of_key_cols=[F.col(a) for a in self.key.split(',')]
        ls_of_key_cols=self.key
        if self.WaterMarkColumns is not None:
            desc_wat_col=F.col(self.WaterMarkColumns[0]).desc()
        else:
            desc_wat_col=F.col(self.key[0]).desc()

        self.new_df = self.mod_df.withColumn("row_number",F.row_number().
                                    over(Window.partitionBy(ls_of_key_cols).orderBy(desc_wat_col))).filter(F.col("row_number")==1).drop("row_number")
        return self.new_df
        """

    def table_load(self):
        # self.fn_retain_latest_of_duplicates()
        print(
            "does table exist",
            self.spark._jsparkSession.catalog().tableExists(
                self.databasename, self.tablename
            ),
        )
        if self.spark._jsparkSession.catalog().tableExists(
            self.databasename, self.tablename
        ):
            self.fn_delta_load()
        else:
            print("Delta Table does not exist")

    def fn_get_stats(self):
        print(f"inside merge stats {self.databasename}.{self.tablename}")

        deltatable = DeltaTable.forName(
            self.spark, f"{self.databasename}.{self.tablename}"
        )
        #     deltatable=DeltaTable.forName(spark,f'sac_dwc.{self.tablename}')
        stats = deltatable.history(1)
        ls = stats.select(F.col("operationMetrics")).collect()
        # print(ls)
        # s=({a:b.strip() for a,b in ls[0][0].items() if a in ls})
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

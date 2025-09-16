import json
from pyspark.sql import DataFrame
from pyspark.sql import functions as func
from functools import reduce


class Movefiles:
    def __init__(
        self,
        dbasecon,
        uf,
        config,
        source_dl_layer,
        dest_dl_layer,
        path,
        fileTemplate,
        spark,
        FNT_ID,
        dbwriter,
        SourceSystem,
    ):
        self.dbcon = dbasecon
     
        self.config = config
        self.SourceSystem = SourceSystem
        # self.dbname = 'silver.'+self.config["deltalake_configs"]["DbName"]
        # self.tablename = self.config["deltalake_configs"]["TabelName"]

        self.dbname = "data_nexus_dev.silver"
        self.tablename =config["deltalake_configs"]["DbName"]+ "_" +config["deltalake_configs"]["TabelName"]
        

        self.spark = spark
        self.schema = config["schema"]
        self.sc = self.spark.sparkContext
        self.schema_df = self.spark.read.json(
            self.sc.parallelize([json.dumps(self.schema)])
        )
        self.columns = (
            self.schema_df.filter("operation='column'")
            .rdd.map(lambda a: a["Expected_Columnname"])
            .collect()
        )
        self.source_dl_layer = source_dl_layer
        self.dest_dl_layer = dest_dl_layer
        self.path = path
        self.FNT_ID = FNT_ID
        self.dbasecon = uf
        self.FileTemplate = fileTemplate
        self.dbw = dbwriter
        self.DBFS_PREFIX = 'dbfs:'

    def get_dbutils(self):
        try:
            from pyspark.dbutils import DBUtils

            dbutils = DBUtils(self.spark)
        except ImportError:
            import IPython

            dbutils = IPython.get_ipython().user_ns["dbutils"]
        return dbutils

    def fn_move_file(self, srcpath, destPath):
        dbutils = self.get_dbutils()
        print("src and dest are", srcpath, destPath)
 
        if srcpath.startswith("/dbfs/"):
            actual_src_path = srcpath.replace("/dbfs/", "dbfs:/")
        else:
            actual_src_path = self.DBFS_PREFIX + srcpath
   
        if destPath.startswith(self.DBFS_PREFIX):
            actual_destpath = destPath
        else:
            actual_destpath = self.DBFS_PREFIX + destPath

        # shutil.move('/dbfs/'+sourcemount+'/'+sourcepath+'/'+filename,'/dbfs/'+destinationmount+'/'+destinationpath+'/'+filename)
        dbutils.fs.mv(actual_src_path, actual_destpath)
        return srcpath, destPath



    def fn_move_error_files(self, filepath, ref_tracking_id, file_id):
        dict_mv = {}
        srcpath = filepath

        file = filepath[1]

        x = file.split("/")
        print("x is", x)
        filename = x[len(x) - 1]
        hie_folder = self.dbasecon.fn_put_datepartition()

        dest_reqpath = self.path["Bronze-Error"]
        destpath = dest_reqpath + self.FileTemplate + hie_folder + filename
        print("src and dest path are", srcpath, destpath)
        srcpath, destpath = self.fn_move_file(srcpath[1], destpath)
        print("File moved to error path")
        dict_mv["filename"] = filename
        dict_mv["destpath"] = destpath
        dict_mv["ref_tracking_id"] = ref_tracking_id
        dict_mv["file_id"] = file_id

        self.dbw.fn_add_alerts(
            self.FNT_ID,
            "DQF_FAILURE_RECORDS",
            "The tracking id is " + (ref_tracking_id),
        )
        print("Error alerts updated successfully")
        return dict_mv

    def fn_consolidateErrors(self, baddf):
        print("keys are", baddf.keys())
        allkeys = [a + "_success" for a in baddf.keys()]
        allkeys.append("Column_success")
        newbaddf = {}
        for k, v in baddf.items():
            print("key is", k)
            missed = set(allkeys) - set(v.columns)
            print("missed is", missed)
            for val in missed:
                v = v.withColumn(val, func.lit(True))

            newbaddf[k] = v
            # print(newbaddf.count())
            print("after adding", v.columns)
            add_col = ["Source_file", "Tracking_Id"]
        return reduce(
            DataFrame.unionByName,
            [
                a.select(sorted(self.columns + allkeys + add_col))
                for a in newbaddf.values()
            ],
        )

    def fn_move_baddf_silver(self, badrows_df, path, FileTemplate,uf):
        errpath = self.path["Silver-Error"]
        folder_date = self.dbasecon.fn_put_datepartition()
        print(folder_date)

        path1 = errpath + FileTemplate

        badrows_df = badrows_df.select(
            [func.col(column).cast("string") for column in badrows_df.columns]
        )
        #print("table_name is", table_name)
        badrows_df.repartition(100).write.format("delta").mode("append").option(
            'path', path1
        ).option('overwriteSchema', 'true').saveAsTable(self.dbname+'.'+self.tablename+'_baddfdata')

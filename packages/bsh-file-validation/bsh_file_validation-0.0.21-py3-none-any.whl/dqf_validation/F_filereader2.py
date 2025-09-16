import json
from .F_csvtxtreader import csvtxtdatareader
from .F_jsonreader import jsonreader
from .F_xmlreader import xmldatareader
from .F_parquetreader import parquetreader
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType
)
from pyspark.sql import functions as func
from .F_json_2reader import json2reader
from pyspark.sql.functions import input_file_name, col, concat, lit
from pyspark.sql.window import Window


class masterdata:
    def __init__(
        self,
        dbwrite,
        dbread,
        tracking_id,
        ref_tracking_ids,
        config,
        list_of_files,
        IOTFlag,
        spark,
        mvfl,
        track_id,
    ):
        self.dbwrite = dbwrite
        self.dbread = dbread
        self.spark = spark
        self.track_id = track_id
        self.duplicate_rows = 0
        self.fnt_id = config["file_read_configs"]["FNT_Id"]
        self.File_Schema = config["file_read_configs"]["Expected_Schema"]
        self.Duplicatecheck_Needed = config["file_read_configs"][
            "Duplicatecheck_Needed"
        ]
        self.expected_timestamp_col = config["file_read_configs"][
            "expected_timestamp_col"
        ]
        self.configs = config["deltalake_configs"]
        if self.configs["KeyColumns"] is not None and self.configs["KeyColumns"] != "":
            self.key = self.configs["KeyColumns"].split(",")
        self.mov = mvfl
        
        self.job_run_id = tracking_id
        self.ref_tracking_ids = ref_tracking_ids
        self.header = config["file_read_configs"]["is_header_present"]
        self.delimiter = config["file_read_configs"]["delimiter"]
        self.schema = config["schema"]
        self.repartition = config["file_read_configs"]["repartition"]
        self.IOTFlag = IOTFlag
        self.spark = spark
        self.sc = self.spark.sparkContext
        self.schema_df = self.spark.read.json(
            self.sc.parallelize([json.dumps(self.schema)])
        )
        self.xmlroottag = config["file_read_configs"]["xmlroottag"]
        self.xmldetailstag = config["file_read_configs"]["xmldetailstag"]
        # print("schema_df is ",self.schema_df)
        self.list_of_files = list_of_files
        # print("list_of_files ",list_of_files)
        selcolumns = (
            self.schema_df.filter("operation='column'")
            .rdd.map(lambda a: a["Expected_Columnname"])
            .collect()
        )
        print(selcolumns)
        self.fileType = config["file_read_configs"]["File_Type"]
        self.file_read_configs = config["file_read_configs"]
        self.csv_obj = csvtxtdatareader(self.header, self.delimiter, self.spark)
        self.json_obj = jsonreader(self.schema_df, self.IOTFlag)
        self.json_obj2 = json2reader(self.spark, self.sc)
        self.xml_obj = xmldatareader(
            self.xmlroottag,
            self.xmldetailstag,
            self.File_Schema,
            self.fnt_id,
            self.spark,
        )
        self.parquet_obj = parquetreader(self.header, self.spark)
        self.function_mapper = {
            "jsondata_32": self.json_obj2.jsondata_32,
            "jsondata_55": self.json_obj2.jsondata_55,
            "jsondata_96": self.json_obj2.jsondata_96,
        }
        self.function_mapper_parq = {
            "api_1_109": self.parquet_obj.api_1_109,
            "api_4_113": self.parquet_obj.api_4_113,
            "api_7_115": self.parquet_obj.api_7_115,
            "api_3_112": self.parquet_obj.api_3_112,
            "api_6_114": self.parquet_obj.api_6_114,
            "api_9_116": self.parquet_obj.api_9_116,
            "api_8_117": self.parquet_obj.api_8_117,
            "db_1": self.parquet_obj.db_1,
            "fn_read_parquet": self.parquet_obj.fn_read_parquet,
        }
        self.schema1 = StructType(
            [
                StructField("file_id", StringType(), True),
                StructField("filepath", StringType(), True),
            ]
        )
        self.id_path = self.spark.sparkContext.parallelize(self.list_of_files)

    def fn_readFiles(self):
        
        # print('path',self.filePath)
        dataframe = None
        print(dataframe)
        data = self.fn_masterdata()
        return data

    def fn_masterdata(self):
        expected_length = self.dbread.fn_get_no_columns_new(self.fnt_id)
        all_files = []
        dict_error = {}
        json_data = []
        error_data = []
        for file in self.list_of_files:
            all_files.append(file[1])
        print("all file paths are---", all_files)
        if self.fileType == "json":
            print("inside filereader at json function")
            tempdat = self.function_mapper[self.file_read_configs["data_func"]](
                all_files
            )
            print("data in temp data")
        elif self.fileType == "csv" or self.fileType == "txt":
            tempdat = self.csv_obj.fn_readcsv_txt(all_files)
        elif self.fileType == "xml":
            tempdat = self.xml_obj.fn_readxml(all_files)
        elif self.fileType == "parquet":
            tempdat = self.function_mapper_parq[self.file_read_configs["data_func"]](
                all_files
            )
            
        print("data in tempdata")

        # add source filename for each row
        print("temp dataframe is")
        
        # tempdat.show()

        if self.fileType == "parquet":
            tempdata1 = tempdat.withColumn("Source_file", input_file_name())
            tempdata1 = tempdata1.withColumn(
                "Source_file", func.regexp_replace(col("Source_file"), "dbfs:", "")
            )
            tempdata1 = tempdata1.withColumn(
                "Source_file", func.regexp_replace(col("Source_file"), "/part.*$", "/")
            )
            row_cnt = tempdata1.count()
            print("total rows", row_cnt)
            tempdata2 = tempdata1.groupBy("Source_file").agg(
                func.count("*").alias("row_cnt")
            )
            tempdata2 = tempdata2.withColumn(
                "filename",
                concat(func.expr("reverse(split(Source_file,'/'))[1]"), lit("/")),
            )

        else:
            tempdata1 = tempdat.withColumn("Source_file", input_file_name())
            # replacing dbfs: with ''
            # tempdata1.show()
            tempdata1 = tempdata1.withColumn(
                "Source_file", func.regexp_replace(col("Source_file"), "dbfs:", "")
            )
           
            # tempdata_1.show()
            row_cnt = tempdata1.count()
            print("total rows", row_cnt)
            # aggregating row count for each source file
            tempdata2 = tempdata1.groupBy("Source_file").agg(
                func.count("*").alias("row_cnt")
            )
            # extracting file name
            tempdata2 = tempdata2.withColumn(
                "filename", func.expr("reverse(split(Source_file,'/'))[0]")
            )
            # creating new df based on file id and filepath
        id_path_df = self.spark.createDataFrame(self.id_path, self.schema1)
        # id_path_df.show()
        # tempdata2.show()
        # joining 2 dfs based on filepaths
        joined_df = tempdata2.join(
            id_path_df, tempdata2["Source_file"] == id_path_df["filepath"], "inner"
        )
        print(joined_df)
        print("df is")
        print(self.list_of_files)
        # tempdata2.show()
        # id_path_df.show()
        # joined_df.show()
        # adding tracking id column for final dataframe
        final_tempdata = tempdata1.withColumn("Tracking_Id", lit(str(self.job_run_id)))
        final_df = final_tempdata
        rows = joined_df.collect()
        list_of_dicts = []
        for row in rows:
            dict_row = row.asDict()
            list_of_dicts.append(dict_row)
        print("list_of_dicts info:", list_of_dicts)
        for i in list_of_dicts:
            dict_data = {}
            dict_data["filename"] = i["filename"]
            dict_data["row_cnt"] = i["row_cnt"]
            dict_data["file_id"] = i["file_id"]
            json_data.append(dict_data)
        print("json_data", json_data)
        self.dbwrite.fn_update_row_cnt_new(json_data)
        if self.Duplicatecheck_Needed == 1:
            w = Window.partitionBy(self.key).orderBy(
                func.desc(self.expected_timestamp_col)
            )
            final_tempdata = (
                final_tempdata.withColumn("rn", func.row_number().over(w))
                .filter("rn = 1")
                .drop("rn")
            )
            self.duplicate_rows = final_df.count() - final_tempdata.count()
            final_df = final_tempdata
        dict_error["ref_tracking_ids"] = self.ref_tracking_ids
        dict_error["error_row_cnt"] = 0
        dict_error["duplicate_data_cnt"] = self.duplicate_rows
        dict_error["expected_length"] = expected_length
        dict_error["Tracking_Id"] = self.track_id
        error_data.append(dict_error)
        print("error_data", error_data)
        self.dbwrite.fn_update_error_row_cnt_new(error_data)
        final_df.persist()
        return final_df

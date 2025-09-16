import json
from .F_csvtxtreader import csvtxtdatareader
from .F_jsonreader import jsonreader
from .F_xmlreader import xmldatareader
from .F_parquetreader import parquetreader
from pyspark.sql.types import (
    StructType
)
from functools import reduce  # For Python 3.x
from pyspark.sql import DataFrame
from pyspark.sql.functions import lit
from .F_json_2reader import json2reader


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
    ):
        self.dbwrite = dbwrite
        self.dbread = dbread
        self.spark = spark
        self.fnt_id = config["file_read_configs"]["FNT_Id"]
        self.File_Schema = config["file_read_configs"]["Expected_Schema"]
        self.mov = mvfl
        
        self.job_run_id = tracking_id
        self.ref_tracking_ids = ref_tracking_ids
        self.header = config["file_read_configs"]["is_header_present"]
        self.delimiter = config["file_read_configs"]["delimiter"]
        self.schema = config["schema"]
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
        self.columns = (
            self.schema_df.filter("operation='column'")
            .rdd.map(lambda a: a["Expected_Columnname"])
            .collect()
        )
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
        self.parquet_obj = parquetreader(self.header)
        self.function_mapper = {
            "jsondata_32": self.json_obj2.jsondata_32,
            "jsondata_55": self.json_obj2.jsondata_55,
            "jsondata_96": self.json_obj2.jsondata_96,
        }

    def fn_readFiles(self):
        
        dataframe = None
        print(dataframe)
        data = self.fn_masterdata()
        return data

    def fn_masterdata(self):
        def unionall(*dfs):
            return reduce(DataFrame.unionall, dfs)

            # Create an empty RDD

        emp_RDD = self.spark.sparkContext.emptyRDD()
        # Create empty schema
        columns = StructType([])
        # Create an empty RDD with empty schema
        data_df = self.spark.createDataFrame(data=emp_RDD, schema=columns)
        Totaldata = []
        error_row_cnt = 0
        json_data = []
        error_data = []
        errorstatus_data = []
        expected_length = self.dbread.fn_get_no_columns_new(self.fnt_id)
        dict_error = {}
        dict_error["error_row_cnt"] = 0
        for file in self.list_of_files:

            dict_data = {}

            print("file is ", file)

            filepath = file[1]
            print('--------------',filepath)
            x = filepath.split("/")
            print('2---------------',x)
            file_id = file[0]
            filename = x[len(x) - 1]
            if self.fileType == "json":
                print("inside filereader at json function")
                tempdata = self.function_mapper[self.file_read_configs["data_func"]](
                    filepath
                )
                print("data in temp data")
            elif self.fileType == "csv" or self.fileType == "txt":
                tempdata = self.csv_obj.fn_readcsv_txt(filepath)
            elif self.fileType == "xml":
                tempdata = self.xml_obj.fn_readxml(filepath)
            elif self.fileType == "parquet":
                tempdata = self.parquet_obj.fn_read_parquet(filepath)
            
            
            tempdata.createOrReplaceTempView("abc")
            row_cnt = self.spark.sql("select count(*) from abc").first()[0]
            
            print("row_cnt", row_cnt)
            dict_data["filename"] = filename
            dict_data["row_cnt"] = row_cnt
            dict_data["file_id"] = file_id
            print("dict_dtaa", dict_data)
            json_data.append(dict_data)
            # self.dbwrite.fn_update_row_cnt(filename,row_cnt,file_id)
            actual_length = len(tempdata.columns)
            print("actual_length_type", type(actual_length))
            
            print("expected_length_type", type(expected_length))
            # if (actual_length != expected_length):
            print("Actual_length", actual_length)
            print("Expected_length", expected_length)

            #   else:
            # print("Actual length in else",actual_length)
            result = self.fn_checkcolumnnames(tempdata) #, file, file_id)
            if result:
                print("inside result")
                act_tempdata = tempdata.withColumn(
                    "Source_file", lit(str(filepath))
                ).withColumn("Tracking_Id", lit(str(self.job_run_id)))
                
                
                Totaldata.append(act_tempdata)
                dict_error["ref_tracking_ids"] = self.ref_tracking_ids
                dict_error["error_row_cnt"] = (
                    dict_error["error_row_cnt"] + error_row_cnt
                )
                dict_error["expected_length"] = expected_length
                

            else:
                print("inside else")
                error_row_cnt = error_row_cnt + tempdata.count()
                data_mov = self.mov.fn_move_error_files(
                    file, self.ref_tracking_ids, file_id
                )

                errorstatus_data.append(data_mov)
                dict_error["ref_tracking_ids"] = self.ref_tracking_ids
                dict_error["error_row_cnt"] = (
                    dict_error["error_row_cnt"] + error_row_cnt
                )
                dict_error["expected_length"] = expected_length

        if len(errorstatus_data) > 0:
            print("ho")
            self.dbwrite.fn_update_error_status_new(errorstatus_data)
        self.dbwrite.fn_update_row_cnt_new(json_data)
        print("before insert delta_logs")

        error_data.append(dict_error)
        print("error_data----------", error_data)
        self.dbwrite.fn_update_error_row_cnt_new(error_data)
        print("updated error row count")
        if len(Totaldata) > 0:
            data_ua = unionall(*Totaldata)
            # display(data)
        else:
            data_ua = None
        # data.persist()
        print("return final dataframe from filereader module")
        return data_ua

    def fn_checkcolumnnames(self, dataframe):
        columns_expected = set(
        self.schema_df.filter("Is_Mandatory_Column='1'")
        .select("Expected_Columnname")
        .rdd.flatMap(lambda x: x)
        .collect()
        )

        columns_actual = set(dataframe.columns)
        print("Columns Expected:", columns_expected)
        print("Columns Actual:", columns_actual)

        return columns_expected.issubset(columns_actual)
        
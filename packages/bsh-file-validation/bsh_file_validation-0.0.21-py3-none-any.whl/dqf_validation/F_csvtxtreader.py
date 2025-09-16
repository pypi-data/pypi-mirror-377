from .F_UtilityFunctions import utilityfunction
from functools import reduce
from pyspark.sql.functions import col, lit
from pyspark.sql import DataFrame

class csvtxtdatareader:
    def __init__(self, header, delimiter, spark):
        self.header = header
        self.delimiter = delimiter
        self.spark = spark

    def fn_readcsv_txt(self, filepath):
        header = "true" if self.header else "false"
        print(header)
        print("filepath", filepath)
        # self.spark.conf.set("spark.sql.legacy.timeParserPolicy","LEGACY")
        # file1=[]
        # for i in filepath:
        # filepath=i.replace('/dbfs/','/')
        # data=self.spark.read.option('inferSchema','true').option('delimter',"'"+str(self.delimiter)+"'").option('header',header).csv(filepath)
        data = (
            self.spark.read.format("csv")
            .option("inferSchema", "true")
            .option("header", "true")
            .option("multiline", "true")
            .load(filepath)
        )
        print("insder csvtxt")
        data.printSchema()
        return data

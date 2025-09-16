from pyspark.sql import functions as f
from pyspark.sql.functions import explode


class json2reader:
    def __init__(self, spark, sc):
        self.spark = spark
        self.sc = sc

    def jsondata_32(self, filepath):
        print("jsondata_32")
        filepath = filepath.replace("/dbfs/", "/")
        vals = (
            self.sc.wholeTextFiles(filepath)
            .values()
            .flatMap(
                lambda a: [
                    '{"EnqueuedTimeUtc":' + val if i > 0 else val
                    for i, val in enumerate(a.split('\r\n{"EnqueuedTimeUtc":'))
                ]
            )
        )
        # print(vals)
        df = self.spark.read.json(vals).select("Body.*")

        return df

    def jsondata_55(self, filepath):
        print("jsondata_55")
        filepath = filepath.replace("/dbfs/", "/")
        df1 = self.spark.read.format("json").option("multiLine", True).load(filepath)
        df2 = df1.select(explode(f.col("people")))
        df3 = df2.select(f.col("col.*"))
        return df3

    def jsondata_96(self, filepath):
        print("jsondata_96")
        print(filepath)
        #filepath = filepath.replace("/dbfs/", "/")
        df1 = self.spark.read.format("json").option("multiLine", True).load(filepath)
        # df1.show(5)
        print("return from jsondata_96 function")
        return df1

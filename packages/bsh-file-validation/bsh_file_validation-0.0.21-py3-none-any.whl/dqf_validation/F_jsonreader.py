import ast
from pyspark.sql.functions import explode


class jsonreader:
    def __init__(self, schema_df, IOTFlag):
        self.schema_df = schema_df
        self.IOTFlag = IOTFlag

    def fn_iot_json(self, filepath, string):
        # print("FNT_ID" ,self.fnt_id)
        vals = (
            sc.wholeTextFiles(filepath)  # noqa: F821
            .values()
            .flatMap(
                lambda a: [
                    '{"EnqueuedTimeUtc":' + val if i > 0 else val
                    for i, val in enumerate(a.split('\r\n{"EnqueuedTimeUtc":'))
                ]
            )
        )
        df = spark.read.json(vals)  # noqa: F821
        data = vals.first()
        BodyMessage = data.split("Body", 1)[1]
        cols_list = BodyMessage.replace('":{', "{").replace("}}", "}")
        print("file path is", filepath)
        # print('col list is',cols_list)
        dictionary = ast.literal_eval(cols_list)
        body_columns = dictionary.keys()
        df_columns = list(body_columns)
        appended_cols = [string + "." + x for x in df_columns]
        # print("df",appended_cols)
        df_json = df.select(appended_cols)
        return df_json

    def fn_readjson(self, filepath):
        """
        This function is for reading json files
        """
        # File location and type
        # file_location = "/FileStore/tables/data.json"
        # file_type = "json"
        # read the file
        # print('filepath',filepath)
        filepath = filepath.replace("/dbfs/", "/")
        if self.IOTFlag == "True":
            string = "Body"
            df = self.fn_iot_json(filepath, string)
            return df
        else:
            df = spark.read.option("multiline", "True").json(filepath)  # noqa: F821
            # display(df)

            # flatten the schema by performing explode if needed

            list_of_cols_explode = self.schema_df.filter("operation='explode'").select(
                "query"
            )
            print("list of cols to explode is", list_of_cols_explode.show())
            if list_of_cols_explode.count() > 0:
                for col in list_of_cols_explode.toPandas().iterrows():
                    print("isnide explode col is", col)
                    print(col[1]["query"])
                    transformed = df.withColumn(
                        col[1]["query"], explode(col[1]["query"])
                    )
            else:
                transformed = df

            # lets create a dynamic select expression based on schema file

            new_schema_df = self.schema_df.filter("operation!='explode'")
            # print(new_schema_df.toPandas().values)
            expr = [str(a[9] + " as " + a[0]) for a in new_schema_df.toPandas().values]

            # print(expr)
            complexnewdf = transformed.selectExpr(expr)
            return complexnewdf

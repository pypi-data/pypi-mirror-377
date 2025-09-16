import pyspark.sql.functions as func
import json
from itertools import chain
import builtins as bi
import functools
from functools import reduce
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
    LongType,
    DecimalType,
    BooleanType,
)
from pyspark.sql.functions import (
    concat,
    collect_list,
    col,
    explode,
    lit,
    when,
    split,
    create_map,
    length,
    to_timestamp
)
import operator


class AttributeValidator:
    def __init__(self, config, temp_file_name, temp_file_path, spark, job_run_id):
        
        self.job_run_id = job_run_id
        self.config = config
        self.schema = config["schema"]
        self.header = config["file_read_configs"]["is_header_present"]
        self.delimiter = config["file_read_configs"]["delimiter"]
        self.attributes = config["list_of_attributes"]
        self.spark = spark
        self.sc = self.spark.sparkContext
        self.schema_df = self.spark.read.json(
            self.sc.parallelize([json.dumps(self.schema)])
        )
        self.schema1 = StructType(
            [
                StructField("id", StringType()),
                StructField("column_success", StringType()),
            ]
        )

        self.columns = (
            self.schema_df.filter("operation='column'")
            .rdd.map(lambda a: a["Expected_Columnname"])
            .collect()
        )
        self.fileType = config["file_read_configs"]["File_Type"]
        self.fnt_id = config["file_read_configs"]["FNT_Id"]
        self.temp_file_name = temp_file_name
        self.temp_file_path = temp_file_path
        self.att_df = self.spark.read.json(
            self.sc.parallelize([json.dumps(self.attributes)])
        )
        
        self.schema3 = StructType(
            [
                StructField("id", StringType()),
                StructField("column", StringType()),
                StructField("Validationtype", StringType()),
            ]
        )
        

        self.function_mapper = {
            "CheckNull": self.fn_filternulls,
            "length": self.fn_checklength,
            "Datatype": self.fn_validate_schema_precision_Scale,
            "DateFormatCheck": self.fn_check_date_time_format,
            "CheckRegex": self.fn_checkregex,
            "check_value_length": self.fn_check_column_value_length,
            "Checkuniquerow": self.fn_check_unique_column_values,
            "Check_required_values": self.fn_check_column_values,
            "CheckColumnCount": self.fn_checkcolumnsum,
            "check_value_range": self.fn_checkcolumn_value_range,
        }
        self.order_of_validation = {
            1: "CheckNull",
            2: "length",
            3: "Datatype",
            4: "DateFormatCheck",
            5: "CheckRegex",
            6: "check_value_length",
            7: "Checkuniquerow",
            8: "Check_required_values",
            9: "CheckColumnCount",
            10: "check_value_range",
        }

    def fn_filternulls(self, flattened_df, strings):
        non_nullable_columns = (
            self.schema_df.filter("Is_Nullable=0")
            .rdd.map(lambda a: a["Expected_Columnname"])
            .collect()
        )
        print("non nullable columns are ", non_nullable_columns)
        null_dict = {}
        if len(non_nullable_columns) > 0:

            matches = [elem for elem in non_nullable_columns if elem in strings]
            for a in matches:
                cond = functools.reduce(operator.or_, [col(a).isNull()])
                null_success_df = flattened_df.select(col("id"), col(a)).withColumn(
                    "null_success", when(cond, False).otherwise(True)
                )
                df = null_success_df.filter(~col("null_success"))
                var = df.select(col("id")).rdd.flatMap(lambda x: x).collect()
                if len(var) != 0:
                    null_dict[a] = (
                        df.select(col("id")).rdd.flatMap(lambda x: x).collect()
                    )
            # print(null_dict)

        return null_dict

    def fn_checklength(self, data, strings):
        # data.show(5)
        df_columns = self.att_df.filter("File_Attribute_Name='length'").select(
            explode(split("Columnnames", "[,]")).alias("Columns")
        )
        # df_columns.show(20)
        length_dict = self.schema_df.select(
            "Expected_Columnname", "Expected_Length"
        ).rdd.collectAsMap()
        mapping_expr = create_map([lit(x) for x in chain(*length_dict.items())])
        df_col_len = df_columns.withColumn("length", mapping_expr[col("Columns")])
        # ls_columns_int_string.show(20)
        ls_columns_int_string_filtered = df_col_len.filter(
            df_columns.Columns.isin(strings)
        )
        collength_dict = ls_columns_int_string_filtered.rdd.collectAsMap()
        
        
        length_dict = {}
        for alias, max_length in collength_dict.items():
            cond = functools.reduce(operator.or_, [length(col(alias)) > max_length])
            len_success_df = data.select(col("id"), col(alias)).withColumn(
                "length_success", when(cond, False).otherwise(True)
            )
            df = len_success_df.filter(~col("length_success"))
            var = df.select(col("id")).rdd.flatMap(lambda x: x).collect()
            if len(var) != 0:
                length_dict[alias] = (
                    df.select(col("id")).rdd.flatMap(lambda x: x).collect()
                )
        # print(length_dict)

        return length_dict

    def fn_check_date_time_format(self, data, strings):
        # data.show(5)
        df_columns = self.att_df.filter("File_Attribute_Name='DateFormatCheck'").select(
            explode(split("Columnnames", "[,]")).alias("Columns")
        )
        # df_columns.show(20)
        datetime_dict = self.schema_df.select(
            "Expected_Columnname", "Expected_DatetimeFormat"
        ).rdd.collectAsMap()
        mapping_expr = create_map([lit(x) for x in chain(*datetime_dict.items())])
        df_col_date = df_columns.withColumn("dateformat", mapping_expr[col("Columns")])
        # ls_columns_int_string.show(20)
        ls_columns_int_string_filtered = df_col_date.filter(
            df_columns.Columns.isin(strings)
        )
        date_formats = ls_columns_int_string_filtered.rdd.collectAsMap()
        
        
        
        date_dict = {}
        for alias, dtformat in date_formats.items():
            cond = functools.reduce(
                operator.or_, [to_timestamp(col(alias), dtformat).isNull()]
            )
            print("cond is", cond)
            len_success_df = data.select(col("id"), col(alias)).withColumn(
                "date_success", when(cond, False).otherwise(True)
            )
            df = len_success_df.filter(~col("date_success"))
            var = df.select(col("id")).rdd.flatMap(lambda x: x).collect()
            if len(var) != 0:
                date_dict[alias] = (
                    df.select(col("id")).rdd.flatMap(lambda x: x).collect()
                )
        # print(date_dict)
        return date_dict

    def fn_validate_schema_precision_Scale(self, data, strings):
        if self.fnt_id == "32":
            struct_type = self.fn_write_to_temp_path(
                data.select(
                    [c for c in data.columns if c not in {"Sequence within Line"}]
                )
            )
        else:
            struct_type = self.fn_write_to_temp_path(data)
        
        print("temp path is", self.temp_file_path + "/" + self.temp_file_name)
        plain = self.spark.read.schema(struct_type).csv(
            self.temp_file_path + "/" + self.temp_file_name, header=True
        )
        # print('count of data is',plain.count())
        print("plain data is", plain)
        print("plain schema is", plain.schema)
        print("file name", self.temp_file_path + "/" + self.temp_file_name)
        length_dict = {}
        final_data = (
            self.spark.read.schema(struct_type)
            .option("primitivesAsString", True)
            .option("mode", "PERMISSIVE")
            .csv(
                self.temp_file_path + "/" + self.temp_file_name,
                header=True,
                multiLine=False,
            )
        )
        
        print("DATA IN DATTPE")
        # data.show()
        print("FINAL DATA")
        # final_data.show()
        # ,multiLine=True, escape='"'
        # final_data_filled=final_data.withColumn('Datatype_success',when(col('_corrupt_record').isNull(),True).otherwise(False))
        final_data_filled = final_data.withColumn(
            "Datatype_success",
            when(col("_corrupt_record").isNull(), True).otherwise(False),
        )
        datatype_success_df, datatype_failure_df = final_data_filled.filter(
            col("Datatype_success")
        ).drop("_corrupt_record"), final_data_filled.filter(
            ~col("Datatype_success")
        ).drop(
            "_corrupt_record"
        )
        datatype_success_df.show()
        var = datatype_failure_df.select(col("id")).rdd.flatMap(lambda x: x).collect()
        if len(var) != 0:
            length_dict["datatypefailed"] = (
                datatype_success_df.select(col("id")).rdd.flatMap(lambda x: x).collect()
            )
        return length_dict

    def fn_checkregex(self, data, strings):
        # data.show(5)
        df_columns = self.att_df.filter("File_Attribute_Name='CheckRegex'").select(
            explode(split("Columnnames", "[,]")).alias("Columns")
        )
        # df_columns.show(20)
        datetime_dict = self.schema_df.select(
            "Expected_Columnname", "Expected_Regex"
        ).rdd.collectAsMap()
        mapping_expr = create_map([lit(x) for x in chain(*datetime_dict.items())])
        ls_columns_regex = df_columns.withColumn("regex", mapping_expr[col("Columns")])
        ls_columns_regex_filtered = ls_columns_regex.filter(
            df_columns.Columns.isin(strings)
        )
        column_names = ls_columns_regex_filtered.rdd.collectAsMap()
        reg_df1 = self.spark.createDataFrame([], StructType([]))
        reg_df1.show()
        # print(column_names)
        regex_dict = {}
        for columns, regex in column_names.items():
            print("regex-columns", columns)
            cond = functools.reduce(operator.or_, [(col(columns)).rlike(regex)])
            reg_success_df = data.select(col("id"), col(columns)).withColumn(
                "regex_success", when(cond, True).otherwise(False)
            )
            df = reg_success_df.filter(~col("regex_success"))
            var = df.select(col("id")).rdd.flatMap(lambda x: x).collect()
            if len(var) != 0:
                regex_dict[columns] = (
                    df.select(col("id")).rdd.flatMap(lambda x: x).collect()
                )
        print("regex_completed")
        return regex_dict

    def fn_check_column_value_length(self, data, strings):
        # data.show(5)
        df_columns = self.att_df.filter(
            "File_Attribute_Name='check_value_length'"
        ).select(explode(split("Columnnames", "[,]")).alias("Columns"))
        # df_columns.show(20)
        length_dict = self.schema_df.select(
            "Expected_Columnname", "Expected_Length"
        ).rdd.collectAsMap()
        mapping_expr = create_map([lit(x) for x in chain(*length_dict.items())])
        df_col_len = df_columns.withColumn("length", mapping_expr[col("Columns")])
        ls_columns_int_string_filtered = df_col_len.filter(
            df_columns.Columns.isin(strings)
        )
        column_names = ls_columns_int_string_filtered.rdd.collectAsMap()
        # print(column_names)
        colvalue_length = {}
        for columns, max_length in column_names.items():
            cond = functools.reduce(
                operator.or_,
                [(length(col(columns)) < 3) | (length(col(columns)) > max_length)],
            )
            columnvalues_success_df = data.select(col("id"), col(columns)).withColumn(
                "valuelen_success", when(cond, False).otherwise(True)
            )
            df = columnvalues_success_df.filter(~col("valuelen_success"))
            var = df.select(col("id")).rdd.flatMap(lambda x: x).collect()
            if len(var) != 0:
                colvalue_length[columns] = (
                    df.select(col("id")).rdd.flatMap(lambda x: x).collect()
                )
        # print(colvalue_length)
        return colvalue_length

    def fn_check_unique_column_values(self, data, strings):
        # data.show(20)
        unique_columns_df = data.distinct()
        dup_columns_df = data.exceptAll(data.drop_duplicates())
        unique_col_failure_df1 = dup_columns_df.withColumn(
            "Checkuniquerow_success", lit("false").cast(BooleanType())
        )
        unique_col_failure_df = unique_col_failure_df1.withColumn(
            "Column_success", lit("check_unique_column_values").cast(StringType())
        )
        return unique_col_failure_df, unique_columns_df

    def fn_check_column_values(self, data, strings):
        # data.show(5)

        ls_columns_string1 = self.att_df.filter(
            "File_Attribute_Name='Check_required_values'"
        ).select(explode(split("Columnnames", "[,]")).alias("Columns"))
        start_val = self.schema_df.select(
            "Expected_Columnname", "Expected_startvalue"
        ).rdd.collectAsMap()
        end_val = self.schema_df.select(
            "Expected_Columnname", "Expected_endvalue"
        ).rdd.collectAsMap()
        mapping_expr = create_map([lit(x) for x in chain(*start_val.items())])
        mapping_expr1 = create_map([lit(x) for x in chain(*end_val.items())])
        ls_columns_string1_df = ls_columns_string1.withColumn(
            "startvalue", mapping_expr[col("Columns")]
        )
        ls_columns_string1_df2 = ls_columns_string1_df.withColumn(
            "endvalue", mapping_expr1[col("Columns")]
        )
        #         ls_columns_string.show(20)
        ls_columns_string1_filtered = ls_columns_string1_df2.filter(
            ls_columns_string1.Columns.isin(strings)
        )
        column_name1 = ls_columns_string1_filtered.rdd.collect()
        colvalues_dict = {}
        for columns, startval, endval in column_name1:
            print("check_required_values-columns", columns)
            cond = functools.reduce(
                operator.or_,
                [
                    ((col(columns)).startswith(startval))
                    & ((col(columns)).endswith(endval))
                ],
            )
            # print(cond)
            colvalue_success_df = data.select(col("id"), col(columns)).withColumn(
                "colvalues_success", when(cond, True).otherwise(False)
            )
            df = colvalue_success_df.filter(~col("colvalues_success"))
            var = df.select(col("id")).rdd.flatMap(lambda x: x).collect()
            if len(var) != 0:
                colvalues_dict[columns] = (
                    df.select(col("id")).rdd.flatMap(lambda x: x).collect()
                )
        # print(colvalues_dict)
        print("check_required_values-completed")
        return colvalues_dict

    def fn_checkcolumnsum(self, data, strings):
        # data.show(5)
        ls_columns_int_string = self.att_df.filter(
            "File_Attribute_Name='CheckColumnCount'"
        ).select(explode(split("Columnnames", "[,]")).alias("Columns"))
        # ls_columns_int_string.show(20)
        ls_columns_int_string_filtered = ls_columns_int_string.filter(
            ls_columns_int_string.Columns.isin(strings)
        )
        columnsum_val = ls_columns_int_string_filtered.rdd.flatMap(
            lambda x: x
        ).collect()

        colsum = {}

        check_cond_df = data.withColumn(
            "ColumnSum", bi.sum(data[col] for col in columnsum_val)
        )
        
        colsum_success_df = check_cond_df.withColumn(
            "colsum_success",
            when(check_cond_df["ColumnSum"] != 10, False).otherwise(True),
        )
        df = colsum_success_df.filter(~func.col("colsum_success"))
        var = df.select(func.col("id")).rdd.flatMap(lambda x: x).collect()
        for c in columnsum_val:
            if len(var) != 0:
                colsum[c] = (
                    df.select(func.col("id")).rdd.flatMap(lambda x: x).collect()
                )
        # print(colsum)
        return colsum

    def fn_checkcolumn_value_range(self, data, strings):
        ls_column_name = self.att_df.filter(
            "File_Attribute_Name='check_value_range'"
        ).select(explode(split("Columnnames", "[,]")).alias("Columns"))
        ls_column_name_filtered = ls_column_name.filter(
            ls_column_name.Columns.isin(strings)
        )
        ls_column_name_filtered.show()
        start_range = self.schema_df.select(
            "Expected_Columnname", "Expected_startrange"
        ).rdd.collectAsMap()
        end_range = self.schema_df.select(
            "Expected_Columnname", "Expected_endrange"
        ).rdd.collectAsMap()
        mapping_expr = create_map([lit(x) for x in chain(*start_range.items())])
        mapping_expr1 = create_map([lit(x) for x in chain(*end_range.items())])
        ls_columns_string1_df = ls_column_name.withColumn(
            "start_range", mapping_expr[col("Columns")]
        )
        ls_columns_string1_df2 = ls_columns_string1_df.withColumn(
            "end_range", mapping_expr1[col("Columns")]
        )
        ls_columns_string1_filtered = ls_columns_string1_df2.filter(
            ls_column_name.Columns.isin(strings)
        )
        column_val = ls_columns_string1_filtered.rdd.collect()
        print("start_range---", start_range)
        print("end_range---", end_range)
     
        valrange_dict = {}
        for cols, start_range, end_range in column_val:
            cond = functools.reduce(
                operator.or_, [data[cols].between(start_range, end_range)]
            )
            range_success_df = data.select(col("id"), col(cols)).withColumn(
                "colvalues_success", when(cond, True).otherwise(False)
            )
            df = range_success_df.filter(~col("colvalues_success"))
            var = df.select(col("id")).rdd.flatMap(lambda x: x).collect()
            if len(var) != 0:
                valrange_dict[cols] = (
                    df.select(col("id")).rdd.flatMap(lambda x: x).collect()
                )
        # print(valrange_dict)
        return valrange_dict

    def fn_write_to_temp_path(self, data):
        
        # print('filename is',self.temp_file_name+'/'+self.temp_file_path)
        data.write.format("csv").mode("overwrite").option("header", "true").save(
            self.temp_file_path + "/" + self.temp_file_name
        )
        print("data schema--------", data.schema)
        to_prepend = [
            StructField("_corrupt_record", StringType(), True),
            StructField("Source_file", StringType(), True),
            StructField("Tracking_Id", StringType(), True),
        ]
        schema = StructType(data.schema.fields + to_prepend)
        print("schema====", schema)
        return schema

    def fn_constructStruct(self):
        schema_df = self.schema_df.filter("operation='column'")
        finallist = self.fn_consolidateSchema(schema_df)
        print("filanlist---", finallist)
        final_schema = StructType(finallist)
        print("schem in json", final_schema.json())

        return final_schema

    # create a udf
    def fn_consolidateSchema(self, df):
        ls = list()
        for a in df.rdd.collect():
            # print(a)
            ls.append(
                self.fn_map_dtype(
                    a["Expected_Columnname"],
                    a["Expected_Datatype"],
                    a["Is_Nullable"],
                    a["Expected_Length"],
                    a["Expected_Scale"],
                    a["Expected_Precision"],
                )
            )
        ls.append(StructField("_corrupt_record", StringType(), True))
        ls.append(StructField("Source_file", StringType(), True))
        ls.append(StructField("Tracking_Id", StringType(), True))
        print("list of schema is", ls)
        return ls

    def fn_map_dtype(self, name, dtype, nullable, length, scale=None, precision=None):
        print(
            "name,dtype,nullable,length,scale,precision",
            name,
            dtype,
            nullable,
            length,
            scale,
            precision,
        )
        data_type = None
        metadata = None
        nullabilty = None

        if (
            dtype == "string"
            or dtype == "UUID"
            or dtype == "varchar"
            or dtype == "nvarchar"
            or dtype == "char"
        ):
            data_type = StringType()
            
        elif dtype == "int" or dtype == "bigint" or dtype == "short":
            data_type = LongType()
            
        elif dtype == "decimal" or dtype == "float":
            data_type = DecimalType(int(precision), int(scale))
            
        elif dtype == "timestamp" or dtype == "datetime":
            data_type = StringType()
        elif dtype == "date":
            data_type = StringType()
        elif dtype == "bit" or dtype == "boolean":
            data_type = BooleanType()
        if nullable == "1":
            nullabilty = True
        elif nullable == "0":
            nullabilty = False

        if data_type is not None:
            structfield = StructField(
                name, data_type, nullable=nullabilty, metadata=metadata
            )
        return structfield

    def fn_getattributesValidation(self, data):
        # print('attributes are',self.attributes)
        goodrows_df = data
        print("insidevalidation", goodrows_df.count())
        unique = {}
        for a in self.order_of_validation.values():
            print("a is", a)
            
            # print([val['File_Attribute_Name'] for val in self.attributes])
            if a in [val["File_Attribute_Name"] for val in self.attributes]:
                b1 = [
                    val for val in self.attributes if val["File_Attribute_Name"] == a
                ][0]
                print("b1 is", b1)
                print("b1 is", type(b1))
                if b1["Validation_Needed"]:
                    print("validation---", b1["File_Attribute_Name"])
                    print("------------------------------")
                    Columnnames = b1["Columnnames"]
                    strings = Columnnames.replace(",", " ").split()

                    unique_dict = self.function_mapper[b1["File_Attribute_Name"]](
                        data, strings
                    )
                    unique[b1["File_Attribute_Name"]] = unique_dict

        print("uniqueeeeeeeeeeee")
        # print(unique)
        """
        for a,b in unique.items():
            for c,d in b.items():
                #print(a+"_"+c)
                #print('__')
                #print(c,d)
                #print("--------")
                for e in d:
                    label1=a+"_"+c
                    if e not in dict1:
                        dict1[e]=[label1]
                    else:
                        dict1[e].append(label1)
        print('after validation-')
        l=[]
        for a,b in unique.items():
            for c,d in b.items():
                for i in d:
                    l.append((i,c,a))
        """
        list1 = []
        
        for a, b in unique.items():
            for c, d in b.items():
                
                # l.append((d,c,a))

                df = self.spark.createDataFrame(d, StringType())
                df = df.withColumn("column", lit(c))
                df = df.withColumn("Validationtype", lit(a))
                list1.append(df)
        print("after lops")
        if len(list1) > 0:
            df_series = reduce(DataFrame.unionAll, list1)
            print("reduced df_series")
            print(df_series.count())

            df_series = df_series.withColumnRenamed("value", "id")
            error_df = df_series
            df1 = df_series.withColumn(
                "combined",
                concat(
                    col("Validationtype"),
                    lit(
                        "_",
                    ),
                    col("column"),
                ),
            ).drop("Validationtype", "column")

            df2 = df1.groupBy(col("id")).agg(
                collect_list(col("combined")).alias("column_success")
            )

            df = df2.withColumn("column_success", df2.column_success.cast(StringType()))
            # df.show(10)
            df.persist()
            print("dict for baddf")
            
            print("converting tuple to dataframe")
            
            
            
            print("main dataframe")
            
            # df.show()

            
            print("before baddf")
            
        

            data.printSchema()

            df = df.withColumn("id", df.id.cast(LongType()))
            df.printSchema()
            # print(data.rdd.getNumPartitions())

            good_df = (
                data.join(df, data.id == df.id, "left_outer")
                .where(df.id.isNull())
                .drop(df.id)
            )
            print("after filtering good_df")

            baddf = data.join(df, on="id")
            good_df = good_df.cache()
            print("aftering filtering baddf")
            baddf = baddf.withColumn("tracking_id", lit(self.job_run_id))
            print("baadf with tracking id")
        else:
            good_df = data
            baddf = self.spark.createDataFrame([], StructType([]))
            error_df = self.spark.createDataFrame([], StructType([]))
        return baddf, good_df, error_df

# print(baddf[a].columns)

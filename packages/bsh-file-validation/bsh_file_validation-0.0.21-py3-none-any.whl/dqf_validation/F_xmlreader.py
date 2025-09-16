from pyspark.sql.types import ArrayType, StructType
from pyspark.sql.functions import explode, col


class xmldatareader:
    def __init__(self, xmlroottag, xmldetailstag, schema, fnt_id, spark1):
        self.xmlroottag = xmlroottag
        self.xmldetailstag = xmldetailstag
        self.spark = spark1
        self.fnt_id = fnt_id
        self.fileschema = schema

    def fn_readxml(self, filepath):
        def read_nested_xml(df):
            column_list = []
            struct_found = False
            for column_name in df.schema.names:
                print("Outside isinstance loop: " + column_name)
                # Checking column type is ArrayType
                if isinstance(df.schema[column_name].dataType, ArrayType):
                    print("Inside isinstance loop of ArrayType: " + column_name)
                    df = df.withColumn(
                        column_name, explode(column_name).alias(column_name)
                    )
                    column_list.append(column_name)

                elif isinstance(df.schema[column_name].dataType, StructType):
                    struct_found = True
                    print("Inside isinstance loop of StructType: " + column_name)
                    for field in df.schema[column_name].dataType.fields:
                        column_list.append(
                            col(column_name + "." + field.name).alias(
                                column_name + "_" + field.name
                            )
                        )

                else:
                    column_list.append(column_name)
            df3 = df.select(column_list)
            return df3, struct_found

        xmldf3 = (
            self.spark.read.format("com.databricks.spark.xml")
            .option("rootTag", self.xmlroottag)
            .option("rowTag", self.xmldetailstag)
            .option("nullValue", "")
            .option("schemaLocation", self.fileschema)
            .load(",".join(filepath))
        )
        # altered by qtr1kor

        read_nested_xml_flag = True
        df, read_nested_xml_flag = read_nested_xml(xmldf3)
        while read_nested_xml_flag:
            df, read_nested_xml_flag = read_nested_xml(df)
            print(read_nested_xml_flag)
        return df

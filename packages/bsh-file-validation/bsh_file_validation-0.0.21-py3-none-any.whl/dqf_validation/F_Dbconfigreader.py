class Dbconfigreaders:
    def __init__(self, dbcon, fnt_id, source_dl_layer, dest_dl_layer, sourcename):
       
        
        self.con = dbcon
        self.fnt_id = fnt_id
        self.source_dl_layer = source_dl_layer
        self.dest_dl_layer = dest_dl_layer
        self.sourceName = sourcename

    def fn_get_schema(self):
        statement = f"""EXEC dbo.sp_get_schema_details  @fnt_id='{self.fnt_id}'"""
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        # print(res)
        results = []
        while resultSet.next():
            vals = {}
            vals["Expected_Columnname"] = resultSet.getString("Expected_Columnname")
            vals["Expected_Datatype"] = resultSet.getString("Expected_Datatype")
            vals["Expected_Length"] = resultSet.getString("Expected_Length")
            vals["Expected_Precision"] = resultSet.getInt("Expected_Precision")
            vals["Expected_Unit"] = resultSet.getString("Expected_Unit")
            vals["Expected_Type"] = resultSet.getString("Expected_Type")
            vals["Expected_Scale"] = resultSet.getInt("Expected_Scale")
            vals["Is_Nullable"] = resultSet.getString("Is_Nullable")
            vals["Is_Unique"] = resultSet.getString("Is_Unique")
            vals["operation"] = resultSet.getString("operation")
            vals["Query"] = resultSet.getString("Query")
            vals["Is_Mandatory_Column"] = resultSet.getString("Is_Mandatory_Column")
            vals["Expected_DatetimeFormat"] = resultSet.getString(
                "Expected_DatetimeFormat"
            )
            vals["Expected_Regex"] = resultSet.getString("Expected_Regex")
            vals["Expected_startvalue"] = resultSet.getString("Expected_startvalue")
            vals["Expected_endvalue"] = resultSet.getString("Expected_endvalue")
            vals["Is_Maskable"] = resultSet.getString("Is_Maskable")
            vals["Mask_Value"] = resultSet.getString("Mask_Value")
            vals["group_no"] = resultSet.getString("group_no")
            vals["Expected_startrange"] = resultSet.getString("Expected_startrange")
            vals["Expected_endrange"] = resultSet.getString("Expected_endrange")

            results.append(vals)
        exec_statement.close()
        return results

    def fn_get_list_of_attributes(self):
        statement = f"""EXEC dbo.[sp_get_mapped_schema_attributes_new] @fnt_id = {self.fnt_id}"""
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        result_dict = []
        while resultSet.next():
            vals = {}
            vals["File_Attribute_Name"] = resultSet.getString("File_attribute_Name")
            vals["Validation_Needed"] = resultSet.getBoolean("Validtion_Needed")
            vals["Validation_Type"] = resultSet.getString("Validation_Type")
            vals["Value_DataType"] = resultSet.getString("value_datatype")
            vals["Columnnames"] = resultSet.getString("Columnnames")
            vals["FK_File_Schema_Attribute_Id"] = resultSet.getString(
                "FK_File_Schema_Attribute_Id"
            )
            vals["group_no"] = resultSet.getString("group_no")
            result_dict.append(vals)
        exec_statement.close()
        # self.con.close()
        return result_dict

    def fn_get_fnt_info(self):
        statement = f"""EXEC dbo.[sp_get_fnt_info_new] @fnt_id={self.fnt_id}"""
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        
        vals = {}
        while resultSet.next():
            vals["Total_columns"] = resultSet.getInt("Total_columns")
            vals["delimiter"] = resultSet.getString("delimiter")
            vals["FNT_Id"] = self.fnt_id
            vals["is_header_present"] = resultSet.getBoolean("is_header_present")
            vals["File_Type"] = resultSet.getString("File_Type")
            vals["xmlroottag"] = resultSet.getString("xmlroottag")
            vals["xmldetailstag"] = resultSet.getString("xmldetailstag")
            vals["data_func"] = resultSet.getString("data_func")
            vals["SCD_Enabled"] = resultSet.getString("SCD_Enabled")
            vals["Expected_Schema"] = resultSet.getString("Expected_Schema")
            vals["repartition"] = resultSet.getInt("repartition")
            vals["Duplicatecheck_Needed"] = resultSet.getInt("Duplicatecheck_Needed")
            vals["expected_timestamp_col"] = resultSet.getString(
                "expected_timestamp_col"
            )
            # result_dict.append(vals)
            # Close connections
        exec_statement.close()
        # self.con.close()
        return vals

    def fn_dqf_needed(self):
        statement = f"""EXEC dbo.[sp_get_dqf_flag] @fnt_id={self.fnt_id}"""
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        while resultSet.next():
            vals = {}
            vals["DQF_Needed"] = resultSet.getBoolean("DQF_Needed")
            vals["Duplicatecheck_Needed"] = resultSet.getBoolean(
                "Duplicatecheck_Needed"
            )
            vals["Date_column"] = resultSet.getString("Date_column")
            vals["Del_duration_value"] = resultSet.getString("Del_Duration_value")
            vals["Del_duration_unit"] = resultSet.getString("Del_Duration_unit")
        exec_statement.close()
        return vals

    def fn_get_deltaLake_configs(self):
        statement = (
            f"""EXEC dbo.[sp_get_Deltatable_configs_new] @fnt_id={self.fnt_id}"""
        )
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        
        while resultSet.next():
            vals = {}
            vals["DbName"] = resultSet.getString("DbName")
            vals["TabelName"] = resultSet.getString("TabelName")
            vals["KeyColumns"] = resultSet.getString("KeyColumns")
            vals["PartitionColumns"] = resultSet.getString("PartitionColumns")
            vals["WaterMarkColumns"] = resultSet.getString("WaterMarkColumns")
            vals["DbLoadType"] = resultSet.getString("DbLoadType")
            vals["SCD_Column"] = resultSet.getString("SCD_Column")
            # result_dict.append(vals)
            # Close connections
        exec_statement.close()
        # self.con.close()
        return vals

    def cleanNullTerms(self, d):
        return {k: v for k, v in d.items() if v is not None}

    def func_get_paths(self):
        vals1 = {}
        for i in [self.source_dl_layer, self.dest_dl_layer]:
            try:
                statement = f"""
                select * from T_MST_file_path fp inner join T_MST_dl_layer la
                on la.PK_Dl_Layer_Id=fp.fk_dl_layer_id
                where la.PK_Dl_Layer_Id = (select PK_Dl_Layer_Id from T_MST_DL_layer
                where Dl_Layer_Name='{i}')
                """
                # print(statement)
                exec_statement = self.con.prepareCall(statement)
                exec_statement.execute()
                resultSet = exec_statement.getResultSet()
                
                while resultSet.next():
                    vals = {}

                    
                    vals[i + "-Success"] = resultSet.getString("Success_File_Path")
                    vals[i + "-Error"] = resultSet.getString("Error_File_Path")
                    vals[i + "-Suspense"] = resultSet.getString("Suspense_File_Path")
                    vals[i + "-Cache"] = resultSet.getString("Cache_File_path")
                   
                    # print(vals)
                    x = self.cleanNullTerms(vals)
                    vals1.update(x)
                # l.append(vals1)

            except Exception as e:
                print(e)
        exec_statement.close()
        path = {}
        for value in vals1.keys():
            
            path[value] = (
                "/Volumes/"
                + vals1[value].replace("{sourcesystem}", self.sourceName)
                + "/"
            )

        return path

    def group_info(self):
        statement = f"""EXEC [dbo].[sp_get_group_configs] @fnt_id={self.fnt_id}"""
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        dic = []
        while resultSet.next():
            vals = {}
            vals["group_number"] = resultSet.getString("group_number")
            vals["allchannels_needed"] = resultSet.getString("allchannels_needed")
            dic.append(vals)
        exec_statement.close()
        return dic

    def iot_data_configs(self):
        try:
            statement = f"""(select * from T_MST_Iot_Data_Config where FK_FNT_Id='{self.fnt_id}') """
            # print(statement)
            exec_statement = self.con.prepareCall(statement)
            exec_statement.execute()
            resultSet = exec_statement.getResultSet()

            results = [] # List to collect multiple results

            while resultSet.next():
                vals = {}
                vals["fnt_id"] = resultSet.getString("FK_FNT_Id")
                vals["connectionString"] = resultSet.getString("connectionString")
                vals["eventhubname"] = resultSet.getString("eventhubname")
                vals["consumergroup"] = resultSet.getString("consumergroup")
                vals["checkpointlocation"] = resultSet.getString("checkpointlocation")
                vals["maxBytesPerTrigger"] = resultSet.getString("maxBytesPerTrigger")
                vals["load_type"] = resultSet.getString("load_type")
                vals["DeviceId"] = resultSet.getString("DeviceId")
                vals["queryname"] = resultSet.getString("queryname")
                vals["uniquecol"] = resultSet.getString("uniquecol")
                vals["log_tablename"] = resultSet.getString("log_tablename")
                vals["errcount"] = resultSet.getString("errcount")
                vals["errrows"] = resultSet.getString("errrows")

                results.append(vals) # Add the current result to the list

            exec_statement.close()
            return vals
        except Exception as e:
            print(e)

    def fn_get_kafka_metadata(self):
        try:
            statement = f"""EXEC dbo.sp_get_kafka_metadata @fntid={self.fnt_id}"""
            exec_statement = self.con.prepareCall(statement)
            exec_statement.execute()
            resultSet = exec_statement.getResultSet()
            result_dict = []
            while resultSet.next():
                vals = {}
                vals["kafka_id"] = resultSet.getString("kafka_id")
                vals["bootstrap"] = resultSet.getString("bootstrap")
                vals["subscribe"] = resultSet.getString("subscribe")
                vals["startingOffsets"] = resultSet.getString("startingOffsets")
                vals["fnt_id"] = resultSet.getString("fk_fnt_id")
                vals["checkPointLocation"] = resultSet.getString("checkPointLocation")
                vals["load_type"] = resultSet.getString("load_type")
                result_dict.append(vals)
            # Close connections
            exec_statement.close()
            # self.con.close()
            return result_dict
        except Exception as e:
            print(e)

    def getall_configs(self):
        config_dict = {}
        columnnames = []
        fileinfo = self.fn_get_fnt_info()
        fileschema = self.fn_get_schema()
        filedelta = self.fn_get_deltaLake_configs()
        fileatt = self.fn_get_list_of_attributes()
        filedqf = self.fn_dqf_needed()
        pat = self.func_get_paths()
        iot = self.iot_data_configs()
        group_data = self.group_info()
        kafka_data = self.fn_get_kafka_metadata()
        for i in fileschema:
            columnnames.append(i["Expected_Columnname"])
        config_dict["file_read_configs"] = fileinfo
        config_dict["columns"] = columnnames
        config_dict["schema"] = fileschema
        config_dict["deltalake_configs"] = filedelta
        config_dict["list_of_attributes"] = fileatt
        config_dict["dqf_needed"] = filedqf
        config_dict["path"] = pat
        config_dict["iot"] = iot
        config_dict["group_data"] = group_data
        config_dict["kafka_configs"] = kafka_data
        return config_dict

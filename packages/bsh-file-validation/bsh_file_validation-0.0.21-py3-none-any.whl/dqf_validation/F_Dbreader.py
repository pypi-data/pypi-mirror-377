class Dbreader:
    def __init__(self, dbcon):
        self.con = dbcon
        

    def fn_get_tags_xml(self, fnt_id):
        try:
            statement = f"""EXEC dbo.sp_get_xmltags @fntid={fnt_id}"""
            exec_statement = self.con.prepareCall(statement)
            exec_statement.execute()
            resultSet = exec_statement.getResultSet()
            result_dict = []
            while resultSet.next():
                vals = {}
                result_dict.append(vals)
                # Close connections
            exec_statement.close()
            # self.con.close()
            return result_dict
        except Exception as e:
            print(e)

    def fn_get_files_for_dqf(self, fnt_id):
        try:
            statement = f"""EXEC dbo.sp_get_files_for_dqf @fntid='{fnt_id}'"""
            print("Statement is ", statement)
            exec_statement = self.con.prepareCall(statement)
            exec_statement.execute()
            resultSet = exec_statement.getResultSet()
            result_dict = []
            while resultSet.next():
                vals = {}
                vals["Tracking_Id"] = resultSet.getString("Tracking_Id")
                vals["To_DL_Layer"] = resultSet.getString("To_DL_Layer")
                vals["FNT_Id"] = resultSet.getString("FNT_Id")
                vals["job_run_id"] = resultSet.getString("job_run_id")
                vals["File_Id"] = resultSet.getString("FK_File_Id")

                result_dict.append(vals)
            # Close connections
            exec_statement.close()
            # self.con.close()
            return result_dict
        except Exception as e:
            print(e)


    def fn_get_no_columns_new(self, fntid):
        try:
            # print("fnt_id is", fntid)
            statement = f"""EXEC [dbo].[sp_get_no_columns_new] @fntid={fntid}"""
            # print("statement",statement)
            exec_statement = self.con.prepareCall(statement)
            exec_statement.execute()
            resultSet = exec_statement.getResultSet()
            while resultSet.next():
                result_dict = resultSet.getInt("Total_columns")
            exec_statement.close()
            return result_dict
        except Exception as e:
            print(e)

    def fn_get_no_rows(self, Tracking_id, fnt_id):
        try:
            statement = f"""EXEC dbo.sp_get_no_rows @Tracking_Id='{Tracking_id}',@fnt_id='{fnt_id}'"""
            print("fn_get_no_rows query is ", statement)
            exec_statement = self.con.prepareCall(statement)
            print(exec_statement.execute())
            resultSet = exec_statement.getResultSet()
            # print(resultSet)
            while resultSet.next():
                result_dict = resultSet.getInt("agg_row_cnt")
            exec_statement.close()
            return result_dict
        except Exception as e:
            print(e)

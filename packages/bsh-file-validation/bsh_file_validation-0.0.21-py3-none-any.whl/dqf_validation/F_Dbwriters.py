import json


class Dbwriters:
    def __init__(self, dbcon):
        self.con = dbcon

    def fn_update_error_status_new(self, final_json):
        statement = f"""EXEC dbo.sp_Update_Error_Status_new @json = '{json.dumps(final_json)}'"""
        print("update statement for error is ", statement)
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        print("Error file status updated")
        # time.sleep(60)
        exec_statement.close()

    def fn_update_row_cnt_new(self, final_json):
        statement = (
            f"""EXEC dbo.sp_update_row_cnt_new @json = '{json.dumps(final_json)}'"""
        )
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)

        exec_statement.close()

    def fn_update_error_row_cnt_new(self, final_json):
        statement = f"""EXEC dbo.sp_insert_delta_summary_logs_new @json = '{json.dumps(final_json)}'"""
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        # print("Error row count updated")
        exec_statement.close()

    def fn_update_error_row_cnt_mdf(self, final_json):
        statement = f"""EXEC dbo.sp_insert_delta_summary_logs_mdf1 @json = '{json.dumps(final_json)}'"""
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        # print("Error row count updated")
        exec_statement.close()

    def fn_file_info_mdf(self, final_json):
        statement = f"""EXEC dbo.sp_insert_T_file_info_mdf1 @json = '{json.dumps(final_json)}'"""
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        # print("Error row count updated")
        exec_statement.close()

    def fn_insert_delta_summary_logs_mdf(
        self, delta_tracking_id, expected_rows, gooddf_count, baddf_count, group_number
    ):
        statement = f"""
                    EXEC dbo.sp_update_delta_summary_logs_mdf
                    @delta_tracking_id='{delta_tracking_id}',
                    @expected_rows='{expected_rows}',
                    @gooddf_count='{gooddf_count}',
                    @baddf_count='{baddf_count}',
                    @group_number='{group_number}'
                    """
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        print("Delta Summary logs updated")
        exec_statement.close()

    def fn_insert_delta_summary_logs(
        self, delta_tracking_id, expected_rows, gooddf_count, baddf_count, track_id
    ):
        statement = f"""
                    EXEC dbo.sp_update_delta_summary_logs @delta_tracking_id='{delta_tracking_id}',
                    @expected_rows='{expected_rows}',@gooddf_count='{gooddf_count}',
                    @baddf_count='{baddf_count}',@Tracking_Id1='{track_id}'
                    """
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        print("Delta Summary logs updated")
        exec_statement.close()

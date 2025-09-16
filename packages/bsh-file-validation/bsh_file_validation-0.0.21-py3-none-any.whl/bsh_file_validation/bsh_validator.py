class BSHValidator:

    def __init__(self, secret_key):
        self.secret_key = "DatanexusARRDemo"
        self.user_key = secret_key
        self.check_license()
    
    def check_license(self):
        if self.user_key != self.secret_key:
            raise Exception("❌ Invalid or missing license key. Access denied.")
        print("✅ License key verified.")

        # try:
        #     resp = requests.post("https://my-license-server.com/check", json={"key": user_key})
        #     if resp.status_code != 200:
        #         raise Exception("❌ License server rejected the key.")
        #     print("✅ License verified by remote server.")
        # except Exception as e:
        #     raise Exception(f"❌ License check failed: {e}")

    def read_csv_from_sas_url(self, spark, sas_url):
        """
        Read CSV file from full SAS URL (including ?sv=...).
        """
        df = spark.read.format("csv") \
            .option("header", "true") \
            .load(sas_url)
        print("✅ Successfully read data from source.")
        return df

    def validate_columns(self, df, required_columns):
        actual_columns = df.columns
        missing = [col for col in required_columns if col not in actual_columns]
        if missing:
            print(f"❌ Validation failed. Missing columns: {missing}")
            return False
        else:
            print("✅ Validation passed. All required columns are present.")
            return True

    def validate_no_nulls(self, df, critical_columns):
        for col in critical_columns:
            null_count = df.filter(df[col].isNull() | (df[col] == '')).count()
            if null_count > 0:
                print(f"❌ Validation failed. Column '{col}' has {null_count} null or empty values.")
                return False
        print("✅ Validation passed. No nulls in critical columns.")
        return True

    def write_csv_to_sas_url(self, df, sas_url):
        """
        Write DataFrame as CSV to full SAS URL (including ?sv=...).
        """
        df.coalesce(1).write.format("csv") \
            .option("header", "true") \
            .mode("overwrite") \
            .save(sas_url)
        print(f"✅ File successfully written to: {sas_url}")
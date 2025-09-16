import requests
import json


class stream_powerbi:
    def fn_post(self, ds):
        print("no of rowas is", ds.count())
        print(ds.head(10))
        df = ds.toPandas()
        # print(df)
        df1 = df.to_dict(orient="index")
        print("dict is", df1)
        ls_of_dct = list(df1.values())
        # copy "Push URL" from "API Info" in Power BI
        url = "https://api.powerbi.com/beta/be89650a-700e-444c-afcf-972a4337d081/datasets/\
            3cf8cc89-1342-4747-a876-81b363410202/rows?\
            key=HDDVU9f2Mpib66izjyyz%2Fh3y%2FSibrJwOnWEBMJz2God12bdHQQNVDoTjBlg%2FpZDv%2FTAcvaNZDqO%2BtWj3yR4IKw%3D%3D"

        headers = {"Content-Type": "application/json"}
        try:
            response = requests.request(
                method="POST", url=url, headers=headers, data=json.dumps(ls_of_dct)
            )
        except Exception as e:
            print("error is ", e)
        else:
            print("succeded")
        # print('processed',ls_of_dct)
        print(response)

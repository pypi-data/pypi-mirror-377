import pandas
import os
import os.path
import datetime
from pyspark.sql.functions import monotonically_increasing_id


class utilityfunction:
    def __init__(self, dbcon, source_dl_layer, dest_dl_layer, sourcename):
        self.source_dl_layer = source_dl_layer
        self.dest_dl_layer = dest_dl_layer
        self.con = dbcon
        self.sourcename = sourcename

    def fn_get_list_of_paths(self, path, start, end):
        lst_files = []

        def get_dir_content(ls_path):
            print("ls path is", ls_path)
            dir_paths = dbutils.fs.ls(ls_path)  # noqa
            print("dir path is", dir_paths)
            subdir_paths = [
                get_dir_content(p.path)
                for p in dir_paths
                if p.isDir() and p.path != ls_path
            ]

            flat_subdir_paths = [p for subdir in subdir_paths for p in subdir]
            

            final_list = [
                p.path for p in dir_paths if not p.isDir()
            ] + flat_subdir_paths
            return final_list

        if start is None:
            lst_files.extend(get_dir_content(path))
            list_of_name_time = [
                {
                    "CreatedTime": datetime.fromtimestamp(
                        os.path.getctime("/" + str(f).replace(":", ""))
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "FileName": os.path.split(f)[1],
                    "FilePath": ("/" + str(f).replace(":", "")),
                }
                for f in lst_files
            ]
        else:
            time_range = pandas.date_range(start, end, freq="H")
            for val in time_range:
                day = str(val.day).zfill(2)
                month = str(val.month).zfill(2)
                year = str(val.year).zfill(4)
                hour = str(val.hour).zfill(2)
                
            
                print(f"{path}/{year}/{month}/{day}/{hour}")
                fullpath = f"{path}/{year}/{month}/{day}/{hour}"
                try:
                    lst_files.extend(get_dir_content(fullpath))
                    list_of_name_time = [
                        {
                            "CreatedTime": datetime.fromtimestamp(
                                os.path.getctime("/" + str(f).replace(":", ""))
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "FileName": os.path.split(f)[1],
                            "FilePath": ("/" + str(f).replace(":", "")),
                        }
                        for f in lst_files
                    ]
                except Exception as ex:
                    print(ex)
                    
        return list_of_name_time

    def fn_put_datepartition(self):
        current_time = datetime.datetime.now()
        return f"/{str(current_time.year).zfill(4)}/ \
                {str(current_time.month).zfill(2)}/ \
                {str(current_time.day).zfill(2)}/{str(current_time.hour).zfill(2)}/"

    def fn_addindex(self, data):
        data1 = data.withColumn("id", monotonically_increasing_id())
        return data1

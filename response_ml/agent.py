from pyspark.streaming import StreamingContext
import gzip
import pandas as pd
import json
pd.set_option('display.max_columns', None)
import numpy as np
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split




'''
helper functions
'''

def gz2df(path):
    with gzip.open(path, 'rb') as f:
        """
        Convert .gz log files into dataframe
        """
        content = f.read().decode('utf-8').split('\n')
        list_rows = []

        for i in range(len(content)-1):
            row = content[i].split(' ')
            list_rows.append(row)
        f.close()

    df = pd.DataFrame(list_rows, columns=['log_timestamp', 'data'])

    return df

def get_type(x):
    idx1 = x.find('"Type":') + 8
    idx2 = x.find(',', idx1) - 1
    rec_type = x[ idx1:idx2 ]

    return rec_type

def filter_by_rec_type(df, rec_type): 
    return df[df.rec_type == rec_type]

def explode_df(df):
    return pd.concat([df.log_timestamp, pd.json_normalize(df.data)], axis=1)



'''
actual agent
'''

if __name__ == "__main__":
    # Create a local StreamingContext with two working thread and batch interval of 15 second
    spark = SparkSession.builder.appName("ResponsAgent").getOrCreate()

    # Create DataFrame representing the stream of input lines from connection to localhost:9999    
    stream = spark.readStream.format("socket").option("host","localhost").option("port", 9999).load()

    query = stream \
    .writeStream \
    .format("console") \
    .start()

    query.awaitTermination()

    # df = gz2df(lines)
    # logging.info("data frame created")
    # df['rec_type'] = df.data.apply(get_type)
    # df['data'] = df.data.apply(json.loads)

    # list_of_df_rectypes = {}  

    # for rec_type in df.rec_type.unique():
    #     logging.info(f"rec_type: {rec_type}")
    #     rec_type_df = filter_by_rec_type(df, rec_type)
    #     df_exploded = explode_df(rec_type_df)
    #     list_of_df_rectypes[rec_type]=df_exploded

    # df_pod = list_of_df_rectypes["Pod"]
    
    # if("open5gs-upf" in df_pod.PodName.unique()):
    #     logging.info("upf data exists")
    #     upf_df = df_pod[df_pod["PodName"]=="open5gs-upf" ]

    #     ## cleaning up the nans in the dataframe

    #     print(upf_df['pod_cpu_usage_total'].isna().sum())
    #     print(len(upf_df))

    #     upf_df = upf_df.dropna(subset=['pod_cpu_usage_total', 'pod_memory_max_usage' ])

    #     ##setting the limits and requests
    #     limit_cpu = max( upf_df[["pod_cpu_usage_total"]].values.tolist() )
    #     request_cpu = np.mean( upf_df[["pod_cpu_usage_total"]].values.tolist() ) 

    #     limit_memory =  max( upf_df[["pod_memory_max_usage"]].values.tolist() )
    #     request_memory = np.mean( upf_df[["pod_memory_max_usage"]].values.tolist() ) 


    #     logging.info(f'limit_cpu: {limit_cpu}')
    #     logging.info(f'request_cpu: {request_cpu}')
    #     logging.info(f'limit_memory: {limit_memory}')
    #     logging.info(f'request_memory: {request_memory}')

# ssc.stop()
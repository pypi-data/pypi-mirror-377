# pcservices/data/utils.py

import os
import pandas as pd
import tempfile
import datetime
from google.cloud import storage
from pyspark.sql import DataFrame as SparkDataFrame

def save_spark_df_to_gcs(df: SparkDataFrame, bucket_name: str, base_name: str, subfolder: str = None):
    """
    Convert a manageable Spark DataFrame to Pandas and upload as CSV to GCS.

    Parameters:
        df (Spark DataFrame) : Spark DataFrame
        bucket_name (str)    : GCS bucket name (without gs://)
        base_name (str)      : Base file name for CSV
        subfolder (str)      : Optional GCS subfolder
    """
    # Convert Spark DataFrame to Pandas
    pandas_df = df.toPandas()

    # Prepare temporary local file path
    formatted_date = datetime.date.today().strftime("%b_%d_%Y").upper()
    local_file_path = os.path.join(tempfile.gettempdir(),
                                   f"{base_name}_{formatted_date}.csv")

    # Save locally
    pandas_df.to_csv(local_file_path, index=False)

    # Upload to GCS
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob_name = f"{subfolder}/{os.path.basename(local_file_path)}" if subfolder else os.path.basename(local_file_path)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_file_path)

    print(f"Uploaded {local_file_path} -> gs://{bucket_name}/{blob_name}")

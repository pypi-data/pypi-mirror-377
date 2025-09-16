from pyspark.sql import SparkSession

class BigQuerySparkConnector:
    def __init__(
        self,
        app_name: str,
        materialization_project: str,
        materialization_dataset: str,
        bigquery_connector_version: str = "0.36.1",
        extra_configs: dict = None,
        local_mode: bool = True,  # Flag to skip GCS in local
    ):
        """Initialize BigQuerySparkConnector with SparkSession."""
        self.app_name = app_name
        self.materialization_project = materialization_project
        self.materialization_dataset = materialization_dataset
        self.bigquery_connector_version = bigquery_connector_version
        self.extra_configs = extra_configs or {}
        self.local_mode = local_mode
        self.spark = self._create_spark_session()

    def _create_spark_session(self) -> SparkSession:
        """Create and configure SparkSession for BigQuery."""
        jars = f"com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:{self.bigquery_connector_version}"
        builder = (
            SparkSession.builder
            .appName(self.app_name)
            .config("spark.jars.packages", jars)
            .config("viewsEnabled", "true")
            .config("materializationProject", self.materialization_project)
            .config("materializationDataset", self.materialization_dataset)
        )
        # Apply any extra configs
        for k, v in self.extra_configs.items():
            builder = builder.config(k, v)

        spark = builder.getOrCreate()
        spark.sparkContext.setCheckpointDir("/tmp")
        spark.sparkContext.setLogLevel("WARN")
        return spark

    def read_table(self, table: str):
        """
        Read a BigQuery table into a Spark DataFrame and print row count.
        
        Args:
            table: BigQuery table name (project.dataset.table)
        
        Returns:
            Spark DataFrame
        """
        df = self.spark.read.format("bigquery").option("table", table).load()
        row_count = df.count()
        print(f"Loaded {row_count} rows from BigQuery table {table}", flush=True)
        return df


    def write_table(self, df, table: str, mode: str = "overwrite", temporary_gcs_bucket: str = None):
        """
        Write a Spark DataFrame to BigQuery with row count info.
        
        Args:
            df: Spark DataFrame to write
            table: BigQuery table name (project.dataset.table)
            mode: Write mode ("overwrite", "append", etc.)
            temporary_gcs_bucket: Optional GCS bucket for temporary storage
        """
        if self.local_mode:
            row_count = df.count()
            print(f"[LOCAL MODE] Skipping write: {mode.capitalize()}d {row_count} rows to {table}", flush=True)
            return

        row_count = df.count()
        writer = df.write.format("bigquery").option("table", table).mode(mode)
        if temporary_gcs_bucket:
            writer = writer.option("temporaryGcsBucket", temporary_gcs_bucket)
        writer.save()

        print(f"{mode.capitalize()}d {row_count} rows to BigQuery table {table}", flush=True)
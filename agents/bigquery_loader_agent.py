import yaml
from google.cloud import bigquery
from google.api_core.exceptions import Conflict, GoogleAPICallError

class BigQueryLoaderAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        self.config_path = config_path

        # Load BQ config
        with open(self.config_path) as f:
            self.cfg = yaml.safe_load(f)

        # Initialize BigQuery client
        self.client = bigquery.Client(project=self.cfg["project_id"])

        # Dataset & table IDs
        self.dataset_id = f"{self.cfg['project_id']}.{self.cfg['dataset']}"
        self.table_id   = f"{self.dataset_id}.{self.cfg['table']}"

        # Ensure dataset exists
        dataset = bigquery.Dataset(self.dataset_id)
        try:
            self.client.create_dataset(dataset)
            print(f"[{self.name}] Created dataset {self.dataset_id}")
        except Conflict:
            # Already exists
            pass

    def load(self, data: list) -> bool:
        if not data:
            print(f"[{self.name}] No data to load.")
            return False

        # Define schema
        schema = [
            bigquery.SchemaField("url",         "STRING"),
            bigquery.SchemaField("title",       "STRING"),
            bigquery.SchemaField("summary",     "STRING"),
            bigquery.SchemaField("fetched_at",  "TIMESTAMP"),
        ]

        # Ensure table exists
        table = bigquery.Table(self.table_id, schema=schema)
        try:
            self.client.create_table(table)
            print(f"[{self.name}] Created table {self.table_id}")
        except Conflict:
            # Table already exists
            pass

        # Insert rows
        errors = []
        try:
            errors = self.client.insert_rows_json(
                self.table_id,
                data,
                row_ids=[None] * len(data)  # let BigQuery assign unique IDs
            )
        except GoogleAPICallError as e:
            print(f"[{self.name}] API error during insert: {e}")
            return False

        if errors:
            print(f"[{self.name}] Insert errors: {errors}")
            return False

        print(f"[{self.name}] Successfully loaded {len(data)} rows into {self.table_id}")
        return True
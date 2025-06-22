import os
import yaml
from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import Conflict, GoogleAPICallError

class BigQueryLoaderAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        # Load BQ config
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)

        # Load service account credentials directly
        key_path = os.path.join(
            os.path.dirname(config_path), 
            "sa-key.json"
        )
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Service account key not found at {key_path}")
        creds = service_account.Credentials.from_service_account_file(key_path)
        self.client = bigquery.Client(
            project=self.cfg["project_id"],
            credentials=creds
        )

        # Prepare IDs
        self.dataset_id = f"{self.cfg['project_id']}.{self.cfg['dataset']}"
        self.table_id   = f"{self.dataset_id}.{self.cfg['table']}"

        # Ensure dataset exists
        ds = bigquery.Dataset(self.dataset_id)
        try:
            self.client.create_dataset(ds)
            print(f"[{self.name}] Created dataset {self.dataset_id}")
        except Conflict:
            pass  # already exists

    def load(self, data: list) -> bool:
        if not data:
            print(f"[{self.name}] No data to load.")
            return False

        # Define schema
        schema = [
            bigquery.SchemaField("url",        "STRING"),
            bigquery.SchemaField("title",      "STRING"),
            bigquery.SchemaField("summary",    "STRING"),
            bigquery.SchemaField("fetched_at", "TIMESTAMP"),
            bigquery.SchemaField("sentiment",  "FLOAT",   mode="NULLABLE"),
        ]

        # Ensure table exists
        table = bigquery.Table(self.table_id, schema=schema)
        try:
            self.client.create_table(table)
            print(f"[{self.name}] Created table {self.table_id}")
        except Conflict:
            pass  # table exists

        # Insert rows
        try:
            errors = self.client.insert_rows_json(self.table_id, data)
        except GoogleAPICallError as e:
            print(f"[{self.name}] API error during insert: {e}")
            return False

        if errors:
            print(f"[{self.name}] Insert errors: {errors}")
            return False

        print(f"[{self.name}] Successfully loaded {len(data)} rows into {self.table_id}")
        return True
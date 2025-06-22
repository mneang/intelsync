import yaml

class BigQueryLoaderAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        self.config_path = config_path

    def load(self, data):
        # Load BQ config
        with open(self.config_path) as f:
            cfg = yaml.safe_load(f)
        print(f"[{self.name}] would load {len(data)} items into "
              f"{cfg['project_id']}.{cfg['dataset']}.{cfg['table']}")
        # TODO: real BigQuery insert logic here
        return True
from agents.web_scraper_agent import WebScraperAgent
from agents.bigquery_loader_agent import BigQueryLoaderAgent
from agents.insight_generator_agent import InsightGeneratorAgent

class IntelSyncOrchestrator:
    def __init__(self, config_dir: str = "config"):
        self.scraper = WebScraperAgent("scraper", f"{config_dir}/scraper_config.yaml")
        self.loader  = BigQueryLoaderAgent("loader",  f"{config_dir}/bq_config.yaml")
        self.insights = InsightGeneratorAgent("insights", f"{config_dir}/insights_config.yaml")

    def run(self):
        print("➡️  Starting web scrape…")
        data = self.scraper.scrape()

        print("➡️  Loading data to BigQuery…")
        self.loader.load(data)

        print("➡️  Generating insights…")
        report = self.insights.generate()

        print(f"✅  Pipeline complete! Insights at: {report}")

if __name__ == "__main__":
    IntelSyncOrchestrator().run()
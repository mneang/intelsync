from google.adk import Workflow
from agents.web_scraper_agent import WebScraperAgent
from agents.bigquery_loader_agent import BigQueryLoaderAgent
from agents.insight_generator_agent import InsightGeneratorAgent

def build_workflow():
    wf = Workflow(name="IntelSync Pipeline")
    wf.add_agent(WebScraperAgent(name="scraper", config_path="config/scraper_config.yaml"))
    wf.add_agent(BigQueryLoaderAgent(name="loader", config_path="config/bq_config.yaml"))
    wf.add_agent(InsightGeneratorAgent(name="insights", config_path="config/insights_config.yaml"))
    wf.set_sequence(["scraper", "loader", "insights"])
    return wf

if __name__ == "__main__":
    build_workflow().run()
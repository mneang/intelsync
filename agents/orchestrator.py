from google_adk import Workflow
from agents.web_scraper_agent import WebScraperAgent
from agents.bigquery_loader_agent import BigQueryLoaderAgent
from agents.insight_generator_agent import InsightGeneratorAgent

def build_intelsync_workflow() -> Workflow:
    """
    Define the IntelSync multi-agent workflow:
    1. Scrape → 2. Load into BigQuery → 3. Generate Insights
    """
    workflow = Workflow(name="IntelSync Market Intel Pipeline")

    # 1. Web Scraper Agent
    workflow.add_agent(
        WebScraperAgent(
            name="scraper",
            config_path="config/scraper_config.yaml"
        )
    )

    # 2. BigQuery Loader Agent
    workflow.add_agent(
        BigQueryLoaderAgent(
            name="loader",
            config_path="config/bq_config.yaml"
        )
    )

    # 3. Insight Generator Agent
    workflow.add_agent(
        InsightGeneratorAgent(
            name="insights",
            config_path="config/insights_config.yaml"
        )
    )

    # Set agent execution order
    workflow.set_sequence(["scraper", "loader", "insights"])
    return workflow

if __name__ == "__main__":
    wf = build_intelsync_workflow()
    wf.run()
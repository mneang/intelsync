import os
import yaml
import json
from google import genai

class InsightGeneratorAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        self.config_path = config_path
        with open(self.config_path) as f:
            self.cfg = yaml.safe_load(f)
        os.makedirs(os.path.dirname(self.cfg["output_path"]), exist_ok=True)

        # Ensure GenAI uses your GCP project and location
        os.environ["GOOGLE_CLOUD_PROJECT"]     = self.cfg["project_id"]
        os.environ["GOOGLE_CLOUD_LOCATION"]    = self.cfg.get("location", "global")
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

        # Initialize the GenAI client (Vertex AI)
        self.client = genai.Client(vertexai=True)  #  [oai_citation:0‡ai.google.dev](https://ai.google.dev/gemini-api/docs/text-generation?utm_source=chatgpt.com)

    def generate(self):
        # Load scraped articles
        input_path = self.cfg["input_path"]
        with open(input_path, "r", encoding="utf-8") as fr:
            articles = json.load(fr)

        # Build prompt bullets
        bullets = [
            f"- **{art['title']}**: {art['summary'][:200]}..."
            for art in articles
        ]
        prompt = (
            f"{self.cfg['prompt_template']}\n\n"
            "Articles:\n" + "\n".join(bullets) + "\n\n"
            "Provide a concise executive summary with actionable recommendations."
        )

        # Call the model
        response = self.client.models.generate_content(
            model=self.cfg["model"],
            contents=prompt
        )
        text = response.text.strip()

        # Write out the insights
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(text + "\n")

        print(f"[{self.name}] Wrote real insights to {out_path}")
        return out_path
import os
import yaml
import json
import vertexai
from vertexai.language_models import TextGenerationModel

class InsightGeneratorAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        self.config_path = config_path
        with open(self.config_path) as f:
            self.cfg = yaml.safe_load(f)
        os.makedirs(os.path.dirname(self.cfg["output_path"]), exist_ok=True)

        # Initialize Vertex AI for Gen AI
        vertexai.init(
            project=self.cfg["project_id"],
            location=self.cfg.get("location", "us-central1")
        )  #  [oai_citation:0‡cloud.google.com](https://cloud.google.com/python/docs/reference/vertexai/latest?utm_source=chatgpt.com)

        # Load the model
        # Note: use the correct model ID, e.g. "text-bison@001"
        model_id = self.cfg.get("model", "text-bison@001")
        self.model = TextGenerationModel.from_pretrained(model_id)  #  [oai_citation:1‡cloud.google.com](https://cloud.google.com/python/docs/reference/aiplatform/1.27.0/vertexai.language_models.TextGenerationModel?utm_source=chatgpt.com)

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

        # Generate
        response = self.model.predict(
            prompt,
            temperature=0.2,
            max_output_tokens=256
        )
        text = response.text.strip()

        # Write out the insights
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(text + "\n")

        print(f"[{self.name}] Wrote real insights to {out_path}")
        return out_path
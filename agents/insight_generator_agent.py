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

        # Init Vertex AI
        vertexai.init(
            project=self.cfg["project_id"],
            location=self.cfg.get("location", "us-central1")
        )

        # Load GenAI model
        model_id = self.cfg.get("model", "text-bison@001")
        try:
            self.model = TextGenerationModel.from_pretrained(model_id)
        except Exception as e:
            print(f"[{self.name}] Warning: could not load GenAI model '{model_id}': {e}")
            self.model = None

    def generate(self):
        # Load scraped articles
        input_path = self.cfg.get("input_path", "data/sample_articles.json")
        with open(input_path, "r", encoding="utf-8") as fr:
            articles = json.load(fr)

        # Build prompt bullets
        bullets = [
            f"- **{art['title']}**: {art['summary'][:200]}..."
            for art in articles
        ]
        prompt = (
            f"{self.cfg.get('prompt_template')}\n\n"
            "Articles:\n" + "\n".join(bullets) + "\n\n"
            "Provide a concise executive summary with actionable recommendations."
        )

        text = None
        if self.model:
            try:
                response = self.model.predict(
                    prompt,
                    temperature=0.2,
                    max_output_tokens=256
                )
                text = response.text.strip()
            except Exception as e:
                print(f"[{self.name}] Warning: GenAI prediction failed: {e}")

        # Fallback summarization
        if not text:
            print(f"[{self.name}] Using fallback summarization.")
            lines = ["## Fallback Summary"]
            for art in articles:
                lines.append(f"- {art['title']}: {art['summary'][:200]}...")
            text = "\n".join(lines)

        # Write out insights
        out_path = self.cfg.get("output_path", "data/insights_summary.txt")
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(text + "\n")

        print(f"[{self.name}] Wrote insights to {out_path}")
        return out_path
import os
import yaml
import json
from google.genai import TextGenerationModel

class InsightGeneratorAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        self.config_path = config_path
        with open(self.config_path) as f:
            self.cfg = yaml.safe_load(f)
        os.makedirs(os.path.dirname(self.cfg["output_path"]), exist_ok=True)

        # Initialize the PaLM model
        model_name = self.cfg.get("model", "models/text-bison-001")
        self.model = TextGenerationModel.from_pretrained(model_name)

    def generate(self):
        # Load scraped articles
        input_path = self.cfg["input_path"]
        with open(input_path, "r", encoding="utf-8") as fr:
            articles = json.load(fr)

        # Build a concise prompt
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
        response = self.model.generate(
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=256
        )
        text = response.generations[0].text.strip()

        # Write real insights
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(text + "\n")

        print(f"[{self.name}] Wrote real insights to {out_path}")
        return out_path
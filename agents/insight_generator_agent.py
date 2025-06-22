
import os
import yaml
import json
import vertexai
from vertexai.language_models import ChatModel

class InsightGeneratorAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)
        os.makedirs(os.path.dirname(self.cfg["output_path"]), exist_ok=True)

        # Init Vertex AI
        vertexai.init(
            project=self.cfg["project_id"],
            location=self.cfg.get("location", "us-central1")
        )

        # Load the chat model
        model_id = self.cfg.get("model", "chat-bison@001")
        try:
            self.chat_model = ChatModel.from_pretrained(model_id)
        except Exception as e:
            print(f"[{self.name}] ERROR loading ChatModel '{model_id}': {e}")
            self.chat_model = None

    def generate(self):
        # Load scraped articles
        with open(self.cfg["input_path"], "r", encoding="utf-8") as fr:
            articles = json.load(fr)

        # Build system & user messages
        bullets = [
            f"- **{a['title']}**: {a['summary'][:200]}..."
            for a in articles
        ]
        system_msg = self.cfg.get("prompt_template")
        user_msg = (
            "Articles:\n" + "\n".join(bullets) +
            "\n\nProvide a concise executive summary with actionable recommendations."
        )

        text = None
        if self.chat_model:
            try:
                chat = self.chat_model.start_chat(context=system_msg)
                response = chat.send_message(user_msg, temperature=0.2)
                text = response.text.strip()
            except Exception as e:
                print(f"[{self.name}] ERROR during chat.predict: {e}")

        # Fallback if GenAI fails
        if not text:
            print(f"[{self.name}] Using fallback summarization.")
            lines = ["## Fallback Summary"] + bullets
            text = "\n".join(lines)

        # Write insights
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(text + "\n")

        print(f"[{self.name}] Wrote insights to {out_path}")
        return out_path
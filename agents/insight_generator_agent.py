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

        # Initialize Vertex AI
        vertexai.init(
            project=self.cfg["project_id"],
            location=self.cfg.get("location", "us-central1")
        )

        # Load the chat model
        model_id = self.cfg.get("model", "chat-bison@001")
        try:
            self.chat = ChatModel.from_pretrained(model_id).start_chat()
        except Exception as e:
            print(f"[{self.name}] ERROR loading ChatModel '{model_id}': {e}")
            self.chat = None

    def generate(self):
        # Load scraped articles
        with open(self.cfg["input_path"], "r", encoding="utf-8") as fr:
            articles = json.load(fr)

        # Build the message
        bullets = [
            f"- **{a['title']}**: {a['summary'][:200]}..."
            for a in articles
        ]
        system = self.cfg.get("prompt_template")
        user_msg = (
            "Articles:\n" + "\n".join(bullets) + 
            "\n\nProvide a concise executive summary with actionable recommendations."
        )

        if self.chat:
            try:
                # System + user roles
                self.chat = self.chat.start_chat(
                    context=system
                )
                response = self.chat.send_message(user_msg, temperature=0.2)
                text = response.text.strip()
            except Exception as e:
                print(f"[{self.name}] ERROR during chat.predict: {e}")
                text = None
        else:
            text = None

        # Fallback if needed
        if not text:
            print(f"[{self.name}] Using fallback summarization.")
            lines = ["## Fallback Summary"]
            lines += bullets
            text = "\n".join(lines)

        # Write out insights
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(text + "\n")

        print(f"[{self.name}] Wrote insights to {out_path}")
        return out_path
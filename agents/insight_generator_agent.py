import os
import yaml
import json
from google.cloud import language_v1

class InsightGeneratorAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)
        os.makedirs(os.path.dirname(self.cfg["output_path"]), exist_ok=True)

        # Initialize NL API client
        self.client = language_v1.LanguageServiceClient()

    def generate(self):
        # Load scraped articles
        with open(self.cfg["input_path"], "r", encoding="utf-8") as fr:
            articles = json.load(fr)

        sentiments = []
        for art in articles:
            doc = language_v1.Document(
                content=art["summary"] or art["title"],
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            result = self.client.analyze_sentiment(request={"document": doc})
            score = result.document_sentiment.score
            sentiments.append(score)
            art["sentiment"] = score

        # Build summary
        avg_sent = sum(sentiments) / len(sentiments) if sentiments else 0
        lines = [
            f"## Market Intelligence Summary",
            f"- Analyzed {len(articles)} articles.",
            f"- Average sentiment score: {avg_sent:.2f} (–1.0 negative … +1.0 positive)",
            "",
            "### Article Sentiments:",
        ]
        for art in articles:
            lines.append(f"- **{art['title']}** → sentiment: {art['sentiment']:.2f}")

        text = "\n".join(lines)

        # Write out insights
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(text + "\n")

        print(f"[{self.name}] Wrote Cloud NL–powered insights to {out_path}")
        return out_path
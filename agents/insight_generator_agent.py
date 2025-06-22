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
        # NL client
        self.client = language_v1.LanguageServiceClient()

    def generate(self):
        # 1) Load scraped articles
        input_path = self.cfg["input_path"]
        with open(input_path, "r", encoding="utf-8") as fr:
            articles = json.load(fr)

        # 2) Analyze sentiment and enrich articles
        scores = []
        for art in articles:
            doc = language_v1.Document(
                content=art["summary"] or art["title"],
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            result = self.client.analyze_sentiment(request={"document": doc})
            score = result.document_sentiment.score
            art["sentiment"] = score
            scores.append(score)
            print(f"[{self.name}] {art['title']} → sentiment: {score:.2f}")

        # 3) Overwrite sample_articles.json with sentiments
        with open(input_path, "w", encoding="utf-8") as fw:
            json.dump(articles, fw, ensure_ascii=False, indent=2)

        # 4) Build and write summary (same as before)
        avg_sent = sum(scores) / len(scores) if scores else 0
        lines = [
            "## Market Intelligence Summary",
            f"- Analyzed {len(articles)} articles.",
            f"- Average sentiment score: {avg_sent:.2f} (–1.0 negative … +1.0 positive)",
            "",
            "### Article Sentiments:"
        ]
        for art in articles:
            lines.append(f"- **{art['title']}** → sentiment: {art['sentiment']:.2f}")

        text = "\n".join(lines)
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(text + "\n")

        print(f"[{self.name}] Wrote Cloud NL–powered insights to {out_path}")
        return out_path
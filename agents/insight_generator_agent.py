import os
import yaml
import json
from google.cloud import language_v1
from google.oauth2 import service_account

class InsightGeneratorAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        # Load config
        with open(config_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)
        os.makedirs(os.path.dirname(self.cfg["output_path"]), exist_ok=True)

        # Load service account key
        key_path = os.path.join(os.path.dirname(config_path), "sa-key.json")
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Service account key not found at {key_path}")
        creds = service_account.Credentials.from_service_account_file(key_path)

        # Init NL client with credentials
        self.client = language_v1.LanguageServiceClient(credentials=creds)

    def generate(self):
        # 1) Load scraped articles
        input_path = self.cfg["input_path"]
        with open(input_path, "r", encoding="utf-8") as fr:
            articles = json.load(fr)

        # Prepare to collect entity rows
        entity_records = []
        sentiment_scores = []

        for art in articles:
            text = art.get("summary") or art.get("title", "")
            doc = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)

            # 2a) Sentiment
            sent_res = self.client.analyze_sentiment(request={"document": doc})
            score = sent_res.document_sentiment.score
            art["sentiment"] = score
            sentiment_scores.append(score)

            # 2b) Entities
            ent_res = self.client.analyze_entities(request={"document": doc})
            # take top 3 by salience
            top3 = sorted(ent_res.entities, key=lambda e: e.salience, reverse=True)[:3]
            art["entities"] = [e.name for e in top3]
            for e in top3:
                entity_records.append({
                    "title": art.get("title", ""),
                    "entity": e.name,
                    "type": language_v1.Entity.Type(e.type_).name,
                    "salience": round(e.salience, 3)
                })

            print(f"[{self.name}] {art.get('title','<no title>')} → sentiment: {score:.2f}, entities: {[e.name for e in top3]}")

        # 3) Persist enriched JSON & entities list
        with open(input_path, "w", encoding="utf-8") as fw:
            json.dump(articles, fw, ensure_ascii=False, indent=2)

        entities_path = os.path.join(os.path.dirname(input_path), "entities.json")
        with open(entities_path, "w", encoding="utf-8") as fe:
            json.dump(entity_records, fe, ensure_ascii=False, indent=2)

        # 4) Build summary text
        avg_sent = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        lines = [
            "## Market Intelligence Summary",
            f"- Analyzed {len(articles)} articles.",
            f"- Average sentiment score: {avg_sent:.2f} (–1.0 negative … +1.0 positive)",
            "",
            "### Article Sentiments:"
        ]
        for art in articles:
            lines.append(f"- **{art['title']}** → sentiment: {art['sentiment']:.2f}")

        summary = "\n".join(lines) + "\n"
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            fw.write(summary)

        print(f"[{self.name}] Wrote Cloud NL–powered insights to {out_path}")
        print(f"[{self.name}] Wrote entity list to {entities_path}")
        return out_path
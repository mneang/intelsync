import os
import json
import yaml
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class WebScraperAgent:
    def __init__(self, name: str, config_path: str):
        self.name = name
        self.config_path = config_path
        # Ensure output folder exists
        with open(self.config_path) as f:
            self.cfg = yaml.safe_load(f)
        os.makedirs(os.path.dirname(self.cfg["output_path"]), exist_ok=True)

    def scrape(self):
        targets = self.cfg.get("targets", [])
        articles = []

        for url in targets:
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                print(f"[{self.name}] ERROR fetching {url}: {e}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string if soup.title else url
            # Combine all paragraph texts as a simple summary
            paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
            summary = " ".join(paragraphs[:3]) if paragraphs else ""
            timestamp = datetime.utcnow().isoformat()

            articles.append({
                "url": url,
                "title": title,
                "summary": summary,
                "fetched_at": timestamp
            })
            print(f"[{self.name}] scraped {url}")

        # Write JSON file
        out_path = self.cfg["output_path"]
        with open(out_path, "w", encoding="utf-8") as fw:
            json.dump(articles, fw, ensure_ascii=False, indent=2)

        print(f"[{self.name}] Wrote {len(articles)} articles to {out_path}")
        return articles
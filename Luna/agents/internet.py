"""
Internet Agent - researches topics, tracks packages, monitors news,
compares products, finds answers from multiple sources.
"""

import urllib.request
import urllib.parse
import json
import ssl
import re
import threading
import time

ssl._create_default_https_context = ssl._create_unverified_context


class InternetAgent:
    def search(self, query, num=5):
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded}&num={num}"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8', errors='ignore')
            titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
            results = []
            for t in titles[:num]:
                clean = re.sub(r'<[^>]+>', '', t).strip()
                if clean:
                    results.append(clean)
            return results if results else ["No results found"]
        except Exception as e:
            return [f"Search error"]

    def research(self, topic):
        results = self.search(topic, num=8)
        summary = f"Research on '{topic}':\n"
        for i, r in enumerate(results, 1):
            summary += f"{i}. {r}\n"

        try:
            import requests
            r = requests.post("http://127.0.0.1:11434/api/generate", json={
                "model": "mistral",
                "prompt": f"Summarize these search results about '{topic}', extracting key insights:\n{chr(10).join(results)}",
                "stream": False,
                "options": {"num_predict": 300}
            }, timeout=15)
            if r.status_code == 200:
                summary = r.json()['response'].strip()
        except Exception:
            pass
        return summary

    def get_weather(self, location=None):
        try:
            loc = location or self._get_location()
            url = f"https://wttr.in/{urllib.parse.quote(loc)}?format=%C+%t+%w+%h"
            req = urllib.request.Request(url, headers={'User-Agent': 'curl/8.0'})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = r.read().decode().strip()
            return f"Weather in {loc}: {data}"
        except Exception:
            return "Weather unavailable"

    def _get_location(self):
        try:
            with urllib.request.urlopen("http://ip-api.com/json/", timeout=5) as r:
                d = json.loads(r.read())
                return f"{d.get('city', '')}, {d.get('countryCode', '')}"
        except Exception:
            return "unknown"

    def get_news(self, topic=None):
        try:
            if topic:
                url = f"https://news.google.com/rss/search?q={urllib.parse.quote(topic)}&hl=en-US"
            else:
                url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8', errors='ignore')
            titles = re.findall(r'<title>(.*?)</title>', html, re.DOTALL)
            return [t.strip() for t in titles[1:9] if t.strip()]
        except Exception:
            return ["News unavailable"]

    def track_package(self, tracking_number):
        carriers = [
            ("FedEx", f"https://www.fedex.com/fedextrack/?trknbr={tracking_number}"),
            ("UPS", f"https://www.ups.com/track?tracknum={tracking_number}"),
            ("USPS", f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"),
            ("DHL", f"https://www.dhl.com/en/express/tracking.html?AWB={tracking_number}"),
        ]
        links = "\n".join([f"{name}: {url}" for name, url in carriers])
        return f"Tracking {tracking_number}. Check status:\n{links}"

    def compare_products(self, product):
        results = self.search(f"best {product} 2026 review comparison", num=10)
        return f"Top results for '{product}':\n" + "\n".join([f"• {r}" for r in results])

    def monitor_news(self, topics, callback):
        def _monitor():
            seen = set()
            while True:
                for topic in topics:
                    news = self.get_news(topic)
                    for item in news:
                        if item not in seen:
                            seen.add(item)
                            callback(topic, item)
                time.sleep(300)
        thread = threading.Thread(target=_monitor, daemon=True)
        thread.start()
        return thread

    def get_definition(self, word):
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
            with urllib.request.urlopen(url, timeout=5) as r:
                data = json.loads(r.read())[0]
            meanings = data.get('meanings', [])
            if meanings:
                defs = meanings[0].get('definitions', [])
                if defs:
                    return f"{word}: {defs[0].get('definition', 'No definition')}"
            return f"No definition found for '{word}'"
        except Exception:
            return f"Could not look up '{word}'"

    def fetch_url(self, url):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                html = r.read().decode('utf-8', errors='ignore')
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000]
        except Exception as e:
            return f"Could not fetch URL: {e}"

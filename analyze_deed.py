import os
import glob
import json
import matplotlib.pyplot as plt
from collections import Counter
import requests
import subprocess

# CONFIG
OLLAMA_MODEL = "llama3"

# Helper: Search on SerpAPI
def search_company(name):
    SERPAPI_API_KEY = "" #use .env for api key or paste directly
    params = {
        "engine": "google",
        "q": name,
        "api_key": SERPAPI_API_KEY,
        "num": 1
    }
    url = "https://serpapi.com/search.json"
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data['organic_results'][0].get('snippet', "")
    except Exception:
        return ""

# Categorize buyer using Ollama locally
def categorize_buyer(text):
    prompt = f"""
Given the following text about a deed holder, classify them into one of these categories:
- Individual
- Trust
- LLC
- Corporation
- Other

Text:
\"\"\"{text}\"\"\"

Respond with only the category name.
"""
    try:
        response = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt.encode('utf-8'),
            capture_output=True,
            check=True
        )
        output = response.stdout.decode('utf-8').strip()
        return output.splitlines()[0]
    except Exception as e:
        print(f"Error in categorize_buyer: {e}")
        return "Other"

# Main function
def analyze_deeds_by_building():
    base_output_path = os.path.join("output")
    building_folders = [f for f in os.listdir(base_output_path) if os.path.isdir(os.path.join(base_output_path, f))]

    print(f"Found {len(building_folders)} building folders.")

    for building in building_folders:
        print(f"\nAnalyzing: {building}")
        deed_file = os.path.join(base_output_path, building, f"{building}_deed_holders.txt")

        if not os.path.exists(deed_file):
            print(f"No deed file found for {building}, skipping.")
            continue

        with open(deed_file, "r") as f:
            names = [line.strip() for line in f if line.strip()]

        print(f"Found {len(names)} deed holders.")

        categories = []
        seen = set()

        for i, name in enumerate(set(names), 1):
            print(f"[{i}/{len(set(names))}] Processing: {name}")
            if name in seen:
                continue
            seen.add(name)

            info_text = name #search_company(name) could be added if want
            category = categorize_buyer(info_text)
            print(f"Categorized as: {category}")
            categories.append(category)

        # Count and plot
        counts = Counter(categories)
        print("Category counts:", counts)

        plt.figure(figsize=(8, 8))
        plt.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%', startangle=140)
        plt.title(f"Buyer Categories — {building}")
        plt.tight_layout()

        # Save per building
        chart_path = os.path.join(base_output_path, building, f"{building}_buyer_categories_pie_chart.png")
        plt.savefig(chart_path)
        plt.close()
        print(f"Saved chart: {chart_path}")

if __name__ == "__main__":
    analyze_deeds_by_building()

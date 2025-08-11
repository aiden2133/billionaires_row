# NYC Skyscraper Deed & Tax Analysis

This project analyzes real estate deed holders and tax data for luxury skyscrapers in New York City. It includes two Python scripts:

- `data_parsing.py` — Parses unit-level CSV data to extract sale prices, owners, and tax assessments.
- `analyze_deed.py` — Classifies deed holders using a local LLM and generates visual summaries.

---

## Project Structure


├── analyze_deed.py

├── data_parsing.py

├── /432ParkAvenue/

├── /centralparktower/

├── /one57/

├── /steinwayTower/

├── /momatower/

└── /output/

---

## Setup & Requirements

**Python Version:** 3.7+

**Dependencies:**

pip install matplotlib requests
Optional:

Ollama for local LLM inference (used for classifying buyer types)

SerpAPI if you want to enrich owner names via Google search (not enabled by default)

---
## About
Buildings Analyzed: 432 Park Avenue
Central Park Tower
One57
MoMA Tower
Steinway Tower

Each building folder contains CSV files with individual unit-level property data.

---
## Script Details
data_parsing.py
Purpose:
Parses CSVs per building to extract: Owner names (from DEED records)
Sale price
Yearly taxable assessed values

Key Features:
Calculates total and average tax values by year
Plots sale price distributions
Tracks vacancy rates based on missing sale prices
Outputs deed holder names to text files for classification

Output (per building):

/output/[building]/[building]_total_tax_value.png

/output/[building]/[building]_sale_price_histogram.png

/output/[building]/[building]_deed_holders.txt


To Run: python data_parsing.py



analyze_deed.py
Purpose:
Classifies deed holders into:
Individual
Trust
LLC
Corporation
Other

How It Works:

Loads names from [building]_deed_holders.txt

Uses a local Ollama model (e.g., LLaMA 3) to classify each entry

Generates pie charts for entity types

Output (per building):

/output/[building]/[building]_buyer_categories_pie_chart.png

To Run: python analyze_deed.py

---
## Configuration Notes
Set your model in analyze_deed.py:

python
Copy
Edit
OLLAMA_MODEL = "llama3"
To enable SerpAPI enrichment (optional), set your API key:
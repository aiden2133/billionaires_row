import csv
import os
import matplotlib.pyplot as plt
from collections import defaultdict


def find_all_files(folder_path):
    # Walk through the folder and collect all CSV files
    csv_files = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.csv'):
            full_path = os.path.join(folder_path, filename)
            csv_files.append(full_path)

    return csv_files

def gather_data(csv_file):
    deeds = []
    yearly_values = {}
    sale_price = None
    name = None

    with open(csv_file, 'r', newline='') as f:
        reader = list(csv.reader(f))

        deed_start_index = None
        for i, row in enumerate(reader):
            if row and row[0].strip() == "Document Type":
                deed_start_index = i + 1
                break

        # --- Process DEED section ---
        deed_rows = reader[deed_start_index:] if deed_start_index is not None else []
        fallback_start_index = None

        # First DEED with "-" triggers fallback mode
        for i, row in enumerate(deed_rows):
            if row and row[0].strip() == "DEED":
                doc_amount_raw = row[2].replace(",", "").replace("$", "").strip()
                if doc_amount_raw == "-":
                    fallback_start_index = i
                    break

        #Try to get next valid DEED after fallback
        found_valid_deed = False
        if fallback_start_index is not None:
            for row in deed_rows[fallback_start_index + 1:]:
                if row and row[0].strip() == "DEED":
                    try:
                        doc_amount_raw = row[2].replace(",", "").replace("$", "").strip()
                        doc_amount = float(doc_amount_raw) if doc_amount_raw not in ("", "-") else None
                        if doc_amount is not None:
                            sale_price = doc_amount
                            name = row[4] if len(row) > 4 else None
                            found_valid_deed = True
                            break
                    except (IndexError, ValueError):
                        continue

        # Fallback — any valid DEED in the list
        if not found_valid_deed:
            for row in deed_rows:
                if row and row[0].strip() == "DEED":
                    try:
                        doc_amount_raw = row[2].replace(",", "").replace("$", "").strip()
                        doc_amount = float(doc_amount_raw) if doc_amount_raw not in ("", "-") else None
                        if doc_amount is not None:
                            sale_price = doc_amount
                            name = row[4] if len(row) > 4 else None
                            break
                    except (IndexError, ValueError):
                        continue

        # ---  Process Yearly Financial Data (search full file) ---
        for row in reader:
            if not row or len(row) < 8:
                continue

            year_raw = row[0].strip()
            if not year_raw.isdigit() or not (2000 <= int(year_raw) <= 2100):
                continue  # Skip junk

            try:
                year = int(year_raw)
                taxable_value_raw = row[7].replace(",", "").strip()
                if taxable_value_raw and taxable_value_raw.lower() != "nd":
                    value = float(taxable_value_raw)
                    yearly_values[year] = value
            except (ValueError, IndexError):
                continue

    return name, sale_price, yearly_values


        # Optional output
        #print("\nIndividual Yearly Values:")
        #for year in sorted(yearly_values.keys(), reverse=True):
        #    print(f"{year}_value = {yearly_values[year]}")
        #print(f"Sale Price: {sale_price}")
        #print(f"Name (party2): {name}")

def plot_avg_total_value_across_units(folder_path, output_path="centralparktower_avg_total_value.png"):
    yearly_totals = defaultdict(list)  # {year: [total values across units]}

    for file in os.listdir(folder_path):
        if not file.endswith(".csv"):
            continue

        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 6:
                    continue

                year_str = row[0].strip()
                if not year_str.isdigit():
                    continue  # skip headers, ND, etc.

                try:
                    year = int(year_str)
                    if year == 2021:
                        continue  # skip year 2021

                    total_value_str = row[5].replace(",", "").strip()
                    if total_value_str.lower() in ("", "nd"):
                        continue
                    total_value = float(total_value_str)
                    yearly_totals[year].append(total_value)
                except ValueError:
                    continue

    # Compute averages, excluding 2021
    avg_total_by_year = {
        year: sum(vals) / len(vals)
        for year, vals in yearly_totals.items()
        if len(vals) > 0 and year != 2021
    }

    if not avg_total_by_year:
        print("No valid data found in folder.")
        return

    # Sort for plotting
    sorted_years = sorted(avg_total_by_year.keys())
    sorted_averages = [avg_total_by_year[yr] for yr in sorted_years]

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(sorted_years, sorted_averages, marker='o', color='teal')
    plt.title("Average Assessed Total Value Over Years — Central Park Tower")
    plt.xlabel("Year")
    plt.ylabel("Average Total Assessed Value")
    plt.grid(True)
    plt.gca().yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    print(f"Saved graph to {output_path}")

if __name__ == "__main__":
    import os
    import csv
    import matplotlib.pyplot as plt
    from collections import defaultdict
    import matplotlib.ticker as mtick
    whole = True

    #plot_avg_total_value_across_units("centralparktower")

    if whole:
        # Map folder names to cleaner titles
        pretty_names = {
            "432ParkAvenue": "432 Park Avenue",
            "centralparktower": "Central Park Tower",
            "momatower": "MoMA Tower",
            "one57": "One57",
            "steinwayTower": "Steinway Tower"
        }

        folders = list(pretty_names.keys())

        for folder in folders:
            print(f"\nProcessing folder: {folder}")
            building_title = pretty_names[folder]
            tax_totals = defaultdict(list)
            sale_prices = []
            deed_names = []
            valid_units = 0
            vacant_count = 0

            folder_path = os.path.join(os.getcwd(), folder)
            output_path = os.path.join(os.getcwd(), "output", folder)
            os.makedirs(output_path, exist_ok=True)

            for file in os.listdir(folder_path):
                if file.endswith(".csv"):
                    csv_path = os.path.join(folder_path, file)
                    name, sale_price, yearly_values = gather_data(csv_path)

                    if sale_price is None:
                        vacant_count += 1
                        continue

                    valid_units += 1

                    # Only add to histogram if ≤ $300M
                    if sale_price <= 300_000_000:
                        sale_prices.append(sale_price)
                    else:
                        print(f"Skipping high-value sale (${sale_price:,.2f}) in histogram for {folder}")

                    if name:
                        deed_names.append(name)

                    for year, value in yearly_values.items():
                        tax_totals[year].append(value)

            # --------- Graph: Average Tax Value Over Years ---------
            if tax_totals:
                total_tax = {year: sum(vals) for year, vals in tax_totals.items()}
                years_sorted = sorted(total_tax.keys())
                values_sorted = [total_tax[yr] for yr in years_sorted]

                plt.figure(figsize=(10, 5))
                plt.plot(years_sorted, values_sorted, marker='o', color='darkgreen')
                plt.title(f"Total Taxable Value Over Years — {building_title}")
                plt.xlabel("Year")
                plt.ylabel("Total Tax Value")
                plt.grid(True)
                plt.gca().yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
                plt.tight_layout()
                plt.savefig(os.path.join(output_path, f"{folder}_total_tax_value.png"))
                plt.close()

            # --------- Graph: Histogram of Sale Prices ---------
            if sale_prices:
                plt.figure(figsize=(8, 5))
                plt.hist(sale_prices, bins=15, color='skyblue', edgecolor='black')
                plt.title(f"Histogram of Sale Prices — {building_title}")
                plt.xlabel("Sale Price ($)")
                plt.ylabel("Frequency")
                plt.gca().xaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
                plt.tight_layout()
                plt.savefig(os.path.join(output_path, f"{folder}_sale_price_histogram.png"))
                plt.close()

            # --------- Percent Vacant ---------
            total_units = valid_units + vacant_count
            percent_vacant = (vacant_count / total_units) * 100 if total_units > 0 else 0
            print(f"Percent Vacant Apartments: {percent_vacant:.2f}%")

            # --------- Total Sale Price ---------
            total_sale_value = sum(sale_prices)
            average_sale_price = total_sale_value / len(sale_prices) if sale_prices else 0

            print(f"Total Sale Value of All Units: ${total_sale_value:,.2f}")
            print(f"Average Sale Price (≤ $300M only): ${average_sale_price:,.2f}")

            # --------- Write Deed Holders ---------
            txt_file = os.path.join(output_path, f"{folder}_deed_holders.txt")
            with open(txt_file, 'w') as f:
                for name in deed_names:
                    f.write(f"{name}\n")

#for moma tower, this is realty group: W2005/HINES WEST FIFTY-THIRD REALTY, LLC
#if Unknown then not sold for centralparktower
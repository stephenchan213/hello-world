import requests
import csv
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

input_file_path = "stock_codes.txt"
url = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': url,
    'Origin': 'https://www3.hkexnews.hk',
}

def process_stock_code(stock_code):
    payload = {
        'today': '20250722',
        'txtStockCode': stock_code,
        '__EVENTTARGET': 'btnSearch',
        'originalShareholdingDate': '2025/07/21',
        'txtShareholdingDate': '2025/07/21',
        'submit': 'Search',
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            with open(f'response{stock_code}.txt', 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"[{stock_code}] Response body written to response{stock_code}.txt")

            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", class_="table table-scroll table-sort table-mobile-list")
            if not table:
                print(f"[{stock_code}] Table not found.")
                return

            # Extract headers
            table_headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]

            # Extract rows
            rows = []
            for tr in table.find("tbody").find_all("tr"):
                # Only extract <div class="mobile-list-body"> text if needed
                row = [div.get_text(strip=True) for div in tr.find_all("div", class_="mobile-list-body")]
                if not row:  # fallback to td text if div not present
                    row = [td.get_text(strip=True) for td in tr.find_all("td")]
                rows.append(row)

            # Write to CSV
            with open(f"output{stock_code}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(table_headers)
                writer.writerows(rows)

            print(f"[{stock_code}] CSV file 'output{stock_code}.csv' created successfully.")
        else:
            print(f"[{stock_code}] Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"[{stock_code}] Error: {e}")

def main():
    with open(input_file_path, 'r') as file:
        stock_codes = file.read().splitlines()

    # You can adjust max_workers as needed (e.g. 5, 10, 20)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_stock_code, stock_code) for stock_code in stock_codes]
        for future in as_completed(futures):
            # This will catch exceptions in threads if any
            try:
                future.result()
            except Exception as exc:
                print(f"Thread generated an exception: {exc}")

if __name__ == "__main__":
    main()
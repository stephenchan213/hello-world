import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

input_file_path = "stock_codes.txt"
url = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': url,
    'Origin': 'https://www3.hkexnews.hk',
}

def fetch_html(stock_code):
    # Replace this URL with your real stock data source
    payload = {
        'today': '20250722',
        'txtStockCode': stock_code,
        '__EVENTTARGET': 'btnSearch',
        'originalShareholdingDate': '2025/07/21',
        'txtShareholdingDate': '2025/07/21',
        'submit': 'Search',
    }
    response = requests.post(url, data=payload, headers=headers, timeout=50)
    return response.text

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    headers = []
    values = []
    category = soup.find('div', class_='summary-category')
    if category and category.text.strip() == "Non-consenting Investor Participants":
        datarow = category.find_parent('div', class_='ccass-search-datarow')
        headers = datarow.find_all('div', class_='header')
        values = datarow.find_all('div', class_='value')
            if header and value:
                headers.append(header.text.strip())
                values.append(value.text.strip())
    return headers, values

def process_stock_code(stock_code):
    html = fetch_html(stock_code)
    headers, values = parse_html(html)
    return stock_code, headers, values

with open(input_file_path, 'r') as file:
    stock_codes = file.read().splitlines()

results = []
all_headers_set = set()
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(process_stock_code, code): code for code in stock_codes}
    for future in as_completed(futures):
        try:
            stock_code, headers, values = future.result()
            results.append({'stock_code': stock_code, 'headers': headers, 'values': values})
            all_headers_set.update(headers)
        except Exception as exc:
            print(f"Thread generated an exception: {exc}")

# Prepare consistent header order
all_headers = ['Stock Code'] + sorted(all_headers_set)

# Aggregate results into rows for CSV
csv_rows = []
for res in results:
    row = {header: '' for header in all_headers}
    row['Stock Code'] = res['stock_code']
    for h, v in zip(res['headers'], res['values']):
        row[h] = v
    csv_rows.append(row)

with open('all_stocks_output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=all_headers)
    writer.writeheader()
    for row in csv_rows:
        writer.writerow(row)

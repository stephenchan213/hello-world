import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor

input_file_path = "stock_codes.txt"
url = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': url,
    'Origin': 'https://www3.hkexnews.hk',
}

with open(input_file_path, 'r') as file:
    stock_codes = file.read().splitlines()

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
        response = requests.post(url, headers=headers, data=payload)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all data rows
        rows = soup.find_all('div', class_='ccass-search-datarow')
        for row in rows:
            category = row.find('div', class_='summary-category')
            if category and category.text.strip() == 'Non-consenting Investor Participants':
                headers_list = [div.text.strip() for div in row.find_all('div', class_='header')]
                values_list = [div.text.strip() for div in row.find_all('div', class_='value')]
                return (stock_code, headers_list, values_list)
    except Exception as e:
        print(f"Error processing stock code {stock_code}: {e}")
    return (stock_code, [], [])

# Use ThreadPoolExecutor for multithreading
results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = executor.map(process_stock_code, stock_codes)
    for result in futures:
        results.append(result)

# Write results to CSV
if results:
    # Determine headers from the first successful result
    for _, headers_row, _ in results:
        if headers_row:
            headers = ['Stock Code'] + headers_row
            break
    else:
        headers = ['Stock Code']

    with open('non_consenting_investors.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for stock_code, _, values_row in results:
            writer.writerow([stock_code] + values_row)

print("CSV file 'non_consenting_investors.csv' has been created.")


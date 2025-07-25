import requests
from bs4 import BeautifulSoup
import csv
import threading

input_file_path = "stock_codes.txt"
url = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': url,
    'Origin': 'https://www3.hkexnews.hk',
}

# Lock for thread-safe writing to shared data
lock = threading.Lock()

# Shared list to store results
results = []
table_headers = []

# Function to process each stock code
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
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        table_headers = [header.get_text(strip=True)) for header in soup.find('div', class_='ccass-search-headerrow').find_parent('div', class_='container content-container ccass-search-container content-container-reset').find_all('div', class_='header')]
        print(table_headers)                                                                                        
        
        categories = soup.find_all('div', class_='summary-category')
        if not categories:
            print(f"[{stock_code}] Table not found.")
            return    
        for category in categories:
            if category.text.strip() == "Non-consenting Investor Participants":
                datarow = category.find_parent('div', class_='ccass-search-datarow')
                headers_divs = datarow.find_all('div', class_='header')
                values_divs = datarow.find_all('div', class_='value')
    
                data = [(stock_code, header.text.strip(), value.text.strip()) for header, value in zip(headers_divs, values_divs)]
                
                with lock:
                    results.extend(data)
    except Exception as e:
        print(f"Error processing stock code {stock_code}: {e}")

# Create and start threads
threads = []

# List of stock codes to process
with open(input_file_path, 'r') as file:
    stock_codes = file.read().splitlines()

for code in stock_codes:
    thread = threading.Thread(target=process_stock_code, args=(code,))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Write results to CSV file
with open('non_consenting_investors_all.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Stock Code', 'Header', 'Value'])
    writer.writerows(results)

print("All data written to non_consenting_investors_all.csv")


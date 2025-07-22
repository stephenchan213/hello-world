import requests
#from bs4 import BeautifulSoup

# Define the paths for input and output files
input_file_path = "stock_codes.txt"          # Relative path
url = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"

# Read stock codes from the input file
with open(input_file_path, 'r') as file:
    stock_codes = file.read().splitlines()

    # Loop through each stock code and submit the request
    for stock_code in stock_codes:
        payload = {
            'today':'20250722',
            'txtStockCode': stock_code,
            '__EVENTTARGET': 'btnSearch',
            'txtShareholdingDate': '20250721',
            'originalShareholdingDate': '20250721',
            'submit': 'Search'
            # Add other parameters as needed
        }
        
        # Send the POST request
        response = requests.post(url, json=payload)
        
	# Check if the request was successful
	if response.status_code == 200:
		# Open a text file in write mode
		with open('response' + stock_code + '.txt', 'w') as file:
			# Write the response body to the file
			file.write(response.text)
		print("Response body written to response" + stock_code + ".txt")
	else:
		print(f"Request failed with status code: {response.status_code}")

import requests

# Step 1: Create a session
session = requests.Session()

# Step 2: Set headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    # "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9"
    # "Accept-Encoding": "gzip, deflate, br",
    # "Accept": "application/json",
}

# Step 3: Get the homepage to establish session cookies
session.get("https://www.nseindia.com", headers=headers)

# Step 4: Now make the API call
url = "https://www.nseindia.com/api/etf"
response = session.get(url, headers=headers)

# Step 5: Parse JSON
if response.status_code == 200:
    data = response.json()
    print(data)  # or access specific values like data['data'], etc.
else:
    print("Failed to fetch data:", response.status_code)


curl.exe 'https://www.nseindia.com/api/etf' \
  -H 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36' \
  -H 'Accept-Language': 'en,gu;q=0.9,hi;q=0.8' \
  --proxy http://123.45.67.89:8080

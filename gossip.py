import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# Replace with your actual API key and target URL
api_key = 'AIzaSyBSIOigkrHJzpyOkh5t8-Vuoj5MkC4gAmA'
url = 'https://www.gossipherald.com'

# Load Google Credentials from GitHub Secrets
creds_json = os.getenv("GOSSIP_CREDENTIALS")
creds = Credentials.from_service_account_info(json.loads(creds_json))
client = gspread.authorize(creds)

# Open the Google Sheet by its name
sheet = client.open('lcp for gossip herald').sheet1

def fetch_lcp(strategy):
    """Fetch the Largest Contentful Paint (LCP) for a given strategy (mobile or desktop)."""
    print(f"Fetching LCP for {strategy}...")
    api_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}&key={api_key}'
    response = requests.get(api_url)

    print(f"Response Status Code for {strategy}: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            try:
                lcp_ms = data['loadingExperience']['metrics']['LARGEST_CONTENTFUL_PAINT_MS']['percentile']
            except KeyError:
                lcp_ms = data['lighthouseResult']['audits']['largest-contentful-paint']['numericValue']
            lcp_seconds = lcp_ms / 1000
            print(f"{strategy.capitalize()} LCP: {lcp_seconds} seconds")
            return lcp_seconds
        except KeyError as e:
            print(f"Error processing JSON response for {strategy}: {e}")
    else:
        print(f"Failed to retrieve data for {strategy}. Error: {response.text}")
    return None

print("Script started...") 

try:
    # Check if sheet is empty and add headers if necessary
    if not sheet.get_all_values():
        print("Adding headers to Google Sheet...")
        sheet.append_row(['Timestamp', 'Label', 'LCP (s)', 'Label', 'LCP (s)'])

    print("Fetching LCP values...")
    mobile_lcp = fetch_lcp('mobile')
    desktop_lcp = fetch_lcp('desktop')

    if mobile_lcp is not None and desktop_lcp is not None:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append_row([now, 'Mobile', mobile_lcp, 'Desktop', desktop_lcp])
        print("Data appended successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

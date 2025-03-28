import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

# Replace with your actual API key and target URL
api_key = 'AIzaSyBSIOigkrHJzpyOkh5t8-Vuoj5MkC4gAmA'
url = 'https://www.gossipherald.com'

# Google Sheets setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
   r"C:/Users/nasir.mehmood/Desktop/halogen-honor-450808-n5-2212b93ab2b9.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet by its name
sheet = client.open('lcp for gossip herald ').sheet1

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
                lcp_seconds = lcp_ms / 1000
                print(f"{strategy.capitalize()} Field Data - Largest Contentful Paint: {lcp_seconds} seconds")
            except KeyError:
                print(f"{strategy.capitalize()} Field Data unavailable. Checking Lab Data...")
                lcp_ms = data['lighthouseResult']['audits']['largest-contentful-paint']['numericValue']
                lcp_seconds = lcp_ms / 1000
                print(f"{strategy.capitalize()} Lab Data - Largest Contentful Paint: {lcp_seconds} seconds")
            return lcp_seconds
        except KeyError as e:
            print(f"Error processing JSON response for {strategy}: {e}")
            return None
    else:
        print(f"Failed to retrieve data for {strategy}. Error: {response.text}")
        return None

print("Script started...") 

try:
    # Check if sheet is empty and add headers if necessary
    if not sheet.get_all_values():
        print("Adding headers to Google Sheet...")
        header = ['Timestamp', 'Label', 'LCP (s)', 'Label', 'LCP (s)']
        sheet.append_row(header)

    print("Entering while loop...")
    while True:
        print("Fetching LCP values...")
        mobile_lcp = fetch_lcp('mobile')
        desktop_lcp = fetch_lcp('desktop')

        print(f"Mobile LCP: {mobile_lcp}, Desktop LCP: {desktop_lcp}")
        if mobile_lcp is None or desktop_lcp is None:
            print("Skipping data row append due to missing values.")
        else:
            # Get the current timestamp
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Prepare the data row
            data_row = [now, 'Mobile', mobile_lcp, 'Desktop', desktop_lcp]

            print("Appending data row to Google Sheet...")
            sheet.append_row(data_row)

        print("Sleeping for 24 hours...")
        time.sleep(24 * 60 * 60)  # Sleep for 24 hours

except Exception as e:
    print(f"An error occurred: {e}")

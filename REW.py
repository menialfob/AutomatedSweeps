import json
import datetime
from dateutil import parser
import requests

def check_warning_recent(response_json):
    # Handle empty response
    if not response_json:
        print("No warning data available.")
        return False
    
    # Parse the time from the response
    warning_time_str = response_json.get("time", "")
    if not warning_time_str:
        print("Warning time is missing.")
        return False
    
    try:
        warning_time = parser.parse(warning_time_str, dayfirst=False, yearfirst=True)
    except ValueError:
        print("Invalid time format.")
        return False
    
    # Get the current time
    current_time = datetime.datetime.now()

    
    # Check the time difference
    time_difference = current_time - warning_time
    
    # If the warning happened within the last 10 seconds, flag it
    if time_difference.total_seconds() <= 10:
        print("Warning is recent!")
        return True
    else:
        print("Warning is not recent.")
        return False
    


# REW API endpoint
# api_url = "http://localhost:4735/measure/number-of-repetitions"
api_url = "http://localhost:4735/application/last-warning"

# Data to set the number of repetitions
data = {"value": "Use as entered"}

try:
    # Send POST request to the API
    # response = requests.post(api_url, json=data)
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        print(f"Response: {response.text}")
        response_json = response.json()
        print(check_warning_recent(response_json))
    else:
        print(f"Failed to set repetitions. Status code: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

import json
import datetime
import time
from dateutil import parser
import requests
import pyautogui

# def get_measure_problems(endpoint):
#     """Fetch the latest problem from the endpoint."""
#     try:
#         response = requests.get(endpoint)
#         response.raise_for_status()
#         data = response.json()
#         return data if isinstance(data, list) else []  # Ensure it handles empty problems
#     except requests.RequestException as e:
#         print(f"Error fetching problems: {e}")
#         return []

# def measure():
#     """Dummy function for MeasureSweep(). Replace this with actual function."""
#     print("Running MeasureSweep()...")
#     time.sleep(20)  # Simulating function execution time

# def check_and_run_measure(warning_endpoint, error_endpoint, max_attempts=3):
#     """Runs MeasureSweep() and checks for new problems, retrying up to max_attempts times."""
#     initial_problems = get_measure_problems(warning_endpoint) + get_measure_problems(error_endpoint)
#     initial_times = {problem.get("time", "") for problem in initial_problems}  # Track initial problem timestamps
#     attempts = 0

#     while attempts < max_attempts:
#         measure()
#         attempts += 1

#         latest_problems = get_measure_problems(warning_endpoint) + get_measure_problems(error_endpoint)
#         latest_times = {problem.get("time", "") for problem in latest_problems}  # Get latest problem timestamps
        
#         new_problems = latest_times - initial_times  # Check for truly new problems based on time
        
#         if not new_problems:
#             print("No new problems detected. MeasureSweep() successful.")
#             return
        
#         print(f"New problem detected: {latest_problems[-1]['title']}")
        
#         # Update initial_times to avoid detecting the same problem in the next iteration
#         initial_times.update(new_problems)
        
#         if attempts < max_attempts:
#             print(f"Retrying MeasureSweep()... Attempt {attempts + 1}")
#         else:
#             print("Max attempts reached. Exiting with problem.")
#             return

# # Replace with the actual endpoint URL
# WARNING_ENDPOINT_URL = "http://localhost:4735/application/warnings"
# ERROR_ENDPOINT_URL = "http://localhost:4735/application/errors"
# check_and_run_measure(WARNING_ENDPOINT_URL, ERROR_ENDPOINT_URL)




# # REW API endpoint
api_url = "http://localhost:4735/measurements/selected-uuid"
api_url_delete = "http://localhost:4735/measurements/66fde9b7-4bad-45e3-b97b-a20460dff666"
api_url_warnings = "http://localhost:4735/application/warnings"
api_url_naming = "http://localhost:4735/measure/naming"
api_url_commands = "http://localhost:4735/measure/commands"
api_url_commands = "http://localhost:4735/measure/commands"
base_url = "http://localhost:4735"
endpoint = "/application/commands"
# api_url_errors = "http://localhost:4735/application/errors"

# # Data to set the number of repetitions
# data = {"value": "Use as entered"}

try:
    # Send POST request to the API
    # response = requests.post(api_url, json=data)
    # response = requests.delete(api_url_delete)
    response = requests.get(base_url + endpoint)

    # Check if the request was successful
    if response.status_code == 200:
        print(f"Response: {response.text}")
        response_json = response.json()
        # print(check_problem_recent(response_json))
    else:
        print(f"Failed to set repetitions. Status code: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

# try:
#     # Send POST request to the API
#     # response = requests.post(api_url, json=data)
#     response = requests.get(api_url_errors)

#     # Check if the request was successful
#     if response.status_code == 200:
#         print(f"Response: {response.text}")
#         response_json = response.json()
#         # print(check_problem_recent(response_json))
#     else:
#         print(f"Failed to set repetitions. Status code: {response.status_code}")
#         print(f"Response: {response.text}")

# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")

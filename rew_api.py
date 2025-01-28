import requests
from config import BASE_URL_ENDPOINT, MEASUREMENT_ENDPOINT, MEASUREMENT_UUID_ENDPOINT, WARNING_ENDPOINT, ERROR_ENDPOINT, VERSION_ENDPOINT

def ensure_rew_api():
    """Check if the REW API is running."""
    try:
        response = requests.get(VERSION_ENDPOINT, timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def ensure_rew_settings():
    """Check REW settings and ensure they match expected values."""
    ENDPOINTS = {
        "/measure/naming": {"namingOption": "Use as entered", "prefixMeasNameWithOutput": False},
        "/measure/playback-mode": {"message": "From file"}
    }
    errors = []

    for endpoint, expected_values in ENDPOINTS.items():
        try:
            response = requests.get(f"{BASE_URL_ENDPOINT}{endpoint}").json()
        except Exception as e:
            errors.append(f"Failed to fetch {endpoint}: {str(e)}")
            continue

        for key, expected_value in expected_values.items():
            if response.get(key) != expected_value:
                errors.append(f"{endpoint}: {key} should be {expected_value}, got {response.get(key)}")

    return errors

def get_measure_errors():
    """Fetch the latest problem from the endpoint."""
    try:
        response = requests.get(ERROR_ENDPOINT)
        response.raise_for_status()
        data = response.json()
        return (
            data if isinstance(data, list) else []
        )  # Ensure it handles empty problems
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return []
    
def get_measure_warnings():
    """Fetch the latest problem from the endpoint."""
    try:
        response = requests.get(WARNING_ENDPOINT)
        response.raise_for_status()
        data = response.json()
        return (
            data if isinstance(data, list) else []
        )  # Ensure it handles empty problems
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return []
    
def check_new_problems(previous_times):
    problems = get_measure_warnings() + get_measure_errors()
    problem_times  = {
        problem.get("time", "") for problem in problems
    }
    new_problem_times = (
            problem_times - previous_times
        )
    return new_problem_times, problems

def get_selected_measurement():
    """Get the id of the selected measurement. Assumption is that selected measurement is the latest one."""
    try:
        response = requests.get(MEASUREMENT_UUID_ENDPOINT)
        response.raise_for_status()
        data = response.json()
        uuid = data["message"]
        return uuid
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return {}


def delete_measurement(uuid):
    """Get the id of the selected measurement. Assumption is that selected measurement is the latest one."""
    try:
        response = requests.delete(MEASUREMENT_ENDPOINT + "/" + uuid)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return {}
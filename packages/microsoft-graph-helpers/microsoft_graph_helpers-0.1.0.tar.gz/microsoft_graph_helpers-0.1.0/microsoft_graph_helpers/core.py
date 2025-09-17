import json, logging, requests, time
from typing import List, Union
from requests.exceptions import Timeout, RequestException


def get_headers(bearer_token):
    # returns basic request header for making Graph calls
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + bearer_token
    }

def make_graph_api_request(
    method: str,
    url: str,
    headers: dict,
    payload: Union[dict, None] = None,
    context: str = "",
    retries: int = 3,
    timeout: int = 15
) -> Union[dict, bool]:
    for attempt in range(1, retries + 1):
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=payload, timeout=timeout)
            else:
                logging.error(f"[{context}] Unsupported HTTP method: {method}")
                return False

            if response.status_code in (200, 202, 204):
                if response.status_code == 204:
                    logging.debug(f"[{context}] Http Status Code: {response.status_code} - Request submitted successfully.")
                    return True
                elif response.status_code == 202:
                    logging.debug(f"[{context}] Http Status Code: {response.status_code} - Request submitted successfully.")
                    return True
                try:
                    return response.json()
                except ValueError:
                    logging.warning(f"[{context}] Http Status Code: {response.status_code} - Response returned no JSON content.")
                    return True
            else:
                handle_graph_api_error(response, context=context)
                return False

        except Timeout:
            logging.warning(f"[{context}] Timeout on attempt {attempt}/{retries}. Retrying...")
        except RequestException as e:
            logging.error(f"[{context}] RequestException: {e}")
            break

        time.sleep(2 ** attempt)

    logging.error(f"[{context}] All retry attempts failed.")
    return False

def handle_graph_api_error(response: requests.Response, context: str = "") -> None:
    """
    Handles and logs errors from Microsoft Graph API responses.
    """
    status_code = response.status_code

    try:
        result = response.json()
        error = result.get("error", {})
        code = error.get("code", "UnknownError")
        message = error.get("message", "No error message provided.")
    except (ValueError, AttributeError) as e:
        code = "InvalidResponse"
        message = f"Failed to parse error response: {e}"
        logging.error(f"Raw response: {response.text}")

    prefix = f"[{context}] " if context else ""
    logging.warning(f"{prefix}Http Status Code: {status_code} - {code}.")
    logging.warning(f"{prefix}{message}")

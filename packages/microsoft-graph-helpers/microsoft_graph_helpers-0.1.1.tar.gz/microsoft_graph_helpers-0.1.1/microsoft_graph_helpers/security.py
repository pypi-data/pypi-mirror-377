import json, logging, requests
from typing import List, Union
from .core import get_headers, make_graph_api_request

def run_hunting_query(bearer_token: str, query: str, timespan: str = "P90D") -> Union[List[dict], bool]:
    logging.debug("Submitting Hunting Query as POST request to Graph API.")

    url = "https://graph.microsoft.com/v1.0/security/runHuntingQuery"
    headers = get_headers(bearer_token)
    payload = {
        "Query": query,
        "Timespan": timespan
    }

    response = make_graph_api_request(
        method="POST",
        url=url,
        headers=headers,
        payload=payload,
        context="run_hunting_query"
    )

    if isinstance(response, dict) and "results" in response:
        logging.debug("200: Hunting query received successful response")
        return response["results"]
    return False

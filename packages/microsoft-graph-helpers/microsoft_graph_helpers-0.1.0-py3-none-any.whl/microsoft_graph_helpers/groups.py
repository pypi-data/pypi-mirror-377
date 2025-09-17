import json, logging, requests
from .core import get_headers, make_graph_api_request

def get_group_guid(bearer_token: str, group_name: str):
    logging.debug(f"Obtaining GUID for group named {group_name} from Microsoft Graph API.")

    url = f"https://graph.microsoft.com/v1.0/groups?$filter=displayName eq '{group_name}'"
    headers = get_headers(bearer_token)
    response = make_graph_api_request(
        method="GET",
        url=url,
        headers=headers,
        context="get_group_guid"
    )
    if isinstance(response, dict):
        value = response.get("value", [])
        if len(value) > 1:
            logging.warning(f"Multiple groups found with name '{group_name}'. Returning the first match.")
        if value and isinstance(value, list):
            return value[0].get("id")
    return False


def get_group_members(bearer_token: str, guid: str):
    logging.debug(f"Obtaining members of group whose GUID is {guid} from Microsoft Graph API.")

    url = f"https://graph.microsoft.com/v1.0/groups/{guid}/members"
    headers = get_headers(bearer_token)

    response = make_graph_api_request(
        method="GET",
        url=url,
        headers=headers,
        context="get_group_members"
    )
    if isinstance(response, dict) and 'value' in response:
        logging.debug(f"Response from Microsoft Graph API contained {len(response['value'])} members.")
        return [member.get('mail') for member in response['value'] if member.get('mail')]
    return False


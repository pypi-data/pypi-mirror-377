import json, logging, requests, urllib.parse
from typing import List, Tuple, Union
from .core import get_headers, make_graph_api_request


def send_message_as(
    bearer_token: str,
    sender_email: str,
    recipient_email: str,
    subject: str,
    body: str,
    save_to_sent_messages: bool = False,
) -> bool:
    logging.debug(f"Sending message from {sender_email} to {recipient_email}")
    headers = get_headers(bearer_token)
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email
                    }
                }
            ]
        },
        "saveToSentItems": str(save_to_sent_messages).lower()
    }

    response = make_graph_api_request(
        method="POST",
        url=f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail",
        headers=headers,
        payload=payload,
        timeout=10,
        context="send_message_as",
    )
    if response == True:
        logging.debug(f"[send_message_as] Message sent to {recipient_email}")
    else:
        logging.debug(f"[send_message_as] Failed to send message to {recipient_email}")
    return response


def retrieve_message(
    bearer_token: str,
    user_principal_name: str,
    internet_message_id: str
) -> Tuple[Union[dict, None], Union[str, None]]:
    """
    Searches for a message by its Internet Message ID across multiple folders
    in the user's mailbox.

    Returns:
        Tuple[dict or None, str or None]: The message object and the folder name it was found in.
    """
    logging.debug(f"Searching for message ID \"{internet_message_id}\" in mailbox \"{user_principal_name}\"")
    encoded_id = urllib.parse.quote(internet_message_id)
    headers = get_headers(bearer_token)
    folders = [
        ("Messages", f"https://graph.microsoft.com/v1.0/users/{user_principal_name}/messages?$filter=internetMessageId eq '{encoded_id}'"),
        ("DeletedItems", f"https://graph.microsoft.com/v1.0/users/{user_principal_name}/mailFolders/DeletedItems/messages?$filter=internetMessageId eq '{encoded_id}'"),
        ("RecoverableItemsDeletions", f"https://graph.microsoft.com/v1.0/users/{user_principal_name}/mailFolders/RecoverableItemsDeletions/messages?$filter=internetMessageId eq '{encoded_id}'"),
        ("RecoverableItemsPurges", f"https://graph.microsoft.com/v1.0/users/{user_principal_name}/mailFolders/RecoverableItemsPurges/messages?$filter=internetMessageId eq '{encoded_id}'"),
        ("RecoverableItemsDiscoveryHolds", f"https://graph.microsoft.com/v1.0/users/{user_principal_name}/mailFolders/RecoverableItemsDiscoveryHolds/messages?$filter=internetMessageId eq '{encoded_id}'")
    ]

    for folder_name, url in folders:
        logging.debug(f"Checking folder: {folder_name}")
        response = make_graph_api_request(
            method="GET",
            url=url,
            headers=headers,
            timeout=10,
            context=f"retrieve_message:{folder_name}"
        )

        if isinstance(response, dict) and response.get("value"):
            logging.info(f"[retrieve_message] Message found in folder: {folder_name}")
            return response, folder_name

    logging.warning(f"Message ID \"{internet_message_id}\" not found in any folder for user \"{user_principal_name}\".")
    return None, None


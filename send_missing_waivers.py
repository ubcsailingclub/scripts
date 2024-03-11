import requests
import json

from config import e_signatures_token as token

ESIG_URL = f'https://esignatures.io/api/contracts?token={token}'
# you gotta quit those e-cigs Earl! It's not healthy!

def send_waiver(name, email, *, url=ESIG_URL, headers=None,
                template_id='965ec98c-3958-4bc6-b131-556918d35649'):
    """
    Sends a waiver to a signer.

    Args:
        name (str): The name of the signer.
        email (str): The email address of the signer.
        url (str, optional): The URL to send the waiver request to. Defaults to
        using esignatures.io; requires config.py file with the secret token.
        headers (dict, optional): Additional headers to include in the request.
        Defaults to {'Content-type': 'application/json'}.
        template_id (str, optional): The ID of the waiver template to use. Defaults
        to the UBC Sailing Club Membership Waiver Form.

    Returns:
        dict: The JSON response from the request.

    """
    if headers is None:
        headers = {}
    headers.setdefault('Content-type', 'application/json')

    data = {
        "template_id": template_id,
        "signers": [
            {
                "name": name,
                "email": email
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

import requests
import json

from config import e_signatures_token as token

ESIG_URL = f'https://esignatures.io/api/contracts%s?token={token}'
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

    response = requests.post(url % '', headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()

def query_contract(contract_id, *, url=ESIG_URL, headers=None):
    """
    Queries the status of a contract.

    Args:
        contract_id (str): The ID of the contract to query.
        url (str, optional): The URL to query the contract status from. Defaults
        to using esignatures.io; requires config.py file with the secret token.
        headers (dict, optional): Additional headers to include in the request.
        Defaults to {'Content-type': 'application/json'}.

    Returns:
        dict: The JSON response from the request.

    """
    if headers is None:
        headers = {}
    headers.setdefault('Content-type', 'application/json')

    response = requests.get(url % f'/{contract_id}', headers=headers)
    response.raise_for_status()
    return response.json()

def download_all_waivers(contracts_data, output_dir):
    """
    Downloads all waivers from the e-signatures service as PDF.

    Args:
        contracts_data (string): The contracts data CSV exported from
        the e-signatures website.
        output_dir (string): The directory to save the PDFs to.

    Notes:
    ------
    Might get rate-limited and/or blocked if there's too many requests.
    This function shouldn't need to be called anymore, as the waivers are
    automatically saved to the Google Drive.

    """
    import urllib.request
    import pandas as pd
    import tqdm

    output_dir += '/' if not output_dir.endswith('/') else ''
    df = pd.read_csv(contracts_data)

    for contract_id in tqdm.tqdm(df['Contract ID']):
        response = query_contract(contract_id)
        url = response['data']['contract_pdf_url']
        timestamp = url.split('/')[-1].split('-utc-')[0]
        name = response['data']['signers'][0]['name']
        urllib.request.urlretrieve(url, output_dir + timestamp + ' ' + name + '.pdf')

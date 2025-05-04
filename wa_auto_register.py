import datetime
import urllib.parse

import parse # pip install parse
import numpy as np # pip install numpy

from waapi import WildApricotClient
from config import wild_apricot_api_key, ubc_auto_register_passphrase

email = 'adam.subanloewen@gmail.com'
hours_before = 48
event_url = 'https://ubcsailing.org/event-5915272'

def get_member_by_email(email):
    params = {'$filter': f'member eq true AND Email eq {email}',
              '$top': '1',
              '$async': 'false'}
    request_url = contacts_requrl + '?' + urllib.parse.urlencode(params)
    print(request_url)
    return api.request(request_url).Contacts[0]

def register_for_event(event, contact, registration_type):
    body = {
        "Event": {
            "Id": event.Id
        },
        "Contact": {
            "Id": contact.Id
        },
        "RegistrationTypeId": registration_type.Id,
        "Memo": 'Registered by automated script at the eleventh hour, please "Confirm without Invoice". If you have any questions, contact the IT Manager.',
    }
    registration = api.request(event_reg_requrl, post_payload=body, method='POST')
    return registration

allowed_window = datetime.timedelta(hours=hours_before)
event_furl = 'https://ubcsailing.org/event-{event_id}'
result = parse.parse(event_furl, event_url)
if result is None:
    message = f"Invalid event URL: {event_url}, expected format: {event_furl}"
    raise ValueError(message) # reply with error message
event_id = result["event_id"]

api = WildApricotClient(api_key=wild_apricot_api_key)
api.authenticate_with_apikey()
# print(api.request("/")) # to get latest API version
accounts = api.request("/v2.3/accounts")
account = accounts[0]

# print([res.Name for res in account.Resources])
contacts_requrl = next(res for res in account.Resources if res.Name == 'Contacts').Url
event_requrl = next(res for res in account.Resources if res.Name == 'Events').Url + event_id
event_reg_requrl = next(res for res in account.Resources if res.Name == 'Event registrations').Url

contact = get_member_by_email(email)
event = api.request(event_requrl)
start = event.StartDate
registrants = event.ConfirmedRegistrationsCount + event.PendingRegistrationsCount
max_registrants = event.RegistrationsLimit
tags = event.Tags # could use to track certification level / prerequisites
registration_types = event.Details.RegistrationTypes
# High-Wind Windsurfing L3 lessons also allow existing L3 members to tag along for safety
# in general, users wouldn't be accessing this service for free registration types,
# so pick the most expensive; usually this will be the only one
most_expensive = np.argmax([reg_type.BasePrice for reg_type in registration_types])
registration_type = registration_types[most_expensive]

if not event.RegistrationEnabled:
    message = f"Registration is not enabled for event {event.Name}."
    raise ValueError(message) # reply with error message

registration = register_for_event(event, contact, registration_type)
print(registration)

# RPC requests don't work; so manually create invoice and payment, and settle invoice with payment all using the API
# reply to user with message to ignore the "pending payment" email and confirm it worked
# test lesson confirmed email got sent



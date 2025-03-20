__author__ = 'dsmirnov@wildapricot.com'

import urllib.parse
import json

from waapi import WildApricotClient
from config import wild_apricot_api_key

def get_10_active_members():
    params = {'$filter': 'member eq true',
              '$top': '2',
              '$async': 'false'}
    request_url = contactsUrl + '?' + urllib.parse.urlencode(params)
    print(request_url)
    return api.request(request_url).Contacts

def get_member_by_email(email):
    params = {'$filter': f'member eq true AND Email eq {email}',
              '$top': '1',
              '$async': 'false'}
    request_url = contactsUrl + '?' + urllib.parse.urlencode(params)
    print(request_url)
    return api.request(request_url).Contacts[0]

def print_contact_info(contact):
    print('Contact details for ' + contact.DisplayName + ', ' + contact.Email)
    print('Main info:')
    print('\tID:' + str(contact.Id))
    print('\tFirst name:' + contact.FirstName)
    print('\tLast name:' + contact.LastName)
    print('\tEmail:' + contact.Email)
    print('\tAll contact fields:')
    for field in contact.FieldValues:
        if field.Value is not None:
            print('\t\t' + field.FieldName + ':' + repr(field.Value))


def create_contact(email, name):
    data = {
        'Email': email,
        'FirstName': name}
    return api.request(contactsUrl, api_request_object=data, method='POST')


def archive_contact(contact_id):
    data = {
        'Id': contact_id,
        'FieldValues': [
            {
                'FieldName': 'Archived',
                'Value': 'true'}]
    }
    return api.request(contactsUrl + str(contact_id), api_request_object=data, method='PUT')

if __name__ == '__main__':
    api = WildApricotClient(api_key=wild_apricot_api_key)
    api.authenticate_with_apikey()
    # api.authenticate_with_contact_credentials("ADMINISTRATOR_USERNAME", "ADMINISTRATOR_PASSWORD")
    accounts = api.request("/v2/accounts")
    account = accounts[0]

    print(account.PrimaryDomainName)

    contactsUrl = next(res for res in account.Resources if res.Name == 'Contacts').Url

    # get top 10 active members and print their details
    contacts = get_10_active_members()
    for contact in contacts:
        print_contact_info(contact)

    # get contact by email
    contact = get_member_by_email('adam.subanloewen@gmail.com')
    print_contact_info(contact)
    print('Parsed certs:')
    equip_cert = [elem.Label for elem in contact["Equipment certification achieved"]]
    print(equip_cert)


    # create new contact
    # new_copntact = create_contact('some_email1@invaliddomain.org', 'John Doe')
    # print_contact_info(new_copntact)

    # finally archive it
    # archived_contact = archive_contact(new_copntact.Id)
    # print_contact_info(archived_contact)

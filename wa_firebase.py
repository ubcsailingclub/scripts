import datetime
import tzlocal
import urllib.parse

from waapi import WildApricotClient
from config import wild_apricot_api_key


def now():
    return datetime.datetime.now(tz=tzlocal.get_localzone())


class WildApricotCustomClient(WildApricotClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authenticate_with_apikey()
        accounts = self.request("/v2/accounts")
        self.account = accounts[0]

        self.contacts_requrl = next(res for res in self.account.Resources if res.Name == 'Contacts').Url
        self.groups_requrl = next(res for res in self.account.Resources if res.Name == 'Member groups').Url

    def get_changed_members_since_datetime(self, datetime, fields):
        """
        All WA contacts that have been created (website profile or membership) or
        modified (changed level or edited profile including card number or equipment certs) since datetime.

        Notes
        -----
        Membership level IDs:
        1144626: General Member
        1258075: JSCA Staff
        1144628: Social Member
        1144621: UBC Student

        References
        ----------
        https://gethelp.wildapricot.com/en/articles/502-contacts-admin-api-call
        https://app.swaggerhub.com/apis-docs/WildApricot/wild-apricot_public_api/7.24.0#/Contacts/GetContactsList

        """
        params = {'$filter': (f"Member eq true AND 'Membership status' eq Active AND 'Membership level ID' ne 1144628 AND ("
                              f"'Creation date' ge {datetime.isoformat()} OR 'Member since' ge {datetime.isoformat()} OR "
                              f"'Level last changed' ge {datetime.isoformat()} OR "
                              f"'Profile last updated' ge {datetime.isoformat()})"),
                  '$select': ','.join(f"'{field}'" for field in fields),
                  '$async': 'false'}
        request_url = self.contacts_requrl + '?' + urllib.parse.urlencode(params)
        return self.request(request_url).Contacts


if __name__ == '__main__':
    since = now() - datetime.timedelta(minutes=5)
    fields = ['First Name', 'Last Name', 'Jericho Card Number', 'Equipment certification achieved']

    api = WildApricotCustomClient(api_key=wild_apricot_api_key)
    updated_contacts = api.get_changed_members_since_datetime(since, fields)
    print(updated_contacts)

    groups = api.request(api.groups_requrl)
    print(groups)

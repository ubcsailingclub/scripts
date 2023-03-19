# scripts

### Purge Contacts

Use this script to set contacts to archived in Wild Apricot.

Steps:

1. After logging into your Wild Apricot Admin account, go to `admin/contacts/` to download a list of contacts. Include the `User ID, Membership status, Subscribed to emails, and Archived` fields. 

2. Go to `admin/emails/log/`, and find the last few newsletters that were sent through Wild Apricot (Search UBSea). Export `User ID` and `Opened` fields. 

3. Replace the file names in the script with those that you just downloaded (marked UDPATE). 

4. Run the script. 

5. In Wild Apricot, go to `admin/contacts/import/upload-file/` and import the file created by the script. 


##### Rolling Back

If you find that you have made a mistake, rollback the data by importing the original contacts list that you downloaded in Wild Apricot `admin/contacts/import/upload-file/`.

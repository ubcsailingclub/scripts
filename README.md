# scripts

### Purge Contacts

Use this script to set contacts to archived in Wild Apricot.

Steps:

1. After logging into your Wild Apricot Admin account, go to `admin/contacts/` to download a list of contacts. Include the `User ID, Membership status, Subscribed to emails, and Archived` fields.

2. Go to `admin/emails/log/`, and find the last few newsletters that were sent through Wild Apricot (Search UBSea). Export `User ID`, `Opened`, and `Clicked` fields.

3. Replace the file names in the script with those that you just downloaded (marked UDPATE). Also update the output filename at the end of the script. Keep in mind the full file path.

4. Ensure pandas is installed. Run the script.

5. In Wild Apricot, go to `admin/contacts/import/upload-file/` and import the file created by the script. Read each import page and select the appropriate options, most likely the defaults are all correct. Don't dilly-dally: if a new member changes their account between when you downloaded the files and then re-uploaded them you might revert their change inadvertantly: so to avoid this race condition, keep it quick and maybe do at night like real hackers :P

##### Rolling Back

If you find that you have made a mistake, rollback the data by importing the original contacts list that you downloaded in Wild Apricot `admin/contacts/import/upload-file/`.

import pandas as pd
from functools import reduce

# load data
# UPDATE the file names to read from
contacts = pd.read_csv("../2024-07-30 Contacts UBC Sailing Club.csv")
newsletters = [pd.read_excel("../2024-07-30 Email details UBC Sailing Club.xls")]

# find members that can potentially be dropped (everyone who is Lapsed or was never active)
dropCandidates =  set(contacts.loc[(contacts["Membership status"] == "Lapsed") | contacts["Membership status"].isnull(), "User ID"])

# always drop candidates that are not subscribed to newsletter
toRemove = set()

nonSubscribers = set(contacts.loc[contacts["Subscribed to emails"] == "no", "User ID"])
toRemove |= nonSubscribers & dropCandidates

# # drop candidates that did not open any of the latest newsletters
# nonReaders = []
# for df in newsletters:
#     nonReaders.append(set(df.loc[df["Opened"] == "No", "User ID"]))
# notReadAny = reduce(lambda a, b: a & b, nonReaders)

# drop candidates that did not click any event in the latest newsletters
non_clickers = []
for newsletter in newsletters:
    non_clickers.append(set(newsletter.loc[newsletter["Clicked"] == "No", "User ID"]))
not_click_any = reduce(lambda a, b: a & b, non_clickers)

toRemove |= not_click_any & dropCandidates

# export user ids that will be archived
print(f"{len(toRemove)} members will be archived. See yaaa")

rollForward = contacts.loc[contacts["User ID"].isin(toRemove), ["User ID"]]
rollForward["Archived"] = "yes"

# UPDATE the file name to export the results to 
rollForward.to_csv("../2024-07-30 Post-Archival Contacts UBC Sailing Club.csv", index=False,
          header=True)

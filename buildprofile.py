# build_profiles.py
HOTELS_FILE = "hotels_processed.csv"
USERS_FILE  = "UserData.csv"
OUT_FILE    = "Group2_Part1_Profile11.csv"   # change Group1 -> your group number

# 1) Load hotel features into a dictionary
item_features = {}  # itemid -> list of features
with open(HOTELS_FILE, "r", encoding="utf-8") as f:
    header = f.readline()  # skip header
    for line in f:
        parts = line.strip().split(",")
        if len(parts) < 4:
            continue
        iid = int(parts[0])
        features = parts[3].split("|") if parts[3] else []
        item_features[iid] = features

# 2) Load user->visited items
user2items = {}  # userid -> list of itemids
with open(USERS_FILE, "r", encoding="utf-8") as f:
    header = f.readline().strip().split(",")
    for line in f:
        row = line.strip().split(",")
        if len(row) < 2: 
            continue
        uid = int(row[0])
        iid = int(row[1])
        if uid not in user2items:
            user2items[uid] = []
        if iid not in user2items[uid]:
            user2items[uid].append(iid)

# 3) Pick first 5 users
user_ids = sorted(user2items.keys())[:5]

# 4) Build profiles (union of all features of visited hotels)
user_profiles = {}
for uid in user_ids:
    feats = []
    for iid in user2items[uid]:
        if iid in item_features:
            for ftr in item_features[iid]:
                if ftr not in feats:
                    feats.append(ftr)
    user_profiles[uid] = feats

# 5) Write profiles to CSV
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("userid,features\n")
    for uid in user_ids:
        feats_str = "|".join(user_profiles[uid])
        f.write(f"{uid},{feats_str}\n")

print("Profiles saved to", OUT_FILE)
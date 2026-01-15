# jaccard_matrix.py
HOTELS_FILE = "hotels_processed.csv"
PROFILES_FILE = "Group2_Part1_Profile11.csv"   # change Group1 -> your group number
USERS_FILE = "UserData.csv"
OUT_FILE = "Group2_Part1_SimMatrix12.csv"

# 1) Load hotel features
item_features = {}
with open(HOTELS_FILE, "r", encoding="utf-8") as f:
    f.readline()  # skip header
    for line in f:
        parts = line.strip().split(",")
        if len(parts) < 4:
            continue
        iid = int(parts[0])
        feats = parts[3].split("|") if parts[3] else []
        item_features[iid] = feats

all_items = sorted(item_features.keys())

# 2) Load user profiles
user_profiles = {}
with open(PROFILES_FILE, "r", encoding="utf-8") as f:
    f.readline()  # skip header
    for line in f:
        uid_str, feats_str = line.strip().split(",", 1)
        uid = int(uid_str)
        feats = feats_str.split("|") if feats_str else []
        user_profiles[uid] = feats

# 3) Load visited hotels
user2items = {}
with open(USERS_FILE, "r", encoding="utf-8") as f:
    f.readline()  # skip header
    for line in f:
        row = line.strip().split(",")
        if len(row) < 2: continue
        uid = int(row[0])
        iid = int(row[1])
        if uid not in user2items:
            user2items[uid] = []
        if iid not in user2items[uid]:
            user2items[uid].append(iid)

# keep the 5 users from profiles file
user_ids = sorted(user_profiles.keys())

# 4) Jaccard function
def jaccard(listA, listB):
    setA = set(listA)
    setB = set(listB)
    if not setA and not setB:
        return 0.0
    inter = 0
    for x in setA:
        if x in setB:
            inter += 1
    union = len(setA) + len(setB) - inter
    if union == 0:
        return 0.0
    return inter / union

# 5) Build matrix and write file
with open(OUT_FILE, "w", encoding="utf-8") as f:
    # header row
    f.write("userid")
    for iid in all_items:
        f.write("," + str(iid))
    f.write("\n")

    for uid in user_ids:
        f.write(str(uid))
        for iid in all_items:
            if iid in user2items.get(uid, []):
                f.write(",")   # leave blank for visited
            else:
                score = jaccard(user_profiles[uid], item_features[iid])
                f.write("," + "{:.6f}".format(score))
        f.write("\n")

print("Similarity matrix saved to", OUT_FILE)
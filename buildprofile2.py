# build_profiles_part2.py
HOTELS_FILE = "hotels_processed.csv"
USERS_FILE  = "UserData.csv"
OUT_FILE    = "Group2_Part2_Profile21.csv"   # change Group1 -> your group number

# ---------- helpers ----------
def split_features(s):
    if not s:
        return []
    parts = s.split("|")
    # de-duplicate within one item
    uniq = []
    seen = {}
    for p in parts:
        p = p.strip()
        if p and (p not in seen):
            seen[p] = True
            uniq.append(p)
    return uniq

# ---------- 1) DF per feature ----------
feature_df = {}      # feature -> document frequency
item_features = {}   # itemid -> list of unique features
N_items = 0

with open(HOTELS_FILE, "r", encoding="utf-8") as f:
    header = f.readline()  # skip header line
    for line in f:
        cols = line.rstrip("\n").split(",")
        if len(cols) < 4:
            continue
        try:
            iid = int(cols[0])
        except:
            continue
        feats = split_features(cols[3])
        item_features[iid] = feats
        N_items += 1
        # update DF (count each feature once per item)
        seen_local = {}
        for ft in feats:
            if ft not in seen_local:
                seen_local[ft] = True
                feature_df[ft] = feature_df.get(ft, 0) + 1

# ---------- 2) IDF ----------
idf = {}  # feature -> idf weight (N_items / df)
for ft in feature_df:
    df = feature_df[ft]
    if df <= 0:
        idf[ft] = 0.0
    else:
        # simple inverse frequency (no log, no imports)
        idf[ft] = float(N_items) / float(df)

# ---------- 3) Item vectors (binary TF × IDF) ----------
item_vector = {}  # itemid -> dict(feature -> weight)
for iid in item_features:
    feats = item_features[iid]
    vec = {}
    for ft in feats:
        vec[ft] = idf.get(ft, 0.0)  # TF is 1 for present features
    item_vector[iid] = vec

# ---------- 4) Load user visits; pick first 5 users ----------
user2items = {}  # userid -> list of visited iids
with open(USERS_FILE, "r", encoding="utf-8") as f:
    header = f.readline().strip().split(",")
    # try to locate columns robustly
    # expect 'userid' and 'itemid' or ' itemid' depending on file
    try:
        uid_idx = header.index("userid")
    except:
        uid_idx = 0
    # find the itemid-ish column
    iid_idx = -1
    for i in range(len(header)):
        h = header[i].strip().lower()
        if "itemid" in h:
            iid_idx = i
            break
    if iid_idx == -1:
        iid_idx = 1  # fallback

    for line in f:
        row = line.strip().split(",")
        if len(row) <= iid_idx:
            continue
        try:
            uid = int(row[uid_idx])
            iid = int(row[iid_idx])
        except:
            continue
        if uid not in user2items:
            user2items[uid] = []
        # avoid duplicates
        if iid not in user2items[uid]:
            user2items[uid].append(iid)

# choose first 5 user IDs that appear
all_user_ids = sorted(user2items.keys())
user_ids = all_user_ids[:5]

# ---------- 5) Build centroid profile per user ----------
user_profile = {}  # userid -> dict(feature -> avg weight)

for uid in user_ids:
    visited = user2items.get(uid, [])
    count = 0
    acc = {}  # feature -> sum of weights across visited items
    for iid in visited:
        vec = item_vector.get(iid)
        if not vec:
            continue
        count += 1
        # add vector
        for ft in vec:
            acc[ft] = acc.get(ft, 0.0) + vec[ft]

    # average
    prof = {}
    if count > 0:
        for ft in acc:
            prof[ft] = acc[ft] / float(count)
    # store
    user_profile[uid] = prof

# ---------- 6) Write Part II profiles ----------
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("userid,features\n")
    for uid in user_ids:
        prof = user_profile.get(uid, {})
        # turn into token:weight, sorted by descending weight then token
        items = []
        # simple list + manual sort (bubble) to avoid imports
        for ft in prof:
            items.append((ft, prof[ft]))

        # sort by (-weight, token)
        n = len(items)
        for i in range(n - 1):
            for j in range(n - 1 - i):
                ft1, w1 = items[j]
                ft2, w2 = items[j + 1]
                swap = False
                if w2 > w1:
                    swap = True
                elif w2 == w1 and ft2 < ft1:
                    swap = True
                if swap:
                    tmp = items[j]
                    items[j] = items[j + 1]
                    items[j + 1] = tmp

        # format: token:weight
        parts = []
        for (ft, w) in items:
            parts.append(ft + ":" + ("{:.6f}".format(w)))
        f.write(str(uid) + "," + "|".join(parts) + "\n")

print("Part II profiles saved to", OUT_FILE)
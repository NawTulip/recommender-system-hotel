# build_model_part2.py
HOTELS_FILE   = "hotels_processed.csv"
USERS_FILE    = "UserData.csv"
PROFILES_FILE = "Group2_Part2_Profile21.csv"   # change Group1 -> your group number
OUT_FILE      = "Group2_Part2_Model22.csv"     # change Group1 -> your group number

# -------- helpers --------
def split_features(s):
    if not s:
        return []
    parts = s.split("|")
    uniq = []
    seen = {}
    for p in parts:
        p = p.strip()
        if p and (p not in seen):
            seen[p] = True
            uniq.append(p)
    return uniq

def parse_weighted_features(s):
    # "token:weight|token:weight|..."
    feats = {}
    if not s:
        return feats
    parts = s.split("|")
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # split on last ":" to be robust if token ever contains ":"
        idx = p.rfind(":")
        if idx <= 0:
            continue
        token = p[:idx]
        w_str = p[idx+1:]
        try:
            w = float(w_str)
        except:
            w = 0.0
        feats[token] = w
    return feats

def dot(a, b):
    # a, b are dict(token -> weight)
    s = 0.0
    # iterate smaller dict for efficiency
    if len(a) > len(b):
        small = b; large = a
    else:
        small = a; large = b
    for k in small:
        if k in large:
            s += small[k] * large[k]
    return s

def norm_sq(a):
    s = 0.0
    for k in a:
        s += a[k] * a[k]
    return s

def cosine(a, b):
    # handle zero norms
    na = norm_sq(a)
    nb = norm_sq(b)
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot(a, b) / ((na ** 0.5) * (nb ** 0.5))

# -------- 1) Build DF for features & collect item features --------
feature_df = {}     # feature -> number of items containing it
item_features = {}  # itemid -> list of unique features
N_items = 0

with open(HOTELS_FILE, "r", encoding="utf-8") as f:
    f.readline()  # skip header
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
        seen_local = {}
        for ft in feats:
            if ft not in seen_local:
                seen_local[ft] = True
                feature_df[ft] = feature_df.get(ft, 0) + 1

# -------- 2) IDF and item vectors (TF is binary) --------
idf = {}  # feature -> N_items / df
for ft in feature_df:
    df = feature_df[ft]
    if df <= 0:
        idf[ft] = 0.0
    else:
        idf[ft] = float(N_items) / float(df)

item_vector = {}  # itemid -> dict(feature -> weight)
for iid in item_features:
    feats = item_features[iid]
    vec = {}
    for ft in feats:
        vec[ft] = idf.get(ft, 0.0)
    item_vector[iid] = vec

# -------- 3) Load visited items per user --------
user2items = {}  # userid -> list of visited itemids
with open(USERS_FILE, "r", encoding="utf-8") as f:
    header = f.readline().strip().split(",")
    # locate columns
    try:
        uid_idx = header.index("userid")
    except:
        uid_idx = 0
    iid_idx = -1
    for i in range(len(header)):
        if "itemid" in header[i].strip().lower():
            iid_idx = i
            break
    if iid_idx == -1:
        iid_idx = 1

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
        if iid not in user2items[uid]:
            user2items[uid].append(iid)

# -------- 4) Load Part II user profiles (weighted) --------
user_profile = {}  # userid -> dict(feature -> weight)
user_ids = []

with open(PROFILES_FILE, "r", encoding="utf-8") as f:
    f.readline()  # skip header
    for line in f:
        # split only on first comma to keep feature string intact
        idx = line.find(",")
        if idx == -1:
            continue
        uid_str = line[:idx].strip()
        feats_str = line[idx+1:].strip()
        try:
            uid = int(uid_str)
        except:
            continue
        prof = parse_weighted_features(feats_str)
        user_profile[uid] = prof
        user_ids.append(uid)

# -------- 5) Build cosine similarity matrix & write CSV --------
# Columns are sorted itemids
all_items = []
for iid in item_vector:
    all_items.append(iid)
# manual sort
for i in range(len(all_items)-1):
    for j in range(len(all_items)-1-i):
        if all_items[j+1] < all_items[j]:
            tmp = all_items[j]
            all_items[j] = all_items[j+1]
            all_items[j+1] = tmp

with open(OUT_FILE, "w", encoding="utf-8") as f:
    # header row
    f.write("userid")
    for iid in all_items:
        f.write("," + str(iid))
    f.write("\n")

    for uid in user_ids:
        f.write(str(uid))
        visited = user2items.get(uid, [])
        prof = user_profile.get(uid, {})
        for iid in all_items:
            if iid in visited:
                # blank for visited items
                f.write(",")
            else:
                vec = item_vector.get(iid, {})
                sim = cosine(prof, vec)
                f.write("," + "{:.6f}".format(sim))
        f.write("\n")

print("Part II model (similarity matrix) saved to", OUT_FILE)
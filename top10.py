# top10_part2.py
HOTELS_FILE = "hotels_processed.csv"
MODEL_FILE  = "Group2_Part2_Model22.csv"     # change Group1 -> your group number
OUT_FILE    = "Group2_Part2_Recommendation23.csv"

# 1) Build lookup: itemid -> (hotelid, hotelname)
item_lookup = {}  # int -> (int, str)
with open(HOTELS_FILE, "r", encoding="utf-8") as f:
    header = f.readline().strip().split(",")  # itemid,hotelid,hotelname,features
    for line in f:
        parts = line.rstrip("\n").split(",")
        if len(parts) < 3:
            continue
        # parse ids safely
        try:
            iid = int(parts[0])
        except:
            continue
        hid = 0
        if parts[1].strip() != "":
            try:
                hid = int(parts[1])
            except:
                hid = 0
        hname = parts[2].replace("\n", " ").replace("\r", " ")
        item_lookup[iid] = (hid, hname)

# 2) Read similarity matrix and compute Top-10 per user
recs = []  # (userid, itemid, hotelid, hotelname, similarity)

with open(MODEL_FILE, "r", encoding="utf-8") as f:
    # header: userid,<itemid1>,<itemid2>,...
    header = f.readline().strip().split(",")
    if len(header) <= 1:
        pass
    else:
        # parse item ids for columns
        item_ids = []
        for c in header[1:]:
            c = c.strip()
            try:
                item_ids.append(int(c))
            except:
                item_ids.append(None)  # keep alignment

        for line in f:
            if not line.strip():
                continue
            row = line.rstrip("\n").split(",")
            # first col is userid
            try:
                uid = int(row[0].strip())
            except:
                continue

            # collect (score, itemid) for non-empty cells
            scored = []
            for i in range(1, len(row)):
                iid = item_ids[i - 1]
                if iid is None:
                    continue
                cell = row[i].strip()
                if cell == "":
                    # blank means visited in our pipeline -> skip
                    continue
                # parse similarity float
                try:
                    s = float(cell)
                except:
                    continue
                scored.append((s, iid))

            # sort scored by similarity desc, then itemid asc — manual bubble sort (no imports)
            n = len(scored)
            for a in range(n - 1):
                for b in range(n - 1 - a):
                    s1, id1 = scored[b]
                    s2, id2 = scored[b + 1]
                    swap = False
                    if s2 > s1:
                        swap = True
                    elif s2 == s1 and id2 < id1:
                        swap = True
                    if swap:
                        tmp = scored[b]
                        scored[b] = scored[b + 1]
                        scored[b + 1] = tmp

            # take Top-10
            limit = 10 if n >= 10 else n
            for t in range(limit):
                s, iid = scored[t]
                hid, hname = item_lookup.get(iid, (0, ""))
                recs.append((uid, iid, hid, hname, s))

# 3) Write output CSV
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("userid,itemid,hotelid,hotelname,similarity\n")
    for (uid, iid, hid, hname, s) in recs:
        # basic cleaning in case hotelname has commas or newlines already removed
        name = hname.replace("\n", " ").replace("\r", " ")
        f.write(str(uid)); f.write(",")
        f.write(str(iid)); f.write(",")
        f.write(str(hid)); f.write(",")
        f.write(name); f.write(",")
        f.write("{:.6f}".format(s)); f.write("\n")

print("Top-10 recommendations saved to", OUT_FILE)
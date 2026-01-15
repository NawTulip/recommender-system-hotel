# top5_recommendations.py
HOTELS_FILE = "hotels_processed.csv"
SIM_FILE    = "Group2_Part1_SimMatrix12.csv"   # change Group1 -> your group number
OUT_FILE    = "Group2_Part1_Recommendation13.csv"

# 1) Build a lookup: itemid -> (hotelid, hotelname)
item_lookup = {}  # int -> (int, str)
with open(HOTELS_FILE, "r", encoding="utf-8") as f:
    header = f.readline().strip().split(",")  # itemid,hotelid,hotelname,features
    # find safe column positions
    # assume order is itemid,hotelid,hotelname,features
    for line in f:
        parts = line.strip().split(",")
        if len(parts) < 3:
            continue
        try:
            iid = int(parts[0])
        except:
            continue
        hid_str = parts[1] if len(parts) > 1 else ""
        hname   = parts[2] if len(parts) > 2 else ""
        try:
            hid = int(hid_str)
        except:
            hid = 0
        item_lookup[iid] = (hid, hname)

# 2) Read similarity matrix and compute Top-5 per user
recommendations = []  # list of rows to write

with open(SIM_FILE, "r", encoding="utf-8") as f:
    # header row: userid, <itemid1>, <itemid2>, ...
    header = f.readline().strip().split(",")
    if len(header) <= 1:
        # nothing to do
        pass
    else:
        # columns after first are itemids
        item_ids = []
        for c in header[1:]:
            try:
                item_ids.append(int(c))
            except:
                item_ids.append(None)  # keep position alignment even if bad

        for line in f:
            row = line.strip().split(",")
            if len(row) == 0:
                continue
            try:
                uid = int(row[0])
            except:
                continue

            # Collect (score, itemid) for non-visited cells (non-empty)
            scored_items = []
            for i in range(1, len(row)):
                iid = item_ids[i - 1]  # align with header
                if iid is None:
                    continue
                cell = row[i].strip()
                if cell == "":  # visited -> left blank
                    continue
                # parse similarity
                try:
                    s = float(cell)
                except:
                    continue
                scored_items.append((s, iid))

            # Sort: highest similarity first, then smaller itemid
            # (negative score for descending sort without imports)
            for j in range(len(scored_items) - 1):
                # simple bubble-sort style to avoid imports; fine for small lists
                for k in range(len(scored_items) - 1 - j):
                    s1, id1 = scored_items[k]
                    s2, id2 = scored_items[k + 1]
                    swap = False
                    if s2 > s1:
                        swap = True
                    elif s2 == s1 and id2 < id1:
                        swap = True
                    if swap:
                        tmp = scored_items[k]
                        scored_items[k] = scored_items[k + 1]
                        scored_items[k + 1] = tmp

            # Take Top-5
            limit = 5 if len(scored_items) >= 5 else len(scored_items)
            for t in range(limit):
                s, iid = scored_items[t]
                hid, hname = item_lookup.get(iid, (0, ""))
                recommendations.append((uid, iid, hid, hname, s))

# 3) Write output CSV
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("userid,itemid,hotelid,hotelname,similarity\n")
    for (uid, iid, hid, hname, s) in recommendations:
        # Ensure commas in hotel names won't break CSV too badly:
        # (basic handling; if you need full CSV quoting you'd implement manual quoting)
        hname_clean = hname.replace("\n", " ").replace("\r", " ")
        f.write(str(uid)); f.write(",")
        f.write(str(iid)); f.write(",")
        f.write(str(hid)); f.write(",")
        f.write(hname_clean); f.write(",")
        f.write("{:.6f}".format(s)); f.write("\n")

print("Top-5 recommendations saved to", OUT_FILE)
# preprocess_hotels.py
IN_FILE = "HOTEL_OUTDATASET.CSV"
OUT_FILE = "hotels_processed.csv"

def norm(s):
    if s is None:
        return ""
    return s.strip().lower()

def parse_amenities(s):
    result = []
    if s is None: 
        return result
    parts = s.split(";")
    for p in parts:
        p = norm(p)
        if p != "" and ("amen=" + p) not in result:
            result.append("amen=" + p)
    return result

agg = {}  # itemid -> info dict

with open(IN_FILE, "r", encoding="utf-8") as f:
    header = f.readline().strip().split(",")
    for line in f:
        row = line.strip().split(",")
        if len(row) < len(header):
            continue
        record = dict(zip(header, row))

        try:
            iid = int(record["itemid"])
        except:
            continue

        if iid not in agg:
            agg[iid] = {
                "hotelid": record.get("hotelid", ""),
                "hotelname": record.get("hotelname", ""),
                "ptype": "",
                "star": "",
                "amen": []
            }

        if agg[iid]["ptype"] == "" and record.get("propertytype"):
            agg[iid]["ptype"] = "ptype=" + norm(record["propertytype"])
        if agg[iid]["star"] == "" and record.get("starrating"):
            agg[iid]["star"] = "star=" + norm(record["starrating"])

        amenities = parse_amenities(record.get("roomamenities", ""))
        for a in amenities:
            if a not in agg[iid]["amen"]:
                agg[iid]["amen"].append(a)

# Write cleaned file
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("itemid,hotelid,hotelname,features\n")
    for iid in sorted(agg.keys()):
        d = agg[iid]
        features = []
        if d["ptype"]: features.append(d["ptype"])
        if d["star"]:  features.append(d["star"])
        features.extend(d["amen"])
        f.write(f"{iid},{d['hotelid']},{d['hotelname']},{'|'.join(features)}\n")
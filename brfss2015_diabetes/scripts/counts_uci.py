import csv, sys, math, collections, json
p = sys.argv[1]
rows = list(csv.reader(open(p, encoding="utf-8")))
h = rows[0]; data = rows[1:]
ix = {k:i for i,k in enumerate(h)}
tr = lambda x: math.floor(x*10000)/10000
print("columns", len(h), h)
print("rows", len(data))
y = collections.Counter(r[ix["Diabetes_binary"]] for r in data); print("label", dict(y), "prev", tr(int(y["1"])/len(data)))
feat = [r[1:] for r in data]  # without ID
full = collections.Counter(tuple(r) for r in feat)
dup_rows = sum(c-1 for c in full.values() if c>1)
print("exact duplicate rows (excluding ID, incl. label): extra copies", dup_rows, "share", tr(dup_rows/len(data)), "distinct", len(full))
X = collections.defaultdict(collections.Counter)
for r in data: X[tuple(r[2:])][r[1]] += 1
conf = sum(1 for v in X.values() if len(v)>1); conf_rows = sum(sum(v.values()) for v in X.values() if len(v)>1)
print("feature vectors with both labels:", conf, "rows involved", conf_rows, "share", tr(conf_rows/len(data)))
dup_pos = sum(c-1 for k,c in full.items() if c>1 and k[0]=="1"); print("extra copies among positives", dup_pos)
def h_(p1,p2): return 2*math.asin(math.sqrt(p1)) - 2*math.asin(math.sqrt(p2))
out = {}
for g in ["Income","Education","Sex","Age"]:
    c = collections.defaultdict(lambda:[0,0])
    for r in data:
        c[r[ix[g]]][0]+=1; c[r[ix[g]]][1]+= r[1]=="1"
    ks = sorted(c, key=lambda k:int(k))
    print(g, [(k, c[k][0], tr(c[k][1]/c[k][0])) for k in ks])
    pl, ph = c[ks[0]][1]/c[ks[0]][0], c[ks[-1]][1]/c[ks[-1]][0]
    pmax = max(c[k][1]/c[k][0] for k in ks); pmin = min(c[k][1]/c[k][0] for k in ks)
    print(f"  Cohen h lowest-vs-highest category {tr(abs(h_(pl,ph)))}; max-vs-min category {tr(abs(h_(pmax,pmin)))}")
# BMI range and odd values
bmi = collections.Counter(int(r[ix["BMI"]]) for r in data); print("BMI min/max", min(bmi), max(bmi), "BMI>=70 rows", sum(v for k,v in bmi.items() if k>=70))
for v in ["MentHlth","PhysHlth","GenHlth","Age","Education","Income"]:
    print(v, sorted(collections.Counter(r[ix[v]] for r in data).items(), key=lambda t:int(t[0])))

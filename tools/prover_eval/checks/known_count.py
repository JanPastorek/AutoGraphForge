import sys, json
sys.path.insert(0,"/mnt/home/japake298/project/GraphConjecturing")
import re
from pipeline import conjecture_lattice as cl
from pipeline.cegis_novelty import classify_statement
c=json.load(open('results/cegis_results.json'))['conjectures']
toks=set()
for x in c: toks |= set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", x.get("statement") or ""))
cols=sorted(toks | {"order_bigger_than_2","order_bigger_than_3"})
surv=cl.parse_survivors(c)
n=0
for s in surv:
    try:
        known,_=classify_statement(s.statement, cols)
    except Exception:
        known=False
    n+=bool(known)
print(f"current 559-entry filter flags {n} of {len(surv)} survivors as known")
print(f"run-time metadata (older table) flagged {sum(1 for x in c if (x['metadata'] or {}).get('known_as'))}")

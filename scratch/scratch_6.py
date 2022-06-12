import csv
import math
from collections import defaultdict
import re

f = open('/home/aryeht/PycharmProjects/ccdb/full_names.csv', encoding="ISO-8859-1")
r = csv.DictReader(f.readlines())
ls = [rr for rr in r]
f.close()

d = defaultdict(defaultdict)
for l in ls:
    if l['sentence'] in d[l['plant']]:
        d[l['plant']][l['sentence']].append(l['CC'])
    else:
        d[l['plant']][l['sentence']] = [l['CC']]

plants_per_sent = defaultdict(list)
ccs_per_sent = defaultdict(list)
for k, v in d.items():
    for kk, vv in v.items():
        plants_per_sent[kk].append(k)
        ccs_per_sent[kk] = vv


options = dict()
sure = dict()
uni = dict()
for k, v in d.items():
    k_union = set()
    k_counts = defaultdict(int)
    for vv in list(v.values()):
        # k_set.intersection_update(set(vv))
        for vvv in vv:
            k_counts[vvv] += 1
        k_union.update(set(vv))
    uni[k] = k_union
    options[k] = [cc for cc, count in k_counts.items() if count == max(k_counts.values())]
    if len(options[k]) == 1:
        sure[k] = options[k][0]

options2 = dict()
for (sent_ps, ps), (sent_ccs, ccs) in zip(plants_per_sent.items(), ccs_per_sent.items()):
    assert sent_ps == sent_ccs
    new_ccs = [cc for cc in ccs]
    new_ps = []
    for p in ps:
        if p in sure:
            if sure[p] in new_ccs:
                new_ccs.remove(sure[p])
        else:
            new_ps.append(p)
    if len(new_ps) == len(new_ccs):
        for p, cc in zip(new_ps, new_ccs):
            options2[p] = list(set(options[p]).difference(set(ccs).difference({cc})))



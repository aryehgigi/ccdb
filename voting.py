from collections import defaultdict
import csv
import math
import re

# read extracted full names
f = open('/full_names.csv', encoding="ISO-8859-1")
r = csv.DictReader(f.readlines())
ls = [rr for rr in r]
f.close()

# create main dictionary holding a mapping from plant to its sentence-to-ccs-list mapping
d = defaultdict(defaultdict)
for l in ls:
    if (l['sentence'], l['s2_url']) in d[l['plant']]:
        d[l['plant']][(l['sentence'], l['s2_url'])].append(l['CC'])
    else:
        d[l['plant']][(l['sentence'], l['s2_url'])] = [l['CC']]

# heuristic 1: take all of those who has only one number (in a single sentence)
ks = []
final_csv1 = []
for k, v in d.items():
    if len(v) == 1:
        (sent, url), vv = list(v.items())[0]
        if len(vv) == 1:
            ks.append(k)
            final_csv1.append({"plant": k, "CC": vv[0], "s2_url": url, "sentence": sent})

# heuristic 2: take all of those who has only one number if we intersect the numbers appearing in all their sentences
final_csv0 = []
final_csv0_unique = []
det_l = defaultdict(list)
sure0 = dict()
for k, v in d.items():
    if k not in ks:
        k_set = set(list(v.values())[0])
        for kk, vv in list(v.items()):
            k_set.intersection_update(set(vv))
            for vvv in set(vv):
                det_l[(k, vvv)].append(kk)
        if len(k_set) == 1:
            sure0[k] = list(k_set)[0]
            for (sent, url) in det_l[(k, sure0[k])]:
                final_csv0.append({"plant": k, "CC": sure0[k], "s2_url": url, "sentence": sent})
            final_csv0_unique.append({"plant": k, "CC": sure0[k], "s2_url": det_l[(k, sure0[k])][0][1], "sentence": det_l[(k, sure0[k])][0][0]})


# heuristic 3: take the majority vote (over the counts of all CCs associated with the plant)
options = dict()
sure = dict()
uni = dict()
details = defaultdict(list)
final_csv2 = []
final_csv2_unique = []
for k, v in d.items():
    k_union = set()
    k_counts = defaultdict(int)
    for kk, vv in list(v.items()):
        # k_set.intersection_update(set(vv))
        for vvv in vv:
            k_counts[vvv] += 1
            details[(k, vvv)].append(kk)
        k_union.update(set(vv))
    uni[k] = k_union
    options[k] = [(cc, details[(k, cc)]) for cc, count in k_counts.items() if count == max(k_counts.values())]
    if len(options[k]) == 1:
        sure[k], det_l = options[k][0]
        if k in sure0 and sure[k] != sure0[k]:
            sure[k] = sure0[k]
        if (k not in ks) and (k not in sure0):
            for (sent, url) in det_l:
                final_csv2.append({"plant": k, "CC": sure[k], "s2_url": url, "sentence": sent})
            final_csv2_unique.append({"plant": k, "CC": sure[k], "s2_url": det_l[0][1], "sentence": det_l[0][0]})

# UNUSED
#
# # create inverse dictionaries
# plants_per_sent = defaultdict(list)
# ccs_per_sent = defaultdict(list)
# for k, v in d.items():
#     for kk, vv in v.items():
#         plants_per_sent[kk].append(k)
#         ccs_per_sent[kk] = vv
#
# options2 = defaultdict(list)
# for (sent_ps, ps), (sent_ccs, ccs) in zip(plants_per_sent.items(), ccs_per_sent.items()):
#     assert sent_ps == sent_ccs
#     new_ccs = [cc for cc in ccs]
#     new_ps = []
#     for p in ps:
#         if p in sure:
#             if sure[p] in new_ccs:
#                 new_ccs.remove(sure[p])
#         else:
#             new_ps.append(p)
#     if len(new_ps) == len(new_ccs):
#         for p, cc in zip(new_ps, new_ccs):
#             minus = set(ccs).difference({cc})
#             for op_cc, op_evidence in options[p]:
#                 if op_cc not in minus:
#                     options2[p].append((op_cc, op_evidence))
#
#
# final_csv3_unique = []
# final_csv3 = []
# for p, v in options2.items():
#     if p not in sure and p not in sure0 and p not in ks:
#         if len(v) == 1:
#             op_cc, op_evidence = v[0]
#             for (sent, url) in op_evidence:
#                 final_csv3.append({"plant": p, "CC": op_cc, "s2_url": url, "sentence": sent})
#             final_csv3_unique.append({"plant": p, "CC": op_cc, "s2_url": op_evidence[0][1], "sentence": op_evidence[0][0]})

# calculate the distance between the plant and the number in the sentence
#   since we only have here the full name as it was shown, we need to do some algo to find it in the sent
iii = 0


def distance(plant, cc, sent):
    global iii
    d_1 = math.inf
    if plant in sent:
        d_1 = sent.index(plant)
    elif f"{plant.split()[0][0]}. {plant.split()[1]}" in sent:
        d_1 = sent.index(f"{plant.split()[0][0]}. {plant.split()[1]}")
    else:
        intersect = [w for w in plant.split() if w in sent]
        if len(intersect) == 0:
            iii += 1
            # print((iii, plant, sent))
            return math.inf
        d_1 = sent.index(intersect[-1])
    blob = [m.end(0) for m in re.finditer(f"2n.*?=\s*([0-9]+)[^a-zA-Z+]", sent) if cc in sent[m.start(0):m.end(0)]]
    return min(abs(d_2 - d_1) for d_2 in blob)


# output
final_csv = final_csv1 + final_csv0 + final_csv2
final_csv = sorted(final_csv, key=lambda x: (x["plant"], distance(x["plant"], x["CC"], x["sentence"].lower())))

fieldnames = ["plant", "CC", "s2_url", "sentence"]
with open('full_names_acc_89.csv', 'w', encoding='utf8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_csv)

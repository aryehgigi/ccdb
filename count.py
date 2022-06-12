import csv
import random


with open("./2n.csv") as f:
    r = csv.DictReader(f)
    d = {rr["sentence_text"]: rr["article_link"] for rr in r}
    sents = set(d.keys())

with open("./plantN2n.csv") as f2:
    r2 = csv.DictReader(f2)
    sents2 = set([rr["sentence_text"] for rr in r2])

assert {None} == sents2.difference(sents)

print(len(sents), len(sents2))

non_plant = list(sents.difference(sents2))
random.shuffle(non_plant)

for i in range(100):
    print(non_plant[i])

with open("Kew_Acc_Syn.csv", encoding="ISO-8859-1") as f:
    r = csv.DictReader(f)
    plants = [rr["taxon_name"] for rr in r]
    plants_lower = [p.lower() for p in plants]
    plants_partial = [pp for p in plants_lower for pp in p.split()]


def g(txt):
    return d[txt]


def g2(candidate):
    if type(candidate) == str:
        candidate = [candidate]
    for c in candidate:
        return {"exact": c.lower() in plants_lower, "partial": any(part_c.lower() in plants_partial for part_c in c.split())}


g("The species with the karyotype of 2n = 48 to 52 shared similar G-band patterns in the largest 14 autosomes and the X. Many of these G-band patterns were shared with S. hispidus and were proposed as primitive for the common ancestor of this group .")
g2("S. hispidus")

print("DONE!")

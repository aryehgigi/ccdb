import json
import csv
import re
import spacy
from tqdm import tqdm
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_lg")

f = open("plants_unique.txt", encoding="ISO-8859-1")
plants = [rr.strip().lower() for rr in f.readlines()]
f.close()
patterns = [nlp.make_doc(text) for text in plants]
matcher2 = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher2.add("TerminologyList", patterns)

f = open("Kew_Acc_Syn.csv", encoding="ISO-8859-1")
r = csv.DictReader(f)
all_plants = [rr["taxon_name"].lower() for rr in tqdm(r)]
f.close()
all_plants_minus = [p for p in all_plants if p not in plants]
plants_partials = [pp for p in all_plants_minus for pp in p.split()]
patterns4 = [nlp.make_doc(text) for text in plants_partials + plants]
matcher4 = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher4.add("TerminologyList", patterns4)


def get_segs4(txt):
    found = set()
    for s in txt.split(" . "):
        if (("2n=" in s) or ("2n =" in s)):
            m = re.findall("2n.*?=\s*([0-9]+)[^a-zA-Z+]", s)
            d = nlp(s)
            for j, (x,y,z) in enumerate(matcher4(d)):
                if j < len(m):
                    found.add((d[y:z].text, m[j]))
    return found



def get_segs2(txt):
    found = set()
    for s in txt.split(" . "):
        if (("2n=" in s) or ("2n =" in s)):
            m = re.findall("2n.*?=\s*([0-9]+)[^a-zA-Z+]", s)
            d = nlp(s)
            for j, (x,y,z) in enumerate(matcher2(d)):
                if j < len(m):
                    found.add((d[y:z].text, m[j]))
    return found


f = open("data/filtered_docs.jsonl", encoding="ISO-8859-1")
ls = f.readlines()
f.close()


def get_docs():
    docs = []
    for i, l in enumerate(ls):
        li = json.loads(l)
        doc = ""
        if 'title' in li and li['title']:
            doc += li['title']
        if 'abstract' in li and li['abstract']:
            doc += (" " if doc.endswith(".") else " . ") + li['abstract']
        if 's2orc' in li and li['s2orc'] and 'pdf_parse' in li['s2orc'] and li['s2orc']['pdf_parse']:
            if 'body_text' in li['s2orc']['pdf_parse'] and li['s2orc']['pdf_parse']['body_text']:
                for sec in li['s2orc']['pdf_parse']['body_text']:
                    if 'text' in sec and sec['text']:
                        doc += (" " if doc.endswith(".") else " . ") + sec['text']
            if 'ref_entries' in li['s2orc']['pdf_parse'] and li['s2orc']['pdf_parse']['ref_entries']:
                for ref in li['s2orc']['pdf_parse']['ref_entries'].values():
                    if 'text' in ref and ref['text']:
                        doc += (" " if doc.endswith(".") else " . ") + ref['text']
        docs.append(doc)
    return docs



piv1 = blob(get_segs4)

d3 = dict()
for k, v in piv1:
    d3[k.lower()] = v

len(d3)

f = open("plants2.txt", "w")
for k in d3.keys():
    f.write(k + "\n")

f.close()


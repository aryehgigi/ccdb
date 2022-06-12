import json
from collections import defaultdict

def get_segs(txt):
    return [seg + ("\n" if seg[-1] != "\n" else "") for seg in txt.split(". ") if (('2n=' in seg) or ('2n =' in seg))]

def match(txt):
    return txt.count('2n =') + txt.count('2n=')

def filt():
    doc_count = 0
    total_count = 0
    ls = []
    jour_doc = defaultdict(int)
    jour_tot = defaultdict(int)
    segs = []
    i = 0
    with open("data/spike_s2orc.jsonl") as f:
        l = "PLACE_HOLDER"
        while l:
            if i % 4430 == 0:
                print(i / 4430, doc_count, total_count)
            l = f.readline()
            if not l:
                break
            li = json.loads(l)
            count_in_doc = 0
            if 'title' in li and li['title']:
                count_in_doc += match(li['title'])
                segs.extend(get_segs(li['title']))
            if 'abstract' in li and li['abstract']:
                count_in_doc += match(li['abstract'])
                segs.extend(get_segs(li['abstract']))
            if 's2orc' in li and li['s2orc'] and 'pdf_parse' in li['s2orc'] and li['s2orc']['pdf_parse']:
                if 'body_text' in li['s2orc']['pdf_parse'] and li['s2orc']['pdf_parse']['body_text']:
                    for sec in li['s2orc']['pdf_parse']['body_text']:
                        if 'text' in sec and sec['text']:
                            count_in_doc += match(sec['text'])
                            segs.extend(get_segs(sec['text']))
                if 'ref_entries' in li['s2orc']['pdf_parse'] and li['s2orc']['pdf_parse']['ref_entries']:
                    for ref in li['s2orc']['pdf_parse']['ref_entries'].values():
                        if 'text' in ref and ref['text']:
                            count_in_doc += match(ref['text'])
                            segs.extend(get_segs(ref['text']))
            if count_in_doc:
                doc_count += 1
                ls.append(l)
                total_count += count_in_doc
                if 'extra' in li and li['extra'] and 'journal' in li['extra'] and li['extra']['journal']:
                    jour_doc[li['extra']['journal'].lower()] += 1
                    jour_tot[li['extra']['journal'].lower()] += count_in_doc
                else:
                    print(f'line {i} didnt have journal name')
            i += 1
    print(sorted(jour_doc.items(), key=lambda j:j[1], reverse=True))
    print(sorted(jour_tot.items(), key=lambda j:j[1], reverse=True))
    print(doc_count, total_count)
    return ls, segs


ls_w, segs_w = filt()

with open("data/filtered_docs.jsonl", "w") as f2:
    f2.writelines(ls_w)

with open("data/filtered_segs.jsonl", "w") as f3:
    f3.writelines(segs_w)

print("DONE!")


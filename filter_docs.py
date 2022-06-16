from tqdm import tqdm
import json


def match(txt):
    return (txt.find('2n =') != -1) or (txt.find('2n=') != -1)


def filt():
    ls = []
    with open("../../data/spike_s2orc.jsonl") as f:
        l = "PLACE_HOLDER"
        for i in tqdm(range(1193740)):
            l = f.readline()
            if not l:
                break
            li = json.loads(l)
            if 'title' in li and li['title']:
                if match(li['title']):
                    ls.append(l)
                    continue
            if 'abstract' in li and li['abstract']:
                if match(li['abstract']):
                    ls.append(l)
                    continue
            if 's2orc' in li and li['s2orc'] and 'pdf_parse' in li['s2orc'] and li['s2orc']['pdf_parse']:
                found = False
                if 'body_text' in li['s2orc']['pdf_parse'] and li['s2orc']['pdf_parse']['body_text']:
                    for sec in li['s2orc']['pdf_parse']['body_text']:
                        if 'text' in sec and sec['text']:
                            if match(sec['text']):
                                ls.append(l)
                                found = True
                                break
                if found:
                    continue
                if 'ref_entries' in li['s2orc']['pdf_parse'] and li['s2orc']['pdf_parse']['ref_entries']:
                    for ref in li['s2orc']['pdf_parse']['ref_entries'].values():
                        if 'text' in ref and ref['text']:
                            if match(ref['text']):
                                ls.append(l)
                                break
            i += 1
    return ls


ls_w = filt()

with open("filtered_docs.jsonl", "w") as f2:
    f2.writelines(ls_w)

print("DONE!")

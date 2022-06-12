
# Creating the ccdb dataset

## Converting s2roc to spike format

outputs spike_s2orc.jsonl
```bash
gcloud compute ssh --zone "us-west1-b" "hillel-s2-data-reader"
sudo su - hillel 
cd /mnt/disks/sdb/spike-s2orc/ 
conda activate spike-s2orc 
python spike_s2orc/organize_one_big_jsonl_5.py --metafile data/metadata.jsonl --citesfile data/citing_paper_id_num_cites.json --authorsfile data/paper_id_to_authors.json --jsondir data/jsons/ --outfile data/spike_s2orc.jsonl > out.txt 2>&1
```

## Filtering the documents

Papers which have either “2n=” or “2n =” in their title, abstract or content(body_text, ref_entries).

simply run `filter_docs.py` relatively to data/spike_s2orc.jsonl

this results in 2 files filtered_docs.jsonl (original docs but after filtering) and filtered_segs.jsonl (flattened set of sentences containing `2n=` or `2n =`)

## Indexing in Spike

with entity ruler = each plant name is a pattern resulting in 1.25M patterns)

note that the plants list is structured such that some plant names also have aliases, but for NER we just flattened everything.

# Getting upper bounds

how many sentences have also plant names. Exact match using:
- spike: `get_upper_bound_with_spike_query.py`
  - notice we didnt keep the spike results in the repo as they are too heavy (TODO: add a link to the query) 
- spacy: `get_upper_bound_with_spacy.py`

# Building a Chromosome Count Database (ccdb)

## Name extraction and resolution

- For each sentence with “2n=” or “2n =” we extracted the names of plants and numbers of the corresponding 2n and formed a mapping.
- To resolve partial names (from the previous step) we:
  - Heuristic A: extracted full names that appeared in the full context (the entire document) and contained the partial name
  - Heuristic B: extracted full names that appeared in the full context (the entire document) and contained the partial name, where the full name did not appear as a sequence in the document but rather each of its individual tokens were found “somewhere” in the full document.
  - This means that for partial names we could have a list of optional full names that resulted from Hursitic A and a list of names that resulted from Heuristic B (and a list of optional numbers just like full-names matches). We chose to continue only with those who had only up to one full name in the Heuristic A (or only one in heuristic B if none in heuristic A)


Running the `name_resolution.py` should do that (TODO - validate)

## Voting

- To choose a single number per full name, we used the following heuristics:
  - If after intersecting all the numbers appearing with a plant, only a single number remained - take that number
  - otherwise, take the majority vote (over the counts of all CCs associated with the plant)
    - in case of a tie dont take that plant

Running the `voting.py` should do that (TODO - validate)

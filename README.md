
# Creating the ccdb dataset

## Convert s2roc to spike format: outputs spike_s2orc.jsonl

```bash
gcloud compute ssh --zone "us-west1-b" "hillel-s2-data-reader"
sudo su - hillel 
cd /mnt/disks/sdb/spike-s2orc/ 
conda activate spike-s2orc 
python spike_s2orc/organize_one_big_jsonl_5.py --metafile data/metadata.jsonl --citesfile data/citing_paper_id_num_cites.json --authorsfile data/paper_id_to_authors.json --jsondir data/jsons/ --outfile data/spike_s2orc.jsonl > out.txt 2>&1
```

## Filtering the documents

Papers which have either “2n=” or “2n =” in their title, abstract or content(body_text, ref_entries).

`filter_docs.py`
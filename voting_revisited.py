import csv

# read extracted full names
f = open('full_names.csv', encoding="ISO-8859-1")
r = csv.DictReader(f.readlines())
ls = [rr for rr in r]
f.close()

# l['plant'], l['sentence'], l['s2_url'], l['CC'], l['priority']
# priority is a 4 tuple:
#   - name aliasing heuristic (values: 0-2, lower is better)
#   - amount of plants in the same sentence which this instance was found (values: 1-inf, lower is better)
#   - amount of ccs in the same sentence which this instance was found (values: 1-inf, lower is better)
#   - distance between plant and cc (values: 0-inf, lower is better)

# bucketing algorithm
lines_with_priority = []
for l in ls:
    priority = 0
    l_p = tuple(map(int, l['priority'][1:-1].split(',')))
    # Bucketing Heuristic 1: the first two name aliasing heuristics can be grouped since a singular full name found in the wider context of the partial name
    #   is most probably correct (almost like finding the full name itself in the narrower context), but the last heuristic might be too loose,
    #   since looking for the single words of the full name spread out in the wider context is a harsh assumption
    if l_p[0] == 2:
        priority += 1
    # Bucketing Heuristic 2: if the plant and the number are the only ones in the sentence, that is a strong cue.
    #   when there are a couple of plants AND a couple of numbers it's a very weak cue.
    #   a middle ground is either when there is a single plant (as it might indeed have more than one number),
    #   or when there is a single number (as it might indeed belong to a group of plants who share the same chromosome count)
    if (l_p[1] == 1) ^ (l_p[2] == 1):
        priority += 1
    elif (l_p[1] > 1) and (l_p[2] > 1):
        priority += 2
    # Bucketing Heuristic 2: when the distance between the plant and the number is too large, it lowers the chance that they belong to each other,
    #   and if the order of plant and number is reversed it should be under prioritized as well
    if l_p[3] > 8:
        priority += 1
    if l_p[4] == 1:
        priority += 1
    lines_with_priority.append(dict(l, **{"bucket": priority}))

# sort the plants by name and by their respective CC, and finally by their bucket
debug_csv = sorted(lines_with_priority, key=lambda l: (l["plant"], l["CC"], l["bucket"]))

# for the final csv, we keep only the first bucket instances of the same plant-cc pair
#   and remove duplicates on the fly
sig = ""
last_priority = -1
final_csv = []
l_set = set()
for l in debug_csv:
    if sig != l['plant'] + str(l['CC']):
        sig = l['plant'] + str(l['CC'])
        last_priority = l["bucket"]
    if l["bucket"] == last_priority:
        if str(l) not in l_set:
            final_csv.append(l)
            l_set.add(str(l))

# now resort for the final_csv by buckets
final_csv = sorted(final_csv, key=lambda l: (l["plant"], l["bucket"], l["sentence"]))

# outputs
fieldnames = ["plant", "CC", "bucket", "s2_url", "sentence"]
with open('full_names_priorities.csv', 'w', encoding='utf8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(final_csv)

fieldnames = ["plant", "CC", "bucket", "priority", "s2_url", "sentence"]
with open('full_names_priorities_with_weights.csv', 'w', encoding='utf8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(debug_csv)


print(f"unique plants: {len(set([l['plant'] for l in final_csv]))}")
print(f"unique plants (debug): {len(set([l['plant'] for l in debug_csv]))}")


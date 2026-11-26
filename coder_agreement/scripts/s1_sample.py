import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
# Blind sampler: reads only identifier columns (doi from TSV; id/pmcid/doi from JSON).
# Never reads the TSV 'code' or 'phrase_short' columns, nor JSON coding fields.
import csv, json, math, random, sys
W = WORK_ROOT + '/coder_agreement_inputs/'
OUT = WORK_ROOT + '/coder_agreement/'
SEED = 20261125
rows = list(csv.DictReader(open(W+'misdescription_list_private.tsv', encoding='utf-8'), delimiter='\t'))
listed = [r['doi'].strip().lower() for r in rows]
cand = json.load(open(W+'misdesc_candidates_private.json', encoding='utf-8'))
recs = [{'id': c.get('id'), 'pmcid': c.get('pmcid') or '', 'doi': (c.get('doi') or '').strip().lower()} for c in cand]
bydoi = {r['doi']: r for r in recs if r['doi']}
A = []  # stratum: on first coder's final list (membership only, code column unread)
for d in listed:
    A.append(bydoi.get(d, {'id': '', 'pmcid': '', 'doi': d}))
setA = set(listed)
B = [r for r in recs if r['doi'] not in setA]
rng = random.Random(SEED)
kA = max(1, math.ceil(0.3*len(A))); kB = math.ceil(0.3*len(B))
if kA + kB < 8: kB = 8 - kA
sA = rng.sample(A, kA); sB = rng.sample(B, kB)
s = sA + sB
rng.shuffle(s)  # hide stratum order
with open(OUT+'sample_ids_private.txt', 'w', encoding='utf-8') as f:
    f.write(f'# seed={SEED}; frame=73 screened candidates; strata by membership in first-coder list (code column not read); 30% ceil per stratum; order shuffled\n')
    f.write('idx\tpmcid\tdoi\n')
    for i, r in enumerate(s, 1):
        f.write(f"C{i:02d}\t{r['pmcid']}\t{r['doi']}\n")
print('frame', len(recs), 'listed', len(A), 'listed_matched_in_json', sum(1 for d in listed if d in bydoi), 'sample', len(s))

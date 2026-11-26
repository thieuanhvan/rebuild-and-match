import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import os, re, time, json, urllib.request, urllib.parse, sys
OUT = WORK_ROOT + '/coder_agreement/'
CACHE1 = WORK_ROOT + '/coder_agreement_inputs/ft_cache/'
CACHE2 = OUT + 'ft_cache_private/'
os.makedirs(CACHE2, exist_ok=True)
UA = {'User-Agent': 'research-script/1.0'}
def get(url):
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code in (429, 503): time.sleep(10*(k+1)); continue
            if e.code == 404: return None
            raise
        finally:
            time.sleep(1.2)
    return None
rows = [l.rstrip('\n').split('\t') for l in open(OUT+'sample_ids_private.txt', encoding='utf-8') if not l.startswith('#')][1:]
KW = re.compile(r'253[,\s.]?680|70[,\s.]?692|diabetes[_ ]binary|diabetes_012|diabetes health indicator|prediabet|pre-diabet|borderline|BRFSS|50[:/ -]50|balanced dataset|Diabetes_binary', re.I)
res = {}
for idx, pmcid, doi in rows:
    pm = pmcid
    if not pm:
        q = get('https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=lite&query=' + urllib.parse.quote(f'DOI:"{doi}"'))
        try:
            hits = json.loads(q)['resultList']['result']; pm = next((h.get('pmcid') for h in hits if h.get('pmcid')), '')
        except Exception: pm = ''
    xml = None
    for c in (CACHE1, CACHE2):
        p = c + pm + '.xml'
        if pm and os.path.exists(p): xml = open(p, encoding='utf-8', errors='replace').read(); break
    if xml is None and pm:
        xml = get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pm}/fullTextXML')
        if xml: open(CACHE2+pm+'.xml', 'w', encoding='utf-8').write(xml)
    if not xml:
        res[idx] = {'pmcid': pm, 'ft': False, 'sents': []}; print(idx, pm, 'NO FULL TEXT'); continue
    txt = re.sub(r'<[^>]+>', ' ', xml); txt = re.sub(r'\s+', ' ', txt)
    sents = re.split(r'(?<=[.;])\s+(?=[A-Z(])', txt)
    hit = [s[:400] for s in sents if KW.search(s)]
    res[idx] = {'pmcid': pm, 'ft': True, 'sents': hit}
    print(idx, pm, 'chars', len(txt), 'hits', len(hit))
json.dump(res, open(OUT+'extract_private.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

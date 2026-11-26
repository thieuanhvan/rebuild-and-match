import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import json, time, urllib.request, urllib.parse, re
OUT=WORK_ROOT + '/coder_agreement/'
UA={'User-Agent':'research-script/1.0'}
rows=[l.rstrip('\n').split('\t') for l in open(OUT+'sample_ids_private.txt',encoding='utf-8') if not l.startswith('#')][1:]
need={'C02','C05','C06','C11','C13','C15','C22'}
res={}
for idx,pm,doi in rows:
    if idx not in need: continue
    u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query='+urllib.parse.quote(f'DOI:"{doi}"')
    d={}
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90) as r: d=json.loads(r.read()); break
        except Exception as e:
            print('retry',idx,type(e).__name__); time.sleep(5*(k+1))
    time.sleep(1.2)
    h=(d.get('resultList',{}).get('result') or [{}])[0]
    ab=re.sub(r'<[^>]+>',' ',h.get('abstractText','') or '')
    res[idx]={'title':h.get('title'),'year':h.get('pubYear'),'oa':h.get('isOpenAccess'),'pmcid':h.get('pmcid'),'abstract':ab}
    kw=re.findall(r'(?i)[^.]*(?:BRFSS|253[, ]?680|70[, ]?692|health indicators|prediabet|kaggle)[^.]*\.',ab)
    print(idx,h.get('pubYear'),(h.get('title') or '')[:90],'| hits:',[k[:250] for k in kw])
json.dump(res,open(OUT+'abstracts_private.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)

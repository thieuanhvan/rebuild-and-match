import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import urllib.request, urllib.parse, time, json, re, xml.etree.ElementTree as ET
OUT=WORK_ROOT + '/coder_agreement/'
UA={'User-Agent':'research-script/1.0'}
NS={'a':'http://www.w3.org/2005/Atom','os':'http://a9.com/-/spec/opensearch/1.1/'}
Q=[('S1','all:BRFSS'),('S2','all:BRFSS AND all:heart'),('S3','all:heart AND all:disease AND all:Kaggle AND all:indicators'),
   ('S4','all:BRFSS AND all:diabetes'),('S5','all:"CDC" AND all:diabetes AND all:indicators AND all:Kaggle'),
   ('S6','ti:"heart disease" AND abs:BRFSS'),('S7','all:"behavioral risk factor surveillance system" AND all:heart')]
res={}
for qid,q in Q:
    url='http://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'start':0,'max_results':200})
    body=None
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=90) as r: body=r.read().decode('utf-8'); break
        except urllib.error.HTTPError as e:
            if e.code in (429,503): time.sleep(30*(k+1)); continue
            if e.code==403: print('403, stopping'); raise SystemExit
            raise
        except Exception as e:
            time.sleep(15*(k+1))
    time.sleep(3.5)
    if body is None: print(qid,'FAILED'); continue
    open(OUT+f'arxiv_raw/{qid}.xml','w',encoding='utf-8').write(body)
    root=ET.fromstring(body)
    tot=root.find('os:totalResults',NS).text
    ents=[{'id':e.find('a:id',NS).text.rsplit('/abs/',1)[-1],'title':re.sub(r'\s+',' ',e.find('a:title',NS).text),'abstract':re.sub(r'\s+',' ',e.find('a:summary',NS).text)} for e in root.findall('a:entry',NS) if e.find('a:title',NS) is not None]
    res[qid]={'query':q,'total':int(tot),'entries':ents}
    print(qid,'total',tot,'returned',len(ents))
json.dump(res,open(OUT+'arxiv_hits_sanity.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)

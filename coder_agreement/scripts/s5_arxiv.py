import os  # release: added
SURVEY_DATA_ROOT = os.environ.get('SURVEY_DATA_ROOT', '/path/to/SURVEY_DATA_ROOT')  # release: raw/published data root
WORK_ROOT = os.environ.get('WORK_ROOT', './work')  # release: intermediate files and outputs
import urllib.request, urllib.parse, time, json, re, xml.etree.ElementTree as ET
OUT=WORK_ROOT + '/coder_agreement/'
UA={'User-Agent':'research-script/1.0'}
NS={'a':'http://www.w3.org/2005/Atom','os':'http://a9.com/-/spec/opensearch/1.1/'}
Q=[('Q1','all:"Personal Key Indicators of Heart Disease"'),
   ('Q2a','all:"heart_2020_cleaned"'),('Q2b','all:"heart 2020 cleaned"'),
   ('Q3a','all:"heart_2022_no_nans"'),('Q3b','all:"heart 2022 no nans"'),
   ('Q4','all:"Key Indicators of Heart Disease" AND all:Kaggle'),
   ('Q4b','all:"Key Indicators of Heart Disease"'),
   ('Q5','all:BRFSS AND all:"heart disease" AND (all:Kaggle OR all:"survey weights" OR all:"data quality" OR all:label)'),
   ('Q6','all:HadHeartAttack'),('Q7','all:HadAngina'),
   ('Q8','all:"Diabetes Health Indicators" AND (all:prediabetes OR all:label OR all:"data quality" OR all:audit)'),
   ('Q8b','all:"Diabetes Health Indicators"')]
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
json.dump(res,open(OUT+'arxiv_hits.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)

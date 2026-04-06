import json, hashlib, time, os
LOG='audit.log'

def log(event):
    prev=''
    if os.path.exists(LOG): 
        prev=open(LOG).readlines()[-1]
    entry={'ts':time.time(),'event':event,'prev':prev}
    entry['hash']=hashlib.sha256(json.dumps(entry).encode()).hexdigest()
    open(LOG,'a').write(json.dumps(entry)+'\n')

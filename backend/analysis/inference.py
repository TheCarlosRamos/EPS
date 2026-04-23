# Engine de inferência de vínculos
from itertools import combinations

def infer(results):
    nodes=set()
    edges=[]
    for r in results:
        if 'value' in r:
            nodes.add(r['value'])
        elif 'title' in r:
            nodes.add(r['title'])
        elif 'profile' in r:
            nodes.add(r['profile'])
    
    for a,b in combinations(nodes,2):
        edges.append({'source':a,'target':b,'type':'coocorrencia'})
    return {'nodes':[{'id':n} for n in nodes],'edges':edges}

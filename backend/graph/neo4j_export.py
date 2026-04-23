from neo4j import GraphDatabase

uri='bolt://neo4j:7687'
auth=('neo4j','osint123')

def export(graph):
    driver=GraphDatabase.driver(uri,auth=auth)
    with driver.session() as s:
        for n in graph['nodes']:
            s.run('MERGE (n:Entidade {id:$id})',id=n['id'])
        for e in graph['edges']:
            s.run('MATCH (a:Entidade {id:$s}),(b:Entidade {id:$t}) MERGE (a)-[:RELACIONADO]->(b)',s=e['source'],t=e['target'])

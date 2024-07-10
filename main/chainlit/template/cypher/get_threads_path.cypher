MATCH (u:User) WHERE u.email=$identifier
MATCH path=(l:Step)-[:NEXT*23..100]->(o:Step)
WHERE (u)-[:START]->(l) AND (o)-[:NEXT]->(:Step {author:$identifier})
RETURN path LIMIT 200
MATCH (m:Step {message_id:$message_id})
MERGE (u:User {email:$email})
ON MATCH SET u.name=$name, u.phonenumber=$phonenumber
ON CREATE SET u.name=$name, u.phonenumber=$phonenumber, u.password="password", u.createdAt=date()
MERGE (u)-[:START]->(m)

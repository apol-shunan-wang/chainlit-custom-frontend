MATCH (m:Step {message_id: $last_message_id})
MATCH (n:Step {message_id: $new_message_id})
MERGE (m)-[r:NEXT]->(n)
ON CREATE SET r.user_session_id=$user_session_id
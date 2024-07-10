MERGE (s:Skill {skill_name: $skill_name})
WITH s
MATCH (msg_last:Step) WHERE msg_last.message_id=$last_message_id
MERGE (msg_last)-[:NEXT {
    createdAt:$createdAt,
    user_session_id:$user_session_id
}]->(:Step {
    message_id:$new_message_id,
    createdAt:$createdAt,
    role:$role,
    author:$author,
    topic:$topic,
    topics:$topics,
    qa_loop:$qa_loop,
    content:$content,
    ifAddToMessages:$ifAddToMessages
})-[:TOPIC]->(s)
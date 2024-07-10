MATCH (m:Message {message_id: $message_id})
MERGE (f:Feedback {
    for_message_id: $message_id,
    value: $value,
    nega_posi: $nega_posi,
    comment: $comment
})-[:UPSERT]->(m)
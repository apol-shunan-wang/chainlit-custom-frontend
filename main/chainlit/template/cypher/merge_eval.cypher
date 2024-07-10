MATCH (msg:Step) WHERE msg.message_id=$message_id
MERGE (:Evaluation {
    evaluation_id:$evaluation_id,
    evaluation_type:$evaluation_type,
    createdAt:$createdAt,
    author:$author,
    hopnumber:$hopnumber,
    instruction:$instruction,
    content:$content,
    score:$score,
    reason:$reason
})-[:EVAL {createdAt:$createdAt}]->(msg)
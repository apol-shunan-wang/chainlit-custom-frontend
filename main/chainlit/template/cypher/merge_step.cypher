MERGE (m:Step {message_id: $message_id})
ON CREATE SET
    m.createdAt=$createdAt,
    m.type=$type,
    m.name=$name,
    m.role=$role,
    m.author=$author,
    m.input=$input,
    m.output=$output,
    m.topic=$topic,
    m.topics=$topics,
    m.qa_loop=$qa_loop,
    m.ifAddToMessages=$ifAddToMessages
ON MATCH SET
    m.updatedAt=$createdAt,
    m.type=$type,
    m.name=$name,
    m.role=$role,
    m.author=$author,
    m.input=$input,
    m.output=$output,
    m.topic=$topic,
    m.topics=$topics,
    m.qa_loop=$qa_loop,
    m.ifAddToMessages=$ifAddToMessages
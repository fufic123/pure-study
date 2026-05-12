"""Anthropic tool schema definitions. Import these into agents."""

SEARCH_MATERIALS = {
    "name": "search_materials",
    "description": "Search MIT OpenCourseWare and Khan Academy for courses matching a query. Returns a list of courses with titles and descriptions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Subject or topic to search for"},
            "limit": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    },
}

FETCH_COURSE_TOPICS = {
    "name": "fetch_course_topics",
    "description": "Fetch the full topic tree for a specific course from a whitelisted source.",
    "input_schema": {
        "type": "object",
        "properties": {
            "source_id": {"type": "string", "enum": ["mit_ocw", "khan_academy"]},
            "course_id": {"type": "string"},
        },
        "required": ["source_id", "course_id"],
    },
}

CREATE_COURSE = {
    "name": "create_course",
    "description": "Create a course node in the user's knowledge graph.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "goal": {"type": "string"},
            "domain": {"type": "string"},
        },
        "required": ["name", "goal", "domain"],
    },
}

CREATE_TOPIC = {
    "name": "create_topic",
    "description": "Create a topic node in the user's knowledge graph.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "slug": {"type": "string", "description": "URL-safe identifier, e.g. 'atomic-structure'"},
            "domain": {"type": "string"},
            "description": {"type": "string"},
            "complexity": {"type": "integer", "minimum": 1, "maximum": 10},
            "status": {"type": "string", "enum": ["available", "locked"]},
        },
        "required": ["name", "slug", "domain", "description", "complexity", "status"],
    },
}

CREATE_EDGE = {
    "name": "create_edge",
    "description": "Create a directed relationship between two nodes in the knowledge graph.",
    "input_schema": {
        "type": "object",
        "properties": {
            "from_id": {"type": "string"},
            "to_id": {"type": "string"},
            "edge_type": {
                "type": "string",
                "enum": ["CONTAINS", "SUBTOPIC_OF", "REQUIRES", "RELATED_TO", "EQUIVALENT_TO"],
            },
        },
        "required": ["from_id", "to_id", "edge_type"],
    },
}

GET_TOPIC = {
    "name": "get_topic",
    "description": "Read the current state of a topic node from the knowledge graph.",
    "input_schema": {
        "type": "object",
        "properties": {
            "topic_id": {"type": "string"},
        },
        "required": ["topic_id"],
    },
}

GET_AVAILABLE_TOPICS = {
    "name": "get_available_topics",
    "description": "List all topics the user can currently study (status=available or in_progress).",
    "input_schema": {"type": "object", "properties": {}},
}

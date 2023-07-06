UPDATE_DEPLOYMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "deployment_id": {"type": "string", "minLength": 1},
        "service_id": {"type": "string", "minLength": 1},
        "plan_id": {"type": "string", "minLength": 1},
        "context": {
            "type": "object",
            "properties": {
                "component_context": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z0-9_-]+$": {
                            "type": "object",
                            "properties": {
                                "update_deployment": {"type": "boolean"},
                                "component": {
                                    "type": "object",
                                    "properties": {
                                        "executables": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "id": {"type": "string", "minLength": 1},
                                                    "name": {"type": "string", "minLength": 1}
                                                },
                                                "required": ["id", "name", "docker"]
                                            }
                                        }
                                    },
                                    "required": ["executables"]
                                }
                            },
                            "required": ["update_deployment", "component"]
                        }
                    }
                }
            },
            "required": ["component_context"]
        }
    },
    "required": ["deployment_id", "service_id", "plan_id", "context"]
}

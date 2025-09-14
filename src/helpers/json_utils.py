def parse_json(json_string: str) -> dict:
    import json
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON string") from e

def validate_json(data: dict, schema: dict) -> bool:
    from jsonschema import validate, ValidationError
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False

def json_to_string(data: dict) -> str:
    import json
    return json.dumps(data, indent=4)
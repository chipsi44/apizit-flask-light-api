from time import sleep

from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)
SLOW_RESPONSE_SECONDS = 80


@api.get("/health")
def health():
    return jsonify(status="ok")


@api.get("/info")
def info():
    return jsonify(framework="flask", profile="light")


@api.post("/echo")
def echo():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="The request body must be a JSON object."), 400

    message = payload.get("message")
    count = payload.get("count")
    if not isinstance(message, str) or not message:
        return jsonify(error="'message' must be a non-empty string."), 400
    if not isinstance(count, int) or isinstance(count, bool):
        return jsonify(error="'count' must be an integer."), 400

    return jsonify(received={"message": message, "count": count})


@api.get("/items/<int:item_id>")
def item(item_id: int):
    if item_id < 1:
        return jsonify(error="'item_id' must be a positive integer."), 400

    raw_include_details = request.args.get("include_details", "false").lower()
    if raw_include_details not in {"true", "false"}:
        return jsonify(error="'include_details' must be true or false."), 400

    include_details = raw_include_details == "true"
    response = {"item_id": item_id, "include_details": include_details}
    if include_details:
        response["details"] = f"Reference item {item_id}"
    return jsonify(response)


@api.get("/slow")
def slow():
    sleep(SLOW_RESPONSE_SECONDS)
    return jsonify(delay_seconds=SLOW_RESPONSE_SECONDS, status="completed")

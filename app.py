from flask import Flask, render_template, request, jsonify
from copy import deepcopy
from roster_2025 import roster_data

app = Flask(__name__)

# Initialize scores if not present
for p in roster_data:
    if "score" not in p:
        p["score"] = 0

# Initialize button counters
green_clicks = 0
red_clicks = 0

history = []

on_court = deepcopy(roster_data[:6])

@app.route("/")
def index():
    return render_template(
        "index.html",
        roster=roster_data,
        on_court=on_court,
        green_clicks=green_clicks,
        red_clicks=red_clicks
    )

@app.route("/rotate", methods=["POST"])
def rotate():
    global on_court
    if len(on_court) == 6:
        indices = [0,1,2,5,4,3]
        rotated = [on_court[i] for i in indices[-1:] + indices[:-1]]
        new_order = [None]*6
        for orig_idx, new_player in zip(indices, rotated):
            new_order[orig_idx] = new_player
        on_court = new_order
    return jsonify({"on_court": on_court, "roster": roster_data})

@app.route("/make_sub", methods=["POST"])
def make_sub():
    global on_court
    data = request.get_json()
    out_name = data.get("sub_out")
    in_name = data.get("sub_in")
    out_index = next((i for i,p in enumerate(on_court) if p["name"]==out_name), None)
    in_player = next((p for p in roster_data if p["name"]==in_name), None)
    if out_index is not None and in_player:
        on_court[out_index] = in_player
    return jsonify({"on_court": on_court, "roster": roster_data})

@app.route("/update_points", methods=["POST"])
def update_points():
    global green_clicks, red_clicks, history
    data = request.get_json()
    delta = data.get("delta", 0)
    players = data.get("players", [])

    # Update counters
    if delta == 1:
        green_clicks += 1
    elif delta == -1:
        red_clicks += 1

    # Apply points
    for p in roster_data:
        if p["name"] in players:
            p["score"] += delta

    # Save this action to history
    history.append({
        "delta": delta,
        "players": players
    })

    return jsonify({
        "roster": roster_data,
        "green_clicks": green_clicks,
        "red_clicks": red_clicks
    })

@app.route("/update_court", methods=["POST"])
def update_court():
    global on_court
    data = request.get_json()
    if isinstance(data, list):
        new_order = []
        for name in data:
            player = next((p for p in roster_data if p["name"]==name), None)
            if player:
                new_order.append(player)
        if len(new_order) == len(on_court):
            on_court = new_order
    return ("", 204)

@app.route("/new_set", methods=["POST"])
def new_set():
    global green_clicks, red_clicks
    green_clicks = 0
    red_clicks = 0
    return jsonify({
        "green_clicks": green_clicks,
        "red_clicks": red_clicks,
        "roster": roster_data  # scores remain unchanged
    })

@app.route("/new_match", methods=["POST"])
def new_match():
    global green_clicks, red_clicks
    green_clicks = 0
    red_clicks = 0
    for p in roster_data:
        p["score"] = 0
    return jsonify({
        "green_clicks": green_clicks,
        "red_clicks": red_clicks,
        "roster": roster_data
    })

@app.route("/undo", methods=["POST"])
def undo():
    global green_clicks, red_clicks, history
    if not history:
        return jsonify({"message":"Nothing to undo"}), 400

    last_action = history.pop()
    delta = last_action["delta"]
    players = last_action["players"]

    # Reverse points
    reverse_delta = -delta
    if delta == 1:
        green_clicks -= 1
    elif delta == -1:
        red_clicks -= 1

    for p in roster_data:
        if p["name"] in players:
            p["score"] += reverse_delta

    return jsonify({
        "roster": roster_data,
        "green_clicks": green_clicks,
        "red_clicks": red_clicks
    })

if __name__ == "__main__":
    app.run(debug=True)

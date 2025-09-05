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
    global green_clicks, red_clicks
    data = request.get_json()
    delta = data.get("delta", 0)
    players = data.get("players", [])

    if delta == 1:
        green_clicks += 1
    elif delta == -1:
        red_clicks += 1

    for p in roster_data:
        if p["name"] in players:
            p["score"] += delta
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

if __name__ == "__main__":
    app.run(debug=True)

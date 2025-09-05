from flask import Flask, render_template, request, jsonify
from copy import deepcopy
from roster_2025 import roster_data

app = Flask(__name__)

# Initialize scores if not present
for p in roster_data:
    if "score" not in p:
        p["score"] = 0

on_court = deepcopy(roster_data[:6])

@app.route("/", methods=["GET", "POST"])
def index():
    global on_court
    if request.method == "POST":
        # Clockwise rotation for 2x3 grid
        if "rotate" in request.form and len(on_court) == 6:
            indices = [0,1,2,5,4,3]
            rotated = [on_court[i] for i in indices[-1:] + indices[:-1]]
            new_order = [None]*6
            for orig_idx, new_player in zip(indices, rotated):
                new_order[orig_idx] = new_player
            on_court = new_order

        # Substitution
        elif "sub_out" in request.form and "sub_in" in request.form:
            out_name = request.form["sub_out"]
            in_name = request.form["sub_in"]
            out_index = next((i for i, p in enumerate(on_court) if p["name"] == out_name), None)
            in_player = next((p for p in roster_data if p["name"] == in_name), None)
            if out_index is not None and in_player:
                on_court[out_index] = in_player

    return render_template("index.html", roster=roster_data, on_court=on_court)

@app.route("/update_court", methods=["POST"])
def update_court():
    global on_court
    data = request.get_json()
    if isinstance(data, list):
        new_order = []
        for name in data:
            player = next((p for p in roster_data if p["name"] == name), None)
            if player:
                new_order.append(player)
        if len(new_order) == len(on_court):
            on_court = new_order
    return ("", 204)

@app.route("/update_points", methods=["POST"])
def update_points():
    global on_court, roster_data
    data = request.get_json()
    delta = data.get("delta")
    players = data.get("players", [])
    result = {}
    for p in roster_data:
        if p["name"] in players:
            p["score"] += delta
            result[p["name"]] = p["score"]
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

# from flask import Flask, render_template, request
#
# app = Flask(__name__)
#
# @app.route("/")
# def home():
#     return "<h1>Hello, Coach!</h1><p>This is our app.</p>"
#
# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ----- DATA -----
# Sample roster, you can start empty or prefill
roster = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hank"]
on_court = roster[:6]  # first 6 players
scores = {p: 0 for p in roster}

# ----- ROUTES -----
@app.route("/", methods=["GET", "POST"])
def index():
    global roster, on_court, scores
    message = ""

    if request.method == "POST":
        # Add point to all on court
        if "plus1" in request.form:
            for p in on_court:
                scores[p] += 1
        elif "minus1" in request.form:
            for p in on_court:
                scores[p] -= 1
        elif "add_player" in request.form:
            name = request.form.get("player_name").strip()
            if name and name not in roster:
                roster.append(name)
                scores[name] = 0
                message = f"{name} added to roster."
        elif "sub_out" in request.form:
            out_p = request.form.get("sub_out")
            in_p = request.form.get("sub_in")
            if out_p in on_court and in_p in roster and in_p not in on_court:
                idx = on_court.index(out_p)
                on_court[idx] = in_p
        elif "rotate" in request.form:
            # Rotate clockwise: 0->5, 5->4, 4->3, 3->2, 2->1, 1->0
            on_court[:] = [on_court[-1]] + on_court[:-1]

        return redirect(url_for("index"))

    # Prepare substitution options
    sub_out_options = on_court
    sub_in_options = [p for p in roster if p not in on_court]

    return render_template(
        "index.html",
        roster=roster,
        on_court=on_court,
        scores=scores,
        sub_out_options=sub_out_options,
        sub_in_options=sub_in_options,
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)

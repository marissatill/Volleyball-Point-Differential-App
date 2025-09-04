from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello, Coach!</h1><p>This is our app.</p>"

if __name__ == "__main__":
    app.run(debug=True)

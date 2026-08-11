from flask import Flask, render_template
from routes.auth import auth

app = Flask(__name__)

app.register_blueprint(auth)

@app.route("/")
def home():
    return render_template("home/index.html")

if __name__ == "__main__":
    app.run(debug=True)
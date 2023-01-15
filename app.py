from flask import Flask, render_template
from inventory.inventory import inventory_blueprint

app = Flask(__name__)

# registering blueprints
app.register_blueprint(inventory_blueprint)


@app.route("/")
def index():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)

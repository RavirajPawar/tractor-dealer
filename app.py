from flask import Flask, render_template
from inventory.inventory import inventory_blueprint
from connector import mongo_conn

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/tractor_dealer?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
mongo_conn.init_app(app)


# registering blueprints
app.register_blueprint(inventory_blueprint)


@app.route("/")
def index():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)

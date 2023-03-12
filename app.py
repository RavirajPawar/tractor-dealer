from flask import Flask, render_template
from inventory.inventory import inventory_blueprint
from orders.orders import orders_blueprint
from connector import mongo_conn
from constants import UPLOAD_FOLDER

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/tractor_dealer?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "Imr@nRih@nReh@n202301"
mongo_conn.init_app(app)


# registering blueprints
app.register_blueprint(inventory_blueprint)
app.register_blueprint(orders_blueprint)


@app.route("/")
def index():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)

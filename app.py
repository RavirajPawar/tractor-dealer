from flask import Flask, render_template

from common.connector import mongo_conn
from config.config import DevConfig
from inventory.inventory import inventory_blueprint
from orders.orders import orders_blueprint
from common.utils import setup_app
from logger import logger

app = Flask(__name__)
app.config.from_object(DevConfig)
mongo_conn.init_app(app)

try:
    setup_app()
except:
    logger.exception("app setup failed", exc_info=True)
    raise

# registering blueprints
app.register_blueprint(inventory_blueprint)
app.register_blueprint(orders_blueprint)


@app.route("/")
def index():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)

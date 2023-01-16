from flask import Blueprint, render_template, request, session, redirect
from connector import mongo_conn

inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)


@inventory_blueprint.route("/inventory", methods=["get", "post"])
def render_inventory():
    tractor_details = dict(request.form)
    print(tractor_details)
    mongo_conn.db.stock_tractor.insert_one(tractor_details)
    return render_template("inventory.html")

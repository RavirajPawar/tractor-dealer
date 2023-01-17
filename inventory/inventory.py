from flask import Blueprint, render_template, request, session, redirect
from werkzeug.utils import secure_filename
from connector import mongo_conn
import os

inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)


@inventory_blueprint.route("/inventory", methods=["get", "post"])
def render_inventory():
    if request.method == "POST":
        tractor_details = dict(request.form)
        mongo_conn.db.stock_tractor.insert_one(tractor_details)
        for file in request.files.getlist("file"):
            filename = secure_filename(file.filename)
            # os.makedirs(f'/data/{tractor_details.get("chassis-number")}')
            file.save(
                os.path.join(f"data",  filename)
            )

    return render_template("inventory.html")

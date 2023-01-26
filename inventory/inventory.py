from flask import Blueprint, render_template, request, session, redirect
from werkzeug.utils import secure_filename
from connector import mongo_conn
import os
from inventory.helper import create_folder, lowercase_data
from logger import logger

inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)


@inventory_blueprint.route("/add-tractor", methods=["GET", "POST"])
def add_tractor():
    if request.method == "POST":
        tractor_details = dict(request.form)
        mongo_conn.db.stock_tractor.insert_one(lowercase_data(tractor_details))
        chassis_number = tractor_details.get("chassis-number")
        create_folder(chassis_number)
        for file in request.files.getlist("pictures"):
            filename = secure_filename(file.filename)
            file.save(
                os.path.join(
                    f"data", tractor_details.get("chassis-number"), "before", filename
                )
            )
    return render_template("add_tractor.html")


@inventory_blueprint.route("/view-tractor", methods=["GET", "POST"])
@inventory_blueprint.route("/view-tractor/<string:tractor>/", methods=["GET", "POST"])
def view_tractor(tractor=None, display_tractor=dict()):
    if request.method == "GET":
        result = mongo_conn.db.stock_tractor.find({}, {"_id": 0})
        all_tractor = list()
        for item in result:
            all_tractor.append(dict(item))
            if not tractor:
                display_tractor = all_tractor[-1]
                tractor = True
            elif item["chassis-number"] == tractor:
                display_tractor = all_tractor[-1]

        return render_template(
            "view_inventory.html",
            all_tractor=all_tractor,
            display_tractor=display_tractor,
        )

    elif request.method == "POST":
        update_tractor = {"$set": dict(request.form)}
        tractor = (
            update_tractor.get("$set").get("chassis-number") if not tractor else tractor
        )
        mongo_conn.db.stock_tractor.update_one(
            {"chassis-number": tractor}, update_tractor
        )
        for file in request.files.getlist("pictures"):
            filename = secure_filename(file.filename)
            file.save(os.path.join(f"data", tractor, "before", filename))
        return redirect("/view-tractor")

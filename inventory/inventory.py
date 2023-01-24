from flask import Blueprint, render_template, request, session, redirect
from werkzeug.utils import secure_filename
from connector import mongo_conn
import os
from inventory.helper import create_folder, lowercase_data
from logger import logger

inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)


@inventory_blueprint.route("/add-tractor", methods=["get", "post"])
def add_tractor():
    if request.method == "POST":
        tractor_details = dict(request.form)
        mongo_conn.db.stock_tractor.insert_one(lowercase_data(tractor_details))
        chassis_number = tractor_details.get("chassis-number")
        create_folder(chassis_number)
        for file in request.files.getlist("file"):
            filename = secure_filename(file.filename)
            file.save(
                os.path.join(f"data", tractor_details.get("chassis-number"), filename)
            )

    return render_template("add_tractor.html")


def xyz():
    if request.method == "GET":
        result = mongo_conn.db.stock_tractor.find({})

        req_keys = [
            "tractor-name",
            "model",
            "year-of-manufacturing",
        ]
        display_tractor = list()
        for document in result:
            temp = dict()
            for req in req_keys:
                temp[req] = document.get(req)
            display_tractor.append(temp)

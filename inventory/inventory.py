from flask import Blueprint, render_template, request, session, redirect
from werkzeug.utils import secure_filename
from connector import mongo_conn
import os
from inventory.helper import create_folder
from logger import logger

inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)


@inventory_blueprint.route("/inventory", methods=["get", "post"])
def render_inventory():
    if request.method == "POST":
        tractor_details = dict(request.form)
        mongo_conn.db.stock_tractor.insert_one(tractor_details)
        chassis_number = tractor_details.get("chassis-number")
        create_folder(chassis_number)
        for file in request.files.getlist("file"):
            filename = secure_filename(file.filename)
            file.save(
                os.path.join(f"data", tractor_details.get("chassis-number"), filename)
            )
    elif request.method == "GET":
        result = mongo_conn.db.stock_tractor.find({})
        # ignore_keys = [
        #     "_id",
        #     "tractor-name",
        #     "chassis-number",
        #     "model",
        #     "year-of-manufacturing",
        #     "registration-number",
        #     "engine-number",
        #     "hp-hours",
        #     "bank",
        #     "original-owner",
        #     "release-date-time",
        #     "delievery-date-time",
        #     "dealer",
        #     "godown-name",
        # ]

        req_keys = [
            "tractor-name",
            "model",
            "year-of-manufacturing",
        ]
        display_tractor = list()
        for document in result:
            temp = dict()
            for req in req_keys:
                temp[req] = document[req]
            display_tractor.append(temp)

    return render_template("inventory.html", display_tractor=display_tractor)

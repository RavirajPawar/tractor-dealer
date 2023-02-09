from flask import Blueprint, render_template, request, session, redirect
from werkzeug.utils import secure_filename
from connector import mongo_conn
import os
from inventory.helper import create_folder, lowercase_data
from logger import logger

orders_blueprint = Blueprint(
    "orders", __name__, template_folder="templates", static_folder="static"
)


@orders_blueprint.route("/sell-tractor", methods=["GET"])
@orders_blueprint.route("/sell-tractor/<string:tractor>/", methods=["GET"])
def sell_tractor(tractor=None, display_tractor=dict()):
    if tractor:
        result = mongo_conn.db.stock_tractor.find_one(
            {"chassis-number": tractor}, {"_id": 0, "old-chassis-number": 0}
        )
        customer_details = {
            "buyer name": "text",
            "address": "text",
            "contact": "text",
            "wintness": "text",
            "witness contact": "text",
            "aadhar card": "file",
            "pan card": "file",
            "7/12": "file",
            "PUC": "file",
            "RC": "file",
            "insurance": "file",
            "NOC delivery": "file",
            "Sell photo": "file",
        }
        keys = list(zip(result.keys(), customer_details.keys()))
        return render_template(
            "cart_tractor.html",
            tractor=tractor,
            result=result,
            customer_details=customer_details,
            keys= keys
        )

    if not tractor:
        logger.info("started processing sell-tractor".center(80, "^"))
        result = mongo_conn.db.stock_tractor.find({}, {"_id": 0})
        all_tractor = list()
        for item in result:
            all_tractor.append(dict(item))
            if not tractor:
                display_tractor = all_tractor[-1]
                tractor = True
            elif item["chassis-number"] == tractor:
                display_tractor = all_tractor[-1]
        logger.info("Finished processing sell-tractor".center(80, "^"))
        return render_template(
            "sell_tractor.html",
            all_tractor=all_tractor,
            display_tractor=display_tractor,
        )

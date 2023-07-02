import os

from flask import Blueprint, redirect, render_template, request, session
from werkzeug.utils import secure_filename

from common.connector import mongo_conn
from common.constants import upload_folder, after_sell
from inventory.helper import create_folder, lowercase_data
from logger import logger

orders_blueprint = Blueprint(
    "orders", __name__, template_folder="templates", static_folder="static"
)


@orders_blueprint.route("/sell-tractor", methods=["GET"])
@orders_blueprint.route("/sell-tractor/<string:tractor>/", methods=["GET"])
def sell_tractor(tractor=None):
    if tractor:
        result = mongo_conn.db.stock_tractor.find_one(
            {"chassis-number": tractor},
            {"_id": 0, "old-chassis-number": 0, "is-sold": 0},
        )
        if not result:  # if result not found
            result = dict()

        customer_details = {
            "buyer-name": "text",
            "address": "text",
            "contact": "text",
            "wintness": "text",
            "witness-contact": "text",
            "aadhar-card": "file",
            "pan-card": "file",
            "7-12": "file",
            "PUC": "file",
            "RC": "file",
            "insurance": "file",
            "NOC-delivery": "file",
            "Sell-photo": "file",
        }
        keys = list(zip(result.keys(), customer_details.keys()))
        return render_template(
            "cart_tractor.html",
            tractor=tractor,
            result=result,
            customer_details=customer_details,
            keys=keys,
        )

    if not tractor:
        logger.info("started processing sell-tractor".center(80, "^"))
        result = mongo_conn.db.stock_tractor.find({"is-sold": "false"}, {"_id": 0})
        all_tractor = [item for item in result]
        logger.info("Finished processing sell-tractor".center(80, "^"))
        return render_template(
            "sell_tractor.html",
            all_tractor=all_tractor,
        )


@orders_blueprint.route("/final-sell", methods=["POST"])
def final_sell():
    chassis_number = request.form.get("chassis-number")
    buyer_name = request.form.get("buyer-name", "default")
    update_tractor = {"$set": lowercase_data(dict(request.form))}
    for field in request.files.keys():
        for file in request.files.getlist(field):
            if secure_filename(file.filename):
                file.save(
                    os.path.join(
                        upload_folder,
                        chassis_number,
                        after_sell,
                        "-".join([buyer_name, field, secure_filename(file.filename)]),
                    )
                )
                logger.info(f"updated at {file.filename}\t-> {chassis_number}")

    logger.info(f"started updating tractor {chassis_number} in DB")
    mongo_conn.db.stock_tractor.update_one(
        {"chassis-number": chassis_number}, update_tractor
    )
    logger.info(f"finished updating tractor {chassis_number} in DB")
    return redirect("/sell-tractor")


@orders_blueprint.route("/sold-tractor", methods=["GET", "POST"])
def sold_tractor():
    result = mongo_conn.db.stock_tractor.find(
        {"is-sold": "true"}, {"_id": 0, "is-sold": 0}
    )
    sold_tractor = [item for item in result]
    return render_template("sold_tractor.html", sold_tractor=sold_tractor)

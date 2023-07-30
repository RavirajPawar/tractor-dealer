import os

from flask import Blueprint, redirect, render_template, request, flash
from werkzeug.utils import secure_filename

from common.connector import mongo_conn
from common.constants import (
    after_sell,
    before_sell,
    buy_document_field,
    file_connector,
    godown_list,
    sell_document_field,
    upload_folder,
)
from common.utils import calculate_time
from inventory.helper import lowercase_data
from logger import logger

orders_blueprint = Blueprint(
    "orders", __name__, template_folder="templates", static_folder="static"
)


@orders_blueprint.route("/sell-tractor", methods=["GET"])
@orders_blueprint.route("/sell-tractor/<string:tractor>/", methods=["GET"])
@calculate_time
def sell_tractor(tractor=None):
    logger.info(f"given chassis-number {tractor if tractor else 'NONE'}")
    if tractor:
        result = mongo_conn.db.stock_tractor.find_one(
            {"chassis-number": tractor},
            {"_id": 0, "old-chassis-number": 0, "is-sold": 0},
        )
        if not result:  # if result not found
            flash(f"wrong chassis number {tractor} is passed")
            logger.info("no record found in DB. redirecting to /sell-tractor")
            return redirect("/sell-tractor")
        path = os.path.join(upload_folder, tractor, before_sell)
        files = [file for file in os.listdir(path)]
        for doc in buy_document_field:
            result[doc] = ""
            for file in files:
                if file.startswith(doc):
                    result[doc] += file
                    result[doc] += file_connector
        customer_details = {
            "buyer-name": "text",
            "address": "text",
            "contact": "text",
            "wintness": "text",
            "witness-contact": "text",
            "real-selling-price": "text",
            "advance": "text",
            "pending-amount": "text",
            "agent-name": "text",
            "sell-time-custom-note": "text",
        }
        for sell_doc_type in sell_document_field:
            customer_details[sell_doc_type] = "file"

        return render_template(
            "cart_tractor.html",
            tractor=tractor,
            result=result,
            customer_details=customer_details,
            document_field=buy_document_field,
            godown_list=godown_list,
        )

    if not tractor:
        result = mongo_conn.db.stock_tractor.find({"is-sold": "false"}, {"_id": 0})
        all_tractor = [item for item in result]
        logger.info(f"got list of total unsold tractors {len(all_tractor)}")
        return render_template(
            "sell_tractor.html",
            all_tractor=all_tractor,
        )


@orders_blueprint.route("/final-sell", methods=["POST"])
@calculate_time
def final_sell():
    chassis_number = request.form.get("chassis-number")
    update_tractor = {"$set": lowercase_data(dict(request.form))}
    logger.info(f"starting storing files for {chassis_number}")
    for field in request.files.keys():
        for file in request.files.getlist(field):
            if secure_filename(file.filename):
                new_filename = os.path.join(
                    upload_folder,
                    chassis_number,
                    after_sell,
                    "-".join([field, secure_filename(file.filename)]),
                )
                file.save(new_filename)
                logger.info(f"saving at {file.filename}\t-> {new_filename}")
    logger.info(f"finished storing files for {chassis_number}")
    logger.info(f"started final-sell update for chasssis_number {chassis_number} in DB")
    mongo_conn.db.stock_tractor.update_one(
        {"chassis-number": chassis_number}, update_tractor
    )
    logger.info(
        f"finished final-sell update for chasssis_number {chassis_number} in DB"
    )
    return redirect("/sell-tractor")


@orders_blueprint.route("/sold-tractor", methods=["GET", "POST"])
@calculate_time
def sold_tractor():
    result = mongo_conn.db.stock_tractor.find(
        {"is-sold": "true"},
        {
            "tractor-name": 1,
            "model": 1,
            "chassis-number": 1,
            "selling-godown": 1,
            "buyer-name": 1,
            "contact": 1,
            "_id": 0,
        },
    )
    sold_tractor = [item for item in result]
    logger.info(f"got list of total sold tractors {len(sold_tractor)}")
    return render_template("sold_tractor.html", sold_tractor=sold_tractor)


@orders_blueprint.route(
    "/update-sold-tractor/<string:tractor>/", methods=["GET", "POST"]
)
@orders_blueprint.route("/update-sold-tractor", methods=["GET", "POST"])
@calculate_time
def update_sold_tractor(tractor=None):
    if not tractor:
        flash("please select tractor from here")
        logger.info(f"redirecting to /sold-tractor")
        return redirect("/sold-tractor")
    if request.method == "GET":
        update_sold_tractor = mongo_conn.db.stock_tractor.find_one(
            {"chassis-number": tractor},
            {
                "_id": 0,
                "real-selling-price": 1,
                "advance": 1,
                "pending-amount": 1,
                "chassis-number": 1,
            },
        )
        if not update_sold_tractor:  # if result not found
            flash(f"wrong chassis number {tractor} is passed")
            logger.info("no record found in DB. redirecting to /sold-tractor")
            return redirect("/sold-tractor")

        path = os.path.join(upload_folder, tractor, before_sell)
        before_sell_doc_report = dict()
        files = [file for file in os.listdir(path)]
        for doc in buy_document_field:
            before_sell_doc_report[doc] = list()
            for file in files:
                if file.startswith(doc):
                    before_sell_doc_report[doc].append(file)

        path = os.path.join(upload_folder, tractor, after_sell)
        after_sell_doc_report = dict()
        files = [file for file in os.listdir(path)]
        for doc in sell_document_field:
            after_sell_doc_report[doc] = list()
            for file in files:
                if file.startswith(doc):
                    after_sell_doc_report[doc].append(file)
        return render_template(
            "update_sold_tractor.html",
            update_sold_tractor=update_sold_tractor,
            before_sell_doc_report=before_sell_doc_report,
            after_sell_doc_report=after_sell_doc_report,
        )
    elif request.method == "POST":
        update_tractor = {"$set": lowercase_data(dict(request.form))}
        logger.info(f"started storing files for {tractor}")
        for doc_field in buy_document_field:
            for file in request.files.getlist(doc_field):
                if secure_filename(file.filename):
                    file_path = os.path.join(
                        upload_folder,
                        tractor,
                        before_sell,
                        "-".join([doc_field, secure_filename(file.filename)]),
                    )
                    file.save(file_path)
                    logger.info(f"storing at {file.filename}->{file_path}")
        for doc_field in sell_document_field:
            for file in request.files.getlist(doc_field):
                if secure_filename(file.filename):
                    file_path = os.path.join(
                        upload_folder,
                        tractor,
                        after_sell,
                        "-".join([doc_field, secure_filename(file.filename)]),
                    )
                    file.save(file_path)
                    logger.info(f"storing at {file.filename}->{file_path}")
        logger.info(f"started updating sold tractor {tractor} in DB")
        mongo_conn.db.stock_tractor.update_one(
            {"chassis-number": tractor}, update_tractor
        )
        logger.info(f"finished updating sold tractor {tractor} in DB")
        return redirect(f"/update-sold-tractor/{tractor}/")

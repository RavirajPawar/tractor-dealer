from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_file,
)
from werkzeug.utils import secure_filename
from connector import mongo_conn
import os
from inventory.helper import create_folder, lowercase_data
from logger import logger
from io import BytesIO
from glob import glob
import zipfile


inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)


@inventory_blueprint.route("/add-tractor", methods=["GET", "POST"])
def add_tractor():
    if request.method == "POST":
        logger.info("started processing add-tractor".center(80, "^"))
        tractor_details = lowercase_data(dict(request.form))
        chassis_number = tractor_details.get("chassis-number")
        if chassis_number in os.listdir(".data"):
            logger.warning(
                f"redirecting to add-tractor cause {chassis_number} folder already exists"
            )
            flash(f"chassis number {chassis_number} already exists")
            return redirect(url_for("inventory.add_tractor"))
        create_folder(chassis_number)
        mongo_conn.db.stock_tractor.insert_one(tractor_details)

        for file in request.files.getlist("pictures"):
            if secure_filename(file.filename):
                file.save(
                    os.path.join(
                        ".data",
                        tractor_details.get("chassis-number"),
                        "before",
                        secure_filename(file.filename),
                    )
                )
                logger.info(f"{file.filename}->{tractor_details.get('chassis-number')}")
    logger.info("finished processing add-tractor".center(80, "^"))
    return render_template("add_tractor.html")


@inventory_blueprint.route("/view-tractor", methods=["GET", "POST"])
@inventory_blueprint.route("/view-tractor/<string:tractor>/", methods=["GET", "POST"])
def view_tractor(tractor=None, display_tractor=dict()):
    if request.method == "GET":
        logger.info("started processing view-tractor".center(80, "^"))
        result = mongo_conn.db.stock_tractor.find({}, {"_id": 0})
        all_tractor = list()
        for item in result:
            all_tractor.append(dict(item))
            if not tractor:
                display_tractor = all_tractor[-1]
                tractor = True
            elif item["chassis-number"] == tractor:
                display_tractor = all_tractor[-1]
        logger.info("Finished processing view-tractor".center(80, "^"))
        return render_template(
            "view_inventory.html",
            all_tractor=all_tractor,
            display_tractor=display_tractor,
        )

    elif request.method == "POST":
        if not dict(request.form):  #
            return redirect("/view-tractor")

        update_tractor = {"$set": lowercase_data(dict(request.form))}
        old_chassis_number = update_tractor.get("$set").get("old-chassis-number")
        chassis_number = update_tractor.get("$set").get("chassis-number")
        tractor = old_chassis_number if not tractor else tractor

        if old_chassis_number != chassis_number:
            if os.path.exists(os.path.join(".data", chassis_number)):
                flash(
                    f"Denied updating chassis number from {old_chassis_number} to {chassis_number}."
                )
                return redirect(url_for("inventory.view_tractor"))
            logger.info(f"renaming tractor {old_chassis_number} folder name")
            os.rename(
                os.path.join(".data", old_chassis_number),
                os.path.join(".data", chassis_number),
            )
            logger.info(f"renamed tractor {chassis_number} folder name")

        logger.info(f"started updating tractor {old_chassis_number} in DB")
        mongo_conn.db.stock_tractor.update_one(
            {"chassis-number": tractor}, update_tractor
        )
        logger.info(f"finished updating tractor {chassis_number} in DB")

        for file in request.files.getlist("pictures"):
            if secure_filename(file.filename):
                file.save(
                    os.path.join(
                        ".data",
                        chassis_number,
                        "before",
                        secure_filename(file.filename),
                    )
                )
                logger.info(f"updated at {file.filename}->{chassis_number}")

        return redirect("/view-tractor")


@inventory_blueprint.route("/download-zip/<string:tractor>/", methods=["GET"])
def download_zip(tractor=None):
    try:
        logger.info(f"started download-zip api for {tractor}")
        zipf = zipfile.ZipFile(
            os.path.join(".data", tractor, f"{tractor}-photos.zip"),
            "w",
            zipfile.ZIP_DEFLATED,
        )
        for file in os.listdir(os.path.join(".data", tractor, "before")):
            zipf.write(os.path.join(".data", tractor, "before", file), file)
        zipf.close()
        logger.info(
            f'created zip file at {os.path.join(".data", tractor, f"{tractor}-photos.zip")}'
        )
        return send_file(
            os.path.join(".data", tractor, f"{tractor}-photos.zip"),
            mimetype="zip",
            download_name=f"{tractor}-photos.zip",
            as_attachment=True,
        )

    except Exception as e:
        logger.exception(str(e), exc_info=True)
        return str(e)

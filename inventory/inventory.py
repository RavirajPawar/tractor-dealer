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
from constants import UPLOAD_FOLDER
import os
from inventory.helper import create_folder, lowercase_data
from logger import logger
import zipfile


inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)


@inventory_blueprint.route("/add-tractor", methods=["GET", "POST"])
def add_tractor():
    """
    * checks `chassis_number` folder is not exists in `.data` folder.
    * if not creates folder under `.data` and `inserts` data to mongo db.
    * saves all files in newly created `before` subfolder unders `chassis-number`.
    """
    if request.method == "POST":
        try:
            logger.info("started processing add-tractor".center(80, "^"))
            tractor_details = lowercase_data(dict(request.form))
            chassis_number = tractor_details.get("chassis-number")
            if chassis_number in os.listdir(UPLOAD_FOLDER):
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
                            UPLOAD_FOLDER,
                            tractor_details.get("chassis-number"),
                            "before",
                            secure_filename(file.filename),
                        )
                    )
                    logger.info(
                        f"{file.filename}->{tractor_details.get('chassis-number')}"
                    )
            logger.info("finished processing add-tractor".center(80, "^"))
        except Exception as e:
            logger.exception(f"{str(e)}", exc_info=True)
    return render_template("add_tractor.html")


@inventory_blueprint.route("/view-tractor", methods=["GET"])
def view_tractor():
    """
    `GET` displays all available tractor in inventory.
    * fetches all `not sold tractor` from mongo db.
    * creates list all tractors and stores in `all_tractor`.
    """
    if request.method == "GET":
        logger.info("started processing view-tractor".center(80, "^"))
        result = mongo_conn.db.stock_tractor.find({"is-sold": "false"}, {"_id": 0})
        all_tractor = [tractor for tractor in result]
        logger.info("Finished processing view-tractor".center(80, "^"))
        return render_template(
            "view_inventory.html",
            all_tractor=all_tractor,
        )


@inventory_blueprint.route("/update-tractor/<string:tractor>/", methods=["GET", "POST"])
def update_tractor(tractor=None):
    """
    `GET` method shows existing information of tractor

    `POST` updates tractors details.
    * empty `request.form` is not affecting existing data.
    * Allows updating chassis-number if already not existes.
    * updates mongo db and uploads new images without deleting old one.

    Args:
        tractor (str, optional): tractor chassis number. Defaults to None.

    """
    if request.method == "GET":
        logger.info("started processing view-tractor".center(80, "^"))
        display_tractor = mongo_conn.db.stock_tractor.find_one(
            {"chassis-number": tractor}, {"_id": 0, "is-sold": 0}
        )
        # Null response check
        display_tractor = display_tractor if display_tractor else dict()
        return render_template(
            "update_tractor.html",
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
            if os.path.exists(os.path.join(UPLOAD_FOLDER, chassis_number)):
                flash(
                    f"Denied updating chassis number from {old_chassis_number} to {chassis_number}."
                )
                flash(f"Reason {chassis_number} already existes.")
                return redirect(url_for("inventory.view_tractor"))
            logger.info(f"renaming tractor {old_chassis_number} folder name")
            os.rename(
                os.path.join(UPLOAD_FOLDER, old_chassis_number),
                os.path.join(UPLOAD_FOLDER, chassis_number),
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
                        UPLOAD_FOLDER,
                        chassis_number,
                        "before",
                        secure_filename(file.filename),
                    )
                )
                logger.info(f"updated at {file.filename}\t-> {chassis_number}")

        return redirect("/view-tractor")


@inventory_blueprint.route("/download-zip/<string:tractor>/", methods=["GET"])
def download_zip(tractor=None):
    """
    purpose is providing zip file of tractor photos before sell to customer.
    * creates zip file under chassis-number folder.
    * clubs all files present under before subfolder.

    Args:
        tractor (str, optional): tractor chassis-number. Defaults to None.

    """
    try:
        logger.info(f"started download-zip api for {tractor}")
        zipf = zipfile.ZipFile(
            os.path.join(UPLOAD_FOLDER, tractor, f"{tractor}-photos.zip"),
            "w",
            zipfile.ZIP_DEFLATED,
        )
        for file in os.listdir(os.path.join(UPLOAD_FOLDER, tractor, "before")):
            zipf.write(os.path.join(UPLOAD_FOLDER, tractor, "before", file), file)
        zipf.close()
        logger.info(
            f'created zip file at {os.path.join(UPLOAD_FOLDER, tractor, f"{tractor}-photos.zip")}'
        )
        return send_file(
            os.path.join(UPLOAD_FOLDER, tractor, f"{tractor}-photos.zip"),
            mimetype="zip",
            download_name=f"{tractor}-photos.zip",
            as_attachment=True,
        )

    except Exception as e:
        flash(f"Invalid operation. {tractor} does not exist.")
        logger.exception(str(e), exc_info=True)
        return redirect("/")

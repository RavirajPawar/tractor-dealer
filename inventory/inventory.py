import os
import zipfile

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename

from common.connector import mongo_conn
from common.constants import (
    upload_folder,
    before_sell,
    buy_document_field,
    godown_list,
    after_sell,
)
from inventory.helper import create_folder, lowercase_data
from logger import logger

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
            logger.info("processing POST /add-tractor".center(80, "^"))
            tractor_details = lowercase_data(dict(request.form))
            chassis_number = tractor_details.get("chassis-number")
            if chassis_number in os.listdir(upload_folder):
                logger.warning(f"{chassis_number} folder already exists")
                flash(f"chassis number {chassis_number} already exists")
                return redirect(url_for("inventory.add_tractor"))
            create_folder(chassis_number)
            mongo_conn.db.stock_tractor.insert_one(tractor_details)
            for doc_field in buy_document_field:
                for file in request.files.getlist(doc_field):
                    if secure_filename(file.filename):
                        file_path = os.path.join(
                            upload_folder,
                            tractor_details.get("chassis-number"),
                            before_sell,
                            "-".join([doc_field, secure_filename(file.filename)]),
                        )
                        file.save(file_path)
                        logger.info(f"{file.filename}->{file_path}")
            logger.info("finished POST /add-tractor".center(80, "^"))
        except Exception as e:
            logger.exception(f"{str(e)}", exc_info=True)
    logger.info("got GET /add-tractor".center(80, "^"))
    return render_template(
        "add_tractor.html",
        godown_list=godown_list,
    )


@inventory_blueprint.route("/view-tractor", methods=["GET"])
def view_tractor():
    """
    `GET` displays all available tractor in inventory.
    * fetches all `not sold tractor` from mongo db.
    * creates list all tractors and stores in `all_tractor`.
    """
    if request.method == "GET":
        logger.info("processing GET /view-tractor".center(80, "^"))
        result = mongo_conn.db.stock_tractor.find({"is-sold": "false"}, {"_id": 0})
        all_tractor = [tractor for tractor in result]
        logger.info("finished /view-tractor".center(80, "^"))
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
        logger.info(f"processing GET /update-tractor/{tractor}".center(80, "^"))
        display_tractor = mongo_conn.db.stock_tractor.find_one(
            {"chassis-number": tractor}, {"_id": 0, "is-sold": 0}
        )
        # Null response check
        display_tractor = display_tractor if display_tractor else dict()
        path = os.path.join(upload_folder, tractor, before_sell)
        files = [file for file in os.listdir(path)]
        document_report = dict()
        for doc in buy_document_field:
            document_report[doc] = list()
            for file in files:
                if file.startswith(doc):
                    document_report[doc].append(file)

        logger.info(f"finished GET /update-tractor/{tractor}".center(80, "^"))
        return render_template(
            "update_tractor.html",
            display_tractor=display_tractor,
            files=files,
            document_field=buy_document_field,
            document_report=document_report,
        )
    elif request.method == "POST":
        logger.info(f"processing POST /update-tractor/{tractor}".center(80, "^"))
        if not dict(request.form):  #
            # TODO: Flash message
            return redirect("/view-tractor")

        update_tractor = {"$set": lowercase_data(dict(request.form))}
        old_chassis_number = update_tractor.get("$set").get("old-chassis-number")
        chassis_number = update_tractor.get("$set").get("chassis-number")
        tractor = old_chassis_number if not tractor else tractor

        if old_chassis_number != chassis_number:
            if os.path.exists(os.path.join(upload_folder, chassis_number)):
                flash(
                    f"Denied updating chassis number from {old_chassis_number} to {chassis_number}."
                )
                flash(f"Reason {chassis_number} already existes.")
                return redirect(url_for("inventory.view_tractor"))
            logger.info(f"renaming tractor {old_chassis_number} folder name")
            os.rename(
                os.path.join(upload_folder, old_chassis_number),
                os.path.join(upload_folder, chassis_number),
            )
            logger.info(f"renamed tractor {chassis_number} folder name")

        logger.info(f"started updating tractor {old_chassis_number} in DB")
        mongo_conn.db.stock_tractor.update_one(
            {"chassis-number": tractor}, update_tractor
        )
        logger.info(f"finished updating tractor {chassis_number} in DB")

        for doc_field in buy_document_field:
            for file in request.files.getlist(doc_field):
                if secure_filename(file.filename):
                    file_path = os.path.join(
                        upload_folder,
                        chassis_number,
                        before_sell,
                        "-".join([doc_field, secure_filename(file.filename)]),
                    )
                    file.save(file_path)
                    logger.info(f"storing at {file.filename}->{file_path}")
        logger.info(f"finished POST /update-tractor/{tractor}".center(80, "^"))
        return redirect(f"/update-tractor/{chassis_number}")


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
        logger.info(f"processing GET /download-zip/{tractor}".center(80, "^"))
        zipf = zipfile.ZipFile(
            os.path.join(upload_folder, tractor, f"{tractor}-documents.zip"),
            "w",
            zipfile.ZIP_DEFLATED,
        )
        for sub_folder in [before_sell, after_sell]:
            for file in os.listdir(os.path.join(upload_folder, tractor, sub_folder)):
                zipf.write(os.path.join(upload_folder, tractor, sub_folder, file), file)
        zipf.close()
        logger.info(
            f'created zip file at {os.path.join(upload_folder, tractor, f"{tractor}-documents.zip")}'
        )
        logger.info(f"finished GET /download-zip/{tractor}".center(80, "^"))
        return send_file(
            os.path.join(upload_folder, tractor, f"{tractor}-documents.zip"),
            mimetype="zip",
            download_name=f"{tractor}-documents.zip",
            as_attachment=True,
        )

    except Exception as e:
        flash(f"Invalid operation. {tractor} does not exist.")
        logger.exception(str(e), exc_info=True)
        return redirect("/")

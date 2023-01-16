from flask import Blueprint, render_template, request, session, redirect

inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)

@inventory_blueprint.route("/inventory", methods=["get", "post"])
def render_inventory():
    print(request.method)
    print(dict(request.form))
    return render_template("inventory.html")

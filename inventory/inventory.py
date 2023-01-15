from flask import Blueprint, render_template, request, session, redirect

inventory_blueprint = Blueprint(
    "inventory", __name__, template_folder="templates", static_folder="static"
)

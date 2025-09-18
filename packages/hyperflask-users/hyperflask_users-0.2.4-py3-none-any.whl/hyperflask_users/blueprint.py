from flask import Blueprint
from flask_file_routes import ModuleView


users_blueprint = Blueprint("users", __name__, template_folder="templates")

ModuleView("hyperflask_users.pages.connect", "users/connect.html", endpoint="connect").register(users_blueprint, "/connect", methods=["GET", "POST"])
ModuleView("hyperflask_users.pages.login", "users/login.html", endpoint="login").register(users_blueprint, "/login", methods=["GET", "POST"])
ModuleView("hyperflask_users.pages.login_link", "users/login_link.html", endpoint="login_link").register(users_blueprint, "/login/link", methods=["GET", "POST"])
ModuleView("hyperflask_users.pages.signup", "users/signup.html", endpoint="signup").register(users_blueprint, "/signup", methods=["GET", "POST"])
ModuleView("hyperflask_users.pages.forgot_password", "users/forgot_password.html", endpoint="forgot_password").register(users_blueprint, "/login/forgot", methods=["GET", "POST"])
ModuleView("hyperflask_users.pages.reset_password", "users/reset_password.html", endpoint="reset_password").register(users_blueprint, "/login/reset", methods=["GET", "POST"])
ModuleView("hyperflask_users.pages.logout", None, endpoint="logout").register(users_blueprint, "/logout", methods=["GET"])

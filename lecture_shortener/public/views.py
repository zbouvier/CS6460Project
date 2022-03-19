# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
import os

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from lecture_shortener.extensions import login_manager
from lecture_shortener.public.forms import LoginForm
from lecture_shortener.user.forms import RegisterForm
from lecture_shortener.user.models import User
from lecture_shortener.utils import flash_errors

blueprint = Blueprint("public", __name__, static_folder="../static")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/")
def upload_form():
    """Renders the home page."""
    return render_template("public/home.html")


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)

    # Handle logging in

    if request.method == "POST" and request.form["type"] == "loginForm":
        current_app.logger.info("Hello from the home page!")
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    elif request.method == "POST" and request.form["type"] == "uploadForm":
        current_app.logger.info(request)
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No image selected for uploading")
            return redirect(request.url)
        else:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            current_app.logger.info("upload_video filename: " + filename)
            flash("Video successfully uploaded and displayed below")
            return render_template("public/upload.html", filename=filename)
    return render_template("public/upload.html", form=form)


def upload_video():
    """Uploads video."""
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)
    else:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        current_app.logger.info("upload_video filename: " + filename)
        flash("Video successfully uploaded and displayed below")
        return render_template("public/upload.html", filename=filename)


@blueprint.route("/display/<filename>")
def display_video(filename):
    """Grabs video from folder and displays it."""
    # print('display_video filename: ' + filename)
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)

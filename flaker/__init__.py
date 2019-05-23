from flask import Flask
from cachecontrol import CacheControl
import requests
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

flaker = Flask(__name__)
session = CacheControl(requests.session())
flaker.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
flaker.config["CI_BASE_URL"] = os.getenv("CI_BASE_URL")
flaker.config["CI_NAMESPACE"] = os.getenv("CI_NAMESPACE")
flaker.config["CI_GIT_REPO"] = os.getenv("CI_GIT_REPO")
flaker.config["CI_GIT_PATH"] = os.getenv("CI_GIT_PATH")
flaker.config["MAIN_GIT_REPO"] = os.getenv("MAIN_GIT_REPO")
flaker.config["MAIN_GIT_LABEL"] = os.getenv("MAIN_GIT_LABEL")
flaker.config["GIT_TOKEN"] = os.getenv("GIT_TOKEN")
flaker.config["GIT_USER"] = os.getenv("GIT_USER")


basedir = os.path.abspath(os.path.dirname(__file__))
flaker.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI"
) or "sqlite:///" + os.path.join(basedir, "flaker.db")
flaker.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(flaker)
migrate = Migrate(flaker, db)

from flaker import routes, models

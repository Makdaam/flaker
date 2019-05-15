from flask import Flask
from cachecontrol import CacheControl
import requests
import os

flaker = Flask(__name__)
session = CacheControl(requests.session())
flaker.config["CI_BASE_URL"] = os.getenv("CI_BASE_URL")
flaker.config["CI_NAMESPACE"] = os.getenv("CI_NAMESPACE")
flaker.config["CI_GIT_REPO"] = os.getenv("CI_GIT_REPO")
flaker.config["CI_GIT_PATH"] = os.getenv("CI_GIT_PATH")
flaker.config["MAIN_GIT_REPO"] = os.getenv("MAIN_GIT_REPO")
flaker.config["MAIN_GIT_LABEL"] = os.getenv("MAIN_GIT_LABEL")
flaker.config["GIT_TOKEN"] = os.getenv("GIT_TOKEN")
flaker.config["GIT_USER"] = os.getenv("GIT_USER")

from flaker import routes

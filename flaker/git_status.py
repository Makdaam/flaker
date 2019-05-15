from flaker import flaker, session
from lxml import etree
import urllib.parse
from pprint import pprint
from requests.auth import HTTPBasicAuth


def get_git_comments():
    comment_list = []
    resp = session.get(
        "https://api.github.com/repos/%s/issues?labels=%s&state=open"
        % (
            flaker.config["MAIN_GIT_REPO"],
            urllib.parse.quote_plus(flaker.config["MAIN_GIT_LABEL"]),
        ),
        auth=HTTPBasicAuth(flaker.config["GIT_USER"], flaker.config["GIT_TOKEN"]),
    )
    issues = resp.json()

    for i in issues:
        i["issue_url"] = i["html_url"]
        resp = session.get(
            i["comments_url"],
            auth=HTTPBasicAuth(flaker.config["GIT_USER"], flaker.config["GIT_TOKEN"]),
        )
        comment_list.append(i)
        comment_list = comment_list + resp.json()
    return comment_list


def enrich_runs(failed_runs):
    git_comments = get_git_comments()
    for r in failed_runs:
        for c in git_comments:
            matched = None
            if r["link"] in c["body"]:
                matched = c
            if "rawlog" in r and r["rawlog"] in c["body"]:
                matched = c
            if matched:
                n = int(matched["issue_url"].split("/")[-1])
                r["issue"] = {"url": matched["issue_url"], "number": n}
    return failed_runs

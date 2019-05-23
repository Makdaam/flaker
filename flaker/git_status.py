from flaker import flaker, session, db, models
from lxml import etree
import urllib.parse
from pprint import pprint
from requests.auth import HTTPBasicAuth
from flaker.models import Issue, Comment, Run
from datetime import datetime


def repopulate_comments():
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
    if len(issues) > 0:
        for i in Issue.query.all():
            for c in i.comments:
                db.session.delete(c)
            db.session.delete(i)
        for i in issues:
            iorm = Issue(
                body=i["body"],
                last_checked=datetime.utcnow(),
                link=i["html_url"],
                number=i["number"],
                title=i["title"],
            )
            db.session.add(iorm)
            db.session.commit()
            resp = session.get(
                i["comments_url"],
                auth=HTTPBasicAuth(
                    flaker.config["GIT_USER"], flaker.config["GIT_TOKEN"]
                ),
            )
            for c in resp.json():
                corm = Comment(issue_id=iorm.id, body=c["body"])
                db.session.add(corm)
            db.session.commit()


def enrich_runs():
    github_comments = Comment.query.all()
    github_issues = Issue.query.all()
    for r in Run.query.filter_by(success=False).all():
        for i in github_issues:
            matched = None
            if r.link in i.body:
                matched = i
            if r.rawlog_link in i.body:
                matched = i
            if matched:
                r.issue_id = matched.id
        for c in github_comments:
            matched = None
            if r.link in c.body:
                matched = c
            if r.rawlog_link in c.body:
                matched = c
            if matched:
                r.issue_id = matched.issue_id
    db.session.commit()

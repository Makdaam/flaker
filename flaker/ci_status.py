from flaker import flaker, session, db, models
from lxml import etree
from pprint import pprint
import yaml
import copy
from datetime import datetime, timezone, timedelta
import time
from requests.auth import HTTPBasicAuth
from flaker.models import Job, Run


def repopulate_jobs():
    resp = session.get(
        "https://api.github.com/repos/%s/contents/%s"
        % (flaker.config["CI_GIT_REPO"], flaker.config["CI_GIT_PATH"]),
        auth=HTTPBasicAuth(flaker.config["GIT_USER"], flaker.config["GIT_TOKEN"]),
    )
    file_list = resp.json()
    jobs_names_list = list()
    for f in file_list:
        if f["name"].endswith(".yaml"):
            resp = session.get(
                f["download_url"],
                auth=HTTPBasicAuth(
                    flaker.config["GIT_USER"], flaker.config["GIT_TOKEN"]
                ),
            )
            yaml_config = yaml.safe_load(resp.content)
            if "postsubmits" in yaml_config:
                if flaker.config["MAIN_GIT_REPO"] in yaml_config["postsubmits"]:
                    for job in yaml_config["postsubmits"][
                        flaker.config["MAIN_GIT_REPO"]
                    ]:
                        jobs_names_list.append(job["name"])
            if "periodics" in yaml_config:
                for job in yaml_config["periodics"]:
                    jobs_names_list.append(job["name"])
    if len(jobs_names_list) > 0:
        # repopulate only if we got valid jobs
        for j in models.Job.query.all():
            for r in j.runs:
                db.session.delete(r)
            db.session.delete(j)
        for j in jobs_names_list:
            nj = Job(
                ci_base_url=flaker.config["CI_BASE_URL"],
                ci_namespace=flaker.config["CI_NAMESPACE"],
                name=j,
                last_checked=datetime.utcfromtimestamp(1),
            )
            db.session.add(nj)
        db.session.commit()


def repopulate_runs():
    if Job.query.count() == 0:
        repopulate_jobs()
    # get jobs from CI, find failed runs
    failed_runs = []
    for job in Job.query.all():
        if (datetime.utcnow() - job.last_checked) > timedelta(hours=1):
            resp = session.get(
                "%s/builds/%s/logs/%s" % (job.ci_base_url, job.ci_namespace, job.name)
            )
            parse_runs(resp.content, job)
            job.last_checked = datetime.utcnow()


def parse_runs(html_content, job, epoch_threshold=7 * 24 * 60 * 60):
    now = int(time.time())
    tree = etree.HTML(html_content)
    runs = list()
    for item in tree.findall(".//span[@class='build-number']"):
        run = {}
        spans = item.getparent().xpath("./span")
        run["link"] = flaker.config["CI_BASE_URL"] + item.getparent().get("href")
        run["num"] = int(item.xpath("text()")[0])
        for s in spans:
            if "build-timestamp" in s.get("class"):
                run["epoch"] = int(s.xpath("./span")[0].get("data-epoch"))
                if run["epoch"] < now - epoch_threshold:
                    # skip if older than epoch_threshold
                    continue
                run["success"] = "SUCCESS" in s.get("title")
                if (
                    Run.query.filter_by(number=run["num"])
                    .filter_by(job_id=job.id)
                    .count()
                    == 0
                ):
                    rorm = Run(
                        number=run["num"],
                        link=run["link"],
                        success=run["success"],
                        timestamp=datetime.utcfromtimestamp(run["epoch"]),
                        job_id=job.id,
                    )
                    # get raw log link
                    resp = session.get(run["link"])
                    tree = etree.HTML(resp.content)
                    for li in tree.findall(".//li[@class='log']"):
                        if "Raw build-log.txt" in li.xpath("string()"):
                            rorm.rawlog_link = li.xpath("./a")[0].get("href")
                    db.session.add(rorm)
        db.session.commit()

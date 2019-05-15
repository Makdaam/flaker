from flaker import flaker, session
from lxml import etree
from pprint import pprint
import yaml
import copy
from datetime import datetime, timezone
import time
from requests.auth import HTTPBasicAuth


def get_failed_runs():
    # get jobs names from CI config
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
    # get jobs from CI, find failed runs
    failed_runs = []
    for job in jobs_names_list:
        resp = session.get(
            "%s/builds/%s/logs/%s"
            % (flaker.config["CI_BASE_URL"], flaker.config["CI_NAMESPACE"], job)
        )
        failed_runs = failed_runs + parse_failed_runs(
            resp.content, {"issue": None, "job": job}
        )
    return failed_runs


def parse_failed_runs(html_content, run_template={}, epoch_threshold=7 * 24 * 60 * 60):
    now = int(time.time())
    tree = etree.HTML(html_content)
    failed_runs = list()
    for item in tree.findall(".//span[@class='build-number']"):
        run = copy.deepcopy(run_template)
        spans = item.getparent().xpath("./span")
        run["link"] = flaker.config["CI_BASE_URL"] + item.getparent().get("href")
        run["id"] = int(item.xpath("text()")[0])
        for s in spans:
            if "build-timestamp" in s.get("class"):
                run["epoch"] = int(s.xpath("./span")[0].get("data-epoch"))
                if run["epoch"] < now - epoch_threshold:
                    # skip if older than epoch_threshold
                    continue
                run["timestamp"] = datetime.fromtimestamp(
                    run["epoch"], timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S")
                run["success"] = "SUCCESS" in s.get("title")
        if "success" in run and not run["success"]:
            failed_runs.append(run)
    return failed_runs


def enrich_runs(runs):
    for r in runs:
        resp = session.get(r["link"])
        tree = etree.HTML(resp.content)
        for li in tree.findall(".//li[@class='log']"):
            if "Raw build-log.txt" in li.xpath("string()"):
                r["rawlog"] = li.xpath("./a")[0].get("href")
    return runs

from flaker import flaker, ci_status, git_status
from flask import render_template


@flaker.route("/")
@flaker.route("/index")
def index():
    fr = ci_status.get_failed_runs()
    fr = ci_status.enrich_runs(fr)
    fr = git_status.enrich_runs(fr)
    return render_template(
        "index.html",
        title="Flakes",
        failed_runs=fr,
        job_base_url="%s/builds/%s/logs/"
        % (flaker.config["CI_BASE_URL"], flaker.config["CI_NAMESPACE"]),
    )

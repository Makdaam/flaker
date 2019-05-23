from flaker import flaker, ci_status, git_status
from flaker.models import Job, Run, Issue
from flaker.forms import EmptyForm
from flask import render_template, redirect


@flaker.route("/", methods=["GET", "POST"])
@flaker.route("/index", methods=["GET", "POST"])
def index():
    f = EmptyForm()
    if f.validate_on_submit():
        ci_status.repopulate_runs()
        git_status.repopulate_comments()
        git_status.enrich_runs()
        return redirect("/index")
    return render_template(
        "index.html",
        title="Flakes",
        form=f,
        runs=Run.query.filter_by(success=False).all(),
        issues=Issue.query.all(),
    )


@flaker.route("/jobs", methods=["GET", "POST"])
def jobs():
    f = EmptyForm()
    if f.validate_on_submit():
        ci_status.repopulate_jobs()
        return redirect("/jobs")
    return render_template("jobs.html", jobs=Job.query.all(), form=f)

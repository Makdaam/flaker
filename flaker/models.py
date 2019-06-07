from flaker import db
from datetime import datetime


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ci_base_url = db.Column(db.String())
    ci_namespace = db.Column(db.String())
    name = db.Column(db.String())
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    runs = db.relationship(
        "Run", backref="job", primaryjoin="Job.id==Run.job_id", lazy="dynamic"
    )

    def __repr__(self):
        return "<Job %s>" % (self.name)


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    success = db.Column(db.Boolean())
    link = db.Column(db.String())
    rawlog_link = db.Column(db.String())
    number = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"))
    issue_id = db.Column(db.Integer, db.ForeignKey("issue.id"))
    issue = db.relationship("Issue", foreign_keys="Run.issue_id")

    def __repr__(self):
        return "<Run %d>" % (self.id)


class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String())
    last_checked = db.Column(db.DateTime)
    link = db.Column(db.String())
    number = db.Column(db.Integer)
    title = db.Column(db.String())
    comments = db.relationship(
        "Comment",
        backref="issue",
        primaryjoin="Issue.id==Comment.issue_id",
        lazy="dynamic",
    )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String())
    issue_id = db.Column(db.Integer, db.ForeignKey("issue.id"))

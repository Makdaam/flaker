"""empty message

Revision ID: 5788c13e88e9
Revises: 
Create Date: 2019-05-23 09:41:15.579503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5788c13e88e9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('issue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('last_checked', sa.DateTime(), nullable=True),
    sa.Column('link', sa.String(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('job',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ci_base_url', sa.String(), nullable=True),
    sa.Column('ci_namespace', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('last_checked', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(), nullable=True),
    sa.Column('issue_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('run',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('success', sa.Boolean(), nullable=True),
    sa.Column('link', sa.String(), nullable=True),
    sa.Column('rawlog_link', sa.String(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('job_id', sa.Integer(), nullable=True),
    sa.Column('issue_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], ),
    sa.ForeignKeyConstraint(['job_id'], ['job.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('run')
    op.drop_table('comment')
    op.drop_table('job')
    op.drop_table('issue')
    # ### end Alembic commands ###
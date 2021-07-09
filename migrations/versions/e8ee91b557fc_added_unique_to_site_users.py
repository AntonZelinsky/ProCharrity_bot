"""added unique to site_users

Revision ID: e8ee91b557fc
Revises: 93011616ac40
Create Date: 2021-07-09 19:03:05.389091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8ee91b557fc'
down_revision = '93011616ac40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('site_users_constr', 'site_users', ['id_hash', 'email'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('site_users_constr', 'site_users', type_='unique')
    # ### end Alembic commands ###
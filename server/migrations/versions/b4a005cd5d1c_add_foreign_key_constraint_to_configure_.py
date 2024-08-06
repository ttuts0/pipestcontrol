"""Add foreign key constraint to configure table

Revision ID: b4a005cd5d1c
Revises: 5d66da3d8ede
Create Date: 2024-07-31 15:24:54.323617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4a005cd5d1c'
down_revision = '5d66da3d8ede'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'configure', 'critter', ['critter_name'], ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'configure', type_='foreignkey')
    # ### end Alembic commands ###
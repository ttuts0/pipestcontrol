"""Add foreign key constraint to configure table

Revision ID: 5d66da3d8ede
Revises: fa35c9f86954
Create Date: 2024-07-31 15:23:37.232396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d66da3d8ede'
down_revision = 'fa35c9f86954'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('configure',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('critter_name', sa.String(length=50), nullable=False),
    sa.Column('cooldown_time', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('critter_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('configure')
    # ### end Alembic commands ###
"""Improved relationships among subscription tables, changed some data types and default values.

Revision ID: 1bd18a8d6c3a
Revises: 9b61853ec0e8
Create Date: 2025-02-26 20:47:32.722876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bd18a8d6c3a'
down_revision: Union[str, None] = '9b61853ec0e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('features', schema=None) as batch_op:
        batch_op.alter_column('value',
               existing_type=sa.VARCHAR(),
               nullable=False)

    with op.batch_alter_table('subscription_plan', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_subscription_plan_name', ['name'])

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscription_plan', schema=None) as batch_op:
        batch_op.drop_constraint('uq_subscription_plan_name', type_='unique')

    with op.batch_alter_table('features', schema=None) as batch_op:
        batch_op.alter_column('value',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###

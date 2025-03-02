"""Updating Modeltype enum and links.

Revision ID: 436073762e72
Revises: 5f4ee3b8b8f9
Create Date: 2025-02-18 15:54:57.093275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '436073762e72'
down_revision: Union[str, None] = '5f4ee3b8b8f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('detections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('model_type', sa.Enum('DETECTION', 'SEGMENTATION', 'CLASSIFICATION', 'POSE', name='modeltypeenum'), nullable=False))

    with op.batch_alter_table('processed_images', schema=None) as batch_op:
        batch_op.add_column(sa.Column('processed_type', sa.Enum('DETECTION', 'SEGMENTATION', 'CLASSIFICATION', 'POSE', name='modeltypeenum'), nullable=False))
        batch_op.create_index(batch_op.f('ix_processed_images_processed_type'), ['processed_type'], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('processed_images', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_processed_images_processed_type'))
        batch_op.drop_column('processed_type')

    with op.batch_alter_table('detections', schema=None) as batch_op:
        batch_op.drop_column('model_type')

    # ### end Alembic commands ###

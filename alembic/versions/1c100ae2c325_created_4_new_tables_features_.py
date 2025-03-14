"""Created 4 new tables Features, FeatureGroup, SubscriptionPlan, SubscriptionFeature for managing subscriptions.

Revision ID: 1c100ae2c325
Revises: ae742472c36f
Create Date: 2025-02-26 18:36:39.377749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '1c100ae2c325'
down_revision: Union[str, None] = 'ae742472c36f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feature_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('feature_group', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_feature_group_title'), ['title'], unique=True)

    op.create_table('subscription_plan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Enum('BASIC', 'SILVER', 'GOLD', name='subscriptionplans'), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('popular', sa.Boolean(), nullable=False),
    sa.Column('premium', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('subscription_plan', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_subscription_plan_name'), ['name'], unique=True)

    op.create_table('features',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('feature_group_id', sa.Integer(), nullable=False),
    sa.Column('key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('data_type', sa.Enum('STRING', 'NUMBER', 'BOOLEAN', name='featuredatatype'), nullable=False),
    sa.Column('required', sa.Boolean(), nullable=False),
    sa.Column('default_value', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['feature_group_id'], ['feature_group.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('features', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_features_feature_group_id'), ['feature_group_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_features_key'), ['key'], unique=False)

    op.create_table('subscription_features',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subscription_plan_id', sa.Integer(), nullable=False),
    sa.Column('feature_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['feature_id'], ['features.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['subscription_plan_id'], ['subscription_plan.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('subscription_features', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_subscription_features_feature_id'), ['feature_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_subscription_features_subscription_plan_id'), ['subscription_plan_id'], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscription_features', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_subscription_features_subscription_plan_id'))
        batch_op.drop_index(batch_op.f('ix_subscription_features_feature_id'))

    op.drop_table('subscription_features')
    with op.batch_alter_table('features', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_features_key'))
        batch_op.drop_index(batch_op.f('ix_features_feature_group_id'))

    op.drop_table('features')
    with op.batch_alter_table('subscription_plan', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_subscription_plan_name'))

    op.drop_table('subscription_plan')
    with op.batch_alter_table('feature_group', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_feature_group_title'))

    op.drop_table('feature_group')
    # ### end Alembic commands ###

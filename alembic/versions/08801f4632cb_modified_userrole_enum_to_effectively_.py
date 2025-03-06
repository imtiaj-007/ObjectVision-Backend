"""Modified UserRole Enum to effectively work accross whole portal.

Revision ID: 08801f4632cb
Revises: b0ac69bfd56b
Create Date: 2025-03-05 15:39:53.636675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08801f4632cb'
down_revision: Union[str, None] = 'b0ac69bfd56b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create the userrole enum type
    userrole_enum = sa.Enum('ADMIN', 'SUB_ADMIN', 'USER', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)

    # Step 2: Add a new temporary column with the ENUM type
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_temp', userrole_enum, nullable=True))

    # Step 3: Migrate data from integer to ENUM
    op.execute("UPDATE users SET role_temp = 'USER' WHERE role = 3;")
    op.execute("UPDATE users SET role_temp = 'SUB_ADMIN' WHERE role = 2;")
    op.execute("UPDATE users SET role_temp = 'ADMIN' WHERE role = 1;")

    # Step 4: Drop the old column and rename the new one
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('role')
        batch_op.alter_column('role_temp', new_column_name='role', nullable=False)
        

def downgrade() -> None:
    # Step 1: Add a new temporary column with INTEGER type
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_temp', sa.INTEGER(), nullable=True))

    # Step 2: Convert ENUM values back to integers
    op.execute("UPDATE users SET role_temp = 3 WHERE role = 'USER';")
    op.execute("UPDATE users SET role_temp = 2 WHERE role = 'SUB_ADMIN';")
    op.execute("UPDATE users SET role_temp = 1 WHERE role = 'ADMIN';")

    # Step 3: Drop the ENUM column and rename the new one
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('role')
        batch_op.alter_column('role_temp', new_column_name='role', nullable=False)

    # Step 4: Drop the userrole ENUM type
    userrole_enum = sa.Enum('ADMIN', 'SUB_ADMIN', 'USER', name='userrole')
    userrole_enum.drop(op.get_bind(), checkfirst=True)

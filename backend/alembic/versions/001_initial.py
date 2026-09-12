"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2026-09-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("preferred_language", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # ------------------------------------------------------------------
    # Senders
    # ------------------------------------------------------------------
    op.create_table(
        "senders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("default_language", sa.String(length=10), nullable=False),
        sa.Column("avatar", sa.String(length=255), nullable=True),
        sa.Column("profile_info", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_senders_id"), "senders", ["id"], unique=False)
    op.create_index(op.f("ix_senders_name"), "senders", ["name"], unique=False)

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sender_id", sa.String(length=36), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_from_user", sa.Boolean(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("is_replied", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["senders.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)
    op.create_index(
        op.f("ix_messages_sender_id"),
        "messages",
        ["sender_id"],
        unique=False,
    )

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------
    op.create_table(
        "memory",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sender_id", sa.String(length=36), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_facts", sa.JSON(), nullable=True),
        sa.Column("pending_actions", sa.JSON(), nullable=True),
        sa.Column("last_interaction", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["senders.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_memory_id"), "memory", ["id"], unique=False)
    op.create_index(
        op.f("ix_memory_sender_id"),
        "memory",
        ["sender_id"],
        unique=True,
    )

    # ------------------------------------------------------------------
    # Replies
    # ------------------------------------------------------------------
    op.create_table(
        "replies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("message_id", sa.String(length=36), nullable=False),
        sa.Column("generated_reply", sa.Text(), nullable=True),
        sa.Column("final_reply", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["messages.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_replies_id"), "replies", ["id"], unique=False)
    op.create_index(
        op.f("ix_replies_message_id"),
        "replies",
        ["message_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_replies_message_id"), table_name="replies")
    op.drop_index(op.f("ix_replies_id"), table_name="replies")
    op.drop_table("replies")

    op.drop_index(op.f("ix_memory_sender_id"), table_name="memory")
    op.drop_index(op.f("ix_memory_id"), table_name="memory")
    op.drop_table("memory")

    op.drop_index(op.f("ix_messages_sender_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_table("messages")

    op.drop_index(op.f("ix_senders_name"), table_name="senders")
    op.drop_index(op.f("ix_senders_id"), table_name="senders")
    op.drop_table("senders")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
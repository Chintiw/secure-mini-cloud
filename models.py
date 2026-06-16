# models.py
# Single source of truth for all database models — SecureCloud v3.0
# Tables: users, files, blockchain_ledger

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# users table
# PRD v2.0 §5 + PRD v3.0 §6 (is_admin amendment)
# ---------------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id             = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    username       = db.Column(db.String(150), unique=True, nullable=False)
    email          = db.Column(db.String(150), unique=True, nullable=False)
    password_hash  = db.Column(db.String(256), nullable=False)
    encryption_key = db.Column(db.String(256), nullable=False)
    is_admin       = db.Column(db.Boolean,  default=False,  nullable=False)   # PRD v3.0 §6
    created_at     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    files = db.relationship('File', backref='owner', lazy='dynamic',
                            cascade='all, delete-orphan')

    # Index: login lookup by email is the hot path
    __table_args__ = (
        db.Index('ix_users_email',    'email'),
        db.Index('ix_users_username', 'username'),
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r} is_admin={self.is_admin}>"


# ---------------------------------------------------------------------------
# files table
# PRD v2.0 §5
# ---------------------------------------------------------------------------
class File(db.Model):
    __tablename__ = 'files'

    id                = db.Column(db.String(36), primary_key=True,
                                  default=lambda: str(uuid.uuid4()))   # ISO-05: UUID, not int
    owner_id          = db.Column(db.Integer, db.ForeignKey('users.id',
                                  ondelete='CASCADE'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename   = db.Column(db.String(255), nullable=False, unique=True)
    file_size         = db.Column(db.Integer,   nullable=False)         # bytes
    uploaded_at       = db.Column(db.DateTime,  default=datetime.utcnow, nullable=False)

    # Index: dashboard query filters by owner_id
    __table_args__ = (
        db.Index('ix_files_owner_id', 'owner_id'),
    )

    def __repr__(self):
        return f"<File id={self.id!r} owner_id={self.owner_id} name={self.original_filename!r}>"


# ---------------------------------------------------------------------------
# blockchain_ledger table
# PRD v3.0 §6 + CHAIN-01
# NFR-06: Only INSERT operations are permitted on this table — never UPDATE or DELETE.
# ---------------------------------------------------------------------------
class BlockchainLedger(db.Model):
    __tablename__ = 'blockchain_ledger'

    # id auto-increments and doubles as the block index (CHAIN-01)
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp     = db.Column(db.Text,    nullable=False)   # ISO-8601 UTC, e.g. 2025-06-13T14:32:01Z
    action        = db.Column(db.Text,    nullable=False)   # UPLOAD|DOWNLOAD|DELETE|LOGIN|LOGIN_FAIL|GENESIS
    actor         = db.Column(db.Text,    nullable=False)   # username or email-attempted
    detail        = db.Column(db.Text,    nullable=True,  default="")  # filename or IP
    previous_hash = db.Column(db.Text,    nullable=False)   # SHA-256 hex of prior block
    hash          = db.Column(db.Text,    nullable=False)   # SHA-256 hex of this block

    # Index: verify_chain() and admin ledger view both ORDER BY id ASC
    __table_args__ = (
        db.Index('ix_blockchain_ledger_id', 'id'),
    )

    def __repr__(self):
        return (f"<Block id={self.id} action={self.action!r} "
                f"actor={self.actor!r} hash={self.hash[:12]}...>")

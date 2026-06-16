# chain.py
# Blockchain Core Module — SecureCloud v3.0
# Satisfies: CHAIN-01, CHAIN-02, CHAIN-03, CHAIN-04
# CHAIN-05 (genesis) is triggered from app.py after db.create_all()

import hashlib
import datetime
import logging

logger = logging.getLogger(__name__)


def _compute_hash(index: int, timestamp: str, action: str,
                  actor: str, detail: str, previous_hash: str) -> str:
    """
    CHAIN-02: SHA-256 of all six block fields concatenated in fixed order.
    Field order: index | timestamp | action | actor | detail | previous_hash
    This order is the chain's 'protocol' — must never change once blocks exist.
    """
    raw = f"{index}{timestamp}{action}{actor}{detail}{previous_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def add_block(action: str, actor: str, detail: str = "") -> None:
    """
    CHAIN-03: Append a new block to the chain.
    Reads the last block's hash from the DB to form the cryptographic link.
    NFR-09: Exceptions are caught and logged — primary route operations are unaffected.
    """
    # Import inside function to avoid circular import at module load time
    from models import db, BlockchainLedger

    try:
        last = BlockchainLedger.query.order_by(BlockchainLedger.id.desc()).first()

        if last is None:
            # No blocks yet — this becomes block #1
            prev_hash = "0" * 64
            new_index = 1
        else:
            prev_hash = last.hash
            new_index = last.id + 1

        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        block_hash = _compute_hash(
            index=new_index,
            timestamp=timestamp,
            action=action,
            actor=actor,
            detail=detail,
            previous_hash=prev_hash,
        )

        entry = BlockchainLedger(
            timestamp=timestamp,
            action=action,
            actor=actor,
            detail=detail,
            previous_hash=prev_hash,
            hash=block_hash,
        )
        db.session.add(entry)
        db.session.commit()

    except Exception as exc:  # NFR-09: graceful degradation
        logger.error("add_block failed (action=%s, actor=%s): %s", action, actor, exc)


def verify_chain() -> tuple:
    """
    CHAIN-04: Verify the entire chain's integrity.
    Returns (True, None) if intact.
    Returns (False, block_id) at the first broken link.
    """
    from models import BlockchainLedger

    blocks = BlockchainLedger.query.order_by(BlockchainLedger.id.asc()).all()

    for i, block in enumerate(blocks):
        # Step 1: Recompute this block's hash from its stored fields
        recomputed = _compute_hash(
            index=block.id,
            timestamp=block.timestamp,
            action=block.action,
            actor=block.actor,
            detail=block.detail,
            previous_hash=block.previous_hash,
        )
        if recomputed != block.hash:
            return False, block.id

        # Step 2: Check that this block correctly references the previous block
        if i > 0 and block.previous_hash != blocks[i - 1].hash:
            return False, block.id

    return True, None

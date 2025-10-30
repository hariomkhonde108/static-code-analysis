"""
Inventory system module.

Provides an InventorySystem class to manage item quantities,
persist to JSON file, and report low-stock items.
"""
from __future__ import annotations
import json
import logging
from typing import Dict, Optional, Iterable
from pathlib import Path
import ast

logger = logging.getLogger(__name__)


class InventorySystem:
    """Simple inventory manager storing item -> quantity mapping."""

    def __init__(self, initial: Optional[Dict[str, int]] = None) -> None:
        """
        Initialize inventory.

        Args:
            initial: optional dict to pre-populate inventory.
        """
        self._inventory: Dict[str, int] = dict(initial or {})

    def add_item(self, name: str, qty: int = 1) -> None:
        """
        Add quantity to an item, validating inputs.

        Args:
            name: item name (non-empty string).
            qty: positive integer to add.

        Raises:
            ValueError: if inputs are invalid.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("qty must be a positive integer")

        prev = self._inventory.get(name, 0)
        self._inventory[name] = prev + qty
        logger.debug("Added %d of %s (previous %d)", qty, name, prev)

    def remove_item(self, name: str, qty: int = 1) -> None:
        """
        Remove quantity from an item.

        Raises:
            KeyError: if item does not exist.
            ValueError: if qty invalid or result would go negative.
        """
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("qty must be a positive integer")
        if name not in self._inventory:
            raise KeyError(f"item '{name}' not found")
        if self._inventory[name] < qty:
            raise ValueError("not enough quantity to remove")

        self._inventory[name] -= qty
        if self._inventory[name] == 0:
            del self._inventory[name]
        logger.debug("Removed %d of %s", qty, name)

    def get_qty(self, name: str) -> int:
        """Return quantity for item (0 if not present)."""
        return int(self._inventory.get(name, 0))

    def load_data(self, filepath: str) -> None:
        """
        Load inventory from JSON file.

        Uses json for safe parsing. Accepts files created by save_data.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"{filepath} not found")

        with path.open("r", encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError as exc:
                logger.error("JSON decode error when loading %s: %s", filepath, exc)
                raise

        if not isinstance(data, dict):
            raise ValueError("inventory file must contain a JSON object mapping names to integers")

        # Validate and normalize values
        normalized: Dict[str, int] = {}
        for k, v in data.items():
            if not isinstance(k, str):
                raise ValueError("inventory keys must be strings")
            if not isinstance(v, int):
                # attempt to coerce safe string/numeric values
                if isinstance(v, str):
                    try:
                        v_eval = ast.literal_eval(v)
                    except (ValueError, SyntaxError):
                        raise ValueError(f"invalid quantity for item {k}")
                    if not isinstance(v_eval, int):
                        raise ValueError(f"invalid quantity for item {k}")
                    normalized[k] = v_eval
                else:
                    raise ValueError(f"invalid quantity type for item {k}")
            else:
                normalized[k] = v
        self._inventory = normalized
        logger.info("Loaded inventory from %s", filepath)

    def save_data(self, filepath: str) -> None:
        """Persist inventory to a JSON file using utf-8 encoding."""
        path = Path(filepath)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(self._inventory, fh, ensure_ascii=False, indent=2)
        logger.info("Saved inventory to %s", filepath)

    def print_data(self) -> None:
        """Print inventory contents (debug helper)."""
        for name, qty in sorted(self._inventory.items()):
            print(f"{name}: {qty}")

    def check_low_items(self, threshold: int = 5) -> Iterable[str]:
        """
        Return list of item names whose quantity <= threshold.

        Args:
            threshold: non-negative int threshold.
        """
        if not isinstance(threshold, int) or threshold < 0:
            raise ValueError("threshold must be a non-negative integer")
        return [name for name, qty in self._inventory.items() if qty <= threshold]

    def as_dict(self) -> Dict[str, int]:
        """Return a shallow copy of the underlying inventory mapping."""
        return dict(self._inventory)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure basic logging for module use."""
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s:%(message)s")
    logger.setLevel(level)


if __name__ == "__main__":
    # Minimal CLI for manual testing (kept small and validated)
    configure_logging()
    inv = InventorySystem()
    # Example usage — in real use, replace with argument parsing / tests
    try:
        inv.add_item("widget", 10)
        inv.remove_item("widget", 2)
        inv.save_data("inventory.json")
        print("Low items:", inv.check_low_items(threshold=5))
    except Exception as exc:  # top-level error handling for CLI demo
        logger.exception("Unhandled error in demo: %s", exc)
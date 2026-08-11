from pathlib import Path

import pytest

from hcx_eval.datasets.inventory import InventoryError, build_inventory


def test_inventory_is_deterministic_and_does_not_mutate_sources(tmp_path: Path) -> None:
    # Given: source files created in non-lexical order.
    source = tmp_path / "source"
    source.mkdir()
    _ = (source / "z.txt").write_bytes(b"z")
    _ = (source / "a.txt").write_bytes(b"a")
    before = {path: path.read_bytes() for path in source.iterdir()}

    # When: two inventories are generated.
    first = build_inventory(source)
    second = build_inventory(source)

    # Then: hashes/order are stable and bytes remain untouched.
    assert first == second
    assert [entry.relative_path for entry in first.files] == ["a.txt", "z.txt"]
    assert before == {path: path.read_bytes() for path in source.iterdir()}


def test_inventory_rejects_symlinks(tmp_path: Path) -> None:
    # Given: a source root containing an alias to data outside its tree.
    source = tmp_path / "source"
    source.mkdir()
    target = tmp_path / "outside.txt"
    _ = target.write_text("outside", encoding="utf-8")
    (source / "link.txt").symlink_to(target)

    # When / Then: inventory refuses ambiguous source identity.
    with pytest.raises(InventoryError):
        _ = build_inventory(source)

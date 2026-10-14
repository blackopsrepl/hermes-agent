"""Tests for the verify-real-artifact bundled skill.

The skill is prose policy, so the load-bearing checks are the mechanical
authoring contract (frontmatter, description budget, in-repo related_skills)
plus content invariants that keep the policy coherent: the bug-fix
repro-first carve-out must stay, and the skill must not regress into
mandating test-first development.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skills" / "software-development" / "verify-real-artifact" / "SKILL.md"
OLD_TDD = REPO / "skills" / "software-development" / "test-driven-development"


@pytest.fixture(scope="module")
def skill_text() -> str:
    assert SKILL.exists(), f"missing {SKILL}"
    return SKILL.read_text()


@pytest.fixture(scope="module")
def frontmatter(skill_text: str) -> dict:
    assert skill_text.startswith("---"), "frontmatter must start at byte 0"
    close = skill_text.index("\n---\n", 3)
    block = skill_text[3:close]
    # Minimal YAML mapping parse without external deps.
    fields: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if m and not line.startswith(" "):
            fields[m.group(1)] = m.group(2).strip().strip('"')
    return fields


def test_description_within_sixty_chars(frontmatter: dict) -> None:
    desc = frontmatter["description"]
    assert len(desc) <= 60, f"description is {len(desc)} chars, hardline is 60"
    assert desc.endswith(".")


def test_required_frontmatter_fields(frontmatter: dict) -> None:
    for field in ("name", "description", "version", "author", "license", "platforms"):
        assert frontmatter.get(field), f"missing frontmatter field: {field}"
    assert frontmatter["author"].startswith("Vittorio"), "human credited first"


def test_repro_first_carve_out_present(skill_text: str) -> None:
    assert "Bug fixes keep failing-test-first" in skill_text
    assert "failing" in skill_text and "repro" in skill_text.lower()


def test_no_test_first_default(skill_text: str) -> None:
    # The policy must not mandate test-first for general feature work.
    iron_law = re.search(r"NO PRODUCTION CODE WITHOUT", skill_text)
    assert iron_law is None, "policy regressed into the TDD Iron Law"


def test_unit_test_justifications_enumerated(skill_text: str) -> None:
    assert "Pure complex logic" in skill_text
    assert "Regression pins" in skill_text


def test_old_tdd_skill_is_gone() -> None:
    assert not OLD_TDD.exists(), (
        "test-driven-development was replaced by verify-real-artifact; "
        "the old directory must not return without a policy decision"
    )


def test_related_skills_resolve_in_repo(skill_text: str) -> None:
    m = re.search(r"related_skills:\s*\[([^\]]*)\]", skill_text)
    assert m, "metadata.hermes.related_skills missing"
    for name in (s.strip() for s in m.group(1).split(",")):
        hits = list(REPO.glob(f"skills/**/{name}/SKILL.md")) + list(
            REPO.glob(f"optional-skills/**/{name}/SKILL.md")
        )
        assert hits, f"related skill {name!r} does not resolve in-repo"

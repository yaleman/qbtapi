default: help

help:
    just --list

checks:
    uv run mypy --strict qbtapi tests
    uv run ruff check qbtapi tests
    uv run pytest
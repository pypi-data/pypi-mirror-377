#!/bin/bash

uv build \
    && uv run twine upload dist/* --skip-existing

# dspy-cli

[![PyPI](https://img.shields.io/pypi/v/dspy-cli.svg)](https://pypi.org/project/dspy-cli/)
[![Changelog](https://img.shields.io/github/v/release/isaacbmiller/dspy-cli?include_prereleases&label=changelog)](https://github.com/isaacbmiller/dspy-cli/releases)
[![Tests](https://github.com/isaacbmiller/dspy-cli/actions/workflows/test.yml/badge.svg)](https://github.com/isaacbmiller/dspy-cli/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/isaacbmiller/dspy-cli/blob/master/LICENSE)

Utility for deploying dspy applications

## Installation

Install this tool using `pip`:
```bash
pip install dspy-cli
```
## Usage

For help, run:
```bash
dspy-cli --help
```
You can also use:
```bash
python -m dspy_cli --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd dspy-cli
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```

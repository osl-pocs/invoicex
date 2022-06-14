# GH-Report

## Installation

### Development

```bash
mamba env create --file conda/dev.yaml --force
conda activate invoicex
poetry install
```

## Configuration

provide a `.env` file with the the `GITHUB_TOKEN`:

```bash
GITHUB_TOKEN=ghp_blablabla
```
## Running

Example:

```bash
python invoicex/main.py \
  --year-month 2022-04 \
  --gh-user $USER \
  --gh-org osl-incubator/invoicex \
  --timezone "-0400"
```

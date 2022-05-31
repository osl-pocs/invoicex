import json
import os

import pandas as pd
from dotenv import load_dotenv
from jinja2 import Template

dotenv_path = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(__file__))), ".env"
)
load_dotenv(dotenv_path=dotenv_path)


async def generate(results: pd.DataFrame, args: dict):
    os.makedirs("/tmp/invoicex", exist_ok=True)
    with open(f"/tmp/invoicex/{args.year_month}.md", "w") as f:
        f.write(results.to_markdown(index=False))

#!/usr/bin/env python3
"""Extract product name and Tabler icon slug (after 'ti ti-') from product_table.html → products.csv."""
import csv
import re
from html import unescape
from pathlib import Path

HTML_PATH = Path(__file__).resolve().parent / "product_table.html"
OUT_PATH = Path(__file__).resolve().parent / "products.csv"

def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    # Second <td> is name; third column has <i class="ti ti-slug">
    pat = re.compile(
        r"<tr>\s*<td class=\"num\">\d+</td>\s*<td>(?P<name>.*?)</td>\s*<td>.*?class=\"ti ti-(?P<icon>[^\"]+)\"",
        re.DOTALL | re.IGNORECASE,
    )
    rows = []
    for m in pat.finditer(html):
        name = unescape(re.sub(r"<[^>]+>", " ", m.group("name")))
        name = " ".join(name.split())
        icon = m.group("icon").strip()
        rows.append((name, icon))

    with OUT_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["name", "icon"])
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()

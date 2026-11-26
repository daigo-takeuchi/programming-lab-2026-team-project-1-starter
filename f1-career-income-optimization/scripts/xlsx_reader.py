"""【教員用】xlsx ファイルを標準ライブラリ（zipfile + xml）だけで読む小さな読み取り関数

開発環境に openpyxl がないため、前処理スクリプト用に最低限の機能だけを実装した。
- 共有文字列（sharedStrings）・インライン文字列・数値を読む。数式は「計算済みの値」を読む。
- 書式・結合セル・日付は扱わない（結合セルは左上のセルにだけ値がある）。

使い方:
    from xlsx_reader import read_xlsx
    sheets = read_xlsx(path)          # {シート名: [[セルの値, ...], ...]}
"""

import re
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def _column_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _text(node):
    return "".join(t.text or "" for t in node.iter(f"{{{NS['m']}}}t"))


def read_xlsx(path):
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [_text(si) for si in root.findall("m:si", NS)]
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels.iter(f"{REL_NS}Relationship")}
        sheets = {}
        for sheet in wb.find("m:sheets", NS):
            rid = sheet.get(f"{{{NS['r']}}}id")
            target = targets[rid].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            root = ET.fromstring(z.read(target))
            rows = []
            for row in root.iter(f"{{{NS['m']}}}row"):
                values = {}
                for c in row.findall("m:c", NS):
                    kind, v = c.get("t"), c.find("m:v", NS)
                    if kind == "s" and v is not None:
                        value = shared[int(v.text)]
                    elif kind == "inlineStr":
                        value = _text(c)
                    elif v is not None:
                        value = v.text
                    else:
                        continue
                    values[_column_index(c.get("r"))] = value
                width = max(values) + 1 if values else 0
                rows.append([values.get(i, "") for i in range(width)])
            sheets[sheet.get("name")] = rows
        return sheets

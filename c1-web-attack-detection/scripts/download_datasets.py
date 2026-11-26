"""公開データの取得スクリプト（教員用）

- Loghub（OpenSSH_2k、Linux_2k）：GitHub から直接ダウンロードし、SHA-256 を確認する（合計 約 1.2MB）。
- CIC-IDS2017：登録フォームへの入力が必要なため、このスクリプトはダウンロードしない。
  手順は docs/cic_ids2017_acquisition_guide.md を参照し、教員が手動で取得する。

保存先：data/raw/loghub/（Git 管理外）

使い方（c1-web-attack-detection ディレクトリで実行する）:
    python3 scripts/download_datasets.py            # 未取得のファイルだけをダウンロードする
    python3 scripts/download_datasets.py --verify   # ダウンロードせず、チェックサムだけを確認する

注意：ダウンロードしたファイルはデータとしてだけ扱い、実行しない。
"""

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw" / "loghub"
BASE_URL = "https://raw.githubusercontent.com/logpai/loghub/master/"

# (リポジトリ内のパス, 保存するファイル名, SHA-256)
# SHA-256 は 2026-11-26 に取得したファイルの値。LICENSE はライセンス文の同梱用。
FILES = [
    ("OpenSSH/OpenSSH_2k.log", "OpenSSH_2k.log",
     "1e4912727fa88245113d41b16a0cd25ceadba7f931e1c406542885b91254264f"),
    ("OpenSSH/OpenSSH_2k.log_structured.csv", "OpenSSH_2k.log_structured.csv",
     "c0996a11545f4b94b435993760afa441a9e373f7bfc9e787afdb8e62f65acb4f"),
    ("Linux/Linux_2k.log", "Linux_2k.log",
     "b3e20bc1afe732ab1bf3ed1de4bf9c809e4194e02f7dea911d918e5342e8e173"),
    ("Linux/Linux_2k.log_structured.csv", "Linux_2k.log_structured.csv",
     "7c86d7b0ecb961a25f00d9475a154df97613b9974f31ce142a146caa2017c71e"),
    ("LICENSE", "LICENSE",          # ライセンス文（出力 CSV と一緒に配布する）
     "9ffa6ae259833cdc6e7ed8a0219fec72ef6455fb457b3c44096cb1ac1f0696d4"),
]
MAX_BYTES = 5 * 1024 * 1024   # 想定外の大きなファイルを取得しないための上限（1 ファイル 5MB）


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(url, dest):
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise RuntimeError(f"{url} が上限（{MAX_BYTES} バイト）を超えています")
    dest.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description="公開データ（Loghub）の取得")
    parser.add_argument("--verify", action="store_true", help="ダウンロードせず、チェックサムだけを確認する")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for repo_path, name, expected in FILES:
        dest = RAW_DIR / name
        if not dest.exists():
            if args.verify:
                print(f"[なし] {name}")
                ok = False
                continue
            download(BASE_URL + repo_path, dest)
            print(f"[取得] {name}（{dest.stat().st_size:,} バイト）")
        actual = sha256(dest)
        if expected is None:
            print(f"[確認] {name} SHA-256 = {actual}")
        elif actual == expected:
            print(f"[OK]   {name} のチェックサムが一致しました")
        else:
            print(f"[NG]   {name} のチェックサムが記録と異なります（配布元で更新された可能性）: {actual}")
            ok = False

    print()
    print("CIC-IDS2017 は登録フォームが必要なため、自動ではダウンロードしません。")
    print("手順：docs/cic_ids2017_acquisition_guide.md")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

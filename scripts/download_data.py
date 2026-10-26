import argparse
import json
import re
from pathlib import Path

from datasets import load_dataset

CODEFORCES = 2
LANGUAGES = {2: "cpp", 3: "python"}

INTERACTIVE = re.compile(r"\binteractive\b|\binteraction\b|flush", re.I)
MANY_ANSWERS = re.compile(
    r"print any|output any|any of them|any valid|any such|in any order"
    r"|if there are (multiple|several|many)|multiple (answers|solutions)",
    re.I,
)
FLOATING = re.compile(
    r"absolute or relative|relative or absolute|absolute error|relative error"
    r"|10\^\{?-\d|decimal places|precision",
    re.I,
)


def is_usable(row):
    if row["source"] != CODEFORCES:
        return False
    if row["input_file"].strip().lower() not in ("", "stdin"):
        return False
    if not row["public_tests"]["input"]:
        return False
    text = row["description"]
    return not (INTERACTIVE.search(text) or MANY_ANSWERS.search(text) or FLOATING.search(text))


def pick_solutions(block, count):
    picked = []
    for lang, code in zip(block["language"], block["solution"]):
        if lang in LANGUAGES:
            picked.append({"language": LANGUAGES[lang], "code": code})
        if len(picked) == count:
            break
    return picked


def time_limit_seconds(row):
    limit = row.get("time_limit")
    if not limit:
        return 2.0
    return limit["seconds"] + limit["nanos"] / 1e9


def build_problem(row):
    correct = pick_solutions(row["solutions"], 1)
    wrong = pick_solutions(row["incorrect_solutions"], 5)
    if not correct or len(wrong) < 2:
        return None

    tests = row["public_tests"]
    samples = [
        {"input": i, "output": o}
        for i, o in zip(tests["input"][:5], tests["output"][:5])
    ]
    return {
        "id": f"{row['cf_contest_id']}{row['cf_index']}",
        "name": row["name"],
        "statement": row["description"],
        "time_limit": time_limit_seconds(row),
        "memory_limit_mb": row["memory_limit_bytes"] // (1024 * 1024),
        "samples": samples,
        "correct": correct[0],
        "wrong": wrong,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="test")
    parser.add_argument("--limit", type=int, default=150)
    parser.add_argument("--out", default="data/problems")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows = load_dataset("deepmind/code_contests", split=args.split, streaming=True)
    saved = 0
    for row in rows:
        if not is_usable(row):
            continue
        problem = build_problem(row)
        if problem is None:
            continue
        (out / f"{problem['id']}.json").write_text(json.dumps(problem, indent=2))
        saved += 1
        if saved == args.limit:
            break

    print(f"saved {saved} problems to {out}")


if __name__ == "__main__":
    main()

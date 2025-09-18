from __future__ import annotations

import json as _json
import os

from sup.cli import run_source


def _dq(s: object) -> str:
    # double-quoted, JSON-escaped string literal for SUP
    return _json.dumps(str(s))


def test_fs_env_subprocess_and_regex(tmp_path) -> None:
    d = str(tmp_path)
    os.makedirs(d, exist_ok=True)
    code = (
        f"""
sup
  set wd to cwd
  set path to join path of {_dq(d)} and "a.txt"
  write file of path and "hello"
  print exists of path
  print regex replace of "h" and read file of path and "H"
  set res to subprocess run of "echo hi"
  print contains of get "out" from res and "hi"
bye
"""
    ).strip()
    out = run_source(code)
    lines = out.splitlines()
    assert lines[0] in {"True", "true"}
    assert lines[1].startswith("Hello")
    assert lines[2] in {"True", "true"}


def test_csv_zip_sqlite(tmp_path) -> None:
    d = str(tmp_path)
    os.makedirs(d, exist_ok=True)
    csvp = os.path.join(d, "t.csv")
    zipp = os.path.join(d, "t.zip")
    dbp = os.path.join(d, "t.db")
    code = (
        f"""
sup
  make list of "a", "b"
  set row1 to list
  make list of "c", "d"
  set row2 to list
  make list of row1, row2
  csv write of {_dq(csvp)} and list
  set rows to csv read of {_dq(csvp)}
  print length of rows
  zip create of {_dq(zipp)} and make list of {_dq(csvp)}
  zip extract of {_dq(zipp)} and {_dq(d)}
  set _ to sqlite exec of {_dq(dbp)} and "create table x(n int)" and make list
  set _ to sqlite exec of {_dq(dbp)} and "insert into x(n) values (?)" and make list of 3
  set r to sqlite query of {_dq(dbp)} and "select n from x"
  print length of r
bye
"""
    ).strip()
    out = run_source(code)
    a, b = out.splitlines()
    assert int(float(a)) == 2
    assert int(float(b)) == 1



#!/usr/bin/python3
"""run_tests.py — RUN pystdf's own test suite and print a parseable summary.

Invoked via the `/mayhem/pystdf-tests` ELF launcher (NOT directly), so the verify-repo sabotage
oracle can neuter the launcher and prove the test oracle is behavioral.

pystdf ships its tests as `tests/test_*.py` (test_IO.py, test_BinSummarizer.py) — known-answer
cases asserting EXACT parser output: field decoding (U1/U2/I1, Cn strings, arrays), record-header
parsing, EOF / end-of-record exception behaviour, field-parser composition, and BinSummarizer
aggregation. A no-op / "exit(0)" / behaviour-altering patch to pystdf cannot pass it.

It runs the real suite, writes a JUnit XML, parses the counts, and prints one line:

    RUNTESTS tests=<n> passed=<p> failed=<f> skipped=<s>

Exit 0 iff failed == 0. mayhem/test.sh parses that line into a CTRF report.
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

import pytest

SRC = os.environ.get("SRC", "/mayhem")
XML = "/tmp/pystdf-junit.xml"
TESTS_DIR = "tests"


def main() -> int:
    os.chdir(SRC)
    pytest.main(["-q", "-p", "no:cacheprovider", TESTS_DIR, "--junitxml", XML])

    root = ET.parse(XML).getroot()
    suites = root.findall("testsuite") or ([root] if root.tag == "testsuite" else [])
    if not suites:
        print("RUNTESTS tests=0 passed=0 failed=1 skipped=0")
        return 1

    tests = failed = skipped = 0
    for s in suites:
        tests += int(s.get("tests", 0))
        failed += int(s.get("failures", 0)) + int(s.get("errors", 0))
        skipped += int(s.get("skipped", 0))
    passed = tests - failed - skipped

    print(f"RUNTESTS tests={tests} passed={passed} failed={failed} skipped={skipped}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

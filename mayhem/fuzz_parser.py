#! /usr/bin/env python3
# Atheris harness for pystdf: fuzzes the STDF v4 stream parser (pystdf.IO.Parser) and the
# DataFrame importer (pystdf.Importer.STDF2DataFrame). Preserved from the original Mayhem Heroes
# integration (target parser-fuzz). Runs under Atheris/libFuzzer; the /mayhem/fuzz-parser ELF
# launcher exec()s `python3 <this>` so Mayhem has an ELF entry point (see mayhem/launcher.c).
import os
import sys

import atheris

# Make the sibling fuzz_helpers importable regardless of CWD (the launcher exec()s us with an
# absolute path; sys.path[0] is this dir, but be explicit for the fork-mode re-exec children too).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Errors that are legitimate "reject this input" signals from the parser, not defects.
from pystdf.Types import EofException, EndOfRecordException, InitialSequenceException
from struct import error

import fuzz_helpers

# Scope instrumentation to the pystdf package only (Atheris fork-mode: a bare instrument-all
# balloons startup per fork child; scoping keeps re-exec children fast and coverage on-target).
with atheris.instrument_imports(include=['pystdf']):
    import pystdf.Importer
    import pystdf.IO


def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        if fdp.ConsumeBool():
            with fdp.ConsumeTemporaryFile(suffix='.stdf', all_data=True, as_bytes=True) as name:
                pystdf.Importer.STDF2DataFrame(name)
        else:
            with fdp.ConsumeMemoryFile(all_data=True, as_bytes=True) as f:
                pystdf.IO.Parser(inp=f)
    except (EofException, EndOfRecordException, InitialSequenceException, error, UnicodeDecodeError):
        return -1


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()

#! /usr/bin/env python3
import atheris
import sys

# Errors
from pystdf.Types import EofException, EndOfRecordException, InitialSequenceException
from struct import error

import fuzz_helpers


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

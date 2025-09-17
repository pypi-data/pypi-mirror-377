# skote/cli/generate_cli.py
# Lightweight, non-intrusive wrapper for skote.runtime.generate
# - Defers heavy imports so --help/--version works in clean envs
# - Prints clear guidance if optional deps (e.g., PyTorch) are missing
# - Never modifies your core implementation

from __future__ import annotations
import sys
import argparse

def _print_wrapper_help(parser: argparse.ArgumentParser) -> None:
    print(parser.format_help())
    print("\n[Skotergy] This is a lightweight wrapper for skote.runtime.generate.")
    print("If you hit import errors, install optional runtime deps, e.g.:")
    print("  pip install 'skotergy[accel]'  # or install a matching PyTorch build")

def main(argv=None) -> int:
    argv = list(argv) if argv is not None else sys.argv[1:]

    # Minimal wrapper-level flags; everything else is passed through
    parser = argparse.ArgumentParser(
        prog="skote-generate",
        description="Skotergy Generate (safe wrapper: deferred imports, graceful help)"
    )
    parser.add_argument("--version", action="store_true", help="Print package version and exit")

    help_requested = ("-h" in argv) or ("--help" in argv)
    args, passthrough = parser.parse_known_args(argv)

    # Handle wrapper-level --version without importing heavy modules
    if args.version:
        try:
            from importlib.metadata import version
            print("skotergy", version("skotergy"))
        except Exception:
            print("skotergy (version unknown)")
        return 0

    # If user asked for help, try to show the real CLI help if available;
    # otherwise fall back to wrapper help without failing the process.
    if help_requested:
        try:
            from skote.runtime import generate as real  # lazy import
            saved = list(sys.argv)
            try:
                # Ask the real parser to print its own help
                sys.argv = [saved[0]] + passthrough + ["--help"]
                real.parse_args()  # will print help and SystemExit(0)
            except SystemExit as se:
                return int(getattr(se, "code", 0) or 0)
            except Exception:
                _print_wrapper_help(parser)
                return 0
            finally:
                sys.argv = saved
        except Exception:
            _print_wrapper_help(parser)
            return 0

    # Normal execution path: delegate to your real implementation.
    try:
        from skote.runtime import generate as real  # lazy import (may need torch, etc.)
    except Exception as e:
        sys.stderr.write("[skotergy] Unable to import skote.runtime.generate: " + str(e) + "\n")
        sys.stderr.write("Hint: install optional runtime deps (e.g., PyTorch) or use --help.\n")
        return 2

    try:
        # Your real main() parses sys.argv itself; we just hand over control.
        return int(real.main())
    except SystemExit as se:
        return int(getattr(se, "code", 0) or 0)
    except Exception as e:
        sys.stderr.write("[skotergy] skote.runtime.generate.main() raised: " + repr(e) + "\n")
        return 3

if __name__ == "__main__":
    raise SystemExit(main())

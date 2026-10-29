"""Allow `python -m pymart` as an alias of `python -m pymart.cli`."""

from pymart.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

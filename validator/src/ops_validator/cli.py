"""CLI entry point for the OPS schema validator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    """Run OPS schema validation from the command line."""
    parser = argparse.ArgumentParser(
        prog="ops-validate",
        description="Validate OPS data artifacts against the OPS Data Standard v0.1.0",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to the artifact to validate (e.g., a .zarr plate store)",
    )
    parser.add_argument(
        "--type",
        choices=["zarr"],
        default="zarr",
        help="Artifact type to validate (default: zarr)",
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"ERROR: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)

    if args.type == "zarr":
        from ops_validator.validators.zarr_images import ZarrImagesValidator

        validator = ZarrImagesValidator(path=args.path)
        validator.validate()
        print(validator.report())
        sys.exit(0 if validator.is_valid else 1)


if __name__ == "__main__":
    main()

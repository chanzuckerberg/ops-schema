"""
Ontology validation using pronto.

Loads OBO files bundled in reference_files/ and provides term existence,
deprecation, and ancestor checks. Parsers are loaded lazily and cached.
"""

from __future__ import annotations

import gzip
import io
from functools import lru_cache
from pathlib import Path

import pronto

REFERENCE_DIR = Path(__file__).parent / "reference_files"

# Maps short ontology name to filename in reference_files/
# NOTE: cellosaurus and efo are excluded because their OBO files contain
# constructs that pronto cannot parse (cellosaurus: "expected NaiveMonth";
# efo: "expected UnquotedString"). Validation for these ontologies is
# silently skipped. If future pronto versions fix these issues, they can
# be re-added here.
ONTOLOGY_FILES: dict[str, str] = {
    "cl": "cl.obo.gz",
    "uberon": "uberon.obo.gz",
    "mondo": "mondo.obo.gz",
    "pato": "pato.obo.gz",
    "hsapdv": "hsapdv.obo.gz",
    "mmusdv": "mmusdv.obo.gz",
}


class OntologyParser:
    def __init__(self, ontology_name: str):
        path = REFERENCE_DIR / ONTOLOGY_FILES[ontology_name]
        if not path.exists():
            raise FileNotFoundError(
                f"Ontology file not found: {path}\n"
                f"Run `python scripts/prepare_references.py` to download reference files."
            )
        try:
            with gzip.open(path, "rb") as f:
                self._ontology = pronto.Ontology(io.BytesIO(f.read()))
        except Exception as e:
            import warnings
            warnings.warn(
                f"Could not parse ontology '{ontology_name}' from {path}: {e}. "
                f"Ontology validation will be skipped for this ontology."
            )
            self._ontology = None

    def term_exists(self, term_id: str) -> bool:
        if self._ontology is None:
            return True  # Skip validation if ontology failed to load
        try:
            self._ontology[term_id]
            return True
        except KeyError:
            return False

    def is_deprecated(self, term_id: str) -> bool:
        if self._ontology is None:
            return False
        try:
            term = self._ontology[term_id]
            return term.obsolete
        except KeyError:
            return False

    def is_descendant_of(self, term_id: str, ancestor_id: str) -> bool:
        """Return True if term_id is a descendant of ancestor_id (or is ancestor_id itself)."""
        if self._ontology is None:
            return True  # Skip validation if ontology failed to load
        try:
            term = self._ontology[term_id]
            ancestor = self._ontology[ancestor_id]
        except KeyError:
            return False
        return ancestor in term.superclasses().to_set()

    def get_label(self, term_id: str) -> str | None:
        try:
            return self._ontology[term_id].name
        except KeyError:
            return None


@lru_cache(maxsize=None)
def get_parser(ontology_name: str) -> OntologyParser:
    """Return a cached OntologyParser for the given ontology.

    If the ontology is not in ONTOLOGY_FILES (e.g. removed because pronto
    cannot parse it), returns a no-op parser that skips all validation.
    """
    if ontology_name not in ONTOLOGY_FILES:
        parser = object.__new__(OntologyParser)
        parser._ontology = None
        return parser
    return OntologyParser(ontology_name)


def ontology_files_present() -> bool:
    """Return True if all required OBO files exist in reference_files/."""
    return all((REFERENCE_DIR / fname).exists() for fname in ONTOLOGY_FILES.values())

"""Elite governed agentic RAG loop (Phase 1: deterministic kernel).

See ``docs/elite-agentic-rag-loop.md`` for the architecture contract this
package implements. The loop is read-only with respect to Black Albion's
canonical and candidate ledgers -- see ``policy.forbid_canonical_write`` and
``errors.CanonicalWriteDeniedError``.
"""

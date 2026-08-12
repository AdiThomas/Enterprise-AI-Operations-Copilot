# Ingestion

Phase 2 work. Put the synthetic company profile and documentation source files
in `docs/`, then build `ingest.py` to chunk, embed, and upsert them into the
`document_chunks` table (pgvector) per Section 5 of the project overview.

**Live-demo docs:** `01-vpn-setup.md` and `02-mfa-account-reset.md` map
directly to the two demo scenarios in the project overview (Scenario A: VPN
setup, Scenario B: MFA reset). `04-network-outage-escalation.md` is the third
hand-edited doc (outages are a named 1-hour-SLA category). These three are
held to a higher editorial bar than the rest of the corpus — treat them as
the ones retrieval/answer quality will be judged against.

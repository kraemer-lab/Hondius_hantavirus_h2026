"""
CLI entry point: run the claim-verification pipeline end-to-end on the outbreak
corpus and report, per news article, whether its stated case count is
consistent with / overstates / understates the ground-truth line list as of the
article's publish date.

    python spiralwatch/cli/verify.py [--data-dir DIR] [--graph-out FILE]
                                     [--show N] [--verdict VERDICT]

This wires together the three layers that already exist in the repo:
    ground_truth  (ingest CSV/JSON -> Event/Claim/Source dataclasses)
    narrative_graph (heuristic claim->event "reports_on" edges)
    analytics/claim_verification (directional verdict per claim)
It performs no network access and reads only the local data/ files.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

# The existing modules import as top-level packages (e.g. `ground_truth.schema`),
# so the package root is spiralwatch/ itself — put it on the path regardless of CWD.
SPIRALWATCH_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SPIRALWATCH_ROOT.parent
sys.path.insert(0, str(SPIRALWATCH_ROOT))

from analytics.claim_verification import ClaimVerification, verify_claims  # noqa: E402
from ground_truth.ingest_articles import load_claims  # noqa: E402
from ground_truth.ingest_linelist import load_events  # noqa: E402
from ground_truth.ingest_sources import load_sources  # noqa: E402
from ground_truth.schema import Claim  # noqa: E402
from narrative_graph.linker import build_graph  # noqa: E402

VERDICT_ORDER = ["overstated", "understated", "unlinked", "unverifiable", "consistent"]


def _resolve_paths(data_dir: Path) -> tuple[Path, Path, Path, Path]:
    linelist = data_dir / "linelist" / "2026_hantavirus.csv"
    news = data_dir / "news sources"
    sources = news / "mc-onlinenews-mediacloud-20260507155422-content.csv"
    articles = news / "hantavirus_articles.json"
    results = news / "hantavirus_results.json"
    return linelist, sources, articles, results


def run(data_dir: Path, graph_out: Path | None, show: int, only_verdict: str | None) -> int:
    linelist, sources_path, articles_path, results_path = _resolve_paths(data_dir)

    sources = load_sources(sources_path)
    events = load_events(linelist)
    claims = load_claims(articles_path, results_path, sources=sources)
    print(f"loaded: {len(events)} cases  {len(claims)} claims  {len(sources)} sources")

    graph = build_graph(events, claims)
    print(f"graph:  {len(graph.nodes)} nodes  {len(graph.edges)} edges")

    verifications = verify_claims(claims, events, graph)
    claims_by_id: dict[str, Claim] = {c.id: c for c in claims}

    counts = Counter(v.verdict for v in verifications)
    print("\nverdicts")
    total = len(verifications) or 1
    for verdict in VERDICT_ORDER:
        n = counts.get(verdict, 0)
        print(f"  {verdict:12} {n:5}  {100 * n / total:5.1f}%")

    _print_samples(verifications, claims_by_id, show, only_verdict)

    if graph_out is not None:
        graph.to_json(graph_out)
        print(f"\nwrote graph -> {graph_out}")

    return 0


def _print_samples(
    verifications: list[ClaimVerification],
    claims_by_id: dict[str, Claim],
    show: int,
    only_verdict: str | None,
) -> None:
    if show <= 0:
        return
    wanted = (
        {only_verdict}
        if only_verdict
        else {"overstated", "understated", "consistent"}
    )
    header = only_verdict or "count-comparable"
    print(f"\nsample verdicts ({header}), strongest match first")
    rows = [
        v
        for v in verifications
        if v.verdict in wanted and v.known_total_as_of_publish is not None
    ]
    rows.sort(key=lambda v: -v.best_match_weight)
    for v in rows[:show]:
        title = (claims_by_id[v.claim_id].title or "").strip()[:66]
        print(
            f"  [{v.verdict:11}] reported={v.reported_total!s:>4} "
            f"known={v.known_total_as_of_publish!s:>4} w={v.best_match_weight:.2f}  {title}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=REPO_ROOT / "data",
        help="Root of the data/ directory (default: repo data/).",
    )
    parser.add_argument(
        "--graph-out",
        type=Path,
        default=None,
        help="If set, write the narrative graph as JSON to this path.",
    )
    parser.add_argument("--show", type=int, default=12, help="How many sample verdicts to print.")
    parser.add_argument(
        "--verdict",
        default=None,
        choices=VERDICT_ORDER,
        help="Restrict the sample list to a single verdict.",
    )
    args = parser.parse_args(argv)
    return run(args.data_dir, args.graph_out, args.show, args.verdict)


if __name__ == "__main__":
    raise SystemExit(main())

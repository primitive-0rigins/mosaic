"""Static HTML reports for Mosaic memory stores."""

from html import escape
from pathlib import Path

from mosaic.hypergraph.graph import HyperGraph


def write_html_report(graph: HyperGraph, output_path: str | Path) -> Path:
    """Write a static index page for the current memory graph."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html_report(graph, path.parent), encoding="utf-8")
    return path


def render_html_report(graph: HyperGraph, report_dir: Path) -> str:
    nodes = graph.nodes()
    edges = graph.edges()
    summary = graph.summary()
    tile_cards = "\n".join(
        _render_tile_card(tile_id, metadata, report_dir)
        for tile_id, metadata in sorted(nodes.items(), key=lambda item: item[0])
    )
    edge_items = "\n".join(_render_edge(edge) for edge in edges)
    if not edge_items:
        edge_items = "<p class=\"empty\">No hyperedges yet.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mosaic Memory Report</title>
  <style>
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f7f9;
      color: #191c20;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    h1, h2, p {{
      margin-top: 0;
    }}
    .stats {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin: 20px 0 28px;
    }}
    .stat {{
      border: 1px solid #d6dde8;
      border-radius: 8px;
      padding: 10px 14px;
      background: #ffffff;
    }}
    .label {{
      display: block;
      color: #586372;
      font-size: 12px;
      text-transform: uppercase;
    }}
    .value {{
      display: block;
      font-size: 22px;
      font-weight: 650;
    }}
    .tiles {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 14px;
    }}
    .tile, .edge {{
      border: 1px solid #d6dde8;
      border-radius: 8px;
      background: #ffffff;
      overflow: hidden;
    }}
    .tile img {{
      width: 100%;
      aspect-ratio: 1;
      object-fit: contain;
      background: #ffffff;
      border-bottom: 1px solid #d6dde8;
    }}
    .tile dl, .edge {{
      padding: 12px;
    }}
    dt {{
      color: #586372;
      font-size: 12px;
    }}
    dd {{
      margin: 0 0 8px;
      overflow-wrap: anywhere;
    }}
    .edges {{
      display: grid;
      gap: 12px;
      margin-bottom: 32px;
    }}
    .empty {{
      color: #586372;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Mosaic Memory Report</h1>
    <section class="stats" aria-label="Memory summary">
      <div class="stat"><span class="label">Tiles</span><span class="value">{summary["nodes"]}</span></div>
      <div class="stat"><span class="label">Hyperedges</span><span class="value">{summary["edges"]}</span></div>
      <div class="stat"><span class="label">Avg degree</span><span class="value">{summary["avg_degree"]:.2f}</span></div>
    </section>
    <h2>Hyperedges</h2>
    <section class="edges">{edge_items}</section>
    <h2>Tiles</h2>
    <section class="tiles">{tile_cards}</section>
  </main>
</body>
</html>
"""


def _render_tile_card(tile_id: str, metadata: dict, report_dir: Path) -> str:
    tile_path = metadata.get("tile_path", "")
    image_src = _relative_path(tile_path, report_dir) if tile_path else ""
    image = f"<img src=\"{escape(image_src)}\" alt=\"{escape(tile_id)}\">" if image_src else ""
    return f"""<article class="tile">
  {image}
  <dl>
    <dt>Tile</dt><dd>{escape(tile_id)}</dd>
    <dt>Source</dt><dd>{escape(Path(metadata["source"]).name)}</dd>
    <dt>Page</dt><dd>{metadata["page"]}</dd>
    <dt>Index</dt><dd>{metadata["index"]}</dd>
  </dl>
</article>"""


def _render_edge(edge) -> str:
    claim = f"<dt>Claim</dt><dd>{escape(edge.claim)}</dd>" if edge.claim else ""
    return f"""<article class="edge">
  <dl>
    <dt>Edge</dt><dd>{escape(edge.edge_id)}</dd>
    <dt>Label</dt><dd>{escape(edge.label)}</dd>
    <dt>Confidence</dt><dd>{edge.confidence:.2f}</dd>
    <dt>Tiles</dt><dd>{escape(", ".join(edge.tile_ids))}</dd>
    {claim}
  </dl>
</article>"""


def _relative_path(path: str, start: Path) -> str:
    try:
        return Path(path).resolve().relative_to(start.resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix()

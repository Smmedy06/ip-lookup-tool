# reporting/exporter.py
import json
import csv
from typing import List, Dict, Any

def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

class ReportExporter:
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
        self.flat_results = [_flatten_dict(res) for res in self.results]

    def to_json(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)

    def to_csv(self, filename: str):
        if not self.flat_results: return
        headers = sorted(list(set(key for d in self.flat_results for key in d.keys())))
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.flat_results)

    def to_html(self, filename: str):
        if not self.results: return
        headers = sorted(list(set(key for d in self.flat_results for key in d.keys())))
        html = f"""
        <html><head><title>IP Analysis Report</title><style>
        body {{ font-family: sans-serif; margin: 2em; }} table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; text-align: left; padding: 8px; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }} th {{ background-color: #4CAF50; color: white; }}
        </style></head><body><h1>IP Analysis Report</h1><table><tr>
        {''.join(f"<th>{h.replace('_', ' ').title()}</th>" for h in headers)}</tr>
        """
        for row in self.flat_results:
            row_cells = ''.join([f'<td>{row.get(h, "N/A")}</td>' for h in headers])
            html += f"<tr>{row_cells}</tr>"

        html += "</table></body></html>"
        with open(filename, 'w', encoding='utf-8') as f: f.write(html)
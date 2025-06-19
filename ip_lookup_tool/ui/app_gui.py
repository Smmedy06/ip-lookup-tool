# ui/app_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import asyncio
import webbrowser  # <--- IMPORTED FOR OPENING LINKS

from core.ip_utils import expand_targets
from core.orchestrator import IPOrchestrator
from reporting.exporter import ReportExporter

class IPToolGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced IP Lookup Tool")
        self.master.geometry("950x600")
        
        self.results_queue = queue.Queue()
        self.last_results = []
        self.map_links = {}  # <--- NEW: Dictionary to store map links by row ID

        style = ttk.Style(self.master)
        style.theme_use('clam')
        
        self._create_widgets()
        self.master.after(100, self._process_queue)

    def _create_widgets(self):
        # --- Main Layout ---
        paned_window = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = ttk.Frame(paned_window, width=250)
        paned_window.add(left_frame, weight=1)
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=3)

        # --- Left Pane: Input and Controls ---
        ttk.Label(left_frame, text="Enter IPs/CIDRs (one per line):").pack(anchor="w", padx=5, pady=(0, 5))
        self.ip_input = scrolledtext.ScrolledText(left_frame, height=10, width=30)
        self.ip_input.pack(fill=tk.BOTH, expand=True, padx=5)
        self.no_threat_var = tk.BooleanVar()
        ttk.Checkbutton(left_frame, text="Disable Threat Intelligence", variable=self.no_threat_var).pack(anchor="w", padx=5, pady=5)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10, padx=5)
        self.scan_btn = ttk.Button(btn_frame, text="Start Scan", command=self._start_scan)
        self.scan_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.save_btn = ttk.Button(btn_frame, text="Save Report", command=self._save_report, state='disabled')
        self.save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.status_var = tk.StringVar(value="Status: Idle")
        ttk.Label(left_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w").pack(side=tk.BOTTOM, fill=tk.X)
        
        # --- Right Pane: Results Treeview ---
        columns = ("ip", "country", "city", "map_link", "org", "threat_score", "reports")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        headings = {"ip": "IP Address", "country": "Country", "city": "City", "map_link": "Map", "org": "Organization", "threat_score": "Threat Score", "reports": "Reports"}
        widths = {"ip": 120, "country": 100, "city": 120, "map_link": 50, "org": 200, "threat_score": 80, "reports": 60}
        
        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda _col=col: self._sort_column(_col, False))
            self.tree.column(col, width=widths[col], anchor='center' if col in ['map_link', 'threat_score', 'reports'] else 'w')

        # NEW: Configure tag for hyperlink style
        self.tree.tag_configure('hyperlink', foreground='blue', font=('Calibri', 10, 'underline'))
        # NEW: Bind click event to the treeview
        self.tree.bind('<Button-1>', self._on_tree_click)

        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # --- NEW: Method to handle clicks on the tree ---
    def _on_tree_click(self, event):
        """Handle single click events on the treeview, opening links if necessary."""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        column_id = self.tree.identify_column(event.x)
        # The 'map_link' is the 4th column, so its ID is #4
        if column_id == '#4':
            row_id = self.tree.identify_row(event.y)
            if row_id in self.map_links:
                webbrowser.open_new_tab(self.map_links[row_id])

    def _start_scan(self):
        targets = [t.strip() for t in self.ip_input.get("1.0", tk.END).strip().split('\n') if t.strip()]
        if not targets:
            messagebox.showwarning("Input Error", "Please enter at least one IP address or CIDR.")
            return
        
        self.scan_btn['state'], self.save_btn['state'] = 'disabled', 'disabled'
        self.tree.delete(*self.tree.get_children())
        self.map_links.clear() # <--- NEW: Clear old links
        self.status_var.set("Status: Expanding targets...")
        
        expanded_ips = expand_targets(targets)
        if not expanded_ips:
            messagebox.showwarning("Input Error", "No valid IP addresses found.")
            self.scan_btn['state'], self.status_var.set('normal', "Status: Idle")
            return
        
        self.status_var.set(f"Status: Scanning {len(expanded_ips)} IPs...")
        threading.Thread(target=self._run_scan_thread, args=(expanded_ips, self.no_threat_var.get()), daemon=True).start()

    def _run_scan_thread(self, ips, no_threat):
        try:
            results = asyncio.run(IPOrchestrator(ips, no_threat=no_threat).run())
            self.results_queue.put(results)
        except Exception as e:
            self.results_queue.put(f"ERROR: {e}")

    def _process_queue(self):
        try:
            result = self.results_queue.get_nowait()
            if isinstance(result, str) and result.startswith("ERROR:"):
                messagebox.showerror("Scan Error", result)
                self.status_var.set("Status: Error during scan.")
            else:
                self.last_results = result
                self._populate_treeview(result)
                self.status_var.set(f"Status: Scan complete. {len(result)} results.")
                self.save_btn['state'] = 'normal'
            self.scan_btn['state'] = 'normal'
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self._process_queue)

    def _populate_treeview(self, results):
        for res in results:
            geo, threat = res.get("geolocation", {}), res.get("threat_intel", {})
            tags = () # Default: no tags
            
            if "error" in res:
                vals = (res["ip"], "Private IP", "N/A", "", "N/A", "N/A", "N/A")
            else:
                loc = geo.get("loc")
                map_url = f"https://www.google.com/maps/search/?api=1&query={loc}" if loc else None
                map_text = "View" if map_url else ""
                
                score = threat.get("abuse_confidence_score", "N/A") if not self.no_threat_var.get() else "Disabled"
                reports = threat.get("total_reports", "N/A") if not self.no_threat_var.get() else "Disabled"
                vals = (res["ip"], geo.get("country", "N/A"), geo.get("city", "N/A"), map_text, geo.get("org", "N/A"), score, reports)

            # Insert row and get its ID
            row_id = self.tree.insert("", "end", values=vals, tags=tags)
            
            # If there's a map URL, store it and apply the hyperlink tag
            if map_url:
                self.map_links[row_id] = map_url
                self.tree.item(row_id, tags=('hyperlink',))
                
    def _sort_column(self, col, reverse):
        """Sort treeview contents when a column is clicked."""
        try:
            data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
            # Attempt to sort numerically if possible, otherwise sort as string
            try:
                data.sort(key=lambda t: int(t[0]), reverse=reverse)
            except ValueError:
                data.sort(reverse=reverse)
            
            for index, (val, child) in enumerate(data):
                self.tree.move(child, '', index)
            
            # Reverse sort direction for next click
            self.tree.heading(col, command=lambda: self._sort_column(col, not reverse))
        except tk.TclError:
            pass # Ignore errors from empty columns like 'map_link'

    def _save_report(self):
        # This function remains the same
        if not self.last_results: return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json"), ("CSV", "*.csv"), ("HTML", "*.html")])
        if not path: return
        try:
            exporter = ReportExporter(self.last_results)
            if path.endswith('.json'): exporter.to_json(path)
            elif path.endswith('.csv'): exporter.to_csv(path)
            elif path.endswith('.html'): exporter.to_html(path)
            else: messagebox.showerror("Format Error", "Unsupported extension."); return
            messagebox.showinfo("Success", f"Report saved to {path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save report:\n{e}")
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter import ttk, messagebox

plt.ion()

AGENTS = ["depth", "noise", "dynamic"]
METRICS_DIR = os.path.join("data", "metrics")

class MetricsVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Metrics Visualizer")
        self.root.geometry("800x600")

        self.selected_agent = tk.StringVar(value=AGENTS[0])

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        self.setup_single_tab(benchmark=False)
        self.setup_compare_tab(benchmark=False)
        self.setup_single_tab(benchmark=True)
        self.setup_compare_tab(benchmark=True)

    def setup_single_tab(self, benchmark):
        tab = ttk.Frame(self.tabs)
        label = "Single Agent (Benchmarks)" if benchmark else "Single Agent"
        self.tabs.add(tab, text=label)

        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="x")

        ttk.Label(frame, text="Select Agent:").grid(row=0, column=0, sticky="w")
        agent_menu = ttk.OptionMenu(frame, self.selected_agent, AGENTS[0], *AGENTS)
        agent_menu.grid(row=0, column=1, sticky="w")

        ttk.Button(frame, text="Plot: Path Length vs Depth/Noise",
                   command=lambda: self.plot_path_vs_param(benchmark)).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(frame, text="Plot: Success Rate",
                   command=lambda: self.plot_success_rate(benchmark)).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(frame, text="Plot: Nodes Explored",
                   command=lambda: self.plot_nodes_explored(benchmark)).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(frame, text="Export All Plots to PDF",
                   command=lambda: self.export_all_plots_pdf(benchmark)).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

    def setup_compare_tab(self, benchmark):
        tab = ttk.Frame(self.tabs)
        label = "Compare Agents (Benchmarks)" if benchmark else "Compare Agents"
        self.tabs.add(tab, text=label)

        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="x")

        ttk.Button(frame, text="Compare Path Lengths",
                   command=lambda: self.compare_plot("Path Length", benchmark)).pack(fill="x", pady=10)

        ttk.Button(frame, text="Compare Success Rates",
                   command=lambda: self.compare_plot("Success_Bool", benchmark)).pack(fill="x", pady=10)

        ttk.Button(frame, text="Compare Nodes Explored",
                   command=lambda: self.compare_plot("Nodes Explored", benchmark)).pack(fill="x", pady=10)

    def load_all_data(self, agent, benchmark=False):
        folder = os.path.join(METRICS_DIR, agent, "benchmark_data" if benchmark else "")
        archive_folder = os.path.join(folder, "archive")

        all_files = []
        if os.path.exists(folder):
            all_files.extend([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".csv")])
        if os.path.exists(archive_folder):
            all_files.extend([os.path.join(archive_folder, f) for f in os.listdir(archive_folder) if f.endswith(".csv")])

        dfs = []
        for file in all_files:
            df = pd.read_csv(file)
            df["_source_file"] = file
            dfs.append(df)

        if not dfs:
            return pd.DataFrame()

        df = pd.concat(dfs, ignore_index=True)
        df.insert(0, "Run", range(1, len(df)+1))
        df["Success_Bool"] = df["Success"] == "Yes"
        return df

    def save_and_show_plot(self, agent, title, filename, benchmark):
        plt.title(title)
        plt.legend(title="Agent")
        plt.grid(True)
        plt.tight_layout()
        subdir = "benchmark_data/graphs" if benchmark else "graphs"
        save_path = os.path.join(METRICS_DIR, agent, subdir)
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, filename))
        plt.show()

    def plot_path_vs_param(self, benchmark):
        agent = self.selected_agent.get()
        df = self.load_all_data(agent, benchmark)
        if df.empty:
            messagebox.showerror("No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Path Length", errorbar="sd", label=agent.capitalize())
        self.save_and_show_plot(agent, f"Path Length vs {x_col}", f"path_vs_{x_col.lower()}.png", benchmark)

    def plot_success_rate(self, benchmark):
        agent = self.selected_agent.get()
        df = self.load_all_data(agent, benchmark)
        if df.empty:
            messagebox.showerror("No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Success_Bool", errorbar="sd", label=agent.capitalize())
        plt.ylabel("Success Rate")
        self.save_and_show_plot(agent, f"Success Rate vs {x_col}", f"success_vs_{x_col.lower()}.png", benchmark)

    def plot_nodes_explored(self, benchmark):
        agent = self.selected_agent.get()
        df = self.load_all_data(agent, benchmark)
        if df.empty:
            messagebox.showerror("No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Nodes Explored", errorbar="sd", label=agent.capitalize())
        self.save_and_show_plot(agent, f"Nodes Explored vs {x_col}", f"nodes_vs_{x_col.lower()}.png", benchmark)

    def compare_plot(self, metric, benchmark):
        plt.figure(figsize=(9, 6))
        for agent in AGENTS:
            df = self.load_all_data(agent, benchmark)
            if df.empty: continue
            x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
            sns.lineplot(data=df, x=x_col, y=metric, errorbar="sd", label=agent.capitalize())
        label = metric if metric != "Success_Bool" else "Success Rate"
        if metric == "Success_Bool":
            plt.ylabel("Success Rate")
        self.save_and_show_plot("compare", f"{label} Comparison", f"compare_{metric.lower()}.png", benchmark)

    def export_all_plots_pdf(self, benchmark):
        agent = self.selected_agent.get()
        df = self.load_all_data(agent, benchmark)
        if df.empty:
            messagebox.showerror("No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
        pdf_path = os.path.join(METRICS_DIR, agent, "benchmark_data" if benchmark else "", "graphs", "summary_report.pdf")
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        with PdfPages(pdf_path) as pdf:
            for title, y_col in [
                (f"Path Length vs {x_col}", "Path Length"),
                (f"Success Rate vs {x_col}", "Success_Bool"),
                (f"Nodes Explored vs {x_col}", "Nodes Explored")
            ]:
                plt.figure(figsize=(8, 5))
                if y_col == "Success_Bool":
                    plt.ylabel("Success Rate")
                sns.lineplot(data=df, x=x_col, y=y_col, errorbar="sd", label=agent.capitalize())
                plt.title(title)
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                pdf.savefig()
                plt.close()

        messagebox.showinfo("Export Complete", f"Plots saved to {pdf_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MetricsVisualizer(root)
    root.mainloop()

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import subprocess
import platform
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk
from tkinter import ttk, messagebox
import config

# Enable interactive plotting
plt.ion()

AGENTS = ["depth", "noise", "dynamic"]


class MetricsVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Metrics Visualiser")
        self.root.geometry("800x600")

        self.selected_agent = tk.StringVar(value=AGENTS[0])
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        # Add tabs for both regular and benchmark data
        self.setup_single_tab(is_benchmark=False)
        self.setup_compare_tab(is_benchmark=False)
        self.setup_single_tab(is_benchmark=True)
        self.setup_compare_tab(is_benchmark=True)

    def setup_single_tab(self, is_benchmark):
        """
        Adds a tab to explore metrics for a single agent.
        """
        tab = ttk.Frame(self.tabs)
        label = "Single Agent (Benchmarks)" if is_benchmark else "Single Agent"
        self.tabs.add(tab, text=label)

        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="x")

        ttk.Label(frame, text="Select Agent:").grid(
            row=0, column=0, sticky="w")
        agent_menu = ttk.OptionMenu(
            frame, self.selected_agent, AGENTS[0], *AGENTS)
        agent_menu.grid(row=0, column=1, sticky="w")

        # Graphing options
        ttk.Button(frame, text="Plot: Path Length vs Depth/Noise",
                   command=lambda: self.plot_path_vs_param(is_benchmark)).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(frame, text="Plot: Success Rate",
                   command=lambda: self.plot_success_rate(is_benchmark)).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(frame, text="Plot: Nodes Explored",
                   command=lambda: self.plot_nodes_explored(is_benchmark)).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(frame, text="Export All Plots to PDF",
                   command=lambda: self.export_all_plots_pdf(is_benchmark)).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Button(frame, text="Open PDF Report",
                   command=lambda: self.open_pdf_report(is_benchmark)).grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

    def setup_compare_tab(self, is_benchmark):
        """
        Adds a tab to compare results across all agents.
        """
        tab = ttk.Frame(self.tabs)
        label = "Compare Agents (Benchmarks)" if is_benchmark else "Compare Agents"
        self.tabs.add(tab, text=label)

        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="x")

        ttk.Button(frame, text="Compare Path Lengths",
                   command=lambda: self.compare_plot("Path Length", is_benchmark)).pack(fill="x", pady=10)
        ttk.Button(frame, text="Compare Success Rates",
                   command=lambda: self.compare_plot("Success_Bool", is_benchmark)).pack(fill="x", pady=10)
        ttk.Button(frame, text="Compare Nodes Explored",
                   command=lambda: self.compare_plot("Nodes Explored", is_benchmark)).pack(fill="x", pady=10)

    def load_all_data(self, agent, is_benchmark=False):
        """
        Loads and merges all CSVs for a given agent, including from archives.
        """
        folder = f"{config.METRICS_DIR}/{agent}/{'benchmark_data' if is_benchmark else ''}"
        archive_folder = os.path.join(folder, "archive")

        all_files = []
        if os.path.exists(folder):
            all_files += [os.path.join(folder, f)
                          for f in os.listdir(folder) if f.endswith(".csv")]
        if os.path.exists(archive_folder):
            all_files += [os.path.join(archive_folder, f)
                          for f in os.listdir(archive_folder) if f.endswith(".csv")]

        dfs = [pd.read_csv(f).assign(_source_file=f) for f in all_files]
        if not dfs:
            return pd.DataFrame()

        df = pd.concat(dfs, ignore_index=True)
        df.insert(0, "Run", range(1, len(df) + 1))
        df["Success_Bool"] = df["Success"] == "Yes"
        return df

    def save_and_show_plot(self, agent, title, filename, is_benchmark):
        """
        Saves the current matplotlib figure to file and shows it.
        """
        plt.title(title)
        plt.legend(title="Agent")
        plt.grid(True)
        plt.tight_layout()

        subfolder = "benchmark_data/graphs" if is_benchmark else "graphs"
        save_path = f"{config.METRICS_DIR}/{agent}/{subfolder}"
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, filename))
        plt.show()

    def plot_path_vs_param(self, is_benchmark):
        """
        Plots path length against the relevant parameter (depth, noise, or run).
        """
        agent = self.selected_agent.get()
        df = self.load_all_data(agent, is_benchmark)
        if df.empty:
            messagebox.showerror(
                "No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else (
            "Max Depth" if agent == "depth" else "Noise Level")
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Path Length",
                     errorbar="sd", label=agent.capitalize())
        self.save_and_show_plot(
            agent, f"Path Length vs {x_col}", f"path_vs_{x_col.lower()}.temp.png", is_benchmark)

    def plot_success_rate(self, is_benchmark):
        """
        Plots success rate against the relevant parameter.
        """
        agent = self.selected_agent.get()
        df = self.load_all_data(agent, is_benchmark)
        if df.empty:
            messagebox.showerror(
                "No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else (
            "Max Depth" if agent == "depth" else "Noise Level")
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Success_Bool",
                     errorbar="sd", label=agent.capitalize())
        plt.ylabel("Success Rate")
        self.save_and_show_plot(
            agent, f"Success Rate vs {x_col}", f"success_vs_{x_col.lower()}.temp.png", is_benchmark)

    def plot_nodes_explored(self, is_benchmark):
        """
        Plots number of nodes explored against the relevant parameter.
        """
        agent = self.selected_agent.get()
        df = self.load_all_data(agent, is_benchmark)
        if df.empty:
            messagebox.showerror(
                "No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else (
            "Max Depth" if agent == "depth" else "Noise Level")
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Nodes Explored",
                     errorbar="sd", label=agent.capitalize())
        self.save_and_show_plot(
            agent, f"Nodes Explored vs {x_col}", f"nodes_vs_{x_col.lower()}.temp.png", is_benchmark)

    def compare_plot(self, metric, is_benchmark):
        """
        Plots a comparison of a metric across all agents.
        """
        plt.figure(figsize=(9, 6))
        for agent in AGENTS:
            df = self.load_all_data(agent, is_benchmark)
            if df.empty:
                continue
            x_col = "Run" if agent == "dynamic" else (
                "Max Depth" if agent == "depth" else "Noise Level")
            sns.lineplot(data=df, x=x_col, y=metric,
                         errorbar="sd", label=agent.capitalize())

        label = "Success Rate" if metric == "Success_Bool" else metric
        if metric == "Success_Bool":
            plt.ylabel("Success Rate")

        self.save_and_show_plot(
            "compare", f"{label} Comparison", f"compare_{metric.lower()}.temp.png", is_benchmark)

    def export_all_plots_pdf(self, is_benchmark):
        """
        Exports all single-agent plots into a single PDF report.
        """
        agent = self.selected_agent.get()
        df = self.load_all_data(agent, is_benchmark)
        if df.empty:
            messagebox.showerror(
                "No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else (
            "Max Depth" if agent == "depth" else "Noise Level")
        pdf_path = os.path.join(
            config.METRICS_DIR, agent, "benchmark_data" if is_benchmark else "", "graphs", "summary_report.temp.pdf")
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
                sns.lineplot(data=df, x=x_col, y=y_col,
                             errorbar="sd", label=agent.capitalize())
                plt.title(title)
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                pdf.savefig()
                plt.close()

        messagebox.showinfo("Export Complete", f"Plots saved to {pdf_path}")

    def open_pdf_report(self, is_benchmark):
        """
        Opens the generated PDF report in the system's default viewer.
        """
        agent = self.selected_agent.get()
        pdf_path = os.path.join(
            config.METRICS_DIR, agent, "benchmark_data" if is_benchmark else "", "graphs", "summary_report.temp.pdf")

        if not os.path.exists(pdf_path):
            messagebox.showerror(
                "Not Found", f"No PDF report found for {agent} agent.")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(pdf_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", pdf_path])
            else:
                subprocess.run(["xdg-open", pdf_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MetricsVisualizer(root)
    root.mainloop()

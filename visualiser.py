import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox

plt.ion()

AGENTS = ["depth", "noise", "dynamic"]
METRICS_DIR = os.path.join("data", "metrics")

class MetricsVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Metrics Visualizer")
        self.root.geometry("700x500")

        self.selected_agent = tk.StringVar(value=AGENTS[0])

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        self.setup_single_agent_tab()
        self.setup_compare_agents_tab()

    def setup_single_agent_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Single Agent")

        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="x")

        ttk.Label(frame, text="Select Agent:").grid(row=0, column=0, sticky="w")
        agent_menu = ttk.OptionMenu(frame, self.selected_agent, AGENTS[0], *AGENTS)
        agent_menu.grid(row=0, column=1, sticky="w")

        ttk.Button(frame, text="Plot: Path Length vs Depth/Noise",
                   command=self.plot_path_vs_param).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(frame, text="Plot: Success Rate",
                   command=self.plot_success_rate).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(frame, text="Plot: Nodes Explored",
                   command=self.plot_nodes_explored).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

    def setup_compare_agents_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Compare Agents")

        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill="x")

        ttk.Button(frame, text="Compare Path Lengths",
                   command=self.compare_path_lengths).pack(fill="x", pady=10)

        ttk.Button(frame, text="Compare Success Rates",
                   command=self.compare_success_rates).pack(fill="x", pady=10)

        ttk.Button(frame, text="Compare Nodes Explored",
                   command=self.compare_nodes_explored).pack(fill="x", pady=10)

    def load_all_data(self, agent):
        folder = os.path.join(METRICS_DIR, agent)
        archive_folder = os.path.join(folder, "archive")

        all_files = []
        if os.path.exists(folder):
            all_files.extend([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".csv")])
        if os.path.exists(archive_folder):
            all_files.extend([os.path.join(archive_folder, f) for f in os.listdir(archive_folder) if f.endswith(".csv")])

        dfs = []
        for file in all_files:
            df = pd.read_csv(file)
            df["_source_file"] = file  # for debugging or filtering
            dfs.append(df)

        if not dfs:
            return pd.DataFrame()

        df = pd.concat(dfs, ignore_index=True)
        df.insert(0, "Run", range(1, len(df)+1))  # Add index as fallback x-axis
        return df

    def save_and_show_plot(self, agent, title, filename):
        plt.title(title)
        plt.legend(title="Agent")
        plt.grid(True)
        plt.tight_layout()
        save_path = os.path.join(METRICS_DIR, agent, "graphs")
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, filename))
        plt.show()

    def plot_path_vs_param(self):
        agent = self.selected_agent.get()
        df = self.load_all_data(agent)
        if df.empty:
            messagebox.showerror("No Data", f"No data found for {agent} agent.")
            return

        if agent == "depth":
            x_col = "Max Depth"
        elif agent == "noise":
            x_col = "Noise Level"
        else:
            x_col = "Run"

        df = df.dropna(subset=[x_col, "Path Length"])

        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Path Length", errorbar="sd", label=agent.capitalize())
        self.save_and_show_plot(agent, f"Path Length vs {x_col}", f"path_vs_{x_col.lower().replace(' ', '_')}.png")

    def plot_success_rate(self):
        agent = self.selected_agent.get()
        df = self.load_all_data(agent)
        if df.empty:
            messagebox.showerror("No Data", f"No data found for {agent} agent.")
            return

        if agent in ("depth", "noise"):
            x_col = "Max Depth" if agent == "depth" else "Noise Level"
        else:
            x_col = "Run"

        df = df[df["Success"].isin(["Yes", "No"])]
        df["Success_Bool"] = df["Success"] == "Yes"

        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Success_Bool", errorbar="sd", label=agent.capitalize())
        plt.ylabel("Success Rate")
        self.save_and_show_plot(agent, f"Success Rate vs {x_col}", f"success_vs_{x_col.lower()}.png")

    def plot_nodes_explored(self):
        agent = self.selected_agent.get()
        df = self.load_all_data(agent)
        if df.empty:
            messagebox.showerror("No Data", f"No data found for {agent} agent.")
            return

        x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
        df = df.dropna(subset=[x_col, "Nodes Explored"])

        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df, x=x_col, y="Nodes Explored", errorbar="sd", label=agent.capitalize())
        self.save_and_show_plot(agent, f"Nodes Explored vs {x_col}", f"nodes_vs_{x_col.lower()}.png")

    def compare_path_lengths(self):
        plt.figure(figsize=(9, 6))
        for agent in AGENTS:
            df = self.load_all_data(agent)
            if df.empty: continue
            x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
            df = df.dropna(subset=[x_col, "Path Length"])
            sns.lineplot(data=df, x=x_col, y="Path Length", errorbar="sd", label=agent.capitalize())
        self.save_and_show_plot("compare", "Path Length Comparison", "compare_path_length.png")

    def compare_success_rates(self):
        plt.figure(figsize=(9, 6))
        for agent in AGENTS:
            df = self.load_all_data(agent)
            if df.empty: continue
            x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
            df = df[df["Success"].isin(["Yes", "No"])]
            df["Success_Bool"] = df["Success"] == "Yes"
            sns.lineplot(data=df, x=x_col, y="Success_Bool", errorbar="sd", label=agent.capitalize())
        plt.ylabel("Success Rate")
        self.save_and_show_plot("compare", "Success Rate Comparison", "compare_success_rate.png")

    def compare_nodes_explored(self):
        plt.figure(figsize=(9, 6))
        for agent in AGENTS:
            df = self.load_all_data(agent)
            if df.empty: continue
            x_col = "Run" if agent == "dynamic" else ("Max Depth" if agent == "depth" else "Noise Level")
            df = df.dropna(subset=[x_col, "Nodes Explored"])
            sns.lineplot(data=df, x=x_col, y="Nodes Explored", errorbar="sd", label=agent.capitalize())
        self.save_and_show_plot("compare", "Nodes Explored Comparison", "compare_nodes_explored.png")


if __name__ == "__main__":
    root = tk.Tk()
    app = MetricsVisualizer(root)
    root.mainloop()

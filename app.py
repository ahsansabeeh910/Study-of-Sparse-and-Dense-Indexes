import pandas as pd
import time
import psutil
import tkinter as tk
from tkinter import filedialog, simpledialog
import matplotlib.pyplot as plt
import sys,random
import os


class SparseIndex:
    def __init__(self, df, column, block_size=50):
        self.column = column
        self.index = {}
        for i in range(0, len(df), block_size):
            value = df.iloc[i][column]
            self.index[value] = i
        self.df = df

    def search(self, value):
        keys = sorted(self.index.keys())
        prev_key = keys[0]
        for key in keys:
            if value < key:
                start = self.index[prev_key]
                break
            prev_key = key
        else:
            start = self.index[prev_key]

        block_size = 50
        block = self.df.iloc[start:start+block_size]
        return block[block[self.column] == value]


class DenseIndex:
    def __init__(self, df, column):
        self.column = column
        self.index = dict(zip(df[column], df.index))
        self.df = df

    def search(self, value):
        if value in self.index:
            idx = self.index[value]
            return self.df.iloc[[idx]]
        else:
            return pd.DataFrame()


def get_memory_usage(obj):
    return sys.getsizeof(obj)

def main():
    root = tk.Tk()
    root.withdraw()

    print("=== Sparse vs Dense Indexing Simulator ===\n")

    file_path = filedialog.askopenfilename(
        title="Select your dataset (CSV file)",
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        print("No file selected. Exiting.")
        return

    df = pd.read_csv(file_path)
    print(f"\n Dataset loaded successfully with {len(df)} rows and {len(df.columns)} columns.")
    print("\nColumns available:", list(df.columns))
    
    MAX_ROWS = 5000  # maximum dataset size allowed for simulation
    if len(df) > MAX_ROWS:
        print(f"\n Dataset too large ({len(df)} rows).")
        print(f"Trimming automatically to first {MAX_ROWS} rows for faster processing...")
        df = df.head(MAX_ROWS)

    column = simpledialog.askstring("Input", "Enter the column name to index:")
    if column not in df.columns:
        print("Invalid column name. Exiting.")
        return

    query_value = simpledialog.askstring("Input", f"Enter the value to search in '{column}' column:")

    
    try:
        col_type = df[column].dtype
        if pd.api.types.is_numeric_dtype(col_type):
            query_value = float(query_value)
        elif pd.api.types.is_datetime64_any_dtype(col_type):
            query_value = pd.to_datetime(query_value)
        else:
            query_value = str(query_value)
    except Exception as e:
        print("Type conversion error:", e)
        query_value = str(query_value)

   
    print("\nBuilding Sparse Index...")
    start = time.time()
    sparse = SparseIndex(df, column)
    build_sparse_time = time.time() - start
    sparse_mem = get_memory_usage(sparse.index)

   
    print("Building Dense Index...")
    start = time.time()
    dense = DenseIndex(df, column)
    build_dense_time = time.time() - start
    dense_mem = get_memory_usage(dense.index)

    
    print("\nRunning queries...")
    start = time.time()
    sparse_result = sparse.search(query_value)
    sparse_query_time = time.time() - start

    start = time.time()
    dense_result = dense.search(query_value)
    dense_query_time = time.time() - start

    
    print("\n=== RESULTS ===")
    print(f"Sparse Index → Build Time: {build_sparse_time:.6f}s | Query Time: {sparse_query_time:.6f}s | Memory: {sparse_mem} KBs")
    print(f"Dense Index  → Build Time: {build_dense_time:.6f}s | Query Time: {dense_query_time:.6f}s | Memory: {dense_mem} KBs")

    print("\nQuery Results (Sparse):")
    print(sparse_result)
    print("\nQuery Results (Dense):")
    print(dense_result)

      
    labels = ['Build Time (s)', 'Query Time (s)', 'Memory Usage (KBs)']
    time_labels = ['Build Time (s)', 'Query Time (s)']

    sparse_times = [build_sparse_time, sparse_query_time]
    dense_times = [build_dense_time, dense_query_time]
    sparse_memory = sparse_mem
    dense_memory = dense_mem

    x_time = range(len(time_labels))
    x_memory = [len(time_labels)]  

    fig, ax1 = plt.subplots(figsize=(9, 5))

    # --- Time metrics (left y-axis)
    width = 0.35
    ax1.bar([i - width/2 for i in x_time], sparse_times, width, label='Sparse - Time', color='skyblue')
    ax1.bar([i + width/2 for i in x_time], dense_times, width, label='Dense - Time', color='orange')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_xticks([0, 1, 2])
    ax1.set_xticklabels(labels)
    ax1.tick_params(axis='y', labelcolor='black')
    ax2 = ax1.twinx()
    ax2.bar([x_memory[0] - width/2], [sparse_memory], width, label='Sparse - Memory', color='deepskyblue', alpha=0.6)
    ax2.bar([x_memory[0] + width/2], [dense_memory], width, label='Dense - Memory', color='coral', alpha=0.6)
    ax2.set_ylabel('Memory Usage (KBs)')
    ax2.tick_params(axis='y', labelcolor='black')

    plt.title('Sparse vs Dense Indexing Performance Comparison')
    lines, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels1 + labels2, loc='upper left')
    plt.tight_layout()
    plt.show()

    print("\n=== ACTUAL VALUES ===")
    print(f"Sparse Index -> Build Time: {build_sparse_time:.6f}s | Query Time: {sparse_query_time:.6f}s | Memory: {sparse_memory} KBs")
    print(f"Dense  Index -> Build Time: {build_dense_time:.6f}s | Query Time: {dense_query_time:.6f}s | Memory: {dense_memory} KBs")

if __name__ == "__main__":
    main()

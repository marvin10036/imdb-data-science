"""
Utility functions for the Oscar prediction project.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def print_dataset_info(df, name="Dataset"):
    """
    Print comprehensive information about a DataFrame.
    
    Args:
        df: pandas DataFrame
        name: Name of the dataset for display
    """
    print(f"\n{'='*60}")
    print(f"{name} Information")
    print(f"{'='*60}")
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"\nColumn types:")
    print(df.dtypes.value_counts())
    print(f"\n{'='*60}\n")


def analyze_missing_values(df):
    """
    Analyze and visualize missing values in DataFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        pandas.DataFrame: Summary of missing values
    """
    missing = df.isnull().sum()
    missing_pct = 100 * missing / len(df)
    
    missing_summary = pd.DataFrame({
        'Column': missing.index,
        'Missing_Count': missing.values,
        'Missing_Percentage': missing_pct.values
    })
    
    missing_summary = missing_summary[missing_summary['Missing_Count'] > 0]
    missing_summary = missing_summary.sort_values('Missing_Percentage', ascending=False)
    
    if len(missing_summary) > 0:
        print(f"\n⚠️  Columns with missing values:")
        print(missing_summary.to_string(index=False))
    else:
        print("\n✅ No missing values found!")
    
    return missing_summary


def plot_class_balance(df, target_col='label', title='Class Balance'):
    """
    Plot class distribution for binary classification.
    
    Args:
        df: pandas DataFrame
        target_col: Name of the target column
        title: Title for the plot
    """
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    
    # Count plot
    counts = df[target_col].value_counts()
    ax[0].bar(['Not Nominated', 'Nominated'], counts.values, color=['#3498db', '#e74c3c'])
    ax[0].set_ylabel('Count')
    ax[0].set_title('Class Distribution')
    for i, v in enumerate(counts.values):
        ax[0].text(i, v + 10, str(v), ha='center', fontweight='bold')
    
    # Percentage pie chart
    percentages = 100 * counts / counts.sum()
    ax[1].pie(percentages, labels=['Not Nominated', 'Nominated'], 
              autopct='%1.1f%%', colors=['#3498db', '#e74c3c'], startangle=90)
    ax[1].set_title('Class Distribution (%)')
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    print(f"\nClass balance:")
    print(f"Not Nominated (0): {counts[0]:,} ({percentages[0]:.2f}%)")
    print(f"Nominated (1): {counts[1]:,} ({percentages[1]:.2f}%)")
    print(f"Imbalance ratio: 1:{counts[0]/counts[1]:.1f}")


def save_figure(filename, directory='reports/figures', dpi=300):
    """
    Save current matplotlib figure.
    
    Args:
        filename: Name of the file
        directory: Directory to save the figure
        dpi: Resolution
    """
    import os
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    print(f"✅ Figure saved to {filepath}")


def set_plot_style():
    """Set consistent styling for all plots."""
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 10


if __name__ == "__main__":
    print("Utils module loaded successfully!")

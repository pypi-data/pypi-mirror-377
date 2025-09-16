"""
Advanced axis and legend customization examples.

This example demonstrates the new axis limit and legend positioning features
added in Rekha v0.2.0.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import rekha as rk

# Create sample data
np.random.seed(42)
n_points = 200

df = pd.DataFrame(
    {
        "x": np.random.randn(n_points).cumsum(),
        "y": np.random.randn(n_points).cumsum(),
        "value": np.random.randn(n_points) * 10 + 50,
        "category": np.random.choice(["A", "B", "C", "D"], n_points),
        "time": range(n_points),
        "experiment": np.repeat(["Exp1", "Exp2"], n_points // 2),
        "condition": np.tile(["Control", "Treatment"], n_points // 2),
    }
)

# Example 1: Direct axis limits
print("Example 1: Setting axis limits directly")
fig1 = rk.scatter(
    df.head(50),
    x="x",
    y="y",
    color="category",
    title="Scatter Plot with Custom Axis Limits",
    xlim=(-10, 10),  # Set x-axis limits
    ylim=(-15, 15),  # Set y-axis limits
    labels={"x": "X Position", "y": "Y Position", "category": "Group"},
)
fig1.save("axis_limits_example.png", format="social")

# Example 2: Legend positioning outside plot
print("\nExample 2: Positioning legend outside plot area")
fig2 = rk.line(
    df.groupby(["time", "category"])["value"].mean().reset_index(),
    x="time",
    y="value",
    color="category",
    title="Time Series with External Legend",
    legend_bbox_to_anchor=(1.05, 1),  # Place legend outside right
    legend_loc="upper left",
    labels={"time": "Time (s)", "value": "Average Value", "category": "Category"},
    figsize=(10, 6),
)
fig2.save("external_legend_example.png", format="social")

# Example 3: Legend above plot
print("\nExample 3: Placing legend above plot")
fig3 = rk.bar(
    df.groupby("category")["value"].mean().reset_index(),
    x="category",
    y="value",
    title="Bar Chart with Top Legend",
    ylim=(0, 70),  # Set y-axis to start at 0
    labels={"category": "Group", "value": "Mean Value"},
)
fig3.save("top_legend_example.png", format="social")

# Example 4: Faceted plot with custom labels and limits
print("\nExample 4: Faceted plot with custom axis configuration")
fig4 = rk.line(
    df,
    x="time",
    y="value",
    color="category",
    facet_col="experiment",
    facet_row="condition",
    title="Faceted Plot with Custom Configuration",
    xlim=(0, 100),  # Applied to all facets
    ylim=(20, 80),  # Applied to all facets
    labels={
        "time": "Time Point",
        "value": "Measurement",
        "category": "Group ID",
        "experiment": "Experiment",
        "condition": "Condition",
    },
    figsize=(12, 8),
)

# Update layout after creation - works correctly with facets now!
fig4.update_layout(xlabel="Time (seconds)", ylabel="Response Value (units)")
fig4.save("faceted_custom_labels.png", format="social")

# Example 5: Combining multiple customizations
print("\nExample 5: Complete customization example")
fig5 = rk.scatter(
    df,
    x="x",
    y="y",
    color="category",
    size="value",
    title="Fully Customized Scatter Plot",
    # Axis configuration
    xlim=(-20, 20),
    ylim=(-20, 20),
    xscale="linear",
    yscale="linear",
    # Legend configuration
    legend_bbox_to_anchor=(1.02, 0.5),
    legend_loc="center left",
    # Labels with legend title
    labels={
        "x": "Horizontal Position",
        "y": "Vertical Position",
        "category": "Sample Group",  # This becomes the legend title
        "value": "Intensity",
    },
    # Styling
    dark_mode=True,
    figsize=(10, 8),
    alpha=0.6,
    # Font sizes
    title_font_size=18,
    label_font_size=14,
    legend_font_size=11,
)
fig5.save("complete_customization.png", format="social")

# Example 6: Dynamic axis limits with update_layout
print("\nExample 6: Updating axis limits after plot creation")
fig6 = rk.histogram(
    df, x="value", color="category", title="Histogram with Dynamic Limits"
)

# Analyze data and set appropriate limits
value_range = df["value"].max() - df["value"].min()
margin = value_range * 0.1

fig6.update_layout(
    xlim=(df["value"].min() - margin, df["value"].max() + margin),
    xlabel="Value Range",
    ylabel="Count",
)
fig6.save("dynamic_limits.png", format="social")

print("\nAll examples completed! Check the generated PNG files.")

# Show the last plot
plt.show()

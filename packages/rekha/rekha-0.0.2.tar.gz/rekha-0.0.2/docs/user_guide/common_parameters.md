# Common Parameters

All Rekha plot functions share a common set of parameters inherited from the `BasePlot` class. These parameters provide consistent styling and customization options across all plot types.

## New Simplified API (v0.2.0+)

Rekha now supports direct parameter specification for common customizations, eliminating the need for `update_layout()` in most cases:

```python
# Before (v0.1.x)
fig = rk.line(df, x='time', y='value', color='category')
fig.update_layout(xlabel='Time (s)', ylabel='Value', xlim=(0, 100))

# After (v0.2.0+) - Everything in one call!
fig = rk.line(
    df, x='time', y='value', color='category',
    xlabel='Time (s)', 
    ylabel='Value',
    xlim=(0, 100),
    color_label='Category Type'
)
```

## Axis Configuration

### `xlim` and `ylim`
*New in version 0.2.0*

Set explicit axis limits without needing to access matplotlib axes.

```python
import rekha as rk

# Set both x and y limits
fig = rk.scatter(df, x='x', y='y', xlim=(0, 100), ylim=(-50, 50))

# Set only one axis limit
fig = rk.line(df, x='time', y='value', ylim=(0, None))  # Auto-scale x, fix y minimum
```

## Legend Configuration

### `legend_bbox_to_anchor`
*New in version 0.2.0*

Position the legend anywhere, including outside the plot area, using matplotlib's bbox_to_anchor syntax.

```python
# Place legend outside right
fig = rk.line(df, x='x', y='y', color='category', 
              legend_bbox_to_anchor=(1.05, 1))

# Place legend above plot
fig = rk.scatter(df, x='x', y='y', color='group',
                 legend_bbox_to_anchor=(0.5, 1.1),
                 legend_loc='upper center')

# Common positions:
# (1.05, 1) - Outside right
# (0.5, 1.1) - Above center
# (1.05, 0.5) - Right center
# (-0.15, 1) - Outside left
```

### Legend Titles
*Improved in version 0.2.0*

When using color mapping, legends now automatically display titles:

```python
# Legend will show "Category" as title
fig = rk.scatter(df, x='x', y='y', color='category')

# Custom legend title through labels
fig = rk.line(df, x='time', y='value', color='sensor_id',
              labels={'sensor_id': 'Sensor'})
```

## Faceting Improvements

### Custom Axis Labels with Faceting
*Fixed in version 0.2.0*

The `update_layout` method now correctly applies custom labels to faceted plots:

```python
fig = rk.line(df, x='x', y='y', color='group', 
              facet_col='condition', facet_row='experiment')

# Update labels after creation
fig.update_layout(xlabel='Time (seconds)', 
                  ylabel='Response (mV)')
```

## Complete Parameter Reference

### Data Parameters
- `data`: DataFrame, dict, or None - The data to plot
- `x`, `y`: str, list, or array - Data for axes
- `color`: str - Column for color grouping
- `size`: str, list, or array - Column for size mapping (scatter plots)
- `shape`: str - Column for shape mapping (scatter plots)

### Layout Parameters
- `title`: str - Plot title
- `xlabel`: str - Direct X-axis label (takes precedence over labels dict)
- `ylabel`: str - Direct Y-axis label (takes precedence over labels dict)
- `labels`: dict - Custom labels for columns (fallback for xlabel/ylabel)
- `figsize`: tuple - Figure size as (width, height) in inches
- `xlim`: tuple - X-axis limits as (min, max)
- `ylim`: tuple - Y-axis limits as (min, max)

### Styling Parameters
- `dark_mode`: bool - Use dark theme
- `palette`: str - Color palette name
- `grayscale_friendly`: bool - Add patterns for printing

### Font Sizes
- `title_font_size`: float (default 16)
- `label_font_size`: float (default 14)
- `tick_font_size`: float (default 12)
- `legend_font_size`: float (default 12)

### Legend Parameters
- `color_label`: str - Direct legend title for color mapping (takes precedence over labels dict)
- `legend_loc`: str - Legend location
- `legend_bbox_to_anchor`: tuple - Custom legend position

### Grid Parameters
- `grid`: bool - Show grid lines
- `grid_alpha`: float - Grid transparency
- `grid_linewidth`: float - Grid line width

### Faceting Parameters
- `facet_row`: str - Column for row facets
- `facet_col`: str - Column for column facets
- `facet_row_label`: str - Direct label for facet rows (takes precedence over labels dict)
- `facet_col_label`: str - Direct label for facet columns (takes precedence over labels dict)
- `share_x`: bool - Share x-axis across facets
- `share_y`: bool - Share y-axis across facets
- `subplot_titles`: bool - Show subplot titles
- `col_wrap`: int - Wrap columns after n facets
- `row_wrap`: int - Wrap rows after n facets

### Scale Parameters
- `xscale`: str - X-axis scale ('linear', 'log', 'symlog', 'logit')
- `yscale`: str - Y-axis scale ('linear', 'log', 'symlog', 'logit')

### Formatting Parameters
- `humanize_units`: bool - Format large numbers (1M, 2K, etc.)
- `humanize_format`: str - Format style ('intword', 'intcomma', 'scientific')
- `rotate_xticks`: bool or float - Rotate x-axis labels

### Matplotlib Parameters
- `alpha`: float - Transparency
- `label`: str - Series label for legend
- `edgecolor`: str - Edge color
- `linewidth`: float - Line width
- `zorder`: float - Drawing order

## Examples

### Complete Customization Example

```python
import rekha as rk
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'time': range(100),
    'signal': np.cumsum(np.random.randn(100)),
    'sensor': ['A'] * 50 + ['B'] * 50,
    'condition': ['Control'] * 25 + ['Test'] * 25 + ['Control'] * 25 + ['Test'] * 25
})

# Create highly customized plot
fig = rk.line(
    df,
    x='time',
    y='signal',
    color='sensor',
    facet_col='condition',
    # Layout
    title='Sensor Readings Over Time',
    labels={'time': 'Time (s)', 'signal': 'Signal (mV)', 'sensor': 'Sensor ID'},
    figsize=(12, 6),
    xlim=(0, 100),
    ylim=(-20, 20),
    # Styling
    dark_mode=True,
    palette='husl',
    # Legend
    legend_loc='upper left',
    legend_bbox_to_anchor=(1.02, 1),
    # Grid
    grid=True,
    grid_alpha=0.3,
    # Fonts
    title_font_size=18,
    label_font_size=14,
    legend_font_size=12
)

# Further customize with update_layout
fig.update_layout(
    title='Updated Title',
    ylim=(-25, 25)
)

# Save in different formats
fig.save('sensor_plot.pdf', format='paper')
fig.save('sensor_plot.png', format='social', transparent=False)
```

### Migration from v0.1.x

If you're upgrading from an earlier version, here are the key improvements:

1. **Direct axis limits**: Instead of `fig.ax.set_xlim()`, use `xlim` parameter
2. **Legend positioning**: Use `legend_bbox_to_anchor` instead of manual legend manipulation
3. **Facet labels**: `update_layout` now works correctly with faceted plots
4. **Legend titles**: Automatically set for color-mapped data

```python
# Old way (v0.1.x)
fig = rk.scatter(df, x='x', y='y', color='group')
fig.ax.set_xlim(0, 100)
fig.ax.legend(bbox_to_anchor=(1.05, 1))

# New way (v0.2.0+)
fig = rk.scatter(df, x='x', y='y', color='group',
                 xlim=(0, 100),
                 legend_bbox_to_anchor=(1.05, 1))
```
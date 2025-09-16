# Changelog

All notable changes to Rekha will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added `xlim` and `ylim` parameters to all plot functions for direct axis limit control
- Added `xlabel` and `ylabel` parameters for direct axis labeling without needing `update_layout()`
- Added `color_label` parameter for direct legend title specification
- Added `facet_row_label` and `facet_col_label` parameters for direct facet labeling
- Added `legend_bbox_to_anchor` parameter for flexible legend positioning, including outside plot area
- Added automatic legend titles when using color mapping
- Added smart y-axis limit detection for better default visualization
- Added comprehensive documentation for common parameters across all plot types
- Added new example scripts demonstrating the simplified API

### Fixed
- Fixed custom axis names not applying correctly when using faceting with `update_layout()`
- Fixed legend titles not showing up for color-mapped data in line, scatter, and other plot types
- Fixed `update_layout()` to properly handle faceted plots for all parameters

### Changed
- Improved `update_layout()` method to work consistently with both single and faceted plots
- Enhanced documentation for `update_layout()` to clarify faceted plot behavior
- Legend titles now use custom labels from the `labels` parameter when provided

### Example Usage

```python
import rekha as rk

# NEW: Everything in one call - no update_layout needed!
fig = rk.line(
    df,
    x='time',
    y='value', 
    color='category',
    facet_col='condition',
    facet_row='experiment',
    # Direct parameter specification
    xlabel='Time (seconds)',
    ylabel='Response (mV)',
    xlim=(0, 100),
    ylim=(-50, 50),
    color_label='Category Type',
    facet_col_label='Experimental Condition',
    facet_row_label='Experiment ID',
    legend_bbox_to_anchor=(1.05, 1)
)

# update_layout() still available for dynamic updates
fig.update_layout(ylim=(0, 100))  # Adjust after seeing the data
```

## [0.1.0] - Previous Release

Initial release of Rekha with core plotting functionality.
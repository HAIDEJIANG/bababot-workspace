# Components Reference

## Screen Component
Base container for TRMNL displays.

**Base:**
```html
<div class="screen">
 <!-- Content -->
</div>
```

**Device Classes:**
- `screen--v2` - TRMNL V2 (1040x780)
- `screen--amazon_kindle_2024` - Kindle 2024 (718x540)

**Bit Depth:**
- `screen--1bit` - Monochrome
- `screen--4bit` - 16 grayscale levels

**Modifiers:**
- `screen--portrait` - Portrait orientation (swaps dimensions)
- `screen--no-bleed` - Remove default padding
- `screen--dark-mode` - Invert colors (except images)
- `screen--backdrop` - Patterned/gray backgrounds

**Scale Variants (4-bit only):**
- `screen--scale-xsmall` (0.75)
- `screen--scale-regular` (1.0)

**Example:**
<div class="screen screen--og screen--2bit">
 <div class="layout">...</div>

## View Component
Container structure for plugin layouts.

**Sizes:**
- `view view--full` - Full-width view
- `view--half_horizontal` - Horizontal half
- `view--half_vertical` - Vertical half
- `view--quadrant` - Quarter-section

**Note:** In markup editor, do NOT manually wrap with view classes (system applies automatically).

## Layout Component
Semantic Flexbox container (see layout-systems.md for full details).

**Base Pattern:**
<div class="layout layout--col layout--center gap--large">
 <span class="title">Title</span>
 <span class="description">Description</span>

## Title Bar Component
Standardized header with icon, title, and optional instance label.

**Structure:**
<div class="title_bar">
 <img class="image" src="icon.svg">
 <span class="title">Title Text</span>
 <span class="instance">Optional Instance</span>

**Elements:**
- `image` - Icon/logo (left side)
- `title` - Main heading
- `instance` - Optional label (right side)

## Divider Component
Visual separator line.

**Horizontal (default):**
<div class="divider"></div>
<div class="divider--h"></div>

**Vertical:**
<div class="divider--v"></div>

**Background-Specific:**
- `divider--on-white` - White/very light backgrounds
- `divider--on-light` - Light gray (gray-50 to gray-65)
- `divider--on-dark` - Dark gray (gray-30 to gray-45)
- `divider--on-black` - Black/very dark backgrounds

**Feature:** Automatic background detection.

## Rich Text Component
Flexible container for formatted text.

<div class="richtext richtext--center">
 <div class="content">
 <p>Formatted text content here.</p>

**Alignment:**
- `richtext--left` (default), `richtext--center`, `richtext--right`

**Content Sizes:**
- `content--large` - Headings/emphasis
- `content` or `content--base` - Default body text
- `content--small` - Captions/secondary

**Enhanced Features:**
- `data-content-limiter="true"` - Auto-adjust text size when overflow
- `data-pixel-perfect="true"` - Crisp 1-bit rendering

<div class="richtext richtext--center" data-content-limiter="true">
 <div class="content content--large">
 <h1>Heading</h1>
 <p>Body text that adapts to available space.</p>

## Item Component
Container for structured content with optional metadata.

**Variant 1: With Meta**
<div class="item">
 <div class="meta">
 <span class="label">Meta</span>
 <span class="title">Item Title</span>
 <span class="description">Description text</span>

**Variant 2: With Meta and Index**
 <span class="index">1</span>
 <span class="title">Task Name</span>
 <span class="label">Status</span>

**Variant 3: With Emphasis**
<div class="item item--emphasis-2">
 <span class="label">Tag</span>
 <span class="title">Highlighted Item</span>

**Emphasis Levels:**
- `item--emphasis-2` - Medium emphasis

**Variant 4: Simple (Content Only)**
 <span class="title">Simple Item</span>
 <span class="description">No meta section</span>

## Table Component
Structured data display with multiple size variants.

**Base Structure:**
<table class="table">
 <thead>
 <tr>
 <th><span class="title">Header 1</span></th>
 <th><span class="title">Header 2</span></th>
 </tr>
 </thead>
 <tbody>
 <td><span class="label">Data 1</span></td>
 <td><span class="label">Data 2</span></td>
 </tbody>
</table>

**Size Variants:**
- `table` or `table--base` - Default size
- `table--large` - Increased row heights
- `table--small` - Compact rows
- `table--xsmall` - Most compact

**Additional Features:**
- `table--indexed` - Add index column
- `data-table-limit="true"` - Overflow with "and X more"
- `data-clamp="1"` - Single-line truncation in cells

**Cell Markup Requirements:**
- Headers must use: `<th><span class="title">...</span></th>`

**Example with Features:**
<table class="table table--small" data-table-limit="true">
 <th><span class="title">Name</span></th>
 <th><span class="title">Value</span></th>
 <td><span class="label" data-clamp="1">Long name that truncates</span></td>
 <td><span class="label">123</span></td>

## Progress Bar Component
Visual progress indicator with label and percentage.

**Base Sizes:**
- `progress-bar` or `progress-bar--base` - Default
- `progress-bar--small` - Compact
- `progress-bar--large` - Prominent

- Default - Standard appearance
- `progress-bar--emphasis-2` - Medium emphasis

<div class="progress-bar progress-bar--large">
 <span class="label">Loading</span>
 <span class="value value--xxsmall">75%</span>
 <div class="track">
 <div class="fill" style="width: 75%"></div>

**Key Elements:**
- `content` - Label and percentage container
- `track` - Background bar
- `fill` - Filled portion (set width via inline style)

## Progress Dots Component
Step indicator with filled/current/empty states.

- `progress-dots` or `progress-dots--base` - Default
- `progress-dots--small` - Compact
- `progress-dots--large` - Prominent

<div class="progress-dots progress-dots--large">
 <div class="dot dot--filled"></div>
 <div class="dot dot--current"></div>
 <div class="dot"></div>

**Dot States:**
- `dot--filled` - Completed step
- `dot--current` - Active step
- `dot` (no modifier) - Upcoming step

## Chart Component
Supports Line, Multi-Series Line, Bar, and Gauge charts.

**Requirements:**
- Highcharts v12.3.0+
- Chartkick v5.0.1+ (optional)
- Pattern-fill module for multi-series

**Critical Configuration (REQUIRED for e-ink):**
```javascript
var chart = new Chartkick.LineChart("chart-id", data, {
 animation: false, // REQUIRED
 enableMouseTracking: false, // Disable interactions
 hover: { enabled: false } // No hover states
});

**Data Formats:**
// Single series
var data = [["2024-06-09", 975], ["2024-06-10", 840]];

// Multi-series
var data = { name: "Current", data: [["2024-06-09", 975]] };

**Container:**
<div id="chart-id" class="w--full h--[200px]"></div>

**Gauge Charts:**
- Range: 0-100
- Arc angles: `startAngle: -150`, `endAngle: 150`
- Transparent backgrounds for pivot elements

**Library Detection:**
if ("Chartkick" in window) {
 createChart();
} else {
 window.addEventListener("chartkick:load", createChart, true);
}

**E-ink Considerations:**
- Disable ALL animations
- Use pattern fills for multi-series (1-bit displays)
- Set explicit dimensions
- Use dithered backgrounds: `bg--gray-30`, `bg--gray-60`
- Configure axes for readability
# Creating Dashboards

Step-by-step guide to building interactive dashboards in Metabase.

---

## Overview

Dashboards in Metabase combine multiple visualizations, filters, and text into a single interactive view. This guide walks you through creating effective dashboards for your Dango data.

**What you'll learn**:

- Creating questions (visualizations)
- Building dashboards from saved questions
- Adding filters and parameters
- Customizing layouts and styling
- Sharing and collaboration
- Dashboard best practices

---

## Quick Start

### Create Your First Dashboard

**End-to-End Example** in 5 minutes:

#### 1. Create a Question

1. Open Metabase: http://localhost:3000
2. Click **"+ New"** → **"Question"**
3. Select **"DuckDB"** database
4. Choose table: `marts.revenue_by_month`
5. Visualization: **Line chart**
   - X-axis: `month`
   - Y-axis: `revenue_usd`
6. Click **"Visualize"**
7. **Save** as "Monthly Revenue Trend"

#### 2. Create a Dashboard

1. Click **"+ New"** → **"Dashboard"**
2. Name: "Revenue Dashboard"
3. Click **"Create"**

#### 3. Add Question to Dashboard

1. Click **"Add a saved question"**
2. Search for "Monthly Revenue Trend"
3. Click to add
4. Resize and position card
5. Click **"Save"**

Done! You now have a working dashboard.

---

## Creating Questions

Questions are individual visualizations that populate dashboards.

### Visual Query Builder

**No SQL required** - use the GUI:

#### Step 1: Choose Data

Click **"+ New"** → **"Question"**

- **Database**: DuckDB
- **Table**: Select from available schemas (e.g., `marts.customer_metrics`)

#### Step 2: Add Filters

Filter data before visualization:

- Click **"Filter"**
- Choose column (e.g., `lifetime_value`)
- Set condition (e.g., "Greater than 100")
- Add multiple filters with AND/OR logic

**Example**: Active customers with orders:
```
Filter: lifetime_orders > 0
Filter: created >= 2024-01-01
```

#### Step 3: Summarize (Aggregate)

Add metrics and grouping:

- Click **"Summarize"**
- **Metric**: Choose aggregation
  - Count of rows
  - Sum of [column]
  - Average of [column]
  - Min/Max of [column]
- **Group by**: Dimension to split by
  - Date (day, month, year)
  - Category
  - User segment

**Example**: Revenue by month:
```
Summarize: Sum of lifetime_value
Group by: created → by Month
```

#### Step 4: Choose Visualization

Select chart type:

- **Line** - Trends over time
- **Bar** - Compare categories
- **Pie** - Part-to-whole
- **Table** - Detailed rows
- **Number** - Single metric

Configure visualization:

- Axis labels
- Colors
- Goal lines
- Formatting (currency, decimals)

#### Step 5: Save Question

1. Click **"Save"** (top-right)
2. Name: "Descriptive question name"
3. Choose collection (folder)
4. Optional: Add description
5. Click **"Save"**

### SQL-Based Questions

**For advanced queries**:

#### Create SQL Question

1. Click **"+ New"** → **"SQL query"**
2. Select **"DuckDB"** database
3. Write SQL:

```sql
SELECT
    DATE_TRUNC('month', created) as month,
    COUNT(*) as new_customers,
    SUM(lifetime_value) as total_ltv,
    AVG(lifetime_value) as avg_ltv
FROM marts.customer_metrics
WHERE created >= CURRENT_DATE - INTERVAL 12 MONTH
GROUP BY month
ORDER BY month DESC
```

4. Click **"Get Answer"** to preview
5. Choose visualization
6. **Save** with descriptive name

#### Adding Variables (Filters)

Make SQL queries interactive:

```sql
SELECT
    customer_id,
    email,
    lifetime_value,
    lifetime_orders
FROM marts.customer_metrics
WHERE created >= {{start_date}}
  AND created < {{end_date}}
  AND lifetime_value > {{min_ltv}}
ORDER BY lifetime_value DESC
```

**Variable types**:
- `{{variable}}` - Text input
- `{{date_variable}}` - Date picker
- `[[AND optional_clause]]` - Optional WHERE clause

Define variables:
1. Metabase auto-detects `{{variables}}`
2. Click variable in left sidebar
3. Set type: Text, Number, Date
4. Set default value
5. Set label (user-facing name)

---

## Building Dashboards

### Create Dashboard

1. **"+ New"** → **"Dashboard"**
2. **Name**: Descriptive title (e.g., "Executive Overview")
3. **Description**: Optional context
4. **Collection**: Choose folder
5. Click **"Create"**

### Add Cards

**Saved Questions**:

1. Click **"Add a saved question"**
2. Search or browse questions
3. Click question to add as card
4. Repeat for all questions

**Text Cards**:

1. Click **"Add a text card"**
2. Write markdown:
   ```markdown
   # Revenue Metrics

   Key metrics for Q4 2024:
   - Target: $1M ARR
   - Focus: Enterprise customers
   ```
3. Click outside to save

**Headings**:

1. Click **"Add a heading"**
2. Type section title
3. Use to organize dashboard into sections

### Layout and Design

#### Resize Cards

- Drag bottom-right corner to resize
- Snap to grid (automatic)
- Make key metrics larger

#### Position Cards

- Drag cards to reorder
- Align cards in rows/columns
- Group related metrics

**Common Layouts**:

**Executive Dashboard**:
```
[  Key Metric 1  ] [  Key Metric 2  ] [  Key Metric 3  ]
[        Large Line Chart - Revenue Trend             ]
[    Bar Chart 1    ] [    Bar Chart 2    ]
```

**Detail Dashboard**:
```
[        Large Table - Detailed Data                  ]
[    Chart 1    ] [    Chart 2    ] [    Chart 3    ]
```

#### Styling

Click card → **Settings** (gear icon):

- **Title**: Override question title
- **Description**: Add context
- **Display**: Show/hide title
- **Click behavior**: Link to detailed view or custom URL

### Add Filters

Make dashboards interactive:

#### Dashboard-Wide Filters

1. Click **"Add a filter"** (top-right)
2. Choose filter type:
   - **Time** - Date range picker
   - **Location** - Dropdown of categories
   - **ID** - Search field
   - **Other Categories** - Multi-select

**Example: Date Filter**

1. Add filter → **Time** → **All Options**
2. Connect to cards:
   - Select cards that have date fields
   - Map filter to correct column (e.g., `created`, `month`)
3. Set default: "Previous 30 days"
4. Save

**Example: Category Filter**

1. Add filter → **Location** → **Dropdown**
2. Source: `marts.customer_metrics.status`
3. Connect to relevant cards
4. Users can now filter by status

#### Filter Best Practices

- Add date range filter (almost always useful)
- Limit to 3-5 filters (avoid clutter)
- Set sensible defaults
- Use "Required" for critical filters

### Auto-Refresh

Keep dashboards live:

1. Open dashboard
2. Click **"..."** (top-right) → **"Auto-refresh"**
3. Choose interval:
   - 1 minute
   - 5 minutes
   - 10 minutes
   - 15 minutes

**Use cases**:
- Live operational dashboards
- Real-time monitoring
- Display on TV/monitor

!!! warning "Performance Impact"
    Auto-refresh re-runs all queries. Use caching and efficient queries for large dashboards.

---

## Dashboard Examples

### Example 1: Revenue Dashboard

**Goal**: Track monthly revenue and top customers

**Questions to create**:

1. **Monthly Revenue Trend** (Line chart)
   ```sql
   SELECT
       month,
       revenue_usd
   FROM marts.revenue_by_month
   ORDER BY month
   ```

2. **Current Month Revenue** (Number)
   ```sql
   SELECT SUM(revenue_usd)
   FROM marts.revenue_by_month
   WHERE month = DATE_TRUNC('month', CURRENT_DATE)
   ```

3. **Revenue Growth** (Number with trend)
   ```sql
   SELECT
       (current_month - previous_month) / previous_month * 100 as growth_pct
   FROM (
       SELECT
           SUM(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE)
               THEN revenue_usd END) as current_month,
           SUM(CASE WHEN month = DATE_TRUNC('month', CURRENT_DATE - INTERVAL 1 MONTH)
               THEN revenue_usd END) as previous_month
       FROM marts.revenue_by_month
   )
   ```

4. **Top 10 Customers by LTV** (Table)
   ```sql
   SELECT
       email,
       lifetime_value,
       lifetime_orders
   FROM marts.customer_metrics
   ORDER BY lifetime_value DESC
   LIMIT 10
   ```

**Dashboard Layout**:
```
[  Current Revenue  ] [  Growth %  ] [  Total Customers  ]
[           Monthly Revenue Trend (Line)                 ]
[           Top 10 Customers (Table)                     ]
```

### Example 2: Customer Acquisition Dashboard

**Questions**:

1. New customers by month
2. Customer acquisition cost (if available)
3. Customer cohort retention
4. Geographic distribution

**Filters**:
- Date range
- Acquisition channel
- Customer segment

### Example 3: Operational Dashboard

**Questions**:

1. Orders processed today
2. Average order value
3. Order status breakdown (pie chart)
4. Recent orders (table with refresh)

**Settings**:
- Auto-refresh: 1 minute
- Default date: Today
- Full-screen mode for TV display

---

## Sharing Dashboards

### Share with Team

**Internal Sharing** (Metabase users):

1. Open dashboard
2. Click **"Share"** icon (top-right)
3. Choose method:
   - **Link** - Copy URL to share
   - **Email subscription** - Daily/weekly email
   - **Slack subscription** - Post to channel

**Permissions**:
- View only (default)
- Can edit (grant in collections)

### Public Sharing

**External Sharing** (no login required):

!!! warning "Security Warning"
    Public links expose data without authentication. Use carefully in production.

1. Open dashboard
2. **"..."** → **"Public link"** → Enable
3. Copy public URL
4. Share with external stakeholders

**Options**:
- Embedded parameters (e.g., `?date=2024-12`
- Disable filters (lock parameters)
- Set expiration date (planned feature)

### Email Subscriptions

Send dashboard snapshots via email:

1. Open dashboard
2. **"Share"** → **"Dashboard subscription"**
3. Configure:
   - **Recipients**: Team emails
   - **Frequency**: Daily, Weekly (Monday, etc.)
   - **Time**: 8 AM, 5 PM, etc.
   - **Filters**: Set default values
4. Click **"Create subscription"**

**Requirements**:
- Admin must configure SMTP in Metabase settings
- Recipients must have Metabase accounts (or use public link)

### Slack Notifications

Post to Slack channels:

1. Admin → Settings → Slack
2. Configure Slack app integration
3. Open dashboard → **"Share"** → **"Send to Slack"**
4. Choose channel and schedule

---

## Advanced Features

### Dashboard Parameters

**Pass values between dashboards**:

Create drill-down experiences:

1. **Parent Dashboard**: Customer overview
2. **Child Dashboard**: Customer detail (filtered by ID)

**Setup**:

1. Create parameter on child dashboard:
   ```
   Filter: customer_id = {{customer_id}}
   ```

2. Link from parent dashboard:
   - Click card → Settings → **Click behavior**
   - **Action**: Go to dashboard
   - **Dashboard**: Customer Detail
   - **Pass parameter**: Map `customer_id` column to `{{customer_id}}` parameter

**Result**: Click customer in overview → Detail dashboard opens with that customer

### Custom Click Behavior

Customize what happens when users click visualizations:

**Options**:

1. **Drill through** - Zoom into data (default)
2. **Link to dashboard** - Navigate to related dashboard
3. **Custom URL** - Open external link
   ```
   https://admin.stripe.com/customers/{{customer_id}}
   ```
4. **Update filter** - Set dashboard filter value

**Example**: Click product name → Open product detail dashboard

### Dashboard Tabs

Organize complex dashboards:

1. Edit dashboard
2. Click **"Add tab"**
3. Name tab (e.g., "Overview", "Details", "Trends")
4. Add cards to each tab
5. Save

**Use case**: Multi-page executive report

### Full-Screen Mode

Display on TVs or monitors:

1. Open dashboard
2. Press **F** or click **"Enter fullscreen"**
3. Auto-refresh for live monitoring

**Exit**: Press **Esc** or **F**

### Version History

Recover previous dashboard versions:

1. Open dashboard
2. **"..."** → **"Revision history"**
3. View changes
4. Restore previous version if needed

---

## Performance Optimization

### Query Optimization

**Slow dashboards? Check these:**

1. **Pre-aggregate in dbt**:
   ```sql
   -- Instead of aggregating in Metabase:
   -- Create marts table in dbt
   SELECT
       DATE_TRUNC('month', created) as month,
       COUNT(*) as customer_count,
       SUM(amount) as revenue
   FROM staging.stg_customers
   GROUP BY month
   ```

2. **Limit date ranges**:
   - Default filters to last 30/90 days
   - Avoid "All Time" on large datasets

3. **Use efficient visualizations**:
   - Tables: Limit rows (top 100)
   - Charts: Aggregate before plotting

### Caching

Enable query result caching:

1. Admin → Settings → Caching
2. **Enable caching**: Yes
3. **Cache TTL**: 1-24 hours (based on update frequency)
4. **Adaptive caching**: Auto-adjusts based on query patterns

**When to cache**:
- Static/slow-changing data (marts)
- High-traffic dashboards
- Complex aggregations

**When not to cache**:
- Real-time operational data
- Dashboards with auto-refresh

### Card-Level Optimization

Per-question settings:

1. Edit question
2. **Settings** → **Display**
3. **Limit**: Cap rows returned (e.g., 1000)
4. **Cache TTL**: Override global setting

---

## Dashboard Best Practices

### Design Principles

#### 1. Show the Most Important Metric First

Place KPI at top-left:
```
[  Primary KPI  ] [ Secondary ] [ Tertiary ]
```

Users scan top-to-bottom, left-to-right.

#### 2. Use Consistent Visualizations

- **Trends over time**: Line charts
- **Comparisons**: Bar charts
- **Part-to-whole**: Pie charts (use sparingly)
- **Single metrics**: Number cards

#### 3. Add Context with Text

Use text cards for:
- Dashboard purpose
- Metric definitions
- Caveats or notes
- Links to documentation

#### 4. Group Related Metrics

Use headings to create sections:
```
Heading: "Revenue Metrics"
[ Chart 1 ] [ Chart 2 ]

Heading: "Customer Metrics"
[ Chart 3 ] [ Chart 4 ]
```

#### 5. Keep It Focused

- One dashboard = One purpose
- Aim for 6-12 cards (max)
- Split into multiple dashboards if needed

### Naming Conventions

**Dashboards**:
- `[Team] - [Purpose]` (e.g., "Sales - Weekly Performance")
- `[Frequency] - [Topic]` (e.g., "Daily - Operations")

**Questions**:
- Descriptive and searchable
- Include metric type: "Customer Count by Month"
- Avoid vague names: ~~"Analysis 1"~~

### Organization

**Use Collections**:

```
Our Analytics/
├── Executive/
│   ├── Weekly Business Review
│   └── Monthly Board Report
├── Sales/
│   ├── Pipeline Dashboard
│   └── Rep Performance
├── Marketing/
│   ├── Campaign Overview
│   └── Funnel Analysis
└── Product/
    └── Feature Usage
```

**Permissions**:
- Restrict access by team
- "Executive" collection: View-only for most users

---

## Troubleshooting

### Dashboard Not Loading

**Check query performance**:

1. Edit dashboard
2. Click card → View question
3. Check execution time
4. Optimize query or underlying dbt model

**Check data availability**:

```bash
# Verify table exists
duckdb data/warehouse.duckdb "SELECT COUNT(*) FROM marts.revenue_by_month"
```

### Filters Not Working

**Common issues**:

1. **Field type mismatch**: Date filter on string column
   - Solution: Cast to date in SQL or dbt model

2. **Filter not connected to card**:
   - Edit dashboard → Click filter → Check connected cards

3. **NULL values**:
   - Filters may exclude NULLs
   - Handle in query: `COALESCE(column, 'Unknown')`

### Visualization Not Updating

**Force refresh**:

1. Open question from dashboard
2. Click **"Refresh"** (circular arrow)
3. Return to dashboard

**Clear cache**:

1. Admin → Troubleshooting
2. **"Clear cache"**

### Permission Issues

**Cannot edit dashboard**:

- Check collection permissions
- Admin → Permissions → Your group → Collection access

**Cannot see data**:

- Check database permissions
- Admin → Permissions → Your group → DuckDB access

---

## Example Workflow

### Building a Complete Dashboard

**Scenario**: Create weekly sales performance dashboard

#### Step 1: Plan Dashboard

**Purpose**: Track weekly sales metrics for sales team

**Questions needed**:
1. Total sales this week (number)
2. Sales vs. last week (% change)
3. Daily sales trend (line chart)
4. Top 5 products (bar chart)
5. Sales by region (bar chart)
6. Recent transactions (table)

#### Step 2: Prepare Data

Ensure dbt mart exists:

```sql
-- dbt/models/marts/sales_performance.sql
{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('day', created) as day,
    DATE_TRUNC('week', created) as week,
    product,
    region,
    amount,
    customer_id
FROM {{ ref('stg_orders') }}
WHERE status = 'completed'
```

Run transformations:
```bash
dango run
```

#### Step 3: Create Questions

Create each visualization:

**Q1: Total Sales This Week**
```sql
SELECT SUM(amount) as total_sales
FROM marts.sales_performance
WHERE week = DATE_TRUNC('week', CURRENT_DATE)
```
Visualization: Number

**Q2: Sales vs Last Week**
```sql
SELECT
    ROUND((this_week - last_week) / last_week * 100, 1) as growth_pct
FROM (
    SELECT
        SUM(CASE WHEN week = DATE_TRUNC('week', CURRENT_DATE)
            THEN amount END) as this_week,
        SUM(CASE WHEN week = DATE_TRUNC('week', CURRENT_DATE - INTERVAL 7 DAY)
            THEN amount END) as last_week
    FROM marts.sales_performance
)
```
Visualization: Number (with arrow)

**Q3-6**: Similar queries, save all as questions

#### Step 4: Build Dashboard

1. Create dashboard: "Sales - Weekly Performance"
2. Add all questions
3. Arrange in layout:
   ```
   [ Total Sales ] [ Growth % ] [ Goal Progress ]
   [        Daily Sales Trend (Line)           ]
   [ Top Products ] [ Sales by Region ]
   [        Recent Transactions (Table)        ]
   ```

#### Step 5: Add Filters

1. Date range filter (default: This week)
2. Region filter (optional)

#### Step 6: Share

1. Share link with sales team
2. Set up Monday morning email subscription
3. Enable auto-refresh (5 minutes)

Done! Sales team now has actionable dashboard.

---

## Next Steps

<div class="grid cards" markdown>

-   :material-code-tags: **SQL Queries**

    ---

    Write advanced SQL queries for DuckDB in Metabase.

    [:octicons-arrow-right-24: SQL Queries Guide](sql-queries.md)

-   :material-chart-box-outline: **Metabase Overview**

    ---

    Learn about Metabase features and configuration in Dango.

    [:octicons-arrow-right-24: Metabase Overview](metabase-overview.md)

-   :material-application-braces-outline: **Transformations**

    ---

    Create analytics-ready tables with dbt for better dashboards.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

-   :material-book-open-outline: **Metabase Docs**

    ---

    Explore official Metabase documentation for advanced features.

    [:octicons-arrow-right-24: Metabase Docs](https://www.metabase.com/docs/latest/)

</div>

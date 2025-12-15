# 📊 Data Structure Explanation

## Excel File: "Sales & Active Stores Data.xlsb"

### 📑 Sheets Overview

| Sheet Name             | Type          | Rows   | Status          | Why?                         |
| ---------------------- | ------------- | ------ | --------------- | ---------------------------- |
| **Sales Data Headers** | Documentation | 32     | ❌ Skip         | Just column explanations     |
| **Sales 2022 Onwards** | Raw Data      | 22,762 | ✅ **USE THIS** | Raw transactional data       |
| **Sales**              | Pivot Table   | 37     | ❌ Skip         | Pre-aggregated, not flexible |
| **Active Store**       | Pivot Table   | 832    | ❌ Skip         | Pre-aggregated, not flexible |

---

## ✅ Why We Use "Sales 2022 Onwards"

**It's raw transactional data** - each row is one invoice line item.

This gives us maximum flexibility:

- Filter by any combination (brand + month + year + region)
- Calculate active stores dynamically
- Aggregate however we want (sum, average, count)
- Answer any question the user asks

**Interview Talking Point:**

> "I chose the raw transactional data over the pivot tables because it gives us flexibility. Pivot tables are pre-aggregated for specific views, but with raw data, we can answer any question dynamically. For example, if someone asks 'Active stores for Lays in January 2024 in the North region', we can filter and count. With a pivot table, we'd be limited to pre-defined aggregations."

---

## 📋 Key Columns (After Cleaning)

### Original → Cleaned Names

| Original Name           | Cleaned Name                           | Type   | Example               | Purpose                        |
| ----------------------- | -------------------------------------- | ------ | --------------------- | ------------------------------ |
| Brand                   | `brand`                                | string | "Neo", "Delphy"       | Filter by brand                |
| Month                   | `month`                                | string | "JAN", "FEB"          | Filter by month                |
| Year                    | `year`                                 | int    | 2024, 2025            | Filter by year                 |
| Value                   | `value` / `sales`                      | float  | 148.00, 455.00        | Sales amount to aggregate      |
| Customer Account Number | `customer_account_number` / `store_id` | int    | 13365, 13518          | Count unique for active stores |
| Category                | `category`                             | string | "Snacks", "Beverages" | Filter by category             |
| Area                    | `area`                                 | string | "North", "South"      | Filter by region               |
| City                    | `city`                                 | string | "Dubai", "Abu Dhabi"  | Filter by city                 |

---

## 🗓️ Month Normalization

**Data format:** Months are stored as 3-letter uppercase codes

- JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC

**User queries:** Users might ask with full names

- "January", "February", "March", etc.

**Solution:** We normalize all month inputs to 3-letter format

```python
"January" → "JAN"
"jan" → "JAN"
"JAN" → "JAN"
```

This ensures queries work regardless of how users phrase the month.

---

## 🏪 Active Stores Calculation

**What is an "Active Store"?**

- A store with **NET SALES > 0** in a given period
- NOT just any transaction - must have positive net sales
- Excludes stores where returns cancel out or exceed purchases

**Important Business Logic:**

Excel defines active stores as: **"Stores with sales are counted as Active Stores"**

This means:

- ✅ Store with ₹1,000 sales = Active
- ✅ Store with ₹500 sales, ₹100 returns = Active (net: ₹400)
- ❌ Store with ₹100 sales, ₹100 returns = NOT Active (net: ₹0)
- ❌ Store with ₹100 sales, ₹150 returns = NOT Active (net: -₹50)

**How we calculate it (CORRECT METHOD):**

```python
# Example: Active stores for Lays in January 2024
filtered = df[
    (df['brand'] == 'Lays') &
    (df['month'] == 'JAN') &
    (df['year'] == 2024)
]

# STEP 1: Calculate net sales per store
store_net_sales = filtered.groupby('store_id')['sales'].sum()

# STEP 2: Count stores with positive net sales
active_stores = (store_net_sales > 0).sum()
```

**Why this matters:**

In Feb 2024 for Delphy:

- 66 stores had transactions
- 2 stores had negative net sales (returns exceeded purchases)
- **64 stores** were truly "active" (matches Excel)

**Why not use the "Active Store" sheet?**

- It's a pivot table with pre-calculated values
- We can't filter it dynamically (e.g., by region + brand + month)
- Calculating from raw data is more flexible and accurate
- Our calculation now matches Excel's business logic exactly

---

## 📊 Dataset Statistics

- **Total Rows:** 22,762 transactions
- **Date Range:** 2024 - 2025
- **Total Sales:** ₹8,334,523.93
- **Unique Brands:** 10
- **Unique Stores:** 801
- **Columns:** 32 (after cleaning: 34 with aliases)

---

## 🎯 Interview Key Points

1. **Why raw data over pivot tables?**

   - Flexibility to answer any question
   - Can filter by any combination of dimensions
   - Calculate aggregations dynamically

2. **Why normalize months?**

   - Data uses "JAN", users might say "January"
   - Ensures queries work regardless of input format
   - Simple mapping function handles all cases

3. **Why calculate active stores ourselves?**

   - More accurate (we control the logic)
   - More flexible (can filter before counting)
   - Easier to explain and debug

4. **Why Pandas instead of database?**
   - Dataset size (22K rows) fits easily in memory
   - Faster development (no schema, no SQL)
   - Simpler to explain and maintain
   - No SQL injection risk

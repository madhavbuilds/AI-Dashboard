from __future__ import annotations

from typing import Any

import pandas as pd


CANONICAL_COLUMNS = ["Date", "Product", "Revenue", "Units_Sold", "Region", "Customer"]
TEXT_FALLBACKS = {
    "Product": "General",
    "Region": "All Regions",
}
COLUMN_PATTERNS = {
    "Date": ["date", "order_date", "invoice_date", "transaction_date", "created_at", "timestamp", "day"],
    "Revenue": ["revenue", "sales", "amount", "total", "value", "gmv", "arr", "price"],
    "Product": ["product", "plan", "sku", "item", "package", "service"],
    "Units_Sold": ["units_sold", "units", "quantity", "qty", "seats", "licenses"],
    "Region": ["region", "territory", "market", "location", "zone", "country"],
    "Customer": ["customer", "client", "account", "company", "buyer"],
}


# Normalize column names so heuristic matching works consistently.
def _normalize_name(name: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in name).strip("_")


# Pick the first column whose normalized name contains any target pattern.
def _find_column_by_pattern(df: pd.DataFrame, canonical_name: str, used_columns: set[str]) -> str | None:
    patterns = COLUMN_PATTERNS[canonical_name]
    normalized_map = {column: _normalize_name(column) for column in df.columns}

    for column, normalized in normalized_map.items():
        if column in used_columns:
            continue
        if any(pattern in normalized for pattern in patterns):
            return column

    return None


# Infer a date column by checking which field parses cleanly to datetimes most often.
def _infer_date_column(df: pd.DataFrame, used_columns: set[str]) -> str | None:
    matched = _find_column_by_pattern(df, "Date", used_columns)
    if matched:
        return matched

    best_column = None
    best_score = 0.0

    for column in df.columns:
        if column in used_columns:
            continue

        parsed = pd.to_datetime(df[column], errors="coerce")
        score = parsed.notna().mean()

        if score > best_score and score >= 0.6:
            best_column = column
            best_score = score

    return best_column


# Infer the revenue field by favoring positive numeric columns with the largest total value.
def _infer_revenue_column(df: pd.DataFrame, used_columns: set[str]) -> str | None:
    matched = _find_column_by_pattern(df, "Revenue", used_columns)
    if matched:
        return matched

    numeric_candidates = []

    for column in df.columns:
        if column in used_columns:
            continue

        series = pd.to_numeric(df[column], errors="coerce")
        valid_ratio = series.notna().mean()

        if valid_ratio >= 0.7 and series.max(skipna=True) > 0:
            numeric_candidates.append((column, float(series.fillna(0).sum())))

    if not numeric_candidates:
        return None

    numeric_candidates.sort(key=lambda item: item[1], reverse=True)
    return numeric_candidates[0][0]


# Infer categorical business columns by preferring human-readable text fields with sensible cardinality.
def _infer_text_column(
    df: pd.DataFrame,
    canonical_name: str,
    used_columns: set[str],
    min_unique: int,
    max_unique: int,
) -> str | None:
    matched = _find_column_by_pattern(df, canonical_name, used_columns)
    if matched:
        return matched

    best_column = None
    best_score = -1

    for column in df.columns:
        if column in used_columns:
            continue

        series = df[column].dropna().astype(str).str.strip()
        unique_count = series.nunique()

        if not (min_unique <= unique_count <= max_unique):
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            continue

        score = len(series) - unique_count
        if score > best_score:
            best_column = column
            best_score = score

    return best_column


# Infer a units column from integer-like numeric data when it exists.
def _infer_units_column(df: pd.DataFrame, used_columns: set[str]) -> str | None:
    matched = _find_column_by_pattern(df, "Units_Sold", used_columns)
    if matched:
        return matched

    best_column = None
    best_score = -1.0

    for column in df.columns:
        if column in used_columns:
            continue

        series = pd.to_numeric(df[column], errors="coerce")
        valid_ratio = series.notna().mean()

        if valid_ratio < 0.7:
            continue

        non_null = series.dropna()
        if non_null.empty:
            continue

        integer_ratio = (non_null.mod(1).abs() < 1e-9).mean()
        if integer_ratio < 0.7:
            continue

        if non_null.mean() <= 0:
            continue

        score = integer_ratio - (non_null.mean() / max(non_null.max(), 1))
        if score > best_score:
            best_column = column
            best_score = score

    return best_column


# Build a canonical business dataset so the dashboard works across differently named CSV schemas.
def standardize_business_data(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = df.copy()
    used_columns: set[str] = set()
    inferred_columns: dict[str, str | None] = {}

    inferred_columns["Date"] = _infer_date_column(normalized_df, used_columns)
    if inferred_columns["Date"]:
        used_columns.add(inferred_columns["Date"])

    inferred_columns["Revenue"] = _infer_revenue_column(normalized_df, used_columns)
    if inferred_columns["Revenue"]:
        used_columns.add(inferred_columns["Revenue"])

    inferred_columns["Product"] = _infer_text_column(
        normalized_df,
        "Product",
        used_columns,
        min_unique=2,
        max_unique=max(6, min(len(normalized_df), 50)),
    )
    if inferred_columns["Product"]:
        used_columns.add(inferred_columns["Product"])

    inferred_columns["Region"] = _infer_text_column(
        normalized_df,
        "Region",
        used_columns,
        min_unique=2,
        max_unique=max(6, min(len(normalized_df), 20)),
    )
    if inferred_columns["Region"]:
        used_columns.add(inferred_columns["Region"])

    inferred_columns["Units_Sold"] = _infer_units_column(normalized_df, used_columns)
    if inferred_columns["Units_Sold"]:
        used_columns.add(inferred_columns["Units_Sold"])

    inferred_columns["Customer"] = _infer_text_column(
        normalized_df,
        "Customer",
        used_columns,
        min_unique=max(5, min(len(normalized_df), 20)),
        max_unique=max(20, len(normalized_df)),
    )

    standardized = pd.DataFrame(index=normalized_df.index)

    if inferred_columns["Date"]:
        standardized["Date"] = pd.to_datetime(normalized_df[inferred_columns["Date"]], errors="coerce")
    else:
        standardized["Date"] = pd.date_range(end=pd.Timestamp.today().normalize(), periods=len(normalized_df), freq="D")

    if inferred_columns["Revenue"]:
        standardized["Revenue"] = pd.to_numeric(normalized_df[inferred_columns["Revenue"]], errors="coerce")
    else:
        standardized["Revenue"] = 0.0

    if inferred_columns["Units_Sold"]:
        standardized["Units_Sold"] = pd.to_numeric(normalized_df[inferred_columns["Units_Sold"]], errors="coerce")
    else:
        standardized["Units_Sold"] = 1

    for column in ("Product", "Region", "Customer"):
        source_column = inferred_columns.get(column)
        if source_column:
            standardized[column] = normalized_df[source_column].astype(str).str.strip()
        elif column == "Customer":
            standardized[column] = [f"Customer {index + 1:03d}" for index in range(len(normalized_df))]
        else:
            standardized[column] = TEXT_FALLBACKS[column]

    standardized["Date"] = standardized["Date"].ffill().bfill()
    standardized["Revenue"] = standardized["Revenue"].fillna(0).clip(lower=0)
    standardized["Units_Sold"] = standardized["Units_Sold"].fillna(1).clip(lower=1).round().astype(int)
    standardized["Product"] = standardized["Product"].replace({"": TEXT_FALLBACKS["Product"]}).fillna(TEXT_FALLBACKS["Product"])
    standardized["Region"] = standardized["Region"].replace({"": TEXT_FALLBACKS["Region"]}).fillna(TEXT_FALLBACKS["Region"])
    standardized["Customer"] = standardized["Customer"].replace({"": "Unknown Customer"}).fillna("Unknown Customer")
    standardized = standardized[CANONICAL_COLUMNS].sort_values("Date").reset_index(drop=True)

    return standardized


# Load an uploaded CSV and return both the raw and canonical views used by the dashboard.
def load_dataset(uploaded_file: Any) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    if uploaded_file is None:
        raise ValueError("Please upload a CSV file to begin.")

    source_name = uploaded_file.name
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    raw_df = pd.read_csv(uploaded_file)
    if raw_df.empty:
        raise ValueError("The uploaded CSV is empty. Please upload a file with at least one row.")

    canonical_df = standardize_business_data(raw_df)
    return raw_df, canonical_df, source_name


# Apply sidebar filters so every metric and chart stays in sync with the selected slice.
def apply_filters(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    regions: list[str],
    products: list[str],
) -> pd.DataFrame:
    mask = df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))

    if regions:
        mask &= df["Region"].isin(regions)

    if products:
        mask &= df["Product"].isin(products)

    return df.loc[mask].copy()


# Calculate headline KPI values that power the dashboard metric cards.
def calculate_summary_metrics(df: pd.DataFrame) -> dict[str, Any]:
    total_revenue = float(df["Revenue"].sum())
    total_orders = int(len(df))
    average_order_value = float(total_revenue / total_orders) if total_orders else 0.0

    monthly_revenue = (
        df.set_index("Date")["Revenue"]
        .resample("MS")
        .sum()
        .reset_index()
    )

    growth_pct = 0.0
    if len(monthly_revenue) >= 2 and monthly_revenue["Revenue"].iloc[-2] != 0:
        current_revenue = monthly_revenue["Revenue"].iloc[-1]
        previous_revenue = monthly_revenue["Revenue"].iloc[-2]
        growth_pct = float(((current_revenue - previous_revenue) / previous_revenue) * 100)

    top_product = "N/A"
    if not df.empty:
        top_product = (
            df.groupby("Product", as_index=False)["Revenue"]
            .sum()
            .sort_values("Revenue", ascending=False)
            .iloc[0]["Product"]
        )

    best_month = "N/A"
    if not monthly_revenue.empty:
        best_row = monthly_revenue.sort_values("Revenue", ascending=False).iloc[0]
        best_month = pd.Timestamp(best_row["Date"]).strftime("%B %Y")

    return {
        "total_revenue": total_revenue,
        "growth_pct": growth_pct,
        "top_product": top_product,
        "total_orders": total_orders,
        "best_month": best_month,
        "average_order_value": average_order_value,
    }


# Aggregate revenue over time for the main trend visualization.
def get_revenue_trend(df: pd.DataFrame) -> pd.DataFrame:
    trend_df = (
        df.set_index("Date")["Revenue"]
        .resample("MS")
        .sum()
        .reset_index()
    )
    trend_df["Label"] = trend_df["Date"].dt.strftime("%b %Y")
    return trend_df


# Aggregate the best-selling products for the ranking chart.
def get_top_products(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    top_products_df = (
        df.groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(limit)
    )
    return top_products_df


# Aggregate revenue distribution across regions for the donut chart.
def get_revenue_by_region(df: pd.DataFrame) -> pd.DataFrame:
    region_df = (
        df.groupby("Region", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    return region_df


# Aggregate monthly order counts for the operational activity chart.
def get_monthly_orders(df: pd.DataFrame) -> pd.DataFrame:
    monthly_orders_df = (
        df.set_index("Date")
        .resample("MS")
        .size()
        .reset_index(name="Orders")
    )
    monthly_orders_df["Label"] = monthly_orders_df["Date"].dt.strftime("%b %Y")
    return monthly_orders_df


# Build all secondary tables in one place so the app can render them together.
def build_supporting_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "trend": get_revenue_trend(df),
        "top_products": get_top_products(df),
        "region_revenue": get_revenue_by_region(df),
        "monthly_orders": get_monthly_orders(df),
    }


# Create a concise text summary for the Groq prompt using the current filtered view.
def build_ai_context(metrics: dict[str, Any], tables: dict[str, pd.DataFrame]) -> str:
    top_products_lines = [
        f"- {row.Product}: {format_currency(row.Revenue)}"
        for row in tables["top_products"].itertuples(index=False)
    ]
    region_lines = [
        f"- {row.Region}: {format_currency(row.Revenue)}"
        for row in tables["region_revenue"].itertuples(index=False)
    ]
    monthly_order_lines = [
        f"- {row.Label}: {int(row.Orders)} orders"
        for row in tables["monthly_orders"].itertuples(index=False)
    ]

    context = "\n".join(
        [
            f"Total revenue: {format_currency(metrics['total_revenue'])}",
            f"Month over month growth: {metrics['growth_pct']:.2f}%",
            f"Top product: {metrics['top_product']}",
            f"Total orders: {metrics['total_orders']}",
            f"Average order value: {format_currency(metrics['average_order_value'])}",
            f"Best month: {metrics['best_month']}",
            "Top 5 products by revenue:",
            *top_products_lines,
            "Revenue by region:",
            *region_lines,
            "Monthly orders:",
            *monthly_order_lines,
        ]
    )
    return context


# Format currency values in a polished dashboard-friendly style.
def format_currency(value: float) -> str:
    return f"${value:,.0f}"


# Format numbers compactly for labels and summaries.
def format_compact_number(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"

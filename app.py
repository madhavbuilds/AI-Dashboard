from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from analysis import (
    apply_filters,
    build_ai_context,
    build_supporting_tables,
    calculate_summary_metrics,
    format_compact_number,
    format_currency,
    load_dataset,
)
from charts import (
    create_monthly_orders_chart,
    create_region_donut_chart,
    create_revenue_trend_chart,
    create_top_products_chart,
)
from insights import generate_ai_report
from styles import (
    APP_CSS,
    get_empty_card_html,
    get_upload_empty_state_html,
    get_hero_html,
    get_metric_card_html,
    get_report_card_html,
    get_section_header_html,
    get_sidebar_header_html,
)


st.set_page_config(
    page_title="AI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()


# Initialize Streamlit session keys used for uploader resets and AI report state.
def initialize_session_state() -> None:
    st.session_state.setdefault("uploader_nonce", 0)
    st.session_state.setdefault("ai_report", "")
    st.session_state.setdefault("ai_report_source", "")
    st.session_state.setdefault("ai_report_dataset", "")
    st.session_state.setdefault("ai_report_signature", "")


# Reset the dashboard back to its empty upload-first state.
def clear_dashboard() -> None:
    st.session_state["uploader_nonce"] += 1
    st.session_state["ai_report"] = ""
    st.session_state["ai_report_source"] = ""
    st.session_state["ai_report_dataset"] = ""
    st.session_state["ai_report_signature"] = ""


# Inject the global premium CSS layer before rendering the rest of the UI.
def inject_styles() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


# Normalize the Streamlit date picker output into an explicit start and end date pair.
def normalize_date_range(date_input: tuple[pd.Timestamp, pd.Timestamp] | list[pd.Timestamp] | pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    if isinstance(date_input, tuple) and len(date_input) == 2:
        return pd.Timestamp(date_input[0]), pd.Timestamp(date_input[1])
    if isinstance(date_input, list) and len(date_input) == 2:
        return pd.Timestamp(date_input[0]), pd.Timestamp(date_input[1])
    single_date = pd.Timestamp(date_input)
    return single_date, single_date


# Render the branded sidebar header and uploader before loading the active dataset.
def render_sidebar_upload() -> tuple[Any, bool]:
    st.sidebar.markdown(get_sidebar_header_html(), unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV",
        type=["csv"],
        help="Drag and drop any business or sales CSV.",
        key=f"csv_uploader_{st.session_state['uploader_nonce']}",
    )
    clear_clicked = False
    if uploaded_file is not None:
        clear_clicked = st.sidebar.button("Clear Dashboard", use_container_width=True)
    return uploaded_file, clear_clicked


# Render a sidebar message when filters are unavailable because no dataset has been uploaded yet.
def render_sidebar_waiting_state() -> None:
    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown(get_section_header_html("Filters", "Waiting For Data"), unsafe_allow_html=True)
    st.sidebar.markdown(
        get_empty_card_html("Upload a CSV to enable date, region, and product filters."),
        unsafe_allow_html=True,
    )


# Render the custom KPI row using HTML cards instead of the default Streamlit metric component.
def render_metric_cards(metrics: dict[str, float | str | int]) -> None:
    growth_value = float(metrics["growth_pct"])
    growth_arrow = "▲" if growth_value >= 0 else "▼"
    growth_class = "metric-positive" if growth_value >= 0 else "metric-negative"
    growth_copy = f"{growth_arrow} {abs(growth_value):.1f}% vs previous month"

    cards = [
        (
            "Total Revenue",
            format_currency(float(metrics["total_revenue"])),
            f"Avg order {format_currency(float(metrics['average_order_value']))}",
            "",
            "metric-value--compact",
        ),
        ("Growth", f"{growth_value:+.1f}%", growth_copy, growth_class, "metric-value--compact"),
        ("Top Product", str(metrics["top_product"]), f"Best month {metrics['best_month']}", "", "metric-value--text"),
        ("Total Orders", f"{int(metrics['total_orders']):,}", f"{format_compact_number(int(metrics['total_orders']))} orders in view", "", ""),
    ]

    columns = st.columns(4)
    for column, card in zip(columns, cards):
        label, value, meta, meta_class, value_class = card
        column.markdown(get_metric_card_html(label, value, meta, meta_class, value_class), unsafe_allow_html=True)


# Render the chart suite with a brief progress animation for a premium loading feel.
def render_charts(tables: dict[str, pd.DataFrame]) -> None:
    progress_bar = st.progress(0, text="Rendering interactive dashboard visuals...")
    for percent in (30, 65, 100):
        time.sleep(0.06)
        progress_bar.progress(percent, text="Rendering interactive dashboard visuals...")
    progress_bar.empty()

    st.markdown(get_section_header_html("Performance Visuals", "Interactive Charts"), unsafe_allow_html=True)

    revenue_fig = create_revenue_trend_chart(tables["trend"])
    st.plotly_chart(revenue_fig, use_container_width=True, config={"displayModeBar": False})

    left_column, right_column = st.columns([2, 1])
    with left_column:
        top_products_fig = create_top_products_chart(tables["top_products"])
        st.plotly_chart(top_products_fig, use_container_width=True, config={"displayModeBar": False})
    with right_column:
        region_fig = create_region_donut_chart(tables["region_revenue"])
        st.plotly_chart(region_fig, use_container_width=True, config={"displayModeBar": False})

    monthly_orders_fig = create_monthly_orders_chart(tables["monthly_orders"])
    st.plotly_chart(monthly_orders_fig, use_container_width=True, config={"displayModeBar": False})


# Animate the AI report into a styled card so it feels polished instead of abrupt.
def render_streaming_report(report_text: str, source_label: str) -> None:
    placeholder = st.empty()
    streamed_words: list[str] = []

    for word in report_text.split():
        streamed_words.append(word)
        streamed_text = " ".join(streamed_words)
        placeholder.markdown(
            get_report_card_html(streamed_text, source_label, show_caret=True),
            unsafe_allow_html=True,
        )
        time.sleep(0.025)

    placeholder.markdown(get_report_card_html(report_text, source_label), unsafe_allow_html=True)


# Build the sidebar filter suite that drives every metric and chart in the app.
def render_sidebar_filters(df: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp, list[str], list[str]]:
    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown(get_section_header_html("Filters", "Refine View"), unsafe_allow_html=True)

    min_date = pd.Timestamp(df["Date"].min()).date()
    max_date = pd.Timestamp(df["Date"].max()).date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    start_date, end_date = normalize_date_range(date_range)

    all_regions = sorted(df["Region"].dropna().unique().tolist())
    all_products = sorted(df["Product"].dropna().unique().tolist())

    selected_regions = st.sidebar.multiselect("Region", options=all_regions, default=all_regions)
    selected_products = st.sidebar.multiselect("Product", options=all_products, default=all_products)

    return start_date, end_date, selected_regions, selected_products


# Render the upload-first landing view before any dataset is available.
def render_empty_dashboard() -> None:
    st.markdown(get_hero_html("No dataset loaded", 0, 0), unsafe_allow_html=True)
    st.markdown(get_section_header_html("Upload Your Data", "Ready When You Are"), unsafe_allow_html=True)
    st.markdown(get_upload_empty_state_html(), unsafe_allow_html=True)

    guidance_columns = st.columns(3)
    guidance_cards = [
        "Recommended columns: Date, Revenue, Product, Region, Units, Customer. Exact names are not required.",
        "Accepted input: any CSV with business or sales rows. The app standardizes common naming variations automatically.",
        "Once uploaded, every metric, chart, and AI insight responds to your active filters in real time.",
    ]
    for column, card in zip(guidance_columns, guidance_cards):
        column.markdown(get_empty_card_html(card), unsafe_allow_html=True)


# Orchestrate the full dashboard experience from data load through charts and AI insights.
def main() -> None:
    initialize_session_state()
    inject_styles()

    uploaded_file, clear_clicked = render_sidebar_upload()
    if clear_clicked:
        clear_dashboard()
        st.rerun()

    if uploaded_file is None:
        render_sidebar_waiting_state()
        render_empty_dashboard()
        return

    try:
        raw_df, canonical_df, dataset_name = load_dataset(uploaded_file)
    except Exception as exc:
        render_sidebar_waiting_state()
        st.markdown(get_hero_html("Upload error", 0, 0), unsafe_allow_html=True)
        st.markdown(get_section_header_html("Could Not Read File", "Upload A Valid CSV"), unsafe_allow_html=True)
        st.markdown(
            get_empty_card_html(
                f"The uploaded file could not be processed. Please upload a valid CSV with tabular business data. Details: {exc}"
            ),
            unsafe_allow_html=True,
        )
        return

    start_date, end_date, selected_regions, selected_products = render_sidebar_filters(canonical_df)
    current_signature = "|".join(
        [
            dataset_name,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            ",".join(selected_regions),
            ",".join(selected_products),
        ]
    )

    filtered_df = apply_filters(canonical_df, start_date, end_date, selected_regions, selected_products)

    st.markdown(get_hero_html(dataset_name, len(filtered_df), len(raw_df.columns)), unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="caption-row">
            <span>Showing a filtered business view from <strong>{start_date.strftime("%d %b %Y")}</strong> to <strong>{end_date.strftime("%d %b %Y")}</strong>.</span>
            <span>{len(filtered_df):,} rows after filters</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Preview dataset", expanded=False):
        st.dataframe(raw_df.head(20), use_container_width=True, hide_index=True)

    if filtered_df.empty:
        st.markdown(
            get_empty_card_html("No records match the current filters. Adjust the date, region, or product selections to continue."),
            unsafe_allow_html=True,
        )
        return

    metrics = calculate_summary_metrics(filtered_df)
    tables = build_supporting_tables(filtered_df)

    st.markdown(get_section_header_html("Executive Snapshot", "Headline Metrics"), unsafe_allow_html=True)
    render_metric_cards(metrics)
    render_charts(tables)

    st.markdown(get_section_header_html("AI Report", "Groq Insights"), unsafe_allow_html=True)

    if st.session_state["ai_report_signature"] != current_signature:
        st.session_state["ai_report"] = ""
        st.session_state["ai_report_source"] = ""
        st.session_state["ai_report_dataset"] = dataset_name
        st.session_state["ai_report_signature"] = current_signature

    if not st.session_state["ai_report"]:
        st.markdown(
            get_empty_card_html(
                "Generate a focused executive summary with wins, risks, and next actions tailored to the current filtered slice."
            ),
            unsafe_allow_html=True,
        )

    if st.button("Generate AI Report", use_container_width=True):
        summary_text = build_ai_context(metrics, tables)
        with st.spinner("Analyzing with Groq AI..."):
            report_text, source_label = generate_ai_report(summary_text)

        st.session_state["ai_report"] = report_text
        st.session_state["ai_report_source"] = source_label
        st.session_state["ai_report_dataset"] = dataset_name
        st.session_state["ai_report_signature"] = current_signature
        render_streaming_report(report_text, source_label)

    elif st.session_state["ai_report"]:
        st.markdown(
            get_report_card_html(
                st.session_state["ai_report"],
                st.session_state["ai_report_source"],
            ),
            unsafe_allow_html=True,
        )

    if st.session_state["ai_report"]:
        st.download_button(
            "Download Full Report",
            data=st.session_state["ai_report"],
            file_name=f"{Path(st.session_state['ai_report_dataset']).stem}_ai_report.txt",
            mime="text/plain",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()

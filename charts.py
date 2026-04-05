from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


COLOR_SEQUENCE = ["#00ff88", "#7c6bff", "#ff6b35", "#00c8ff", "#f4d35e"]
PLOT_BACKGROUND = "#111118"
PAPER_BACKGROUND = "#111118"
GRID_COLOR = "#1e1e2e"


# Apply the shared dark visual system so every chart feels like one premium product.
def _apply_chart_theme(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        title=title,
        paper_bgcolor=PAPER_BACKGROUND,
        plot_bgcolor=PLOT_BACKGROUND,
        font={"color": "#e6e6f0", "family": "Inter, sans-serif"},
        title_font={"size": 18, "color": "#ffffff"},
        margin={"l": 20, "r": 20, "t": 56, "b": 20},
        hovermode="x unified",
        hoverlabel={
            "bgcolor": "#0d0d12",
            "bordercolor": GRID_COLOR,
            "font": {"color": "#ffffff"},
        },
        legend={"bgcolor": "rgba(0,0,0,0)", "borderwidth": 0},
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, showline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, zeroline=False, showline=False)
    return fig


# Create the main revenue trend chart using a smoothed line with a soft filled area.
def create_revenue_trend_chart(trend_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend_df["Date"],
            y=trend_df["Revenue"],
            mode="lines+markers",
            name="Revenue",
            line={"color": COLOR_SEQUENCE[0], "width": 4, "shape": "spline", "smoothing": 1.0},
            marker={"size": 8, "color": COLOR_SEQUENCE[0], "line": {"width": 0}},
            fill="tozeroy",
            fillcolor="rgba(0, 255, 136, 0.10)",
            hovertemplate="%{x|%b %Y}<br>Revenue: $%{y:,.0f}<extra></extra>",
        )
    )
    fig = _apply_chart_theme(fig, "Revenue Trend Over Time")
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Revenue")
    return fig


# Create a ranked horizontal bar chart for the top-performing products.
def create_top_products_chart(top_products_df: pd.DataFrame) -> go.Figure:
    chart_df = top_products_df.sort_values("Revenue", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=chart_df["Revenue"],
            y=chart_df["Product"],
            orientation="h",
            marker={"color": COLOR_SEQUENCE[: len(chart_df)]},
            hovertemplate="%{y}<br>Revenue: $%{x:,.0f}<extra></extra>",
        )
    )
    fig = _apply_chart_theme(fig, "Top 5 Products")
    fig.update_layout(showlegend=False, hovermode="y")
    fig.update_xaxes(title_text="Revenue")
    fig.update_yaxes(title_text="")
    return fig


# Create a donut chart that shows how revenue is distributed across regions.
def create_region_donut_chart(region_df: pd.DataFrame) -> go.Figure:
    fig = px.pie(
        region_df,
        names="Region",
        values="Revenue",
        hole=0.68,
        color="Region",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig = _apply_chart_theme(fig, "Revenue By Region")
    fig.update_traces(
        textinfo="percent",
        textfont={"color": "#ffffff"},
        marker={"line": {"color": PLOT_BACKGROUND, "width": 2}},
        hovertemplate="%{label}<br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )
    fig.update_layout(showlegend=True)
    return fig


# Create the monthly order activity chart to complement the revenue trend.
def create_monthly_orders_chart(monthly_orders_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=monthly_orders_df["Date"],
            y=monthly_orders_df["Orders"],
            marker={"color": COLOR_SEQUENCE[3]},
            hovertemplate="%{x|%b %Y}<br>Orders: %{y}<extra></extra>",
        )
    )
    fig = _apply_chart_theme(fig, "Monthly Orders")
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Orders")
    return fig

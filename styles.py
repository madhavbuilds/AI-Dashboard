from __future__ import annotations

from html import escape


APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Syne:wght@500;700;800&display=swap');

:root {
    --bg-main: #08080d;
    --bg-sidebar: #0f0f13;
    --bg-card: #111118;
    --border: #1e1e2e;
    --text-main: #ffffff;
    --text-muted: #8f90a6;
    --accent: #00ff88;
    --accent-soft: rgba(0, 255, 136, 0.14);
    --shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top right, rgba(0, 255, 136, 0.08), transparent 28%),
        radial-gradient(circle at top left, rgba(124, 107, 255, 0.10), transparent 24%),
        linear-gradient(180deg, #09090f 0%, var(--bg-main) 100%);
    color: var(--text-main);
}

[data-testid="stAppViewBlockContainer"] {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top, rgba(0, 255, 136, 0.08), transparent 20%),
        var(--bg-sidebar);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text-main);
}

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", sans-serif;
}

h1, h2, h3, .syne-font {
    font-family: "Syne", "Inter", sans-serif !important;
}

.block-container {
    padding-top: 1.5rem;
}

.hero-card {
    background: linear-gradient(135deg, rgba(17, 17, 24, 0.94), rgba(10, 10, 14, 0.98));
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 1.6rem 1.8rem;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
    margin-bottom: 1.35rem;
}

.hero-card::after {
    content: "";
    position: absolute;
    inset: auto -10% -55% auto;
    width: 240px;
    height: 240px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(0, 255, 136, 0.18), transparent 60%);
}

.hero-eyebrow {
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.28em;
    font-size: 0.72rem;
    margin-bottom: 0.75rem;
}

.hero-title {
    color: var(--text-main);
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.6rem;
}

.hero-subtitle {
    color: #d9daeb;
    max-width: 780px;
    line-height: 1.7;
    margin-bottom: 1.1rem;
}

.hero-pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.7rem;
}

.hero-pill {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.55rem 0.95rem;
    color: #d5d6e7;
    font-size: 0.9rem;
}

.sidebar-brand {
    padding: 0.4rem 0 1.1rem 0;
}

.sidebar-title {
    font-family: "Syne", sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text-main);
    margin-bottom: 0.35rem;
}

.live-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    color: #cfd0df;
    font-size: 0.88rem;
    margin-bottom: 1rem;
}

.live-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 0 6px rgba(0, 255, 136, 0.12);
}

.section-header {
    border-left: 3px solid var(--accent);
    padding-left: 0.9rem;
    margin: 1.5rem 0 1rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    padding-bottom: 0.8rem;
}

.section-kicker {
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.22em;
    font-size: 0.74rem;
    margin-bottom: 0.35rem;
}

.section-title {
    color: var(--text-main);
    text-transform: uppercase;
    letter-spacing: 0.16em;
    font-size: 1rem;
    font-weight: 700;
}

.metric-card {
    background: linear-gradient(180deg, rgba(17, 17, 24, 0.98), rgba(10, 10, 15, 0.98));
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 16px;
    padding: 1.15rem 1.2rem;
    min-height: 156px;
    box-shadow: var(--shadow);
    transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0, 255, 136, 0.28);
    background: linear-gradient(180deg, rgba(18, 18, 27, 1), rgba(12, 12, 18, 1));
}

.metric-label {
    color: var(--text-muted);
    font-size: 0.82rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
}

.metric-value {
    color: var(--text-main);
    font-size: clamp(1.55rem, 1.6vw + 0.8rem, 2.45rem);
    line-height: 1;
    font-weight: 700;
    font-family: "Space Grotesk", "Inter", sans-serif;
    letter-spacing: -0.05em;
    margin-bottom: 0.55rem;
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: break-word;
    text-wrap: balance;
}

.metric-value--compact {
    font-size: clamp(1.45rem, 1.35vw + 0.8rem, 2.15rem);
}

.metric-value--text {
    font-size: clamp(1.25rem, 1vw + 0.9rem, 1.95rem);
    line-height: 1.08;
    max-width: 100%;
}

.metric-meta {
    color: #cfd0de;
    font-size: 0.92rem;
    line-height: 1.45;
    overflow-wrap: anywhere;
}

.metric-positive {
    color: var(--accent);
}

.metric-negative {
    color: #ff7a7a;
}

.report-shell {
    background: linear-gradient(180deg, rgba(17, 17, 24, 0.98), rgba(9, 9, 13, 1));
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 18px;
    padding: 1.35rem 1.45rem;
    box-shadow: var(--shadow);
}

.report-meta {
    color: var(--accent);
    font-size: 0.78rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.85rem;
}

.report-text {
    color: #ebebf5;
    line-height: 1.8;
    font-size: 1rem;
    white-space: pre-wrap;
}

.report-caret {
    display: inline-block;
    width: 10px;
    color: var(--accent);
    animation: blink 1s steps(1) infinite;
}

@keyframes blink {
    50% { opacity: 0; }
}

.empty-card {
    background: rgba(17, 17, 24, 0.82);
    border: 1px dashed rgba(0, 255, 136, 0.24);
    border-radius: 18px;
    padding: 1.3rem;
    color: #cbccda;
}

.empty-state-shell {
    background: linear-gradient(180deg, rgba(17, 17, 24, 0.96), rgba(9, 9, 13, 0.98));
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 1.6rem 1.7rem;
    box-shadow: var(--shadow);
    margin-top: 0.8rem;
}

.empty-state-title {
    font-family: "Syne", sans-serif;
    font-size: 1.8rem;
    color: var(--text-main);
    margin-bottom: 0.65rem;
}

.empty-state-copy {
    color: #d0d1e0;
    line-height: 1.8;
    max-width: 760px;
}

.empty-state-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-top: 1.2rem;
}

.empty-state-panel {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1rem 1.05rem 1rem;
}

.empty-state-label {
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-size: 0.72rem;
    margin-bottom: 0.55rem;
}

.empty-state-panel strong {
    display: block;
    color: var(--text-main);
    margin-bottom: 0.4rem;
}

.empty-state-panel span {
    color: #c7c8d8;
    line-height: 1.65;
    font-size: 0.95rem;
}

@media (max-width: 1200px) {
    .metric-card {
        min-height: 148px;
    }

    .metric-value {
        font-size: clamp(1.35rem, 1.15vw + 0.8rem, 2rem);
    }

    .metric-value--text {
        font-size: clamp(1.15rem, 0.9vw + 0.8rem, 1.7rem);
    }
}

.caption-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    color: var(--text-muted);
    font-size: 0.9rem;
    margin: 0.65rem 0 0.25rem 0;
}

.sidebar-footnote {
    color: var(--text-muted);
    font-size: 0.82rem;
    padding-top: 1rem;
}

.sidebar-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.06);
    margin: 1rem 0 1rem 0;
}

.stFileUploader, .stDateInput, .stSelectbox, .stMultiSelect, .stExpander, .stDataFrame {
    background: transparent;
}

[data-testid="stFileUploaderDropzone"] {
    background: rgba(17, 17, 24, 0.96);
    border: 1px dashed rgba(0, 255, 136, 0.28);
    border-radius: 16px;
    padding: 1rem 0.8rem;
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stDateInput > div > div,
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(17, 17, 24, 0.96) !important;
    border-color: var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 12px !important;
}

.stButton > button,
.stDownloadButton > button {
    width: 100%;
    border-radius: 14px;
    border: 1px solid rgba(0, 255, 136, 0.35);
    background: linear-gradient(180deg, #00ff88, #00d974);
    color: #03150d;
    font-weight: 800;
    letter-spacing: 0.04em;
    min-height: 3rem;
    box-shadow: 0 10px 30px rgba(0, 255, 136, 0.18);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: rgba(0, 255, 136, 0.65);
    background: linear-gradient(180deg, #2bff9f, #00eb80);
    color: #020f0a;
}

.stProgress > div > div > div > div {
    background-color: var(--accent);
}

[data-testid="stSpinner"] {
    color: var(--accent);
}

.stAlert {
    background: rgba(17, 17, 24, 0.95);
    border: 1px solid var(--border);
    color: var(--text-main);
}
</style>
"""


# Create the premium hero banner shown at the top of the dashboard.
def get_hero_html(dataset_name: str, row_count: int, column_count: int) -> str:
    return f"""
    <div class="hero-card">
        <div class="hero-eyebrow">AI Business Intelligence</div>
        <div class="hero-title">Executive Analytics Console</div>
        <div class="hero-subtitle">
            Upload a business dataset, explore interactive performance visuals, and turn raw rows into
            plain-English recommendations powered by Groq AI.
        </div>
        <div class="hero-pill-row">
            <div class="hero-pill">Dataset: {escape(dataset_name)}</div>
            <div class="hero-pill">Rows: {row_count:,}</div>
            <div class="hero-pill">Columns: {column_count:,}</div>
            <div class="hero-pill">Interactive Plotly visuals</div>
        </div>
    </div>
    """


# Create the branded sidebar header with the requested live status indicator.
def get_sidebar_header_html() -> str:
    return """
    <div class="sidebar-brand">
        <div class="sidebar-title">AI Dashboard</div>
        <div class="live-indicator">
            <span class="live-dot"></span>
            <span>Live</span>
        </div>
    </div>
    """


# Create the shared section header style used throughout the page.
def get_section_header_html(title: str, kicker: str) -> str:
    return f"""
    <div class="section-header">
        <div class="section-kicker">{escape(kicker)}</div>
        <div class="section-title">{escape(title)}</div>
    </div>
    """


# Create a custom KPI card that matches the premium dashboard styling.
def get_metric_card_html(
    label: str,
    value: str,
    meta: str,
    meta_class: str = "",
    value_class: str = "",
) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{escape(label)}</div>
        <div class="metric-value {value_class}">{escape(value)}</div>
        <div class="metric-meta {meta_class}">{meta}</div>
    </div>
    """


# Create the AI report container with an optional typewriter caret during streaming.
def get_report_card_html(report_text: str, source_label: str, show_caret: bool = False) -> str:
    caret = '<span class="report-caret">|</span>' if show_caret else ""
    return f"""
    <div class="report-shell">
        <div class="report-meta">{escape(source_label)}</div>
        <div class="report-text">{escape(report_text)}{caret}</div>
    </div>
    """


# Create a subdued placeholder card for empty states and setup guidance.
def get_empty_card_html(message: str) -> str:
    return f'<div class="empty-card">{escape(message)}</div>'


# Create the upload-first empty state so the app feels intentional before any data is added.
def get_upload_empty_state_html() -> str:
    return """
    <div class="empty-state-shell">
        <div class="hero-eyebrow">Upload Required</div>
        <div class="empty-state-title">Start with your own CSV</div>
        <div class="empty-state-copy">
            This dashboard now opens empty by design. Upload any business or sales CSV from the sidebar to unlock
            automatic column detection, KPI cards, interactive charts, and a Groq-powered executive report built
            from your actual data.
        </div>
        <div class="empty-state-grid">
            <div class="empty-state-panel">
                <div class="empty-state-label">Step 1</div>
                <strong>Upload a CSV</strong>
                <span>Drag and drop your file in the sidebar. Date, revenue, product, region, and customer columns are detected automatically when possible.</span>
            </div>
            <div class="empty-state-panel">
                <div class="empty-state-label">Step 2</div>
                <strong>Refine the view</strong>
                <span>After upload, date, region, and product filters appear so every KPI and chart can update dynamically.</span>
            </div>
            <div class="empty-state-panel">
                <div class="empty-state-label">Step 3</div>
                <strong>Generate insights</strong>
                <span>Use the AI report action to turn the filtered summary into a concise executive brief you can download as TXT.</span>
            </div>
        </div>
    </div>
    """

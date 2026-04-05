# AI Business Data Dashboard

A premium Streamlit dashboard for business and sales CSVs with polished dark UI, interactive Plotly visuals, automated Pandas analysis, and Groq-powered executive reporting.

## What You Get

- Drag-and-drop CSV upload with automatic schema detection
- Beautiful dark UI with custom CSS, premium cards, and hidden default Streamlit chrome
- Interactive Plotly charts for revenue trend, product performance, region mix, and monthly orders
- Sidebar filters for date range, region, and product
- AI executive report powered by Groq `llama3-70b-8192`
- TXT download for the generated report
- Upload-first experience with a clean empty state and dynamic filters after data is loaded

## Project Structure

- `app.py`: Streamlit app entry point and UI layout
- `analysis.py`: data cleaning, schema detection, filtering, and KPI logic
- `charts.py`: Plotly figure builders and shared theme settings
- `insights.py`: Groq report generation and demo fallback
- `styles.py`: premium CSS and HTML helper blocks
- `sample_data.csv`: optional sample dataset for manual testing
- `.env.example`: environment variable template

## Local Setup

1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your Groq API key in `.env`:

```env
GROQ_API_KEY=your-key-here
```

4. Launch the app:

```bash
streamlit run app.py
```

## Groq Integration

The AI report uses `llama3-70b-8192` through the Groq Python SDK. If no API key is configured, the app still runs and returns a polished demo report so the experience remains fully explorable.

## Screenshots Description

- Hero section: glossy executive banner with dataset pills and live context
- KPI row: four premium metric cards with green accent borders and hover lift
- Charts section: full-width revenue trend, split product and regional analysis, plus monthly orders
- AI section: typewriter-style report reveal inside a dark insight card with green accent border

## Deploy Options

### Streamlit Community Cloud

1. Push this project to a Git repository.
2. In Streamlit Community Cloud, create a new app and point it to `app.py`.
3. Add `GROQ_API_KEY` as a secret or environment variable.
4. Deploy.

### Local or VM Deployment

1. Install Python and the dependencies from `requirements.txt`.
2. Export `GROQ_API_KEY` or place it in `.env`.
3. Start with `streamlit run app.py`.
4. Reverse-proxy behind Nginx or Caddy if you want a production URL.

## Notes

- The dashboard starts empty and waits for a CSV upload.
- Filters update every KPI and chart together.
- The app standardizes common business column names automatically, so uploaded CSV schemas can vary.
# AI-Dashboard

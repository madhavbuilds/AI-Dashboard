from __future__ import annotations

import os
import re
from typing import Iterator

from dotenv import load_dotenv


# Build a demo report so the app still feels complete when no Groq key is configured yet.
def _build_demo_report(summary_text: str) -> str:
    total_revenue = re.search(r"Total revenue: (.+)", summary_text)
    growth = re.search(r"Month over month growth: (.+)", summary_text)
    top_product = re.search(r"Top product: (.+)", summary_text)
    best_month = re.search(r"Best month: (.+)", summary_text)

    revenue_value = total_revenue.group(1) if total_revenue else "the current dataset"
    growth_value = growth.group(1) if growth else "steady"
    top_product_value = top_product.group(1) if top_product else "the leading offer"
    best_month_value = best_month.group(1) if best_month else "the strongest month in view"

    return (
        f"Executive snapshot: the business generated {revenue_value} in the selected view, with month over month "
        f"growth landing at {growth_value}. {top_product_value} is leading the portfolio, which suggests the core "
        "offer is doing the heavy lifting and is likely the clearest lever for predictable expansion. Momentum looks "
        f"strongest in {best_month_value}, so that period is a useful benchmark for what healthy demand, pricing, and "
        "sales execution should look like.\n\nWhat is performing well: the revenue mix shows that buyers are still "
        "responding to the flagship product set, and order volume indicates the funnel is generating enough activity "
        "to support scale. What needs attention: concentration risk is likely building if one product or one region is "
        "carrying too much of the result, and softer periods in the trend line should be reviewed for channel, pricing, "
        "or retention issues.\n\nRecommended actions: first, double down on the top product with a focused upsell or "
        "bundle strategy. Second, audit the weakest month and lowest-performing segment to identify friction in demand "
        "generation or deal conversion. Third, use the best month as the operating baseline and replicate the campaign, "
        "sales, and pricing inputs that produced that peak."
    )


# Send the current dashboard summary to Groq and return a polished executive report.
def generate_ai_report(summary_text: str) -> tuple[str, str]:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key == "your-key-here":
        return _build_demo_report(summary_text), "Demo mode"

    try:
        from groq import Groq
    except ModuleNotFoundError:
        return _build_demo_report(summary_text), "Demo mode (groq package missing)"

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        temperature=0.45,
        messages=[
            {
                "role": "system",
                "content": "You are an elite business analyst writing concise, executive-ready reporting.",
            },
            {
                "role": "user",
                "content": (
                    "You are a business analyst. Given this data summary, write a 200-word executive report. "
                    "Include: what is performing well, what needs attention, 3 specific action recommendations. "
                    "Be direct and insightful.\n\n"
                    f"{summary_text}"
                ),
            },
        ],
    )
    report = response.choices[0].message.content.strip()
    return report, "Groq llama3-70b-8192"


# Yield report text word by word so the UI can animate a typewriter reveal.
def stream_words(text: str) -> Iterator[str]:
    for word in text.split():
        yield f"{word} "

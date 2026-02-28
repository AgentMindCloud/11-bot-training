"""Prompt templates for the Competitor Analysis bot."""

EXTRACT_COMPETITOR_DATA_PROMPT = """You are a restaurant business analyst. Extract structured data from the following website content.

URL: {url}
Restaurant we're analysing for: {our_restaurant_name}

Website text:
\"\"\"
{website_text}
\"\"\"

Extract all available information and return a JSON object with:
- "name": restaurant name
- "url": the URL provided
- "cuisine": cuisine type if mentioned
- "price_range": price range (e.g. "$", "$$", "$$$") if mentioned
- "menu_items": list of objects with "name", "description", "price", "category" (null if not available)
- "usps": list of unique selling points / differentiators mentioned
- "delivery_platforms": list of delivery services mentioned (UberEats, DoorDash, etc.)
- "promotions": list of current promotions or deals mentioned

If information is not available, use null or empty list. Extract what you can.
"""

COMPARE_COMPETITORS_PROMPT = """You are a restaurant business strategy consultant.

Our restaurant:
{our_restaurant_json}

Competitor profile:
{competitor_json}

Compare them across key business dimensions. Return a JSON object with:
- "our_restaurant": our restaurant name
- "competitor": the full competitor profile object (pass through as-is)
- "comparison_axes": dict mapping dimension names to comparison text strings, covering:
  * "pricing": how pricing compares
  * "cuisine_overlap": how much the menus overlap
  * "differentiators": what makes each unique
  * "delivery_presence": delivery platform comparison
  * "promotions": promotional strategy comparison
  * "opportunities": gaps we can exploit
- "summary": 2-3 sentence executive summary of the comparison
"""

GENERATE_REPORT_PROMPT = """You are a restaurant marketing consultant writing an executive report.

Restaurant: {restaurant_name}
Analysis date: {analysis_date}

Competitor comparisons (JSON):
{comparisons_json}

Write a comprehensive competitor analysis report in Markdown format. Include:
# Competitor Analysis Report
## Executive Summary
## Market Landscape
## Individual Competitor Profiles (one section per competitor)
## Competitive Gaps & Opportunities
## Recommended Actions

Be specific, data-driven, and actionable. Use the data provided.
"""

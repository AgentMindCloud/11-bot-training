"""Prompt templates for the Link Building bot."""

PROSPECT_DISCOVERY_PROMPT = """You are a link-building specialist for local businesses.

Target business:
- Restaurant name: {restaurant_name}
- City: {city}
- Cuisine: {cuisine}
- Keywords: {keywords_list}

Identify potential link-building targets that would likely link to or feature this restaurant.
Think about: local food bloggers, neighbourhood guides, city tourism sites, food review sites,
local news outlets, event listing sites, culinary schools, community directories.

Return a JSON object with key "prospects" containing a list of objects, each with:
- "url": the website URL (realistic, plausible URL)
- "email": guessed contact email if known pattern, else null
- "contact_name": typical contact person title/name if obvious, else null
- "domain_authority_estimate": estimated DA score 1-100
- "relevance_score": float 0.0-1.0 how relevant this site is
- "notes": why this is a good prospect
- "status": always "prospect"

Return at least 8 diverse prospects.
"""

OUTREACH_EMAIL_PROMPT = """You are a professional outreach specialist writing personalised link-building emails.

Restaurant:
- Name: {restaurant_name}
- City: {city}
- Cuisine: {cuisine}
- Website: {restaurant_website}

Target prospect:
- URL: {prospect_url}
- Notes: {prospect_notes}

Write a warm, personalised outreach email that:
1. Opens with a genuine compliment about their site/content
2. Briefly introduces the restaurant
3. Proposes a natural link/feature opportunity
4. Is concise (under 200 words)
5. Ends with a clear, low-pressure call-to-action

Return a JSON object with:
- "prospect_url": the target URL
- "subject": email subject line (under 60 characters)
- "body": full email body text
"""

"""Prompt templates for the Local SEO bot."""

KEYWORD_RESEARCH_PROMPT = """You are an expert local SEO consultant specialising in restaurant marketing.

Generate a comprehensive set of keyword clusters for a restaurant with the following details:
- Restaurant name: {restaurant_name}
- City: {city}
- Neighborhood: {neighborhood}
- Cuisine type: {cuisine}

Return a JSON object with a single key "keyword_clusters" whose value is a list of objects, each with:
- "keyword": the primary keyword phrase
- "variations": list of 3-5 related keyword variations
- "search_intent": one of "informational", "navigational", "transactional", "local"
- "monthly_volume_estimate": estimated monthly search volume (integer)

Focus on high-intent local search terms, cuisine-specific terms, and neighborhood/city combos.
Return at least 8 keyword clusters covering different aspects (e.g. delivery, dine-in, cuisine type, occasion).
"""

SEO_META_PROMPT = """You are an expert on-page SEO specialist for local businesses.

Restaurant details:
- Name: {restaurant_name}
- City: {city}
- Neighborhood: {neighborhood}
- Cuisine: {cuisine}

Target keyword clusters (JSON):
{keyword_clusters_json}

Pages to optimise:
{pages_list}

For each page, return a JSON object with key "seo_metas" containing a list of objects, each with:
- "page_type": the page name/type
- "title_tag": SEO-optimised title tag (50-60 characters)
- "meta_description": compelling meta description (150-160 characters)
- "h1": primary H1 heading
- "target_keywords": list of 2-4 target keywords for this page

Make every title/description unique, local, and click-worthy.
"""

INTERNAL_LINKS_PROMPT = """You are an internal linking SEO expert.

Restaurant: {restaurant_name} ({cuisine}, {city})

Available pages and their content summaries:
{content_map_json}

Suggest internal link opportunities. Return a JSON object with key "internal_links" containing a list of objects, each with:
- "source_page": page where the link should be placed
- "target_page": page the link should point to
- "anchor_text": exact anchor text to use (keyword-rich)
- "reason": brief explanation of why this link helps SEO

Aim for at least 6 link suggestions that improve crawlability and keyword authority.
"""

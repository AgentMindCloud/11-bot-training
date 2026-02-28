"""Prompt templates for the Trend Tracking bot."""

TREND_ANALYSIS_PROMPT = """You are a restaurant industry trend analyst.

Restaurant context:
- Name: {restaurant_name}
- City: {city}
- Cuisine: {cuisine}

Recent news headlines and summaries:
{headlines_text}

Analyse these headlines and identify the most relevant trends for this restaurant. For each trend:
1. Determine how relevant it is to a local restaurant business
2. Summarise the trend clearly

Return a JSON object with key "trends" containing a list of objects, each with:
- "topic": trend topic name
- "source": where this trend was spotted (headline source)
- "summary": 2-3 sentence summary of the trend
- "relevance_score": float 0.0-1.0 (how relevant to a local restaurant)
- "actionable_ideas": empty list (will be filled separately)

Only include trends with relevance_score >= 0.5. Return at least 5 trends if available.
"""

ACTIONABLE_IDEAS_PROMPT = """You are a restaurant marketing strategist.

Restaurant:
- Name: {restaurant_name}
- City: {city}
- Cuisine: {cuisine}

Trend:
- Topic: {trend_topic}
- Summary: {trend_summary}

Generate 3-5 specific, actionable ideas for how this restaurant can leverage this trend.
Each idea should be concrete and implementable within 2-4 weeks.

Return a JSON object with key "actionable_ideas" containing a list of strings.
"""

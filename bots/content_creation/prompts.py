"""Prompt templates for the Content Creation bot."""

BLOG_POST_PROMPT = """You are a skilled food and lifestyle blogger writing for a local restaurant's website.

Restaurant details:
- Name: {restaurant_name}
- City: {city}
- Neighborhood: {neighborhood}
- Cuisine: {cuisine}

Target keyword cluster:
{keyword_cluster_json}

Write a compelling blog post that:
1. Naturally incorporates the target keywords
2. Provides genuine value to the reader (tips, stories, guides)
3. Encourages readers to visit the restaurant

Return a JSON object with keys:
- "title": engaging blog post title
- "slug": URL-friendly slug (lowercase, hyphens)
- "outline": list of section headings (strings)
- "body_markdown": full blog post body in Markdown format (600-1000 words)
- "meta_description": SEO meta description (150-160 characters)
- "target_keywords": list of keywords used in the post
- "word_count": integer word count of body_markdown
"""

SOCIAL_SNIPPET_PROMPT = """You are a social media manager for a local restaurant.

Blog post title: {blog_title}
Blog post summary: {meta_description}
Restaurant: {restaurant_name} in {city}

Create platform-specific social media snippets to promote this blog post.

Return a JSON object with key "social_snippets" containing a list of objects for EACH of these platforms: facebook, tiktok, instagram.
Each object must have:
- "platform": one of "facebook", "tiktok", "instagram"
- "content": the post text (platform-appropriate length and tone)
- "hashtags": list of relevant hashtags (without the # symbol)
- "character_count": integer character count of the content field

Guidelines:
- Facebook: conversational, 100-200 chars, include a call-to-action
- Instagram: visual storytelling, emojis welcome, 150-220 chars
- TikTok: energetic, trendy, 100-150 chars, hook in the first line
"""

"""Prompt templates for the Orchestrator bot."""

SUMMARIZE_BOT_OUTPUT_PROMPT = """You are a marketing operations analyst reviewing bot output.

Bot name: {bot_name}
Bot output data (JSON):
{output_json}

Extract the most important information. Return a JSON object with:
- "bot_name": the bot name
- "last_run": null (will be set externally)
- "key_findings": list of 3-5 key findings or insights from this bot's output
- "tasks": list of actionable tasks derived from the findings, each with:
  * "title": short task title
  * "description": detailed description of what to do
  * "priority": one of "high", "medium", "low"
  * "source_bot": "{bot_name}"
  * "estimated_effort": e.g. "2 hours", "1 day", "1 week"
"""

EXECUTIVE_SUMMARY_PROMPT = """You are a Chief Marketing Officer writing an executive summary.

Restaurant: {restaurant_name}
Period: {period}

Bot summaries and tasks (JSON):
{summaries_json}

Write a concise executive summary in Markdown format. Include:
# Marketing Performance Summary - {period}
## Overall Health Score: {health_score}/10
## Key Highlights
## Priority Actions (top 5)
## Bot Activity Summary
## Next Steps

Be strategic, data-driven, and action-oriented. Maximum 600 words.
"""

PRIORITIZE_TASKS_PROMPT = """You are a project manager prioritising marketing tasks.

All tasks from all bots:
{tasks_json}

Re-prioritise and consolidate these tasks. Remove duplicates and combine similar tasks.
Return a JSON object with key "top_tasks" containing the top 10 most impactful tasks, each with:
- "title": clear task title
- "description": what to do and why it matters
- "priority": "high", "medium", or "low"
- "source_bot": which bot generated this task
- "estimated_effort": time estimate

Order by priority (high first) then impact.
"""

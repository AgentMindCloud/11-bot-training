"""Tests for the Link Building bot."""
from __future__ import annotations

import json

import pytest

from bots.link_building.bot import LinkBuildingBot
from bots.link_building.models import LinkProspect, OutreachEmail


_PROSPECTS_RESPONSE = json.dumps({
    "prospects": [
        {
            "url": "https://nycfoodblog.example.com",
            "email": "editor@nycfoodblog.example.com",
            "contact_name": "Editor",
            "domain_authority_estimate": 45,
            "relevance_score": 0.9,
            "notes": "Popular NYC food blog that covers East Village restaurants",
            "status": "prospect",
        },
        {
            "url": "https://eastvillageguide.example.com",
            "email": None,
            "contact_name": None,
            "domain_authority_estimate": 30,
            "relevance_score": 0.8,
            "notes": "Neighbourhood guide covering local businesses",
            "status": "prospect",
        },
    ]
})

_EMAIL_RESPONSE = json.dumps({
    "prospect_url": "https://nycfoodblog.example.com",
    "subject": "Feature opportunity: authentic Italian in East Village",
    "body": "Hi there,\n\nI'm a huge fan of your NYC food coverage - your East Village roundup from last month was spot on!\n\nI'm reaching out on behalf of Test Trattoria, a family-run Italian restaurant in East Village that's been getting rave reviews for its handmade pasta.\n\nWould you be open to a complimentary tasting visit? I think your readers would love our story.\n\nBest,\nThe Team at Test Trattoria",
})


class TestLinkBuildingBot:
    def test_discover_prospects_returns_link_prospects(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _PROSPECTS_RESPONSE
        bot = LinkBuildingBot(llm=mock_llm_client)
        prospects = bot.discover_prospects(["Italian restaurant NYC"], "New York", "Italian")
        assert len(prospects) == 2
        assert all(isinstance(p, LinkProspect) for p in prospects)
        assert prospects[0].url == "https://nycfoodblog.example.com"

    def test_discover_prospects_have_required_fields(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _PROSPECTS_RESPONSE
        bot = LinkBuildingBot(llm=mock_llm_client)
        prospects = bot.discover_prospects(["keyword"], "City", "Cuisine")
        for p in prospects:
            assert p.url
            assert 0.0 <= p.relevance_score <= 1.0

    def test_generate_outreach_email_returns_outreach_email(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _EMAIL_RESPONSE
        bot = LinkBuildingBot(llm=mock_llm_client)
        prospect = LinkProspect(
            url="https://nycfoodblog.example.com",
            notes="NYC food blog",
            relevance_score=0.9,
        )
        email = bot.generate_outreach_email(
            prospect,
            {"restaurant_name": "Test Trattoria", "city": "New York", "cuisine": "Italian"},
        )
        assert isinstance(email, OutreachEmail)
        assert email.subject
        assert email.body
        assert email.prospect_url == "https://nycfoodblog.example.com"

    def test_generate_outreach_email_has_subject_and_body(self, mock_llm_client, tmp_output_dir, mock_settings):
        mock_llm_client.chat_completion.return_value = _EMAIL_RESPONSE
        bot = LinkBuildingBot(llm=mock_llm_client)
        prospect = LinkProspect(url="https://example.com", relevance_score=0.5)
        email = bot.generate_outreach_email(prospect, {"restaurant_name": "R", "city": "C", "cuisine": "I"})
        assert len(email.subject) > 0
        assert len(email.body) > 0

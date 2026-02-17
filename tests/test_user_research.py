import json
import pytest
from unittest.mock import MagicMock, patch

from core.research.user_research import (
    build_search_query,
    parse_research_results,
    generate_user_dossier,
    research_user,
)


class TestBuildSearchQuery:
    def test_uses_name_and_domain(self):
        query = build_search_query("John Smith", "john@google.com")
        assert "John Smith" in query
        assert "google.com" in query

    def test_handles_gmail(self):
        query = build_search_query("Jane Doe", "jane@gmail.com")
        assert "Jane Doe" in query
        # gmail.com is generic, should not be included
        assert "gmail.com" not in query

    def test_handles_empty_email(self):
        query = build_search_query("Jane Doe", "")
        assert "Jane Doe" in query


class TestParseResearchResults:
    def test_extracts_snippets(self):
        raw_results = {
            "organic_results": [
                {"title": "John Smith - LinkedIn", "snippet": "Software Engineer at Google", "link": "https://linkedin.com/in/john"},
                {"title": "John Smith Blog", "snippet": "Writes about AI and robotics", "link": "https://johnsmith.com"},
            ]
        }
        parsed = parse_research_results(raw_results)
        assert len(parsed) > 0
        assert any("Software Engineer" in p for p in parsed)

    def test_handles_empty_results(self):
        parsed = parse_research_results({})
        assert parsed == []

    def test_handles_no_organic(self):
        parsed = parse_research_results({"something_else": []})
        assert parsed == []


class TestGenerateUserDossier:
    def test_generates_dossier_from_snippets(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content=json.dumps({
                "personality_traits": ["analytical", "curious"],
                "values": ["innovation", "learning"],
                "communication_style": "direct and technical",
                "likely_motivations": ["building impactful products"],
                "potential_insecurities": ["imposter syndrome in fast-moving field"],
                "professional_context": "Software engineer at a large tech company",
                "interests": ["AI", "robotics", "open source"],
            })
        )
        snippets = [
            "Software Engineer at Google",
            "Writes about AI and robotics",
            "Open source contributor",
        ]
        dossier = generate_user_dossier(mock_llm, "John Smith", snippets)
        assert "personality_traits" in dossier
        assert len(dossier["personality_traits"]) > 0
        mock_llm.invoke.assert_called_once()

    def test_returns_empty_dossier_on_no_snippets(self):
        mock_llm = MagicMock()
        dossier = generate_user_dossier(mock_llm, "John Smith", [])
        assert dossier == {}
        mock_llm.invoke.assert_not_called()


class TestResearchUser:
    @patch("core.research.user_research.search_web")
    def test_full_pipeline(self, mock_search):
        mock_search.return_value = {
            "organic_results": [
                {"title": "Test", "snippet": "Test snippet", "link": "https://example.com"},
            ]
        }
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content=json.dumps({
                "personality_traits": ["driven"],
                "values": ["growth"],
                "communication_style": "casual",
                "likely_motivations": ["learning"],
                "potential_insecurities": [],
                "professional_context": "Unknown",
                "interests": ["technology"],
            })
        )
        dossier = research_user(mock_llm, "Test User", "test@company.com")
        assert "personality_traits" in dossier
        mock_search.assert_called_once()

    @patch("core.research.user_research.search_web")
    def test_handles_search_failure(self, mock_search):
        mock_search.side_effect = Exception("API error")
        mock_llm = MagicMock()
        dossier = research_user(mock_llm, "Test User", "test@company.com")
        assert dossier == {}

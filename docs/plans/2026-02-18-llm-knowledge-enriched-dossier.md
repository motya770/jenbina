# LLM Knowledge-Enriched User Dossier Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Augment user research with GPT's built-in knowledge about people, running in parallel with web search, to produce richer psychological dossiers.

**Architecture:** Add a `query_llm_knowledge()` function that asks GPT what it already knows about a person. Run it in parallel with the existing Serper web search using `concurrent.futures.ThreadPoolExecutor`. Both results feed into the existing `generate_user_dossier()` call via an updated merge prompt.

**Tech Stack:** Python, LangChain (HumanMessage/SystemMessage), concurrent.futures, pytest

---

### Task 1: Add `query_llm_knowledge()` function with tests

**Files:**
- Modify: `core/research/user_research.py`
- Modify: `tests/test_user_research.py`

**Step 1: Write the failing tests**

Add to `tests/test_user_research.py`:

```python
from core.research.user_research import (
    build_search_query,
    parse_research_results,
    generate_user_dossier,
    research_user,
    query_llm_knowledge,
)


class TestQueryLlmKnowledge:
    def test_returns_knowledge_string(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content="Known tech entrepreneur, co-founded a startup in AI space. "
                    "Writes about machine learning. Public speaker at tech conferences."
        )
        result = query_llm_knowledge(mock_llm, "John Smith", "john@techco.com")
        assert isinstance(result, str)
        assert len(result) > 0
        mock_llm.invoke.assert_called_once()

    def test_returns_empty_string_when_no_knowledge(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content="NO_INFORMATION"
        )
        result = query_llm_knowledge(mock_llm, "Unknown Person", "unknown@gmail.com")
        assert result == ""

    def test_handles_llm_error(self):
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        result = query_llm_knowledge(mock_llm, "Test", "test@test.com")
        assert result == ""
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python -m pytest tests/test_user_research.py::TestQueryLlmKnowledge -v`
Expected: FAIL with ImportError (query_llm_knowledge doesn't exist yet)

**Step 3: Implement `query_llm_knowledge()`**

Add to `core/research/user_research.py` after the `parse_research_results` function:

```python
_LLM_KNOWLEDGE_PROMPT = """\
What do you already know about a person named "{name}"{email_hint} from your \
training data? This could include their professional work, public writings, \
talks, open source contributions, or any other publicly known information.

If you have specific knowledge about this person, provide a concise summary \
covering: who they are, what they do, what they're known for, and any notable \
qualities or interests.

If you do not have any specific information about this person, respond with \
exactly: NO_INFORMATION

Do not guess or fabricate information. Only share what you are confident about."""


def query_llm_knowledge(llm, name: str, email: str) -> str:
    """Ask the LLM what it already knows about a person from training data.

    Returns a text summary, or empty string if no knowledge or on error.
    """
    try:
        email_hint = f" (email: {email})" if email else ""
        prompt = _LLM_KNOWLEDGE_PROMPT.format(name=name, email_hint=email_hint)
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        if content == "NO_INFORMATION":
            return ""
        return content
    except Exception:
        return ""
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python -m pytest tests/test_user_research.py::TestQueryLlmKnowledge -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add core/research/user_research.py tests/test_user_research.py
git commit -m "feat: add query_llm_knowledge() to ask GPT about users"
```

---

### Task 2: Update `_DOSSIER_PROMPT` and `generate_user_dossier()` to accept prior knowledge

**Files:**
- Modify: `core/research/user_research.py`
- Modify: `tests/test_user_research.py`

**Step 1: Write the failing tests**

Update existing test and add new tests in `tests/test_user_research.py`:

```python
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

    def test_returns_empty_dossier_on_no_snippets_and_no_knowledge(self):
        mock_llm = MagicMock()
        dossier = generate_user_dossier(mock_llm, "John Smith", [])
        assert dossier == {}
        mock_llm.invoke.assert_not_called()

    def test_generates_dossier_from_prior_knowledge_alone(self):
        """When web search returns nothing but GPT knows the person."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content=json.dumps({
                "personality_traits": ["visionary"],
                "values": ["innovation"],
                "communication_style": "charismatic",
                "likely_motivations": ["changing the world"],
                "potential_insecurities": [],
                "professional_context": "Tech CEO",
                "interests": ["AI", "space"],
            })
        )
        dossier = generate_user_dossier(
            mock_llm, "Famous Person", [],
            prior_knowledge="Well-known tech CEO, founded multiple companies."
        )
        assert "personality_traits" in dossier
        mock_llm.invoke.assert_called_once()

    def test_prompt_includes_both_sources(self):
        """Verify the prompt sent to LLM contains both web snippets and prior knowledge."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content=json.dumps({
                "personality_traits": ["analytical"],
                "values": ["learning"],
                "communication_style": "direct",
                "likely_motivations": ["building"],
                "potential_insecurities": [],
                "professional_context": "Engineer",
                "interests": ["AI"],
            })
        )
        snippets = ["Engineer at Google"]
        prior = "Known AI researcher and speaker"
        generate_user_dossier(mock_llm, "Test", snippets, prior_knowledge=prior)

        call_args = mock_llm.invoke.call_args[0][0]
        prompt_text = call_args[0].content
        assert "Engineer at Google" in prompt_text
        assert "Known AI researcher and speaker" in prompt_text
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python -m pytest tests/test_user_research.py::TestGenerateUserDossier -v`
Expected: FAIL — new tests fail because `generate_user_dossier` doesn't accept `prior_knowledge` param, and the empty-snippets test now needs updating.

**Step 3: Update `_DOSSIER_PROMPT` and `generate_user_dossier()`**

Replace `_DOSSIER_PROMPT` in `core/research/user_research.py`:

```python
_DOSSIER_PROMPT = """\
You are analyzing information about a person to build a psychological profile. \
This will be used by Jenbina (an AGI simulation) to have more meaningful \
conversations with this person.

Person's name: {name}

{web_section}

{knowledge_section}

Based on ALL available information above, generate a JSON object with these fields:
- "personality_traits": list of 2-4 likely personality traits
- "values": list of 2-3 core values
- "communication_style": one sentence describing likely communication style
- "likely_motivations": list of 1-3 things that likely drive this person
- "potential_insecurities": list of 0-2 possible insecurities (be respectful)
- "professional_context": one sentence about their professional life
- "interests": list of 2-5 interests/topics they care about

Prioritize web search results for recent/factual information. Use prior knowledge \
for deeper psychological insight and context that search snippets might miss.

Be insightful but not invasive. Focus on what would help someone have a \
genuinely meaningful conversation with this person. If information is sparse, \
make reasonable inferences but note lower confidence.

Return ONLY valid JSON."""
```

Update `generate_user_dossier()`:

```python
def generate_user_dossier(llm, name: str, snippets: List[str],
                          prior_knowledge: str = "") -> Dict[str, Any]:
    """Use LLM to generate a psychological profile from research snippets
    and prior LLM knowledge."""
    if not snippets and not prior_knowledge:
        return {}

    web_section = (
        "Public information found via web search:\n"
        + "\n".join(f"- {s}" for s in snippets)
        if snippets
        else "No web search results available."
    )

    knowledge_section = (
        f"Prior knowledge about this person:\n{prior_knowledge}"
        if prior_knowledge
        else "No prior knowledge available."
    )

    prompt = _DOSSIER_PROMPT.format(
        name=name,
        web_section=web_section,
        knowledge_section=knowledge_section,
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except (json.JSONDecodeError, IndexError):
        return {}
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python -m pytest tests/test_user_research.py::TestGenerateUserDossier -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add core/research/user_research.py tests/test_user_research.py
git commit -m "feat: update dossier generation to merge web search with LLM knowledge"
```

---

### Task 3: Update `research_user()` to run both sources in parallel

**Files:**
- Modify: `core/research/user_research.py`
- Modify: `tests/test_user_research.py`

**Step 1: Write the failing tests**

Update tests in `tests/test_user_research.py`:

```python
class TestResearchUser:
    @patch("core.research.user_research.search_web")
    def test_full_pipeline_with_both_sources(self, mock_search):
        mock_search.return_value = {
            "organic": [
                {"title": "Test", "snippet": "Test snippet", "link": "https://example.com"},
            ]
        }
        mock_llm = MagicMock()
        # LLM is called twice: once for query_llm_knowledge, once for generate_user_dossier
        mock_llm.invoke.side_effect = [
            MagicMock(content="Known tech person, works on AI projects."),
            MagicMock(content=json.dumps({
                "personality_traits": ["driven"],
                "values": ["growth"],
                "communication_style": "casual",
                "likely_motivations": ["learning"],
                "potential_insecurities": [],
                "professional_context": "Unknown",
                "interests": ["technology"],
            })),
        ]
        dossier = research_user(mock_llm, "Test User", "test@company.com")
        assert "personality_traits" in dossier
        mock_search.assert_called_once()
        assert mock_llm.invoke.call_count == 2

    @patch("core.research.user_research.search_web")
    def test_works_when_search_fails_but_llm_knows(self, mock_search):
        """Web search fails, but GPT knows the person — should still produce a dossier."""
        mock_search.side_effect = Exception("API error")
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [
            MagicMock(content="Famous researcher in machine learning."),
            MagicMock(content=json.dumps({
                "personality_traits": ["analytical"],
                "values": ["knowledge"],
                "communication_style": "academic",
                "likely_motivations": ["research"],
                "potential_insecurities": [],
                "professional_context": "ML researcher",
                "interests": ["machine learning"],
            })),
        ]
        dossier = research_user(mock_llm, "Test User", "test@company.com")
        assert "personality_traits" in dossier

    @patch("core.research.user_research.search_web")
    def test_works_when_llm_has_no_knowledge(self, mock_search):
        """LLM has no knowledge, but web search works — still produces dossier."""
        mock_search.return_value = {
            "organic": [
                {"title": "Test", "snippet": "Some info", "link": "https://example.com"},
            ]
        }
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = [
            MagicMock(content="NO_INFORMATION"),
            MagicMock(content=json.dumps({
                "personality_traits": ["quiet"],
                "values": ["privacy"],
                "communication_style": "reserved",
                "likely_motivations": ["stability"],
                "potential_insecurities": [],
                "professional_context": "Unknown",
                "interests": ["reading"],
            })),
        ]
        dossier = research_user(mock_llm, "Unknown Person", "unknown@gmail.com")
        assert "personality_traits" in dossier

    @patch("core.research.user_research.search_web")
    def test_returns_empty_when_both_fail(self, mock_search):
        """Both sources fail — returns empty dict."""
        mock_search.side_effect = Exception("API error")
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        dossier = research_user(mock_llm, "Test", "test@test.com")
        assert dossier == {}
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python -m pytest tests/test_user_research.py::TestResearchUser -v`
Expected: FAIL — `research_user` doesn't call `query_llm_knowledge` or use ThreadPoolExecutor yet.

**Step 3: Update `research_user()` with parallel execution**

Replace `research_user()` in `core/research/user_research.py`:

```python
def research_user(llm, display_name: str, email: str) -> Dict[str, Any]:
    """Full pipeline: search web + query LLM knowledge in parallel -> merge -> generate dossier.

    Returns a dossier dict, or empty dict on failure.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    snippets = []
    prior_knowledge = ""

    def _web_search():
        query = build_search_query(display_name, email)
        raw_results = search_web(query)
        return parse_research_results(raw_results)

    def _llm_knowledge():
        return query_llm_knowledge(llm, display_name, email)

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            web_future = executor.submit(_web_search)
            llm_future = executor.submit(_llm_knowledge)

            try:
                snippets = web_future.result(timeout=20)
            except Exception as e:
                print(f"Web search failed: {e}")

            try:
                prior_knowledge = llm_future.result(timeout=20)
            except Exception as e:
                print(f"LLM knowledge query failed: {e}")

        if not snippets and not prior_knowledge:
            return {}

        return generate_user_dossier(llm, display_name, snippets,
                                     prior_knowledge=prior_knowledge)
    except Exception as e:
        print(f"User research failed: {e}")
        return {}
```

Add `import` at top of file — `concurrent.futures` is stdlib, no new dependency needed.

**Step 4: Run tests to verify they pass**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python -m pytest tests/test_user_research.py -v`
Expected: ALL tests pass (old and new)

**Step 5: Commit**

```bash
git add core/research/user_research.py tests/test_user_research.py
git commit -m "feat: run web search and LLM knowledge query in parallel for richer dossiers"
```

---

### Task 4: Run full test suite and verify no regressions

**Files:** None (verification only)

**Step 1: Run the user research tests**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python -m pytest tests/test_user_research.py -v`
Expected: All tests pass

**Step 2: Run the full test suite**

Run: `cd /Users/wizard/Desktop/programming/projects/jenbina && python tests/run_tests.py`
Expected: No regressions

**Step 3: Commit design doc**

```bash
git add docs/plans/2026-02-18-llm-knowledge-enriched-dossier.md
git commit -m "docs: add design doc for LLM knowledge-enriched dossier"
```

"""Social cognition / Theory-of-Mind system for Jenbina.

Tracks beliefs about other entities, relationship dynamics, likely reactions,
and conversational strategy.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
import re


EMOTION_CUES = {
    "sad": ["sad", "down", "depressed", "upset", "lonely", "hurt"],
    "anxious": ["anxious", "worried", "nervous", "stressed", "afraid", "scared"],
    "angry": ["angry", "mad", "furious", "annoyed", "frustrated", "hate"],
    "happy": ["happy", "great", "excited", "glad", "good", "awesome"],
    "neutral": [],
}

TOPIC_KEYWORDS = {
    "technology": [
        "tech", "technology", "ai", "ml", "machine learning", "code", "coding",
        "python", "javascript", "api", "software", "computer", "programming",
    ],
    "work": ["work", "job", "career", "project", "deadline", "boss", "meeting"],
    "relationships": ["friend", "family", "partner", "relationship", "people"],
    "health": ["health", "sleep", "exercise", "diet", "sick", "doctor"],
    "creativity": ["music", "art", "write", "writing", "design", "creative"],
}

POLITE_MARKERS = ["please", "thank you", "thanks", "would you", "could you"]
HOSTILE_MARKERS = ["stupid", "idiot", "shut up", "useless", "hate you"]
SELF_DISCLOSURE_MARKERS = ["i feel", "i'm", "i am", "my", "me", "i think"]


@dataclass
class RelationshipState:
    trust: float = 50.0
    closeness: float = 35.0
    conflict: float = 10.0
    interactions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trust": self.trust,
            "closeness": self.closeness,
            "conflict": self.conflict,
            "interactions": self.interactions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationshipState":
        return cls(
            trust=float(data.get("trust", 50.0)),
            closeness=float(data.get("closeness", 35.0)),
            conflict=float(data.get("conflict", 10.0)),
            interactions=int(data.get("interactions", 0)),
        )


@dataclass
class PersonModel:
    beliefs: List[str] = field(default_factory=list)
    interests: Dict[str, float] = field(default_factory=dict)  # topic -> score [0,1]
    inferred_emotional_state: str = "neutral"
    relationship: RelationshipState = field(default_factory=RelationshipState)
    last_predicted_reaction: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "beliefs": list(self.beliefs),
            "interests": dict(self.interests),
            "inferred_emotional_state": self.inferred_emotional_state,
            "relationship": self.relationship.to_dict(),
            "last_predicted_reaction": self.last_predicted_reaction,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonModel":
        return cls(
            beliefs=list(data.get("beliefs", [])),
            interests=dict(data.get("interests", {})),
            inferred_emotional_state=data.get("inferred_emotional_state", "neutral"),
            relationship=RelationshipState.from_dict(data.get("relationship", {})),
            last_predicted_reaction=data.get("last_predicted_reaction", ""),
        )


class SocialCognitionSystem:
    """Tracks social models and chooses social strategy for conversations."""

    def __init__(self):
        self.models: Dict[str, PersonModel] = {}

    def get_or_create_model(self, entity_name: str) -> PersonModel:
        if entity_name not in self.models:
            self.models[entity_name] = PersonModel()
        return self.models[entity_name]

    def observe_entity_message(self, entity_name: str, message: str):
        """Update person model from an incoming message."""
        model = self.get_or_create_model(entity_name)
        rel = model.relationship
        lower = message.lower()

        rel.interactions += 1

        inferred_emotion, emotion_score = self._infer_emotion(lower)
        if emotion_score > 0:
            model.inferred_emotional_state = inferred_emotion

        self._update_interests(model, lower)
        self._extract_beliefs(model, message)

        polite_hits = sum(1 for marker in POLITE_MARKERS if marker in lower)
        hostile_hits = sum(1 for marker in HOSTILE_MARKERS if marker in lower)
        disclosure_hits = sum(1 for marker in SELF_DISCLOSURE_MARKERS if marker in lower)

        rel.trust += polite_hits * 1.5
        rel.closeness += polite_hits * 1.0

        rel.trust -= hostile_hits * 3.0
        rel.closeness -= hostile_hits * 2.0
        rel.conflict += hostile_hits * 5.0

        if disclosure_hits > 0:
            rel.closeness += 1.5
            rel.trust += 0.5

        if "?" in message:
            rel.closeness += 0.5

        if inferred_emotion in ("sad", "anxious"):
            rel.closeness += 0.5

        self._clamp_relationship(rel)

    def observe_response_effect(self, entity_name: str, strategy: str):
        """Estimate relationship drift after Jenbina's response strategy."""
        model = self.get_or_create_model(entity_name)
        rel = model.relationship

        if strategy == "nice":
            rel.trust += 1.0
            rel.closeness += 1.2
            rel.conflict -= 0.6
        elif strategy == "polite":
            rel.trust += 0.5
            rel.conflict -= 0.3
        elif strategy == "assertive":
            rel.trust += 0.2
            rel.closeness += 0.3
            rel.conflict += 0.4

        self._clamp_relationship(rel)

    def choose_social_strategy(self, entity_name: str, latest_user_message: str = "") -> str:
        """Choose when to be nice, polite, or assertive."""
        model = self.get_or_create_model(entity_name)
        rel = model.relationship
        emotion = model.inferred_emotional_state
        lower = latest_user_message.lower()

        if emotion in ("sad", "anxious"):
            return "nice"

        if rel.conflict >= 45 or rel.trust <= 30:
            return "polite"

        directness_request = any(
            phrase in lower
            for phrase in ["be direct", "be honest", "straight answer", "just tell me"]
        )
        if (rel.trust >= 68 and rel.closeness >= 60 and rel.conflict <= 25) or directness_request:
            return "assertive"

        return "nice" if rel.closeness >= 50 else "polite"

    def predict_reaction(self, entity_name: str, strategy: str) -> Dict[str, Any]:
        """Predict likely reaction from relationship + inferred emotional state."""
        model = self.get_or_create_model(entity_name)
        rel = model.relationship

        score = (rel.trust * 0.45 + rel.closeness * 0.35 - rel.conflict * 0.40) / 100.0
        if strategy == "nice":
            score += 0.08
        elif strategy == "assertive":
            score -= 0.03 if rel.conflict > 30 else 0.05

        score = max(-1.0, min(1.0, score))

        if score >= 0.35:
            reaction = "receptive"
        elif score <= -0.15:
            reaction = "defensive"
        else:
            reaction = "neutral"

        confidence = min(0.95, 0.55 + abs(score) * 0.35)
        model.last_predicted_reaction = reaction

        return {
            "reaction": reaction,
            "valence": round(score, 2),
            "confidence": round(confidence, 2),
        }

    def format_for_prompt(self, entity_name: str, latest_user_message: str = "") -> str:
        """Build a concise ToM context block for LLM prompting."""
        model = self.get_or_create_model(entity_name)
        strategy = self.choose_social_strategy(entity_name, latest_user_message)
        prediction = self.predict_reaction(entity_name, strategy)

        top_interests = sorted(
            model.interests.items(), key=lambda kv: kv[1], reverse=True
        )[:3]
        interests_text = ", ".join(f"{k} ({v:.2f})" for k, v in top_interests) or "unknown"
        beliefs_text = "; ".join(model.beliefs[-3:]) or "No strong beliefs yet"

        rel = model.relationship
        return (
            f"Person model for {entity_name}:\n"
            f"- Inferred emotion: {model.inferred_emotional_state}\n"
            f"- Beliefs: {beliefs_text}\n"
            f"- Interests: {interests_text}\n"
            f"- Relationship: trust={rel.trust:.1f}, closeness={rel.closeness:.1f}, conflict={rel.conflict:.1f}\n"
            f"- Recommended social strategy: {strategy}\n"
            f"- Predicted reaction: {prediction['reaction']} (valence={prediction['valence']}, confidence={prediction['confidence']})\n"
            f"Strategy guide: nice=warm+empathetic, polite=respectful+measured, assertive=direct+clear."
        )

    def get_stats(self) -> Dict[str, Any]:
        return {
            "tracked_entities": len(self.models),
            "entities": {name: model.to_dict() for name, model in self.models.items()},
        }

    def to_dict(self) -> Dict[str, Any]:
        return {"models": {name: model.to_dict() for name, model in self.models.items()}}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialCognitionSystem":
        sys = cls()
        models = data.get("models", {}) if isinstance(data, dict) else {}
        for name, raw in models.items():
            sys.models[name] = PersonModel.from_dict(raw)
        return sys

    def _infer_emotion(self, text: str) -> Tuple[str, int]:
        best_emotion = "neutral"
        best_score = 0
        for emotion, cues in EMOTION_CUES.items():
            if emotion == "neutral":
                continue
            score = sum(1 for cue in cues if cue in text)
            if score > best_score:
                best_emotion = emotion
                best_score = score
        return best_emotion, best_score

    def _update_interests(self, model: PersonModel, text: str):
        for topic, keywords in TOPIC_KEYWORDS.items():
            hits = sum(1 for k in keywords if k in text)
            if hits:
                current = model.interests.get(topic, 0.0)
                model.interests[topic] = min(1.0, current + 0.12 * hits)

    def _extract_beliefs(self, model: PersonModel, message: str):
        patterns = [
            r"\bI like ([^\.!\?]+)",
            r"\bI love ([^\.!\?]+)",
            r"\bI hate ([^\.!\?]+)",
            r"\bI am ([^\.!\?]+)",
            r"\bI'm ([^\.!\?]+)",
        ]

        for pattern in patterns:
            for match in re.findall(pattern, message, flags=re.IGNORECASE):
                belief = match.strip()
                if belief:
                    belief_text = belief[:120]
                    if belief_text not in model.beliefs:
                        model.beliefs.append(belief_text)
                        if len(model.beliefs) > 40:
                            model.beliefs = model.beliefs[-40:]

    @staticmethod
    def _clamp_relationship(rel: RelationshipState):
        rel.trust = max(0.0, min(100.0, rel.trust))
        rel.closeness = max(0.0, min(100.0, rel.closeness))
        rel.conflict = max(0.0, min(100.0, rel.conflict))

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
import json
from enum import Enum
from langchain.prompts import PromptTemplate


class NeedLevel(Enum):
    """Maslow's hierarchy levels"""
    PHYSIOLOGICAL = 1
    SAFETY = 2
    SOCIAL = 3
    ESTEEM = 4
    SELF_ACTUALIZATION = 5


class NeedCategory(Enum):
    """Categories within each need level"""
    # Physiological needs
    FOOD = "food"
    WATER = "water"
    SLEEP = "sleep"
    SHELTER = "shelter"
    CLOTHING = "clothing"
    HEALTH = "health"
    
    # Safety needs
    SECURITY = "security"
    STABILITY = "stability"
    PROTECTION = "protection"
    ORDER = "order"
    LAW = "law"
    FREEDOM_FROM_FEAR = "freedom_from_fear"
    
    # Social needs
    FRIENDSHIP = "friendship"
    LOVE = "love"
    BELONGING = "belonging"
    FAMILY = "family"
    INTIMACY = "intimacy"
    SOCIAL_CONNECTION = "social_connection"
    
    # Esteem needs
    SELF_ESTEEM = "self_esteem"
    CONFIDENCE = "confidence"
    ACHIEVEMENT = "achievement"
    RESPECT = "respect"
    RECOGNITION = "recognition"
    INDEPENDENCE = "independence"
    
    # Self-actualization needs
    PERSONAL_GROWTH = "personal_growth"
    CREATIVITY = "creativity"
    PURPOSE = "purpose"
    MEANING = "meaning"
    POTENTIAL = "potential"
    TRANSCENDENCE = "transcendence"


@dataclass
class MaslowNeed:
    """Represents a single need in Maslow's hierarchy"""
    name: str
    category: NeedCategory
    level: NeedLevel
    satisfaction: float = 100.0  # 0-100 scale
    decay_rate: float = 10.0  # How much satisfaction decreases per update
    importance: float = 1.0  # Relative importance within the level (0-1)
    last_updated: datetime = field(default_factory=datetime.now)
    growth_rate: float = 0.0  # How much satisfaction can grow beyond 100 (for self-actualization)
    max_satisfaction: float = 100.0  # Maximum possible satisfaction
    
    def update(self, time_delta: timedelta = None):
        """Update need satisfaction over time"""
        if time_delta is None:
            time_delta = timedelta(minutes=1)  # Default 1 minute update
        
        # Calculate decay based on time passed
        hours_passed = time_delta.total_seconds() / 3600
        decay_amount = self.decay_rate * hours_passed * random.uniform(0.8, 1.2)
        
        # Apply decay
        self.satisfaction = max(0, self.satisfaction - decay_amount)
        self.last_updated = datetime.now()
        
        # For self-actualization needs, allow growth beyond 100
        if self.level == NeedLevel.SELF_ACTUALIZATION and self.satisfaction < self.max_satisfaction:
            growth_amount = self.growth_rate * hours_passed * random.uniform(0.5, 1.5)
            self.satisfaction = min(self.max_satisfaction, self.satisfaction + growth_amount)
    
    def satisfy(self, amount: float, source: str = "unknown"):
        """Increase satisfaction by given amount"""
        old_satisfaction = self.satisfaction
        
        # For self-actualization, allow growth beyond 100
        if self.level == NeedLevel.SELF_ACTUALIZATION:
            self.satisfaction = min(self.max_satisfaction, self.satisfaction + amount)
        else:
            self.satisfaction = min(100, self.satisfaction + amount)
        
        self.last_updated = datetime.now()
        return self.satisfaction - old_satisfaction  # Return actual amount satisfied
    
    def is_critical(self) -> bool:
        """Check if need is critically low"""
        if self.level == NeedLevel.PHYSIOLOGICAL:
            return self.satisfaction < 20
        elif self.level == NeedLevel.SAFETY:
            return self.satisfaction < 30
        else:
            return self.satisfaction < 40
    
    def is_low(self) -> bool:
        """Check if need is low"""
        if self.level == NeedLevel.PHYSIOLOGICAL:
            return self.satisfaction < 50
        elif self.level == NeedLevel.SAFETY:
            return self.satisfaction < 60
        else:
            return self.satisfaction < 70
    
    def is_met(self) -> bool:
        """Check if need is adequately met"""
        return self.satisfaction >= 70
    
    def get_priority_score(self) -> float:
        """Calculate priority score based on level, satisfaction, and importance"""
        # Lower levels have higher priority
        level_priority = 6 - self.level.value  # 5 for physiological, 1 for self-actualization
        
        # Lower satisfaction increases priority
        satisfaction_priority = (100 - self.satisfaction) / 100
        
        # Combine with importance
        return level_priority * satisfaction_priority * self.importance


@dataclass
class MaslowNeedsSystem:
    """Complete Maslow's hierarchy of needs system"""
    needs: Dict[str, MaslowNeed] = field(default_factory=dict)
    personality_traits: Dict[str, float] = field(default_factory=dict)
    growth_stage: int = 1  # Current stage of personal development (1-5)
    last_comprehensive_update: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize all needs in Maslow's hierarchy"""
        if not self.needs:
            self._initialize_all_needs()
    
    def _initialize_all_needs(self):
        """Initialize all needs across all five levels"""
        
        # Physiological Needs (Level 1)
        self.needs.update({
            'hunger': MaslowNeed('hunger', NeedCategory.FOOD, NeedLevel.PHYSIOLOGICAL, 
                               satisfaction=100.0, decay_rate=8.0, importance=1.0),
            'thirst': MaslowNeed('thirst', NeedCategory.WATER, NeedLevel.PHYSIOLOGICAL, 
                               satisfaction=100.0, decay_rate=6.0, importance=1.0),
            'sleep': MaslowNeed('sleep', NeedCategory.SLEEP, NeedLevel.PHYSIOLOGICAL, 
                              satisfaction=100.0, decay_rate=4.0, importance=1.0),
            'shelter': MaslowNeed('shelter', NeedCategory.SHELTER, NeedLevel.PHYSIOLOGICAL, 
                                satisfaction=100.0, decay_rate=1.0, importance=0.8),
            'health': MaslowNeed('health', NeedCategory.HEALTH, NeedLevel.PHYSIOLOGICAL, 
                               satisfaction=100.0, decay_rate=2.0, importance=0.9),
        })
        
        # Safety Needs (Level 2)
        self.needs.update({
            'security': MaslowNeed('security', NeedCategory.SECURITY, NeedLevel.SAFETY, 
                                 satisfaction=100.0, decay_rate=3.0, importance=0.9),
            'stability': MaslowNeed('stability', NeedCategory.STABILITY, NeedLevel.SAFETY, 
                                  satisfaction=100.0, decay_rate=2.0, importance=0.8),
            'protection': MaslowNeed('protection', NeedCategory.PROTECTION, NeedLevel.SAFETY, 
                                   satisfaction=100.0, decay_rate=2.5, importance=0.9),
            'order': MaslowNeed('order', NeedCategory.ORDER, NeedLevel.SAFETY, 
                              satisfaction=100.0, decay_rate=1.5, importance=0.7),
        })
        
        # Social Needs (Level 3)
        self.needs.update({
            'friendship': MaslowNeed('friendship', NeedCategory.FRIENDSHIP, NeedLevel.SOCIAL, 
                                   satisfaction=70.0, decay_rate=2.0, importance=0.8),
            'love': MaslowNeed('love', NeedCategory.LOVE, NeedLevel.SOCIAL, 
                             satisfaction=60.0, decay_rate=1.5, importance=0.9),
            'belonging': MaslowNeed('belonging', NeedCategory.BELONGING, NeedLevel.SOCIAL, 
                                  satisfaction=65.0, decay_rate=1.8, importance=0.8),
            'social_connection': MaslowNeed('social_connection', NeedCategory.SOCIAL_CONNECTION, 
                                          NeedLevel.SOCIAL, satisfaction=75.0, decay_rate=2.2, importance=0.7),
        })
        
        # Esteem Needs (Level 4)
        self.needs.update({
            'self_esteem': MaslowNeed('self_esteem', NeedCategory.SELF_ESTEEM, NeedLevel.ESTEEM, 
                                    satisfaction=50.0, decay_rate=1.0, importance=0.8),
            'confidence': MaslowNeed('confidence', NeedCategory.CONFIDENCE, NeedLevel.ESTEEM, 
                                   satisfaction=45.0, decay_rate=1.2, importance=0.9),
            'achievement': MaslowNeed('achievement', NeedCategory.ACHIEVEMENT, NeedLevel.ESTEEM, 
                                    satisfaction=40.0, decay_rate=0.8, importance=0.8),
            'respect': MaslowNeed('respect', NeedCategory.RESPECT, NeedLevel.ESTEEM, 
                                satisfaction=55.0, decay_rate=1.0, importance=0.7),
        })
        
        # Self-Actualization Needs (Level 5)
        self.needs.update({
            'personal_growth': MaslowNeed('personal_growth', NeedCategory.PERSONAL_GROWTH, 
                                        NeedLevel.SELF_ACTUALIZATION, satisfaction=30.0, 
                                        decay_rate=0.5, importance=0.9, growth_rate=0.2, max_satisfaction=150.0),
            'creativity': MaslowNeed('creativity', NeedCategory.CREATIVITY, 
                                   NeedLevel.SELF_ACTUALIZATION, satisfaction=25.0, 
                                   decay_rate=0.6, importance=0.8, growth_rate=0.3, max_satisfaction=150.0),
            'purpose': MaslowNeed('purpose', NeedCategory.PURPOSE, 
                                NeedLevel.SELF_ACTUALIZATION, satisfaction=20.0, 
                                decay_rate=0.3, importance=1.0, growth_rate=0.1, max_satisfaction=200.0),
            'meaning': MaslowNeed('meaning', NeedCategory.MEANING, 
                                NeedLevel.SELF_ACTUALIZATION, satisfaction=15.0, 
                                decay_rate=0.4, importance=0.9, growth_rate=0.15, max_satisfaction=180.0),
        })
    
    def update_all_needs(self, time_delta: timedelta = None):
        """Update all needs based on time passed"""
        if time_delta is None:
            time_delta = datetime.now() - self.last_comprehensive_update
        
        for need in self.needs.values():
            need.update(time_delta)
        
        self.last_comprehensive_update = datetime.now()
        self._update_growth_stage()
    
    def _update_growth_stage(self):
        """Update the current growth stage based on need satisfaction"""
        # Calculate average satisfaction for each level
        level_satisfactions = {}
        for level in NeedLevel:
            level_needs = [need for need in self.needs.values() if need.level == level]
            if level_needs:
                avg_satisfaction = sum(need.satisfaction for need in level_needs) / len(level_needs)
                level_satisfactions[level] = avg_satisfaction
        
        # Determine growth stage based on level satisfaction
        if level_satisfactions.get(NeedLevel.PHYSIOLOGICAL, 0) >= 70:
            if level_satisfactions.get(NeedLevel.SAFETY, 0) >= 70:
                if level_satisfactions.get(NeedLevel.SOCIAL, 0) >= 60:
                    if level_satisfactions.get(NeedLevel.ESTEEM, 0) >= 50:
                        if level_satisfactions.get(NeedLevel.SELF_ACTUALIZATION, 0) >= 30:
                            self.growth_stage = 5  # Self-actualization
                        else:
                            self.growth_stage = 4  # Esteem
                    else:
                        self.growth_stage = 3  # Social
                else:
                    self.growth_stage = 2  # Safety
            else:
                self.growth_stage = 1  # Physiological
    
    def satisfy_need(self, need_name: str, amount: float, source: str = "unknown") -> float:
        """Satisfy a specific need"""
        if need_name not in self.needs:
            raise ValueError(f"Unknown need: {need_name}")
        
        return self.needs[need_name].satisfy(amount, source)
    
    def get_need_satisfaction(self, need_name: str) -> float:
        """Get satisfaction level for a specific need"""
        return self.needs.get(need_name, MaslowNeed(need_name, NeedCategory.FOOD, NeedLevel.PHYSIOLOGICAL, 0.0)).satisfaction
    
    def get_level_satisfaction(self, level: NeedLevel) -> float:
        """Get average satisfaction for a specific level"""
        level_needs = [need for need in self.needs.values() if need.level == level]
        if not level_needs:
            return 0.0
        return sum(need.satisfaction for need in level_needs) / len(level_needs)
    
    def get_overall_satisfaction(self) -> float:
        """Calculate weighted overall satisfaction across all levels"""
        if not self.needs:
            return 0.0
        
        # Weight by level importance (lower levels more important)
        total_weighted_satisfaction = 0
        total_weight = 0
        
        for need in self.needs.values():
            weight = (6 - need.level.value) * need.importance  # Higher weight for lower levels
            total_weighted_satisfaction += need.satisfaction * weight
            total_weight += weight
        
        return total_weighted_satisfaction / total_weight if total_weight > 0 else 0
    
    def get_critical_needs(self) -> List[str]:
        """Get list of needs that are critically low, prioritized by level"""
        critical_needs = [need for need in self.needs.values() if need.is_critical()]
        critical_needs.sort(key=lambda x: x.get_priority_score(), reverse=True)
        return [need.name for need in critical_needs]
    
    def get_low_needs(self) -> List[str]:
        """Get list of needs that are low, prioritized by level"""
        low_needs = [need for need in self.needs.values() if need.is_low()]
        low_needs.sort(key=lambda x: x.get_priority_score(), reverse=True)
        return [need.name for need in low_needs]
    
    def get_priority_needs(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get the most urgent needs to address"""
        all_needs = list(self.needs.values())
        all_needs.sort(key=lambda x: x.get_priority_score(), reverse=True)
        
        priority_needs = []
        for need in all_needs[:top_k]:
            priority_needs.append({
                'name': need.name,
                'category': need.category.value,
                'level': need.level.value,
                'satisfaction': need.satisfaction,
                'priority_score': need.get_priority_score(),
                'is_critical': need.is_critical(),
                'is_low': need.is_low()
            })
        
        return priority_needs
    
    def get_growth_insights(self) -> Dict[str, Any]:
        """Get insights about personal growth and development"""
        insights = {
            'current_stage': self.growth_stage,
            'stage_name': self._get_stage_name(self.growth_stage),
            'level_satisfactions': {},
            'next_priorities': [],
            'growth_opportunities': []
        }
        
        # Level satisfactions
        for level in NeedLevel:
            insights['level_satisfactions'][level.name] = self.get_level_satisfaction(level)
        
        # Next priorities
        insights['next_priorities'] = self.get_priority_needs(3)
        
        # Growth opportunities (needs that can grow beyond 100)
        growth_needs = [need for need in self.needs.values() 
                       if need.level == NeedLevel.SELF_ACTUALIZATION and need.satisfaction < need.max_satisfaction]
        insights['growth_opportunities'] = [
            {
                'name': need.name,
                'current': need.satisfaction,
                'potential': need.max_satisfaction,
                'growth_room': need.max_satisfaction - need.satisfaction
            }
            for need in growth_needs
        ]
        
        return insights
    
    def _get_stage_name(self, stage: int) -> str:
        """Get human-readable name for growth stage"""
        stage_names = {
            1: "Survival Mode",
            2: "Safety Seeking",
            3: "Social Connection",
            4: "Achievement & Recognition",
            5: "Self-Actualization"
        }
        return stage_names.get(stage, "Unknown Stage")
    
    def add_need(self, name: str, category: NeedCategory, level: NeedLevel, 
                initial_satisfaction: float = 100.0, decay_rate: float = 10.0, 
                importance: float = 1.0, growth_rate: float = 0.0, max_satisfaction: float = 100.0):
        """Add a new need to the system"""
        self.needs[name] = MaslowNeed(
            name=name,
            category=category,
            level=level,
            satisfaction=initial_satisfaction,
            decay_rate=decay_rate,
            importance=importance,
            growth_rate=growth_rate,
            max_satisfaction=max_satisfaction
        )
    
    def remove_need(self, name: str):
        """Remove a need from the system"""
        if name in self.needs:
            del self.needs[name]
    
    def get_needs_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all needs"""
        summary = {
            'overall_satisfaction': self.get_overall_satisfaction(),
            'growth_stage': self.growth_stage,
            'stage_name': self._get_stage_name(self.growth_stage),
            'critical_needs_count': len(self.get_critical_needs()),
            'low_needs_count': len(self.get_low_needs()),
            'level_summaries': {},
            'priority_needs': self.get_priority_needs(5)
        }
        
        # Summarize each level
        for level in NeedLevel:
            level_needs = [need for need in self.needs.values() if need.level == level]
            if level_needs:
                summary['level_summaries'][level.name] = {
                    'average_satisfaction': sum(need.satisfaction for need in level_needs) / len(level_needs),
                    'need_count': len(level_needs),
                    'critical_count': len([need for need in level_needs if need.is_critical()]),
                    'low_count': len([need for need in level_needs if need.is_low()])
                }
        
        return summary
    
    def __str__(self):
        """String representation of the needs system"""
        summary = self.get_needs_summary()
        needs_str = ", ".join([f"{name}: {need.satisfaction:.1f}" for name, need in self.needs.items()])
        return f"MaslowNeeds(stage: {summary['stage_name']}, overall: {summary['overall_satisfaction']:.1f}%, {needs_str})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'needs': {name: {
                'name': need.name,
                'category': need.category.value,
                'level': need.level.value,
                'satisfaction': need.satisfaction,
                'decay_rate': need.decay_rate,
                'importance': need.importance,
                'growth_rate': need.growth_rate,
                'max_satisfaction': need.max_satisfaction,
                'last_updated': need.last_updated.isoformat()
            } for name, need in self.needs.items()},
            'growth_stage': self.growth_stage,
            'last_comprehensive_update': self.last_comprehensive_update.isoformat(),
            'personality_traits': self.personality_traits
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaslowNeedsSystem':
        """Create from dictionary"""
        system = cls()
        system.growth_stage = data.get('growth_stage', 1)
        system.last_comprehensive_update = datetime.fromisoformat(data.get('last_comprehensive_update', datetime.now().isoformat()))
        system.personality_traits = data.get('personality_traits', {})
        
        # Reconstruct needs
        for name, need_data in data.get('needs', {}).items():
            need = MaslowNeed(
                name=need_data['name'],
                category=NeedCategory(need_data['category']),
                level=NeedLevel(need_data['level']),
                satisfaction=need_data['satisfaction'],
                decay_rate=need_data['decay_rate'],
                importance=need_data['importance'],
                growth_rate=need_data.get('growth_rate', 0.0),
                max_satisfaction=need_data.get('max_satisfaction', 100.0),
                last_updated=datetime.fromisoformat(need_data['last_updated'])
            )
            system.needs[name] = need
        
        return system


# Backward compatibility classes and functions
@dataclass
class Need:
    """Legacy Need class for backward compatibility"""
    name: str
    satisfaction: float = 100.0
    decay_rate: float = 10.0
    
    def update(self):
        """Decrease satisfaction over time"""
        self.satisfaction = max(0, self.satisfaction - random.uniform(0.5 * self.decay_rate, 1.5 * self.decay_rate))
        
    def satisfy(self, amount: float):
        """Increase satisfaction by given amount"""
        self.satisfaction = min(100, self.satisfaction + amount)
        
    def is_critical(self) -> bool:
        """Check if need is critically low (below 20)"""
        return self.satisfaction < 20
        
    def is_low(self) -> bool:
        """Check if need is low (below 50)"""
        return self.satisfaction < 50


class BasicNeeds:
    """Legacy BasicNeeds class for backward compatibility - now wraps MaslowNeedsSystem"""
    
    def __init__(self):
        self.maslow_system = MaslowNeedsSystem()
        # Map legacy need names to Maslow needs
        self.legacy_mapping = {
            'hunger': 'hunger',
            'sleep': 'sleep', 
            'safety': 'security'
        }
    
    @property
    def needs(self):
        """Legacy needs property that maps to Maslow needs"""
        legacy_needs = {}
        for legacy_name, maslow_name in self.legacy_mapping.items():
            if maslow_name in self.maslow_system.needs:
                maslow_need = self.maslow_system.needs[maslow_name]
                legacy_needs[legacy_name] = Need(
                    name=legacy_name,
                    satisfaction=maslow_need.satisfaction,
                    decay_rate=maslow_need.decay_rate
                )
        return legacy_needs
    
    def update_needs(self):
        """Update all needs (decrease satisfaction over time)"""
        self.maslow_system.update_all_needs()
    
    def satisfy_need(self, need_name: str, amount: float):
        """Satisfy a specific need"""
        if need_name in self.legacy_mapping:
            maslow_name = self.legacy_mapping[need_name]
            self.maslow_system.satisfy_need(maslow_name, amount)
        else:
            raise ValueError(f"Unknown need: {need_name}")
    
    def get_need_satisfaction(self, need_name: str) -> float:
        """Get satisfaction level for a specific need"""
        if need_name in self.legacy_mapping:
            maslow_name = self.legacy_mapping[need_name]
            return self.maslow_system.get_need_satisfaction(maslow_name)
        return 0.0
    
    def get_overall_satisfaction(self) -> float:
        """Calculate overall satisfaction percentage across all needs"""
        return self.maslow_system.get_overall_satisfaction()
    
    def get_critical_needs(self) -> list:
        """Get list of needs that are critically low"""
        return [need.name for need in self.needs.values() if need.is_critical()]
    
    def get_low_needs(self) -> list:
        """Get list of needs that are low"""
        return [need.name for need in self.needs.values() if need.is_low()]
    
    def add_need(self, name: str, initial_satisfaction: float = 100.0, decay_rate: float = 10.0):
        """Add a new need to the system"""
        # Map to appropriate Maslow category
        if name not in self.legacy_mapping:
            self.legacy_mapping[name] = name
            # Add to Maslow system with default physiological category
            self.maslow_system.add_need(name, NeedCategory.FOOD, NeedLevel.PHYSIOLOGICAL, 
                                      initial_satisfaction, decay_rate)
    
    def remove_need(self, name: str):
        """Remove a need from the system"""
        if name in self.legacy_mapping:
            maslow_name = self.legacy_mapping[name]
            self.maslow_system.remove_need(maslow_name)
            del self.legacy_mapping[name]
    
    def __str__(self):
        needs_str = ", ".join([f"{name}: {need.satisfaction:.1f}" for name, need in self.needs.items()])
        return f"BasicNeeds(overall: {self.get_overall_satisfaction():.1f}%, {needs_str})"


def create_basic_needs_chain(llm_json_mode, person: BasicNeeds):
    """Legacy function for backward compatibility - now uses Maslow decision system"""
    from core.needs.maslow_decision_chain import create_maslow_decision_chain
    
    # Convert BasicNeeds to MaslowNeedsSystem for decision making
    if hasattr(person, 'maslow_system'):
        return create_maslow_decision_chain(llm_json_mode, person.maslow_system)
    else:
        # Fallback to basic decision making
        needs_prompt = PromptTemplate(
            input_variables=["needs_status", "overall_satisfaction", "critical_needs", "low_needs"],
            template="""You are an AI making decisions based on basic needs.

Current needs status: {needs_status}
Overall satisfaction: {overall_satisfaction:.1f}%
Critical needs (below 20%): {critical_needs}
Low needs (below 50%): {low_needs}

Based on these needs, what action should be taken? 
Respond in JSON format with two fields:
- action: what to do (eat, sleep, find_safety, find_food, rest, or continue_activities)
- reasoning: brief explanation why

Consider:
- Critical needs (below 20%): Immediate action required
- Low needs (below 50%): Should address soon
- Above 50%: Can continue other activities
- Prioritize the most critical needs first"""
        )

        # Prepare the needs status string
        needs_status = ", ".join([f"{name}: {need.satisfaction:.1f}%" for name, need in person.needs.items()])
        
        # Use the newer invoke method instead of run
        response = llm_json_mode.invoke(
            needs_prompt.format(
                needs_status=needs_status,
                overall_satisfaction=person.get_overall_satisfaction(),
                critical_needs=person.get_critical_needs(),
                low_needs=person.get_low_needs()
            )
        )
        
        # Extract content from the response
        response_content = response.content if hasattr(response, 'content') else str(response)
        
        print(f"Current state: {person}")
        print(f"AI Decision: {response_content}")
        return response_content 
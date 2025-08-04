#!/usr/bin/env python3
"""
Unit tests for the Maslow needs system
Tests all functionality including needs, growth stages, and decision making
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
import json

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from core.needs.maslow_needs import (
    MaslowNeedsSystem, MaslowNeed, NeedLevel, NeedCategory,
    BasicNeeds, Need, create_basic_needs_chain
)


class TestMaslowNeed(unittest.TestCase):
    """Test individual MaslowNeed functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.need = MaslowNeed(
            name="test_need",
            category=NeedCategory.FOOD,
            level=NeedLevel.PHYSIOLOGICAL,
            satisfaction=80.0,
            decay_rate=5.0,
            importance=1.0
        )
    
    def test_need_initialization(self):
        """Test need initialization with correct values"""
        self.assertEqual(self.need.name, "test_need")
        self.assertEqual(self.need.category, NeedCategory.FOOD)
        self.assertEqual(self.need.level, NeedLevel.PHYSIOLOGICAL)
        self.assertEqual(self.need.satisfaction, 80.0)
        self.assertEqual(self.need.decay_rate, 5.0)
        self.assertEqual(self.need.importance, 1.0)
    
    def test_need_update(self):
        """Test need satisfaction decay over time"""
        initial_satisfaction = self.need.satisfaction
        self.need.update(timedelta(hours=1))
        
        # Satisfaction should decrease
        self.assertLess(self.need.satisfaction, initial_satisfaction)
        self.assertGreaterEqual(self.need.satisfaction, 0)
    
    def test_need_satisfy(self):
        """Test satisfying a need"""
        initial_satisfaction = self.need.satisfaction
        satisfied_amount = self.need.satisfy(20.0, "test_source")
        
        self.assertEqual(satisfied_amount, 20.0)
        self.assertEqual(self.need.satisfaction, 100.0)  # Should cap at 100
    
    def test_need_satisfy_overflow(self):
        """Test that satisfaction doesn't exceed 100 for regular needs"""
        self.need.satisfaction = 95.0
        satisfied_amount = self.need.satisfy(20.0, "test_source")
        
        self.assertEqual(satisfied_amount, 5.0)  # Only 5 points satisfied
        self.assertEqual(self.need.satisfaction, 100.0)
    
    def test_self_actualization_growth(self):
        """Test that self-actualization needs can grow beyond 100"""
        growth_need = MaslowNeed(
            name="creativity",
            category=NeedCategory.CREATIVITY,
            level=NeedLevel.SELF_ACTUALIZATION,
            satisfaction=90.0,
            growth_rate=0.5,
            max_satisfaction=150.0
        )
        
        satisfied_amount = growth_need.satisfy(30.0, "test_source")
        self.assertEqual(satisfied_amount, 30.0)
        self.assertEqual(growth_need.satisfaction, 120.0)
    
    def test_need_critical_status(self):
        """Test critical status detection"""
        # Physiological need should be critical below 20
        self.need.satisfaction = 15.0
        self.assertTrue(self.need.is_critical())
        
        self.need.satisfaction = 25.0
        self.assertFalse(self.need.is_critical())
        
        # Safety need should be critical below 30
        safety_need = MaslowNeed(
            name="security",
            category=NeedCategory.SECURITY,
            level=NeedLevel.SAFETY,
            satisfaction=25.0
        )
        self.assertTrue(safety_need.is_critical())
    
    def test_need_low_status(self):
        """Test low status detection"""
        self.need.satisfaction = 40.0
        self.assertTrue(self.need.is_low())
        
        self.need.satisfaction = 60.0
        self.assertFalse(self.need.is_low())
    
    def test_priority_score(self):
        """Test priority score calculation"""
        # Lower level needs should have higher priority
        physiological_need = MaslowNeed(
            name="hunger",
            category=NeedCategory.FOOD,
            level=NeedLevel.PHYSIOLOGICAL,
            satisfaction=50.0
        )
        
        esteem_need = MaslowNeed(
            name="confidence",
            category=NeedCategory.CONFIDENCE,
            level=NeedLevel.ESTEEM,
            satisfaction=50.0
        )
        
        self.assertGreater(physiological_need.get_priority_score(), esteem_need.get_priority_score())


class TestMaslowNeedsSystem(unittest.TestCase):
    """Test the complete Maslow needs system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.needs_system = MaslowNeedsSystem()
    
    def test_system_initialization(self):
        """Test system initialization with all needs"""
        # Should have needs for all 5 levels
        self.assertGreater(len(self.needs_system.needs), 15)
        
        # Check that all levels are represented
        levels = set(need.level for need in self.needs_system.needs.values())
        self.assertEqual(len(levels), 5)
        self.assertIn(NeedLevel.PHYSIOLOGICAL, levels)
        self.assertIn(NeedLevel.SAFETY, levels)
        self.assertIn(NeedLevel.SOCIAL, levels)
        self.assertIn(NeedLevel.ESTEEM, levels)
        self.assertIn(NeedLevel.SELF_ACTUALIZATION, levels)
    
    def test_update_all_needs(self):
        """Test updating all needs over time"""
        initial_satisfactions = {
            name: need.satisfaction 
            for name, need in self.needs_system.needs.items()
        }
        
        self.needs_system.update_all_needs(timedelta(hours=2))
        
        # All satisfactions should have decreased
        for name, need in self.needs_system.needs.items():
            self.assertLessEqual(need.satisfaction, initial_satisfactions[name])
    
    def test_satisfy_need(self):
        """Test satisfying a specific need"""
        # First reduce the need so we can satisfy it
        self.needs_system.needs['hunger'].satisfaction = 70.0
        
        initial_satisfaction = self.needs_system.get_need_satisfaction('hunger')
        satisfied_amount = self.needs_system.satisfy_need('hunger', 30.0, 'test')
        
        # The satisfied amount should be the amount we tried to satisfy
        self.assertGreater(satisfied_amount, 0.0)
        new_satisfaction = self.needs_system.get_need_satisfaction('hunger')
        self.assertGreaterEqual(new_satisfaction, initial_satisfaction)
    
    def test_get_level_satisfaction(self):
        """Test getting average satisfaction for a level"""
        satisfaction = self.needs_system.get_level_satisfaction(NeedLevel.PHYSIOLOGICAL)
        self.assertGreaterEqual(satisfaction, 0)
        self.assertLessEqual(satisfaction, 100)
    
    def test_get_overall_satisfaction(self):
        """Test overall satisfaction calculation"""
        satisfaction = self.needs_system.get_overall_satisfaction()
        self.assertGreaterEqual(satisfaction, 0)
        self.assertLessEqual(satisfaction, 100)
    
    def test_get_critical_needs(self):
        """Test getting critical needs"""
        # Set some needs to critical levels
        self.needs_system.needs['hunger'].satisfaction = 15.0
        self.needs_system.needs['love'].satisfaction = 25.0
        
        critical_needs = self.needs_system.get_critical_needs()
        self.assertIn('hunger', critical_needs)
        self.assertIn('love', critical_needs)
    
    def test_get_low_needs(self):
        """Test getting low needs"""
        # Set some needs to low levels
        self.needs_system.needs['hunger'].satisfaction = 40.0
        self.needs_system.needs['confidence'].satisfaction = 45.0
        
        low_needs = self.needs_system.get_low_needs()
        self.assertIn('hunger', low_needs)
        self.assertIn('confidence', low_needs)
    
    def test_get_priority_needs(self):
        """Test getting priority needs"""
        priority_needs = self.needs_system.get_priority_needs(5)
        
        self.assertLessEqual(len(priority_needs), 5)
        for need in priority_needs:
            self.assertIn('name', need)
            self.assertIn('satisfaction', need)
            self.assertIn('priority_score', need)
    
    def test_growth_stage_progression(self):
        """Test automatic growth stage progression"""
        # Start at survival mode
        self.assertEqual(self.needs_system.growth_stage, 1)
        
        # Satisfy physiological needs to advance to safety stage
        self.needs_system.satisfy_need('hunger', 50.0, 'test')
        self.needs_system.satisfy_need('thirst', 50.0, 'test')
        self.needs_system.satisfy_need('sleep', 50.0, 'test')
        
        self.needs_system._update_growth_stage()
        # The stage should advance, but we don't know exactly which stage
        self.assertGreater(self.needs_system.growth_stage, 1)
    
    def test_get_growth_insights(self):
        """Test growth insights generation"""
        insights = self.needs_system.get_growth_insights()
        
        self.assertIn('current_stage', insights)
        self.assertIn('stage_name', insights)
        self.assertIn('level_satisfactions', insights)
        self.assertIn('next_priorities', insights)
        self.assertIn('growth_opportunities', insights)
    
    def test_get_needs_summary(self):
        """Test needs summary generation"""
        summary = self.needs_system.get_needs_summary()
        
        self.assertIn('overall_satisfaction', summary)
        self.assertIn('growth_stage', summary)
        self.assertIn('stage_name', summary)
        self.assertIn('critical_needs_count', summary)
        self.assertIn('low_needs_count', summary)
        self.assertIn('level_summaries', summary)
        self.assertIn('priority_needs', summary)
    
    def test_add_need(self):
        """Test adding a new need"""
        initial_count = len(self.needs_system.needs)
        
        self.needs_system.add_need(
            'custom_need',
            NeedCategory.FOOD,
            NeedLevel.PHYSIOLOGICAL,
            initial_satisfaction=75.0,
            decay_rate=3.0,
            importance=0.8
        )
        
        self.assertEqual(len(self.needs_system.needs), initial_count + 1)
        self.assertIn('custom_need', self.needs_system.needs)
        
        need = self.needs_system.needs['custom_need']
        self.assertEqual(need.satisfaction, 75.0)
        self.assertEqual(need.decay_rate, 3.0)
        self.assertEqual(need.importance, 0.8)
    
    def test_remove_need(self):
        """Test removing a need"""
        initial_count = len(self.needs_system.needs)
        
        self.needs_system.remove_need('hunger')
        
        self.assertEqual(len(self.needs_system.needs), initial_count - 1)
        self.assertNotIn('hunger', self.needs_system.needs)
    
    def test_serialization(self):
        """Test serialization and deserialization"""
        # Modify some needs
        self.needs_system.satisfy_need('hunger', 20.0, 'test')
        self.needs_system.satisfy_need('love', 15.0, 'test')
        
        # Serialize
        data = self.needs_system.to_dict()
        
        # Deserialize
        new_system = MaslowNeedsSystem.from_dict(data)
        
        # Check that the systems are equivalent
        self.assertEqual(new_system.growth_stage, self.needs_system.growth_stage)
        self.assertEqual(
            new_system.get_need_satisfaction('hunger'),
            self.needs_system.get_need_satisfaction('hunger')
        )
        self.assertEqual(
            new_system.get_need_satisfaction('love'),
            self.needs_system.get_need_satisfaction('love')
        )


class TestBasicNeedsBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with BasicNeeds"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.basic_needs = BasicNeeds()
    
    def test_basic_needs_initialization(self):
        """Test BasicNeeds initialization"""
        self.assertIsNotNone(self.basic_needs.maslow_system)
        self.assertIn('hunger', self.basic_needs.legacy_mapping)
        self.assertIn('sleep', self.basic_needs.legacy_mapping)
        self.assertIn('safety', self.basic_needs.legacy_mapping)
    
    def test_basic_needs_property(self):
        """Test the needs property mapping"""
        needs = self.basic_needs.needs
        self.assertIn('hunger', needs)
        self.assertIn('sleep', needs)
        self.assertIn('safety', needs)
        
        # Check that they're Need objects (legacy)
        for need in needs.values():
            self.assertIsInstance(need, Need)
    
    def test_basic_needs_update(self):
        """Test updating basic needs"""
        initial_satisfaction = self.basic_needs.get_overall_satisfaction()
        self.basic_needs.update_needs()
        
        # Should have changed due to time passing
        new_satisfaction = self.basic_needs.get_overall_satisfaction()
        self.assertNotEqual(initial_satisfaction, new_satisfaction)
    
    def test_basic_needs_satisfy(self):
        """Test satisfying basic needs"""
        initial_satisfaction = self.basic_needs.get_need_satisfaction('hunger')
        self.basic_needs.satisfy_need('hunger', 20.0)
        
        new_satisfaction = self.basic_needs.get_need_satisfaction('hunger')
        self.assertEqual(new_satisfaction, min(100.0, initial_satisfaction + 20.0))
    
    def test_basic_needs_critical_low(self):
        """Test critical and low need detection"""
        # Set hunger to critical level
        self.basic_needs.maslow_system.needs['hunger'].satisfaction = 15.0
        
        critical_needs = self.basic_needs.get_critical_needs()
        low_needs = self.basic_needs.get_low_needs()
        
        self.assertIn('hunger', critical_needs)
        self.assertIn('hunger', low_needs)
    
    def test_basic_needs_add_remove(self):
        """Test adding and removing needs"""
        initial_count = len(self.basic_needs.needs)
        
        # Add a new need
        self.basic_needs.add_need('test_need', 80.0, 5.0)
        self.assertEqual(len(self.basic_needs.needs), initial_count + 1)
        self.assertIn('test_need', self.basic_needs.needs)
        
        # Remove the need
        self.basic_needs.remove_need('test_need')
        self.assertEqual(len(self.basic_needs.needs), initial_count)
        self.assertNotIn('test_need', self.basic_needs.needs)


class TestLegacyNeed(unittest.TestCase):
    """Test the legacy Need class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.need = Need('test_need', 80.0, 5.0)
    
    def test_need_initialization(self):
        """Test legacy Need initialization"""
        self.assertEqual(self.need.name, 'test_need')
        self.assertEqual(self.need.satisfaction, 80.0)
        self.assertEqual(self.need.decay_rate, 5.0)
    
    def test_need_update(self):
        """Test legacy Need update"""
        initial_satisfaction = self.need.satisfaction
        self.need.update()
        
        self.assertLess(self.need.satisfaction, initial_satisfaction)
        self.assertGreaterEqual(self.need.satisfaction, 0)
    
    def test_need_satisfy(self):
        """Test legacy Need satisfy"""
        initial_satisfaction = self.need.satisfaction
        self.need.satisfy(20.0)
        
        self.assertEqual(self.need.satisfaction, min(100.0, initial_satisfaction + 20.0))
    
    def test_need_critical_low(self):
        """Test legacy Need critical and low detection"""
        self.need.satisfaction = 15.0
        self.assertTrue(self.need.is_critical())
        self.assertTrue(self.need.is_low())
        
        self.need.satisfaction = 30.0
        self.assertFalse(self.need.is_critical())
        self.assertTrue(self.need.is_low())
        
        self.need.satisfaction = 60.0
        self.assertFalse(self.need.is_critical())
        self.assertFalse(self.need.is_low())


if __name__ == '__main__':
    unittest.main() 
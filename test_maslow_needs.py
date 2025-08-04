#!/usr/bin/env python3
"""
Test script for the Maslow's hierarchy of needs system
Demonstrates all five levels of human motivation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from datetime import datetime, timedelta
from maslow_needs import MaslowNeedsSystem, NeedLevel, NeedCategory
import json

def test_maslow_needs_system():
    """Test the comprehensive Maslow needs system"""
    
    print("🧠 Initializing Maslow's Hierarchy of Needs System...")
    
    # Create the needs system
    needs_system = MaslowNeedsSystem()
    
    print(f"✅ Needs system initialized")
    print(f"📊 Initial state: {needs_system}")
    
    # Show initial summary
    print(f"\n📋 Initial Needs Summary:")
    summary = needs_system.get_needs_summary()
    print(json.dumps(summary, indent=2))
    
    # Show growth insights
    print(f"\n🌱 Growth Insights:")
    insights = needs_system.get_growth_insights()
    print(json.dumps(insights, indent=2))
    
    # Simulate time passing and need decay
    print(f"\n⏰ Simulating time passing (2 hours)...")
    needs_system.update_all_needs(timedelta(hours=2))
    print(f"📊 After 2 hours: {needs_system}")
    
    # Show priority needs
    print(f"\n🎯 Priority Needs (Top 5):")
    priority_needs = needs_system.get_priority_needs(5)
    for i, need in enumerate(priority_needs, 1):
        print(f"  {i}. {need['name']} (Level {need['level']}): {need['satisfaction']:.1f}% - Priority: {need['priority_score']:.2f}")
    
    # Satisfy some needs
    print(f"\n🍽️ Satisfying some needs...")
    
    # Satisfy physiological needs
    hunger_satisfied = needs_system.satisfy_need('hunger', 30.0, 'eating')
    print(f"  ✅ Satisfied hunger by {hunger_satisfied:.1f} points")
    
    thirst_satisfied = needs_system.satisfy_need('thirst', 25.0, 'drinking')
    print(f"  ✅ Satisfied thirst by {thirst_satisfied:.1f} points")
    
    # Satisfy social needs
    friendship_satisfied = needs_system.satisfy_need('friendship', 15.0, 'social_interaction')
    print(f"  ✅ Satisfied friendship by {friendship_satisfied:.1f} points")
    
    # Satisfy esteem needs
    confidence_satisfied = needs_system.satisfy_need('confidence', 10.0, 'achievement')
    print(f"  ✅ Satisfied confidence by {confidence_satisfied:.1f} points")
    
    # Satisfy self-actualization needs
    creativity_satisfied = needs_system.satisfy_need('creativity', 20.0, 'creative_activity')
    print(f"  ✅ Satisfied creativity by {creativity_satisfied:.1f} points")
    
    print(f"\n📊 After satisfying needs: {needs_system}")
    
    # Show updated summary
    print(f"\n📋 Updated Needs Summary:")
    updated_summary = needs_system.get_needs_summary()
    print(json.dumps(updated_summary, indent=2))
    
    # Show level satisfactions
    print(f"\n📈 Level Satisfactions:")
    for level in NeedLevel:
        satisfaction = needs_system.get_level_satisfaction(level)
        print(f"  {level.name}: {satisfaction:.1f}%")
    
    # Show critical and low needs
    print(f"\n🚨 Critical Needs: {needs_system.get_critical_needs()}")
    print(f"⚠️ Low Needs: {needs_system.get_low_needs()}")
    
    # Simulate more time passing
    print(f"\n⏰ Simulating more time passing (5 hours)...")
    needs_system.update_all_needs(timedelta(hours=5))
    print(f"📊 After 5 more hours: {needs_system}")
    
    # Show final growth insights
    print(f"\n🌱 Final Growth Insights:")
    final_insights = needs_system.get_growth_insights()
    print(json.dumps(final_insights, indent=2))
    
    # Test serialization
    print(f"\n💾 Testing serialization...")
    needs_dict = needs_system.to_dict()
    reconstructed_system = MaslowNeedsSystem.from_dict(needs_dict)
    print(f"✅ Serialization/deserialization successful")
    print(f"📊 Reconstructed system: {reconstructed_system}")
    
    print(f"\n✅ Maslow needs system test completed successfully!")

def demonstrate_growth_stages():
    """Demonstrate how the system progresses through growth stages"""
    
    print(f"\n🌱 Demonstrating Growth Stages...")
    
    # Create a system starting at survival mode
    needs_system = MaslowNeedsSystem()
    
    # Start with very low physiological needs
    needs_system.needs['hunger'].satisfaction = 15.0
    needs_system.needs['thirst'].satisfaction = 20.0
    needs_system.needs['sleep'].satisfaction = 10.0
    
    print(f"📊 Stage 1 - Survival Mode: {needs_system}")
    
    # Satisfy physiological needs to move to safety stage
    print(f"\n🛡️ Satisfying physiological needs...")
    needs_system.satisfy_need('hunger', 60.0, 'eating')
    needs_system.satisfy_need('thirst', 65.0, 'drinking')
    needs_system.satisfy_need('sleep', 70.0, 'sleeping')
    
    needs_system._update_growth_stage()
    print(f"📊 Stage 2 - Safety Seeking: {needs_system}")
    
    # Satisfy safety needs to move to social stage
    print(f"\n👥 Satisfying safety needs...")
    needs_system.satisfy_need('security', 75.0, 'finding_safety')
    needs_system.satisfy_need('stability', 80.0, 'establishing_routine')
    needs_system.satisfy_need('protection', 70.0, 'finding_shelter')
    
    needs_system._update_growth_stage()
    print(f"📊 Stage 3 - Social Connection: {needs_system}")
    
    # Satisfy social needs to move to esteem stage
    print(f"\n💕 Satisfying social needs...")
    needs_system.satisfy_need('friendship', 75.0, 'making_friends')
    needs_system.satisfy_need('love', 70.0, 'finding_love')
    needs_system.satisfy_need('belonging', 80.0, 'joining_community')
    
    needs_system._update_growth_stage()
    print(f"📊 Stage 4 - Achievement & Recognition: {needs_system}")
    
    # Satisfy esteem needs to move to self-actualization
    print(f"\n🏆 Satisfying esteem needs...")
    needs_system.satisfy_need('self_esteem', 75.0, 'self_improvement')
    needs_system.satisfy_need('confidence', 80.0, 'achieving_goals')
    needs_system.satisfy_need('achievement', 70.0, 'accomplishing_tasks')
    needs_system.satisfy_need('respect', 75.0, 'earning_respect')
    
    needs_system._update_growth_stage()
    print(f"📊 Stage 5 - Self-Actualization: {needs_system}")
    
    # Work on self-actualization needs
    print(f"\n🌟 Working on self-actualization...")
    needs_system.satisfy_need('personal_growth', 50.0, 'learning_new_skills')
    needs_system.satisfy_need('creativity', 60.0, 'creative_expression')
    needs_system.satisfy_need('purpose', 40.0, 'finding_meaning')
    needs_system.satisfy_need('meaning', 35.0, 'philosophical_exploration')
    
    print(f"📊 Final Stage - Self-Actualization: {needs_system}")
    
    # Show growth opportunities
    print(f"\n🚀 Growth Opportunities:")
    growth_opportunities = needs_system.get_growth_insights()['growth_opportunities']
    for opportunity in growth_opportunities:
        print(f"  {opportunity['name']}: {opportunity['current']:.1f}/{opportunity['potential']:.1f} ({opportunity['growth_room']:.1f} room for growth)")

if __name__ == "__main__":
    test_maslow_needs_system()
    demonstrate_growth_stages() 
#!/usr/bin/env python3
"""
Test script for the enhanced Maslow decision-making system
Demonstrates decision making, action execution, and goal setting
"""

import sys
import os
# Add the parent directory to the path to allow importing core module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from core.needs.maslow_needs import MaslowNeedsSystem
from core.needs.maslow_decision_chain import (
    create_maslow_decision_chain,
    create_maslow_action_executor,
    create_maslow_goal_setter,
    analyze_maslow_progress
)
from langchain_ollama import ChatOllama
import json

def test_maslow_decision_system():
    """Test the comprehensive Maslow decision-making system"""
    
    print("🧠 Initializing Enhanced Maslow Decision System...")
    
    # Initialize LLM
    llm_json_mode = ChatOllama(model="llama3.2:3b-instruct-fp16", temperature=0, format='json')
    
    # Create needs system with some needs already low
    needs_system = MaslowNeedsSystem()
    
    # Simulate some time passing to create realistic need states
    needs_system.update_all_needs(timedelta(hours=3))
    
    # Manually set some needs to low levels to test decision making
    needs_system.needs['hunger'].satisfaction = 25.0
    needs_system.needs['sleep'].satisfaction = 30.0
    needs_system.needs['love'].satisfaction = 35.0
    needs_system.needs['confidence'].satisfaction = 20.0
    
    print(f"✅ Initial state: {needs_system}")
    
    # Test decision making
    print(f"\n🤔 Testing Decision Making...")
    try:
        decision = create_maslow_decision_chain(llm_json_mode, needs_system)
        print(f"Decision: {decision}")
    except Exception as e:
        print(f"Decision making failed: {e}")
        # Create a mock decision for testing
        decision = {
            "action": "eat",
            "category": "PHYSIOLOGICAL",
            "reasoning": "Hunger is critically low and needs immediate attention",
            "urgency": "critical",
            "expected_outcome": "Satisfy hunger need and improve overall health",
            "alternative_actions": ["drink", "rest", "find_food"]
        }
        print(f"Using mock decision: {json.dumps(decision, indent=2)}")
    
    # Test action execution
    print(f"\n⚡ Testing Action Execution...")
    action_executor = create_maslow_action_executor(needs_system)
    
    # Execute the recommended action
    if isinstance(decision, dict):
        action = decision.get('action', 'eat')
    else:
        action = 'eat'  # Default action
    
    result = action_executor(action)
    print(f"Action executed: {action}")
    print(f"Result: {json.dumps(result, indent=2)}")
    
    print(f"📊 After action: {needs_system}")
    
    # Test goal setting
    print(f"\n🎯 Testing Goal Setting...")
    goal_setter = create_maslow_goal_setter(needs_system)
    goals = goal_setter()
    print(f"Generated Goals: {json.dumps(goals, indent=2)}")
    
    # Test progress analysis
    print(f"\n📈 Testing Progress Analysis...")
    progress = analyze_maslow_progress(needs_system)
    print(f"Progress Analysis: {json.dumps(progress, indent=2)}")
    
    # Simulate a series of actions
    print(f"\n🔄 Simulating Action Sequence...")
    actions_to_test = ['drink', 'sleep', 'socialize', 'build_confidence', 'learn_new_things']
    
    for action in actions_to_test:
        print(f"\n--- Executing: {action} ---")
        result = action_executor(action)
        print(f"Result: {result}")
        print(f"Current state: {needs_system}")
        
        # Show updated goals after each action
        updated_goals = goal_setter()
        print(f"Updated immediate goals: {len(updated_goals['immediate_goals'])}")
    
    # Final analysis
    print(f"\n📊 Final Analysis...")
    final_progress = analyze_maslow_progress(needs_system)
    print(f"Final State: {needs_system}")
    print(f"Final Recommendations: {final_progress['recommendations']}")
    
    print(f"\n✅ Enhanced Maslow decision system test completed!")

def demonstrate_growth_progression():
    """Demonstrate how the system progresses through different growth stages"""
    
    print(f"\n🌱 Demonstrating Growth Progression...")
    
    # Create a fresh needs system
    needs_system = MaslowNeedsSystem()
    llm_json_mode = ChatOllama(model="llama3.2:3b-instruct-fp16", temperature=0, format='json')
    action_executor = create_maslow_action_executor(needs_system)
    goal_setter = create_maslow_goal_setter(needs_system)
    
    # Start at survival mode
    needs_system.needs['hunger'].satisfaction = 15.0
    needs_system.needs['thirst'].satisfaction = 20.0
    needs_system.needs['sleep'].satisfaction = 10.0
    needs_system._update_growth_stage()
    
    print(f"Starting at: {needs_system.get_needs_summary()['stage_name']}")
    
    # Stage 1: Survival Mode -> Safety Seeking
    print(f"\n🛡️ Stage 1: Addressing Physiological Needs...")
    physiological_actions = ['eat', 'drink', 'sleep', 'find_shelter']
    
    for action in physiological_actions:
        result = action_executor(action)
        print(f"  {action}: {result['new_stage_name']} (satisfaction: {result['overall_satisfaction']:.1f}%)")
    
    # Stage 2: Safety Seeking -> Social Connection
    print(f"\n👥 Stage 2: Addressing Safety Needs...")
    safety_actions = ['find_safety', 'establish_routine', 'create_order']
    
    for action in safety_actions:
        result = action_executor(action)
        print(f"  {action}: {result['new_stage_name']} (satisfaction: {result['overall_satisfaction']:.1f}%)")
    
    # Stage 3: Social Connection -> Achievement & Recognition
    print(f"\n💕 Stage 3: Addressing Social Needs...")
    social_actions = ['socialize', 'make_friends', 'seek_love', 'join_community']
    
    for action in social_actions:
        result = action_executor(action)
        print(f"  {action}: {result['new_stage_name']} (satisfaction: {result['overall_satisfaction']:.1f}%)")
    
    # Stage 4: Achievement & Recognition -> Self-Actualization
    print(f"\n🏆 Stage 4: Addressing Esteem Needs...")
    esteem_actions = ['work_on_goals', 'build_confidence', 'seek_recognition', 'develop_skills']
    
    for action in esteem_actions:
        result = action_executor(action)
        print(f"  {action}: {result['new_stage_name']} (satisfaction: {result['overall_satisfaction']:.1f}%)")
    
    # Stage 5: Self-Actualization
    print(f"\n🌟 Stage 5: Self-Actualization...")
    actualization_actions = ['learn_new_things', 'be_creative', 'find_purpose', 'explore_meaning']
    
    for action in actualization_actions:
        result = action_executor(action)
        print(f"  {action}: {result['new_stage_name']} (satisfaction: {result['overall_satisfaction']:.1f}%)")
    
    # Show final goals
    final_goals = goal_setter()
    print(f"\n🎯 Final Growth Goals:")
    for goal_type, goals in final_goals.items():
        if goals:
            print(f"  {goal_type}: {len(goals)} goals")
            for goal in goals[:2]:  # Show first 2 goals of each type
                if isinstance(goal, dict):
                    if 'need' in goal:
                        print(f"    - {goal['need']}: {goal['current_level']:.1f} -> {goal['target_level']:.1f}")
                    elif 'goal' in goal:
                        print(f"    - {goal['goal']}")
    
    print(f"\n✅ Growth progression demonstration completed!")

if __name__ == "__main__":
    test_maslow_decision_system()
    demonstrate_growth_progression() 
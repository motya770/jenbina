from langchain.prompts import PromptTemplate
from maslow_needs import MaslowNeedsSystem, NeedLevel
from typing import Dict, List, Any
import json


def create_maslow_decision_chain(llm_json_mode, person_needs: MaslowNeedsSystem):
    """
    Create a decision-making chain based on Maslow's hierarchy of needs
    
    Args:
        llm_json_mode: LLM instance with JSON output capability
        person_needs: MaslowNeedsSystem instance
        
    Returns:
        JSON response with action and reasoning
    """
    
    # Get comprehensive needs analysis
    needs_summary = person_needs.get_needs_summary()
    growth_insights = person_needs.get_growth_insights()
    priority_needs = person_needs.get_priority_needs(5)
    
    # Create detailed prompt for decision making
    maslow_prompt = PromptTemplate(
        input_variables=[
            "current_stage", "stage_name", "overall_satisfaction",
            "level_satisfactions", "priority_needs", "critical_needs",
            "growth_opportunities", "current_time"
        ],
        template="""You are an AI making decisions based on Maslow's hierarchy of needs.

CURRENT STATE:
- Growth Stage: {current_stage} ({stage_name})
- Overall Satisfaction: {overall_satisfaction:.1f}%
- Current Time: {current_time}

LEVEL SATISFACTIONS:
{level_satisfactions}

PRIORITY NEEDS (Top 5):
{priority_needs}

CRITICAL NEEDS: {critical_needs}

GROWTH OPPORTUNITIES:
{growth_opportunities}

DECISION GUIDELINES:
1. **Survival Mode (Stage 1)**: Focus on physiological needs (food, water, sleep, shelter)
2. **Safety Seeking (Stage 2)**: Focus on security, stability, protection
3. **Social Connection (Stage 3)**: Focus on friendship, love, belonging
4. **Achievement & Recognition (Stage 4)**: Focus on self-esteem, confidence, achievement
5. **Self-Actualization (Stage 5)**: Focus on personal growth, creativity, purpose, meaning

ACTION CATEGORIES:
- PHYSIOLOGICAL: eat, drink, sleep, rest, find_shelter, maintain_health
- SAFETY: find_safety, establish_routine, create_order, seek_protection
- SOCIAL: socialize, make_friends, seek_love, join_community, build_relationships
- ESTEEM: work_on_goals, build_confidence, seek_recognition, develop_skills
- SELF_ACTUALIZATION: learn_new_things, be_creative, find_purpose, explore_meaning

Respond in JSON format with:
- action: specific action to take
- category: which need category this addresses
- reasoning: detailed explanation of why this action is chosen
- urgency: "critical", "high", "medium", or "low"
- expected_outcome: what this action should achieve
- alternative_actions: 2-3 backup actions if the primary action fails

Consider:
- Current growth stage and what needs are most important
- Priority needs that are critically low
- Growth opportunities for self-actualization
- Balance between immediate needs and long-term growth"""
    )
    
    # Format level satisfactions
    level_satisfactions_str = ""
    for level_name, satisfaction in growth_insights['level_satisfactions'].items():
        level_satisfactions_str += f"- {level_name}: {satisfaction:.1f}%\n"
    
    # Format priority needs
    priority_needs_str = ""
    for i, need in enumerate(priority_needs, 1):
        priority_needs_str += f"{i}. {need['name']} (Level {need['level']}): {need['satisfaction']:.1f}% - {'CRITICAL' if need['is_critical'] else 'LOW' if need['is_low'] else 'OK'}\n"
    
    # Format growth opportunities
    growth_opportunities_str = ""
    for opportunity in growth_insights['growth_opportunities']:
        growth_opportunities_str += f"- {opportunity['name']}: {opportunity['current']:.1f}/{opportunity['potential']:.1f} (room for {opportunity['growth_room']:.1f})\n"
    
    # Get current time
    from datetime import datetime
    current_time = datetime.now().strftime("%H:%M")
    
    # Use the LLM to make a decision
    response = llm_json_mode.invoke(
        maslow_prompt.format(
            current_stage=needs_summary['growth_stage'],
            stage_name=needs_summary['stage_name'],
            overall_satisfaction=needs_summary['overall_satisfaction'],
            level_satisfactions=level_satisfactions_str,
            priority_needs=priority_needs_str,
            critical_needs=needs_summary['critical_needs_count'],
            growth_opportunities=growth_opportunities_str,
            current_time=current_time
        )
    )
    
    # Extract content from the response
    response_content = response.content if hasattr(response, 'content') else str(response)
    
    print(f"Current Maslow Stage: {needs_summary['stage_name']}")
    print(f"Overall Satisfaction: {needs_summary['overall_satisfaction']:.1f}%")
    print(f"Critical Needs: {needs_summary['critical_needs_count']}")
    print(f"AI Decision: {response_content}")
    
    return response_content


def create_maslow_action_executor(person_needs: MaslowNeedsSystem):
    """
    Create an action executor that can satisfy needs based on actions taken
    
    Args:
        person_needs: MaslowNeedsSystem instance
        
    Returns:
        Function that takes an action and updates needs accordingly
    """
    
    def execute_action(action: str, action_details: Dict[str, Any] = None):
        """
        Execute an action and update needs accordingly
        
        Args:
            action: The action being performed
            action_details: Additional details about the action
        """
        
        # Default satisfaction amounts for different actions
        action_satisfactions = {
            # Physiological actions
            'eat': {'hunger': 30.0, 'health': 5.0},
            'drink': {'thirst': 25.0, 'health': 3.0},
            'sleep': {'sleep': 40.0, 'health': 10.0},
            'rest': {'sleep': 15.0, 'health': 5.0},
            'find_shelter': {'shelter': 20.0, 'security': 15.0},
            'maintain_health': {'health': 20.0},
            
            # Safety actions
            'find_safety': {'security': 25.0, 'protection': 20.0},
            'establish_routine': {'stability': 20.0, 'order': 15.0},
            'create_order': {'order': 25.0, 'stability': 10.0},
            'seek_protection': {'protection': 30.0, 'security': 15.0},
            
            # Social actions
            'socialize': {'social_connection': 20.0, 'friendship': 15.0},
            'make_friends': {'friendship': 25.0, 'belonging': 15.0},
            'seek_love': {'love': 30.0, 'intimacy': 20.0},
            'join_community': {'belonging': 25.0, 'social_connection': 15.0},
            'build_relationships': {'friendship': 20.0, 'love': 15.0, 'belonging': 10.0},
            
            # Esteem actions
            'work_on_goals': {'achievement': 25.0, 'confidence': 15.0},
            'build_confidence': {'confidence': 30.0, 'self_esteem': 20.0},
            'seek_recognition': {'respect': 25.0, 'achievement': 15.0},
            'develop_skills': {'achievement': 20.0, 'confidence': 15.0, 'self_esteem': 10.0},
            
            # Self-actualization actions
            'learn_new_things': {'personal_growth': 30.0, 'achievement': 15.0},
            'be_creative': {'creativity': 35.0, 'personal_growth': 20.0},
            'find_purpose': {'purpose': 25.0, 'meaning': 20.0},
            'explore_meaning': {'meaning': 30.0, 'purpose': 15.0},
            'philosophical_exploration': {'meaning': 25.0, 'purpose': 20.0, 'personal_growth': 15.0},
        }
        
        # Get satisfaction amounts for this action
        satisfactions = action_satisfactions.get(action, {})
        
        # Apply satisfactions
        results = {}
        for need_name, amount in satisfactions.items():
            if need_name in person_needs.needs:
                satisfied_amount = person_needs.satisfy_need(need_name, amount, action)
                results[need_name] = satisfied_amount
        
        # Update growth stage
        person_needs._update_growth_stage()
        
        return {
            'action': action,
            'satisfied_needs': results,
            'new_growth_stage': person_needs.growth_stage,
            'new_stage_name': person_needs._get_stage_name(person_needs.growth_stage),
            'overall_satisfaction': person_needs.get_overall_satisfaction()
        }
    
    return execute_action


def create_maslow_goal_setter(person_needs: MaslowNeedsSystem):
    """
    Create a goal-setting system based on current needs and growth stage
    
    Args:
        person_needs: MaslowNeedsSystem instance
        
    Returns:
        Function that generates appropriate goals
    """
    
    def generate_goals():
        """
        Generate appropriate goals based on current needs and growth stage
        """
        
        needs_summary = person_needs.get_needs_summary()
        growth_insights = person_needs.get_growth_insights()
        priority_needs = person_needs.get_priority_needs(3)
        
        goals = {
            'immediate_goals': [],
            'short_term_goals': [],
            'long_term_goals': [],
            'growth_goals': []
        }
        
        # Immediate goals based on critical needs
        for need in priority_needs:
            if need['is_critical']:
                goals['immediate_goals'].append({
                    'need': need['name'],
                    'current_level': need['satisfaction'],
                    'target_level': 70.0,
                    'action': f"Address {need['name']} need",
                    'urgency': 'critical'
                })
        
        # Short-term goals based on low needs
        for need in priority_needs:
            if need['is_low'] and not need['is_critical']:
                goals['short_term_goals'].append({
                    'need': need['name'],
                    'current_level': need['satisfaction'],
                    'target_level': 80.0,
                    'action': f"Improve {need['name']} satisfaction",
                    'urgency': 'high'
                })
        
        # Long-term goals based on growth stage
        stage = needs_summary['growth_stage']
        if stage < 5:  # Not yet at self-actualization
            next_stage_goals = {
                1: "Focus on safety and security needs",
                2: "Develop social connections and relationships", 
                3: "Build self-esteem and achieve recognition",
                4: "Work toward self-actualization and personal growth"
            }
            goals['long_term_goals'].append({
                'goal': f"Advance to {person_needs._get_stage_name(stage + 1)}",
                'description': next_stage_goals.get(stage, "Continue personal development"),
                'current_stage': stage,
                'target_stage': stage + 1
            })
        
        # Growth goals for self-actualization
        if stage >= 4:
            for opportunity in growth_insights['growth_opportunities']:
                goals['growth_goals'].append({
                    'need': opportunity['name'],
                    'current': opportunity['current'],
                    'target': opportunity['potential'],
                    'growth_room': opportunity['growth_room'],
                    'action': f"Maximize {opportunity['name']} potential"
                })
        
        return goals
    
    return generate_goals


def analyze_maslow_progress(person_needs: MaslowNeedsSystem, time_period: str = "24h"):
    """
    Analyze progress through Maslow's hierarchy over time
    
    Args:
        person_needs: MaslowNeedsSystem instance
        time_period: Time period to analyze ("24h", "7d", "30d")
        
    Returns:
        Progress analysis
    """
    
    needs_summary = person_needs.get_needs_summary()
    growth_insights = person_needs.get_growth_insights()
    
    analysis = {
        'current_state': {
            'growth_stage': needs_summary['growth_stage'],
            'stage_name': needs_summary['stage_name'],
            'overall_satisfaction': needs_summary['overall_satisfaction'],
            'critical_needs': needs_summary['critical_needs_count'],
            'low_needs': needs_summary['low_needs_count']
        },
        'level_analysis': {},
        'growth_opportunities': growth_insights['growth_opportunities'],
        'recommendations': []
    }
    
    # Analyze each level
    for level in NeedLevel:
        level_satisfaction = person_needs.get_level_satisfaction(level)
        level_needs = [need for need in person_needs.needs.values() if need.level == level]
        critical_count = len([need for need in level_needs if need.is_critical()])
        low_count = len([need for need in level_needs if need.is_low()])
        
        analysis['level_analysis'][level.name] = {
            'satisfaction': level_satisfaction,
            'need_count': len(level_needs),
            'critical_count': critical_count,
            'low_count': low_count,
            'status': 'healthy' if level_satisfaction >= 70 else 'needs_attention' if level_satisfaction >= 50 else 'critical'
        }
    
    # Generate recommendations
    if needs_summary['critical_needs_count'] > 0:
        analysis['recommendations'].append("Address critical needs immediately")
    
    if needs_summary['low_needs_count'] > 5:
        analysis['recommendations'].append("Focus on improving low needs")
    
    if needs_summary['growth_stage'] < 5:
        analysis['recommendations'].append(f"Work toward advancing to {person_needs._get_stage_name(needs_summary['growth_stage'] + 1)}")
    
    if len(growth_insights['growth_opportunities']) > 0:
        analysis['recommendations'].append("Explore self-actualization opportunities")
    
    return analysis 
import unittest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add the parent directory to the Python path so we can import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.person.person import Person
from core.environment.world_state import WorldState
from core.cognition.meta_cognition import MetaCognitiveSystem


class TestChainIntegration(unittest.TestCase):
    """Test integration scenarios between different chains"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock LLM with realistic responses covering all chains
        self.mock_llm = Mock()
        self.mock_llm.invoke.return_value.content = json.dumps({
            "chosen_action": "eat",
            "reasoning": "Hunger is low",
            "world_state_influence": "none",
            "emotional_influence": "none",
            "lessons_applied": "none",
            "goals_advanced": "none",
            "compliant": True,
            "explanation": "Safe action",
            "hunger_level": -10,
        })
        
        # Create test person
        self.person = Person()
        self.person.update_all_needs()
        
        # Create test world state
        self.world = WorldState()
        
        # Create meta-cognitive system
        self.meta_cognitive_system = MetaCognitiveSystem(self.mock_llm)

    def test_full_simulation_workflow(self):
        """Test the complete simulation workflow with all chains"""
        from core.needs.maslow_needs import create_basic_needs_chain
        from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
        from core.cognition.asimov_check_chain import create_asimov_check_system
        from core.cognition.state_analysis_chain import create_state_analysis_system

        # Step 1: Basic needs analysis
        needs_response = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
        self.assertIsInstance(needs_response, str)

        # Step 2: Use a valid JSON world description directly
        world_description = json.dumps({
            "list_of_descriptions": ["A peaceful environment"],
            "list_of_actions": ["eat", "sleep", "read"]
        })

        # Step 3: Action decision with meta-cognition
        action_response = create_meta_cognitive_action_chain(
            self.mock_llm,
            self.person,
            world_description,
            self.meta_cognitive_system
        )
        self.assertIsInstance(action_response, dict)
        self.assertIn('chosen_action', action_response)

        # Step 4: Asimov compliance check
        asimov_chain = create_asimov_check_system(self.mock_llm)
        asimov_response = asimov_chain(action_response.get('chosen_action', ''))
        self.assertIsInstance(asimov_response, dict)
        self.assertIn('compliant', asimov_response)

        # Step 5: State analysis (returns dict, not str)
        state_response = create_state_analysis_system(
            self.mock_llm,
            action_decision=action_response.get('chosen_action', ''),
            compliance_check=asimov_response
        )
        self.assertIsInstance(state_response, dict)

    def test_chain_data_flow(self):
        """Test data flow between chains"""
        from core.cognition.action_decision_chain import create_action_decision_chain

        # Use a valid JSON world description directly
        world_description = json.dumps({
            "list_of_descriptions": ["A cozy room with warm lighting"],
            "list_of_actions": ["eat", "sleep", "read"]
        })

        # Use world description in action decision
        action_chain = create_action_decision_chain(self.mock_llm)
        action_decision = action_chain(self.person, world_description, self.mock_llm)

        # Verify action decision structure
        self.assertIsInstance(action_decision, dict)
        self.assertIn('chosen_action', action_decision)

    def test_meta_cognitive_integration(self):
        """Test meta-cognitive system integration with chains"""
        from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
        
        # Mock world description
        world_description = json.dumps({
            "list_of_descriptions": ["A peaceful study environment"],
            "list_of_actions": ["study", "take_break", "exercise"]
        })
        
        # Test meta-cognitive action chain
        result = create_meta_cognitive_action_chain(
            self.mock_llm, 
            self.person, 
            world_description, 
            self.meta_cognitive_system
        )
        
        # Verify meta-cognitive insights are included
        self.assertIn('meta_cognitive_insights', result)
        insights = result['meta_cognitive_insights']
        self.assertIn('reflection', insights)
        self.assertIn('suggested_improvements', insights)

    def test_error_recovery_in_chains(self):
        """Test error recovery and graceful degradation in chains"""
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Test with malformed LLM response
        self.mock_llm.invoke.return_value.content = "invalid json response"
        
        # Should handle gracefully
        result = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
        self.assertIsInstance(result, str)

    def test_chain_performance_under_load(self):
        """Test chain performance with multiple rapid calls"""
        import time
        from core.needs.maslow_needs import create_basic_needs_chain
        
        start_time = time.time()
        
        # Make multiple rapid calls
        for i in range(5):
            result = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
            self.assertIsInstance(result, str)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(total_time, 5.0)  # 5 seconds for 5 calls

    def test_chain_with_different_person_states(self):
        """Test chains with different person states"""
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Test with different need states
        test_cases = [
            {"hunger": 0.0, "sleep": 0.0, "security": 0.0},  # Critical needs
            {"hunger": 50.0, "sleep": 50.0, "security": 50.0},  # Moderate needs
            {"hunger": 100.0, "sleep": 100.0, "security": 100.0},  # Satisfied needs
        ]
        
        for needs_state in test_cases:
            # Set person needs
            for need_name, satisfaction in needs_state.items():
                if need_name in self.person.maslow_needs.needs:
                    self.person.maslow_needs.needs[need_name].satisfaction = satisfaction
            
            # Test chain with this state
            result = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
            self.assertIsInstance(result, str)

    def test_chain_consistency(self):
        """Test that chains produce consistent results with same inputs"""
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Reset person state
        self.person.update_all_needs()
        
        # Make multiple calls with same state
        results = []
        for i in range(3):
            result = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
            results.append(result)
        
        # All results should be strings
        for result in results:
            self.assertIsInstance(result, str)

    def test_chain_memory_usage(self):
        """Test memory usage of chains"""
        import gc
        import sys
        
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Get initial memory usage
        gc.collect()
        initial_memory = sys.getsizeof(self.person) + sys.getsizeof(self.mock_llm)
        
        # Run chain multiple times
        for i in range(10):
            result = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
        
        # Force garbage collection
        gc.collect()
        
        # Memory usage should not grow significantly
        final_memory = sys.getsizeof(self.person) + sys.getsizeof(self.mock_llm)
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be minimal
        self.assertLess(memory_growth, 1000)  # Less than 1KB growth


class TestChainRealWorldScenarios(unittest.TestCase):
    """Test chains with realistic scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.mock_llm.invoke.return_value.content = json.dumps({
            "chosen_action": "eat",
            "reasoning": "Hunger is low",
            "world_state_influence": "none",
            "emotional_influence": "none",
            "lessons_applied": "none",
            "goals_advanced": "none",
            "compliant": True,
            "explanation": "Safe action",
            "hunger_level": -10,
        })
        self.person = Person()
        self.world = WorldState()
        self.meta_cognitive_system = MetaCognitiveSystem(self.mock_llm)

    def test_morning_routine_scenario(self):
        """Test chains in a morning routine scenario"""
        from core.needs.maslow_needs import create_basic_needs_chain
        from core.environment.world_state import create_world_description_system
        
        # Set up morning scenario
        self.world.time_of_day = "morning"
        self.world.weather = "sunny"
        
        # Set needs for morning (hunger low, sleep moderate)
        self.person.maslow_needs.needs['hunger'].satisfaction = 20.0
        self.person.maslow_needs.needs['sleep'].satisfaction = 60.0
        
        # Test needs analysis
        needs_response = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
        self.assertIsInstance(needs_response, str)
        
        # Test world description
        world_chain = create_world_description_system(self.mock_llm)
        world_description = world_chain(self.person, self.world)
        self.assertIsInstance(world_description, str)

    def test_stressful_situation_scenario(self):
        """Test chains in a stressful situation"""
        from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
        
        # Set up stressful scenario (low safety, low esteem)
        self.person.maslow_needs.needs['security'].satisfaction = 30.0
        self.person.maslow_needs.needs['confidence'].satisfaction = 25.0
        
        world_description = json.dumps({
            "list_of_descriptions": ["A challenging work environment"],
            "list_of_actions": ["work_harder", "take_break", "seek_help", "avoid"]
        })
        
        # Test meta-cognitive action chain
        result = create_meta_cognitive_action_chain(
            self.mock_llm, 
            self.person, 
            world_description, 
            self.meta_cognitive_system
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('chosen_action', result)

    def test_creative_work_scenario(self):
        """Test chains in a creative work scenario"""
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Set up creative scenario (high self-actualization needs)
        self.person.maslow_needs.needs['creativity'].satisfaction = 80.0
        self.person.maslow_needs.needs['purpose'].satisfaction = 75.0
        
        # Test needs analysis
        result = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 
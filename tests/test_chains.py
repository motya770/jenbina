import unittest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add the parent directory to the Python path so we can import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.needs.maslow_needs import MaslowNeedsSystem, BasicNeeds
from core.person.person import Person
from core.environment.world_state import WorldState
from core.cognition.meta_cognition import MetaCognitiveSystem
from langchain_ollama import ChatOllama


class TestChains(unittest.TestCase):
    """Test cases for all chain functions in the Jenbina system"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock LLM for testing — returns realistic JSON for each chain
        self.mock_llm = Mock()
        self._set_mock_response({
            "chosen_action": "eat",
            "reasoning": "Hunger is low",
            "world_state_influence": "none",
            "emotional_influence": "none",
            "lessons_applied": "none",
            "goals_advanced": "none",
            "compliant": True,
            "explanation": "Safe action",
            "hunger_level": -10,
            "response": "test response"
        })

        # Create test person with needs
        self.person = Person()
        self.person.update_all_needs()

        # Create test world state
        self.world = WorldState()

        # Create meta-cognitive system
        self.meta_cognitive_system = MetaCognitiveSystem(self.mock_llm)

    def _set_mock_response(self, response_dict):
        """Helper to set mock LLM response"""
        self.mock_llm.invoke.return_value.content = json.dumps(response_dict)

    def test_create_basic_needs_chain(self):
        """Test the basic needs chain creation and execution"""
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Test with BasicNeeds object
        basic_needs = BasicNeeds()
        result = create_basic_needs_chain(self.mock_llm, basic_needs)
        
        # Verify the function was called
        self.mock_llm.invoke.assert_called()
        self.assertIsInstance(result, str)

    def test_create_world_description_system(self):
        """Test the world description system chain"""
        from core.environment.world_state import create_world_description_system
        
        # Create the chain
        world_chain = create_world_description_system(self.mock_llm)
        
        # Test execution
        result = world_chain(self.person, self.world)
        
        # Verify the function was called
        self.mock_llm.invoke.assert_called()
        self.assertIsInstance(result, str)

    def test_create_action_decision_chain(self):
        """Test the action decision chain"""
        from core.cognition.action_decision_chain import create_action_decision_chain
        
        # Mock world description
        world_description = json.dumps({
            "list_of_descriptions": ["A cozy room with warm lighting"],
            "list_of_actions": ["eat", "sleep", "read"]
        })
        
        # Create the chain
        action_chain = create_action_decision_chain(self.mock_llm)
        
        # Test execution
        result = action_chain(self.person, world_description, self.mock_llm)
        
        # Verify the function was called
        self.mock_llm.invoke.assert_called()
        self.assertIsInstance(result, dict)
        self.assertIn('chosen_action', result)

    def test_create_meta_cognitive_action_chain(self):
        """Test the enhanced meta-cognitive action chain"""
        from core.cognition.enhanced_action_decision_chain import create_meta_cognitive_action_chain
        
        # Mock world description
        world_description = json.dumps({
            "list_of_descriptions": ["A peaceful environment"],
            "list_of_actions": ["meditate", "exercise", "work"]
        })
        
        # Test execution
        result = create_meta_cognitive_action_chain(
            self.mock_llm, 
            self.person, 
            world_description, 
            self.meta_cognitive_system
        )
        
        # Verify the result structure
        self.assertIsInstance(result, dict)
        self.assertIn('chosen_action', result)
        self.assertIn('meta_cognitive_insights', result)

    def test_create_asimov_check_system(self):
        """Test the Asimov compliance check system"""
        from core.cognition.asimov_check_chain import create_asimov_check_system
        
        # Create the chain
        asimov_chain = create_asimov_check_system(self.mock_llm)
        
        # Test with a safe action
        safe_action = "Read a book"
        result = asimov_chain(safe_action)
        
        # Verify the function was called
        self.mock_llm.invoke.assert_called()
        self.assertIsInstance(result, dict)
        self.assertIn('compliant', result)

    def test_create_state_analysis_system(self):
        """Test the state analysis system"""
        from core.cognition.state_analysis_chain import create_state_analysis_system

        # Test execution
        action_decision = "Eat a healthy meal"
        compliance_check = {"compliant": True, "explanation": "Safe action"}

        result = create_state_analysis_system(
            self.mock_llm,
            action_decision=action_decision,
            compliance_check=compliance_check
        )

        # Verify the function was called
        self.mock_llm.invoke.assert_called()
        # create_state_analysis_system returns parsed JSON dict (or None)
        self.assertIsInstance(result, dict)

    def test_maslow_decision_chain(self):
        """Test the Maslow decision chain"""
        from core.needs.maslow_decision_chain import create_maslow_decision_chain

        # create_maslow_decision_chain invokes the LLM directly and returns
        # the response content string
        result = create_maslow_decision_chain(self.mock_llm, self.person.maslow_needs)

        # Verify the function was called
        self.mock_llm.invoke.assert_called()
        self.assertIsInstance(result, str)

    def test_chain_integration(self):
        """Test integration between multiple chains"""
        from core.cognition.action_decision_chain import create_action_decision_chain
        from core.cognition.asimov_check_chain import create_asimov_check_system

        # Use a valid JSON world description directly (world_chain returns
        # the raw LLM content which isn't guaranteed to be parseable JSON)
        world_description = json.dumps({
            "list_of_descriptions": ["A cozy room"],
            "list_of_actions": ["eat", "sleep"]
        })

        # Make action decision
        action_chain = create_action_decision_chain(self.mock_llm)
        action_decision = action_chain(self.person, world_description, self.mock_llm)

        # Check Asimov compliance
        asimov_chain = create_asimov_check_system(self.mock_llm)
        compliance = asimov_chain(action_decision.get('chosen_action', ''))

        # Verify all chains executed
        self.assertIsInstance(action_decision, dict)
        self.assertIn('chosen_action', action_decision)
        self.assertIsInstance(compliance, dict)
        self.assertIn('compliant', compliance)

    def test_error_handling(self):
        """Test error handling in chains"""
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Test with invalid LLM
        with self.assertRaises(Exception):
            create_basic_needs_chain(None, BasicNeeds())

    def test_chain_with_real_llm(self):
        """Test chains with a real LLM (if available)"""
        try:
            # Try to create a real LLM
            real_llm = ChatOllama(model='llama3.2:3b-instruct-fp16', temperature=0)
            
            from core.needs.maslow_needs import create_basic_needs_chain
            
            # Test with real LLM
            basic_needs = BasicNeeds()
            result = create_basic_needs_chain(real_llm, basic_needs)
            
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            
        except Exception as e:
            # Skip if real LLM is not available
            self.skipTest(f"Real LLM not available: {e}")

    def test_chain_performance(self):
        """Test chain performance and response times"""
        import time
        
        from core.needs.maslow_needs import create_basic_needs_chain
        
        start_time = time.time()
        basic_needs = BasicNeeds()
        result = create_basic_needs_chain(self.mock_llm, basic_needs)
        end_time = time.time()
        
        # Verify reasonable response time (should be fast with mock)
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0)  # Should be under 1 second with mock
        self.assertIsInstance(result, str)

    def test_chain_data_validation(self):
        """Test data validation in chains"""
        from core.cognition.action_decision_chain import create_action_decision_chain
        
        # Test with invalid world description
        invalid_world_description = "invalid json"
        
        action_chain = create_action_decision_chain(self.mock_llm)
        
        # Should handle invalid JSON gracefully
        with self.assertRaises(json.JSONDecodeError):
            action_chain(self.person, invalid_world_description, self.mock_llm)


class TestChainEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions for chains"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.mock_llm.invoke.return_value.content = '{"response": "test response"}'
        self.person = Person()
        self.world = WorldState()

    def test_empty_needs(self):
        """Test chains with empty or minimal needs"""
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Create person with minimal needs
        person = Person()
        # Reset needs to minimum
        for need in person.maslow_needs.needs.values():
            need.satisfaction = 0.0
        
        result = create_basic_needs_chain(self.mock_llm, person.maslow_needs)
        self.assertIsInstance(result, str)

    def test_extreme_needs(self):
        """Test chains with extreme need values"""
        from core.needs.maslow_needs import create_basic_needs_chain
        
        # Set needs to extreme values
        for need in self.person.maslow_needs.needs.values():
            need.satisfaction = 100.0  # Maximum satisfaction
        
        result = create_basic_needs_chain(self.mock_llm, self.person.maslow_needs)
        self.assertIsInstance(result, str)

    def test_large_world_description(self):
        """Test chains with very large world descriptions"""
        from core.cognition.action_decision_chain import create_action_decision_chain
        
        # Create large world description
        large_description = json.dumps({
            "list_of_descriptions": ["A very detailed description " * 100],
            "list_of_actions": ["action1", "action2", "action3"] * 50
        })
        
        action_chain = create_action_decision_chain(self.mock_llm)
        result = action_chain(self.person, large_description, self.mock_llm)
        
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 
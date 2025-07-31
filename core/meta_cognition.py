from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.base import BaseLLM

@dataclass
class CognitiveProcess:
    """Represents a single cognitive process/decision"""
    timestamp: datetime
    process_type: str  # "decision", "reasoning", "learning", etc.
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reasoning_chain: List[str]  # Step-by-step reasoning
    confidence: float
    success_metrics: Dict[str, float] = field(default_factory=dict)
    meta_reflection: Optional[str] = None

@dataclass
class MetaCognitiveInsight:
    """Represents insights about cognitive processes"""
    insight_type: str  # "bias_detected", "strategy_improvement", "error_pattern", etc.
    description: str
    confidence: float
    suggested_improvement: str
    created_at: datetime = field(default_factory=datetime.now)

class MetaCognitiveSystem:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.cognitive_history: List[CognitiveProcess] = []
        self.insights: List[MetaCognitiveInsight] = []
        self.cognitive_biases: Dict[str, float] = {
            "confirmation_bias": 0.0,
            "anchoring_bias": 0.0,
            "availability_bias": 0.0,
            "overconfidence": 0.0
        }
        self.thinking_strategies: Dict[str, Dict[str, Any]] = {}
    
    def monitor_cognitive_process(self, process_type: str, input_data: Dict, 
                                output_data: Dict, reasoning_chain: List[str], 
                                confidence: float) -> CognitiveProcess:
        """Monitor and record a cognitive process"""
        process = CognitiveProcess(
            timestamp=datetime.now(),
            process_type=process_type,
            input_data=input_data,
            output_data=output_data,
            reasoning_chain=reasoning_chain,
            confidence=confidence
        )
        
        self.cognitive_history.append(process)
        return process
    
    def reflect_on_process(self, process: CognitiveProcess) -> MetaCognitiveInsight:
        """Reflect on the quality of a cognitive process"""
        reflection_prompt = PromptTemplate(
            input_variables=["process_type", "input_data", "output_data", "reasoning_chain", "confidence"],
            template="""Analyze this cognitive process and identify potential issues or improvements:

Process Type: {process_type}
Input Data: {input_data}
Output Data: {output_data}
Reasoning Chain: {reasoning_chain}
Confidence: {confidence}

Think through this step by step:
1. Was the reasoning logical and complete?
2. Were there any cognitive biases present?
3. Was the confidence level appropriate?
4. Could the reasoning have been improved?
5. What strategies would make this process better?

Respond in JSON format:
{{
    "insight_type": "bias_detected|strategy_improvement|error_pattern|good_reasoning",
    "description": "detailed analysis of the cognitive process",
    "confidence": 0.8,
    "suggested_improvement": "specific suggestion for improvement",
    "bias_detected": "type of bias if any",
    "reasoning_quality": "excellent|good|fair|poor"
}}"""
        )
        
        reflection_chain = LLMChain(llm=self.llm, prompt=reflection_prompt)
        
        try:
            result = reflection_chain.run(
                process_type=process.process_type,
                input_data=json.dumps(process.input_data),
                output_data=json.dumps(process.output_data),
                reasoning_chain="\n".join(process.reasoning_chain),
                confidence=process.confidence
            )
            
            reflection_data = json.loads(result)
            
            insight = MetaCognitiveInsight(
                insight_type=reflection_data["insight_type"],
                description=reflection_data["description"],
                confidence=reflection_data["confidence"],
                suggested_improvement=reflection_data["suggested_improvement"]
            )
            
            self.insights.append(insight)
            
            # Update bias tracking
            if "bias_detected" in reflection_data:
                bias_type = reflection_data["bias_detected"]
                if bias_type in self.cognitive_biases:
                    self.cognitive_biases[bias_type] += 0.1
            
            return insight
            
        except Exception as e:
            print(f"Error in meta-cognitive reflection: {e}")
            return None
    
    def analyze_cognitive_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across multiple cognitive processes"""
        if len(self.cognitive_history) < 3:
            return {"message": "Not enough data for pattern analysis"}
        
        pattern_prompt = PromptTemplate(
            input_variables=["cognitive_history"],
            template="""Analyze these cognitive processes and identify patterns:

Cognitive History:
{cognitive_history}

Look for:
1. Recurring biases or errors
2. Successful reasoning patterns
3. Areas where confidence is often misplaced
4. Strategies that work well
5. Opportunities for improvement

Respond in JSON format:
{{
    "recurring_biases": ["bias1", "bias2"],
    "successful_patterns": ["pattern1", "pattern2"],
    "confidence_issues": "description of confidence problems",
    "improvement_areas": ["area1", "area2"],
    "overall_cognitive_health": "excellent|good|fair|poor"
}}"""
        )
        
        pattern_chain = LLMChain(llm=self.llm, prompt=pattern_prompt)
        
        # Format cognitive history for analysis
        history_text = "\n\n".join([
            f"Process {i+1}: {p.process_type} (confidence: {p.confidence})"
            for i, p in enumerate(self.cognitive_history[-10:])  # Last 10 processes
        ])
        
        try:
            result = pattern_chain.run(cognitive_history=history_text)
            return json.loads(result)
        except Exception as e:
            return {"error": f"Pattern analysis failed: {e}"}
    
    def suggest_thinking_strategy(self, current_situation: Dict) -> Dict[str, Any]:
        """Suggest thinking strategies based on meta-cognitive insights"""
        strategy_prompt = PromptTemplate(
            input_variables=["current_situation", "cognitive_biases", "insights"],
            template="""Based on meta-cognitive insights, suggest thinking strategies for this situation:

Current Situation: {current_situation}
Known Cognitive Biases: {cognitive_biases}
Recent Insights: {insights}

Suggest specific strategies to:
1. Avoid known biases
2. Improve reasoning quality
3. Calibrate confidence appropriately
4. Enhance decision-making

Respond in JSON format:
{{
    "strategies": ["strategy1", "strategy2"],
    "bias_mitigation": "how to avoid biases",
    "reasoning_approach": "suggested reasoning method",
    "confidence_calibration": "how to assess confidence"
}}"""
        )
        
        strategy_chain = LLMChain(llm=self.llm, prompt=strategy_prompt)
        
        # Format insights for display
        insights_text = "\n".join([
            f"- {insight.insight_type}: {insight.description}"
            for insight in self.insights[-5:]  # Last 5 insights
        ])
        
        try:
            result = strategy_chain.run(
                current_situation=json.dumps(current_situation),
                cognitive_biases=json.dumps(self.cognitive_biases),
                insights=insights_text
            )
            return json.loads(result)
        except Exception as e:
            return {"error": f"Strategy suggestion failed: {e}"}
    
    def get_meta_cognitive_stats(self) -> Dict[str, Any]:
        """Get statistics about meta-cognitive performance"""
        return {
            "total_processes": len(self.cognitive_history),
            "total_insights": len(self.insights),
            "cognitive_biases": self.cognitive_biases,
            "recent_insights": [
                {
                    "type": insight.insight_type,
                    "description": insight.description,
                    "confidence": insight.confidence
                }
                for insight in self.insights[-3:]  # Last 3 insights
            ]
        }
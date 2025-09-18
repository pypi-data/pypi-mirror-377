"""Pythonic models for AgentLab SDK.

This module provides more pythonic wrapper classes for the protobuf-generated models,
making them easier to work with, serialize, and print.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum


class EvaluationState(Enum):
    """State of an evaluation run."""
    UNSPECIFIED = "STATE_UNSPECIFIED"
    PENDING = "PENDING" 
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class EvaluatorResultState(Enum):
    """State of an individual evaluator result."""
    UNSPECIFIED = "STATE_UNSPECIFIED"
    PENDING = "PENDING"
    RUNNING = "RUNNING" 
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@dataclass
class EvaluatorResult:
    """Result from a single evaluator."""
    evaluator_name: str
    output: str
    state: EvaluatorResultState
    error_message: Optional[str] = None
    _evaluation_run: Optional['EvaluationRun'] = None  # Reference to parent evaluation run
    
    @property
    def parsed_output(self) -> Dict[str, Any]:
        """Parse the output JSON if possible, otherwise return raw output in a dict."""
        try:
            return json.loads(self.output)
        except (json.JSONDecodeError, TypeError):
            return {"raw": self.output}
    
    @property
    def is_successful(self) -> bool:
        """Check if the evaluator completed successfully."""
        return self.state == EvaluatorResultState.SUCCEEDED
    
    @property
    def score(self) -> Optional[float]:
        """Get the score for this evaluator from the evaluation run metadata."""
        if self._evaluation_run is None:
            # Try to extract score from parsed output as fallback
            parsed = self.parsed_output
            if isinstance(parsed, dict) and "score" in parsed:
                try:
                    return float(parsed["score"])
                except (ValueError, TypeError):
                    pass
            return None
        
        # Look for score in metadata using evaluator name as key
        metadata = self._evaluation_run.metadata
        if self.evaluator_name in metadata:
            score_val = metadata[self.evaluator_name]
            if isinstance(score_val, (int, float)):
                return float(score_val)
        
        # Also try to extract from parsed output
        parsed = self.parsed_output
        if isinstance(parsed, dict) and "score" in parsed:
            try:
                return float(parsed["score"])
            except (ValueError, TypeError):
                pass
        
        return None
    
    def __repr__(self) -> str:
        score = self.score
        return (f"EvaluatorResult(evaluator='{self.evaluator_name}', "
                f"state={self.state.value}, score={score})")


@dataclass  
class EvaluationRun:
    """A complete evaluation run with results from multiple evaluators."""
    name: str
    state: EvaluationState
    evaluator_names: List[str]
    user_question: str
    agent_answer: str
    ground_truth: str
    instructions: str
    evaluator_results: Dict[str, EvaluatorResult]
    agent_name: str
    agent_version: str
    evaluation_hash: str
    metadata: Dict[str, Union[str, int, bool, float]] = field(default_factory=dict)
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Set up back-references from evaluator results to this evaluation run."""
        for result in self.evaluator_results.values():
            result._evaluation_run = self
    
    
    @property
    def is_successful(self) -> bool:
        """Check if the evaluation completed successfully."""
        return self.state == EvaluationState.SUCCEEDED
    
    
    def get_evaluator_result(self, evaluator_name: str) -> Optional[EvaluatorResult]:
        """Get result for a specific evaluator."""
        return self.evaluator_results.get(evaluator_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for JSON serialization."""
        return {
            "name": self.name,
            "state": self.state.value,
            "evaluator_names": self.evaluator_names,
            "user_question": self.user_question,
            "agent_answer": self.agent_answer,
            "ground_truth": self.ground_truth,
            "instructions": self.instructions,
            "evaluator_results": {
                name: {
                    "evaluator_name": result.evaluator_name,
                    "output": result.parsed_output,
                    "state": result.state.value,
                    "score": result.score,
                    "error_message": result.error_message,
                    "is_successful": result.is_successful
                }
                for name, result in self.evaluator_results.items()
            },
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "evaluation_hash": self.evaluation_hash,
            "metadata": self.metadata,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
            "is_successful": self.is_successful,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return (f"EvaluationRun(name='{self.name}', state={self.state.value}, "
                f"evaluators={len(self.evaluator_results)}")
    
    def __str__(self) -> str:
        """Provide a nice string representation for printing."""
        lines = [
            f"🧪 Evaluation: {self.name}",
            f"📊 State: {self.state.value}",
            f"🤖 Agent: {self.agent_name} v{self.agent_version}",
            f"❓ Question: {self.user_question}",
            f"💬 Answer: {self.agent_answer}",
            f"✅ Ground Truth: {self.ground_truth}",
        ]
        
        lines.append("\n📋 Evaluator Results:")
        for name, result in self.evaluator_results.items():
            status_emoji = "✅" if result.is_successful else "❌"
            lines.append(f"  {status_emoji} {result.evaluator_name}: "
                        f"{result.state.value} (score: {result.score:.3f})")
            
            # Add parsed output if available
            try:
                parsed = result.parsed_output
                if "rationale" in parsed:
                    lines.append(f"    💭 {parsed['rationale']}")
            except Exception:
                pass
        
        if self.create_time:
            lines.append(f"\n🕒 Created: {self.create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)


@dataclass
class Evaluator:
    """An evaluator definition."""
    name: str
    display_name: str
    description: str
    hashed_fields: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name, 
            "description": self.description,
            "hashed_fields": self.hashed_fields
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f"Evaluator(name='{self.name}', display_name='{self.display_name}')"


@dataclass
class ListEvaluatorsResponse:
    """Response containing a list of evaluators."""
    evaluators: List[Evaluator]
    next_page_token: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evaluators": [evaluator.to_dict() for evaluator in self.evaluators],
            "next_page_token": self.next_page_token
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass  
class ListEvaluationRunsResponse:
    """Response containing a list of evaluation runs."""
    evaluation_runs: List[EvaluationRun] 
    next_page_token: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "evaluation_runs": [run.to_dict() for run in self.evaluation_runs],
            "next_page_token": self.next_page_token
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

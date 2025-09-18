"""Converters for transforming protobuf objects to pythonic models.

This module provides functions to convert protobuf-generated objects into
more pythonic wrapper classes that are easier to work with.
"""

from datetime import datetime
from typing import Dict, List, Union, Any

from .models import (
    EvaluationRun, EvaluatorResult, Evaluator, 
    ListEvaluatorsResponse, ListEvaluationRunsResponse,
    EvaluationState, EvaluatorResultState
)


def _parse_timestamp(timestamp_pb) -> datetime:
    """Convert protobuf timestamp to datetime."""
    if timestamp_pb is None:
        return None
    
    try:
        # Protobuf timestamps have seconds and nanos fields
        seconds = getattr(timestamp_pb, 'seconds', 0)
        nanos = getattr(timestamp_pb, 'nanos', 0)
        return datetime.fromtimestamp(seconds + nanos / 1_000_000_000)
    except (AttributeError, TypeError, ValueError):
        return None


def _parse_score_value(score_value_pb) -> Union[str, int, bool, float]:
    """Convert protobuf ScoreValue to Python type."""
    if score_value_pb is None:
        return None
    
    # ScoreValue is a oneof field - check which type it contains
    if hasattr(score_value_pb, 'string_value') and score_value_pb.HasField('string_value'):
        return score_value_pb.string_value
    elif hasattr(score_value_pb, 'int_value') and score_value_pb.HasField('int_value'):
        return score_value_pb.int_value
    elif hasattr(score_value_pb, 'bool_value') and score_value_pb.HasField('bool_value'):
        return score_value_pb.bool_value
    elif hasattr(score_value_pb, 'float_value') and score_value_pb.HasField('float_value'):
        return score_value_pb.float_value
    
    return None


def _parse_enum_state(state_value, enum_class) -> Any:
    """Convert protobuf enum value to our enum."""
    if isinstance(state_value, int):
        # Convert int enum value to string first
        state_names = {
            0: "STATE_UNSPECIFIED",
            1: "PENDING", 
            2: "RUNNING",
            3: "SUCCEEDED",
            4: "FAILED"
        }
        state_str = state_names.get(state_value, "STATE_UNSPECIFIED")
    else:
        state_str = str(state_value)
    
    # Try to find matching enum value
    for enum_val in enum_class:
        if enum_val.value == state_str:
            return enum_val
    
    return enum_class.UNSPECIFIED


def convert_evaluator_result(evaluator_result_pb) -> EvaluatorResult:
    """Convert protobuf EvaluatorResult to pythonic EvaluatorResult."""
    return EvaluatorResult(
        evaluator_name=getattr(evaluator_result_pb, 'evaluator_name', ''),
        output=getattr(evaluator_result_pb, 'output', ''),
        state=_parse_enum_state(getattr(evaluator_result_pb, 'state', 0), EvaluatorResultState),
        error_message=getattr(evaluator_result_pb, 'error_message', None) or None
    )


def convert_evaluation_run(evaluation_run_pb) -> EvaluationRun:
    """Convert protobuf EvaluationRun to pythonic EvaluationRun."""
    
    # Convert evaluator results
    evaluator_results = {}
    evaluator_results_pb = getattr(evaluation_run_pb, 'evaluator_results', {})
    if hasattr(evaluator_results_pb, 'items'):
        for name, result_pb in evaluator_results_pb.items():
            evaluator_results[name] = convert_evaluator_result(result_pb)
    
    # Convert metadata
    metadata = {}
    metadata_pb = getattr(evaluation_run_pb, 'metadata', {})
    if hasattr(metadata_pb, 'items'):
        for key, score_value_pb in metadata_pb.items():
            metadata[key] = _parse_score_value(score_value_pb)
    
    # Convert evaluator names list
    evaluator_names = []
    evaluator_names_pb = getattr(evaluation_run_pb, 'evaluator_names', [])
    if hasattr(evaluator_names_pb, '__iter__'):
        evaluator_names = list(evaluator_names_pb)
    
    return EvaluationRun(
        name=getattr(evaluation_run_pb, 'name', ''),
        state=_parse_enum_state(getattr(evaluation_run_pb, 'state', 0), EvaluationState),
        evaluator_names=evaluator_names,
        user_question=getattr(evaluation_run_pb, 'user_question', ''),
        agent_answer=getattr(evaluation_run_pb, 'agent_answer', ''),
        ground_truth=getattr(evaluation_run_pb, 'ground_truth', ''),
        instructions=getattr(evaluation_run_pb, 'instructions', ''),
        evaluator_results=evaluator_results,
        agent_name=getattr(evaluation_run_pb, 'agent_name', ''),
        agent_version=getattr(evaluation_run_pb, 'agent_version', ''),
        evaluation_hash=getattr(evaluation_run_pb, 'evaluation_hash', ''),
        metadata=metadata,
        create_time=_parse_timestamp(getattr(evaluation_run_pb, 'create_time', None)),
        update_time=_parse_timestamp(getattr(evaluation_run_pb, 'update_time', None))
    )


def convert_evaluator(evaluator_pb) -> Evaluator:
    """Convert protobuf Evaluator to pythonic Evaluator."""
    
    # Convert hashed fields list
    hashed_fields = []
    hashed_fields_pb = getattr(evaluator_pb, 'hashed_fields', [])
    if hasattr(hashed_fields_pb, '__iter__'):
        hashed_fields = list(hashed_fields_pb)
    
    return Evaluator(
        name=getattr(evaluator_pb, 'name', ''),
        display_name=getattr(evaluator_pb, 'display_name', ''),
        description=getattr(evaluator_pb, 'description', ''),
        hashed_fields=hashed_fields
    )


def convert_list_evaluators_response(response_pb) -> ListEvaluatorsResponse:
    """Convert protobuf ListEvaluatorsResponse to pythonic version."""
    
    evaluators = []
    evaluators_pb = getattr(response_pb, 'evaluators', [])
    if hasattr(evaluators_pb, '__iter__'):
        evaluators = [convert_evaluator(evaluator_pb) for evaluator_pb in evaluators_pb]
    
    return ListEvaluatorsResponse(
        evaluators=evaluators,
        next_page_token=getattr(response_pb, 'next_page_token', '')
    )


def convert_list_evaluation_runs_response(response_pb) -> ListEvaluationRunsResponse:
    """Convert protobuf ListEvaluationRunsResponse to pythonic version."""
    
    evaluation_runs = []
    evaluation_runs_pb = getattr(response_pb, 'evaluation_runs', [])
    if hasattr(evaluation_runs_pb, '__iter__'):
        evaluation_runs = [convert_evaluation_run(run_pb) for run_pb in evaluation_runs_pb]
    
    return ListEvaluationRunsResponse(
        evaluation_runs=evaluation_runs,
        next_page_token=getattr(response_pb, 'next_page_token', '')
    )


# Convenience function to convert any supported type
def convert_protobuf_object(pb_object):
    """Automatically convert a protobuf object to its pythonic equivalent."""
    
    # Get the object's type name
    type_name = type(pb_object).__name__
    
    # Map type names to converter functions
    converters = {
        'EvaluationRun': convert_evaluation_run,
        'EvaluatorResult': convert_evaluator_result,
        'Evaluator': convert_evaluator,
        'ListEvaluatorsResponse': convert_list_evaluators_response,
        'ListEvaluationRunsResponse': convert_list_evaluation_runs_response,
    }
    
    converter = converters.get(type_name)
    if converter:
        return converter(pb_object)
    
    # If no specific converter found, return the original object
    return pb_object

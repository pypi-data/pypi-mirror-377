"""AgentLab Python Client for evaluation platform using Connect RPC."""

import urllib3
import os
from typing import Optional, Dict, List, Union, Callable, Awaitable
import json

from .exceptions import AgentLabError, AuthenticationError, APIError
from .converters import (
    convert_evaluation_run, convert_evaluator, convert_list_evaluators_response, 
    convert_list_evaluation_runs_response
)
from proto.agentlab.evaluations.v1.evaluation_pb2_connect import EvaluationServiceClient, AsyncEvaluationServiceClient
from proto.agentlab.evaluations.v1 import evaluation_pb2
from proto.agentlab.iam.v1.iam_service_pb2_connect import IAMServiceClient, AsyncIAMServiceClient
from proto.agentlab.iam.v1 import iam_service_pb2

# Type aliases
TokenGetter = Callable[[], Awaitable[Optional[str]]]


class CreateEvaluationOptions:
    """Options for creating an evaluation."""
    
    def __init__(
        self,
        agent_name: str,
        agent_version: str,
        evaluator_names: List[str],
        user_question: str,
        agent_answer: str,
        project_id: Optional[str] = None,
        ground_truth: Optional[str] = None,
        instructions: Optional[str] = None,
        metadata: Optional[Dict[str, Union[str, int, bool, float]]] = None
    ):
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.evaluator_names = evaluator_names
        self.user_question = user_question
        self.agent_answer = agent_answer
        self.project_id = project_id
        self.ground_truth = ground_truth
        self.instructions = instructions
        self.metadata = metadata or {}


class AgentLabClientOptions:
    """Configuration options for the AgentLab client."""
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        token_getter: Optional[TokenGetter] = None,
        base_url: Optional[str] = None
    ):
        # If api_token is not provided, try to get it from environment variable
        if api_token is None:
            api_token = os.getenv('AGENTLAB_API_TOKEN')
        
        self.api_token = api_token
        self.token_getter = token_getter
        self.base_url = base_url or "https://api.agentlab.vectorlabs.cz"


class AgentLabClient:
    """Main client for interacting with the AgentLab evaluation platform."""
    
    def __init__(self, options: AgentLabClientOptions):
        """Initialize the AgentLab client.
        
        Args:
            options: Configuration options for the client
        """
        self._base_url = options.base_url
        self._get_token = None
        self._auth_context = None
        
        # Set up token getter
        if options.token_getter:
            self._get_token = options.token_getter
        elif options.api_token:
            self._get_token = self._create_static_token_getter(options.api_token)
        
        # Create HTTP client with custom interceptor for authentication
        self._http_client = urllib3.PoolManager()
        
        # Create service clients
        self.evaluations = EvaluationServiceClient(self._base_url, self._http_client)
        self.iam = IAMServiceClient(self._base_url, self._http_client)
    
    def _create_static_token_getter(self, token: str) -> Callable[[], str]:
        """Create a token getter that returns a static token."""
        def get_token():
            return token
        return get_token
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests."""
        headers = {}
        if self._get_token:
            try:
                token = self._get_token()
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                else:
                    print("⚠️  No token available for authenticated request")
            except Exception as error:
                print(f"❌ Failed to get authentication token: {error}")
        else:
            print("⚠️  No token getter provided for request")
        return headers
    
    def _get_auth_context(self):
        """Initialize auth context on client creation (called automatically)."""
        if self._auth_context:
            return self._auth_context
        
        request = iam_service_pb2.GetAuthContextRequest()
        
        try:
            self._auth_context = self.iam.get_auth_context(
                request, 
                extra_headers=self._get_auth_headers()
            )
            return self._auth_context
        except Exception as e:
            raise AuthenticationError(f"Failed to get auth context: {e}")
    
    def _get_project_id(self, project_id: Optional[str] = None) -> str:
        """Get project ID, either from parameter or auto-filled from auth context."""
        if project_id:
            return project_id
        
        # Auto-fill projectId from auth context
        try:
            auth_context = self._get_auth_context()
            auto_project_id = getattr(auth_context, 'project_id', None)
            if auto_project_id:
                return auto_project_id
        except Exception:
            pass  # Fall through to error
        
        raise AgentLabError(
            "project_id is required. Please provide it explicitly or ensure you have access to at least one project."
        )
    
    def run_evaluation(self, options: CreateEvaluationOptions):
        """Create a new evaluation run using multiple evaluators.
        
        Args:
            options: Configuration for the evaluation run
            
        Returns:
            EvaluationRun: The created evaluation run (pythonic model)
            
        Raises:
            AgentLabError: If projectId is not provided and can't be auto-filled
        """
        # Get project ID
        project_id = self._get_project_id(options.project_id)
        
        # Convert metadata to ScoreValue objects
        metadata_entries = {}
        for key, value in options.metadata.items():
            score_value = evaluation_pb2.ScoreValue()
            if isinstance(value, str):
                score_value.string_value = value
            elif isinstance(value, bool):
                score_value.bool_value = value 
            elif isinstance(value, int):
                score_value.int_value = value
            elif isinstance(value, float):
                score_value.float_value = value
            else:
                score_value.string_value = str(value)
            metadata_entries[key] = score_value
        
        # Format evaluator names with full resource paths
        evaluator_names = []
        for name in options.evaluator_names:
            if name.startswith("projects/"):
                evaluator_names.append(name)
            else:
                evaluator_names.append(f"projects/{project_id}/evaluators/{name}")
        
        # Create the request
        request = evaluation_pb2.RunEvaluationRequest(
            parent=f"projects/{project_id}",
            evaluator_names=evaluator_names,
            user_question=options.user_question,
            agent_answer=options.agent_answer,
            ground_truth=options.ground_truth or "",
            instructions=options.instructions or "",
            agent_name=options.agent_name,
            agent_version=options.agent_version,
            metadata=metadata_entries
        )
        
        try:
            response = self.evaluations.run_evaluation(
                request,
                extra_headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_evaluation_run(response)
        except Exception as e:
            raise APIError(f"Failed to run evaluation: {e}")
    
    def get_evaluation_run(self, name: str):
        """Get an evaluation run by its name.
        
        Args:
            name: The name/ID of the evaluation run
            
        Returns:
            EvaluationRun: The evaluation run (pythonic model)
        """
        request = evaluation_pb2.GetEvaluationRunRequest(name=name)
        
        try:
            response = self.evaluations.get_evaluation_run(
                request,
                extra_headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_evaluation_run(response)
        except Exception as e:
            raise APIError(f"Failed to get evaluation run: {e}")
    
    def list_evaluators(self, project_id: Optional[str] = None):
        """List available evaluators for a project.
        
        Args:
            project_id: The project ID (will be auto-filled if not provided)
            
        Returns:
            ListEvaluatorsResponse: The list of evaluators (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        request = evaluation_pb2.ListEvaluatorsRequest(
            parent=f"projects/{resolved_project_id}",
            page_size=50,
            page_token=""
        )
        
        try:
            response = self.evaluations.list_evaluators(
                request,
                extra_headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_list_evaluators_response(response)
        except Exception as e:
            raise APIError(f"Failed to list evaluators: {e}")
    
    def get_evaluator(self, name: str):
        """Get a specific evaluator.
        
        Args:
            name: The name/ID of the evaluator
            
        Returns:
            Evaluator: The evaluator (pythonic model)
        """
        request = evaluation_pb2.GetEvaluatorRequest(name=name)
        
        try:
            response = self.evaluations.get_evaluator(
                request,
                extra_headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_evaluator(response)
        except Exception as e:
            raise APIError(f"Failed to get evaluator: {e}")
    
    def list_evaluation_runs(self, project_id: Optional[str] = None):
        """List evaluation runs for a project.
        
        Args:
            project_id: The project ID (will be auto-filled if not provided)
            
        Returns:
            ListEvaluationRunsResponse: The list of evaluation runs (pythonic model)
        """
        resolved_project_id = self._get_project_id(project_id)
        request = evaluation_pb2.ListEvaluationRunsRequest(
            parent=f"projects/{resolved_project_id}",
            page_size=50,
            page_token="",
            filter=""
        )
        
        try:
            response = self.evaluations.list_evaluation_runs(
                request,
                extra_headers=self._get_auth_headers()
            )
            
            # Always convert to pythonic model
            return convert_list_evaluation_runs_response(response)
        except Exception as e:
            raise APIError(f"Failed to list evaluation runs: {e}")
    
    def get_evaluation_result(self, name: str):
        """Get evaluation result with structured evaluator results.
        
        Args:
            name: The name/ID of the evaluation run
            
        Returns:
            dict: Dictionary containing 'run' and 'results' keys
        """
        run = self.get_evaluation_run(name)
        
        # Parse JSON outputs from evaluator results
        results = {}
        evaluator_results = getattr(run, 'evaluator_results', {})
        
        for evaluator_name, result in evaluator_results.items():
            try:
                output = getattr(result, 'output', '')
                results[evaluator_name] = json.loads(output)
            except (json.JSONDecodeError, AttributeError) as error:
                print(f"Failed to parse output for evaluator {evaluator_name}: {error}")
                results[evaluator_name] = {"raw": getattr(result, 'output', '')}
        
        return {
            "run": run,
            "results": results
        }

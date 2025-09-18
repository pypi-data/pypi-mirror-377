# AgentLab Python Client

[![PyPI version](https://badge.fury.io/py/agentlab-py.svg)](https://badge.fury.io/py/agentlab-py)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for the AgentLab evaluation platform using Connect RPC. This library provides a simple and intuitive interface for running AI agent evaluations, managing evaluators, and accessing evaluation results.

## 🚀 Quick Start

```bash
pip install agentlab-py
```

Set your API token as an environment variable:
```bash
export AGENTLAB_API_TOKEN=your-api-token-here
```

```python
from agentlab import AgentLabClient, AgentLabClientOptions, CreateEvaluationOptions

# Initialize the client (automatically loads AGENTLAB_API_TOKEN), or pass the token via api_token parameter
client = AgentLabClient(AgentLabClientOptions())

# Run an evaluation
evaluation = client.run_evaluation(CreateEvaluationOptions(
    agent_name='my-agent',
    agent_version='1.0.0',
    project_id='your-project-id',
    evaluator_names=['correctness-v1'],
    user_question='What is the capital of France?',
    agent_answer='The capital of France is Paris.',
    ground_truth='Paris is the capital of France',
    metadata={'confidence': 0.95}  # Optional metadata for tracking
))

print(f"Evaluation completed: {evaluation.name}")
```

### Retrieving Results

```python
# Get evaluation run details
evaluation_run = client.get_evaluation_run('evaluation-run-id')

# Get structured results with parsed JSON
result_data = client.get_evaluation_result('evaluation-run-id')
print(result_data['results'])  # Parsed evaluator outputs

# Access raw evaluator results
for evaluator_name, result in evaluation_run.evaluator_results.items():
    print(f"{evaluator_name}: {result.output}")
```

### Listing Evaluation Runs

```python
# List recent evaluation runs
runs_response = client.list_evaluation_runs('project-123')
for run in runs_response.evaluation_runs:
    print(f"Run: {run.name} - Question: {run.user_question}")
```

## 🔧 Development

### Setting up the development environment

```bash
# Clone the repository
git clone https://github.com/VectorLabsCZ/agentlab-py.git
cd agentlab-py

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .
```

### Running Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Async usage example
python examples/async_usage.py
```

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=agentlab

# Run type checking
mypy agentlab/
```

## 📦 Building and Publishing

### Building the package

```bash
# Install build tools
pip install build

# Build the package
python -m build
```

### Publishing to PyPI

```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*
```

## 🌟 Examples

### Complete Evaluation Workflow

```python
import json
from agentlab import AgentLabClient, AgentLabClientOptions, CreateEvaluationOptions

def main():
    # Initialize client
    client = AgentLabClient(AgentLabClientOptions(
        api_token='your-api-token'
    ))
    
    project_id = 'your-project-id'
    
    try:
        # 1. List available evaluators
        print("📋 Available evaluators:")
        evaluators = client.list_evaluators(project_id)
        for evaluator in evaluators.evaluators[:3]:  # Show first 3
            print(f"  - {evaluator.name}: {evaluator.display_name}")
        
        # 2. Run evaluation
        print("\n🚀 Running evaluation...")
        evaluation = client.run_evaluation(CreateEvaluationOptions(
            agent_name='demo-agent',
            agent_version='1.0.0',
            project_id=project_id,
            evaluator_names=['correctness-v1'],
            user_question='What is the square root of 16?',
            agent_answer='The square root of 16 is 4.',
            ground_truth='4',
            metadata={'confidence': 1.0}  # Additional context/scores
        ))
        
        # 3. Get results
        print(f"\n✅ Evaluation completed: {evaluation.name}")
        result_data = client.get_evaluation_result(evaluation.name)
        
        print("\n📊 Results:")
        print(json.dumps(result_data['results'], indent=2))
        
        # 4. List recent runs
        print("\n📈 Recent evaluation runs:")
        runs = client.list_evaluation_runs(project_id)
        for run in runs.evaluation_runs[:3]:  # Show first 3
            print(f"  - {run.name}: {run.user_question[:50]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
```

### Error Handling

```python
from agentlab import AgentLabClient, AgentLabError, AuthenticationError, APIError

try:
    client = AgentLabClient(AgentLabClientOptions(api_token='invalid-token'))
    evaluation = client.run_evaluation(options)
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    
except APIError as e:
    print(f"API error (status {e.status_code}): {e}")
    
except AgentLabError as e:
    print(f"AgentLab error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🆚 Comparison with JavaScript SDK

| Feature | Python | JavaScript |
|---------|--------|------------|
| Installation | `pip install agentlab-py` | `npm install @vectorlabs/agentlab-js` |
| Import | `from agentlab import AgentLabClient` | `const { AgentLabClient } = require('@vectorlabs/agentlab-js')` |
| Async Support | ✅ Built-in support | ✅ Native async/await |
| Type Safety | ✅ Full type hints | ✅ TypeScript definitions |
| Error Handling | ✅ Custom exception classes | ✅ Custom error classes |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Issues and Feature Requests

- 🐛 [Report a bug](https://github.com/VectorLabsCZ/agentlab-py/issues/new?template=bug_report.md)
- 💡 [Request a feature](https://github.com/VectorLabsCZ/agentlab-py/issues/new?template=feature_request.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [AgentLab Platform](https://agentlab.vectorlabs.cz)
- [Documentation](https://docs.agentlab.vectorlabs.cz)
- [JavaScript SDK](https://github.com/VectorLabsCZ/agentlab-js)
- [API Reference](https://api.agentlab.vectorlabs.cz/docs)

## 🏢 About VectorLabs

AgentLab is developed by [VectorLabs](https://vectorlabs.cz), a company focused on advancing AI agent evaluation and development tools.

---

Made with ❤️ by the VectorLabs team


#!/usr/bin/env python3
"""
ADK Book Agent - AgentLab Evaluation Script

This script demonstrates how to evaluate the ADK Book Agent using AgentLab
with realistic agent responses that show actual evaluation results.

Setup:
Set your API token as an environment variable:
export AGENTLAB_API_TOKEN=your-api-token-here
"""

import sys
import os

# Add the parent directory to the path to import agentlab
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from agentlab import AgentLabClient, AgentLabClientOptions, CreateEvaluationOptions


# Realistic agent responses that simulate actual book agent behavior
REALISTIC_RESPONSES = {
    "hitchhiker_search": """📚 The Hitchhiker's Guide to the Galaxy is a comedic science fiction novel by Douglas Adams, published in 1979. It follows Arthur Dent's adventures through space after Earth is destroyed to make way for a hyperspace bypass.

The book is famous for introducing the number 42 as 'the answer to the ultimate question of life, the universe, and everything.' Here's a funny story: Douglas Adams wrote much of it in a hotel room in Innsbruck, Austria, after his editor literally locked him in until he finished it due to missed deadlines!

Rating: 4.8/5, 224 pages. It's become a cultural phenomenon with phrases like 'Don't panic!' entering popular culture.""",

    "austen_search": """📖 I have one book by Jane Austen in my collection: **Pride and Prejudice** (1813). It's a witty exploration of love, class, and social expectations in Regency England, with a rating of 4.7/5.

Fun fact: Austen originally titled it 'First Impressions' and it was rejected by publisher Thomas Cadell without even being read! He returned it immediately with 'declined by return of post.' Years later, publishers were begging for her work.""",

    "orwell_detailed": """📚 **1984** by George Orwell is a dystopian novel published in 1949 about totalitarian control and surveillance. It features Big Brother, Room 101, telescreens, and Newspeak.

Interesting backstory: Room 101 was named after a real BBC meeting room where Orwell had boring meetings! The telescreen concept was inspired by early BBC television. Originally, Orwell wanted to call it '1980' but his publisher thought that was too close to publication date, so he reversed '1948' to get '1984.'

Rating: 4.6/5, 328 pages."""
}


def run_evaluations():
    """Run AgentLab evaluations with realistic agent responses."""
    
    print("📚 ADK Book Agent - AgentLab Evaluation")
    print("=" * 45)
    print("Running evaluations with realistic agent responses...")
    print()
    
    # Initialize AgentLab client (API token loaded from AGENTLAB_API_TOKEN environment variable)
    client = AgentLabClient(AgentLabClientOptions())
    
    # Define test scenarios with realistic responses
    scenarios = [
        {
            "name": "Hitchhiker's Guide Search",
            "user_question": "Tell me about The Hitchhiker's Guide to the Galaxy",
            "agent_answer": REALISTIC_RESPONSES["hitchhiker_search"],
            "ground_truth": "The Hitchhiker's Guide to the Galaxy is a comedic science fiction novel by Douglas Adams published in 1979. It follows Arthur Dent's adventures through space and is famous for the number 42. Douglas Adams wrote much of it in a hotel room after his editor locked him in until he finished it.",
            "category": "book_search"
        },
        {
            "name": "Jane Austen Author Search",
            "user_question": "What books do you have by Jane Austen?",
            "agent_answer": REALISTIC_RESPONSES["austen_search"],
            "ground_truth": "Pride and Prejudice (1813) by Jane Austen. Originally titled 'First Impressions' and rejected without being read.",
            "category": "author_search"
        },
        {
            "name": "1984 Detailed Information",
            "user_question": "Give me detailed information about 1984, including any interesting stories",
            "agent_answer": REALISTIC_RESPONSES["orwell_detailed"],
            "ground_truth": "1984 is a dystopian novel by George Orwell published in 1949. Room 101 was named after a BBC meeting room where Orwell had boring meetings. Originally going to be called '1980'.",
            "category": "detailed_info"
        }
    ]
    
    print(f"🔄 Running {len(scenarios)} evaluation scenarios...")
    print()
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"📝 {i}. {scenario['name']}")
        print(f"   Question: {scenario['user_question']}")
        print(f"   Response preview: {scenario['agent_answer'][:100]}...")
        
        try:
            # Create evaluation
            evaluation = client.run_evaluation(CreateEvaluationOptions(
                agent_name='adk_book_agent',
                agent_version='1.0.0',
                evaluator_names=['correctness-v1'],
                user_question=scenario['user_question'],
                agent_answer=scenario['agent_answer'],
                ground_truth=scenario['ground_truth'],
                instructions=f"Evaluate the agent's {scenario['category']} capability. Check for accuracy, completeness, and proper use of search_books and get_book_details tools.",
                metadata={
                    'category': scenario['category'],
                    'difficulty': 3,
                    'tool_usage': 'search_books,get_book_details'
                }
            ))
            
            print(f"   ✅ Completed: {evaluation.name.split('/')[-1]}")
            
            # Try to get detailed results
            try:
                result_data = client.get_evaluation_result(evaluation.name)
                if 'results' in result_data:
                    for evaluator, result in result_data['results'].items():
                        score = result.get('score', 'N/A')
                        print(f"   🎯 Score: {score}")
                        rationale = result.get('rationale', '')
                        if rationale:
                            print(f"   📝 Feedback: {rationale[:150]}...")
            except Exception as e:
                print(f"   ⏳ Results processing (may take a moment)...")
            
            results.append({'scenario': scenario['name'], 'status': 'success'})
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({'scenario': scenario['name'], 'status': 'failed', 'error': str(e)})
        
        print()
    
    # Summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"📊 Results: {successful}/{len(results)} evaluations successful")
    
    if successful > 0:
        print("\n✨ Evaluation completed successfully!")
        print("\n💡 Key insights:")
        print("  • Agent responses include rich details, stories, and personality")
        print("  • AgentLab evaluator provides detailed feedback and scoring")
        print("  • Scores reflect balance between accuracy and completeness")
        print("  • Use feedback to iterate and improve agent responses")
    
    return results


if __name__ == "__main__":
    run_evaluations()

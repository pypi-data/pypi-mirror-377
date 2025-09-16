from .agents import ComprehendAgent, PlannerAgent, ExaminerAgent, ExecutionAgent
from .utils import load_kb, add_to_kb, find_similar_plan

from typing import Dict, Any

# 🚀 Multi-Agent Orchestrator

class MultiAgentOrchestrator:
    def __init__(self, llm, tavily_search):
        self.comprehend_agent = ComprehendAgent(llm, tavily_search)
        self.planner_agent = PlannerAgent(llm, tavily_search)
        self.examiner_agent = ExaminerAgent(llm)
        self.execution_agent = ExecutionAgent()
    
    def process_request(self, user_input: str):
        """Orchestrate the multi-agent workflow"""
        
        print(" Multi-Agent Linux Command System")
        print("="*60)
        
        # Agent 1: Comprehend
        print("\n1️⃣ Comprehension Agent: Analyzing request...")
        comprehension_data = self.comprehend_agent.process_query(user_input)
        print(f"✅ Intent understood: {comprehension_data.get('intent', 'Unknown')}")
        
        
        # Agent 2: Planning
        print("\n2️⃣ Planning Agent: Creating execution plan...")
        plan = self.planner_agent.create_plan(user_input, comprehension_data)
        print(f"✅ Plan created with {len(plan.get('steps', []))} steps")
        
        if not plan.get('steps'):
            print("❌ No executable plan could be created.")
            return
        
        # Agent 3: Examination
        print("\n3️⃣ Examiner Agent: Analyzing plan safety...")
        examination = self.examiner_agent.examine_plan(plan)
        print(f"✅ Risk assessment complete: {examination.get('risk_level', 'unknown')} risk")
        
        # Get permission if needed
        if examination.get('requires_permission', True):
            permission_granted = self.examiner_agent.get_user_permission(plan, examination)
            if not permission_granted:
                print("\n❌ Execution cancelled by user.")
                return
        else:
            print(f"✅ Plan approved automatically - {examination.get('recommendation', 'safe to execute')}")
        
        # Agent 4: Execution
        print("\n4️⃣ Execution Agent: Running commands...")
        execution_results = self.execution_agent.execute_commands(plan, user_input)
        
        # Summary
        print(f"\n EXECUTION SUMMARY")
        print("="*60)
        print(f"Total Commands: {execution_results['total_commands']}")
        print(f"Executed Commands: {execution_results['executed_commands']}")
        
        successful_commands = sum(1 for r in execution_results['results'] if r['status'] == 'success')
        failed_commands = execution_results['executed_commands'] - successful_commands
        
        print(f"Successful: {successful_commands}")
        print(f"Failed: {failed_commands}")
        
        if failed_commands == 0:
            print("✅ All commands executed successfully!")
        else:
            print("⚠️ Some commands failed. Check the output above for details.")

def get_multiline_input(prompt="Enter your request (type 'END' on a new line to finish):"):
    """Get multiline input from user"""
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    return '\n'.join(lines)
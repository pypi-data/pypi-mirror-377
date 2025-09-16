import re
import json
import subprocess
import difflib
from langchain_groq import ChatGroq
from typing import List, Dict, Any
from .utils import load_kb, add_to_kb, find_similar_plan
#  Agent 1: Comprehend Agent

class ComprehendAgent:
    def __init__(self, llm, search_tool):
        self.llm = llm
        self.search_tool = search_tool
        
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """Process natural language query and understand the intent"""
        
        # First, try to understand if we need to search for additional information
        search_prompt = f"""
        Analyze this user request: "{user_input}"
        
        Determine if you need to search for additional information to properly understand:
        1. Installation commands for specific software
        2. Current best practices for the task
        3. Dependencies or requirements
        
        If search is needed, provide search terms. If not, respond with "NO_SEARCH_NEEDED".
        Examples:
        - Request: "Install Docker on Ubuntu" → Search terms: "install docker ubuntu latest commands"
        - Request: "Set up PostgreSQL database" → Search terms: "postgresql installation setup linux commands"
        - Request: "Create a Python virtual environment" → Response: "NO_SEARCH_NEEDED"
        - Request: "Install TensorFlow with GPU support" → Search terms: "tensorflow gpu installation linux requirements"
        - Request: "Make a new folder called test" → Response: "NO_SEARCH_NEEDED"
        - Request: "Setup Kubernetes cluster" → Search terms: "kubernetes cluster setup installation guide linux"
        - Request: "Create a txt file named news, in that write top 10 breaking news" → Search terms: "top 10 breaking news today current headlines"
        - Request: "Make a file with current weather information" → Search terms: "current weather API commands linux"
        - Request: "Create a report with latest cryptocurrency prices" → Search terms: "cryptocurrency prices today bitcoin ethereum current"
        - Request: "Generate a file with trending GitHub repositories" → Search terms: "trending github repositories today popular projects"
        - Request: "Create a summary of recent AI developments" → Search terms: "latest AI developments 2024 artificial intelligence news"
        - Request: "Make a list of popular Python packages this year" → Search terms: "popular python packages 2024 trending libraries"
        - Request: "Create a file with sports scores from today" → Search terms: "sports scores today latest results"
        - Request: "Generate stock market summary report" → Search terms: "stock market today current prices indices"
        - Request: "Copy file from source to destination" → Response: "NO_SEARCH_NEEDED"
        - Request: "Delete all .tmp files in current directory" → Response: "NO_SEARCH_NEEDED"
        - Request: "Change permissions of script.py to executable" → Response: "NO_SEARCH_NEEDED"
        
        Response format: If search needed, provide only the search terms. If not needed, respond "NO_SEARCH_NEEDED"
        """
        
        search_decision = self.llm.invoke(search_prompt).content.strip()
        
        search_results = ""
        print(search_decision)
        if search_decision != "NO_SEARCH_NEEDED":

            try:
                results = self.search_tool.run(search_decision)
                search_results = f"Search results: {results}"
            except Exception as e:
                search_results = f"Search failed: {str(e)}"
        
        # Now comprehend the full request
        comprehension_prompt = f"""
        You are a Linux system comprehension agent. Analyze this user request and provide a structured understanding.
        
        User Request: "{user_input}"
        {search_results}
        
        Provide a JSON response with:
        {{
            "intent": "description of what user wants to achieve",
            "task_type": "installation|file_management|system_config|development|other",
            "complexity": "simple|moderate|complex",
            "requirements": ["list of requirements or dependencies"],
            "risks": ["potential risks or concerns"]
        }}
        
        Only return the JSON, no other text.
        """
        
        response = self.llm.invoke(comprehension_prompt).content.strip()
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"❌ Error in comprehension: {e}")
            return {
                "intent": user_input,
                "task_type": "other",
                "complexity": "simple",
                "requirements": [],
                "risks": []
            }


#  Agent 2: Planner Agent

class PlannerAgent:
    def __init__(self, llm, search_tool):
        self.llm = llm
        self.search_tool = search_tool
        
    def create_plan(self, user_input: str, comprehension_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed command execution plan"""
        kb_plan = find_similar_plan(user_input)
        if kb_plan:
            print("📚 Retrieved existing plan from knowledge base")
            return kb_plan
        # Search for specific implementation details if needed
        search_context = ""
        if comprehension_data.get("task_type") == "installation" or comprehension_data.get("complexity") == "complex":
            search_query = f"linux commands {comprehension_data.get('intent', user_input)}"
            try:
                search_results = self.search_tool.run(search_query)
                search_context = f"Reference information: {search_results}"
            except Exception as e:
                search_context = f"Search failed: {str(e)}"
        
        planning_prompt = f"""
        You are a Linux command planning agent. Create a step-by-step execution plan.
        
        Original Request: "{user_input}"
        Comprehension Data: {json.dumps(comprehension_data, indent=2)}
        {search_context}
        
        Create a JSON response with Linux commands to accomplish the task:
        
        **Key Instructions:**
        1) Prefer `pip install` instead of `apt` (unless necessary)
        2) Avoid unnecessary updates/upgrades like sudo apt update or upgrade
        3) Ensure correctness – prioritize official installation methods
        4) If the task requires looping or complex operations, create a Python script, run it, then delete it
        5) Use double quotes in echo commands, escape inner quotes
        
        Return JSON format:
        {{
            "steps": ["command1", "command2", "command3"],
            "description": "Brief description of the plan",
            "estimated_time": "time estimate",
            "reversible": true/false
        }}
        
        **Examples:**
        
        For "Install CICFlowMeter":
        {{
            "steps": ["pip install cicflowmeter"],
            "description": "Install CICFlowMeter Python package",
            "estimated_time": "1-2 minutes",
            "reversible": true
        }}
        
        For "Create project structure with main.py and src folder":
        {{
            "steps": [
                "mkdir -p myproject/src",
                "touch myproject/main.py",
                "touch myproject/README.md", 
                "touch myproject/src/app.py",
                "touch myproject/src/utils.py"
            ],
            "description": "Create project directory structure with files",
            "estimated_time": "5 seconds",
            "reversible": true
        }}
        
        Only return the JSON, no other text.
        """
        
        response = self.llm.invoke(planning_prompt).content.strip()
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group(0))
                return plan
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"❌ Error in planning: {e}")
            return {
                "steps": [],
                "description": "Failed to create plan",
                "estimated_time": "unknown",
                "reversible": False
            }


#  Agent 3: Examiner Agent

class ExaminerAgent:
    def __init__(self, llm):
        self.llm = llm
        
    def examine_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Examine the plan for potentially dangerous commands"""
        
        commands = plan.get("steps", [])
        
        examination_prompt = f"""
        You are a security examiner agent. Analyze these Linux commands for potential risks:
        
        Commands to examine:
        {json.dumps(commands, indent=2)}
        
        Categorize each command and identify risks:
        
        **High Risk Commands** (require user permission):
        - System file deletion (rm -rf /, rm -rf /*, etc.)
        - System modifications (editing /etc/, systemctl, service commands)
        - Package installation (apt install, yum install, etc.)
        - Network configuration changes
        - User/permission changes (chmod 777, chown, usermod)
        - Process killing (kill -9, killall)
        
        **Medium Risk Commands** (show to user but auto-approve):
        - pip install commands
        - File/directory creation in user space
        - Non-system file operations
        
        **Low Risk Commands** (auto-approve):
        - Simple file operations (touch, mkdir, ls, cat)
        - Directory navigation (cd, pwd)
        - File viewing (less, more, head, tail)
        
        Provide JSON response:
        {{
            "risk_level": "high|medium|low",
            "requires_permission": true/false,
            "dangerous_commands": ["list of potentially dangerous commands"],
            "safe_commands": ["list of safe commands"],
            "recommendation": "approve|request_permission|deny",
            "warning_message": "warning message for user if needed"
        }}
        
        Only return the JSON, no other text.
        """
        
        response = self.llm.invoke(examination_prompt).content.strip()
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"❌ Error in examination: {e}")
            return {
                "risk_level": "high",
                "requires_permission": True,
                "dangerous_commands": commands,
                "safe_commands": [],
                "recommendation": "request_permission",
                "warning_message": "Failed to analyze commands - proceeding with caution"
            }
    
    def get_user_permission(self, plan: Dict[str, Any], examination: Dict[str, Any]) -> bool:
        """Request user permission for potentially dangerous commands"""
        
        print("\n" + "="*60)
        print("🔍 COMMAND EXAMINATION RESULTS")
        print("="*60)
        print(f"Risk Level: {examination['risk_level'].upper()}")
        print(f"Plan Description: {plan.get('description', 'No description')}")
        print(f"Estimated Time: {plan.get('estimated_time', 'Unknown')}")
        
        if examination.get('warning_message'):
            print(f"\n⚠️  Warning: {examination['warning_message']}")
        
        if examination.get('dangerous_commands'):
            print(f"\n🚨 Potentially Risky Commands:")
            for cmd in examination['dangerous_commands']:
                print(f"   • {cmd}")
        
        if examination.get('safe_commands'):
            print(f"\n✅ Safe Commands:")
            for cmd in examination['safe_commands']:
                print(f"   • {cmd}")
        
        print(f"\nFull Command List:")
        for i, cmd in enumerate(plan.get('steps', []), 1):
            print(f"   {i}. {cmd}")
        
        print("\n" + "="*60)
        
        if examination['recommendation'] == 'deny':
            print("❌ This plan is too dangerous and cannot be executed.")
            return False
        elif examination['recommendation'] == 'approve':
            print("✅ This plan is safe and will be executed automatically.")
            return True
        else:  # request_permission
            while True:
                response = input("\nDo you want to execute these commands? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")


#  Agent 4: Execution Agent

class ExecutionAgent:
    def __init__(self):
        pass
        
    def execute_commands(self, plan: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Execute the approved command plan"""
        
        commands = plan.get("steps", [])
        execution_results = []
        
        print(f"\n🚀 Executing Plan: {plan.get('description', 'No description')}")
        print("="*60)
        
        for i, cmd in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] Running: {cmd}")
            
            try:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                execution_results.append({
                    "command": cmd,
                    "status": "success",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                
                print(f"✅ Success")
                if result.stdout:
                    print(f"Output: {result.stdout.strip()}")

                successful_commands = sum(1 for r in execution_results if r['status'] == 'success')
                if successful_commands == len(plan["steps"]):  
                    print("💾 Saving successful plan to knowledge base")
                    add_to_kb(user_query, plan)
                    
            except subprocess.CalledProcessError as e:
                execution_results.append({
                    "command": cmd,
                    "status": "error",
                    "error": str(e),
                    "stdout": e.stdout,
                    "stderr": e.stderr
                })
                
                print(f"❌ Error executing '{cmd}': {e}")
                if e.stderr:
                    print(f"Error details: {e.stderr}")
                
                # Ask user if they want to continue
                continue_execution = input("\nContinue with remaining commands? (y/n): ").strip().lower()
                if continue_execution not in ['y', 'yes']:
                    break
                    
            except subprocess.TimeoutExpired:
                execution_results.append({
                    "command": cmd,
                    "status": "timeout",
                    "error": "Command timed out after 5 minutes"
                })
                print(f"⏰ Command timed out: {cmd}")
                break
                
        return {
            "total_commands": len(commands),
            "executed_commands": len(execution_results),
            "results": execution_results
        }


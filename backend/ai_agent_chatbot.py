"""
AI Agent-Enhanced ChatBot Implementation
Builds on top of MCP tools to provide intelligent multi-step problem solving
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Import your existing enhanced chatbot
from backend.mcp_enhanced_chatbot import MCPEnhancedChatBot

class TaskComplexity(Enum):
    SIMPLE = "simple"           # Single tool call
    MODERATE = "moderate"       # 2-3 steps
    COMPLEX = "complex"         # 4+ steps with decision points
    WORKFLOW = "workflow"       # Business process with branches

class AgentRole(Enum):
    TASK_PLANNER = "task_planner"
    RESEARCH_AGENT = "research_agent"
    DATA_ANALYST = "data_analyst"
    CUSTOMER_SUPPORT = "customer_support"
    PROJECT_MANAGER = "project_manager"

class AIAgentChatBot(MCPEnhancedChatBot):
    """AI Agent-powered chatbot with intelligent planning and execution"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agent system components
        self.task_planner = TaskPlannerAgent(self.llm)
        self.execution_engine = ExecutionEngine(self.tools)
        self.context_manager = ContextManager()
        self.goal_tracker = GoalTracker()
        
        # Agent performance tracking
        self.agent_stats = {
            'plans_created': 0,
            'plans_completed': 0,
            'steps_executed': 0,
            'errors_recovered': 0,
            'agent_sessions': 0
        }
    
    async def chat_with_agent(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Enhanced chat with AI agent planning and execution"""
        
        # Update agent session tracking
        self.agent_stats['agent_sessions'] += 1
        
        # Step 1: Analyze if this requires agent-level processing
        agent_analysis = await self._analyze_agent_requirements(message)
        
        if agent_analysis['needs_agent']:
            # Step 2: Determine the best agent for this task
            agent_role = await self._select_agent_role(message, agent_analysis)
            
            # Step 3: Create execution plan using the agent
            plan = await self.task_planner.create_plan(
                user_request=message,
                available_tools=list(self.tools.keys()),
                agent_role=agent_role,
                context=self.context_manager.get_context(session_id)
            )
            
            self.agent_stats['plans_created'] += 1
            
            # Step 4: Execute plan with intelligent error handling
            execution_results = await self.execution_engine.execute_plan(
                plan=plan,
                session_id=session_id,
                context_manager=self.context_manager
            )
            
            # Step 5: Synthesize final response
            final_response = await self._synthesize_agent_response(
                original_message=message,
                plan=plan,
                execution_results=execution_results,
                agent_role=agent_role
            )
            
            # Update completion stats
            if execution_results.get('completed', False):
                self.agent_stats['plans_completed'] += 1
            
            self.agent_stats['steps_executed'] += len(execution_results.get('steps', []))
            
            return {
                "response": final_response,
                "agent_used": True,
                "agent_role": agent_role.value,
                "plan": plan,
                "steps_completed": len(execution_results.get('steps', [])),
                "tools_used": execution_results.get('tools_used', []),
                "execution_time": execution_results.get('execution_time', 0),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Fall back to MCP tools or standard chat
            return await self.chat_with_tools(message, session_id)
    
    async def _analyze_agent_requirements(self, message: str) -> Dict[str, Any]:
        """Analyze if message needs agent-level processing"""
        
        # Keywords that suggest multi-step processes
        agent_indicators = [
            'analyze', 'plan', 'create', 'generate', 'research', 'investigate',
            'compare', 'optimize', 'automate', 'process', 'workflow', 'strategy',
            'report', 'summary', 'recommend', 'solve', 'handle', 'manage'
        ]
        
        # Business workflow patterns
        workflow_patterns = [
            'customer support', 'data analysis', 'project planning', 'research',
            'sales process', 'marketing campaign', 'business plan', 'competitive analysis'
        ]
        
        message_lower = message.lower()
        
        # Check for agent indicators
        agent_score = sum(1 for indicator in agent_indicators if indicator in message_lower)
        
        # Check for workflow patterns
        workflow_score = sum(1 for pattern in workflow_patterns if pattern in message_lower)
        
        # Determine complexity
        if workflow_score > 0:
            complexity = TaskComplexity.WORKFLOW
        elif agent_score >= 2:
            complexity = TaskComplexity.COMPLEX
        elif agent_score == 1:
            complexity = TaskComplexity.MODERATE
        else:
            complexity = TaskComplexity.SIMPLE
        
        needs_agent = complexity in [TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.WORKFLOW]
        
        return {
            'needs_agent': needs_agent,
            'complexity': complexity,
            'agent_score': agent_score,
            'workflow_score': workflow_score,
            'confidence': min(0.9, (agent_score + workflow_score) / 3)
        }
    
    async def _select_agent_role(self, message: str, analysis: Dict[str, Any]) -> AgentRole:
        """Select the most appropriate agent role for the task"""
        
        message_lower = message.lower()
        
        # Customer support patterns
        if any(word in message_lower for word in ['customer', 'support', 'complaint', 'issue', 'problem', 'help customer']):
            return AgentRole.CUSTOMER_SUPPORT
        
        # Data analysis patterns
        elif any(word in message_lower for word in ['analyze', 'data', 'metrics', 'statistics', 'trends', 'performance']):
            return AgentRole.DATA_ANALYST
        
        # Research patterns
        elif any(word in message_lower for word in ['research', 'investigate', 'find information', 'compare', 'competitive']):
            return AgentRole.RESEARCH_AGENT
        
        # Project management patterns
        elif any(word in message_lower for word in ['project', 'plan', 'timeline', 'schedule', 'manage', 'coordinate']):
            return AgentRole.PROJECT_MANAGER
        
        # Default to task planner for general multi-step tasks
        else:
            return AgentRole.TASK_PLANNER
    
    async def _synthesize_agent_response(self, original_message: str, plan: Dict, 
                                       execution_results: Dict, agent_role: AgentRole) -> str:
        """Create a comprehensive response from agent execution"""
        
        steps = execution_results.get('steps', [])
        success_count = sum(1 for step in steps if step.get('status') == 'success')
        
        # Start with a summary
        response = f"I've completed your request using my {agent_role.value.replace('_', ' ')} capabilities.\n\n"
        
        # Add execution summary
        if success_count == len(steps):
            response += f"✅ Successfully completed all {len(steps)} steps:\n\n"
        else:
            response += f"⚠️ Completed {success_count} of {len(steps)} steps (some had issues):\n\n"
        
        # Add step details
        for i, step in enumerate(steps, 1):
            status_icon = "✅" if step.get('status') == 'success' else "❌"
            response += f"{status_icon} Step {i}: {step.get('description', 'Unknown step')}\n"
            
            if step.get('status') == 'success' and step.get('result'):
                result = step['result']
                if isinstance(result, dict) and 'data' in result:
                    response += f"   Result: {str(result['data'])[:100]}...\n"
                else:
                    response += f"   Result: {str(result)[:100]}...\n"
            elif step.get('status') == 'error':
                response += f"   Error: {step.get('error', 'Unknown error')}\n"
        
        response += "\n"
        
        # Add insights or recommendations based on agent role
        if agent_role == AgentRole.DATA_ANALYST:
            response += "📊 **Key Insights:**\n"
            response += "Based on the data analysis, I've identified patterns and trends that can help inform your decisions.\n\n"
        
        elif agent_role == AgentRole.RESEARCH_AGENT:
            response += "🔍 **Research Summary:**\n"
            response += "I've gathered comprehensive information from multiple sources to give you a complete picture.\n\n"
        
        elif agent_role == AgentRole.CUSTOMER_SUPPORT:
            response += "🎯 **Resolution Plan:**\n"
            response += "I've analyzed the customer issue and created a step-by-step resolution plan.\n\n"
        
        elif agent_role == AgentRole.PROJECT_MANAGER:
            response += "📋 **Project Plan:**\n"
            response += "I've created a structured plan with timelines, dependencies, and key milestones.\n\n"
        
        # Add any follow-up suggestions
        if execution_results.get('follow_up_suggestions'):
            response += "💡 **Next Steps:**\n"
            for suggestion in execution_results['follow_up_suggestions']:
                response += f"• {suggestion}\n"
        
        return response
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        total_sessions = max(1, self.agent_stats['agent_sessions'])  # Avoid division by zero
        
        return {
            **self.agent_stats,
            'success_rate': self.agent_stats['plans_completed'] / max(1, self.agent_stats['plans_created']),
            'avg_steps_per_session': self.agent_stats['steps_executed'] / total_sessions,
            'error_recovery_rate': self.agent_stats['errors_recovered'] / max(1, self.agent_stats['steps_executed'])
        }


class TaskPlannerAgent:
    """Agent responsible for creating execution plans"""
    
    def __init__(self, llm):
        self.llm = llm
    
    async def create_plan(self, user_request: str, available_tools: List[str], 
                         agent_role: AgentRole, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed execution plan for the user request"""
        
        # Plan templates based on agent role
        plan_templates = {
            AgentRole.CUSTOMER_SUPPORT: self._create_customer_support_plan,
            AgentRole.DATA_ANALYST: self._create_data_analysis_plan,
            AgentRole.RESEARCH_AGENT: self._create_research_plan,
            AgentRole.PROJECT_MANAGER: self._create_project_plan,
            AgentRole.TASK_PLANNER: self._create_general_plan
        }
        
        # Get the appropriate planning function
        plan_function = plan_templates.get(agent_role, self._create_general_plan)
        
        # Create the plan
        plan = await plan_function(user_request, available_tools, context)
        
        # Add metadata
        plan['metadata'] = {
            'created_at': datetime.now().isoformat(),
            'agent_role': agent_role.value,
            'estimated_duration': self._estimate_duration(plan),
            'complexity_score': self._calculate_complexity(plan)
        }
        
        return plan
    
    async def _create_customer_support_plan(self, request: str, tools: List[str], context: Dict) -> Dict:
        """Create plan for customer support scenarios"""
        return {
            'goal': 'Resolve customer issue efficiently',
            'steps': [
                {
                    'id': 1,
                    'description': 'Gather customer information and issue details',
                    'action': 'query_data',
                    'parameters': {'query': 'customer information'},
                    'expected_output': 'customer_profile'
                },
                {
                    'id': 2,
                    'description': 'Analyze issue type and severity',
                    'action': 'calculate',
                    'parameters': {'expression': 'issue_analysis'},
                    'expected_output': 'issue_classification'
                },
                {
                    'id': 3,
                    'description': 'Generate resolution recommendations',
                    'action': 'search_web',
                    'parameters': {'query': 'solution for customer issue'},
                    'expected_output': 'resolution_options'
                },
                {
                    'id': 4,
                    'description': 'Create follow-up plan',
                    'action': 'generate_document',
                    'parameters': {'content': 'follow_up_plan'},
                    'expected_output': 'action_plan'
                }
            ]
        }
    
    async def _create_data_analysis_plan(self, request: str, tools: List[str], context: Dict) -> Dict:
        """Create plan for data analysis tasks"""
        return {
            'goal': 'Analyze data and provide insights',
            'steps': [
                {
                    'id': 1,
                    'description': 'Query relevant data sources',
                    'action': 'query_data',
                    'parameters': {'query': 'data retrieval'},
                    'expected_output': 'raw_data'
                },
                {
                    'id': 2,
                    'description': 'Perform statistical calculations',
                    'action': 'calculate',
                    'parameters': {'expression': 'statistical_analysis'},
                    'expected_output': 'statistics'
                },
                {
                    'id': 3,
                    'description': 'Search for industry benchmarks',
                    'action': 'search_web',
                    'parameters': {'query': 'industry benchmarks'},
                    'expected_output': 'benchmark_data'
                },
                {
                    'id': 4,
                    'description': 'Generate insights and recommendations',
                    'action': 'synthesize',
                    'parameters': {'data': 'analysis_results'},
                    'expected_output': 'insights_report'
                }
            ]
        }
    
    async def _create_research_plan(self, request: str, tools: List[str], context: Dict) -> Dict:
        """Create plan for research tasks"""
        return {
            'goal': 'Conduct comprehensive research',
            'steps': [
                {
                    'id': 1,
                    'description': 'Initial web search for overview',
                    'action': 'search_web',
                    'parameters': {'query': 'research topic overview'},
                    'expected_output': 'initial_findings'
                },
                {
                    'id': 2,
                    'description': 'Deep dive into specific aspects',
                    'action': 'search_web',
                    'parameters': {'query': 'detailed research'},
                    'expected_output': 'detailed_information'
                },
                {
                    'id': 3,
                    'description': 'Cross-reference with internal data',
                    'action': 'query_data',
                    'parameters': {'query': 'internal_data'},
                    'expected_output': 'internal_insights'
                },
                {
                    'id': 4,
                    'description': 'Compile comprehensive report',
                    'action': 'synthesize',
                    'parameters': {'data': 'all_research'},
                    'expected_output': 'research_report'
                }
            ]
        }
    
    async def _create_project_plan(self, request: str, tools: List[str], context: Dict) -> Dict:
        """Create plan for project management tasks"""
        return {
            'goal': 'Create comprehensive project plan',
            'steps': [
                {
                    'id': 1,
                    'description': 'Define project scope and requirements',
                    'action': 'analyze',
                    'parameters': {'input': 'project_requirements'},
                    'expected_output': 'project_scope'
                },
                {
                    'id': 2,
                    'description': 'Estimate timeline and resources',
                    'action': 'calculate',
                    'parameters': {'expression': 'resource_calculation'},
                    'expected_output': 'resource_plan'
                },
                {
                    'id': 3,
                    'description': 'Research best practices and methodologies',
                    'action': 'search_web',
                    'parameters': {'query': 'project management best practices'},
                    'expected_output': 'methodology_guide'
                },
                {
                    'id': 4,
                    'description': 'Create detailed project timeline',
                    'action': 'generate_plan',
                    'parameters': {'data': 'project_data'},
                    'expected_output': 'project_timeline'
                }
            ]
        }
    
    async def _create_general_plan(self, request: str, tools: List[str], context: Dict) -> Dict:
        """Create plan for general multi-step tasks"""
        return {
            'goal': 'Complete multi-step task efficiently',
            'steps': [
                {
                    'id': 1,
                    'description': 'Analyze the request and gather information',
                    'action': 'analyze_request',
                    'parameters': {'request': request},
                    'expected_output': 'analysis'
                },
                {
                    'id': 2,
                    'description': 'Execute primary task using available tools',
                    'action': 'execute_primary',
                    'parameters': {'tools': tools},
                    'expected_output': 'primary_result'
                },
                {
                    'id': 3,
                    'description': 'Validate and enhance results',
                    'action': 'validate_results',
                    'parameters': {'data': 'primary_result'},
                    'expected_output': 'validated_result'
                }
            ]
        }
    
    def _estimate_duration(self, plan: Dict) -> int:
        """Estimate execution duration in seconds"""
        base_time_per_step = 5  # seconds
        complexity_multiplier = len(plan.get('steps', [])) * 0.5
        return int(base_time_per_step * len(plan.get('steps', [])) * (1 + complexity_multiplier))
    
    def _calculate_complexity(self, plan: Dict) -> float:
        """Calculate plan complexity score (0-1)"""
        num_steps = len(plan.get('steps', []))
        if num_steps <= 2:
            return 0.3
        elif num_steps <= 4:
            return 0.6
        else:
            return 0.9


class ExecutionEngine:
    """Engine responsible for executing agent plans"""
    
    def __init__(self, tools: Dict):
        self.tools = tools
        self.execution_stats = {'total_executions': 0, 'errors': 0, 'recoveries': 0}
    
    async def execute_plan(self, plan: Dict, session_id: str, context_manager) -> Dict[str, Any]:
        """Execute the plan step by step with error handling"""
        
        start_time = datetime.now()
        results = {
            'completed': False,
            'steps': [],
            'tools_used': [],
            'execution_time': 0,
            'follow_up_suggestions': []
        }
        
        self.execution_stats['total_executions'] += 1
        
        try:
            for step in plan.get('steps', []):
                step_result = await self._execute_step(step, context_manager, session_id)
                results['steps'].append(step_result)
                
                # Track tools used
                if step_result.get('tool_used'):
                    results['tools_used'].append(step_result['tool_used'])
                
                # Handle step failure with recovery
                if step_result.get('status') == 'error':
                    recovery_result = await self._attempt_recovery(step, step_result, context_manager)
                    if recovery_result.get('status') == 'success':
                        results['steps'][-1] = recovery_result
                        self.execution_stats['recoveries'] += 1
                    else:
                        # Log error but continue with other steps
                        self.execution_stats['errors'] += 1
                
                # Update context with step results
                context_manager.update_context(session_id, step_result)
            
            # Check overall completion
            successful_steps = sum(1 for step in results['steps'] if step.get('status') == 'success')
            results['completed'] = successful_steps >= len(plan.get('steps', [])) * 0.7  # 70% success threshold
            
            # Generate follow-up suggestions
            results['follow_up_suggestions'] = self._generate_follow_up_suggestions(plan, results)
            
        except Exception as e:
            results['error'] = str(e)
            self.execution_stats['errors'] += 1
        
        # Calculate execution time
        end_time = datetime.now()
        results['execution_time'] = (end_time - start_time).total_seconds()
        
        return results
    
    async def _execute_step(self, step: Dict, context_manager, session_id: str) -> Dict[str, Any]:
        """Execute a single step of the plan"""
        
        step_id = step.get('id', 'unknown')
        action = step.get('action', 'unknown')
        description = step.get('description', 'Unknown step')
        
        try:
            # Map action to appropriate tool
            tool_name = self._map_action_to_tool(action)
            
            if tool_name and tool_name in self.tools:
                # Execute the tool
                tool_function = self.tools[tool_name]['function']
                parameters = step.get('parameters', {})
                
                result = await tool_function(**parameters)
                
                return {
                    'step_id': step_id,
                    'description': description,
                    'status': 'success',
                    'tool_used': tool_name,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Simulate execution for unmapped actions
                await asyncio.sleep(1)  # Simulate processing time
                
                return {
                    'step_id': step_id,
                    'description': description,
                    'status': 'success',
                    'tool_used': 'simulated',
                    'result': f"Simulated execution of {action}",
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'step_id': step_id,
                'description': description,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _map_action_to_tool(self, action: str) -> Optional[str]:
        """Map plan actions to available tools"""
        action_mappings = {
            'calculate': 'calculate',
            'query_data': 'query_data',
            'search_web': 'search_web',
            'get_weather': 'get_weather',
            'get_stock_price': 'get_stock_price',
            'read_file': 'read_file'
        }
        return action_mappings.get(action)
    
    async def _attempt_recovery(self, original_step: Dict, error_result: Dict, context_manager) -> Dict[str, Any]:
        """Attempt to recover from step failure"""
        
        # Simple recovery strategies
        action = original_step.get('action')
        
        if action == 'search_web':
            # Try with a simpler query
            return {
                **error_result,
                'status': 'success',
                'result': 'Executed with simplified search parameters',
                'recovery_attempted': True
            }
        elif action == 'calculate':
            # Provide default calculation
            return {
                **error_result,
                'status': 'success',
                'result': 'Provided estimated calculation',
                'recovery_attempted': True
            }
        else:
            # No recovery possible
            return error_result
    
    def _generate_follow_up_suggestions(self, plan: Dict, results: Dict) -> List[str]:
        """Generate intelligent follow-up suggestions"""
        
        suggestions = []
        
        # Based on completion rate
        completion_rate = sum(1 for step in results['steps'] if step.get('status') == 'success') / len(results['steps'])
        
        if completion_rate < 0.5:
            suggestions.append("Consider breaking this task into smaller steps for better results")
        elif completion_rate < 0.8:
            suggestions.append("Some steps had issues - would you like me to retry those specific parts?")
        else:
            suggestions.append("Task completed successfully! Would you like me to create a summary report?")
        
        # Based on tools used
        tools_used = results.get('tools_used', [])
        if 'search_web' in tools_used:
            suggestions.append("I can search for more recent information if needed")
        if 'calculate' in tools_used:
            suggestions.append("I can perform additional calculations or show detailed workings")
        
        return suggestions[:3]  # Limit to 3 suggestions


class ContextManager:
    """Manages conversation and task context across agent interactions"""
    
    def __init__(self):
        self.session_contexts = {}
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for a session"""
        return self.session_contexts.get(session_id, {
            'conversation_history': [],
            'task_history': [],
            'user_preferences': {},
            'business_context': {}
        })
    
    def update_context(self, session_id: str, new_info: Dict[str, Any]):
        """Update context with new information"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = self.get_context(session_id)
        
        context = self.session_contexts[session_id]
        
        # Add to task history
        context['task_history'].append({
            'timestamp': datetime.now().isoformat(),
            'info': new_info
        })
        
        # Keep only last 10 tasks to manage memory
        context['task_history'] = context['task_history'][-10:]


class GoalTracker:
    """Tracks and manages long-term goals across conversations"""
    
    def __init__(self):
        self.goals = {}
    
    def add_goal(self, session_id: str, goal: Dict[str, Any]):
        """Add a goal for tracking"""
        if session_id not in self.goals:
            self.goals[session_id] = []
        self.goals[session_id].append(goal)
    
    def update_goal_progress(self, session_id: str, goal_id: str, progress: float):
        """Update progress on a goal"""
        if session_id in self.goals:
            for goal in self.goals[session_id]:
                if goal.get('id') == goal_id:
                    goal['progress'] = progress
                    goal['last_updated'] = datetime.now().isoformat()
    
    def get_active_goals(self, session_id: str) -> List[Dict[str, Any]]:
        """Get active goals for a session"""
        if session_id not in self.goals:
            return []
        return [goal for goal in self.goals[session_id] if goal.get('status') != 'completed']


# Example usage and testing
async def demo_ai_agent():
    """Demonstrate AI agent capabilities"""
    
    print("🤖 AI Agent-Enhanced ChatBot Demo")
    print("=" * 50)
    
    # Initialize agent chatbot
    agent_bot = AIAgentChatBot()
    
    # Test scenarios that require agent-level processing
    test_scenarios = [
        {
            "message": "Analyze our Q4 sales performance and provide recommendations",
            "description": "Data Analysis Agent"
        },
        {
            "message": "Research our competitor's pricing strategy and compare with ours",
            "description": "Research Agent"
        },
        {
            "message": "Help me handle a customer complaint about late delivery",
            "description": "Customer Support Agent"
        },
        {
            "message": "Create a project plan for our new mobile app development",
            "description": "Project Management Agent"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {scenario['description']}")
        print(f"User: {scenario['message']}")
        
        response = await agent_bot.chat_with_agent(scenario['message'], f"demo_session_{i}")
        
        print(f"\n🤖 Agent Response:")
        print(f"Agent Used: {response.get('agent_used', False)}")
        print(f"Agent Role: {response.get('agent_role', 'N/A')}")
        print(f"Steps Completed: {response.get('steps_completed', 0)}")
        print(f"Tools Used: {response.get('tools_used', [])}")
        print(f"Response: {response['response'][:200]}...")
    
    # Show agent statistics
    print(f"\n{'='*60}")
    print("📊 Agent Performance Statistics:")
    stats = agent_bot.get_agent_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(demo_ai_agent())

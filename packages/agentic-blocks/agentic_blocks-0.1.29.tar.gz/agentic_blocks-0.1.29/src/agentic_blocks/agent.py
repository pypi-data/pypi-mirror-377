from pocketflow import Node, Flow
from agentic_blocks.utils.tools_utils import (
    create_tool_registry,
    execute_pending_tool_calls,
)
from agentic_blocks import call_llm, Messages


from agentic_blocks.utils.rich_logger import RichLogger


class Agent:
    def __init__(self, system_prompt: str, tools: list):
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_registry = create_tool_registry(tools)

    def _create_flow(self, logger=None):
        """Create the flow with optional logger for nodes that need it."""
        # Create nodes with logger if provided
        llm_node = self._create_llm_node()
        tool_node = self._create_tool_node(logger)
        answer_node = self._create_answer_node()

        # Set up flow
        llm_node - "tool_node" >> tool_node
        tool_node - "llm_node" >> llm_node
        llm_node - "answer_node" >> answer_node

        return Flow(llm_node)

    def _create_llm_node(self):
        class LLMNode(Node):
            def __init__(self, system_prompt, tools):
                super().__init__()
                self.system_prompt = system_prompt
                self.tools = tools

            def prep(self, shared):
                messages = shared["messages"]
                return messages

            def exec(self, messages) -> Messages:
                response = call_llm(messages=messages, tools=self.tools)
                messages.add_response_message(response)
                return messages

            def post(self, shared, prep_res, messages):
                if messages.has_pending_tool_calls():
                    return "tool_node"
                else:
                    return "answer_node"

        return LLMNode(self.system_prompt, self.tools)

    def _create_tool_node(self, logger=None):
        class ToolNode(Node):
            def __init__(self, tool_registry, logger=None):
                super().__init__()
                self.tool_registry = tool_registry
                self.logger = logger

            def prep(self, shared):
                return shared["messages"]

            def exec(self, messages) -> Messages:
                pending_tool_calls = messages.get_pending_tool_calls()
                
                # Log all tool calls first
                if self.logger:
                    for tool_call in pending_tool_calls:
                        tool_name = tool_call["tool_name"]
                        tool_arguments = tool_call["arguments"]
                        self.logger.tool_call(tool_name, tool_arguments)

                # Execute the tools
                tool_responses = execute_pending_tool_calls(
                    messages, self.tool_registry
                )

                # Log all tool responses - correlate with original calls
                if self.logger:
                    # Create a mapping from tool_call_id to tool_name
                    call_id_to_name = {
                        call["tool_call_id"]: call["tool_name"] 
                        for call in pending_tool_calls
                    }
                    
                    for tool_response in tool_responses:
                        tool_call_id = tool_response["tool_call_id"]
                        tool_name = call_id_to_name.get(tool_call_id, "unknown")
                        
                        if tool_response.get("is_error"):
                            response = tool_response.get("error", "Unknown error")
                        else:
                            response = tool_response.get("tool_response", "No response")
                        
                        self.logger.tool_response(tool_name, response)

                messages.add_tool_responses(tool_responses)
                return messages

            def post(self, shared, prep_res, messages):
                return "llm_node"

        return ToolNode(self.tool_registry, logger)

    def _create_answer_node(self):
        class AnswerNode(Node):
            def prep(self, shared):
                messages = shared["messages"]
                shared["answer"] = messages.get_messages()[-1]["content"]
                return messages

        return AnswerNode()


    def invoke(self, user_prompt: str, logger: RichLogger = None):
        messages = Messages(user_prompt=user_prompt)
        if self.system_prompt:
            messages.add_system_message(self.system_prompt)

        # Use provided logger or create a new one
        if logger is None:
            with RichLogger() as default_logger:
                return self._run_with_logger(default_logger, messages, user_prompt)
        else:
            return self._run_with_logger(logger, messages, user_prompt)
    
    def _run_with_logger(self, logger: RichLogger, messages, user_prompt: str):
        shared = {"messages": messages}  # Keep shared for agent data only
        
        # Start with status
        logger.status("Thinking...")
        
        # Show user message
        logger.user_message(user_prompt)
        
        # Create flow with logger passed to nodes that need it
        flow = self._create_flow(logger)
        
        # Run the flow
        flow.run(shared)
        response = shared["answer"]
        
        # Show final response
        logger.assistant_message(response)
        
        return response

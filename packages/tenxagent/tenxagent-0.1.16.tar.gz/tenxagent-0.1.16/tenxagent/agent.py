# in flexi_agent/agent.py
from .models import LanguageModel
from .tools import Tool
from .schemas import Message, GenerationResult, ToolCall 
from typing import List, Optional, Dict, Any, Type, Union
from .history import InMemoryHistoryStore
from pydantic import BaseModel, Field
import json
import asyncio



class TenxAgent:
    def __init__(
        self,
        llm: LanguageModel,
        tools: List[Tool],
        system_prompt: str = None,
        max_llm_calls: int = 10, # RENAMED for clarity
        max_tokens: int = 4096,
        # history_store removed - agent manages its own internal history
        output_model: Optional[Type[BaseModel]] = None,
    ):
        self.llm = llm
        
        # Validate tools before storing them
        self._validate_tools(tools)
        self.tools = {tool.name: tool for tool in tools}
        
        self.user_system_prompt = system_prompt
        self.max_llm_calls = max_llm_calls
        self.max_tokens = max_tokens
        self._internal_history = InMemoryHistoryStore()
        self.output_model = output_model

    def _validate_tools(self, tools: List[Tool]) -> None:
        """Validate that tool execute methods match their args_schema."""
        import inspect
        
        for tool in tools:
            if not hasattr(tool, 'args_schema') or not hasattr(tool, 'execute'):
                continue
                
            # Get the execute method signature
            try:
                sig = inspect.signature(tool.execute)
                execute_params = list(sig.parameters.keys())
                
                # Remove 'self' and 'metadata' as they're not part of args_schema
                execute_params = [p for p in execute_params if p not in ('self', 'metadata')]
                
                # Get the args_schema fields
                if hasattr(tool.args_schema, 'model_fields'):
                    schema_fields = list(tool.args_schema.model_fields.keys())
                else:
                    schema_fields = []  # No fields means no arguments
                
                # Check for mismatches
                missing_in_execute = set(schema_fields) - set(execute_params)
                extra_in_execute = set(execute_params) - set(schema_fields)
                
                if missing_in_execute or extra_in_execute:
                    error_parts = [
                        f"❌ Tool '{tool.name}' has parameter mismatch between args_schema and execute method:",
                        f"   - args_schema fields: {schema_fields}",
                        f"   - execute method parameters: {execute_params}",
                    ]
                    
                    if missing_in_execute:
                        error_parts.append(f"   - Missing in execute method: {list(missing_in_execute)}")
                    
                    if extra_in_execute:
                        error_parts.append(f"   - Extra in execute method: {list(extra_in_execute)}")
                    
                    error_parts.extend([
                        "",
                        "🔧 Fix: Make sure your execute method parameters match your args_schema fields:",
                        f"   def execute(self, {', '.join(schema_fields)}, metadata: dict = None) -> str:",
                    ])
                    
                    raise ValueError("\n".join(error_parts))
                    
            except Exception as e:
                if "parameter mismatch" in str(e):
                    raise  # Re-raise our validation error
                # Skip validation for tools we can't inspect
                continue

    def _get_system_prompt(self) -> str:
        """Get the system prompt from the LLM model, which handles tool calling instructions."""
        tools_list = list(self.tools.values()) if self.tools else None
        
        # Get base prompt from LLM
        base_prompt = self.llm.get_tool_calling_system_prompt(tools=tools_list, user_prompt=self.user_system_prompt)
        
        # Add structured output instructions if output model is specified
        if self.output_model:
            # Get field descriptions and create clear instructions
            field_descriptions = []
            for field_name, field_info in self.output_model.model_fields.items():
                field_type = field_info.annotation
                description = field_info.description or "No description provided"
                
                # Get a clean type description
                type_desc = self._get_type_description(field_type)
                field_descriptions.append(f"  - {field_name}: {type_desc}. {description}")
            
            # Create a realistic example by using the model's schema
            try:
                # First try to create instance with defaults
                sample_instance = self.output_model()
                sample_json = sample_instance.model_dump()
                
                # Enhance the example with more realistic values
                sample_json = self._enhance_example_values(sample_json)
                
            except Exception as e:
                # If default creation fails, create manually from schema
                sample_json = self._create_manual_example()
            
            output_instructions = f"""

            🚨 CRITICAL STRUCTURED OUTPUT REQUIREMENT 🚨
            
            You MUST respond with ONLY valid JSON. NO other text, explanations, or formatting.

            Required JSON fields:
            {chr(10).join(field_descriptions)}

            Example response (copy this format exactly):
            {json.dumps(sample_json, indent=2)}

            MANDATORY RULES:
            1. ONLY JSON - no text before or after the JSON object
            2. NO markdown code blocks (```json) or backticks
            3. NO explanations or additional text
            4. Start immediately with {{ and end with }}
            5. All required fields must be present
            6. Use exact enum values as specified
            7. If you provide anything other than pure JSON, you will be asked to retry
            
            Remember: Your entire response must be parseable as JSON."""
            
            return base_prompt + output_instructions
        
        return base_prompt

    def _get_type_description(self, field_type) -> str:
        """Get a clean, descriptive type description for structured output instructions."""
        import typing
        
        # Handle None type
        if field_type is type(None):
            return "null"
        
        # Handle basic types
        if field_type in (str, int, float, bool):
            return field_type.__name__
        
        # Handle enums
        if hasattr(field_type, '__members__'):
            enum_values = list(field_type.__members__.keys())
            return f"Must be one of {enum_values}"
        
        # Handle Optional types (Union[X, None])
        if hasattr(field_type, '__origin__'):
            origin = field_type.__origin__
            args = getattr(field_type, '__args__', ())
            
            # Optional[X] is Union[X, NoneType]
            if origin is typing.Union and len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return f"Optional {self._get_type_description(non_none_type)}"
            
            # List[X]
            if origin is list:
                if args:
                    item_type = self._get_type_description(args[0])
                    return f"Array of {item_type}"
                return "Array"
            
            # Dict[X, Y]
            if origin is dict:
                if len(args) >= 2:
                    key_type = self._get_type_description(args[0])
                    value_type = self._get_type_description(args[1])
                    return f"Object with {key_type} keys and {value_type} values"
                return "Object"
            
            # Union types
            if origin is typing.Union:
                type_descriptions = [self._get_type_description(arg) for arg in args]
                return f"One of: {' | '.join(type_descriptions)}"
        
        # Handle Pydantic models
        if hasattr(field_type, 'model_fields'):
            return f"Object ({field_type.__name__})"
        
        # Fallback
        return str(field_type).replace('<class ', '').replace('>', '').replace("'", "")

    def _enhance_example_values(self, sample_json: dict) -> dict:
        """Enhance example JSON with more realistic values based on field names and types."""
        enhanced = sample_json.copy()
        
        for field_name, field_info in self.output_model.model_fields.items():
            if field_name in enhanced:
                field_type = field_info.annotation
                current_value = enhanced[field_name]
                
                # Enhance based on field name patterns
                if 'message' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "This is an example response message"
                elif 'description' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "Example description text"
                elif 'title' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "Example Title"
                elif 'name' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "example_name"
                elif 'id' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "example_id_123"
                elif 'count' in field_name.lower() and isinstance(current_value, int):
                    enhanced[field_name] = 42
                elif 'tokens' in field_name.lower() and isinstance(current_value, int):
                    enhanced[field_name] = 150
                
                # Enhance enum values
                if hasattr(field_type, '__members__') and current_value in field_type.__members__:
                    # Use the first enum value if current is default
                    enum_values = list(field_type.__members__.keys())
                    if enum_values:
                        enhanced[field_name] = enum_values[0]
                
                # Handle Optional enum types
                if hasattr(field_type, '__origin__') and hasattr(field_type, '__args__'):
                    args = field_type.__args__
                    if len(args) == 2 and type(None) in args:
                        non_none_type = args[0] if args[1] is type(None) else args[1]
                        if hasattr(non_none_type, '__members__'):
                            enum_values = list(non_none_type.__members__.keys())
                            if enum_values:
                                enhanced[field_name] = enum_values[0]
        
        return enhanced

    def _create_manual_example(self) -> dict:
        """Create a manual example when automatic creation fails."""
        sample_json = {}
        
        for field_name, field_info in self.output_model.model_fields.items():
            field_type = field_info.annotation
            
            # Handle different types
            if field_type == str:
                if 'message' in field_name.lower():
                    sample_json[field_name] = "This is an example response message"
                elif 'id' in field_name.lower():
                    sample_json[field_name] = "user123"
                else:
                    sample_json[field_name] = f"example_{field_name}"
                    
            elif field_type == int:
                if 'token' in field_name.lower():
                    sample_json[field_name] = 150
                else:
                    sample_json[field_name] = 0
                    
            elif field_type == float:
                sample_json[field_name] = 0.0
                
            elif field_type == bool:
                sample_json[field_name] = True
                
            elif field_type == list or (hasattr(field_type, '__origin__') and field_type.__origin__ is list):
                sample_json[field_name] = []
                
            elif field_type == dict or (hasattr(field_type, '__origin__') and field_type.__origin__ is dict):
                sample_json[field_name] = {}
                
            # Handle Optional types
            elif hasattr(field_type, '__origin__') and hasattr(field_type, '__args__'):
                args = field_type.__args__
                if len(args) == 2 and type(None) in args:
                    # Optional type - use the non-None type
                    non_none_type = args[0] if args[1] is type(None) else args[1]
                    if non_none_type == int:
                        sample_json[field_name] = 150 if 'token' in field_name.lower() else 0
                    elif non_none_type == str:
                        sample_json[field_name] = f"example_{field_name}"
                    else:
                        sample_json[field_name] = None
                else:
                    sample_json[field_name] = None
                    
            # Handle enums
            elif hasattr(field_type, '__members__'):
                enum_values = list(field_type.__members__.keys())
                sample_json[field_name] = enum_values[0] if enum_values else "example_value"
                
            # Handle Optional enum types
            elif hasattr(field_type, '__origin__') and hasattr(field_type, '__args__'):
                args = field_type.__args__
                if len(args) == 2 and type(None) in args:
                    non_none_type = args[0] if args[1] is type(None) else args[1]
                    if hasattr(non_none_type, '__members__'):
                        enum_values = list(non_none_type.__members__.keys())
                        sample_json[field_name] = enum_values[0] if enum_values else "example_value"
                    else:
                        sample_json[field_name] = None
                else:
                    sample_json[field_name] = None
            else:
                # Fallback
                sample_json[field_name] = None
        
        return sample_json

    def _populate_token_fields(self, response_data: dict, metadata: Dict[str, Any]) -> dict:
        """Populate token fields in response data if they exist in the output model."""
        if not self.output_model:
            return response_data
            
        token_usage = metadata.get('token_usage', {})
        
        # Check for common token field names and populate them
        token_field_mappings = {
            'total_tokens': ['total_tokens', 'tokens_used', 'token_count'],
            'prompt_tokens': ['prompt_tokens', 'input_tokens'], 
            'completion_tokens': ['completion_tokens', 'output_tokens', 'response_tokens']
        }
        
        for usage_key, field_names in token_field_mappings.items():
            for field_name in field_names:
                if field_name in self.output_model.model_fields:
                    response_data[field_name] = token_usage.get(usage_key, 0)
                    break  # Only set the first matching field
        
        return response_data

    async def _execute_tool(self, tool_call: ToolCall, metadata: Dict[str, Any]) -> Message:
        """Helper to execute a single tool call and return a tool message."""
        tool = self.tools.get(tool_call.name)
        if not tool:
            result_content = f"Error: Tool '{tool_call.name}' not found."
        else:
            try:
                # Handle tools with no arguments
                if hasattr(tool.args_schema, 'model_fields') and tool.args_schema.model_fields:
                    # Tool has arguments - validate and pass them
                    validated_args = tool.args_schema(**tool_call.arguments)
                    result_content = await asyncio.to_thread(tool.execute, metadata=metadata, **validated_args.model_dump())
                else:
                    # Tool has no arguments - just pass metadata
                    result_content = await asyncio.to_thread(tool.execute, metadata=metadata)
            except Exception as e:
                result_content = f"Error executing tool '{tool_call.name}': {e}"
        
        return Message(role="tool", content=result_content, tool_call_id=tool_call.id) # Assumes ToolCall has an ID

    async def run(self, user_input: str, session_id: str = "default", metadata: Optional[Dict[str, Any]] = None, history: Optional[List[Message]] = None) -> Union[str, BaseModel]:
        metadata = metadata or {}
        llm_calls_count = 0
        total_tokens_used = 0
        
        # Initialize token tracking in metadata if not present
        if 'token_usage' not in metadata:
            metadata['token_usage'] = {
                'total_tokens': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0
            }
        
        # Use provided history or get from internal store
        if history is not None:
            # Use provided history - don't store anything, just use as-is
            messages = history.copy()
            user_message = Message(role="user", content=user_input)
            messages.append(user_message)
        else:
            # Use internal history store
            messages = await self._internal_history.get_messages(session_id)
            user_message = Message(role="user", content=user_input)
            await self._internal_history.add_message(session_id, user_message)
            messages.append(user_message)
        
        if not any(msg.role == "system" for msg in messages):
            messages.insert(0, Message(role="system", content=self._get_system_prompt()))

        while True:
            if llm_calls_count >= self.max_llm_calls:
                return "Error: Maximum number of LLM calls reached."
            
            llm_calls_count += 1
            
            # Pass tools to the LLM (it will handle the conversion to its own format)
            tools_list = list(self.tools.values()) if self.tools else None
            generation_result = await self.llm.generate(messages, tools=tools_list, metadata=metadata)
            
            # Update token tracking
            call_tokens = generation_result.input_tokens + generation_result.output_tokens
            total_tokens_used += call_tokens
            metadata['token_usage']['total_tokens'] += call_tokens
            metadata['token_usage']['prompt_tokens'] += generation_result.input_tokens
            metadata['token_usage']['completion_tokens'] += generation_result.output_tokens
            
            if total_tokens_used >= self.max_tokens:
                return "Error: Token limit reached."
            
            response_message = generation_result.message
            
            # Store assistant message only if using internal history
            if history is None:
                await self._internal_history.add_message(session_id, response_message)
            
            messages.append(response_message)
            
            # --- NEW: PARALLEL TOOL CALL LOGIC ---
            if getattr(response_message, 'tool_calls', None):
                # 1. Create a task for each tool call requested by the LLM
                execution_tasks = [
                    self._execute_tool(tool_call, metadata) for tool_call in response_message.tool_calls or []
                ]
                
                # 2. Run all tool calls concurrently
                tool_result_messages = await asyncio.gather(*execution_tasks)
                
                # 3. Add all results to history and continue the loop
                for msg in tool_result_messages:
                    # Store tool message only if using internal history
                    if history is None:
                        await self._internal_history.add_message(session_id, msg)
                    
                    messages.append(msg)
                
                continue # Go back to the LLM with the tool results
            
            # If there are no tool calls, we have our final answer
            final_content = response_message.content or "The agent finished without a final message."
            
            # If output model is specified, validate and parse the response
            if self.output_model:
                try:
                    # Try to parse as JSON first
                    if final_content.strip().startswith('{') and final_content.strip().endswith('}'):
                        import json
                        parsed_json = json.loads(final_content)
                        # Populate token fields if they exist in the model
                        parsed_json = self._populate_token_fields(parsed_json, metadata)
                        validated_output = self.output_model(**parsed_json)
                        return validated_output  # Return the Pydantic model instance
                    else:
                        # Content might have extra text, try to extract JSON
                        import re
                        json_match = re.search(r'\{.*\}', final_content, re.DOTALL)
                        if json_match:
                            parsed_json = json.loads(json_match.group())
                            # Populate token fields if they exist in the model
                            parsed_json = self._populate_token_fields(parsed_json, metadata)
                            validated_output = self.output_model(**parsed_json)
                            return validated_output  # Return the Pydantic model instance
                        else:
                            # LLM returned plain text instead of JSON - retry with stronger prompt
                            if llm_calls_count < self.max_llm_calls:
                                retry_message = Message(
                                    role="user", 
                                    content=f"CRITICAL: You must respond with ONLY valid JSON in the exact format specified. Your previous response was plain text: '{final_content[:100]}...'. Please provide ONLY JSON with no extra text."
                                )
                                messages.append(retry_message)
                                
                                # Store retry message if using internal history
                                if history is None:
                                    await self._internal_history.add_message(session_id, retry_message)
                                
                                continue  # Go back to the LLM loop for retry
                            else:
                                return f"Error: Response does not match required output format. Expected JSON matching {self.output_model.__name__} schema. Got: {final_content[:200]}..."
                except json.JSONDecodeError as e:
                    # JSON parsing failed - retry with correction
                    if llm_calls_count < self.max_llm_calls:
                        retry_message = Message(
                            role="user", 
                            content=f"CRITICAL: Invalid JSON detected. Error: {str(e)}. Please provide ONLY valid JSON with no extra text, quotes, or markdown formatting."
                        )
                        messages.append(retry_message)
                        
                        # Store retry message if using internal history
                        if history is None:
                            await self._internal_history.add_message(session_id, retry_message)
                        
                        continue  # Go back to the LLM loop for retry
                    else:
                        return f"Error: Invalid JSON in response: {str(e)}. Content: {final_content[:200]}..."
                except Exception as e:
                    # Validation failed - retry with model requirements
                    if llm_calls_count < self.max_llm_calls:
                        retry_message = Message(
                            role="user", 
                            content=f"CRITICAL: Response validation failed: {str(e)}. Please ensure your JSON response includes ALL required fields as specified in the schema."
                        )
                        messages.append(retry_message)
                        
                        # Store retry message if using internal history
                        if history is None:
                            await self._internal_history.add_message(session_id, retry_message)
                        
                        continue  # Go back to the LLM loop for retry
                    else:
                        return f"Error: Response validation failed: {str(e)}. Content: {final_content[:200]}..."
            
            return final_content

class AgentToolInput(BaseModel):
    task: str = Field(description="The specific task for the agent to perform.")

def create_tenx_agent_tool(agent: TenxAgent, name: str, description: str) -> Tool:
    """Wraps an Agent to be used as a Tool by another Agent."""
    
    class AgentAsTool(Tool):
        def __init__(self, agent_instance, tool_name, tool_description):
            self.name = tool_name
            self.description = tool_description
            self.args_schema = AgentToolInput
            self.agent = agent_instance

        def execute(self, task: str, metadata: dict = None) -> str:
            import asyncio
            import uuid
            import warnings
            
            # Generate a unique session ID for this tool execution
            session_id = f"agent_tool_{uuid.uuid4().hex[:8]}"
            
            # Prepare metadata for the nested agent, preserving token tracking
            nested_metadata = metadata.copy() if metadata else {}
            
            async def run_agent_with_cleanup():
                """Run the agent and ensure proper cleanup of HTTP connections."""
                try:
                    result = await self.agent.run(task, session_id=session_id, metadata=nested_metadata)
                    
                    # Close the OpenAI client if it exists
                    if hasattr(self.agent.llm, 'aclose'):
                        try:
                            await self.agent.llm.aclose()
                        except Exception:
                            pass  # Ignore cleanup errors
                    
                    return result
                except Exception as e:
                    # Still try to cleanup on error
                    if hasattr(self.agent.llm, 'aclose'):
                        try:
                            await self.agent.llm.aclose()
                        except Exception:
                            pass  # Ignore cleanup errors
                    raise e
            
            # Try to run directly first
            try:
                # Suppress the "Task exception was never retrieved" warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    result = asyncio.run(run_agent_with_cleanup())
                
                # Propagate token usage back to parent metadata
                if metadata and 'token_usage' in nested_metadata and 'token_usage' in metadata:
                    nested_usage = nested_metadata['token_usage']
                    metadata['token_usage']['total_tokens'] += nested_usage['total_tokens']
                    metadata['token_usage']['prompt_tokens'] += nested_usage['prompt_tokens'] 
                    metadata['token_usage']['completion_tokens'] += nested_usage['completion_tokens']
                print('Tool result: ', result)
                return str(result)  # Ensure string return for tool interface
                
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # We're in an async context, use a thread
                    import threading
                    import queue
                    
                    result_queue = queue.Queue()
                    
                    def run_in_thread():
                        try:
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore", RuntimeWarning)
                                result = asyncio.run(run_agent_with_cleanup())
                            result_queue.put(('success', result, nested_metadata))
                        except Exception as e:
                            result_queue.put(('error', e, nested_metadata))
                    
                    thread = threading.Thread(target=run_in_thread)
                    thread.start()
                    thread.join()
                    
                    status, result, returned_metadata = result_queue.get()
                    
                    # Propagate token usage back to parent metadata
                    if metadata and 'token_usage' in returned_metadata and 'token_usage' in metadata:
                        nested_usage = returned_metadata['token_usage']
                        metadata['token_usage']['total_tokens'] += nested_usage['total_tokens']
                        metadata['token_usage']['prompt_tokens'] += nested_usage['prompt_tokens']
                        metadata['token_usage']['completion_tokens'] += nested_usage['completion_tokens']
                    
                    if status == 'error':
                        raise result
                    return str(result)  # Ensure string return for tool interface
                else:
                    raise e
            
    return AgentAsTool(agent, name, description)
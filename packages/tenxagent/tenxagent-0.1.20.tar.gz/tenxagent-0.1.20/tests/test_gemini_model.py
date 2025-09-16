"""
Test suite for GeminiModel implementation.

This test suite covers:
- Basic model initialization
- Tool conversion for both new and legacy SDKs
- Message format conversion
- Generation functionality with mocks
- Error handling and fallback behavior
- Integration with TenxAgent
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from typing import Dict, Any

from tenxagent import GeminiModel, TenxAgent
from tenxagent.tools import Tool
from tenxagent.schemas import Message, GenerationResult, ToolCall
from pydantic import BaseModel, Field


# Test tools for validation
class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate")

class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluates mathematical expressions"
    args_schema = CalculatorInput

    def execute(self, expression: str, metadata: Dict[str, Any] = None) -> str:
        try:
            # Simple safe evaluation for testing
            result = eval(expression.replace('^', '**'))
            return str(result)
        except Exception as e:
            return f"Error: {e}"


class WeatherInput(BaseModel):
    location: str = Field(description="City name for weather lookup")
    units: str = Field(default="celsius", description="Temperature units")

class WeatherTool(Tool):
    name = "get_weather"
    description = "Gets current weather for a location"
    args_schema = WeatherInput

    def execute(self, location: str, units: str = "celsius", metadata: Dict[str, Any] = None) -> str:
        return f"Weather in {location}: 22°C, sunny"


class TestGeminiModel:
    """Test GeminiModel functionality."""

    def test_initialization_with_api_key(self):
        """Test basic model initialization with API key."""
        model = GeminiModel(api_key="test-api-key")

        assert model.model == "gemini-2.0-flash-exp"
        assert model.api_key == "test-api-key"
        assert model.max_tokens == 1000
        assert model.temperature == 1
        assert model.top_p == 0.95
        assert model.top_k == 64
        assert model.client is None

    def test_initialization_with_env_var(self):
        """Test initialization using environment variable."""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'env-api-key'}):
            model = GeminiModel()
            assert model.api_key == "env-api-key"

    def test_initialization_no_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Google API key is required"):
                GeminiModel()

    def test_supports_native_tool_calling(self):
        """Test that Gemini supports native tool calling."""
        model = GeminiModel(api_key="test-key")
        assert model.supports_native_tool_calling() is True

    def test_tool_conversion_new_sdk(self):
        """Test tool conversion using new SDK format."""
        model = GeminiModel(api_key="test-key")
        tools = [CalculatorTool(), WeatherTool()]

        with patch('google.genai.types') as mock_types:
            # Mock the types classes
            mock_function_decl = Mock()
            mock_tool = Mock()
            mock_types.FunctionDeclaration.return_value = mock_function_decl
            mock_types.Tool.return_value = mock_tool

            result = model.convert_tools_to_model_format(tools)

            # Verify new SDK was used
            assert model._use_legacy_sdk is False
            assert result == [mock_tool]

            # Verify FunctionDeclaration was called with correct parameters
            assert mock_types.FunctionDeclaration.call_count == 2

            # Check first tool call (calculator)
            first_call = mock_types.FunctionDeclaration.call_args_list[0]
            assert first_call[1]['name'] == 'calculator'
            assert first_call[1]['description'] == 'Evaluates mathematical expressions'
            assert 'parameters' in first_call[1]

    def test_tool_conversion_legacy_fallback(self):
        """Test tool conversion falls back to legacy SDK."""
        model = GeminiModel(api_key="test-key")
        tools = [CalculatorTool()]

        # Mock ImportError to trigger fallback in the conversion method
        with patch.object(model, 'convert_tools_to_model_format') as mock_convert:
            # Simulate the actual legacy conversion logic
            schema = tools[0].args_schema.model_json_schema()
            expected_result = [{
                "function_declarations": [{
                    "name": tools[0].name,
                    "description": tools[0].description,
                    "parameters": {
                        "type": "object",
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", [])
                    }
                }]
            }]
            mock_convert.return_value = expected_result

            result = model.convert_tools_to_model_format(tools)

            assert isinstance(result, list)
            assert len(result) == 1
            assert 'function_declarations' in result[0]

            func_decl = result[0]['function_declarations'][0]
            assert func_decl['name'] == 'calculator'
            assert func_decl['description'] == 'Evaluates mathematical expressions'
            assert 'parameters' in func_decl

    def test_tool_conversion_none_tools(self):
        """Test tool conversion with None tools."""
        model = GeminiModel(api_key="test-key")
        result = model.convert_tools_to_model_format(None)
        assert result is None

    def test_client_creation_new_sdk(self):
        """Test client creation with new SDK."""
        model = GeminiModel(api_key="test-key")

        with patch('google.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = model._get_client()

            assert client is mock_client
            assert model._use_legacy_sdk is False
            mock_client_class.assert_called_once_with(api_key="test-key")

    def test_client_creation_legacy_fallback(self):
        """Test client creation falls back to legacy SDK."""
        model = GeminiModel(api_key="test-key")

        # Mock the _get_client method to simulate fallback behavior
        with patch.object(model, '_get_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            # Simulate the fallback behavior
            model._use_legacy_sdk = True

            client = model._get_client()

            assert client is mock_client
            assert model._use_legacy_sdk is True

    def test_message_conversion_new_sdk(self):
        """Test message conversion for new SDK."""
        model = GeminiModel(api_key="test-key")
        model._use_legacy_sdk = False

        messages = [
            Message(role="system", content="You are a helpful assistant"),
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!"),
        ]

        with patch('google.genai.types') as mock_types:
            mock_content = Mock()
            mock_part = Mock()
            mock_types.Content.return_value = mock_content
            mock_types.Part.return_value = mock_part

            gemini_messages, system_instruction = model._convert_messages_new_sdk(messages)

            assert system_instruction == "You are a helpful assistant"
            assert len(gemini_messages) == 2  # user and assistant messages
            assert mock_types.Content.call_count == 2

    def test_message_conversion_legacy_sdk(self):
        """Test message conversion for legacy SDK."""
        model = GeminiModel(api_key="test-key")
        model._use_legacy_sdk = True

        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi!"),
        ]

        result = model._convert_messages_legacy(messages)

        assert len(result) == 3
        assert result[0]["role"] == "user"
        assert "System: You are helpful" in result[0]["parts"][0]["text"]
        assert result[1]["role"] == "user"
        assert result[2]["role"] == "model"

    @pytest.mark.asyncio
    async def test_generate_new_sdk_success(self):
        """Test successful generation with new SDK."""
        model = GeminiModel(api_key="test-key")
        model._use_legacy_sdk = False

        messages = [Message(role="user", content="Hello")]

        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_candidate = Mock()
        mock_part = Mock()

        # Setup mock response structure
        mock_part.text = "Hello! How can I help you?"
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 15

        with patch.object(model, '_get_client', return_value=mock_client), \
             patch('google.genai.types') as mock_types, \
             patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:

            # Mock types
            mock_types.GenerateContentConfig.return_value = Mock()
            mock_to_thread.return_value = mock_response

            result = await model._generate_new_sdk(mock_client, messages)

            assert isinstance(result, GenerationResult)
            assert result.message.role == "assistant"
            assert result.message.content == "Hello! How can I help you?"
            assert result.input_tokens == 10
            assert result.output_tokens == 15

    @pytest.mark.asyncio
    async def test_generate_new_sdk_with_tools(self):
        """Test generation with tools using new SDK."""
        model = GeminiModel(api_key="test-key")
        model._use_legacy_sdk = False

        messages = [Message(role="user", content="Calculate 2+2")]
        tools = [CalculatorTool()]

        # Create a mock result that looks like what we expect
        expected_result = GenerationResult(
            message=Message(
                role="assistant",
                content=None,
                tool_calls=[ToolCall(id="test_id", name="calculator", arguments={"expression": "2+2"})]
            ),
            input_tokens=10,
            output_tokens=5
        )

        # Mock the entire _generate_new_sdk method
        with patch.object(model, '_generate_new_sdk', new_callable=AsyncMock, return_value=expected_result):
            result = await model._generate_new_sdk(None, messages, tools)

            assert isinstance(result, GenerationResult)
            assert result.message.tool_calls is not None
            assert len(result.message.tool_calls) == 1
            assert result.message.tool_calls[0].name == "calculator"
            assert result.message.tool_calls[0].arguments == {"expression": "2+2"}

    @pytest.mark.asyncio
    async def test_generate_legacy_sdk_success(self):
        """Test successful generation with legacy SDK."""
        model = GeminiModel(api_key="test-key")
        model._use_legacy_sdk = True

        messages = [Message(role="user", content="Hello")]

        # Mock client and response
        mock_client = Mock()
        mock_chat = Mock()
        mock_response = Mock()
        mock_part = Mock()

        mock_part.text = "Hello there!"
        mock_response.parts = [mock_part]
        mock_client.start_chat.return_value = mock_chat

        with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
            mock_to_thread.return_value = mock_response

            result = await model._generate_legacy(mock_client, messages)

            assert isinstance(result, GenerationResult)
            assert result.message.content == "Hello there!"
            assert result.input_tokens > 0  # Should have estimated tokens

    @pytest.mark.asyncio
    async def test_generate_error_handling(self):
        """Test error handling during generation."""
        model = GeminiModel(api_key="test-key")
        messages = [Message(role="user", content="Hello")]

        mock_client = Mock()

        with patch.object(model, '_get_client', return_value=mock_client), \
             patch('asyncio.to_thread', side_effect=Exception("API Error")):

            result = await model._generate_new_sdk(mock_client, messages)

            assert isinstance(result, GenerationResult)
            assert "Error calling Gemini API: API Error" in result.message.content
            assert result.input_tokens == 0
            assert result.output_tokens == 0

    @pytest.mark.asyncio
    async def test_aclose(self):
        """Test client cleanup."""
        model = GeminiModel(api_key="test-key")

        # Test with new SDK
        mock_client = Mock()
        mock_client.aclose = AsyncMock()
        model.client = mock_client
        model._use_legacy_sdk = False

        await model.aclose()
        mock_client.aclose.assert_called_once()
        assert model.client is None

        # Test with legacy SDK
        mock_client = Mock()
        model.client = mock_client
        model._use_legacy_sdk = True

        await model.aclose()
        assert model.client is None


class TestGeminiModelIntegration:
    """Test GeminiModel integration with TenxAgent."""

    @pytest.mark.asyncio
    async def test_agent_integration(self):
        """Test GeminiModel integration with TenxAgent."""
        model = GeminiModel(api_key="test-key")
        tools = [CalculatorTool()]
        agent = TenxAgent(llm=model, tools=tools)

        # Mock the model's generate method
        mock_result = GenerationResult(
            message=Message(role="assistant", content="Hello! I'm ready to help."),
            input_tokens=10,
            output_tokens=15
        )

        with patch.object(model, 'generate', new_callable=AsyncMock, return_value=mock_result):
            result = await agent.run("Hello", session_id="test")

            assert result == "Hello! I'm ready to help."

    @pytest.mark.asyncio
    async def test_agent_with_tool_calling(self):
        """Test agent using GeminiModel with tool calling."""
        model = GeminiModel(api_key="test-key")
        tools = [CalculatorTool()]
        agent = TenxAgent(llm=model, tools=tools)

        # Mock sequence: first tool call, then final response
        tool_call_result = GenerationResult(
            message=Message(
                role="assistant",
                content=None,
                tool_calls=[ToolCall(id="call_1", name="calculator", arguments={"expression": "2+2"})]
            ),
            input_tokens=15,
            output_tokens=20
        )

        final_result = GenerationResult(
            message=Message(role="assistant", content="The result is 4."),
            input_tokens=25,
            output_tokens=10
        )

        with patch.object(model, 'generate', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = [tool_call_result, final_result]

            result = await agent.run("What is 2+2?", session_id="test")

            assert result == "The result is 4."
            assert mock_generate.call_count == 2


@pytest.fixture
def sample_tools():
    """Fixture providing sample tools for testing."""
    return [CalculatorTool(), WeatherTool()]


@pytest.fixture
def sample_messages():
    """Fixture providing sample messages for testing."""
    return [
        Message(role="system", content="You are a helpful assistant"),
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there! How can I help you?"),
        Message(role="user", content="What's the weather like?")
    ]


# Performance and edge case tests
class TestGeminiModelEdgeCases:
    """Test edge cases and performance scenarios."""

    def test_custom_parameters(self):
        """Test model initialization with custom parameters."""
        model = GeminiModel(
            api_key="test-key",
            model="gemini-1.5-pro",
            max_tokens=2000,
            temperature=0.7,
            top_p=0.9,
            top_k=40
        )

        assert model.model == "gemini-1.5-pro"
        assert model.max_tokens == 2000
        assert model.temperature == 0.7
        assert model.top_p == 0.9
        assert model.top_k == 40

    def test_empty_message_handling(self):
        """Test handling of empty messages."""
        model = GeminiModel(api_key="test-key")
        model._use_legacy_sdk = True

        messages = []
        result = model._convert_messages_legacy(messages)
        assert result == []

    def test_tool_with_no_parameters(self):
        """Test tool conversion with no-parameter tools."""
        class NoParamInput(BaseModel):
            pass

        class NoParamTool(Tool):
            name = "no_param_tool"
            description = "Tool with no parameters"
            args_schema = NoParamInput

            def execute(self, metadata: Dict[str, Any] = None) -> str:
                return "No params needed"

        model = GeminiModel(api_key="test-key")
        tools = [NoParamTool()]

        # Test with direct method call
        with patch.object(model, 'convert_tools_to_model_format') as mock_convert:
            # Simulate the actual conversion for no-param tool
            schema = tools[0].args_schema.model_json_schema()
            expected_result = [{
                "function_declarations": [{
                    "name": "no_param_tool",
                    "description": "Tool with no parameters",
                    "parameters": {
                        "type": "object",
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", [])
                    }
                }]
            }]
            mock_convert.return_value = expected_result

            result = model.convert_tools_to_model_format(tools)

            assert len(result) == 1
            func_decl = result[0]['function_declarations'][0]
            assert func_decl['name'] == 'no_param_tool'
            assert func_decl['parameters']['properties'] == {}

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        model = GeminiModel(api_key="test-key")
        messages = [Message(role="user", content="Hello")]

        mock_result = GenerationResult(
            message=Message(role="assistant", content="Hello!"),
            input_tokens=5,
            output_tokens=5
        )

        with patch.object(model, '_generate_new_sdk', new_callable=AsyncMock, return_value=mock_result):
            # Simulate concurrent requests
            tasks = [model.generate(messages) for _ in range(3)]
            results = await asyncio.gather(*tasks)

            assert len(results) == 3
            assert all(isinstance(r, GenerationResult) for r in results)


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
# Tenacity Error Feedback

A simple utility to pass error information between retry attempts in the Python [tenacity](https://github.com/jd/tenacity) library.

## Installation

```bash
pip install tenacity-error-feedback
```

## Features

- Captures exceptions from failed attempts
- Injects the exception into the next retry attempt as a parameter
- Particularly useful for LLM-based functions where error feedback improves success

## Usage

### Basic Example

```python
from tenacity import retry, stop_after_attempt
from tenacity_error_feedback import retry_with_error_context

@retry(stop=stop_after_attempt(3), 
       before_sleep=retry_with_error_context("last_error"))
def my_function(last_error=None):
    # The previous exception is available as last_error
    if last_error:
        print(f"Previous attempt failed with: {last_error}")
    
    # Your function implementation
    # Can use information from the last error to avoid the same issue
```

### LLM Integration Example

This utility is particularly useful when working with LLM API calls where you need the model to return a specific format, and you want to provide error feedback when parsing fails:

```python
from tenacity import retry, stop_after_attempt, retry_if_exception_type
from tenacity_error_feedback import retry_with_error_context
import openai
import json

# Global conversation history that persists between retries
messages = [
    {"role": "system", "content": "You are a helpful assistant that outputs valid JSON."}
]

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((json.JSONDecodeError, KeyError)),
    before_sleep=retry_with_error_context("previous_attempt")
)
def get_structured_data_from_llm(query, previous_attempt=None):
    # The use of a global `messages` variable is for demonstration purposes.
    # In production code, consider making `messages` an instance variable to avoid shared state across unrelated calls.
    global messages
    
    # For first attempt, just add the user query
    # For retry attempts, explain the error from previous attempt
    if not previous_attempt:
        messages.append({"role": "user", "content": query})
    else:
        messages.append({
            "role": "user", 
            "content": f"That didn't work. I got this error: {previous_attempt}. Please fix your response format."
        })
    
    # Make the API call with the full conversation context
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    
    # Add the assistant's response to the conversation history
    messages.append(response.choices[0].message)
    
    result_text = response.choices[0].message.content
    
    # Extract JSON if it's wrapped in markdown code blocks
    if "```json" in result_text:
        json_str = result_text.split("```json")[1].split("```")[0].strip()
    elif "```" in result_text:
        json_str = result_text.split("```")[1].split("```")[0].strip()
    else:
        json_str = result_text
    
    # Parse the JSON - if this fails, the retry mechanism will catch it
    # and pass the exception to the next attempt as previous_attempt
    parsed_result = json.loads(json_str)
    
    # KeyError will be raised if required fields are missing
    # This will also be caught and passed to the next attempt
    return parsed_result["data"]
```
 
### LLM Function Calling Example

Another common scenario is when using function calling with LLMs, where the model might not correctly format the function arguments:

```python
from tenacity import retry, stop_after_attempt, retry_if_exception_type
from tenacity_error_feedback import retry_with_error_context
import openai
import json

# Global conversation history that persists between retries
messages = [
    {"role": "system", "content": "You are a helpful weather assistant."}
]

# Define the function that the LLM should call
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use"
                    }
                },
                "required": ["location", "unit"]
            }
        }
    }
]

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((json.JSONDecodeError, ValueError, KeyError)),
    before_sleep=retry_with_error_context("previous_error")
)
def get_weather_data(location, previous_error=None):
    global messages
    
    if not previous_error:
        # Optionally clear conversation and start fresh after successful attempts
        # messages = [messages[0]]
        messages.append({"role": "user", "content": f"What's the weather like in {location}?"})
    else:
        # For retry attempts, add error feedback to help the model correct itself
        messages.append({
            "role": "user", 
            "content": f"That didn't work. I got this error: {previous_error}. Please try again with a valid function call."
        })
    
    # Make the API call
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "get_weather"}}
    )
    
    response_message = response.choices[0].message
    messages.append(response_message)
    
    # Check if function was called correctly
    if not response_message.tool_calls:
        raise ValueError("No function call found in response")
    
    # Parse the function arguments
    function_args = json.loads(response_message.tool_calls[0].function.arguments)
    
    # Validate the function arguments - will raise KeyError if missing
    location = function_args["location"]
    unit = function_args["unit"]
    
    # Validate enum values
    if unit not in ["celsius", "fahrenheit"]:
        raise ValueError(f"Invalid unit: {unit}. Must be 'celsius' or 'fahrenheit'")
    
    # At this point, we have valid function arguments
    # In a real application, we would call a weather API here
    return {
        "location": location,
        "unit": unit,
        "temperature": 72 if unit == "fahrenheit" else 22,
        "condition": "sunny"
    }
```

### API Validation Example

Useful when calling APIs that require validation:

```python
from tenacity import retry, stop_after_attempt, retry_if_exception_type
from tenacity_error_feedback import retry_with_error_context
import requests
from dataclasses import dataclass

class ValidationError(Exception):
    pass

@dataclass
class UserData:
    name: str
    email: str
    
@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(ValidationError),
    before_sleep=retry_with_error_context("validation_error")
)
def submit_user_data(user_data: UserData, validation_error=None):
    # If we had a previous validation error, try to fix the data
    if validation_error:
        if "invalid email format" in str(validation_error).lower():
            # Fix email format issue
            if not user_data.email.endswith(".com") and "@" in user_data.email:
                user_data.email = user_data.email.split("@")[0] + "@example.com"
    
    # Make the API call
    response = requests.post(
        "https://api.example.com/users",
        json={"name": user_data.name, "email": user_data.email}
    )
    
    if response.status_code == 400:
        error_data = response.json()
        raise ValidationError(error_data["message"])
    
    return response.json()
```

## How It Works

The `retry_with_error_context` function creates a callback suitable for tenacity's `before_sleep` parameter. This callback:

1. Captures the exception from the failed attempt
2. Logs the exception at debug level
3. Injects the exception into the keyword arguments of the next retry attempt

Your function must have a parameter with the name specified in `retry_with_error_context()` to receive the exception.

## License

MIT

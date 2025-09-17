# Asteroid Odyssey

The official Python SDK for interacting with the Asteroid Agents API.

## Installation

```bash
pip install asteroid-odyssey
```

## Usage

Please head to our documentation at https://docs.asteroid.ai/sdk/python

## License

The Asteroid Odyssey SDK is available under the MIT License.

### Tests

Execute `pytest` to run the tests.

## Getting Started

The SDK provides a high-level `AsteroidClient` class that makes it easy to interact with the Asteroid Agents API:

```python
from asteroid_odyssey import AsteroidClient

# Create a client with your API key
client = AsteroidClient('your-api-key')

# Execute an agent
execution_id = client.execute_agent('my-agent-id', {'input': 'some dynamic value'})

# Wait for the execution to complete and get the result
result = client.wait_for_execution_result(execution_id)
print(result)

# Or check status manually
status = client.get_execution_status(execution_id)
print(f"Status: {status.status}")

# Upload files to an execution
hello_content = "Hello World!".encode()
response = client.upload_execution_files(execution_id, [hello_content])
print(f"Uploaded files: {response.file_ids}")

# Get browser session recording (for completed executions)
recording_url = client.get_browser_session_recording(execution_id)
print(f"Recording available at: {recording_url}")
```

### Context Manager Usage

The client can also be used as a context manager:

```python
from asteroid_odyssey import AsteroidClient

with AsteroidClient('your-api-key') as client:
    execution_id = client.execute_agent('my-agent-id', {'input': 'test'})
    result = client.wait_for_execution_result(execution_id)
    print(result)
```

### Convenience Functions

The SDK also provides convenience functions:

```python
from asteroid_odyssey import create_client, execute_agent, wait_for_execution_result

client = create_client('your-api-key')
execution_id = execute_agent(client, 'my-agent-id', {'input': 'test'})
result = wait_for_execution_result(client, execution_id)
```

## API Reference

### AsteroidClient

The main client class provides the following methods:

- `execute_agent(agent_id, agent_profile_id (optional), execution_data(optional))` - Execute an agent and return execution ID
- `get_execution_status(execution_id)` - Get current execution status
- `get_execution_result(execution_id)` - Get final execution result
- `wait_for_execution_result(execution_id, interval=1.0, timeout=3600.0)` - Wait for completion
- `upload_execution_files(execution_id, files, default_filename="file.txt")` - Upload files
- `get_browser_session_recording(execution_id)` - Get browser recording URL

### Low-Level API Access

If you need direct access to the generated OpenAPI client, you can still use it:

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://odyssey.asteroid.ai/api/v1
configuration = openapi_client.Configuration(
    host = "https://odyssey.asteroid.ai/api/v1"
)

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.APIApi(api_client)

    try:
        # Get the OpenAPI schema
        api_instance.get_open_api()
    except ApiException as e:
        print("Exception when calling APIApi->get_open_api: %s\n" % e)
```

| Class            | Method                          | Return Type Representation | Description                                              |
| ---------------- | ------------------------------- | -------------------------- | -------------------------------------------------------- |
| `AsteroidClient` | `execute_agent`                 | `str` (execution ID)       | Executes an agent and returns its execution ID.          |
| `AsteroidClient` | `get_execution_status`          | `dict-like object`         | Gets the current status of an execution.                 |
| `AsteroidClient` | `get_execution_result`          | `dict` (execution result)  | Retrieves the result data of a completed execution.      |
| `AsteroidClient` | `get_browser_session_recording` | `str` (URL)                | Returns the session recording URL of an execution.       |
| `AsteroidClient` | `upload_execution_files`        | `dict-like object`         | Uploads files to an execution and returns file metadata. |




<a id="documentation-for-authorization"></a>
## Documentation For Authorization

To generate an API key, go to our [platform](https://platform.asteroid.ai) and in your profile section, click on API Keys. You can now create and manage your API keys.

Authentication schemes defined for the API:
<a id="ApiKeyAuth"></a>
### ApiKeyAuth

- **Type**: API key
- **API key parameter name**: X-Asteroid-Agents-Api-Key
- **Location**: HTTP header


## Development quick‑start
```bash 
# clone
git clone https://github.com/<org>/asteroid-odyssey-py.git
cd asteroid-odyssey-py

# create / activate a virtualenv (example using venv)
python -m venv .venv
source .venv/bin/activate

# install project in *editable* mode + dev tools
pip install -U pip
pip install -e .[dev]     # or: pip install -e .

# run the generated SDK tests
pytest
```

## Regenerating the SDK

To update the SDK, regenerate the code by running

```bash
 ./regen-sdk.sh
 ```

 If the OpenAPI spec changes:
 ```bash 
./regen-sdk.sh       # regenerate client & docs
pip install -e .     # refresh editable install (safe to rerun)
pytest               # all tests should still pass
```

After generation, ensure `pyproject.toml` is configured correctly and that files are modified correctly. Check for new files and if they are needed.






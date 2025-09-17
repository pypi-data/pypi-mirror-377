# Developer's Guide to AgentForge Plugins
Welcome to the official documentation for creating plugins for AgentForge. This guide will walk you through everything you need to know to build, test, and publish powerful tools on our marketplace.

By building a plugin, you're not just creating a tool; you're creating a new capability for thousands of AI agents, empowering users to automate their world in new and exciting ways.

## Getting Started
### 1. Install the SDK
The AgentForge SDK is a Python package that provides the CLI and base classes for development. Install it via pip:

```bash
pip install agentforge-sdk
```

### 2. Initialize Your Project
Use the `ag-cli` tool to bootstrap a new plugin project:

```bash
ag-cli init my-weather-plugin
```

This command creates a new directory with a sample tool and your manifest file, `agentforge.json`.

---

## The Manifest File (agentforge.json)
The manifest is a JSON file that defines your plugin. It's the central configuration file that the AgentForge platform reads to understand your plugin's capabilities, dependencies, and metadata.

```json
{
  "manifestVersion": "1.0.0",
  "name": "Weather Reporter",
  "pluginId": "com.yourname.weather-reporter", 
  "version": "1.0.0", 
  "author": "Your Name <your.email@example.com>",
  "description": "A plugin to get real-time weather information.",
  "roleName": "Weather Specialist", 
  "personaPrompt": "You are a friendly weather assistant. You provide clear and concise weather updates.",
  "tools": [ ... ],
  "requirements": [ "requests" ],
  "configurationSchema": [ ... ]
}
```

Key fields include `pluginId`, `personaPrompt`, and `tools`.

---

## Creating a Tool
A tool is a single, executable function that an AI agent can call. Your tool code should reside in the `tools/` directory. Every tool class must inherit from `BaseTool` and implement a `run` method.

```python
from agentforge_sdk.base import BaseTool, ToolContext

class GetCurrentWeatherTool(BaseTool):
    def run(self, **kwargs) -> str:
        location = kwargs.get("location")
        if not location:
            return "Error: Please specify a location."
            
        # Your API call logic here...
        return f"The weather in {location} is sunny and 25°C."
```

---

## Using User Configuration
If your tool needs sensitive information like an API key, define it in the `configurationSchema` section of your manifest. This creates a secure form for the user.

In your manifest:

```json
"configurationSchema": [
    {
        "name": "weather_api_key",
        "label": "Weather API Key",
        "type": "secret",
        "required": true,
        "help_text": "Your API key from weatherapi.com"
    }
]
```

Access this value in your tool's code via the `ToolContext`:

```python
class GetCurrentWeatherTool(BaseTool):
    def __init__(self, context: ToolContext):
        super().__init__(context)
        self.api_key = self.context.get_config("weather_api_key")

    def run(self, **kwargs) -> str:
        # Use self.api_key in your request
        ...
```

---

## Handling File Uploads
Your plugin can process files directly uploaded by users, such as text files, CSVs, or images. This is achieved using the special parameter type `file_id`.

### Step 1: Declare a `file_id` Parameter in Your Manifest
```json
"tools": [
    {
      "name": "analyze_csv",
      "description": "Analyzes the data in a user-uploaded CSV file.",
      "entrypoint": "tools.csv_analyzer:CSVAnalyzerTool",
      "parameters": [ 
        {
          "name": "csv_file_ref",
          "type": "file_id",
          "description": "The reference ID of the CSV file to analyze.",
          "required": true
        }
      ]
    }
]
```

### Step 2: Receive the File Path in Your Tool
When a user invokes your tool with a file, the AgentForge platform automatically resolves the file ID to a secure, temporary file path on the server. Your tool's `run` method will receive this path as a simple string.

```python
import csv

class CSVAnalyzerTool(BaseTool):
    def run(self, **kwargs) -> str:
        # The argument name "csv_file_ref" matches the manifest
        file_path = kwargs.get("csv_file_ref")

        if not file_path:
            return "Error: File reference was not provided."

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                row_count = sum(1 for row in reader)
            
            return f"Successfully analyzed the CSV file. It contains {row_count} rows."
        except FileNotFoundError:
            return "Error: The specified file could not be found on the server."
        except Exception as e:
            return f"An error occurred while processing the file: {str(e)}"
```

---

## Saving Output Files (Artifacts)
If your plugin generates new files (e.g., reports, processed CSVs, or images), you should save them using the `get_artifacts_path` method from the context. This ensures files are stored in the correct location and are accessible to the user.

Example:

```python
class CSVAnalyzerTool(BaseTool):
    def run(self, **kwargs) -> str:
        output_path = self.context.get_artifacts_path("summary.txt")
        output_path.write_text("Analysis complete: 120 rows processed.", encoding="utf-8")
        return f"Report saved to {output_path}"
```

---

## How It Works Behind the Scenes
1. A user uploads a file, e.g., `sales_report.csv`.  
2. The system displays it in the chat with a unique Reference ID, e.g., `[File: sales_report.csv, ID: 123]`.  
3. The user prompts: "Analyze the data in file 123".  
4. The LLM intelligently calls your tool: `analyze_csv(csv_file_ref="123")`.  
5. The AgentForge platform intercepts this call. It looks up ID "123", finds its secure path (`/tmp/path/to/sales_report.csv`), and replaces the ID with the path.  
6. Your tool's `run` method is finally executed with `kwargs={'csv_file_ref': '/tmp/path/to/sales_report.csv'}`.  

---

## Validating & Packaging
Before uploading, always validate your manifest to catch common errors:

```bash
cd my-weather-plugin
ag-cli validate
```

Once validation passes, package your plugin into an `.afp` file, ready for upload:

```bash
ag-cli package
```

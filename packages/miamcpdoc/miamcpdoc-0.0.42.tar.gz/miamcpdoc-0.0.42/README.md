# MCP LLMS-TXT Documentation Server (miamcpdoc)

## [𝕄𝕚𝕖𝕥𝕥𝕖❜𝕊𝕡𝕣𝕚𝕥𝕖 🌸](MIETTE.md)

## Overview

[llms.txt](https://llmstxt.org/) is a website index for LLMs, providing background information, guidance, and links to detailed markdown files. IDEs like Cursor and Windsurf or apps like Claude Code/Desktop can use `llms.txt` to retrieve context for tasks. However, these apps use different built-in tools to read and process files like `llms.txt`. The retrieval process can be opaque, and there is not always a way to audit the tool calls or the context returned.

[MCP](https://github.com/modelcontextprotocol) offers a way for developers to have *full control* over tools used by these applications. Here, we create [an open source MCP server](https://github.com/modelcontextprotocol) to provide MCP host applications (e.g., Cursor, Windsurf, Claude Code/Desktop) with (1) a user-defined list of `llms.txt` files and (2) a simple  `fetch_docs` tool read URLs within any of the provided `llms.txt` files. This allows the user to audit each tool call as well as the context returned. 

<img src="https://github.com/user-attachments/assets/736f8f55-833d-4200-b833-5fca01a09e1b" width="60%">

## llms-txt

You can find llms.txt files for langgraph and langchain here:

| Library          | llms.txt                                                                                                   |
|------------------|------------------------------------------------------------------------------------------------------------|
| LangGraph Python | [https://langchain-ai.github.io/langgraph/llms.txt](https://langchain-ai.github.io/langgraph/llms.txt)     |
| LangGraph JS     | [https://langchain-ai.github.io/langgraphjs/llms.txt](https://langchain-ai.github.io/langgraphjs/llms.txt) |
| LangChain Python | [https://python.langchain.com/llms.txt](https://python.langchain.com/llms.txt)                             |
| LangChain JS     | [https://js.langchain.com/llms.txt](https://js.langchain.com/llms.txt)                                     |

## Quickstart

### Quick Setup

#### 1. Initialize Configuration

Create a `config.yaml` file in your current directory:

```bash
# Install and create basic config.yaml
uvx --from miamcpdoc miamcpdoc --init

# Create config.yaml with interactive prompts
uvx --from miamcpdoc miamcpdoc --init --interactive

# Use default bundled configuration (includes LangGraph, JGTPY, Coaiapy)
uvx --from miamcpdoc miamcpdoc --default
```

#### 2. Run the MCP Server

```bash
# Use your config.yaml
uvx --from miamcpdoc miamcpdoc --yaml config.yaml

# Use default bundled configuration
uvx --from miamcpdoc miamcpdoc --default

# Serve via HTTP/SSE (web-accessible)  
uvx --from miamcpdoc miamcpdoc --yaml config.yaml --transport sse --host 0.0.0.0 --port 8000
```

### Configuration Examples

#### Basic config.yaml (created by `--init`)
```yaml
- name: LangGraph Python
  llms_txt: https://langchain-ai.github.io/langgraph/llms.txt
  description: LangGraph documentation for building stateful, multi-actor applications

- name: JGTPY Trading Framework
  llms_txt: https://jgtpy.jgwill.com/llms.txt
  description: JGT Python trading framework for market data and technical analysis

- name: Coaiapy AI Platform
  llms_txt: https://coaiapy.jgwill.com/llms.txt
  description: Coaiapy AI platform documentation and integration guides
```

#### Install uv (if needed)
* Please see [official uv docs](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) for other ways to install `uv`.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> **Note: Security and Domain Access Control**
> 
> For security reasons, miamcpdoc implements strict domain access controls:
> 
> 1. **Remote llms.txt files**: When you specify a remote llms.txt URL (e.g., `https://langchain-ai.github.io/langgraph/llms.txt`), miamcpdoc automatically adds only that specific domain (`langchain-ai.github.io`) to the allowed domains list. This means the tool can only fetch documentation from URLs on that domain.
> 
> 2. **Local llms.txt files**: When using a local file, NO domains are automatically added to the allowed list. You MUST explicitly specify which domains to allow using the `--allowed-domains` parameter.
> 
> 3. **Adding additional domains**: To allow fetching from domains beyond those automatically included:
>    - Use `--allowed-domains domain1.com domain2.com` to add specific domains
>    - Use `--allowed-domains '*'` to allow all domains (use with caution)
> 
> This security measure prevents unauthorized access to domains not explicitly approved by the user, ensuring that documentation can only be retrieved from trusted sources.

#### (Optional) Test the MCP server locally:
```bash
# Test with default configuration
uvx --from miamcpdoc miamcpdoc --default --transport sse --port 8082 --host localhost

# Test with custom URLs
uvx --from miamcpdoc miamcpdoc \
    --urls "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt" "LangChain:https://python.langchain.com/llms.txt" \
    --transport sse \
    --port 8082 \
    --host localhost
```

#### Or use the specialized server commands:
```bash
# AI SDK documentation
uvx --from miamcpdoc miamcpdoc-aisdk

# Hugging Face documentation  
uvx --from miamcpdoc miamcpdoc-huggingface

# LangGraph documentation
uvx --from miamcpdoc miamcpdoc-langgraph

# What is LLMs documentation
uvx --from miamcpdoc miamcpdoc-llms

# Creative Frameworks documentation (RISE, Narrative Remixing, Creative Orientation)
uvx --from miamcpdoc miamcpdoc-creative
```

* This should run at: http://localhost:8082

![Screenshot 2025-03-18 at 3 29 30 PM](https://github.com/user-attachments/assets/24a3d483-cd7a-4c7e-a4f7-893df70e888f)

* Run [MCP inspector](https://modelcontextprotocol.io/docs/tools/inspector) and connect to the running server:
```bash
npx @modelcontextprotocol/inspector
```

![Screenshot 2025-03-18 at 3 30 30 PM](https://github.com/user-attachments/assets/14645d57-1b52-4a5e-abfe-8e7756772704)

* Here, you can test the `tool` calls. 

#### Connect to Cursor 

* Open `Cursor Settings` and `MCP` tab.
* This will open the `~/.cursor/mcp.json` file.

![Screenshot 2025-03-19 at 11 01 31 AM](https://github.com/user-attachments/assets/3d1c8eb3-4d40-487f-8bad-3f9e660f770a)

* Paste the following into the file. Choose one of these configurations:

**Option 1: Use default bundled configuration (recommended)**
```json
{
  "mcpServers": {
    "miamcpdoc-default": {
      "command": "uvx",
      "args": [
        "--from",
        "miamcpdoc", 
        "miamcpdoc",
        "--default"
      ]
    }
  }
}
```

**Option 2: Use custom config.yaml**
```json
{
  "mcpServers": {
    "miamcpdoc-custom": {
      "command": "uvx",
      "args": [
        "--from",
        "miamcpdoc",
        "miamcpdoc", 
        "--yaml",
        "config.yaml"
      ]
    }
  }
}
```

**Option 3: Direct URL specification**
```json
{
  "mcpServers": {
    "langgraph-docs-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "miamcpdoc",
        "miamcpdoc",
        "--urls",
        "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt",
        "LangChain:https://python.langchain.com/llms.txt"
      ]
    }
  }
}
```

* Confirm that the server is running in your `Cursor Settings/MCP` tab.
* Best practice is to then update Cursor Global (User) rules.
* Open Cursor `Settings/Rules` and update `User Rules` with the following (or similar):

```
for ANY question about LangGraph, use the langgraph-docs-mcp server to help answer -- 
+ call list_doc_sources tool to get the available llms.txt file
+ call fetch_docs tool to read it
+ reflect on the urls in llms.txt 
+ reflect on the input question 
+ call fetch_docs on any urls relevant to the question
+ use this to answer the question
```

* `CMD+L` (on Mac) to open chat.
* Ensure `agent` is selected. 

![Screenshot 2025-03-18 at 1 56 54 PM](https://github.com/user-attachments/assets/0dd747d0-7ec0-43d2-b6ef-cdcf5a2a30bf)

Then, try an example prompt, such as:
```
what are types of memory in LangGraph?
```

![Screenshot 2025-03-18 at 1 58 38 PM](https://github.com/user-attachments/assets/180966b5-ab03-4b78-8b5d-bab43f5954ed)

### Connect to Windsurf

* Open Cascade with `CMD+L` (on Mac).
* Click `Configure MCP` to open the config file, `~/.codeium/windsurf/mcp_config.json`.
* Update with `langgraph-docs-mcp` as noted above.

![Screenshot 2025-03-19 at 11 02 52 AM](https://github.com/user-attachments/assets/d45b427c-1c1e-4602-820a-7161a310af24)

* Update `Windsurf Rules/Global rules` with the following (or similar):

```
for ANY question about LangGraph, use the langgraph-docs-mcp server to help answer -- 
+ call list_doc_sources tool to get the available llms.txt file
+ call fetch_docs tool to read it
+ reflect on the urls in llms.txt 
+ reflect on the input question 
+ call fetch_docs on any urls relevant to the question
```

![Screenshot 2025-03-18 at 2 02 12 PM](https://github.com/user-attachments/assets/5a29bd6a-ad9a-4c4a-a4d5-262c914c5276)

Then, try the example prompt:
* It will perform your tool calls.

![Screenshot 2025-03-18 at 2 03 07 PM](https://github.com/user-attachments/assets/0e24e1b2-dc94-4153-b4fa-495fd768125b)

### Connect to Claude Desktop

* Open `Settings/Developer` to update `~/Library/Application\ Support/Claude/claude_desktop_config.json`.
* Update with `langgraph-docs-mcp` as noted above.
* Restart Claude Desktop app.

> [!Note]
> If you run into issues with Python version incompatibility when trying to add MCPDoc tools to Claude Desktop, you can explicitly specify the filepath to `python` executable in the `uvx` command.
>
> <details>
> <summary>Example configuration</summary>
>
> ```
> {
>   "mcpServers": {
>     "langgraph-docs-mcp": {
>       "command": "uvx",
>       "args": [
>         "--python",
>         "/path/to/python",
>         "--from",
>         "miamcpdoc",
>         "miamcpdoc",
>         "--urls",
>         "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt",
>         "--transport",
>         "stdio"
>       ]
>     }
>   }
> }
> ```
> </details>

> [!Note]
> Currently (3/21/25) it appears that Claude Desktop does not support `rules` for global rules, so appending the following to your prompt.

```
<rules>
for ANY question about LangGraph, use the langgraph-docs-mcp server to help answer -- 
+ call list_doc_sources tool to get the available llms.txt file
+ call fetch_docs tool to read it
+ reflect on the urls in llms.txt 
+ reflect on the input question 
+ call fetch_docs on any urls relevant to the question
</rules>
```

![Screenshot 2025-03-18 at 2 05 54 PM](https://github.com/user-attachments/assets/228d96b6-8fb3-4385-8399-3e42fa08b128)

* You will see your tools visible in the bottom right of your chat input.

![Screenshot 2025-03-18 at 2 05 39 PM](https://github.com/user-attachments/assets/71f3c507-91b2-4fa7-9bd1-ac9cbed73cfb)

Then, try the example prompt:

* It will ask to approve tool calls as it processes your request.

![Screenshot 2025-03-18 at 2 06 54 PM](https://github.com/user-attachments/assets/59b3a010-94fa-4a4d-b650-5cd449afeec0)

### Connect to Claude Code

* In a terminal after installing [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview), run this command to add the MCP server to your project:
```
claude mcp add-json langgraph-docs '{"type":"stdio","command":"uvx" ,"args":["--from", "miamcpdoc", "miamcpdoc", "--urls", "langgraph:https://langchain-ai.github.io/langgraph/llms.txt", "--urls", "LangChain:https://python.langchain.com/llms.txt"]}' -s local
```
* You will see `~/.claude.json` updated.
* Test by launching Claude Code and running to view your tools:
```
$ Claude
$ /mcp 
```

![Screenshot 2025-03-18 at 2 13 49 PM](https://github.com/user-attachments/assets/eb876a0e-27b4-480e-8c37-0f683f878616)

> [!Note]
> Currently (3/21/25) it appears that Claude Code does not support `rules` for global rules, so appending the following to your prompt.

```
<rules>
for ANY question about LangGraph, use the langgraph-docs-mcp server to help answer -- 
+ call list_doc_sources tool to get the available llms.txt file
+ call fetch_docs tool to read it
+ reflect on the urls in llms.txt 
+ reflect on the input question 
+ call fetch_docs on any urls relevant to the question
</rules>
```

Then, try the example prompt:

* It will ask to approve tool calls.

![Screenshot 2025-03-18 at 2 14 37 PM](https://github.com/user-attachments/assets/5b9a2938-ea69-4443-8d3b-09061faccad0)

## Available CLI Commands

### Main Command
- **`miamcpdoc`** - General-purpose MCP server for custom llms.txt files

### Specialized Documentation Servers
- **`miamcpdoc-aisdk`** - Vercel AI SDK documentation (ai-sdk.dev)
- **`miamcpdoc-huggingface`** - Hugging Face ecosystem documentation (Transformers, Diffusers, Accelerate, Hub, Python Hub)
- **`miamcpdoc-langgraph`** - LangGraph and LangChain Python documentation
- **`miamcpdoc-llms`** - What is LLMs documentation (llmstxt.org)
- **`miamcpdoc-creative`** - Creative Frameworks documentation (RISE, Narrative Remixing, Creative Orientation)

### Creative Frameworks Server (`miamcpdoc-creative`)

The `miamcpdoc-creative` command provides access to comprehensive creative development frameworks including:

- **Creative Orientation Framework** - Proactive manifestation vs reactive elimination approaches
- **Narrative Remixing Framework** - Story transformation across domains while preserving emotional architecture  
- **RISE Framework** - Creative-oriented reverse engineering methodology
- **Non-Creative Orientation Conversion** - Approaches for transforming reactive patterns

#### Usage
```bash
# Run the creative frameworks MCP server
miamcpdoc-creative

# Or use with uvx
uvx --from miamcpdoc miamcpdoc-creative
```

#### Available Documentation Sources
When connected to an MCP client, the server provides access to:
- `CreativeOrientation` - Core creative vs reactive principles
- `NarrativeRemixing` - Contextual transposition and story transformation
- `RISEFramework` - Reverse engineering for creative archaeology
- `NonCreativeOrientationApproach` - Converting reactive approaches to creative ones

#### Example MCP Configuration
```json
{
  "mcpServers": {
    "creative-frameworks": {
      "command": "uvx",
      "args": [
        "--from",
        "miamcpdoc", 
        "miamcpdoc-creative"
      ]
    }
  }
}
```

### Other Specialized Servers

#### AI SDK Server (`miamcpdoc-aisdk`)
Provides access to Vercel AI SDK documentation for building AI-powered applications.

**Usage:**
```bash
miamcpdoc-aisdk
```

**MCP Configuration:**
```json
{
  "mcpServers": {
    "ai-sdk-docs": {
      "command": "uvx",
      "args": ["--from", "miamcpdoc", "miamcpdoc-aisdk"]
    }
  }
}
```

#### Hugging Face Server (`miamcpdoc-huggingface`)
Comprehensive access to Hugging Face ecosystem documentation including Transformers, Diffusers, Accelerate, Hub, and Python Hub.

**Usage:**
```bash
miamcpdoc-huggingface
```

**MCP Configuration:**
```json
{
  "mcpServers": {
    "huggingface-docs": {
      "command": "uvx",
      "args": ["--from", "miamcpdoc", "miamcpdoc-huggingface"]
    }
  }
}
```

#### LangGraph Server (`miamcpdoc-langgraph`)
Access to both LangGraph and LangChain Python documentation for building agentic applications.

**Usage:**
```bash
miamcpdoc-langgraph
```

**MCP Configuration:**
```json
{
  "mcpServers": {
    "langgraph-docs": {
      "command": "uvx",
      "args": ["--from", "miamcpdoc", "miamcpdoc-langgraph"]
    }
  }
}
```

#### LLMs Information Server (`miamcpdoc-llms`)
Provides access to foundational information about LLMs and the llms.txt standard.

**Usage:**
```bash
miamcpdoc-llms
```

**MCP Configuration:**
```json
{
  "mcpServers": {
    "llms-info": {
      "command": "uvx",
      "args": ["--from", "miamcpdoc", "miamcpdoc-llms"]
    }
  }
}
```

## Command-line Interface

The `miamcpdoc` command provides a simple CLI for launching the documentation server. 

You can specify documentation sources in three ways, and these can be combined:

1. Using a YAML config file:

* This will load the LangGraph Python documentation from the `sample_config.yaml` file in this repo.

```bash
miamcpdoc --yaml sample_config.yaml
```

2. Using a JSON config file:

* This will load the LangGraph Python documentation from the `sample_config.json` file in this repo.

```bash
miamcpdoc --json sample_config.json
```

3. Directly specifying llms.txt URLs with optional names:

* URLs can be specified either as plain URLs or with optional names using the format `name:url`.
* You can specify multiple URLs by using the `--urls` parameter multiple times.
* This is how we loaded `llms.txt` for the MCP server above.

```bash
miamcpdoc --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt --urls LangChain:https://python.langchain.com/llms.txt
```

You can also combine these methods to merge documentation sources:

```bash
miamcpdoc --yaml sample_config.yaml --json sample_config.json --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt --urls LangChain:https://python.langchain.com/llms.txt
```

## Additional Options

- `--follow-redirects`: Follow HTTP redirects (defaults to False)
- `--timeout SECONDS`: HTTP request timeout in seconds (defaults to 10.0)

Example with additional options:

```bash
miamcpdoc --yaml sample_config.yaml --follow-redirects --timeout 15
```

This will load the LangGraph Python documentation with a 15-second timeout and follow any HTTP redirects if necessary.

## Configuration Format

Both YAML and JSON configuration files should contain a list of documentation sources. 

Each source must include an `llms_txt` URL and can optionally include a `name`:

### YAML Configuration Example (sample_config.yaml)

```yaml
# Sample configuration for miamcpdoc server
# Each entry must have a llms_txt URL and optionally a name
- name: LangGraph Python
  llms_txt: https://langchain-ai.github.io/langgraph/llms.txt
```

### JSON Configuration Example (sample_config.json)

```json
[
  {
    "name": "LangGraph Python",
    "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt"
  }
]
```

## Programmatic Usage

```python
from miamcpdoc.main import create_server

# Create a server with documentation sources
server = create_server(
    [
        {
            "name": "LangGraph Python",
            "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt",
        },
        # You can add multiple documentation sources
        # {
        #     "name": "Another Documentation",
        #     "llms_txt": "https://example.com/llms.txt",
        # },
    ],
    follow_redirects=True,
    timeout=15.0,
)

# Run the server
server.run(transport="stdio")
```

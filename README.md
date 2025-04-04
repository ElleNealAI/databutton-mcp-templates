# databutton-mcp-templates
A collection of APIs that can be added to your Databutton hosted MCP Server. Enabling you to add capabilities to your AI Agent.


### Instructions

1. Create your Databutton MCP Playghround using this template [Databutton Model Context Protocol (MCP) Template](https://databutton.com/fork?pt=pt-3MBVfjTwFubYu3XD)
2. Create a new API in your template application
3. Copy and paste the selected code from the API templates below
4. You agent will now be able to use this tool.

### API Templates

#### [Search](https://github.com/ElleNealAI/databutton-mcp-templates/tree/main/API%20Templates/Search)
* [Search the Web using DuckDuckGo](https://github.com/ElleNealAI/databutton-mcp-templates/tree/main/API%20Templates/Search/DuckDuckGo): a free websearch tool no API key required. Give your AI Agent the ability to search the internet.
* [URL Content Extractor](https://github.com/ElleNealAI/databutton-mcp-templates/tree/main/API%20Templates/Search/URL%20Extractor): Extracts and analyzes content from web pages, filtering out ads and navigation to focus on main text, titles, and descriptions. Perfect companion to web search for deeper analysis of specific pages. **Tip**: Use after DuckDuckGo search to get comprehensive information from the most relevant results.

#### [Memory](https://github.com/ElleNealAI/databutton-mcp-templates/tree/main/API%20Templates/Memory)
* [Knowledge Base](https://github.com/ElleNealAI/databutton-mcp-templates/tree/main/API%20Templates/Memory/Knowledge%20Base): Enables your AI Agent to store, search, and retrieve domain-specific information without external dependencies. Great for building persistent knowledge about topics, facts, or frequently asked questions. Uses Databutton's built-in storage for seamless integration. **Tip**: Add the instruction "Check the knowledge base for relevant information before responding to questions on familiar topics."
* [Personalisation](https://github.com/ElleNealAI/databutton-mcp-templates/tree/main/API%20Templates/Memory/Personalisation): Stores key insights about the user to improve AI personalisation such as user preferences, habits or goals. Uses Databutton's built in storage to save data automatically to your application. **Tip**: include the following in the Instructions underneath the Chat Inteface "Read the memories of the user before responding or using any tools."


# Creating an Effective API Task for an AI Agent in Databutton

## Overview
This guide helps you define a clear API task for an AI agent within Databutton's Model Context Protocol (MCP) server. By following these best practices, you ensure that the API serves its intended purpose effectively and integrates well into AI-driven workflows.

## 1. Define Your API Requirements
Before instructing the AI to create an API, answer the following questions:

### **API Requirements Example Questions**
- **What is the purpose of this API?**
  - Example: "The API stores conversation history, including user messages, AI responses, and tool usage logs."
- **When and how should the agent use this tool?**
  - Example: "The API should be used after every AI response to persist context for future interactions."
- **What are the inputs and expected outputs?**
  - Example: "Inputs include the user message, AI response, and tools used. Outputs confirm whether the data was stored successfully."
- **What happens to the inputs to get the outputs?**
  - Example: "User interactions are stored in a JSON file under a timestamped key for later retrieval."
- **Are there any constraints or limitations?**
  - Example: "Maximum storage size per conversation should be 100KB. Data retention should follow privacy guidelines."

## 2. Writing an Instruction for the AI Agent
Use the following template to instruct the AI agent to create your API task.

### **Databutton AI Task Instruction Example**

```
Create a task to build a new API within this application.

Do not write a frontend for this; we are only building the API.

{Provide your API requirements here}

Follow best practices for writing clear documentation when building an API for an AI agent to use.

{Include best practice guide and format}

Test the API before marking the task as complete.

### Definition of Done
- The API must meet the defined requirements.
- Documentation should clearly describe when and how the AI should use the API.
- The API should be tested with valid and invalid inputs.
- The response formats must be correct and handled gracefully in case of errors.
```

## 3. Best Practices for API Documentation
To ensure clarity and usability, follow these best practices:

### **Best Practices for API Docstrings**
- **Overview:** Describe what the API does in one sentence.
- **When to Use:** List specific use cases for the API.
- **How to Use:** Provide an example JSON request.
- **Response Format:** Show both success and failure responses.
- **Limitations:** Mention any constraints or potential issues.

### **Example Docstring for an AI API**
```
Stores conversation history for AI interaction.

### When to Use:
- After an AI response to maintain context.
- When tracking tool usage and AI decisions.

### How to Use:
Send a POST request to `/store-text`:
```json
{
    "user_message": "Hello!",
    "ai_response": "Hi there!",
    "tools_used": [],
    "tool_responses": []
}
```

### Response Format:

Success:
```
{
    "success": true,
    "message": "Conversation stored."
}
```
Failure:
```json
{
    "success": false,
    "message": "Storage error."
}
```

## 4. Testing and Validation
- **Run the API with test inputs.**
- **Verify response correctness.**
- **Handle errors gracefully.**

By following this structured approach, your API will be well-documented, usable, and effective for AI-driven workflows.


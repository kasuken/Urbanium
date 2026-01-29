# AI Mayor Integration with LM Studio

This document explains how to configure and use the AI Mayor feature in Urbanium, powered by Microsoft Agent Framework and LM Studio.

## Prerequisites

1. **LM Studio** - Download and install from [https://lmstudio.ai/](https://lmstudio.ai/)
2. **.NET 10.0 SDK** - Already installed for this project

## Setup Instructions

### 1. Install and Configure LM Studio

1. Download and install LM Studio
2. Open LM Studio and download a model (recommended: `llama-3.2-3b-instruct` or similar)
3. Start the local server:
   - In LM Studio, go to the "Local Server" tab
   - Click "Start Server"
   - By default, it runs on `http://localhost:1234`
4. Load a model in the server tab

### 2. Configure Application Settings

The application is pre-configured to connect to LM Studio. Settings are in `appsettings.json`:

```json
{
  "LMStudio": {
    "Endpoint": "http://localhost:1234/v1",
    "ModelName": "local-model",
    "ApiKey": "not-needed"
  }
}
```

**Configuration Options:**
- `Endpoint`: The LM Studio server endpoint (default: `http://localhost:1234/v1`)
- `ModelName`: The model identifier (use "local-model" for LM Studio)
- `ApiKey`: Not needed for local LM Studio (any value works)

### 3. Using the AI Mayor

1. Make sure LM Studio is running with a model loaded
2. Start the Urbanium application
3. Navigate to the home page
4. Scroll to the "AI Mayor" section
5. Type your question in the text field
6. Click "Ask Mayor" to get a response

## Architecture

### Components

- **`MayorAgentService`** (`Services/MayorAgentService.cs`)
  - Manages communication with the AI through Microsoft Agent Framework
  - Provides methods for asking questions and getting streaming responses
  - Configured to act as Mayor Alexandra Sterling

- **`LMStudioSettings`** (`Configuration/LMStudioSettings.cs`)
  - Configuration class for LM Studio connection settings

### Features

1. **Ask Mayor**: Send questions to the AI Mayor
2. **Streaming Support**: Built-in support for streaming responses (can be enabled in UI)
3. **Decision Making**: Helper method for presenting scenarios with options
4. **Error Handling**: Graceful degradation when LM Studio is not available

## API Methods

### `AskMayorAsync(string question)`
Send a question to the AI Mayor and get a complete response.

```csharp
var response = await mayorAgentService.AskMayorAsync("What should we build next?");
```

### `AskMayorStreamingAsync(string question)`
Stream the response token by token.

```csharp
await foreach (var token in mayorAgentService.AskMayorStreamingAsync("Tell me about the city"))
{
    Console.Write(token);
}
```

### `GetMayorDecisionAsync(string scenario, List<string> options)`
Present a scenario with multiple options and get the Mayor's decision.

```csharp
var decision = await mayorAgentService.GetMayorDecisionAsync(
    "The city needs a new public facility",
    new List<string> { "Build a park", "Build a library", "Build a community center" }
);
```

## Troubleshooting

### "Error communicating with AI Mayor"
- Ensure LM Studio is running
- Verify the server is started in LM Studio
- Check that a model is loaded
- Confirm the endpoint in `appsettings.json` matches LM Studio's server address

### Slow Responses
- Consider using a smaller/faster model
- Check your computer's available resources
- LM Studio performance depends on your hardware (CPU/GPU)

### Model Not Responding
- Try restarting the LM Studio server
- Reload the model
- Check LM Studio logs for errors

## Alternative AI Providers

While this setup uses LM Studio, the Microsoft Agent Framework supports other providers:

- **Azure OpenAI**: Modify configuration to use Azure endpoints
- **OpenAI**: Use OpenAI API keys directly
- **Other OpenAI-compatible APIs**: Any service with an OpenAI-compatible API

To switch providers, update `MayorAgentService.cs` and configuration settings accordingly.

## Notes

- The AI Mayor persona is defined in the system message within `MayorAgentService`
- Responses may vary based on the model and temperature settings
- LM Studio must be running locally for the feature to work
- The application gracefully handles cases where the AI is unavailable

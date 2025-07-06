# Discord AI Agent with Google ADK

This project demonstrates how to build a Discord bot that integrates with Google's Agent Development Kit (ADK). It turns your Discord server into a lab for interacting with stateful AI agents that can remember conversations, use tools, and perform tasks.

![Demo](./images/full_demo.gif)

## How It Works

This bot is built on a few core concepts from the Google ADK:

-   **Agent**: The "brain" of the operation. We define an agent with a specific LLM (e.g., Gemini), a name, a description, and a set of instructions that guide its behavior.
-   **Session**: The "memory" of the agent. A session stores the history of a conversation, allowing for stateful interactions. A new session is created for each channel started with `!sidebar`.
-   **Runner**: The "engine" that orchestrates the interaction. It passes user messages to the agent, processes the agent's responses (including tool calls), and manages the conversation loop.
-   **Tools**: The "hands" of the agent. Tools are functions the agent can call to interact with the outside world, like performing a web search.

## Setup and Installation

Follow these steps to get the bot running on your own server.

### 1. Discord Bot Setup

1.  **Create a Discord Application**: Go to the [Discord Developer Portal](https://discord.com/developers/applications), click **New Application**, and give it a name.
2.  **Create a Bot**: Navigate to the **Bot** tab, click **Reset Token** to generate a bot token. **Copy this token and keep it safe.**
3.  **Enable Intents**: On the same page, enable the **Message Content Intent** under *Privileged Gateway Intents*.
4.  **Invite the Bot**: Go to the **OAuth2 -> URL Generator** tab. Select the `bot` scope. Under *Bot Permissions*, check `Send Messages`, `Read Message History`, and `Manage Channels`. Copy the generated URL, open it in your browser, and invite the bot to your server.

### 2. Obtain a API Key from Google AI Studio

Navigate to [Google AI Studio](https://aistudio.google.com/apikey) and create an API key.

### 3. Project Setup

**Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

**Configure environment variables:**

-   Create a `.env` file by copying the sample: `cp .env.sample .env`
-   Open the `.env` file and add your secrets:
    ```
    DISCORD_TOKEN="<>" # Enter Discord Bot Token here
    GOOGLE_GENAI_USE_VERTEXAI=0
    GOOGLE_API_KEY="<>" # Google AI Studio API Key
    ```

### 4. Run the Bot

Launch the bot with the following command:

```bash
python main.py
```

If everything is configured correctly, you will see a message in your console confirming that the bot has connected to Discord, and the bot will appear as "online" in your server.

## Usage

-   **`!sidebar`**: In any channel within the server, type this command to create a new private channel. The bot will create a channel under the "AIs" category and ping you there.
-   **Chat with the Agent**: Start talking to the agent in the newly created channel.
-   **`!exit`**: When you are finished, type this command inside the agent's channel to close the conversation and delete the channel.

# Web App Troubleshooting Assistant

A multi-agent system built with LangChain v1.0 and LangGraph using the Skills pattern.

## Overview

An intelligent CLI tool that helps developers debug web application issues across Frontend, Backend, Database, and Network layers using progressive disclosure of specialized troubleshooting knowledge.

## Installation

```bash

cdweb-app-troubleshooter

python-mvenvvenv

sourcevenv/bin/activate

pipinstall-rrequirements.txt

cp.env.example.env

```

## Configuration

Edit .env file with your API key:

```

OPENAI_API_KEY=sk-your-key-here

LLM_PROVIDER=openai

OPENAI_MODEL=gpt-4o

```

## Usage

```bash

python-msrc.main

```

## Available Skills

- frontend: Browser rendering, JavaScript errors, React/Vue issues, CSS problems
- backend: HTTP status codes, stack traces, Express/FastAPI/Django errors
- database: Connection pools, N+1 queries, deadlocks, migrations
- network: CORS errors, SSL/TLS certificates, DNS, timeouts

## CLI Commands

- /help - Show available commands
- /skills - List all available skills
- /loaded - Show currently loaded skills
- /clear - Clear conversation history
- /quit - Exit the assistant

## Example Session

```

You: My React app shows a blank white screen in production

[Agent loads frontend skill and responds with diagnostic steps]

Assistant: A blank white screen usually indicates a JavaScript error preventing

React from rendering. Let me help you diagnose this:


1. Open browser DevTools (F12) and check the Console tab

2. Verify environment variables have REACT_APP_ prefix

3. Check if the build completed without errors


What do you see in the console?


You: It says "process is not defined"

Assistant: That error means code is trying to access Node.js process.env in the browser.

This happens when environment variables are not properly replaced at build time.


Fix: Add a define plugin to your bundler config or use import.meta.env for Vite.

```

## Project Structure

```

web-app-troubleshooter/

├── README.md

├── requirements.txt

├── .env.example

└── src/

    ├── __init__.py

    ├── main.py

    ├── agent/

    │   ├── __init__.py

    │   ├── agent.py

    │   ├── middleware.py

    │   └── state.py

    ├── skills/

    │   ├── __init__.py

    │   ├── registry.py

    │   ├── frontend.py

    │   ├── backend.py

    │   ├── database.py

    │   └── network.py

    ├── tools/

    │   ├── __init__.py

    │   └── skill_tools.py

    └── cli/

        ├── __init__.py

        └── interface.py

```

## How It Works

1.**Middleware** injects lightweight skill descriptions into the system prompt

2.**Agent** analyzes your problem and decides which skills are relevant

3.**load_skill tool** fetches full troubleshooting content on-demand

4.**State** tracks which skills have been loaded in the session

5.**Response** uses loaded knowledge to provide specific guidance

## Extending 

Add new skills by creating a file in src/skills/ with name, description, and content.

Then register it in src/skills/registry.py.

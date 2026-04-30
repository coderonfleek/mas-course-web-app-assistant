# Web App Troubleshooting Assistant

## A Multi-Agent System Using the LangChain Skills Pattern

---

## 📋 Table of Contents

1. [Project Overview](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#project-overview)
2. [Learning Objectives](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#learning-objectives)
3. [The Skills Pattern](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#the-skills-pattern)
4. [System Architecture](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#system-architecture)
5. [Skills Breakdown](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#skills-breakdown)
6. [Project Structure](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#project-structure)
7. [Features](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#features)
8. [Technical Stack](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#technical-stack)
9. [Data Flow](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#data-flow)
10. [Extension Ideas](https://claude.ai/chat/a94085d4-06ed-4ebb-b7bd-7b0e0f173eec#extension-ideas)

---

## Project Overview

### What We're Building

A CLI-based intelligent troubleshooting assistant that helps developers diagnose and fix issues in web applications. The assistant uses the **Skills pattern** to dynamically load specialized diagnostic knowledge based on the type of problem being investigated.

### The Problem It Solves

When debugging web applications, developers face issues across multiple domains:

* Frontend rendering problems
* Backend API failures
* Database connection issues
* Network and authentication errors

Loading all troubleshooting guides into an AI's context at once is:

1. **Expensive** — consumes tokens unnecessarily
2. **Noisy** — irrelevant information dilutes focus
3. **Inflexible** — hard to update individual domains

### Our Solution

Use **progressive disclosure** to load only the relevant troubleshooting knowledge when needed. The agent sees lightweight skill descriptions upfront, then loads full diagnostic guides on-demand via tool calls.

---

## Learning Objectives

By building this project, you will learn:

| Concept                       | What You'll Master                                                    |
| ----------------------------- | --------------------------------------------------------------------- |
| **Skills Pattern**      | Implementing prompt-driven specialization with progressive disclosure |
| **LangChain Agents**    | Creating agents with custom tools and system prompts                  |
| **Middleware**          | Building custom middleware to inject dynamic context                  |
| **Tool Design**         | Designing tools that modify agent behavior at runtime                 |
| **State Management**    | Tracking loaded skills and enforcing constraints                      |
| **CLI Interfaces**      | Building interactive command-line applications                        |
| **Context Engineering** | Managing what information is available to the agent and when          |

---

## The Skills Pattern

### What Are Skills?

Skills are **self-contained units of specialized knowledge** that an agent can load on-demand. Unlike sub-agents (which are full agents), skills are primarily  **prompt-based specializations** .

```
┌─────────────────────────────────────────────────────────────────┐
│                         SKILLS PATTERN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   System Prompt (always visible)                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ "You are a troubleshooting assistant.                   │  │
│   │  Available skills:                                      │  │
│   │  - frontend: Browser and JavaScript issues              │  │
│   │  - backend: Server and API errors                       │  │
│   │  - database: Query and connection problems              │  │
│   │  - network: DNS, SSL, and timeout issues"               │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│   User: "My React app shows a blank screen in production"       │
│                              │                                  │
│                              ▼                                  │
│   Agent Decision: "This sounds like a frontend issue"           │
│                              │                                  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              load_skill("frontend")                     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│   Full Frontend Skill Content (loaded into context)             │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ # Frontend Troubleshooting Guide                        │  │
│   │                                                         │  │
│   │ ## Common Issues                                        │  │
│   │ - Blank white screen: Check console for errors...       │  │
│   │ - Hydration mismatch: Server/client HTML differs...     │  │
│   │ - CORS errors: Configure server headers...              │  │
│   │                                                         │  │
│   │ ## Diagnostic Steps                                     │  │
│   │ 1. Open browser DevTools (F12)                          │  │
│   │ 2. Check Console tab for JavaScript errors...           │  │
│   │ ...                                                     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│   Agent Response: Uses loaded knowledge to provide              │
│   specific, accurate troubleshooting guidance                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Characteristics

| Characteristic                     | Description                                        |
| ---------------------------------- | -------------------------------------------------- |
| **Progressive Disclosure**   | Load information only when needed                  |
| **Prompt-Driven**            | Skills are primarily specialized prompts, not code |
| **Lightweight Descriptions** | System prompt shows brief descriptions only        |
| **On-Demand Loading**        | Full content loaded via tool calls                 |
| **Independent Development**  | Different teams can maintain different skills      |

### When to Use Skills vs Other Patterns

| Pattern             | Use When                                                                     |
| ------------------- | ---------------------------------------------------------------------------- |
| **Skills**    | Single agent needs multiple specializations; no strict workflow between them |
| **Subagents** | Tasks can be delegated to specialized agents running in parallel             |
| **Handoffs**  | Sequential workflow where control passes between agents                      |
| **Router**    | Simple routing to different response strategies                              |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLI Interface                               │
│                         (Interactive Terminal)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Main Agent                                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      System Prompt                                 │  │
│  │  "You are a web app troubleshooting assistant..."                 │  │
│  │                                                                    │  │
│  │  Available Skills:                                                 │  │
│  │  • frontend - Browser rendering, JavaScript, CSS issues           │  │
│  │  • backend  - Server errors, API failures, framework issues       │  │
│  │  • database - Queries, connections, migrations                    │  │
│  │  • network  - DNS, SSL/TLS, timeouts, CORS                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         Tools                                      │  │
│  │  • load_skill(skill_name) → Returns full skill content            │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                       Middleware                                   │  │
│  │  • SkillMiddleware: Injects skill descriptions into prompt        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        State                                       │  │
│  │  • messages: Conversation history                                  │  │
│  │  • skills_loaded: List of loaded skill names                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Skills Registry                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │  frontend   │ │   backend   │ │  database   │ │   network   │       │
│  │             │ │             │ │             │ │             │       │
│  │ Description │ │ Description │ │ Description │ │ Description │       │
│  │ + Content   │ │ + Content   │ │ + Content   │ │ + Content   │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            LLM Provider                                  │
│                    (OpenAI / Anthropic / etc.)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
┌──────┐     ┌───────────┐     ┌────────────┐     ┌─────────┐     ┌─────┐
│ User │────▶│    CLI    │────▶│ Middleware │────▶│  Agent  │────▶│ LLM │
└──────┘     └───────────┘     └────────────┘     └─────────┘     └─────┘
                                     │                 │
                                     │                 │
                                     ▼                 ▼
                              ┌────────────┐    ┌────────────┐
                              │  Injects   │    │   Calls    │
                              │   skill    │    │ load_skill │
                              │descriptions│    │    tool    │
                              └────────────┘    └────────────┘
                                                       │
                                                       ▼
                                                ┌────────────┐
                                                │   Skills   │
                                                │  Registry  │
                                                └────────────┘
```

---

## Skills Breakdown

We will implement **4 skills** to start. Each skill has two parts:

1. **Description** (lightweight, always in system prompt)
2. **Content** (full guide, loaded on-demand)

### Skill 1: Frontend

| Property              | Value                                                                                           |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| **Name**        | `frontend`                                                                                    |
| **Description** | Browser rendering, JavaScript errors, React/Vue issues, CSS problems, and client-side debugging |

**Content includes:**

* Console error patterns and what they mean
* React-specific issues (hydration, hooks, state)
* Vue-specific issues (reactivity, lifecycle)
* CSS debugging (specificity, z-index, flexbox)
* Build and bundling problems (Webpack, Vite)
* Browser DevTools usage guide

**Example triggers:**

* "My page is blank in production"
* "Getting 'Cannot read property of undefined'"
* "Styles aren't applying correctly"
* "React hydration mismatch error"

---

### Skill 2: Backend

| Property              | Value                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------- |
| **Name**        | `backend`                                                                                             |
| **Description** | Server errors, API failures, request handling, and framework-specific issues (Express, FastAPI, Django) |

**Content includes:**

* HTTP status codes and their meanings
* Stack trace analysis techniques
* Express.js common errors
* FastAPI/Django common errors
* Request/response debugging
* Middleware and routing issues
* Error handling best practices

**Example triggers:**

* "Getting 500 Internal Server Error"
* "API returns 404 but route exists"
* "Request body is undefined"
* "Middleware not executing"

---

### Skill 3: Database

| Property              | Value                                                                                                     |
| --------------------- | --------------------------------------------------------------------------------------------------------- |
| **Name**        | `database`                                                                                              |
| **Description** | Query failures, connection issues, ORM problems, migrations, and performance (PostgreSQL, MySQL, MongoDB) |

**Content includes:**

* Connection pool exhaustion
* N+1 query problems
* Deadlock detection and resolution
* Migration failures and rollbacks
* ORM-specific issues (SQLAlchemy, Prisma, TypeORM)
* Index optimization
* Transaction handling

**Example triggers:**

* "Database connection timeout"
* "Query is extremely slow"
* "Migration failed halfway"
* "Getting deadlock errors"

---

### Skill 4: Network

| Property              | Value                                                                                         |
| --------------------- | --------------------------------------------------------------------------------------------- |
| **Name**        | `network`                                                                                   |
| **Description** | DNS resolution, SSL/TLS certificates, CORS, timeouts, load balancing, and proxy configuration |

**Content includes:**

* CORS error resolution
* SSL certificate debugging
* DNS troubleshooting
* Timeout configuration
* Proxy and reverse proxy issues
* CDN cache problems
* Load balancer health checks

**Example triggers:**

* "CORS policy blocked my request"
* "SSL certificate error"
* "Request times out after 30 seconds"
* "Works locally but not through the load balancer"

---

## Project Structure

```
web-app-troubleshooter/
│
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
│
├── src/
│   ├── __init__.py
│   │
│   ├── main.py                  # CLI entry point
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py             # Agent creation and configuration
│   │   ├── middleware.py        # SkillMiddleware implementation
│   │   └── state.py             # Custom state schema
│   │
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── registry.py          # Skills registry and loader
│   │   ├── frontend.py          # Frontend skill definition
│   │   ├── backend.py           # Backend skill definition
│   │   ├── database.py          # Database skill definition
│   │   └── network.py           # Network skill definition
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   └── skill_tools.py       # load_skill tool implementation
│   │
│   └── cli/
│       ├── __init__.py
│       └── interface.py         # CLI interaction logic
│
└── examples/
    └── sample_sessions.md       # Example troubleshooting sessions
```

### File Responsibilities

| File               | Responsibility                                            |
| ------------------ | --------------------------------------------------------- |
| `main.py`        | Entry point, initializes agent and starts CLI loop        |
| `agent.py`       | Creates the LangChain agent with model, tools, middleware |
| `middleware.py`  | Injects skill descriptions into system prompt             |
| `state.py`       | Defines custom state schema to track loaded skills        |
| `registry.py`    | Stores all skills, provides lookup functionality          |
| `skill_tools.py` | Implements the `load_skill`tool                         |
| `interface.py`   | Handles CLI input/output, formatting, colors              |

---

## Features

### Core Features

| Feature                                | Description                                      |
| -------------------------------------- | ------------------------------------------------ |
| **Progressive Skill Loading**    | Skills loaded on-demand via `load_skill()`tool |
| **Skill Descriptions in Prompt** | Agent always sees what skills are available      |
| **Conversation Memory**          | Multi-turn conversations with context            |
| **Multi-Skill Sessions**         | Can load multiple skills in one conversation     |
| **Interactive CLI**              | User-friendly terminal interface                 |

### Advanced Features (Optional Extensions)

| Feature                       | Description                                                |
| ----------------------------- | ---------------------------------------------------------- |
| **Skill Tracking**      | State tracks which skills have been loaded                 |
| **Skill Constraints**   | Certain tools only available after loading specific skills |
| **Hierarchical Skills** | Skills can have sub-skills (e.g.,`frontend.react`)       |
| **Skill Search**        | Semantic search across skill content                       |
| **Custom Skills**       | Users can add their own skills                             |

---

## Technical Stack

### Dependencies

| Package                 | Version | Purpose                                |
| ----------------------- | ------- | -------------------------------------- |
| `langchain`           | ^1.0.x  | Agent framework, tools, middleware     |
| `langgraph`           | ^0.4.x  | State management, checkpointing        |
| `langchain-openai`    | ^0.4.x  | OpenAI model integration               |
| `langchain-anthropic` | ^0.4.x  | Anthropic model integration (optional) |
| `python-dotenv`       | ^1.0.x  | Environment variable management        |
| `rich`                | ^13.x   | Beautiful CLI formatting               |

---

## Data Flow

### Single Query Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                                            │
│    "My React app shows a blank white screen in production"              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. MIDDLEWARE INJECTION                                                  │
│    System prompt + skill descriptions added to request                  │
│                                                                          │
│    "You are a troubleshooting assistant.                                │
│     Available skills:                                                    │
│     - frontend: Browser rendering, JavaScript errors...                 │
│     - backend: Server errors, API failures...                           │
│     - database: Query failures, connection issues...                    │
│     - network: DNS, SSL/TLS, CORS..."                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. LLM DECISION                                                          │
│    Agent analyzes query and decides to load frontend skill              │
│                                                                          │
│    Tool Call: load_skill("frontend")                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. SKILL LOADING                                                         │
│    Full frontend troubleshooting guide returned as ToolMessage          │
│                                                                          │
│    "# Frontend Troubleshooting Guide                                    │
│     ## Blank White Screen                                               │
│     This typically indicates:                                           │
│     1. JavaScript error preventing render                               │
│     2. Build configuration issue                                        │
│     3. Environment variable missing..."                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. LLM RESPONSE                                                          │
│    Agent uses loaded skill knowledge to provide specific guidance       │
│                                                                          │
│    "A blank white screen in React production builds usually means:     │
│                                                                          │
│     1. **Check browser console** (F12 → Console tab)                    │
│        Look for JavaScript errors that prevent rendering                │
│                                                                          │
│     2. **Verify environment variables**                                 │
│        React requires REACT_APP_ prefix for env vars...                 │
│                                                                          │
│     3. **Check the build output**                                       │
│        Run `npm run build` locally and look for warnings..."            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. CLI OUTPUT                                                            │
│    Formatted response displayed to user                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

### Multi-Skill Flow

Some issues require multiple skills:

```
User: "My API call fails with CORS error and then the database 
       connection times out"

Agent thinking:
  - CORS error → network skill
  - Database timeout → database skill
  - Need both skills to fully diagnose

Agent actions:
  1. load_skill("network")    → Gets CORS troubleshooting
  2. load_skill("database")   → Gets connection timeout guide
  3. Synthesizes both to provide comprehensive answer
```

---

## Extension Ideas

Once the core project is complete, students can extend it:

### 1. Additional Skills

| Skill           | Description                              |
| --------------- | ---------------------------------------- |
| `docker`      | Container issues, Dockerfile debugging   |
| `kubernetes`  | Pod crashes, networking, resource limits |
| `auth`        | JWT, OAuth, session management           |
| `performance` | Profiling, caching, optimization         |
| `security`    | Vulnerabilities, OWASP, hardening        |

### 2. Hierarchical Skills

```
frontend/
├── react       # React-specific issues
├── vue         # Vue-specific issues
├── css         # CSS debugging
└── bundling    # Webpack, Vite issues
```

### 3. Dynamic Tool Registration

When `database` skill loads, also register:

* `explain_query` - Run EXPLAIN on SQL
* `check_indexes` - Verify index usage

### 4. Skill Search (RAG)

For large skill libraries:

* Embed skill content
* Semantic search to find relevant skills
* Auto-load top matching skills

### 5. Web Interface

Replace CLI with:

* Streamlit dashboard
* FastAPI + React frontend
* Slack bot integration

---

## Summary

This project teaches multi-agent system design through a practical, relatable use case. By building a Web App Troubleshooting Assistant, you will master:

✅ The Skills pattern and progressive disclosure

✅ LangChain agent architecture

✅ Custom middleware development

✅ State management and checkpointing

✅ Tool design and implementation

✅ CLI application development

The skills pattern is used in production systems like **Claude Code** and follows best practices documented by both **LangChain** and  **Anthropic** .

Let's build it! 🚀

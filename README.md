# VibbersBlog

> An ultra-lightweight, MCP-powered headless CMS designed for AI agents to write, edit, and publish blogs or custom pages directly into production.

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.137.1%2B-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiptap.dev/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Supported-orange.svg)](https://modelcontextprotocol.io/)

VibbersBlog bridges the gap between your code repository and your publishing platform. Instead of managing complex admin panels, you equip your favorite AI Agent with the **Model Context Protocol (MCP)** tools provided by this app and let it build your content, templates, or landing pages for you.

---

## Key Architectural Insights

### 1. In-Memory Jinja2 Templates (RAM-Cached)

To achieve extreme speed, VibbersBlog caches templates directly in **RAM** instead of reading raw HTML files from the disk on every page render.

> [!WARNING]
> **Scale Consideration:** While this makes page delivery blisteringly fast, hosting thousands of complex, highly distinct templates on a resource-constrained server (e.g., a 512MB/1GB RAM VPS) will increase idle memory usage. Keep your template collection curated!

### 2. "Everything is a Blog" (Dynamic Routing)

The application handles layouts using two simple concepts:

- **Templates:** Skeleton HTML files containing structure and standard Jinja/template slots (e.g., `{{title}}`, `{{content}}`) but containing no actual post data.
- **Blogs:** The raw content payload. Although named "blogs", a blog instance can be designated as a custom page (using the `is_blog=False` schema flag).

Combined with the wildcard route (`/{slug}`), you can serve anything from conventional blog entries to complex, single-page landing structures.

---

## MCP Tools Exposed

The application registers **10 MCP tools** allowing agents to manage layout and content lifecycle:

- **Templates:** Create, read list, edit, and delete presentation layouts.
- **Content:** Publish blogs, modify text payloads, delete articles, or retrieve page components dynamically.

---

## Getting Started

### 1. Prerequisites

Ensure you have [uv](https://github.com/astral-sh/uv) installed (a fast Python package installer and resolver).

### 2. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/vibbers-blog.git
cd vibbers-blog

# Install dependencies using uv
uv sync

# Configure your database details inside your environment or config file
```

### 3. Running the Server

#### Start the FastAPI Web Engine:

```bash
# Change to the application directory and run Uvicorn
cd app
uvicorn main:app --reload --port 8000
```

#### Start the MCP Agent Server:

In a new terminal window:

```bash
python app/mcp_main.py
```

Now both your public-facing site (FastAPI) and the background agent channel (MCP) are active!

---

## Connecting Your Agent

To hook VibbersBlog up to your development agent (like Claude Desktop, cursor, or custom wrappers), register it in your agent's `mcp.json` file:

```json
{
  "mcpServers": {
    "vibbers_blog": {
      "transport": "streamable-http",
      "url": "http://localhost:6767/mcp"
    }
  }
}
```

Alternatively, paste the snippet above into your workspace chat window and instruct your Agent:

> _"Register this HTTP MCP server to access my website database and templates."_

See [app/mcp_connect.py](file:///C:/Users/balum/Desktop/opinions/app/mcp_connect.py) for a boilerplate implementation on how to connect programmatically using LangChain.

---

## ! Security Notice

> [!CAUTION]
> **Do not deploy this in production as-is.**
> Out of the box, this application has **no authentication layers** guarding either the frontend routes or the raw MCP control socket. Anyone who locates your endpoints can modify your site database. Before deploying to public servers, make sure to add JWT, API Key, or Basic auth middlewares to lock down the endpoints.

---

## What's Next? (v2 Roadmap)

- Add native JWT OAuth2 authentication.
- Role-based access control for tools.

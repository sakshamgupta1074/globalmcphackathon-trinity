## Trinity Chat — Secure Multi‑Agent Assistant with AI Agent IAM (Flask)

Trinity Chat is a groundbreaking, secure, multi‑agent assistant that revolutionizes AI Agent identity and access management using **Descope's advanced IAM APIs**. Built on Flask and Azure OpenAI, it combines multiple specialized agents (Planner and Notifier) with **intelligent scoping restrictions** to understand tasks, create calendar events, and send reminders — all behind an elegant, responsive chat UI with dark mode.

### 🚀 Revolutionary AI Agent Security
- **First-of-its-kind AI Agent IAM**: Using Descope's cutting-edge APIs to implement granular scoping restrictions for autonomous agents
- **Dynamic Permission Boundaries**: Each AI agent operates within precisely defined scopes, preventing unauthorized actions
- **Agent-to-Agent Authentication**: Secure inter-agent communication with role-based access controls
- **Real-time Scope Management**: Dynamic permission adjustment based on user context and task complexity

### Why it matters
- Everyday coordination (meetings, reminders, follow‑ups) is fragmented across apps.
- Trinity unifies this into a single conversation: "Create a calendar event for Friday 3pm, then remind the team."
- **Revolutionary approach**: Our AI agents are secured with enterprise-grade IAM, each operating within carefully scoped permissions using Descope's advanced APIs.
- Under the hood, an agent team plans, executes, and reports back — **securely scoped and transparently audited**.

---

## 🔐 Descope-Powered AI Agent Security Features

### Intelligent Agent Scoping
- **Role-Based Agent Permissions**: Each agent (Planner, Notifier) has specific, Descope-managed access scopes
- **Dynamic Scope Inheritance**: User permissions dynamically cascade to AI agents with appropriate restrictions
- **Cross-Agent Authorization**: Secure handoffs between agents with verified permission boundaries
- **Audit Trail**: Complete visibility into agent actions and permission usage

### Enterprise-Ready IAM for AI
- **Zero-Trust Agent Architecture**: Every AI action requires explicit Descope authorization
- **Contextual Permission Scaling**: Agent capabilities adapt based on user role and data sensitivity
- **Automated Compliance**: Built-in compliance features for AI agent operations
- **Session-Based Agent Tokens**: Temporary, scoped tokens for each AI interaction

---

## Features
- Beautiful chat UI with dark mode, autosizing input, code formatting, copy‑to‑clipboard, and quick suggestion chips
- **🎯 Descope-powered AI Agent IAM**: Industry-first implementation of identity management for autonomous AI agents
- **Granular Agent Scoping**: Each AI agent operates within precisely defined permission boundaries
- Secure auth via Descope and Google OAuth hand‑off for Calendar/Gmail scopes
- Multi‑agent reasoning with Autogen AgentChat (Planner, Notifier) — **all security-scoped via Descope**
- Async Flask endpoint with streaming aggregation for responsive replies
- Azure OpenAI integration via a simple `.env` file
- **Real-time Permission Validation**: Every agent action verified against Descope policies

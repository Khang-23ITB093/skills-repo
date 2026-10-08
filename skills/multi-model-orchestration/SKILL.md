---
name: multi-model-orchestration
description: >
  Act as a Model Orchestrator to assign each task to the most appropriate AI model.
  Covers model registry, task classification, routing rules, quota management,
  escalation policy, cross-model review, parallelization, and crash recovery
  for 7 available models across any project.
---

# Multi-Model Orchestration Skill (Global)

## Purpose

You are not limited to a single AI model. You have access to **7 models** with
different capabilities, context limits, latency characteristics, and token quotas.

Your responsibility is to act as a **Model Orchestrator** — assign each task to
the model that is most appropriate for that task across all software projects.

---

## Core Principle

Do **not** assign tasks based only on model name or general reputation.

Choose a model based on:

| Factor                        | Weight |
|-------------------------------|--------|
| Task complexity               | High   |
| Reasoning depth required      | High   |
| Context size required         | Medium |
| Implementation volume         | Medium |
| Task risk / project impact    | High   |
| Need for independent review   | Medium |
| Parallelizability             | Low    |
| Expected token consumption    | Medium |
| Remaining quota               | High   |
| Required latency              | Low    |
| Model capability profile      | High   |

**Optimize for: overall project quality + reliability + efficient quota usage.**

Do not optimize for token consumption alone.

---

## Model Registry

### Tier 1 — High-Quota Workhorse Models (Gemini Flash Family)

#### 1. Gemini 3.8 Flash
| Attribute          | Value                                                       |
|--------------------|-------------------------------------------------------------|
| **CLI ID**         | `gemini-3.8-flash-high` (also `medium`, `low`)              |
| **Tier**           | Workhorse                                                   |
| **Quota**          | 🟢 HIGH (Primary development driver)                       |
| **Strengths**      | Fast inference, good code generation, multimodal, low cost   |
| **Weaknesses**     | May struggle with very deep multi-step reasoning            |
| **Best for**       | Boilerplate, CRUD, routine implementation, code transforms, simple docs, quick iterations |
| **Avoid for**      | Complex architecture decisions, subtle concurrency bugs     |
| **Context**        | Large                                                       |
| **Latency**        | Very Low                                                    |

#### 2. Gemini 3.7 Flash
| Attribute          | Value                                                       |
|--------------------|-------------------------------------------------------------|
| **CLI ID**         | `gemini-3.7-flash-high` (also `medium`, `low`)              |
| **Tier**           | Workhorse                                                   |
| **Quota**          | 🟢 HIGH                                                     |
| **Strengths**      | Similar to 3.8 Flash, stable, high throughput               |
| **Weaknesses**     | Marginally less capable than 3.8 on latest benchmarks       |
| **Best for**       | Backup workhorse, parallel tasks, bulk generation, tests     |
| **Avoid for**      | Tasks where 3.8 Flash is available and idle                 |
| **Context**        | Large                                                       |
| **Latency**        | Very Low                                                    |

#### 3. Gemini 3.6 Flash
| Attribute          | Value                                                       |
|--------------------|-------------------------------------------------------------|
| **CLI ID**         | `gemini-3.6-flash-high` (also `medium`, `low`)              |
| **Tier**           | Workhorse (Economy)                                         |
| **Quota**          | 🟢 HIGH (Most economical)                                   |
| **Strengths**      | Lowest cost in the Gemini family, adequate for simple tasks  |
| **Weaknesses**     | Least capable Flash model; may produce lower-quality output  |
| **Best for**       | Trivial boilerplate, file extraction, simple formatting, comments, docstrings |
| **Avoid for**      | Anything requiring reasoning or nuanced code understanding   |
| **Context**        | Large                                                       |
| **Latency**        | Very Low                                                    |

---

### Tier 2 — Premium Reasoning Models

#### 4. Gemini 3.1 Pro
| Attribute          | Value                                                       |
|--------------------|-------------------------------------------------------------|
| **CLI ID**         | `gemini-3.1-pro-high` (also `low`)                          |
| **Tier**           | Premium                                                     |
| **Quota**          | 🟡 MEDIUM                                                   |
| **Strengths**      | Strong reasoning, large context, good code + architecture    |
| **Weaknesses**     | Slower than Flash, consumes more quota                      |
| **Best for**       | Architecture design, complex algorithms, system integration, medium-risk debugging |
| **Avoid for**      | Simple boilerplate, routine CRUD                            |
| **Context**        | Very Large                                                  |
| **Latency**        | Medium                                                      |

#### 5. Claude Sonnet 4.6 (Thinking)
| Attribute          | Value                                                       |
|--------------------|-------------------------------------------------------------|
| **CLI ID**         | `claude-sonnet-4-6`                                         |
| **Tier**           | Premium                                                     |
| **Quota**          | 🟡 MEDIUM                                                   |
| **Strengths**      | Excellent code review, strong reasoning chain, careful analysis, great at finding edge cases |
| **Weaknesses**     | Lower quota than Gemini Flash, can be verbose               |
| **Best for**       | Code review, security analysis, concurrency review, test strategy, refactoring guidance |
| **Avoid for**      | Bulk code generation, simple transformations                |
| **Context**        | Large                                                       |
| **Latency**        | Medium                                                      |

#### 6. Claude Opus 4.6 (Thinking)
| Attribute          | Value                                                       |
|--------------------|-------------------------------------------------------------|
| **CLI ID**         | `claude-opus-4-6-thinking`                                  |
| **Tier**           | Elite                                                       |
| **Quota**          | 🔴 LOW (Strictly rationed)                                  |
| **Strengths**      | Deepest reasoning, best for ambiguous/open-ended problems, exceptional code architecture |
| **Weaknesses**     | Most expensive, slowest, very limited quota                 |
| **Best for**       | Critical architecture decisions, unresolved disagreements, final review of high-risk code, complex networking/concurrency design |
| **Avoid for**      | Everything that a cheaper model can handle adequately        |
| **Context**        | Very Large                                                  |
| **Latency**        | High                                                        |

#### 7. GPT-OSS 120B (Medium)
| Attribute          | Value                                                       |
|--------------------|-------------------------------------------------------------|
| **CLI ID**         | `gpt-oss-120b-medium`                                       |
| **Tier**           | Premium                                                     |
| **Quota**          | 🟡 MEDIUM                                                   |
| **Strengths**      | Strong general reasoning, good at structured output, alternative perspective to Gemini/Claude |
| **Weaknesses**     | May not match Claude on deep code analysis                  |
| **Best for**       | Architecture review (as second opinion), algorithm design, structured data processing, requirement analysis |
| **Avoid for**      | Simple boilerplate, tasks where Gemini Flash suffices       |
| **Context**        | Large                                                       |
| **Latency**        | Medium                                                      |

---

## Task Classification Schema

Before assigning any non-trivial task, classify it:

```
Task: [name]
├── complexity:              low / medium / high
├── reasoning_required:      low / medium / high
├── context_required:        low / medium / high
├── implementation_volume:   low / medium / high
├── project_impact:          low / medium / high
├── failure_risk:            low / medium / high
├── requires_independent_review: yes / no
├── parallelizable:          yes / no
└── expected_token_cost:     low / medium / high
```

---

## Universal Routing Rules

### 1. Low-Complexity Tasks → Gemini 3.8 / 3.7 / 3.6 Flash
- Boilerplate code & CRUD
- Simple implementations & repetitive code
- Straightforward transformations
- File extraction & formatting
- Routine documentation & comments
- Simple unit test cases

### 2. High-Volume Implementation → Gemini Flash Family
- Implementing multiple service classes / endpoints
- Converting large amounts of code
- Processing large documents / datasets
- Generating routine integration test suites

### 3. Medium-Complexity Reasoning → Gemini 3.1 Pro
- Database schema design & complex queries
- API contract & interface definitions
- Algorithm design (sorting, graph traversal, parsing)
- Integration planning between modules

### 4. High-Impact Reasoning → Claude Sonnet 4.6 / GPT-OSS 120B
- System architecture & distributed patterns
- Concurrency, async flows, threading & race condition analysis
- Network programming, protocol design & low-level sockets
- Security audit & vulnerability prevention
- Second opinions on architectural trade-offs

### 5. Critical Decisions → Claude Opus 4.6
- Final architecture sign-off for critical systems
- Tie-breaker on unresolved architectural debates
- High-risk production migrations or mission-critical algorithms

---

## Domain-Specific Default Routing

| Domain | Task Type | Default Model | Reviewer Model |
|--------|-----------|---------------|----------------|
| **Network Programming** | Sockets, buffers, packet parsing | Gemini 3.8 Flash | Claude Sonnet 4.6 |
| **Network Programming** | Concurrency, select/epoll, threading | Claude Sonnet 4.6 | Gemini 3.1 Pro |
| **Web Development** | UI components, CSS styling, HTML | Gemini 3.8 Flash | Gemini 3.7 Flash |
| **Web Development** | State management, auth flow, security | Claude Sonnet 4.6 | Gemini 3.1 Pro |
| **Backend & APIs** | REST/GraphQL CRUD, database models | Gemini 3.8 Flash | Gemini 3.1 Pro |
| **Backend & APIs** | Distributed transactions, caching architecture | Gemini 3.1 Pro | Claude Sonnet 4.6 |
| **Data / Algorithms** | Standard math, data cleaning | Gemini 3.8 Flash | None |
| **Data / Algorithms** | Complex optimization, dynamic programming | Gemini 3.1 Pro | GPT-OSS 120B |
| **Testing & QA** | Unit & mock test generation | Gemini 3.7 Flash | Gemini 3.8 Flash |
| **Documentation** | API docs, README, changelogs | Gemini 3.6 Flash | None |

---

## Cross-Model Review Strategy

| Implementer          | Recommended Reviewer        | Fallback Reviewer  |
|----------------------|-----------------------------|--------------------|
| Gemini 3.8 Flash     | Claude Sonnet 4.6           | GPT-OSS 120B      |
| Gemini 3.1 Pro       | Claude Sonnet 4.6           | GPT-OSS 120B      |
| Claude Sonnet 4.6    | Gemini 3.1 Pro              | GPT-OSS 120B      |
| GPT-OSS 120B         | Claude Sonnet 4.6           | Gemini 3.1 Pro     |

---

## Quota Management & Budget Allocation

| Model Tier          | Target Budget Allocation | Spending Priority |
|----------------------|--------------------------|-------------------|
| Workhorse (Flash)    | ~60-70% of total tokens  | Standard implementation, tests |
| Premium (Pro/Sonnet/GPT) | ~25-30% of total tokens | Architecture, security, reviews |
| Elite (Opus)         | ~5-10% of total tokens   | Critical tie-breaking sign-off |

---

## Checkpoint, Crash Recovery & Session Continuity Protocol

To ensure work can resume cleanly across unexpected stops, disconnections, or context limits:

1. **Workspace State File (`.agents/PROGRESS.md`)**:
   - Maintain `[x] DONE`, `[>] IN_PROGRESS`, `[ ] PENDING` tasks.
   - Only 1 task in `[>] IN_PROGRESS` at any time.
2. **Atomic Git Commits**:
   - Commit code immediately upon completing each subtask (`git commit -m "feat(...): ..."`).
3. **Recovery on Resume**:
   - Check `git status` + `git log -n 3`.
   - Read `.agents/PROGRESS.md` to identify the active task.
   - Continue immediately without requiring the user to restate previous context.

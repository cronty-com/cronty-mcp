# FastMCP Server Evaluation Guide

## Overview

The measure of quality of an MCP server is NOT how well it implements tools, but how well those implementations enable LLMs to accomplish real-world tasks.

Create evaluations that test whether LLMs can effectively use your MCP server to answer realistic, complex questions.

---

## Quick Reference

### Evaluation Requirements
- Create 10 human-readable questions
- Questions must be READ-ONLY, INDEPENDENT, NON-DESTRUCTIVE, IDEMPOTENT
- Each question requires multiple tool calls (potentially dozens)
- Answers must be single, verifiable values
- Answers must be STABLE (won't change over time)

### Output Format
```xml
<evaluation>
   <qa_pair>
      <question>Your question here</question>
      <answer>Single verifiable answer</answer>
   </qa_pair>
</evaluation>
```

---

## Question Guidelines

### Core Requirements

1. **Questions MUST be independent**
   - Each question should NOT depend on answers to other questions
   - Should not assume prior operations from other questions

2. **Questions MUST require ONLY NON-DESTRUCTIVE and IDEMPOTENT operations**
   - Should not require modifying state to arrive at the answer
   - Read-only tool usage only
   - Repeated execution must yield the same results

3. **Questions must be REALISTIC, CLEAR, CONCISE, and COMPLEX**
   - Require multiple (potentially dozens of) tool calls
   - Based on real use cases humans would care about

### Complexity and Depth

4. **Questions must require deep exploration**
   - Multi-hop questions requiring sequential tool calls
   - Each step benefits from information found in previous calls

5. **Questions may require extensive paging**
   - Paging through multiple pages of results
   - Querying old data to find niche information
   - The questions must be DIFFICULT

6. **Questions must require deep understanding**
   - Not surface-level knowledge
   - May use True/False format requiring evidence
   - May use multiple-choice where LLM must search different hypotheses

7. **Questions must not be solvable with straightforward keyword search**
   - Don't include specific keywords from target content
   - Use synonyms, related concepts, or paraphrases
   - Require multiple searches and context extraction

### Tool Testing

8. **Questions should stress-test tool return values**
   - May elicit tools returning large objects
   - Require understanding multiple data types:
     - IDs and names
     - Timestamps and datetimes
     - File IDs, names, extensions
     - URLs, etc.

9. **Include ambiguous questions**
   - May require difficult decisions on which tools to call
   - Despite ambiguity, still have a SINGLE VERIFIABLE ANSWER

10. **Questions should MOSTLY reflect real human use cases**
    - Information retrieval tasks that humans assisted by an LLM would care about
    - Not artificial or contrived scenarios

11. **Questions may require dozens of tool calls**
    - This challenges LLMs with limited context
    - Encourages MCP server tools to reduce information returned

### Stability

12. **Answers must NOT change over time**
    - Don't ask about "current state" which is dynamic
    - Don't count things that change (reactions, replies, members)
    - Use historical/completed data

### Challenge

13. **DO NOT let the MCP server RESTRICT the kinds of questions you create**
    - Create challenging and complex questions
    - Some may not be solvable with available MCP server tools
    - Questions may require specific output formats
    - This helps identify gaps in tool coverage

---

## Answer Guidelines

### Verification

1. **Answers must be verifiable via direct string comparison**
   - Specify output format in the question when needed
   - Examples: "Use YYYY/MM/DD.", "Answer True or False.", "Answer A, B, C, or D."

2. **Valid answer types:**
   - User ID, username, display name
   - Channel/project ID or name
   - Message ID, text content
   - URL, title
   - Numerical quantity
   - Timestamp, datetime
   - Boolean (True/False)
   - Email, phone number
   - File ID, filename
   - Multiple choice answer

### Readability

3. **Prefer HUMAN-READABLE formats**
   - Names over opaque IDs (though IDs are acceptable)
   - Datetime over epoch timestamps
   - Yes/No over 1/0

### Stability

4. **Answers must be STABLE**
   - Based on "closed" concepts (ended conversations, completed projects)
   - Fixed time windows insulate from non-stationary answers
   - Context unlikely to change

### Diversity

5. **Answers must be DIVERSE**
   - Different modalities across questions
   - Mix of user info, timestamps, IDs, counts, names

6. **Answers must NOT be complex structures**
   - Not lists of values
   - Not complex objects
   - Single verifiable value only

---

## Evaluation Process

### Step 1: Documentation Inspection

Read the documentation of the target API:
- Understand available endpoints and functionality
- Parallelize this step AS MUCH AS POSSIBLE
- If ambiguity exists, fetch additional information from the web
- Do NOT read the MCP server implementation code

### Step 2: Tool Inspection

List the tools available in your MCP server:
- Understand input/output schemas
- Read docstrings and descriptions
- Do NOT call tools yet at this stage

### Step 3: Developing Understanding

Iterate steps 1 and 2 until you have a good understanding:
- Think about the kinds of tasks you want to create
- Refine your understanding of tool capabilities
- Do NOT read the MCP server implementation code
- Use intuition to create realistic but VERY challenging tasks

### Step 4: Content Exploration

Use the MCP server tools to explore content:
- Use READ-ONLY and NON-DESTRUCTIVE operations only
- Identify specific content for creating questions
- Use `limit` parameter (<10) to avoid overwhelming context
- Use pagination
- Parallelize exploration with independent sub-agents

### Step 5: Task Generation & Verification

Create 10 questions and verify answers:
- Complex, multi-hop questions
- Read-only, independent, idempotent
- Stable answers with diverse types
- Solve each question yourself using the MCP server
- Flag any operations requiring write access
- Remove questions that require destructive operations
- Parallelize solving to avoid running out of context

---

## Output Format

```xml
<evaluation>
   <qa_pair>
      <question>Find the project created in Q2 2024 with the highest number of completed tasks. What is the project name?</question>
      <answer>Website Redesign</answer>
   </qa_pair>
   <qa_pair>
      <question>Search for issues labeled "bug" closed in March 2024. Which user closed the most? Provide their username.</question>
      <answer>sarah_dev</answer>
   </qa_pair>
   <qa_pair>
      <question>Find pull requests modifying /api directory merged in January 2024. How many different contributors?</question>
      <answer>7</answer>
   </qa_pair>
</evaluation>
```

---

## Example Questions

### Good Questions

**Multi-hop requiring deep exploration:**
```xml
<qa_pair>
   <question>Find the repository archived in Q3 2023 that was previously the most forked. What was its primary language?</question>
   <answer>Python</answer>
</qa_pair>
```

Why it's good:
- Requires multiple searches (archived repos, fork counts)
- Historical data (won't change)
- Single verifiable answer

**Requires context without keyword matching:**
```xml
<qa_pair>
   <question>Locate the initiative focused on improving customer onboarding completed in late 2023. What was the project lead's role title?</question>
   <answer>Product Manager</answer>
</qa_pair>
```

Why it's good:
- Doesn't use specific project name
- Requires finding and understanding context
- Based on completed work

**Complex aggregation:**
```xml
<qa_pair>
   <question>Among critical bugs reported in January 2024, which assignee resolved the highest percentage within 48 hours? Provide their username.</question>
   <answer>alex_eng</answer>
</qa_pair>
```

Why it's good:
- Requires filtering, grouping, calculation
- Tests timestamp understanding
- Historical data

### Poor Questions

**Answer changes over time:**
```xml
<qa_pair>
   <question>How many open issues are currently assigned to engineering?</question>
   <answer>47</answer>
</qa_pair>
```

Why it's poor: Count will change as issues are created/closed.

**Too easy with keyword search:**
```xml
<qa_pair>
   <question>Find the PR titled "Add authentication feature" - who created it?</question>
   <answer>developer123</answer>
</qa_pair>
```

Why it's poor: Direct keyword match, no exploration needed.

**Ambiguous answer format:**
```xml
<qa_pair>
   <question>List all repositories with Python as primary language.</question>
   <answer>repo1, repo2, repo3</answer>
</qa_pair>
```

Why it's poor: List format, order may vary. Better: "How many repositories have Python as primary language?"

---

## Running Evaluations

The evaluation harness uses FastMCP Client for MCP connections and Claude for answering questions.

### Setup

**Using uv (recommended):**
```bash
cd .claude/skills/fastmcp-builder/scripts
uv sync
export ANTHROPIC_EVAL_API_KEY=your_api_key_here
```

**Using pip:**
```bash
pip install -r requirements.txt
export ANTHROPIC_EVAL_API_KEY=your_api_key_here
```

### Running the Evaluation Script

**Local server (stdio) - run from project root:**
```bash
uv run python .claude/skills/fastmcp-builder/scripts/evaluation.py \
  -c "uv run fastmcp run server.py" \
  evaluation.xml
```

**With working directory:**
```bash
uv run python evaluation.py \
  -c "uv run fastmcp run server.py" \
  --cwd /path/to/project \
  evaluation.xml
```

**HTTP server:**
```bash
uv run python evaluation.py \
  -t http \
  -u https://example.com/mcp \
  evaluation.xml
```

**With custom model and output:**
```bash
uv run python evaluation.py \
  -c "uv run fastmcp run server.py" \
  -m claude-haiku-4-5 \
  -o report.md \
  evaluation.xml
```

### Command-Line Options

```
positional arguments:
  eval_file             Path to evaluation XML file

options:
  -t, --transport       Transport type: stdio or http (default: stdio)
  -c, --command         Command to run server (for stdio)
  --cwd                 Working directory for the server command
  -u, --url             Server URL (for http transport)
  -m, --model           Claude model (default: claude-haiku-4-5)
  -o, --output          Output file for report (default: stdout)
```

### Manual Testing with FastMCP Client

```python
import asyncio
from fastmcp.client import Client
from server import mcp

async def run_evaluation():
    async with Client(transport=mcp) as client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        result = await client.call_tool(
            "search_users",
            {"query": "project lead", "limit": 10}
        )
        print(result)

asyncio.run(run_evaluation())
```

### Evaluation Tips

1. **Think hard before generating tasks**
2. **Parallelize exploration** with independent sub-queries
3. **Focus on realistic use cases**
4. **Create challenging questions** that test limits
5. **Ensure stability** with historical data
6. **Verify answers** by solving them yourself
7. **Iterate and refine** based on findings

---

## Troubleshooting

### Connection Errors

If you get connection errors:
- **stdio**: Verify the server script path is correct
- **http**: Check the URL is accessible
- Ensure required API keys are set in environment variables

### Low Accuracy

If many evaluations fail:
- Review Claude's feedback for each task
- Check if tool descriptions are clear and comprehensive
- Verify input parameters are well-documented
- Consider whether tools return too much or too little data
- Ensure error messages are actionable

### Timeout Issues

If tasks are timing out:
- Use a more capable model
- Check if tools are returning too much data
- Verify pagination is working correctly
- Consider simplifying complex questions

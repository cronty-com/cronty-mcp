# FastMCP Server Evaluation Guide

## Overview

The measure of quality of an MCP server is NOT how well it implements tools, but how well those implementations enable LLMs to accomplish real-world tasks.

Create evaluations that test whether LLMs can effectively use your MCP server to answer realistic, complex questions.

---

## Quick Reference

### Evaluation Requirements
- Create 10 human-readable questions
- Questions must be READ-ONLY, INDEPENDENT, NON-DESTRUCTIVE
- Each question requires multiple tool calls
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

2. **Questions MUST require ONLY NON-DESTRUCTIVE operations**
   - Should not require modifying state to arrive at the answer
   - Read-only tool usage only

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

### Stability

10. **Answers must NOT change over time**
    - Don't ask about "current state" which is dynamic
    - Don't count things that change (reactions, replies, members)
    - Use historical/completed data

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

### Step 1: Tool Inspection

List the tools available in your MCP server:
- Understand input/output schemas
- Read docstrings and descriptions
- Do NOT call tools yet

### Step 2: Content Exploration

Use the MCP server tools to explore content:
- Use READ-ONLY operations only
- Identify specific content for creating questions
- Use `limit` parameter (<10) to avoid overwhelming context
- Use pagination

### Step 3: Question Generation

Create 10 questions following all guidelines:
- Complex, multi-hop
- Read-only, independent
- Stable answers
- Diverse answer types

### Step 4: Answer Verification

Solve each question yourself using the MCP server:
- Verify answers are correct
- Ensure answers are stable
- Remove questions requiring write operations

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

### With FastMCP Test Client

```python
import asyncio
from fastmcp.client import Client
from server import mcp

async def run_evaluation():
    async with Client(transport=mcp) as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Test a specific question
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

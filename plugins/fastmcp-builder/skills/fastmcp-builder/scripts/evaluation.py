#!/usr/bin/env python3
"""
FastMCP Server Evaluation Harness

Evaluates MCP servers by running test questions against them using Claude.
Uses FastMCP Client for MCP connections and Anthropic SDK for Claude integration.

Environment:
    ANTHROPIC_EVAL_API_KEY: Required. API key for Claude evaluation.
    (Uses a separate key from ANTHROPIC_API_KEY to avoid accidental charges
    when using Claude Code with a different billing setup.)

Usage:
    # From scripts directory (recommended)
    cd .claude/skills/fastmcp-builder/scripts
    uv sync
    uv run python evaluation.py -c "uv run fastmcp run server.py" \\
        --cwd /path/to/project evaluation.xml

    # HTTP server
    python evaluation.py -t http -u https://example.com/mcp evaluation.xml

    # With custom model and output
    python evaluation.py -c "uv run fastmcp run server.py" \\
        --cwd /path/to/project -m claude-haiku-4-5 -o report.md evaluation.xml
"""

import argparse
import asyncio
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastmcp import Client

EVAL_API_KEY_VAR = "ANTHROPIC_EVAL_API_KEY"


def load_env_file(cwd: str | None) -> None:
    """Load .env file from cwd (project root) or current directory."""
    if cwd:
        env_path = Path(cwd) / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            return
    load_dotenv()


def get_api_key() -> str:
    """Get API key from environment, with clear error message."""
    import os

    api_key = os.environ.get(EVAL_API_KEY_VAR)
    if not api_key:
        print(
            f"Error: {EVAL_API_KEY_VAR} environment variable not set.\n"
            f"This script uses a separate API key to avoid accidentally charging "
            f"your account when Claude Code is configured with ANTHROPIC_API_KEY.\n"
            f"Set {EVAL_API_KEY_VAR} in your .env file or environment.",
            file=sys.stderr,
        )
        sys.exit(1)
    return api_key


@dataclass
class QAPair:
    question: str
    expected_answer: str


@dataclass
class TaskResult:
    question: str
    expected_answer: str
    actual_answer: str
    correct: bool
    duration: float
    tool_calls: int
    summary: str = ""
    feedback: str = ""


@dataclass
class EvaluationReport:
    results: list[TaskResult] = field(default_factory=list)
    total_duration: float = 0.0
    total_tool_calls: int = 0

    @property
    def accuracy(self) -> float:
        if not self.results:
            return 0.0
        correct = sum(1 for r in self.results if r.correct)
        return correct / len(self.results)


def parse_evaluation_file(path: Path) -> list[QAPair]:
    tree = ET.parse(path)
    root = tree.getroot()

    pairs = []
    for qa_pair in root.findall(".//qa_pair"):
        question_elem = qa_pair.find("question")
        answer_elem = qa_pair.find("answer")

        if question_elem is not None and answer_elem is not None:
            q_text = question_elem.text.strip() if question_elem.text else ""
            a_text = answer_elem.text.strip() if answer_elem.text else ""
            pairs.append(QAPair(question=q_text, expected_answer=a_text))

    return pairs


def convert_mcp_tools_to_claude_format(mcp_tools: list) -> list[dict]:
    claude_tools = []
    for tool in mcp_tools:
        input_schema = tool.inputSchema if hasattr(tool, "inputSchema") else {}
        if not input_schema:
            input_schema = {"type": "object", "properties": {}}

        claude_tools.append(
            {
                "name": tool.name,
                "description": tool.description or f"Tool: {tool.name}",
                "input_schema": input_schema,
            }
        )
    return claude_tools


def create_read_resource_tool(resources: list) -> dict | None:
    if not resources:
        return None

    resource_list = []
    for r in resources:
        uri = r.uri if hasattr(r, "uri") else str(r)
        desc = r.description if hasattr(r, "description") else ""
        resource_list.append(f"  - {uri}: {desc}" if desc else f"  - {uri}")

    description = (
        "Read a resource from the MCP server by URI. "
        "Available resources:\n" + "\n".join(resource_list)
    )

    return {
        "name": "read_resource",
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The URI of the resource to read",
                }
            },
            "required": ["uri"],
        },
    }


def extract_xml_tag(text: str, tag: str) -> str:
    pattern = rf"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""


def normalize_answer(answer: str) -> str:
    return answer.strip().lower()


def check_answer(actual: str, expected: str) -> bool:
    return normalize_answer(actual) == normalize_answer(expected)


SYSTEM_PROMPT = """\
You are evaluating an MCP server by answering questions using available tools.

For each question:
1. Use the available tools to find the answer
2. Think through the problem step by step
3. Make multiple tool calls if needed
4. Provide your final answer in the exact format requested

After finding the answer, you MUST provide your response in this exact format:

<summary>
Brief description of how you found the answer (1-2 sentences)
</summary>

<feedback>
Feedback on the MCP server tools - what worked well, what could be improved
</feedback>

<response>
Your final answer (just the answer value, nothing else)
</response>

IMPORTANT: The <response> tag should contain ONLY the answer value.
If the answer is a username, just put the username. If it's a number, just the number.
"""


async def run_single_evaluation(
    client: Client,
    claude: anthropic.Anthropic,
    qa_pair: QAPair,
    claude_tools: list[dict],
    model: str,
) -> TaskResult:
    start_time = time.time()
    tool_calls = 0

    messages = [{"role": "user", "content": qa_pair.question}]

    while True:
        response = claude.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=claude_tools,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            tool_use_blocks = [
                block for block in response.content if block.type == "tool_use"
            ]

            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for tool_use in tool_use_blocks:
                tool_calls += 1
                try:
                    if tool_use.name == "read_resource":
                        uri = tool_use.input.get("uri", "")
                        result = await client.read_resource(uri)
                        result_content = str(result)
                    else:
                        result = await client.call_tool(tool_use.name, tool_use.input)
                        result_content = str(result)
                except Exception as e:
                    result_content = f"Error calling tool: {e}"

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result_content,
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            text_content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    text_content += block.text

            actual_answer = extract_xml_tag(text_content, "response")
            summary = extract_xml_tag(text_content, "summary")
            feedback = extract_xml_tag(text_content, "feedback")

            duration = time.time() - start_time
            correct = check_answer(actual_answer, qa_pair.expected_answer)

            return TaskResult(
                question=qa_pair.question,
                expected_answer=qa_pair.expected_answer,
                actual_answer=actual_answer,
                correct=correct,
                duration=duration,
                tool_calls=tool_calls,
                summary=summary,
                feedback=feedback,
            )

        else:
            duration = time.time() - start_time
            return TaskResult(
                question=qa_pair.question,
                expected_answer=qa_pair.expected_answer,
                actual_answer="[No response]",
                correct=False,
                duration=duration,
                tool_calls=tool_calls,
                summary="Unexpected stop reason: " + str(response.stop_reason),
                feedback="",
            )


def generate_report(report: EvaluationReport) -> str:
    lines = []
    lines.append("# MCP Server Evaluation Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    correct_count = sum(1 for r in report.results if r.correct)
    total_count = len(report.results)
    avg_duration = report.total_duration / total_count
    avg_tool_calls = report.total_tool_calls / total_count
    acc = f"{report.accuracy:.1%} ({correct_count}/{total_count})"
    lines.append(f"- **Accuracy**: {acc}")
    lines.append(f"- **Total Duration**: {report.total_duration:.1f}s")
    lines.append(f"- **Average Duration**: {avg_duration:.1f}s per task")
    lines.append(f"- **Total Tool Calls**: {report.total_tool_calls}")
    lines.append(f"- **Average Tool Calls**: {avg_tool_calls:.1f} per task")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Results")
    lines.append("")

    for i, result in enumerate(report.results, 1):
        status = "PASS" if result.correct else "FAIL"
        lines.append(f"### Task {i}: {status}")
        lines.append("")
        lines.append(f"**Question**: {result.question}")
        lines.append("")
        lines.append(f"**Expected**: `{result.expected_answer}`")
        lines.append("")
        lines.append(f"**Actual**: `{result.actual_answer}`")
        lines.append("")
        dur = f"{result.duration:.1f}s"
        lines.append(f"**Duration**: {dur} | **Tool Calls**: {result.tool_calls}")
        lines.append("")
        if result.summary:
            lines.append(f"**Summary**: {result.summary}")
            lines.append("")
        if result.feedback:
            lines.append(f"**Feedback**: {result.feedback}")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


async def run_evaluation(
    transport: str,
    command: str | None,
    url: str | None,
    eval_file: Path,
    model: str,
    cwd: str | None,
) -> EvaluationReport:
    qa_pairs = parse_evaluation_file(eval_file)
    if not qa_pairs:
        print("No QA pairs found in evaluation file", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(qa_pairs)} evaluation tasks")

    if transport == "stdio":
        if not command:
            print("Command required for stdio transport (-c)", file=sys.stderr)
            sys.exit(1)
        parts = command.split()
        config = {
            "mcpServers": {
                "eval-server": {
                    "command": parts[0],
                    "args": parts[1:],
                }
            }
        }
        if cwd:
            config["mcpServers"]["eval-server"]["cwd"] = cwd
        mcp_client = Client(config)
    elif transport == "http":
        if not url:
            print("URL required for http transport", file=sys.stderr)
            sys.exit(1)
        mcp_client = Client(url)
    else:
        print(f"Unknown transport: {transport}", file=sys.stderr)
        sys.exit(1)

    claude = anthropic.Anthropic(api_key=get_api_key())

    report = EvaluationReport()

    async with mcp_client:
        mcp_tools = await mcp_client.list_tools()
        claude_tools = convert_mcp_tools_to_claude_format(mcp_tools)
        print(f"Loaded {len(claude_tools)} tools from MCP server")

        try:
            mcp_resources = await mcp_client.list_resources()
            if mcp_resources:
                read_resource_tool = create_read_resource_tool(mcp_resources)
                if read_resource_tool:
                    claude_tools.append(read_resource_tool)
                print(f"Loaded {len(mcp_resources)} resources from MCP server")
        except Exception:
            pass

        for i, qa_pair in enumerate(qa_pairs, 1):
            print(f"\nRunning task {i}/{len(qa_pairs)}...")
            result = await run_single_evaluation(
                mcp_client, claude, qa_pair, claude_tools, model
            )
            report.results.append(result)
            report.total_duration += result.duration
            report.total_tool_calls += result.tool_calls

            status = "PASS" if result.correct else "FAIL"
            dur = f"{result.duration:.1f}s"
            print(f"  {status} ({dur}, {result.tool_calls} tool calls)")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate an MCP server using Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local server (stdio) - run from project root
  python evaluation.py -t stdio -c "uv run fastmcp run server.py" evaluation.xml

  # With working directory
  python evaluation.py -t stdio -c "uv run fastmcp run server.py" \\
      --cwd /path/to/project evaluation.xml

  # HTTP server
  python evaluation.py -t http -u https://example.com/mcp evaluation.xml

  # With custom model and output
  python evaluation.py -t stdio -c "uv run fastmcp run server.py" \\
      -m claude-haiku-4-5 -o report.md evaluation.xml
        """,
    )

    parser.add_argument("eval_file", type=Path, help="Path to evaluation XML file")
    parser.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "-c",
        "--command",
        help="Command to run server (for stdio)",
    )
    parser.add_argument("--cwd", help="Working directory for the server command")
    parser.add_argument("-u", "--url", help="Server URL (for http)")
    parser.add_argument(
        "-m",
        "--model",
        default="claude-haiku-4-5",
        help="Claude model (default: claude-haiku-4-5)",
    )
    parser.add_argument("-o", "--output", type=Path, help="Output file for report")

    args = parser.parse_args()

    load_env_file(args.cwd)

    if not args.eval_file.exists():
        print(f"Evaluation file not found: {args.eval_file}", file=sys.stderr)
        sys.exit(1)

    report = asyncio.run(
        run_evaluation(
            transport=args.transport,
            command=args.command,
            url=args.url,
            eval_file=args.eval_file,
            model=args.model,
            cwd=args.cwd,
        )
    )

    report_text = generate_report(report)

    if args.output:
        args.output.write_text(report_text)
        print(f"\nReport written to: {args.output}")
    else:
        print("\n" + report_text)

    print(f"\nFinal Accuracy: {report.accuracy:.1%}")


if __name__ == "__main__":
    main()


import ast
import operator
import os
import re
from pathlib import Path

from ddgs import DDGS
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted
)
from reportlab.lib.units import inch
from xml.sax.saxutils import escape

from crewai.tools import tool


# Create output directory
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# TOOL 1: WEB SEARCH
# --------------------------------------------------

@tool("Web Search Tool")
def web_search(query: str) -> str:
    """Search the internet for useful information about a topic."""

    try:
        results = DDGS().text(
            query,
            max_results=5
        )

        if not results:
            return "No search results found."

        formatted_results = []

        for item in results:
            formatted_results.append(
                f"Title: {item.get('title', '')}\n"
                f"URL: {item.get('href', '')}\n"
                f"Description: {item.get('body', '')}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"Search failed: {str(e)}"


# --------------------------------------------------
# TOOL 2: CALCULATOR
# --------------------------------------------------

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_calculate(node):
    if isinstance(node, ast.Expression):
        return _safe_calculate(node.body)

    if isinstance(node, ast.Constant):
        if type(node.value) not in (int, float):
            raise ValueError("Only numbers are allowed.")
        return node.value

    if isinstance(node, ast.BinOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operation.")

        left = _safe_calculate(node.left)
        right = _safe_calculate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large.")

        result = operation(left, right)

        if abs(result) > 10**100:
            raise ValueError("Result is too large.")

        return result

    if isinstance(node, ast.UnaryOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operation.")

        return operation(_safe_calculate(node.operand))

    raise ValueError("Invalid mathematical expression.")


@tool("Calculator Tool")
def calculator(expression: str) -> str:
    """Calculate mathematical expressions using basic arithmetic."""

    try:
        if len(expression) > 150:
            return "Expression is too long."

        tree = ast.parse(expression, mode="eval")
        result = _safe_calculate(tree)

        return f"Calculation result: {result}"

    except Exception as e:
        return f"Calculation error: {str(e)}"


# --------------------------------------------------
# TOOL 3: FILE READER
# --------------------------------------------------

@tool("File Reader Tool")
def file_reader(filename: str) -> str:
    """Read a text file from the outputs directory."""

    try:
        safe_name = Path(filename).name
        file_path = OUTPUT_DIR / safe_name

        if not file_path.is_file():
            return "File does not exist."

        if file_path.stat().st_size > 2 * 1024 * 1024:
            return "File is too large to read."

        return file_path.read_text(encoding="utf-8")

    except Exception as e:
        return f"File reading error: {str(e)}"


# --------------------------------------------------
# TOOL 4: FILE WRITER
# --------------------------------------------------

@tool("File Writer Tool")
def file_writer(filename: str, content: str) -> str:
    """Save text content as a file inside the outputs directory."""

    try:
        safe_name = Path(filename).name

        if not safe_name.endswith(".md") and not safe_name.endswith(".txt"):
            return "Only .md and .txt files are allowed."

        if len(content) > 500_000:
            return "Content is too large."

        file_path = OUTPUT_DIR / safe_name

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return f"File successfully saved: {file_path}"

    except Exception as e:
        return f"File writing error: {str(e)}"


# --------------------------------------------------
# TOOL 5: PDF REPORT GENERATOR
# --------------------------------------------------

@tool("PDF Report Generator")
def pdf_generator(filename: str, content: str) -> str:
    """Generate a PDF report from text content and save it in outputs."""

    try:
        safe_name = Path(filename).stem
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", safe_name)

        if not safe_name:
            safe_name = "task_report"

        file_path = OUTPUT_DIR / f"{safe_name}.pdf"

        document = SimpleDocTemplate(
            str(file_path),
            pagesize=A4,
            rightMargin=0.7 * inch,
            leftMargin=0.7 * inch,
            topMargin=0.7 * inch,
            bottomMargin=0.7 * inch
        )

        styles = getSampleStyleSheet()

        story = [
            Paragraph("Task Execution Agent Report", styles["Title"]),
            Spacer(1, 20)
        ]

        for line in content.splitlines():
            if line.strip():
                story.append(
                    Preformatted(
                        escape(line),
                        styles["Code"]
                    )
                )
            else:
                story.append(Spacer(1, 8))

        document.build(story)

        return f"PDF successfully generated: {file_path}"

    except Exception as e:
        return f"PDF generation error: {str(e)}"

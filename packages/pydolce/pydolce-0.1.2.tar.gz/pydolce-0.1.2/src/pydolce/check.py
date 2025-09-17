from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Counter

import rich
from docsig._core import _Messages, runner
from docsig._report import Failed
from docsig.messages import E

from pydolce.client import LLMClient, LLMConfig
from pydolce.config import DolceConfig
from pydolce.parser import (
    CodeSegment,
    CodeSegmentReport,
    DocStatus,
    code_docs_from_path,
)
from pydolce.rules import RULES_FROM_REF, DocRule


def ruled_check_prompts(
    function_code: str,
    rules: list[DocRule],
) -> tuple[str, str]:
    """
    Create system and user prompts for the model to check if docstring follows the defined rules.

    This will NOT check parameters, returns values, or any other section but the
    main description of the docstring.

    This will NOT check for completeness, only for CRITICAL inconsistencies.

    Args:
        function_code: The Python function code to analyze
        existing_docstring: Current docstring (if any)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """

    rules_str = "\n".join(
        f"- {r.ref}: {r.prompt if r.prompt else r.description}" for r in rules
    )
    system_prompt = """You are an expert Python docstring analyzer. Your task is to analyze if a Python function docstring follows a set of defined rules."""

    system_prompt += f"""
Analysis scopes:
- DOCSTRING: The entire docstring, including all sections.
- DESCRIPTION: The main description of the docstring.
- PARAM_DESCRIPTION: The description of each parameter in the docstring.
- RETURN_DESCRIPTION: The description of the return value in the docstring.
- CODE: The actual code of the function.

RULES TO CHECK:
{rules_str}
"""

    system_prompt += """
Go rule by rule, and check if the docstring violates any of them independently of the others. For each rule use only the scope information provided in the rule description to determine if the rule is violated or not.

EXACT OUTPUT FORMAT IN JSON:

```
{
    "status": "[CORRECT/INCORRECT]",
    "issues": [List of specific rules references (DOCXXX) that were violated. Empty if status is CORRECT.]
    "descr": [List of specific descriptions of the issues found, one per issue. No more than one sentence. Empty if status is CORRECT.]
}
```

VERY IMPORTANT: NEVER ADD ANY EXTRA COMENTARY OR DESCRIPTION. STICK TO THE EXACT OUTPUT FORMAT.
"""

    user_prompt = f"""
Check this code:
```python
{function_code.strip()}
```
"""
    return system_prompt, user_prompt


def simple_check_prompts(
    function_code: str,
) -> tuple[str, str]:
    """
    Create system and user prompts for the model to check docstring inconsistency.

    This will NOT check parameters, returns values, or any other section but the
    main description of the docstring.

    This will NOT check for completeness, only for CRITICAL inconsistencies.

    Args:
        function_code: The Python function code to analyze
        existing_docstring: Current docstring (if any)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """

    system_prompt = """You are an expert Python code analyzer specializing in docstring validation. Your task is to analyze if a Python function docstring has critical inconsistencies with the actual code implementation.

ANALYSIS FOCUS:
- Check if the docstring match what the code actually does.
- Completeness is NOT a goal. ONLY check for CRITICAL INCONSISTENCIES.

ONLY analyze the function description. DO NOT analyze the parameters or return value.
If there is something in the code that is NOT mentioned in the docstring, it is NOT an issue.
JUST focus on what is documented, and if it matches the code.

EXACT OUTPUT FORMAT IN JSON:

```
{
"status": "[CORRECT/INCORRECT]",
"issues": [List of specific issues foundm, enumerated, one sentence max per issue. Empty list if no issues.]
}
```

VERY IMPORTANT: DO NOT ADD ANY EXTRA COMENTARY OR DESCRIPTION. STICK TO THE EXACT OUTPUT FORMAT.
"""

    user_prompt = f"""
```python
{function_code.strip()}
```
"""
    return system_prompt, user_prompt


def _extract_json_object(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None

    brace_count = 0
    in_string = False
    escape_next = False

    for i, char in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    return text[start : i + 1]

    return None


def _print_summary(responses: list[CodeSegmentReport]) -> None:
    statuses_count = Counter(resp.status for resp in responses)
    rich.print("\n[bold]Summary:[/bold]")
    if DocStatus.CORRECT in statuses_count:
        rich.print(f"[green]✓ Correct: {statuses_count[DocStatus.CORRECT]}[/green]")
    if DocStatus.INCORRECT in statuses_count:
        rich.print(f"[red]✗ Incorrect: {statuses_count[DocStatus.INCORRECT]}[/red]")


def check_signature(path: Path, docsig_config: dict) -> dict[int, list[Failed]]:
    target = (
        _Messages()
        if docsig_config.get("target") is None
        else [E.from_ref(ref=r) for r in docsig_config["target"]]
    )
    disable = (
        _Messages()
        if docsig_config.get("disable") is None
        else [E.from_ref(ref=r) for r in docsig_config["disable"]]
    )

    _docsig_config = docsig_config.copy()
    _docsig_config["target"] = target
    _docsig_config["disable"] = disable

    failures = runner(
        path,
        **_docsig_config,
    )
    sig_errors = defaultdict(list)
    for failure in failures:
        for error in failure:
            sig_errors[error.lineno].append(error)

    return sig_errors


def check_description(
    codeseg: CodeSegment, llm: LLMClient, rules: list[DocRule]
) -> CodeSegmentReport | None:
    sys_prompt, user_prompt = ruled_check_prompts(
        function_code=codeseg.code, rules=rules
    )
    response = llm.generate(
        prompt=user_prompt,
        system=sys_prompt,
    )

    json_resp_str = _extract_json_object(response)

    if json_resp_str is None:
        rich.print(
            "  [yellow]⚠ Invalid response from model. Ignoring function[/yellow]"
        )
        return None

    json_resp = json.loads(json_resp_str)

    if json_resp["status"] == DocStatus.CORRECT.value:
        return CodeSegmentReport.correct()

    if json_resp["issues"]:
        issues = []
        for i, issue in enumerate(json_resp["issues"]):
            ref_search = re.search(r"DOC\d{3}", issue)
            if ref_search is None:
                # Unknown issue format
                continue

            ref = ref_search[0]
            rule_descr = RULES_FROM_REF.get(ref).description
            issue_descr = (
                json_resp["descr"][i]
                if "descr" in json_resp and len(json_resp["descr"]) > i
                else ""
            )

            issue_str = f"{ref}: {rule_descr}"
            if issue_descr:
                issue_str += f" ({issue_descr})"
            issues.append(issue_str)
        json_resp["issues"] = issues

    return CodeSegmentReport(
        status=DocStatus.INCORRECT,
        issues=json_resp["issues"],
    )


def check(path: str, config: DolceConfig) -> None:
    checkpath = Path(path)

    llm = None
    if config.rule_set.contains_llm_rules():
        llm = LLMClient(LLMConfig.from_dolce_config(config))
        if not llm.test_connection():
            rich.print("[red]✗ Connection failed[/red]")
            return

    reports: list[CodeSegmentReport] = []

    last_path = None
    sig_errors: dict[int, list[Failed]] = {}
    for pair in code_docs_from_path(checkpath):
        if pair.file_path != last_path:
            sig_errors = check_signature(pair.file_path, config.docsig_config or {})
            last_path = pair.file_path
        # if config.ignore_missing and (not pair.doc or pair.doc.strip() == ""):
        #     continue

        loc = f"[blue]{pair.code_path}[/blue]"

        quick_issues = config.rule_set.check(pair)
        if quick_issues:
            rich.print(f"[red][ ERROR ][/red] {loc}")
            report = CodeSegmentReport(
                status=DocStatus.INCORRECT,
                issues=quick_issues,
            )
            for issue in report.issues:
                rich.print(f"[red]  - {issue}[/red]")
            reports.append(report)
            continue

        segment_length = len(pair.code.splitlines())
        curr_errors: list[Failed] = []
        for lineno, error in sig_errors.items():
            if pair.lineno <= lineno < pair.lineno + segment_length:
                curr_errors.extend(error)
        if curr_errors:
            rich.print(f"[red][ ERROR ][/red] {loc}")
            report = CodeSegmentReport(
                status=DocStatus.INCORRECT,
                issues=[f"{issue.ref}: {issue.description}" for issue in curr_errors],
            )
            for issue in report.issues:
                rich.print(f"[red]  - {issue}[/red]")
            reports.append(report)
            continue

        if llm is not None:
            desc_report = check_description(pair, llm, config.rule_set.llm_rules())
            if desc_report is None:
                continue

            if desc_report.status != DocStatus.CORRECT:
                reports.append(desc_report)
                rich.print(f"[red][ ERROR ][/red] {loc}")
                for issue in desc_report.issues:
                    rich.print(f"[red]  - {issue}[/red]")
                continue

        reports.append(CodeSegmentReport.correct())
        rich.print(f"[green][  OK   ][/green] {loc}")

    _print_summary(reports)

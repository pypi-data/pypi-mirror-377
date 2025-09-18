"""
Jest-specific log parser for JavaScript/TypeScript test analysis.

This parser handles Jest test output, test failures, and JavaScript-specific errors.

Copyright (c) 2025 Siarhei Skuratovich
Licensed under the MIT License - see LICENSE file for details
"""

import re
from typing import Any

from .base_parser import BaseFrameworkDetector, BaseFrameworkParser, TestFramework


class JestDetector(BaseFrameworkDetector):
    """Detects Jest-based TypeScript/JavaScript jobs"""

    @property
    def framework(self) -> TestFramework:
        return TestFramework.JEST

    @property
    def priority(self) -> int:
        return 85  # High priority for JS/TS projects

    def detect(self, job_name: str, job_stage: str, trace_content: str) -> bool:
        """Detect Jest test jobs"""
        # Job name patterns
        jest_job_patterns = [
            r"jest",
            r"js.*test",
            r"ts.*test",
            r"javascript.*test",
            r"typescript.*test",
        ]

        if self._check_job_name_patterns(job_name, jest_job_patterns):
            return True

        # Trace content patterns
        jest_trace_patterns = [
            r"Test Suites:.*passed",
            r"Tests:.*passed.*failed",
            r"PASS.*\.test\.(js|ts)",
            r"FAIL.*\.test\.(js|ts)",
            r"Jest CLI Options",
            r"Running tests with Jest",
        ]

        return self._check_trace_content_patterns(trace_content, jest_trace_patterns)


class JestParser(BaseFrameworkParser):
    """Jest-specific log parser for JavaScript/TypeScript tests"""

    @property
    def framework(self) -> TestFramework:
        return TestFramework.JEST

    def parse(self, trace_content: str, **kwargs) -> dict[str, Any]:
        """Parse Jest test output"""
        errors = []
        warnings = []

        # Jest error patterns
        jest_error_patterns = [
            # Test failures
            (r"FAIL\s+(.+\.test\.(js|ts|jsx|tsx))", "Jest Test Failure"),
            # Syntax errors
            (r"SyntaxError:\s+(.+)", "JavaScript Syntax Error"),
            # TypeScript errors
            (r"TS\d+:\s+(.+)", "TypeScript Error"),
            # Module resolution errors
            (r"Cannot find module '(.+)'", "Module Not Found"),
            # Timeout errors
            (r"Test timeout of \d+ms exceeded", "Test Timeout"),
            # Async errors
            (r"Error: expect\(received\)\.(.+)", "Jest Assertion Error"),
        ]

        # Jest warning patterns
        jest_warning_patterns = [
            r"WARNING:\s+(.+)",
            r"DEPRECATED:\s+(.+)",
            r"Jest:\s+(.+deprecated.+)",
        ]

        lines = trace_content.split("\n")
        current_test_file = "unknown"

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Track current test file
            file_match = re.search(
                r"(PASS|FAIL)\s+(.+\.test\.(js|ts|jsx|tsx))", line_stripped
            )
            if file_match:
                current_test_file = file_match.group(2)

            # Check for errors
            for pattern, error_type in jest_error_patterns:
                match = re.search(pattern, line_stripped)
                if match:
                    errors.append(
                        {
                            "test_file": self._extract_test_file(
                                line_stripped, current_test_file
                            ),
                            "test_function": self._extract_test_function(lines, i),
                            "exception_type": error_type,
                            "message": line_stripped,
                            "line_number": i + 1,
                            "has_traceback": self._has_jest_traceback(lines, i),
                            "jest_details": self._extract_jest_details(lines, i),
                        }
                    )

            # Check for warnings
            for pattern in jest_warning_patterns:
                if re.search(pattern, line_stripped):
                    warnings.append(
                        {
                            "message": line_stripped,
                            "line_number": i + 1,
                            "type": "jest_warning",
                        }
                    )

        return self.validate_output(
            {
                "parser_type": "jest",
                "framework": self.framework.value,
                "errors": errors,
                "error_count": len(errors),
                "warnings": warnings,
                "warning_count": len(warnings),
                "summary": self._extract_jest_summary(trace_content),
            }
        )

    def _extract_test_file(self, line: str, current_file: str) -> str:
        """Extract test file from Jest output line"""
        file_match = re.search(r"(.+\.test\.(js|ts|jsx|tsx))", line)
        if file_match:
            return file_match.group(1)
        return current_file

    def _extract_test_function(self, lines: list[str], current_line: int) -> str:
        """Extract test function name from context"""
        # Look for test descriptions in surrounding lines
        for i in range(max(0, current_line - 10), min(len(lines), current_line + 3)):
            line = lines[i].strip()

            # Jest test description patterns
            test_patterns = [
                r"✕\s+(.+)",  # Failed test marker
                r"●\s+(.+)",  # Test suite marker
                r"describe\s*\(\s*['\"](.+)['\"]\s*,",  # describe block
                r"it\s*\(\s*['\"](.+)['\"]\s*,",  # it block
                r"test\s*\(\s*['\"](.+)['\"]\s*,",  # test block
            ]

            for pattern in test_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1)

        return "unknown test"

    def _has_jest_traceback(self, lines: list[str], current_line: int) -> bool:
        """Check if Jest error has stack trace"""
        # Look for stack trace patterns after the error
        for i in range(current_line + 1, min(len(lines), current_line + 10)):
            line = lines[i].strip()
            if re.search(r"at\s+.+\(.+:\d+:\d+\)", line) or re.search(
                r"^\s+\d+\s+\|", line
            ):
                return True
        return False

    def _extract_jest_details(
        self, lines: list[str], current_line: int
    ) -> dict[str, Any]:
        """Extract Jest-specific test details"""
        details = {}

        # Look for test suite and test names
        for i in range(max(0, current_line - 15), min(len(lines), current_line + 5)):
            line = lines[i].strip()

            # Extract suite name
            suite_match = re.search(r"describe\s*\(\s*['\"](.+)['\"]\s*,", line)
            if suite_match:
                details["test_suite"] = suite_match.group(1)

            # Extract expected vs received
            if "Expected:" in line:
                details["expected"] = line.split("Expected:")[-1].strip()
            elif "Received:" in line:
                details["received"] = line.split("Received:")[-1].strip()

            # Extract line numbers from stack traces
            stack_match = re.search(r"at\s+.+\((.+):(\d+):(\d+)\)", line)
            if stack_match:
                details["source_file"] = stack_match.group(1)
                details["source_line"] = int(stack_match.group(2))
                details["source_column"] = int(stack_match.group(3))

        return details

    def _extract_jest_summary(self, trace_content: str) -> dict[str, Any]:
        """Extract Jest test run summary"""
        summary: dict[str, int | str | None] = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "total_suites": 0,
            "passed_suites": 0,
            "failed_suites": 0,
            "time": None,
        }

        # Jest summary patterns
        summary_patterns = [
            (
                r"Tests:\s+(\d+)\s+failed,\s+(\d+)\s+passed,\s+(\d+)\s+total",
                "test_results",
            ),
            (
                r"Test Suites:\s+(\d+)\s+failed,\s+(\d+)\s+passed,\s+(\d+)\s+total",
                "suite_results",
            ),
            (r"Time:\s+([0-9.]+\s*s)", "execution_time"),
        ]

        for pattern, result_type in summary_patterns:
            match = re.search(pattern, trace_content)
            if match and result_type == "test_results":
                summary["failed_tests"] = int(match.group(1))
                summary["passed_tests"] = int(match.group(2))
                summary["total_tests"] = int(match.group(3))
            elif match and result_type == "suite_results":
                summary["failed_suites"] = int(match.group(1))
                summary["passed_suites"] = int(match.group(2))
                summary["total_suites"] = int(match.group(3))
            elif match and result_type == "execution_time":
                summary["time"] = match.group(1)

        return summary

    def _extract_source_file_and_line(
        self, error_message: str, full_log_text: str = "", error_type: str = ""
    ) -> tuple[str | None, int | None]:
        """
        Jest-specific implementation of source file and line number extraction.

        Jest typically provides stack traces in the format:
        "at Object.<anonymous> (/path/to/file.js:42:5)"
        """
        # Jest stack trace patterns
        patterns = [
            # Standard Jest stack trace: "at Object.<anonymous> (/path/to/file.js:42:5)"
            r"at\s+.+\(([^:]+):(\d+):(\d+)\)",
            # Alternative format: "at /path/to/file.js:42:5"
            r"at\s+([^:]+):(\d+):(\d+)",
            # Simple file:line format that might appear in Jest output
            r"([^\s:]+\.(js|ts|jsx|tsx)):(\d+)(?::(\d+))?",
        ]

        # First try to extract from error message
        for pattern in patterns:
            match = re.search(pattern, error_message)
            if match:
                groups = match.groups()
                file_path = groups[0]
                line_number_str = groups[1] if len(groups) > 1 else None

                # Skip node_modules and system paths
                if not any(
                    skip in file_path for skip in ["node_modules", "/usr/", "internal/"]
                ):
                    try:
                        return file_path.strip(), (
                            int(line_number_str) if line_number_str else None
                        )
                    except (ValueError, TypeError):
                        continue

        # If not found in error message, search the full log text
        if full_log_text:
            for pattern in patterns:
                matches = re.findall(pattern, full_log_text)
                for match in matches:
                    file_path = match[0] if isinstance(match, tuple) else match
                    line_number_str = (
                        match[1]
                        if isinstance(match, tuple) and len(match) > 1
                        else None
                    )

                    # Skip system paths
                    if not any(
                        skip in file_path
                        for skip in ["node_modules", "/usr/", "internal/"]
                    ):
                        try:
                            return file_path.strip(), (
                                int(line_number_str) if line_number_str else None
                            )
                        except (ValueError, TypeError):
                            continue

        return None, None

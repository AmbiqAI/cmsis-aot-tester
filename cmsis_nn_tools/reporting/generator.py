"""
Report generator for multiple output formats.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import TestReport, TestResult, TestStatus


class ReportGenerator:
    """Generate test reports in multiple formats."""
    
    def __init__(self, output_dir: Path = Path("reports")):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_reports(self, 
                        report: TestReport, 
                        formats: List[str] = None) -> Dict[str, Path]:
        """
        Generate reports in specified formats.
        
        Args:
            report: TestReport object
            formats: List of formats to generate (json, html, md)
            
        Returns:
            Dictionary mapping format to output file path
        """
        if formats is None:
            formats = ["json", "html", "md"]
        
        generated_files = {}
        
        for format_type in formats:
            if format_type == "json":
                file_path = self._generate_json_report(report)
                generated_files["json"] = file_path
            elif format_type == "html":
                file_path = self._generate_html_report(report)
                generated_files["html"] = file_path
            elif format_type == "md":
                file_path = self._generate_markdown_report(report)
                generated_files["md"] = file_path
        
        return generated_files
    
    def _generate_json_report(self, report: TestReport) -> Path:
        """Generate JSON report."""
        timestamp = report.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{report.cpu}_{timestamp}.json"
        file_path = self.output_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        return file_path
    
    def _generate_html_report(self, report: TestReport) -> Path:
        """Generate HTML report."""
        timestamp = report.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{report.cpu}_{timestamp}.html"
        file_path = self.output_dir / filename
        
        html_content = self._create_html_content(report)
        
        with open(file_path, 'w') as f:
            f.write(html_content)
        
        return file_path
    
    def _generate_markdown_report(self, report: TestReport) -> Path:
        """Generate Markdown report."""
        timestamp = report.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{report.cpu}_{timestamp}.md"
        file_path = self.output_dir / filename
        
        md_content = self._create_markdown_content(report)
        
        with open(file_path, 'w') as f:
            f.write(md_content)
        
        return file_path
    
    def _create_html_content(self, report: TestReport) -> str:
        """Create HTML content for the report."""
        status_counts = report.get_status_counts()
        failed_tests = report.get_failed_tests()
        passed_tests = report.get_passed_tests()
        skipped_tests = report.get_skipped_tests()
        
        # Calculate percentages
        total = report.total_tests
        pass_rate = (status_counts["passed"] / total * 100) if total > 0 else 0
        fail_rate = (status_counts["failed"] / total * 100) if total > 0 else 0
        skip_rate = (status_counts["skipped"] / total * 100) if total > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CMSIS-NN Test Report - {report.cpu}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .summary-card {{ 
            background-color: #e8f4fd; 
            padding: 15px; 
            border-radius: 5px; 
            text-align: center;
            min-width: 120px;
        }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .skipped {{ background-color: #fff3cd; }}
        .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .results-table th, .results-table td {{ 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left; 
        }}
        .results-table th {{ background-color: #f2f2f2; }}
        .status-pass {{ color: green; font-weight: bold; }}
        .status-fail {{ color: red; font-weight: bold; }}
        .status-skip {{ color: orange; font-weight: bold; }}
        .status-timeout {{ color: purple; font-weight: bold; }}
        .status-error {{ color: darkred; font-weight: bold; }}
        .failure-details {{ 
            background-color: #f8f9fa; 
            padding: 10px; 
            border-left: 4px solid #dc3545;
            margin: 5px 0;
        }}
        .expandable {{ cursor: pointer; }}
        .hidden {{ display: none; }}
    </style>
    <script>
        function toggleDetails(testName) {{
            var details = document.getElementById('details-' + testName);
            details.classList.toggle('hidden');
        }}
    </script>
</head>
<body>
    <div class="header">
        <h1>CMSIS-NN Test Report</h1>
        <p><strong>CPU:</strong> {report.cpu}</p>
        <p><strong>Run ID:</strong> {report.run_id}</p>
        <p><strong>Start Time:</strong> {report.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Duration:</strong> {report.duration:.2f} seconds</p>
        <p><strong>Summary:</strong> {report.summary}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card passed">
            <h3>{status_counts["passed"]}</h3>
            <p>Passed<br>({pass_rate:.1f}%)</p>
        </div>
        <div class="summary-card failed">
            <h3>{status_counts["failed"]}</h3>
            <p>Failed<br>({fail_rate:.1f}%)</p>
        </div>
        <div class="summary-card skipped">
            <h3>{status_counts["skipped"]}</h3>
            <p>Skipped<br>({skip_rate:.1f}%)</p>
        </div>
    </div>
    
    <h2>Test Results</h2>
    <table class="results-table">
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Duration (s)</th>
                <th>Failure Reason</th>
                <th>Details</th>
            </tr>
        </thead>
        <tbody>
"""
        
        # Add test results
        for result in report.results:
            status_class = f"status-{result.status.value.lower()}"
            failure_reason = result.failure_reason or result.skip_reason or ""
            
            html += f"""
            <tr>
                <td>{result.test_name}</td>
                <td class="{status_class}">{result.status.value}</td>
                <td>{result.duration:.2f}</td>
                <td>{failure_reason}</td>
                <td>
                    <button class="expandable" onclick="toggleDetails('{result.test_name}')">
                        Show Details
                    </button>
                </td>
            </tr>
            <tr id="details-{result.test_name}" class="hidden">
                <td colspan="5">
                    <div class="failure-details">
                        <p><strong>ELF Path:</strong> {result.elf_path}</p>
                        <p><strong>Timestamp:</strong> {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
            
            if result.cycles:
                html += f"<p><strong>Cycles:</strong> {result.cycles:,}</p>"
            if result.memory_usage:
                html += f"<p><strong>Memory Usage:</strong> {result.memory_usage:,} bytes</p>"
            if result.exit_code is not None:
                html += f"<p><strong>Exit Code:</strong> {result.exit_code}</p>"
            
            if result.output_lines:
                html += "<p><strong>Output:</strong></p><pre>"
                for line in result.output_lines[:20]:  # Limit output
                    html += f"{line}\n"
                if len(result.output_lines) > 20:
                    html += "... (truncated)"
                html += "</pre>"
            
            html += """
                    </div>
                </td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
</body>
</html>
"""
        return html
    
    def _create_markdown_content(self, report: TestReport) -> str:
        """Create Markdown content for the report."""
        status_counts = report.get_status_counts()
        failed_tests = report.get_failed_tests()
        passed_tests = report.get_passed_tests()
        skipped_tests = report.get_skipped_tests()
        
        # Calculate percentages
        total = report.total_tests
        pass_rate = (status_counts["passed"] / total * 100) if total > 0 else 0
        fail_rate = (status_counts["failed"] / total * 100) if total > 0 else 0
        skip_rate = (status_counts["skipped"] / total * 100) if total > 0 else 0
        
        md = f"""# CMSIS-NN Test Report

## Summary

- **CPU:** {report.cpu}
- **Run ID:** {report.run_id}
- **Start Time:** {report.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Duration:** {report.duration:.2f} seconds
- **Total Tests:** {report.total_tests}

## Results Overview

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Passed | {status_counts["passed"]} | {pass_rate:.1f}% |
| ❌ Failed | {status_counts["failed"]} | {fail_rate:.1f}% |
| ⏭️ Skipped | {status_counts["skipped"]} | {skip_rate:.1f}% |
"""
        
        if status_counts["timed_out"] > 0:
            timeout_rate = (status_counts["timed_out"] / total * 100)
            md += f"| ⏰ Timed Out | {status_counts['timed_out']} | {timeout_rate:.1f}% |\n"
        
        if status_counts["errors"] > 0:
            error_rate = (status_counts["errors"] / total * 100)
            md += f"| 💥 Errors | {status_counts['errors']} | {error_rate:.1f}% |\n"
        
        md += "\n## Test Results\n\n"
        
        # Add summary table
        md += "| Test Name | Status | Duration (s) | Failure Reason |\n"
        md += "|-----------|--------|--------------|----------------|\n"
        
        for result in report.results:
            status_emoji = {
                TestStatus.PASS: "✅",
                TestStatus.FAIL: "❌", 
                TestStatus.SKIP: "⏭️",
                TestStatus.TIMEOUT: "⏰",
                TestStatus.ERROR: "💥"
            }.get(result.status, "❓")
            
            failure_reason = result.failure_reason or result.skip_reason or ""
            md += f"| {result.test_name} | {status_emoji} {result.status.value} | {result.duration:.2f} | {failure_reason} |\n"
        
        # Add detailed failure information
        if failed_tests:
            md += "\n## Failed Tests Details\n\n"
            for result in failed_tests:
                md += f"### {result.test_name}\n\n"
                md += f"- **Status:** {result.status.value}\n"
                md += f"- **Duration:** {result.duration:.2f} seconds\n"
                md += f"- **ELF Path:** `{result.elf_path}`\n"
                md += f"- **Timestamp:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                if result.cycles:
                    md += f"- **Cycles:** {result.cycles:,}\n"
                if result.memory_usage:
                    md += f"- **Memory Usage:** {result.memory_usage:,} bytes\n"
                if result.exit_code is not None:
                    md += f"- **Exit Code:** {result.exit_code}\n"
                
                if result.failure_reason:
                    md += f"- **Failure Reason:** {result.failure_reason}\n"
                
                if result.output_lines:
                    md += "\n**Output:**\n```\n"
                    for line in result.output_lines[:30]:  # Limit output
                        md += f"{line}\n"
                    if len(result.output_lines) > 30:
                        md += "... (truncated)\n"
                    md += "```\n\n"
        
        return md

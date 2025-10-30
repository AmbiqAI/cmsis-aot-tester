"""
Report storage and retrieval functionality.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import TestReport, TestResult, TestStatus


class ReportStorage:
    """Handle storage and retrieval of test reports."""
    
    def __init__(self, reports_dir: Path = Path("reports")):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    def save_report(self, report: TestReport) -> Path:
        """
        Save a test report to disk.
        
        Args:
            report: TestReport to save
            
        Returns:
            Path to saved report file
        """
        timestamp = report.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{report.cpu}_{timestamp}.json"
        file_path = self.reports_dir / filename
        
        with open(file_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        return file_path
    
    def load_report(self, file_path: Path) -> TestReport:
        """
        Load a test report from disk.
        
        Args:
            file_path: Path to report file
            
        Returns:
            TestReport object
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self._dict_to_report(data)
    
    def list_reports(self, cpu: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List available reports.
        
        Args:
            cpu: Filter by CPU type
            limit: Maximum number of reports to return
            
        Returns:
            List of report metadata dictionaries
        """
        reports = []
        
        for file_path in sorted(self.reports_dir.glob("test_report_*.json"), reverse=True):
            if limit > 0 and len(reports) >= limit:
                break
                
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Filter by CPU if specified
                if cpu and data.get('cpu') != cpu:
                    continue
                
                reports.append({
                    'file_path': file_path,
                    'cpu': data.get('cpu', 'unknown'),
                    'start_time': data.get('start_time'),
                    'duration': data.get('duration', 0),
                    'total_tests': data.get('total_tests', 0),
                    'passed': data.get('passed', 0),
                    'failed': data.get('failed', 0),
                    'skipped': data.get('skipped', 0)
                })
            except (json.JSONDecodeError, KeyError):
                continue
        
        return reports
    
    def get_latest_report(self, cpu: Optional[str] = None) -> Optional[TestReport]:
        """
        Get the most recent report.
        
        Args:
            cpu: Filter by CPU type
            
        Returns:
            Latest TestReport or None if no reports found
        """
        reports = self.list_reports(cpu=cpu, limit=1)
        if not reports:
            return None
        
        return self.load_report(reports[0]['file_path'])
    
    def get_report_summary(self, cpu: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """
        Get summary statistics for recent reports.
        
        Args:
            cpu: Filter by CPU type
            days: Number of days to look back
            
        Returns:
            Summary statistics dictionary
        """
        reports = self.list_reports(cpu=cpu, limit=100)  # Get more reports for analysis
        
        # Filter by date
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_reports = []
        
        for report in reports:
            try:
                report_time = datetime.fromisoformat(report['start_time'].replace('Z', '+00:00'))
                if report_time.timestamp() >= cutoff_date:
                    recent_reports.append(report)
            except (ValueError, TypeError):
                continue
        
        if not recent_reports:
            return {
                'total_runs': 0,
                'avg_duration': 0,
                'avg_pass_rate': 0,
                'total_tests': 0,
                'trend': 'no_data'
            }
        
        # Calculate statistics
        total_runs = len(recent_reports)
        total_duration = sum(r['duration'] for r in recent_reports)
        avg_duration = total_duration / total_runs if total_runs > 0 else 0
        
        total_tests = sum(r['total_tests'] for r in recent_reports)
        total_passed = sum(r['passed'] for r in recent_reports)
        avg_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Calculate trend (comparing first half to second half)
        trend = 'stable'
        if len(recent_reports) >= 4:
            mid_point = len(recent_reports) // 2
            first_half = recent_reports[mid_point:]
            second_half = recent_reports[:mid_point]
            
            first_half_pass_rate = sum(r['passed'] for r in first_half) / sum(r['total_tests'] for r in first_half) * 100
            second_half_pass_rate = sum(r['passed'] for r in second_half) / sum(r['total_tests'] for r in second_half) * 100
            
            if second_half_pass_rate > first_half_pass_rate + 5:
                trend = 'improving'
            elif second_half_pass_rate < first_half_pass_rate - 5:
                trend = 'declining'
        
        return {
            'total_runs': total_runs,
            'avg_duration': avg_duration,
            'avg_pass_rate': avg_pass_rate,
            'total_tests': total_tests,
            'trend': trend,
            'date_range': {
                'start': recent_reports[-1]['start_time'] if recent_reports else None,
                'end': recent_reports[0]['start_time'] if recent_reports else None
            }
        }
    
    def cleanup_old_reports(self, keep_days: int = 30) -> int:
        """
        Remove old report files.
        
        Args:
            keep_days: Number of days of reports to keep
            
        Returns:
            Number of files removed
        """
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        removed_count = 0
        
        for file_path in self.reports_dir.glob("test_report_*.json"):
            try:
                # Check file modification time
                if file_path.stat().st_mtime < cutoff_date:
                    file_path.unlink()
                    removed_count += 1
            except OSError:
                continue
        
        return removed_count
    
    def _dict_to_report(self, data: Dict[str, Any]) -> TestReport:
        """Convert dictionary to TestReport object."""
        # Convert results
        results = []
        for result_data in data.get('results', []):
            result = TestResult(
                test_name=result_data['test_name'],
                status=TestStatus(result_data['status']),
                duration=result_data['duration'],
                cpu=result_data['cpu'],
                elf_path=Path(result_data['elf_path']),
                failure_reason=result_data.get('failure_reason'),
                skip_reason=result_data.get('skip_reason'),
                output_lines=result_data.get('output_lines', []),
                timestamp=datetime.fromisoformat(result_data['timestamp']),
                memory_usage=result_data.get('memory_usage'),
                cycles=result_data.get('cycles'),
                exit_code=result_data.get('exit_code'),
                error_type=result_data.get('error_type')
            )
            results.append(result)
        
        # Create report
        report = TestReport(
            run_id=data['run_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            cpu=data['cpu'],
            total_tests=data['total_tests'],
            passed=data['passed'],
            failed=data['failed'],
            skipped=data['skipped'],
            timed_out=data.get('timed_out', 0),
            errors=data.get('errors', 0),
            results=results
        )
        
        return report

"""
Data models for test reporting.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class TestStatus(Enum):
    """Test execution status."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


@dataclass
class TestResult:
    """Individual test result."""
    test_name: str
    status: TestStatus
    duration: float  # seconds
    cpu: str
    elf_path: str
    failure_reason: Optional[str] = None
    skip_reason: Optional[str] = None
    output_lines: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    memory_usage: Optional[int] = None  # bytes
    cycles: Optional[int] = None  # for PMU runs
    exit_code: Optional[int] = None
    error_type: Optional[str] = None  # "assertion", "timeout", "crash", etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "duration": self.duration,
            "cpu": self.cpu,
            "elf_path": str(self.elf_path),
            "failure_reason": self.failure_reason,
            "skip_reason": self.skip_reason,
            "output_lines": self.output_lines,
            "timestamp": self.timestamp.isoformat(),
            "memory_usage": self.memory_usage,
            "cycles": self.cycles,
            "exit_code": self.exit_code,
            "error_type": self.error_type
        }


@dataclass
class TestReport:
    """Complete test run report."""
    run_id: str
    start_time: datetime
    end_time: datetime
    cpu: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    timed_out: int
    errors: int
    results: List[TestResult] = field(default_factory=list)
    summary: str = ""
    duration: float = 0.0
    
    def __post_init__(self):
        """Calculate derived fields after initialization."""
        self.duration = (self.end_time - self.start_time).total_seconds()
        self._generate_summary()
    
    def _generate_summary(self):
        """Generate human-readable summary."""
        total = self.total_tests
        if total == 0:
            self.summary = "No tests executed"
            return
            
        pass_rate = (self.passed / total) * 100
        fail_rate = (self.failed / total) * 100
        skip_rate = (self.skipped / total) * 100
        
        self.summary = (
            f"Tests: {total} total, {self.passed} passed ({pass_rate:.1f}%), "
            f"{self.failed} failed ({fail_rate:.1f}%), {self.skipped} skipped ({skip_rate:.1f}%)"
        )
        
        if self.timed_out > 0:
            timeout_rate = (self.timed_out / total) * 100
            self.summary += f", {self.timed_out} timed out ({timeout_rate:.1f}%)"
            
        if self.errors > 0:
            error_rate = (self.errors / total) * 100
            self.summary += f", {self.errors} errors ({error_rate:.1f}%)"
    
    def get_status_counts(self) -> Dict[str, int]:
        """Get count of tests by status."""
        return {
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "timed_out": self.timed_out,
            "errors": self.errors
        }
    
    def get_failed_tests(self) -> List[TestResult]:
        """Get list of failed tests."""
        return [r for r in self.results if r.status in [TestStatus.FAIL, TestStatus.ERROR, TestStatus.TIMEOUT]]
    
    def get_passed_tests(self) -> List[TestResult]:
        """Get list of passed tests."""
        return [r for r in self.results if r.status == TestStatus.PASS]
    
    def get_skipped_tests(self) -> List[TestResult]:
        """Get list of skipped tests."""
        return [r for r in self.results if r.status == TestStatus.SKIP]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "cpu": self.cpu,
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "timed_out": self.timed_out,
            "errors": self.errors,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
            "duration": self.duration
        }

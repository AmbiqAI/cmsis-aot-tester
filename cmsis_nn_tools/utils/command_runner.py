"""
Command execution utilities.
"""

import subprocess
from pathlib import Path
from typing import List, Optional

from ..core.logger import get_logger


def run_command(
    cmd: List[str], 
    cwd: Optional[Path] = None, 
    check: bool = True, 
    capture_output: bool = False, 
    verbose: bool = False
) -> subprocess.CompletedProcess:
    """
    Run a command with proper error handling and output.
    
    Args:
        cmd: Command to run as list of strings
        cwd: Working directory (default: current directory)
        check: Whether to raise exception on non-zero exit code
        capture_output: Whether to capture stdout/stderr
        verbose: Whether to show command output
        
    Returns:
        CompletedProcess object
        
    Raises:
        subprocess.CalledProcessError: If command fails and check=True
        FileNotFoundError: If command not found
    """
    logger = get_logger(__name__)
    
    if verbose:
        logger.debug(f"Running: {' '.join(cmd)}")
        if cwd:
            logger.debug(f"Directory: {cwd}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=capture_output or not verbose,  # Capture output if not verbose or explicitly requested
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        if (capture_output or not verbose) and e.stdout:
            logger.debug(f"stdout: {e.stdout}")
        if (capture_output or not verbose) and e.stderr:
            logger.debug(f"stderr: {e.stderr}")
        raise
    except FileNotFoundError as e:
        logger.error(f"Command not found: {e}")
        raise

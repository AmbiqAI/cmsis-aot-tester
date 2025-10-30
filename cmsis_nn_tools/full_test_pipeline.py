#!/usr/bin/env python3
"""
Full Test Pipeline - Complete workflow for CMSIS-NN testing.

This script orchestrates the complete test pipeline:
1. Generate TFLite models using pytest (TfliteGenerator)
2. Convert TFLite models to C modules using helia-aot
3. Generate Unity test runners
4. Build for FVP using CMake
5. Run tests on FVP simulator

Usage:
    python3 python_scripts/full_test_pipeline.py [options]

Examples:
    # Run complete pipeline
    python3 python_scripts/full_test_pipeline.py

    # Run with specific filters
    python3 python_scripts/full_test_pipeline.py --op Conv2D --dtype S8

    # Skip generation, only build and run
    python3 python_scripts/full_test_pipeline.py --skip-generation

    # Dry run to see what would be done
    python3 python_scripts/full_test_pipeline.py --dry-run
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_step(step_num: int, total_steps: int, title: str, description: str = ""):
    """Print a formatted step header."""
    print(f"\n{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Step {step_num}/{total_steps}: {title}{Colors.END}")
    if description:
        print(f"{Colors.WHITE}{description}{Colors.END}")
    print(f"{Colors.CYAN}{'='*80}{Colors.END}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


def run_command(cmd: List[str], cwd: Optional[Path] = None, check: bool = True, 
                capture_output: bool = False, verbose: bool = False) -> subprocess.CompletedProcess:
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
    """
    if verbose:
        print(f"{Colors.MAGENTA}Running: {' '.join(cmd)}{Colors.END}")
        if cwd:
            print(f"{Colors.MAGENTA}Directory: {cwd}{Colors.END}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed with exit code {e.returncode}")
        if capture_output and e.stdout:
            print(f"stdout: {e.stdout}")
        if capture_output and e.stderr:
            print(f"stderr: {e.stderr}")
        raise
    except FileNotFoundError as e:
        print_error(f"Command not found: {e}")
        raise


def step1_generate_tflite_models(op_filter: Optional[str] = None, 
                                dtype_filter: Optional[str] = None,
                                limit: Optional[int] = None,
                                verbose: bool = False) -> bool:
    """
    Step 1: Generate TFLite models using pytest.
    
    Returns:
        True if successful, False otherwise
    """
    print_step(1, 5, "Generate TFLite Models", 
               "Generate TensorFlow Lite models using pytest in TfliteGenerator")
    
    tflite_gen_dir = Path("cmsis_nn_tools/tflite_generator")
    if not tflite_gen_dir.exists():
        print_error(f"TfliteGenerator directory not found: {tflite_gen_dir.absolute()}")
        return False
    
    # Build pytest command
    cmd = ["pytest", "test_ops.py::test_generation", "-v"]
    
    # Add filters
    if op_filter:
        cmd.extend(["--op", op_filter])
    if dtype_filter:
        cmd.extend(["--dtype", dtype_filter])
    if limit:
        cmd.extend(["--limit", str(limit)])
    
    try:
        run_command(cmd, cwd=tflite_gen_dir, verbose=verbose)
        print_success("TFLite models generated successfully")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_error(f"Failed to generate TFLite models: {e}")
        return False


def step2_convert_tflite_models(input_dir: Path = Path("GeneratedTests"),
                               verbose: bool = False,
                               dry_run: bool = False) -> bool:
    """
    Step 2: Convert TFLite models to C modules using helia-aot.
    
    Returns:
        True if successful, False otherwise
    """
    print_step(2, 5, "Convert TFLite to C Modules",
               "Convert TensorFlow Lite models to standalone C inference modules")
    
    if not input_dir.exists():
        print_error(f"Input directory not found: {input_dir}")
        return False
    
    # Find all TFLite files
    tflite_files = list(input_dir.rglob("*.tflite"))
    if not tflite_files:
        print_error(f"No TFLite files found in {input_dir}")
        return False
    
    print_info(f"Found {len(tflite_files)} TFLite files to convert")
    
    if dry_run:
        print_info("Dry run mode - would convert the following files:")
        for tflite_file in tflite_files:
            print(f"  - {tflite_file}")
        return True
    
    # Convert each TFLite file
    success_count = 0
    for tflite_file in tflite_files:
        # Determine output directory (same as TFLite file directory)
        output_dir = tflite_file.parent
        
        # Extract module name from filename
        module_name = tflite_file.stem
        
        # Build helia-aot command
        cmd = [
            "helia-aot",
            "convert",
            "--model.path", str(tflite_file),
            "--module.path", str(output_dir),
            "--module.name", module_name,
            "--module.prefix", module_name,
        ]
        
        try:
            if verbose:
                run_command(cmd, verbose=True)
            else:
                run_command(cmd, capture_output=True)
            print_success(f"Converted: {module_name}")
            success_count += 1
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print_error(f"Failed to convert {module_name}: {e}")
            continue
    
    if success_count == 0:
        print_error("No TFLite files were successfully converted")
        return False
    
    print_success(f"Successfully converted {success_count}/{len(tflite_files)} TFLite files")
    return True


def step3_generate_test_runners(root_dir: Path = Path("GeneratedTests"),
                               verbose: bool = False,
                               dry_run: bool = False) -> bool:
    """
    Step 3: Generate Unity test runners.
    
    Returns:
        True if successful, False otherwise
    """
    print_step(3, 5, "Generate Test Runners",
               "Generate Unity test runners for all test directories")
    
    script_path = Path("scripts/generate_test_runners.py")
    if not script_path.exists():
        print_error(f"Test runner script not found: {script_path}")
        return False
    
    # Check if there are any model headers to generate runners for
    model_headers = list(root_dir.rglob("includes-api/*_model.h"))
    if not model_headers:
        print_warning("No model headers found - test runners will be generated after TFLite conversion")
        print_info("This step will be skipped for now and run after conversion")
        return True
    
    # Build command
    cmd = ["python3", str(script_path), "--root", str(root_dir)]
    if verbose:
        cmd.append("--verbose")
    if dry_run:
        cmd.append("--dry-run")
    
    try:
        run_command(cmd, verbose=verbose)
        print_success("Test runners generated successfully")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_error(f"Failed to generate test runners: {e}")
        return False


def step4_build_fvp(cpu: str = "cortex-m55",
                   optimization: str = "-Ofast",
                   jobs: Optional[int] = None,
                   verbose: bool = False,
                   dry_run: bool = False) -> bool:
    """
    Step 4: Build for FVP using CMake.
    
    Returns:
        True if successful, False otherwise
    """
    print_step(4, 5, "Build for FVP",
               f"Build test executables for {cpu} using CMake")
    
    if dry_run:
        print_info("Dry run mode - would build for FVP")
        return True
    
    # Use the existing build_and_run_fvp.py script but only build
    script_path = Path("cmsis_nn_tools/build_and_run_fvp.py")
    if not script_path.exists():
        print_error(f"Build script not found: {script_path}")
        return False
    
    # Build command (only build, don't run)
    # Use CMake definition instead of --opt to avoid argument parsing issues
    cmd = [
        "python3", str(script_path),
        "--cpu", cpu,
        "--cmake-def", f"CMSIS_OPTIMIZATION_LEVEL={optimization}",
        "--no-run",  # Only build, don't run
    ]
    
    if jobs:
        cmd.extend(["--jobs", str(jobs)])
    if not verbose:
        cmd.append("--quiet")
    
    try:
        run_command(cmd, verbose=verbose)
        print_success(f"Successfully built for {cpu}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_error(f"Failed to build for FVP: {e}")
        return False


def step5_run_tests(cpu: str = "cortex-m55",
                   timeout: float = 0.0,
                   fail_fast: bool = True,
                   verbose: bool = False,
                   dry_run: bool = False) -> bool:
    """
    Step 5: Run tests on FVP simulator.
    
    Returns:
        True if all tests passed, False otherwise
    """
    print_step(5, 5, "Run Tests on FVP",
               "Execute test binaries on FVP Corstone-300 simulator")
    
    if dry_run:
        print_info("Dry run mode - would run tests on FVP")
        return True
    
    # Use the existing build_and_run_fvp.py script but only run
    script_path = Path("cmsis_nn_tools/build_and_run_fvp.py")
    if not script_path.exists():
        print_error(f"Build script not found: {script_path}")
        return False
    
    # Build command (only run, don't build)
    cmd = [
        "python3", str(script_path),
        "--cpu", cpu,
        "--no-build",  # Only run, don't build
    ]
    
    if timeout > 0:
        cmd.extend(["--timeout-run", str(timeout)])
    if not fail_fast:
        cmd.append("--no-fail-fast")
    if not verbose:
        cmd.append("--quiet")
    
    try:
        result = run_command(cmd, verbose=verbose)
        print_success("All tests completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Some tests failed (exit code: {e.returncode})")
        return False
    except FileNotFoundError as e:
        print_error(f"Failed to run tests: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Complete CMSIS-NN test pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python3 python_scripts/full_test_pipeline.py

  # Run with specific filters
  python3 python_scripts/full_test_pipeline.py --op Conv2D --dtype S8

  # Skip generation, only build and run
  python3 python_scripts/full_test_pipeline.py --skip-generation

  # Dry run to see what would be done
  python3 python_scripts/full_test_pipeline.py --dry-run
        """
    )
    
    # Pipeline control
    parser.add_argument("--skip-generation", action="store_true",
                       help="Skip TFLite model generation (assume models exist)")
    parser.add_argument("--skip-conversion", action="store_true",
                       help="Skip TFLite to C conversion (assume C modules exist)")
    parser.add_argument("--skip-runners", action="store_true",
                       help="Skip test runner generation (assume runners exist)")
    parser.add_argument("--skip-build", action="store_true",
                       help="Skip FVP build (assume binaries exist)")
    parser.add_argument("--skip-run", action="store_true",
                       help="Skip FVP test execution")
    
    # Generation filters
    parser.add_argument("--op", type=str, default=None,
                       help="Generate only specific operator (e.g., 'Conv2D')")
    parser.add_argument("--dtype", type=str, default=None,
                       help="Generate only specific dtype (e.g., 'S8', 'S16')")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit number of models to generate")
    
    # Build options
    parser.add_argument("--cpu", type=str, default="cortex-m55",
                       help="Target CPU (default: cortex-m55)")
    parser.add_argument("--opt", type=str, default="-Ofast",
                       help="Optimization level (default: -Ofast)")
    parser.add_argument("--jobs", type=int, default=None,
                       help="Parallel build jobs (default: auto)")
    
    # Run options
    parser.add_argument("--timeout", type=float, default=0.0,
                       help="Per-test timeout in seconds (0 = none)")
    parser.add_argument("--no-fail-fast", action="store_true",
                       help="Don't stop on first test failure")
    
    # General options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed output")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without actually doing it")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Reduce output verbosity")
    
    args = parser.parse_args()
    
    # Set verbosity
    verbose = args.verbose and not args.quiet
    dry_run = args.dry_run
    
    # Print header
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("=" * 80)
    print("CMSIS-NN Full Test Pipeline")
    print("=" * 80)
    print(f"{Colors.END}")
    
    if dry_run:
        print_warning("DRY RUN MODE - No actual changes will be made")
    
    # Track overall success
    overall_success = True
    start_time = time.time()
    
    # Step 1: Generate TFLite models
    if not args.skip_generation:
        success = step1_generate_tflite_models(
            op_filter=args.op,
            dtype_filter=args.dtype,
            limit=args.limit,
            verbose=verbose
        )
        if not success:
            overall_success = False
            if not args.no_fail_fast:
                print_error("Stopping due to failure in TFLite generation")
                return 1
    else:
        print_info("Skipping TFLite model generation")
    
    # Step 2: Convert TFLite models
    if not args.skip_conversion and overall_success:
        success = step2_convert_tflite_models(
            input_dir=Path("GeneratedTests"),
            verbose=verbose,
            dry_run=dry_run
        )
        if not success:
            overall_success = False
            if not args.no_fail_fast:
                print_error("Stopping due to failure in TFLite conversion")
                return 1
    else:
        print_info("Skipping TFLite to C conversion")
    
    # Step 3: Generate test runners (first attempt - may skip if no model headers yet)
    if not args.skip_runners and overall_success:
        success = step3_generate_test_runners(
            root_dir=Path("GeneratedTests"),
            verbose=verbose,
            dry_run=dry_run
        )
        if not success:
            overall_success = False
            if not args.no_fail_fast:
                print_error("Stopping due to failure in test runner generation")
                return 1
    else:
        print_info("Skipping test runner generation")
    
    # Step 3.5: Generate test runners after conversion (if not done in step 3)
    if not args.skip_runners and overall_success and not args.skip_conversion:
        # Check if we need to generate runners after conversion
        model_headers = list(Path("GeneratedTests").rglob("includes-api/*_model.h"))
        if not model_headers:
            print_info("Generating test runners after TFLite conversion...")
            success = step3_generate_test_runners(
                root_dir=Path("GeneratedTests"),
                verbose=verbose,
                dry_run=dry_run
            )
            if not success:
                overall_success = False
                if not args.no_fail_fast:
                    print_error("Stopping due to failure in test runner generation")
                    return 1
    
    # Step 4: Build for FVP
    if not args.skip_build and overall_success:
        success = step4_build_fvp(
            cpu=args.cpu,
            optimization=args.opt,
            jobs=args.jobs,
            verbose=verbose,
            dry_run=dry_run
        )
        if not success:
            overall_success = False
            if not args.no_fail_fast:
                print_error("Stopping due to failure in FVP build")
                return 1
    else:
        print_info("Skipping FVP build")
    
    # Step 5: Run tests
    if not args.skip_run and overall_success:
        success = step5_run_tests(
            cpu=args.cpu,
            timeout=args.timeout,
            fail_fast=not args.no_fail_fast,
            verbose=verbose,
            dry_run=dry_run
        )
        if not success:
            overall_success = False
    else:
        print_info("Skipping FVP test execution")
    
    # Print summary
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}Pipeline Summary{Colors.END}")
    print(f"{Colors.CYAN}{'='*80}{Colors.END}")
    
    if overall_success:
        print_success(f"Pipeline completed successfully in {duration:.1f} seconds")
        return 0
    else:
        print_error(f"Pipeline failed after {duration:.1f} seconds")
        return 1


if __name__ == "__main__":
    sys.exit(main())

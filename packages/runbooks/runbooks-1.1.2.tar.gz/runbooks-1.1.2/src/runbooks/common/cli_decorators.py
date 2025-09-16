"""
CLI Decorators for runbooks package - Enterprise CLI Standardization

Provides standard decorators for common CLI options, eliminating code duplication
and ensuring consistent user experience across all runbooks modules.

Following KISS & DRY principles - enhance existing structure without creating complexity.
"""

import click
from functools import wraps
from typing import Callable, Any


def common_aws_options(f: Callable) -> Callable:
    """
    Standard AWS options for all runbooks commands.

    Provides consistent AWS configuration options across all modules:
    - --profile: AWS profile override (highest priority in 3-tier system)
    - --region: AWS region override
    - --dry-run: Safe analysis mode (enterprise default)

    Usage:
        @common_aws_options
        @click.command()
        def my_command(profile, region, dry_run, **kwargs):
            # Your command logic here
    """
    @click.option(
        '--profile',
        help='AWS profile override (highest priority over environment variables)',
        type=str
    )
    @click.option(
        '--region',
        help='AWS region override (default: us-east-1)',
        type=str,
        default='us-east-1'
    )
    @click.option(
        '--dry-run',
        is_flag=True,
        default=True,
        help='Safe analysis mode - no resource modifications (enterprise default)'
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def common_output_options(f: Callable) -> Callable:
    """
    Standard output options for all runbooks commands.

    Provides consistent output formatting and export options:
    - --output-format: JSON, CSV, table, PDF output formats
    - --output-dir: Output directory for generated files
    - --export: Enable multi-format export capability

    Usage:
        @common_output_options
        @click.command()
        def my_command(output_format, output_dir, export, **kwargs):
            # Your command logic here
    """
    @click.option(
        '--output-format',
        type=click.Choice(['json', 'csv', 'table', 'pdf', 'markdown'], case_sensitive=False),
        default='table',
        help='Output format for results display'
    )
    @click.option(
        '--output-dir',
        default='./awso_evidence',
        help='Directory for generated files and evidence packages',
        type=click.Path()
    )
    @click.option(
        '--export',
        is_flag=True,
        help='Enable multi-format export (CSV, JSON, PDF, HTML)'
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def mcp_validation_option(f: Callable) -> Callable:
    """
    MCP validation option for cost optimization and inventory modules.

    Provides MCP (Model Context Protocol) validation capability for enhanced accuracy:
    - --validate: Enable MCP validation with ≥99.5% accuracy target
    - --confidence-threshold: Minimum confidence threshold (default: 99.5%)

    Usage:
        @mcp_validation_option
        @click.command()
        def my_command(validate, confidence_threshold, **kwargs):
            # Your command logic with MCP validation
    """
    @click.option(
        '--validate',
        is_flag=True,
        help='Enable MCP validation for enhanced accuracy (≥99.5% target)'
    )
    @click.option(
        '--confidence-threshold',
        type=float,
        default=99.5,
        help='Minimum confidence threshold for validation (default: 99.5%%)'
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def enterprise_options(f: Callable) -> Callable:
    """
    Enterprise-specific options for multi-account operations.

    Provides enterprise deployment options:
    - --all: Use all available AWS profiles
    - --combine: Combine profiles from same AWS account
    - --approval-required: Require human approval for operations

    Usage:
        @enterprise_options
        @click.command()
        def my_command(all_profiles, combine, approval_required, **kwargs):
            # Your enterprise command logic
    """
    @click.option(
        '--all',
        'all_profiles',
        is_flag=True,
        help='Use all available AWS profiles for multi-account operations'
    )
    @click.option(
        '--combine',
        is_flag=True,
        help='Combine profiles from the same AWS account for unified reporting'
    )
    @click.option(
        '--approval-required',
        is_flag=True,
        default=True,
        help='Require human approval for state-changing operations (enterprise default)'
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def performance_options(f: Callable) -> Callable:
    """
    Performance monitoring options for enterprise operations.

    Provides performance monitoring and optimization options:
    - --performance-target: Target execution time in seconds
    - --timeout: Maximum execution timeout
    - --parallel: Enable parallel processing where supported

    Usage:
        @performance_options
        @click.command()
        def my_command(performance_target, timeout, parallel, **kwargs):
            # Your performance-monitored command
    """
    @click.option(
        '--performance-target',
        type=int,
        default=30,
        help='Target execution time in seconds (enterprise default: 30s)'
    )
    @click.option(
        '--timeout',
        type=int,
        default=300,
        help='Maximum execution timeout in seconds (default: 5 minutes)'
    )
    @click.option(
        '--parallel',
        is_flag=True,
        help='Enable parallel processing for multi-resource operations'
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def all_standard_options(f: Callable) -> Callable:
    """
    Convenience decorator applying all standard options.

    Combines common_aws_options, common_output_options, mcp_validation_option,
    enterprise_options, and performance_options for comprehensive CLI commands.

    Usage:
        @all_standard_options
        @click.command()
        def comprehensive_command(**kwargs):
            # Command with all standard options available
    """
    @performance_options
    @enterprise_options
    @mcp_validation_option
    @common_output_options
    @common_aws_options
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper
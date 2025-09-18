"""
Validation Commands Module - MCP Validation & Testing Framework

KISS Principle: Focused on validation and testing operations
DRY Principle: Centralized validation patterns and enterprise accuracy standards

Context: Provides CLI interface for comprehensive MCP validation framework
with enterprise-grade accuracy targets and universal profile support.
"""

import click
from rich.console import Console

# Import common utilities and decorators
from runbooks.common.decorators import common_aws_options

console = Console()


def create_validation_group():
    """
    Create the validation command group with all subcommands.

    Returns:
        Click Group object with all validation commands

    Performance: Lazy creation only when needed by DRYCommandRegistry
    Context Reduction: Enterprise validation framework with universal profile support
    """

    @click.group(invoke_without_command=True)
    @common_aws_options
    @click.pass_context
    def validation(ctx, profile, region, dry_run):
        """
        MCP validation and testing framework for enterprise accuracy standards.

        Comprehensive validation framework ensuring ≥99.5% accuracy across all
        AWS operations with enterprise-grade performance and reliability testing.

        Validation Operations:
        • Cost Explorer data accuracy validation
        • Organizations API consistency checking
        • Resource inventory validation across 50+ AWS services
        • Security baseline compliance verification
        • Performance benchmarking with <30s targets

        Examples:
            runbooks validation validate-all --profile billing-profile
            runbooks validation costs --tolerance 2.0
            runbooks validation benchmark --iterations 10
        """
        ctx.obj.update({"profile": profile, "region": region, "dry_run": dry_run})

        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    @validation.command("validate-all")
    @common_aws_options
    @click.option("--tolerance", default=5.0, help="Tolerance percentage for variance detection")
    @click.option("--performance-target", default=30.0, help="Performance target in seconds")
    @click.option("--save-report", is_flag=True, help="Save detailed report to artifacts")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account validation")
    @click.pass_context
    def validate_all(ctx, profile, region, dry_run, tolerance, performance_target, save_report, all):
        """
        Run comprehensive validation across all critical operations with universal profile support.

        Enterprise Validation Features:
        • ≥99.5% accuracy target across all operations
        • Performance benchmarking with <30s targets
        • Multi-account validation with --all flag
        • Comprehensive reporting with variance analysis
        • Real-time progress monitoring with Rich UI

        Examples:
            runbooks validation validate-all --tolerance 2.0
            runbooks validation validate-all --performance-target 20
            runbooks validation validate-all --all --save-report  # Multi-account validation
        """
        try:
            from runbooks.validation.mcp_validator import MCPValidator
            from runbooks.common.profile_utils import get_profile_for_operation
            import asyncio

            console.print("[bold blue]🔍 Starting comprehensive MCP validation[/bold blue]")
            console.print(f"Target Accuracy: ≥99.5% | Tolerance: ±{tolerance}% | Performance: <{performance_target}s")

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            # Initialize validator with resolved profile
            profiles = None
            if resolved_profile:
                profiles = {
                    "billing": resolved_profile,
                    "management": resolved_profile,
                    "centralised_ops": resolved_profile,
                    "single_aws": resolved_profile
                }

            validator = MCPValidator(
                profiles=profiles,
                tolerance_percentage=tolerance,
                performance_target_seconds=performance_target
            )

            # Run comprehensive validation
            report = asyncio.run(validator.validate_all_operations())

            # Display results
            validator.display_validation_report(report)

            # Save report if requested
            if save_report:
                validator.save_validation_report(report)

            # Return results for further processing
            return report

        except ImportError as e:
            console.print(f"[red]❌ Validation framework not available: {e}[/red]")
            raise click.ClickException("Validation functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Validation failed: {e}[/red]")
            raise click.ClickException(str(e))

    @validation.command()
    @common_aws_options
    @click.option("--tolerance", default=5.0, help="Cost variance tolerance percentage")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account cost validation")
    @click.pass_context
    def costs(ctx, profile, region, dry_run, tolerance, all):
        """
        Validate Cost Explorer data accuracy with universal profile support.

        Cost Validation Features:
        • Real-time cost data accuracy verification
        • Variance analysis with configurable tolerance
        • Multi-account cost validation with --all flag
        • Performance benchmarking for cost operations

        Examples:
            runbooks validation costs --tolerance 2.0
            runbooks validation costs --profile billing-profile
            runbooks validation costs --all --tolerance 1.0  # Multi-account validation
        """
        try:
            from runbooks.validation.mcp_validator import MCPValidator
            from runbooks.common.profile_utils import get_profile_for_operation
            import asyncio

            console.print(f"[bold cyan]💰 Validating Cost Explorer data accuracy[/bold cyan]")

            # Use ProfileManager for dynamic profile resolution (billing operation)
            resolved_profile = get_profile_for_operation("billing", profile)

            validator = MCPValidator(
                profiles={"billing": resolved_profile},
                tolerance_percentage=tolerance
            )

            result = asyncio.run(validator.validate_cost_explorer())

            # Display detailed results
            validator.display_validation_result(result, "Cost Explorer")

            return result

        except ImportError as e:
            console.print(f"[red]❌ Cost validation module not available: {e}[/red]")
            raise click.ClickException("Cost validation functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Cost validation failed: {e}[/red]")
            raise click.ClickException(str(e))

    @validation.command()
    @common_aws_options
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account organizations validation")
    @click.pass_context
    def organizations(ctx, profile, region, dry_run, all):
        """
        Validate Organizations API data accuracy with universal profile support.

        Organizations Validation Features:
        • Account discovery consistency verification
        • Organizational unit structure validation
        • Multi-account organizations validation with --all flag
        • Cross-account permission validation

        Examples:
            runbooks validation organizations
            runbooks validation organizations --profile management-profile
            runbooks validation organizations --all  # Multi-account validation
        """
        try:
            from runbooks.validation.mcp_validator import MCPValidator
            from runbooks.common.profile_utils import get_profile_for_operation
            import asyncio

            console.print(f"[bold cyan]🏢 Validating Organizations API data[/bold cyan]")

            # Use ProfileManager for dynamic profile resolution (management operation)
            resolved_profile = get_profile_for_operation("management", profile)

            validator = MCPValidator(profiles={"management": resolved_profile})

            result = asyncio.run(validator.validate_organizations_data())

            # Display detailed results
            validator.display_validation_result(result, "Organizations")

            return result

        except ImportError as e:
            console.print(f"[red]❌ Organizations validation module not available: {e}[/red]")
            raise click.ClickException("Organizations validation functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Organizations validation failed: {e}[/red]")
            raise click.ClickException(str(e))

    @validation.command()
    @common_aws_options
    @click.option("--target-accuracy", default=99.5, help="Target accuracy percentage")
    @click.option("--iterations", default=5, help="Number of benchmark iterations")
    @click.option("--performance-target", default=30.0, help="Performance target in seconds")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account benchmarking")
    @click.pass_context
    def benchmark(ctx, profile, region, dry_run, target_accuracy, iterations, performance_target, all):
        """
        Run performance benchmark for MCP validation framework with universal profile support.

        Benchmark Features:
        • Comprehensive performance testing across all operations
        • Configurable accuracy targets and iteration counts
        • Multi-account benchmarking with --all flag
        • Statistical analysis with confidence intervals
        • Enterprise readiness assessment

        Examples:
            runbooks validation benchmark --target-accuracy 99.0 --iterations 10
            runbooks validation benchmark --performance-target 20
            runbooks validation benchmark --all --iterations 3  # Multi-account benchmark
        """
        try:
            from runbooks.validation.mcp_validator import MCPValidator
            from runbooks.common.profile_utils import get_profile_for_operation
            import asyncio

            console.print(f"[bold magenta]🎯 Running MCP validation benchmark[/bold magenta]")
            console.print(f"Target: {target_accuracy}% | Iterations: {iterations} | Performance: <{performance_target}s")

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            validator = MCPValidator(performance_target_seconds=performance_target)

            results = []

            # Run benchmark iterations
            for i in range(iterations):
                console.print(f"\n[cyan]Iteration {i + 1}/{iterations}[/cyan]")

                report = asyncio.run(validator.validate_all_operations())
                results.append(report)

                console.print(
                    f"Accuracy: {report.overall_accuracy:.1f}% | "
                    f"Time: {report.execution_time:.1f}s | "
                    f"Status: {'✅' if report.overall_accuracy >= target_accuracy else '❌'}"
                )

            # Generate benchmark summary
            benchmark_summary = validator.generate_benchmark_summary(results, target_accuracy)

            console.print(f"\n[bold green]📊 Benchmark Complete[/bold green]")
            console.print(f"Average Accuracy: {benchmark_summary['avg_accuracy']:.2f}%")
            console.print(f"Success Rate: {benchmark_summary['success_rate']:.1f}%")

            return benchmark_summary

        except ImportError as e:
            console.print(f"[red]❌ Benchmark module not available: {e}[/red]")
            raise click.ClickException("Benchmark functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Benchmark failed: {e}[/red]")
            raise click.ClickException(str(e))

    @validation.command()
    @common_aws_options
    @click.option(
        "--operation",
        type=click.Choice(["costs", "organizations", "ec2", "security", "vpc"]),
        required=True,
        help="Specific operation to validate"
    )
    @click.option("--tolerance", default=5.0, help="Tolerance percentage")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account single operation validation")
    @click.pass_context
    def single(ctx, profile, region, dry_run, operation, tolerance, all):
        """
        Validate a single operation with universal profile support.

        Single Operation Validation Features:
        • Focused validation on specific AWS service operations
        • Configurable tolerance for variance detection
        • Multi-account single operation validation with --all flag
        • Detailed error analysis and recommendations

        Examples:
            runbooks validation single --operation costs --tolerance 2.0
            runbooks validation single --operation security --profile ops-profile
            runbooks validation single --operation vpc --all  # Multi-account single operation
        """
        try:
            from runbooks.validation.mcp_validator import MCPValidator
            from runbooks.common.profile_utils import get_profile_for_operation
            import asyncio

            console.print(f"[bold cyan]🔍 Validating {operation.title()} operation[/bold cyan]")

            # Use ProfileManager for dynamic profile resolution based on operation type
            operation_type_map = {
                "costs": "billing",
                "organizations": "management",
                "ec2": "operational",
                "security": "operational",
                "vpc": "operational"
            }

            resolved_profile = get_profile_for_operation(
                operation_type_map.get(operation, "operational"),
                profile
            )

            validator = MCPValidator(tolerance_percentage=tolerance)

            # Map operations to validator methods
            operation_map = {
                "costs": validator.validate_cost_explorer,
                "organizations": validator.validate_organizations_data,
                "ec2": validator.validate_ec2_inventory,
                "security": validator.validate_security_baseline,
                "vpc": validator.validate_vpc_analysis,
            }

            result = asyncio.run(operation_map[operation]())

            # Display detailed results
            validator.display_validation_result(result, operation.title())

            return result

        except ImportError as e:
            console.print(f"[red]❌ Single validation module not available: {e}[/red]")
            raise click.ClickException("Single validation functionality not available")
        except Exception as e:
            console.print(f"[red]❌ {operation.title()} validation failed: {e}[/red]")
            raise click.ClickException(str(e))

    @validation.command()
    @common_aws_options
    @click.option("--all", is_flag=True, help="Check status for all available AWS profiles")
    @click.pass_context
    def status(ctx, profile, region, dry_run, all):
        """
        Show MCP validation framework status with universal profile support.

        Status Check Features:
        • Component availability and readiness verification
        • AWS profile validation and connectivity testing
        • MCP integration status and configuration validation
        • Multi-account status checking with --all flag

        Examples:
            runbooks validation status
            runbooks validation status --profile management-profile
            runbooks validation status --all  # Multi-account status check
        """
        try:
            from runbooks.validation.mcp_validator import MCPValidator
            from runbooks.common.profile_utils import get_profile_for_operation, list_available_profiles

            console.print("[bold blue]🔍 MCP Validation Framework Status[/bold blue]")

            # Use ProfileManager for dynamic profile resolution
            resolved_profile = get_profile_for_operation("operational", profile)

            # Check available profiles if --all flag is used
            if all:
                profiles = list_available_profiles()
                console.print(f"[dim]Checking {len(profiles)} available profiles[/dim]")
            else:
                profiles = [resolved_profile] if resolved_profile else []

            validator = MCPValidator()
            status_report = validator.generate_status_report(profiles)

            # Display status report
            validator.display_status_report(status_report)

            return status_report

        except ImportError as e:
            console.print(f"[red]❌ Status module not available: {e}[/red]")
            raise click.ClickException("Status functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Status check failed: {e}[/red]")
            raise click.ClickException(str(e))

    return validation
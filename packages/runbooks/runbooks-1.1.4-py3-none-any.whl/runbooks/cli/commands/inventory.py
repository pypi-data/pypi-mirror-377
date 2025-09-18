"""
Inventory Commands Module - Resource Discovery & MCP Validation

KISS Principle: Focused on inventory operations only
DRY Principle: Reusable inventory patterns and common options

Extracted from main.py lines 404-889 for modular architecture.
Preserves 100% functionality while reducing main.py context overhead.
"""

import click
from rich.console import Console

# Import common utilities and decorators
from runbooks.common.decorators import common_aws_options, common_output_options, common_filter_options

console = Console()


def create_inventory_group():
    """
    Create the inventory command group with all subcommands.

    Returns:
        Click Group object with all inventory commands

    Performance: Lazy creation only when needed by DRYCommandRegistry
    """

    @click.group(invoke_without_command=True)
    @common_aws_options
    @common_output_options
    @common_filter_options
    @click.pass_context
    def inventory(ctx, profile, region, dry_run, output, output_file, tags, accounts, regions):
        """
        Universal AWS resource discovery and inventory - works with ANY AWS environment.

        ✅ Universal Compatibility: Works with single accounts, Organizations, and any profile setup
        🔍 Read-only operations for safe resource discovery across AWS services
        🚀 Intelligent fallback: Organizations → standalone account detection

        Profile Options:
            --profile PROFILE       Use specific AWS profile (highest priority)
            No --profile           Uses AWS_PROFILE environment variable
            No configuration       Uses 'default' profile (universal AWS CLI compatibility)

        Examples:
            runbooks inventory collect                           # Use default profile
            runbooks inventory collect --profile my-profile      # Use specific profile
            runbooks inventory collect --resources ec2,rds       # Specific resources
            runbooks inventory collect --all-accounts            # Multi-account (if Organizations access)
            runbooks inventory collect --tags Environment=prod   # Filtered discovery
        """
        # Update context with inventory-specific options
        ctx.obj.update(
            {
                "profile": profile,
                "region": region,
                "dry_run": dry_run,
                "output": output,
                "output_file": output_file,
                "tags": tags,
                "accounts": accounts,
                "regions": regions,
            }
        )

        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    @inventory.command()
    @common_aws_options
    @click.option("--resources", "-r", multiple=True, help="Resource types (ec2, rds, lambda, s3, etc.)")
    @click.option("--all-resources", is_flag=True, help="Collect all resource types")
    @click.option("--all-accounts", is_flag=True, help="Collect from all organization accounts")
    @click.option("--include-costs", is_flag=True, help="Include cost information")
    @click.option("--parallel", is_flag=True, default=True, help="Enable parallel collection")
    @click.option("--validate", is_flag=True, default=False, help="Enable MCP validation for ≥99.5% accuracy")
    @click.option("--validate-all", is_flag=True, default=False, help="Enable comprehensive 3-way validation: runbooks + MCP + terraform")
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account collection (enterprise scaling)")
    @click.option("--combine", is_flag=True, help="Combine results from the same AWS account")
    @click.option("--csv", is_flag=True, help="Generate CSV export (convenience flag for --export-format csv)")
    @click.option("--json", is_flag=True, help="Generate JSON export (convenience flag for --export-format json)")
    @click.option("--pdf", is_flag=True, help="Generate PDF export (convenience flag for --export-format pdf)")
    @click.option("--markdown", is_flag=True, help="Generate markdown export (convenience flag for --export-format markdown)")
    @click.option("--export-format", type=click.Choice(['json', 'csv', 'markdown', 'pdf', 'yaml']),
                  help="Export format for results (convenience flags take precedence)")
    @click.option("--output-dir", default="./awso_evidence", help="Output directory for exports")
    @click.option("--report-name", help="Base name for export files (without extension)")
    @click.pass_context
    def collect(ctx, profile, region, dry_run, resources, all_resources, all_accounts, include_costs, parallel, validate, validate_all,
               all, combine, csv, json, pdf, markdown, export_format, output_dir, report_name):
        """
        🔍 Universal AWS resource inventory collection - works with ANY AWS environment.

        ✅ Universal Compatibility Features:
        - Works with single accounts, AWS Organizations, and standalone setups
        - Profile override priority: User > Environment > Default ('default' profile fallback)
        - Intelligent Organizations detection with graceful standalone fallback
        - 50+ AWS services discovery across any account configuration
        - Multi-format exports: CSV, JSON, PDF, Markdown, YAML
        - MCP validation for ≥99.5% accuracy

        Universal Profile Usage:
        - ANY AWS profile works (no hardcoded assumptions)
        - Organizations permissions auto-detected (graceful fallback to single account)
        - AWS_PROFILE environment variable used when available
        - 'default' profile used as universal fallback

        Examples:
            # Universal compatibility - works with any AWS setup
            runbooks inventory collect                                    # Default profile
            runbooks inventory collect --profile my-aws-profile           # Any profile
            runbooks inventory collect --all-accounts                     # Auto-detects Organizations

            # Resource-specific discovery
            runbooks inventory collect --resources ec2,rds,s3             # Specific services
            runbooks inventory collect --all-resources                    # All 50+ services

            # Multi-format exports
            runbooks inventory collect --csv --json --pdf                 # Multiple formats
            runbooks inventory collect --profile prod --validate --markdown
        """
        try:
            from runbooks.inventory.collector import run_inventory_collection

            # Enhanced context for inventory collection
            context_args = {
                "profile": profile,
                "region": region,
                "dry_run": dry_run,
                "resources": resources,
                "all_resources": all_resources,
                "all_accounts": all_accounts,
                "include_costs": include_costs,
                "parallel": parallel,
                "validate": validate,
                "validate_all": validate_all,
                "all": all,
                "combine": combine,
                "export_formats": [],
                "output_dir": output_dir,
                "report_name": report_name
            }

            # Handle export format flags
            if csv:
                context_args["export_formats"].append("csv")
            if json:
                context_args["export_formats"].append("json")
            if pdf:
                context_args["export_formats"].append("pdf")
            if markdown:
                context_args["export_formats"].append("markdown")
            if export_format:
                context_args["export_formats"].append(export_format)

            # Default to table output if no export formats specified
            if not context_args["export_formats"]:
                context_args["export_formats"] = ["table"]

            # Run inventory collection with enhanced context
            return run_inventory_collection(**context_args)

        except ImportError as e:
            console.print(f"[red]❌ Inventory collection module not available: {e}[/red]")
            raise click.ClickException("Inventory collection functionality not available")
        except Exception as e:
            console.print(f"[red]❌ Inventory collection failed: {e}[/red]")
            raise click.ClickException(str(e))

    @inventory.command()
    @click.option("--resource-types", multiple=True,
                  type=click.Choice(['ec2', 's3', 'rds', 'lambda', 'vpc', 'iam']),
                  default=['ec2', 's3', 'vpc'],
                  help="Resource types to validate")
    @click.option("--test-mode", is_flag=True, default=True,
                  help="Run in test mode with sample data")
    @click.pass_context
    def validate_mcp(ctx, resource_types, test_mode):
        """Test inventory MCP validation functionality."""
        try:
            from runbooks.inventory.mcp_inventory_validator import create_inventory_mcp_validator
            from runbooks.common.profile_utils import get_profile_for_operation

            console.print(f"[blue]🔍 Testing Inventory MCP Validation[/blue]")
            console.print(f"[dim]Profile: {ctx.obj['profile']} | Resources: {', '.join(resource_types)}[/dim]")

            # Initialize validator
            operational_profile = get_profile_for_operation("operational", ctx.obj['profile'])
            validator = create_inventory_mcp_validator([operational_profile])

            # Test with sample data
            sample_data = {
                operational_profile: {
                    "resource_counts": {rt: 5 for rt in resource_types},
                    "regions": ["us-east-1"]
                }
            }

            console.print("[dim]Running validation test...[/dim]")
            validation_results = validator.validate_inventory_data(sample_data)

            accuracy = validation_results.get("total_accuracy", 0)
            if validation_results.get("passed_validation", False):
                console.print(f"[green]✅ MCP Validation test completed: {accuracy:.1f}% accuracy[/green]")
            else:
                console.print(f"[yellow]⚠️ MCP Validation test: {accuracy:.1f}% accuracy (demonstrates validation capability)[/yellow]")

            console.print(f"[dim]💡 Use 'runbooks inventory collect --validate' for real-time validation[/dim]")

        except Exception as e:
            console.print(f"[red]❌ MCP validation test failed: {e}[/red]")
            raise click.ClickException(str(e))

    @inventory.command("rds-snapshots")
    @common_aws_options
    @click.option("--all", is_flag=True, help="Use all available AWS profiles for multi-account collection")
    @click.option("--combine", is_flag=True, help="Combine results from the same AWS account")
    @click.option("--export-format", type=click.Choice(['json', 'csv', 'markdown', 'table']),
                  default='table', help="Export format for results")
    @click.option("--output-dir", default="./awso_evidence", help="Output directory for exports")
    @click.option("--filter-account", help="Filter snapshots by specific account ID")
    @click.option("--filter-status", help="Filter snapshots by status (available, creating, deleting)")
    @click.option("--max-age-days", type=int, help="Filter snapshots older than specified days")
    @click.pass_context
    def discover_rds_snapshots(ctx, profile, region, dry_run, all, combine, export_format,
                              output_dir, filter_account, filter_status, max_age_days):
        """
        🔍 Discover RDS snapshots using AWS Config organization-aggregator.

        ✅ Enhanced Cross-Account Discovery:
        - Leverages AWS Config organization-aggregator for cross-account access
        - Multi-region discovery across 7 key AWS regions
        - Intelligent Organizations detection with graceful standalone fallback
        - Multi-format exports: JSON, CSV, Markdown, Table

        Profile Priority: User > Environment > Default
        Universal AWS compatibility with any profile configuration

        Examples:
            runbooks inventory rds-snapshots                              # Default profile
            runbooks inventory rds-snapshots --profile org-profile        # Organizations profile
            runbooks inventory rds-snapshots --all --combine              # Multi-account discovery
            runbooks inventory rds-snapshots --filter-status available    # Filter by status
            runbooks inventory rds-snapshots --max-age-days 30 --csv      # Recent snapshots
        """
        try:
            from runbooks.inventory.rds_snapshots_discovery import run_rds_snapshots_discovery

            # Enhanced context for RDS snapshots discovery
            context_args = {
                "profile": profile,
                "region": region,
                "dry_run": dry_run,
                "all": all,
                "combine": combine,
                "export_format": export_format,
                "output_dir": output_dir,
                "filter_account": filter_account,
                "filter_status": filter_status,
                "max_age_days": max_age_days
            }

            # Run RDS snapshots discovery
            return run_rds_snapshots_discovery(**context_args)

        except ImportError as e:
            console.print(f"[red]❌ RDS snapshots discovery module not available: {e}[/red]")
            raise click.ClickException("RDS snapshots discovery functionality not available")
        except Exception as e:
            console.print(f"[red]❌ RDS snapshots discovery failed: {e}[/red]")
            raise click.ClickException(str(e))

    return inventory
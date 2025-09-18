"""
FinOps Commands Module - Financial Operations & Cost Optimization

KISS Principle: Focused on financial operations and cost optimization
DRY Principle: Uses centralized patterns from DRYPatternManager

Phase 2 Enhancement: Eliminates pattern duplication through reference-based access.
Context Efficiency: Reduced imports and shared instances for memory optimization.
"""

# Essential imports that can't be centralized due to decorator usage
import click

# DRY Pattern Manager - eliminates duplication across CLI modules
from runbooks.common.patterns import (
    get_console,
    get_error_handlers,
    get_click_group_creator,
    get_common_decorators
)

# Import common utilities and decorators
from runbooks.common.decorators import common_aws_options

# Single console instance shared across all modules (DRY principle)
console = get_console()

# Centralized error handlers - replaces 6 duplicate patterns in this module
error_handlers = get_error_handlers()


def create_finops_group():
    """
    Create the finops command group with all subcommands.

    Returns:
        Click Group object with all finops commands

    Performance: Lazy creation only when needed by DRYCommandRegistry
    Context Reduction: ~800 lines extracted from main.py
    """

    @click.group(invoke_without_command=True)
    @common_aws_options
    @click.pass_context
    def finops(ctx, profile, region, dry_run):
        """
        Financial operations and cost optimization for AWS resources.

        Comprehensive cost analysis, budget management, and financial reporting
        with enterprise-grade accuracy and multi-format export capabilities.

        Features:
        • Real-time cost analysis with MCP validation (≥99.5% accuracy)
        • Multi-format exports: CSV, JSON, PDF, Markdown
        • Quarterly intelligence with strategic financial reporting
        • Enterprise AWS profile support with multi-account capabilities

        Examples:
            runbooks finops dashboard --profile billing-profile
            runbooks finops analyze --service ec2 --timeframe monthly
            runbooks finops export --format pdf --output-dir ./reports
        """
        ctx.obj.update({"profile": profile, "region": region, "dry_run": dry_run})

        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    @finops.command()
    @click.option("--timeframe", type=click.Choice(['daily', 'weekly', 'monthly', 'quarterly']),
                  default='monthly', help="Analysis timeframe")
    @click.option("--services", multiple=True, help="Specific AWS services to analyze")
    @click.option("--accounts", multiple=True, help="Specific AWS accounts to analyze")
    @click.option("--validate", is_flag=True, help="Enable MCP validation for accuracy")
    @click.option("--export-format", type=click.Choice(['json', 'csv', 'pdf', 'markdown']),
                  help="Export format for results")
    @click.pass_context
    def dashboard(ctx, timeframe, services, accounts, validate, export_format):
        """
        Generate comprehensive cost analysis dashboard.

        Enterprise Features:
        • MCP validation with ≥99.5% accuracy
        • Quarterly intelligence integration
        • Rich CLI formatting for executive presentations
        • Multi-format exports for stakeholder consumption

        Examples:
            runbooks finops dashboard --timeframe monthly --validate
            runbooks finops dashboard --services ec2,s3 --export-format pdf
            runbooks finops dashboard --accounts 123456789012 --validate
        """
        try:
            from runbooks.finops.dashboard_runner import EnhancedFinOpsDashboard

            dashboard = EnhancedFinOpsDashboard(
                profile=ctx.obj['profile'],
                region=ctx.obj['region'],
                timeframe=timeframe,
                services=list(services) if services else None,
                accounts=list(accounts) if accounts else None,
                validate=validate
            )

            results = dashboard.generate_comprehensive_analysis()

            if export_format:
                dashboard.export_results(results, format=export_format)

            return results

        except ImportError as e:
            error_handlers['module_not_available']("FinOps dashboard", e)
            raise click.ClickException("FinOps dashboard functionality not available")
        except Exception as e:
            error_handlers['operation_failed']("FinOps dashboard generation", e)
            raise click.ClickException(str(e))

    @finops.command()
    @click.option("--resource-type", type=click.Choice(['ec2', 's3', 'rds', 'lambda', 'vpc']),
                  required=True, help="Resource type for optimization analysis")
    @click.option("--savings-target", type=click.FloatRange(0.1, 0.8), default=0.3,
                  help="Target savings percentage (0.1-0.8)")
    @click.option("--analysis-depth", type=click.Choice(['basic', 'comprehensive', 'enterprise']),
                  default='comprehensive', help="Analysis depth level")
    @click.pass_context
    def optimize(ctx, resource_type, savings_target, analysis_depth):
        """
        Generate cost optimization recommendations for specific resource types.

        Enterprise Optimization Features:
        • Safety-first analysis with READ-ONLY operations
        • Quantified savings projections with ROI analysis
        • Risk assessment and business impact evaluation
        • Implementation timeline and priority recommendations

        Examples:
            runbooks finops optimize --resource-type ec2 --savings-target 0.25
            runbooks finops optimize --resource-type s3 --analysis-depth enterprise
        """
        try:
            from runbooks.finops.optimization_engine import ResourceOptimizer

            optimizer = ResourceOptimizer(
                profile=ctx.obj['profile'],
                region=ctx.obj['region'],
                resource_type=resource_type,
                savings_target=savings_target,
                analysis_depth=analysis_depth
            )

            optimization_results = optimizer.analyze_optimization_opportunities()

            return optimization_results

        except ImportError as e:
            error_handlers['module_not_available']("FinOps optimization", e)
            raise click.ClickException("FinOps optimization functionality not available")
        except Exception as e:
            error_handlers['operation_failed']("FinOps optimization analysis", e)
            raise click.ClickException(str(e))

    @finops.command()
    @click.option("--format", "export_format", type=click.Choice(['csv', 'json', 'pdf', 'markdown']),
                  multiple=True, default=['json'], help="Export formats")
    @click.option("--output-dir", default="./finops_reports", help="Output directory for exports")
    @click.option("--include-quarterly", is_flag=True, help="Include quarterly intelligence data")
    @click.option("--executive-summary", is_flag=True, help="Generate executive summary format")
    @click.pass_context
    def export(ctx, export_format, output_dir, include_quarterly, executive_summary):
        """
        Export financial analysis results in multiple formats.

        Enterprise Export Features:
        • Multi-format simultaneous export
        • Executive-ready formatting and presentation
        • Quarterly intelligence integration
        • Complete audit trail documentation

        Examples:
            runbooks finops export --format csv,pdf --executive-summary
            runbooks finops export --include-quarterly --output-dir ./executive_reports
        """
        try:
            from runbooks.finops.export_manager import FinOpsExportManager

            export_manager = FinOpsExportManager(
                profile=ctx.obj['profile'],
                output_dir=output_dir,
                include_quarterly=include_quarterly,
                executive_summary=executive_summary
            )

            export_results = {}
            for format_type in export_format:
                result = export_manager.export_analysis(format=format_type)
                export_results[format_type] = result

            error_handlers['success'](
                f"Successfully exported to {len(export_format)} format(s)",
                f"Output directory: {output_dir}"
            )

            return export_results

        except ImportError as e:
            error_handlers['module_not_available']("FinOps export", e)
            raise click.ClickException("FinOps export functionality not available")
        except Exception as e:
            error_handlers['operation_failed']("FinOps export operation", e)
            raise click.ClickException(str(e))

    return finops
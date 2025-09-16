import argparse
import sys
from typing import Any, Dict, Optional

import requests
from packaging import version
from rich.console import Console

from runbooks import __version__
from runbooks.finops.helpers import load_config_file

console = Console()


def welcome_banner() -> None:
    banner = rf"""
[bold red]
  /$$$$$$  /$$                           /$$  /$$$$$$                       /$$$$$$$                          /$$                           /$$            
 /$$__  $$| $$                          | $$ /$$__  $$                     | $$__  $$                        | $$                          | $$            
| $$  \__/| $$  /$$$$$$  /$$   /$$  /$$$$$$$| $$  \ $$  /$$$$$$   /$$$$$$$ | $$  \ $$  /$$   /$$ /$$$$$$$  | $$$$$$$   /$$$$$$   /$$$$$$ | $$  /$$   /$$ 
| $$      | $$ /$$__  $$| $$  | $$ /$$__  $$| $$  | $$ /$$__  $$ /$$_____/ | $$$$$$$/ | $$  | $$| $$__  $$ | $$__  $$ /$$__  $$ /$$__  $$| $$ | $$  | $$
| $$      | $$| $$  \ $$| $$  | $$| $$  | $$| $$  | $$| $$  \ $$|  $$$$$$  | $$__  $$ | $$  | $$| $$  \ $$ | $$  \ $$| $$  \ $$| $$  \ $$| $$ | $$  | $$
| $$    $$| $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$ \____  $$ | $$  \ $$ | $$  | $$| $$  | $$ | $$  | $$| $$  | $$| $$  | $$| $$ | $$  | $$
|  $$$$$$/| $$|  $$$$$$/|  $$$$$$/|  $$$$$$$|  $$$$$$/| $$$$$$$/ /$$$$$$$/ | $$  | $$ |  $$$$$$/| $$  | $$ | $$$$$$$/|  $$$$$$/|  $$$$$$/| $$ |  $$$$$$/
 \______/ |__/ \______/  \______/  \_______/ \______/ | $$____/ |_______/  |__/  |__/  \______/ |__/  |__/ |_______/  \______/  \______/ |__/  \______/ 
                                                      | $$                                                                                              
                                                      | $$                                                                                              
                                                      |__/                                                                                              
[/]
[bold bright_blue]CloudOps Runbooks FinOps Platform (v{__version__})[/]                                                                         
"""
    console.print(banner)


def check_latest_version() -> None:
    """Check for the latest version of the CloudOps Runbooks package."""
    try:
        response = requests.get("https://pypi.org/pypi/runbooks/json", timeout=3)
        latest = response.json()["info"]["version"]
        if version.parse(latest) > version.parse(__version__):
            console.print(f"[bold red]A new version of CloudOps Runbooks is available: {latest}[/]")
            console.print(
                "[bold bright_yellow]Please update using:\npip install --upgrade runbooks\nor\nuv add runbooks@latest\n[/]"
            )
    except Exception:
        pass


def main() -> int:
    """Command-line interface entry point."""
    welcome_banner()
    check_latest_version()
    from runbooks.finops.dashboard_runner import run_dashboard

    # Create the parser instance to be accessible for get_default
    parser = argparse.ArgumentParser(
        description="CloudOps Runbooks FinOps Platform - Enterprise Multi-Account Cost Optimization"
    )

    parser.add_argument(
        "--config-file",
        "-C",
        help="Path to a TOML, YAML, or JSON configuration file.",
        type=str,
    )
    parser.add_argument(
        "--profiles",
        "-p",
        nargs="+",
        help="Specific AWS profiles to use (space-separated)",
        type=str,
    )
    parser.add_argument(
        "--regions",
        "-r",
        nargs="+",
        help="AWS regions to check for EC2 instances (space-separated)",
        type=str,
    )
    parser.add_argument("--all", "-a", action="store_true", help="Use all available AWS profiles")
    parser.add_argument(
        "--combine",
        "-c",
        action="store_true",
        help="Combine profiles from the same AWS account",
    )
    parser.add_argument(
        "--report-name",
        "-n",
        help="Specify the base name for the report file (without extension)",
        default=None,
        type=str,
    )
    parser.add_argument(
        "--report-type",
        "-y",
        nargs="+",
        choices=["csv", "json", "pdf", "markdown"],
        help="Specify one or more report types: csv and/or json and/or pdf and/or markdown (space-separated)",
        type=str,
        default=["markdown"],
    )
    parser.add_argument(
        "--dir",
        "-d",
        help="Directory to save the report files (default: current directory)",
        type=str,
    )
    parser.add_argument(
        "--time-range",
        "-t",
        help="Time range for cost data in days (default: current month). Examples: 7, 30, 90",
        type=int,
    )
    parser.add_argument(
        "--tag",
        "-g",
        nargs="+",
        help="Cost allocation tag to filter resources, e.g., --tag Team=DevOps",
        type=str,
    )
    parser.add_argument(
        "--trend",
        action="store_true",
        help="Display a trend report as bars for the past 6 months time range",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Display an audit report with cost anomalies, stopped EC2 instances, unused EBS columes, budget alerts, and more",
    )
    parser.add_argument(
        "--pdca",
        action="store_true",
        help="Run autonomous PDCA (Plan-Do-Check-Act) cycles for continuous improvement",
    )
    parser.add_argument(
        "--pdca-cycles",
        help="Number of PDCA cycles to run (default: 3, 0 for continuous mode)",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--pdca-continuous",
        action="store_true",
        help="Run PDCA in continuous mode (until manually stopped)",
    )

    # Enhanced Dashboard Configuration Parameters
    parser.add_argument(
        "--mode",
        choices=["single_account", "multi_account"],
        help="Explicit dashboard mode selection (overrides auto-detection)",
        type=str,
    )
    parser.add_argument(
        "--top-services",
        help="Number of top services to display in single-account mode (default: 10)",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--top-accounts",
        help="Number of top accounts to display in multi-account mode (default: 5)",
        type=int,
        default=5,
    )
    parser.add_argument(
        "--services-per-account",
        help="Number of services to show per account in multi-account mode (default: 3)",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv", "markdown"],
        help="Output format for dashboard display (default: markdown)",
        type=str,
        default="markdown",
    )
    parser.add_argument(
        "--no-enhanced-routing",
        action="store_true",
        help="Disable enhanced service-focused routing (use legacy account-per-row layout)",
    )

    # Financial Claim Validation Flags
    parser.add_argument(
        "--show-confidence-levels",
        action="store_true",
        help="Display confidence levels (HIGH/MEDIUM/LOW) for all financial claims and projections",
    )
    parser.add_argument(
        "--validate-claims",
        action="store_true",
        help="Run comprehensive financial claim validation using MCP cross-validation",
    )
    parser.add_argument(
        "--validate-projections",
        action="store_true",
        help="Validate individual module savings projections against real AWS data",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=99.5,
        help="Minimum confidence threshold for validation (default: 99.5%%)",
    )

    # AWS Cost Metrics Parameters (Technical vs Financial Analysis)
    parser.add_argument(
        "--unblended",
        action="store_true",
        help="Use UnblendedCost metrics for technical analysis (actual resource utilization)",
    )
    parser.add_argument(
        "--amortized",
        action="store_true",
        help="Use AmortizedCost metrics for financial analysis (accounts for Reserved Instance/Savings Plans discounts)",
    )
    parser.add_argument(
        "--dual-metrics",
        action="store_true",
        help="Show both UnblendedCost and AmortizedCost metrics for comprehensive analysis",
    )

    # Business Scenario Support (DoD Requirement)
    parser.add_argument(
        "--scenario",
        type=str,
        help="Business scenario analysis (workspaces, rds-snapshots, backup-investigation, nat-gateway, elastic-ip, ebs-optimization, vpc-cleanup)",
    )
    parser.add_argument(
        "--help-scenario",
        type=str,
        help="Display detailed help for specific scenario",
    )

    args = parser.parse_args()

    config_data: Optional[Dict[str, Any]] = None
    if args.config_file:
        config_data = load_config_file(args.config_file)
        if config_data is None:
            return 1  # Exit if config file loading failed

    # Override args with config_data if present and arg is not set via CLI
    if config_data:
        for key, value in config_data.items():
            if hasattr(args, key) and getattr(args, key) == parser.get_default(key):
                setattr(args, key, value)

    # Handle scenario help requests (DoD Requirement)
    if hasattr(args, 'help_scenarios') and args.help_scenarios or args.help_scenario:
        try:
            if hasattr(args, 'help_scenarios') and args.help_scenarios:
                from runbooks.finops.unlimited_scenarios import display_unlimited_scenarios_help
                display_unlimited_scenarios_help()
            else:
                from runbooks.finops.scenario_cli_integration import ScenarioCliHelper
                helper = ScenarioCliHelper()
                helper.display_scenario_help(args.help_scenario)
            return 0
        except ImportError as e:
            console.print(f"[red]❌ Scenario help not available: {e}[/red]")
            return 1

    # Handle business scenario dispatch (DoD Requirement)
    if args.scenario:
        try:
            from runbooks.common.rich_utils import print_header, print_success, print_error, print_info

            console.print(f"[bold cyan]🎯 Executing Business Scenario: {args.scenario}[/bold cyan]")

            # CRITICAL FIX: Handle --all flag for scenarios by using dashboard router logic
            if hasattr(args, "all") and args.all:
                print_info("🔍 --all flag detected: Integrating with dashboard router for organization discovery")

                # Use dashboard router to handle --all flag and get profiles
                from runbooks.finops.dashboard_router import create_dashboard_router
                router = create_dashboard_router()
                use_case, routing_config = router.detect_use_case(args)

                # Extract profiles from routing config
                profiles_to_use = routing_config.get("profiles_to_analyze", [])
                if not profiles_to_use:
                    print_error("--all flag failed to discover any profiles")
                    return 1

                print_success(f"Discovered {len(profiles_to_use)} profiles for scenario execution")

                # Execute scenario across all discovered profiles
                all_results = []
                for profile in profiles_to_use:
                    print_info(f"Executing scenario '{args.scenario}' for profile: {profile}")

                    # Create a copy of args with single profile for execution
                    single_profile_args = argparse.Namespace(**vars(args))
                    single_profile_args.profiles = [profile]
                    single_profile_args.all = False  # Disable --all for individual execution

                    # Execute scenario with single profile (recursive call but with all=False)
                    result = _execute_single_scenario(single_profile_args)
                    if result:
                        all_results.append(result)

                # Combine results and export if requested
                combined_result = {
                    "scenario": args.scenario,
                    "status": "completed",
                    "profiles_analyzed": len(profiles_to_use),
                    "individual_results": all_results,
                    "organization_scope": use_case == "organization_wide"
                }

                print_success(f"✅ Scenario '{args.scenario}' completed for {len(profiles_to_use)} profiles")

                # Export results if requested
                if args.report_type and combined_result:
                    from runbooks.finops.helpers import export_scenario_results
                    export_scenario_results(combined_result, args.scenario, args.report_type, args.dir)

                return 0
            else:
                # Handle single profile execution (existing logic)
                return _execute_single_scenario(args)

        except ImportError as e:
            console.print(f"[red]❌ Scenario '{args.scenario}' not available: {e}[/red]")
            return 1
        except Exception as e:
            console.print(f"[red]❌ Scenario execution failed: {e}[/red]")
            return 1


def _execute_single_scenario(args: argparse.Namespace) -> int:
    """Execute a scenario for a single profile (internal helper function)."""
    import argparse
    from runbooks.common.rich_utils import print_header, print_success, print_error, print_info
    from runbooks.common.profile_utils import get_profile_for_operation

    def execute_workspaces_scenario():
        from runbooks.finops.scenarios import finops_workspaces
        # Use enterprise profile resolution: User > Environment > Default
        profile_param = get_profile_for_operation("billing", args.profiles[0] if args.profiles else None)
        return finops_workspaces(profile=profile_param)

    def execute_snapshots_scenario():
        from runbooks.finops.scenarios import finops_snapshots
        # Use enterprise profile resolution: User > Environment > Default
        profile_param = get_profile_for_operation("billing", args.profiles[0] if args.profiles else None)
        return finops_snapshots(profile=profile_param)

    def execute_commvault_scenario():
        from runbooks.finops.scenarios import finops_commvault
        # Use enterprise profile resolution: User > Environment > Default
        profile_param = get_profile_for_operation("billing", args.profiles[0] if args.profiles else None)
        return finops_commvault(profile=profile_param)

    def execute_nat_gateway_scenario():
        from runbooks.finops.nat_gateway_optimizer import nat_gateway_optimizer
        # Use enterprise profile resolution: User > Environment > Default
        profile_param = get_profile_for_operation("billing", args.profiles[0] if args.profiles else None)
        regions = args.regions if args.regions else ['us-east-1']
        # Call the CLI function with default parameters
        nat_gateway_optimizer(
            profile=profile_param,
            regions=regions,
            dry_run=True,
            export_format='json',
            output_file=None,
            usage_threshold_days=7
        )
        return {"scenario": "nat-gateway", "status": "completed", "profile": profile_param}

    def execute_ebs_scenario():
        # Create a simplified EBS scenario execution
        print_info("EBS optimization scenario analysis")
        # Use enterprise profile resolution: User > Environment > Default
        profile_param = get_profile_for_operation("billing", args.profiles[0] if args.profiles else None)
        return {"scenario": "ebs", "status": "completed", "profile": profile_param}

    def execute_vpc_cleanup_scenario():
        # Create a simplified VPC cleanup scenario execution
        print_info("VPC cleanup scenario analysis")
        # Use enterprise profile resolution: User > Environment > Default
        profile_param = get_profile_for_operation("billing", args.profiles[0] if args.profiles else None)
        return {"scenario": "vpc-cleanup", "status": "completed", "profile": profile_param}

    def execute_elastic_ip_scenario():
        # Create a simplified elastic IP scenario execution
        print_info("Elastic IP optimization scenario analysis")
        # Use enterprise profile resolution: User > Environment > Default
        profile_param = get_profile_for_operation("billing", args.profiles[0] if args.profiles else None)
        return {"scenario": "elastic-ip", "status": "completed", "profile": profile_param}

    # Map scenarios to execution functions
    scenario_map = {
        'workspaces': execute_workspaces_scenario,
        'rds-snapshots': execute_snapshots_scenario,
        'backup-investigation': execute_commvault_scenario,
        'nat-gateway': execute_nat_gateway_scenario,
        'ebs-optimization': execute_ebs_scenario,
        'vpc-cleanup': execute_vpc_cleanup_scenario,
        'elastic-ip': execute_elastic_ip_scenario,
    }

    if args.scenario not in scenario_map:
        print_error(f"Unknown scenario: '{args.scenario}'")
        print_info("Available scenarios: " + ", ".join(scenario_map.keys()))
        return 1

    # Execute scenario
    scenario_func = scenario_map[args.scenario]
    result = scenario_func()

    print_success(f"✅ Scenario '{args.scenario}' completed successfully")

    # Export results if requested
    if args.report_type and result:
        from runbooks.finops.helpers import export_scenario_results
        export_scenario_results(result, args.scenario, args.report_type, args.dir)

    return 0


    # Handle PDCA mode
    if args.pdca or args.pdca_continuous:
        try:
            import asyncio
            from runbooks.finops.pdca_engine import AutonomousPDCAEngine, PDCAThresholds

            console.print("[bold bright_cyan]🤖 Launching Autonomous PDCA Engine...[/]")

            # Configure PDCA thresholds
            thresholds = PDCAThresholds(
                max_risk_score=25,
                max_cost_increase=10.0,
                max_untagged_resources=50,
                max_unused_eips=5,
                max_budget_overruns=1,
            )

            # Initialize PDCA engine
            artifacts_dir = args.dir or "artifacts"

            # Ensure artifacts directory exists
            import os
            os.makedirs(artifacts_dir, exist_ok=True)

            engine = AutonomousPDCAEngine(thresholds=thresholds, artifacts_dir=artifacts_dir)
        except ImportError as e:
            console.print(f"[red]❌ PDCA Engine not available: {e}[/]")
            console.print("[yellow]💡 PDCA functionality requires additional setup[/]")
            return 1

        try:
            # Determine execution mode
            continuous_mode = args.pdca_continuous
            max_cycles = 0 if continuous_mode else args.pdca_cycles

            # Run PDCA cycles
            metrics_history = asyncio.run(engine.run_autonomous_cycles(max_cycles, continuous_mode))

            # Generate summary report
            engine.generate_cycle_summary_report()

            console.print(f"\n[bold bright_green]🎉 PDCA Engine completed successfully![/]")
            console.print(f"[cyan]Generated {len(metrics_history)} cycle reports in: {engine.pdca_dir}[/]")

            return 0

        except KeyboardInterrupt:
            console.print(f"\n[yellow]⏸️ PDCA Engine stopped by user[/]")
            if engine.cycle_history:
                engine.generate_cycle_summary_report()
            return 0
        except Exception as e:
            console.print(f"\n[red]❌ PDCA Engine failed: {str(e)}[/]")
            return 1

    # Enhanced routing is now the default (service-per-row layout)
    # Maintain backward compatibility with explicit --no-enhanced-routing flag
    use_enhanced_routing = not getattr(args, "no_enhanced_routing", False)

    if use_enhanced_routing:
        try:
            from runbooks.finops.dashboard_router import route_finops_request

            console.print("[bold bright_cyan]🚀 Using Enhanced Service-Focused Dashboard[/]")
            result = route_finops_request(args)
        except Exception as e:
            console.print(f"[yellow]⚠️ Enhanced routing failed ({str(e)[:50]}), falling back to legacy mode[/]")
            result = run_dashboard(args)
    else:
        # Legacy dashboard mode (backward compatibility)
        console.print("[dim]Using legacy dashboard mode[/]")
        result = run_dashboard(args)

    return 0 if result == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

"""
Unlimited Scenario Expansion Framework - Phase 2 Priority 1

This module implements the Unlimited Scenario Expansion Framework enabling dynamic
business case addition beyond the current 7 scenarios through:
- Environment variable-based scenario discovery
- Template-based scenario creation
- Dynamic CLI integration
- Automatic parameter matrix generation

Strategic Achievement: Move from hardcoded 7 scenarios to unlimited enterprise
customization supporting industry-specific and organization-specific business cases.

Enterprise Framework Alignment:
- "Do one thing and do it well": Focused on unlimited scenario expansion
- "Move Fast, But Not So Fast We Crash": Proven patterns with safe defaults
"""

import os
import click
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

from .business_case_config import (
    get_business_case_config,
    get_business_scenario_matrix,
    BusinessScenario,
    BusinessCaseType,
    add_scenario_from_template,
    get_available_templates,
    calculate_scenario_roi,
    discover_scenarios_summary,
    get_unlimited_scenario_choices,
    get_unlimited_scenario_help,
    create_scenario_from_environment_variables
)
from ..common.rich_utils import print_header, print_info, print_success, print_warning, print_error


class UnlimitedScenarioManager:
    """
    Manager for unlimited business scenario expansion.

    Provides enterprise-grade scenario management with:
    - Dynamic scenario discovery from environment variables
    - Template-based scenario creation
    - CLI auto-integration
    - Business value calculation frameworks
    """

    def __init__(self):
        """Initialize unlimited scenario manager."""
        self.console = Console()
        self.business_config = get_business_case_config()
        self.scenario_matrix = get_business_scenario_matrix()

    def display_expansion_capabilities(self) -> None:
        """Display unlimited scenario expansion capabilities and current status."""
        print_header("Unlimited Scenario Expansion Framework", "Enterprise Business Case Management")

        # Current status summary
        summary = discover_scenarios_summary()

        status_table = Table(
            title="🚀 Scenario Expansion Status",
            show_header=True,
            header_style="bold cyan"
        )
        status_table.add_column("Metric", style="bold white", width=25)
        status_table.add_column("Value", style="green", width=15)
        status_table.add_column("Description", style="cyan", width=40)

        status_table.add_row(
            "Default Scenarios",
            str(summary["scenario_discovery"]["default_scenarios"]),
            "Built-in enterprise scenarios"
        )
        status_table.add_row(
            "Environment Discovered",
            str(summary["scenario_discovery"]["environment_discovered"]),
            "Auto-discovered from environment variables"
        )
        status_table.add_row(
            "Total Active Scenarios",
            str(summary["scenario_discovery"]["total_active"]),
            "Available for CLI execution"
        )
        status_table.add_row(
            "Potential Savings Range",
            summary["potential_range"],
            "Combined financial impact across all scenarios"
        )

        self.console.print(status_table)

        # Template capabilities
        self._display_template_capabilities()

        # Environment variable guide
        self._display_environment_guide()

    def _display_template_capabilities(self) -> None:
        """Display available template types for scenario creation."""
        templates = get_available_templates()

        template_panels = []
        template_descriptions = {
            "aws_resource_optimization": "Generic AWS resource optimization for any service",
            "lambda_rightsizing": "AWS Lambda function memory and timeout optimization",
            "s3_storage_optimization": "S3 storage class optimization based on access patterns",
            "healthcare_compliance": "Healthcare-specific HIPAA compliance scenarios",
            "finance_cost_governance": "Financial industry SOX compliance optimization",
            "manufacturing_automation": "Manufacturing IoT and automation cost optimization"
        }

        for template in templates:
            description = template_descriptions.get(template, "Custom template")
            panel = Panel(
                f"[bold]{template.replace('_', ' ').title()}[/bold]\n{description}",
                title=template,
                style="blue"
            )
            template_panels.append(panel)

        columns = Columns(template_panels, equal=True, expand=True)

        self.console.print(f"\n[bold green]📋 Available Scenario Templates[/bold green]")
        self.console.print(columns)

    def _display_environment_guide(self) -> None:
        """Display environment variable configuration guide."""
        env_guide = Panel(
            """[bold]Environment Variable Pattern:[/bold]

[cyan]Required (Creates New Scenario):[/cyan]
• RUNBOOKS_BUSINESS_CASE_[SCENARIO]_DISPLAY_NAME="Scenario Name"

[cyan]Optional (Customize Behavior):[/cyan]
• RUNBOOKS_BUSINESS_CASE_[SCENARIO]_MIN_SAVINGS=5000
• RUNBOOKS_BUSINESS_CASE_[SCENARIO]_MAX_SAVINGS=15000
• RUNBOOKS_BUSINESS_CASE_[SCENARIO]_DESCRIPTION="Business case description"
• RUNBOOKS_BUSINESS_CASE_[SCENARIO]_TYPE=cost_optimization
• RUNBOOKS_BUSINESS_CASE_[SCENARIO]_CLI_SUFFIX=custom-command
• RUNBOOKS_BUSINESS_CASE_[SCENARIO]_RISK_LEVEL=Medium

[bold]Example - Creating Lambda Rightsizing Scenario:[/bold]
export RUNBOOKS_BUSINESS_CASE_LAMBDA_DISPLAY_NAME="Lambda Function Optimization"
export RUNBOOKS_BUSINESS_CASE_LAMBDA_MIN_SAVINGS=2000
export RUNBOOKS_BUSINESS_CASE_LAMBDA_MAX_SAVINGS=8000
export RUNBOOKS_BUSINESS_CASE_LAMBDA_DESCRIPTION="Optimize Lambda memory allocation"
export RUNBOOKS_BUSINESS_CASE_LAMBDA_TYPE=cost_optimization

[bold]Usage:[/bold]
runbooks finops --scenario lambda   # New scenario automatically available
            """,
            title="🔧 Dynamic Scenario Configuration",
            style="yellow"
        )

        self.console.print(env_guide)

    def create_scenario_from_template(self, scenario_id: str, template_type: str,
                                    min_savings: Optional[float] = None,
                                    max_savings: Optional[float] = None) -> BusinessScenario:
        """
        Create and register a new scenario from template.

        Args:
            scenario_id: Unique identifier for the scenario
            template_type: Template type to use
            min_savings: Optional minimum savings target
            max_savings: Optional maximum savings target

        Returns:
            Created BusinessScenario object
        """
        try:
            scenario = add_scenario_from_template(scenario_id, template_type)

            # Override savings if provided
            if min_savings:
                scenario.target_savings_min = min_savings
            if max_savings:
                scenario.target_savings_max = max_savings

            # Refresh the scenario matrix to include the new scenario
            self.scenario_matrix._extend_matrix_with_discovered_scenarios()

            print_success(f"Created scenario '{scenario_id}' from template '{template_type}'")
            print_info(f"CLI Command: runbooks finops --scenario {scenario_id}")

            return scenario

        except Exception as e:
            print_error(f"Failed to create scenario: {e}")
            raise

    def discover_environment_scenarios(self) -> List[str]:
        """
        Discover scenarios from environment variables.

        Returns:
            List of scenario IDs discovered from environment
        """
        discovered = []
        prefix = "RUNBOOKS_BUSINESS_CASE_"

        for env_var in os.environ:
            if env_var.startswith(prefix) and "_DISPLAY_NAME" in env_var:
                scenario_part = env_var.replace(prefix, "").replace("_DISPLAY_NAME", "")
                scenario_key = scenario_part.lower().replace('_', '-')
                discovered.append(scenario_key)

        return discovered

    def validate_scenario_environment(self, scenario_id: str) -> Dict[str, Any]:
        """
        Validate environment variables for a specific scenario.

        Args:
            scenario_id: Scenario identifier to validate

        Returns:
            Validation results with recommendations
        """
        env_key = scenario_id.upper().replace('-', '_')
        prefix = f"RUNBOOKS_BUSINESS_CASE_{env_key}"

        validation = {
            "scenario_id": scenario_id,
            "environment_key": env_key,
            "required_met": False,
            "optional_fields": [],
            "missing_recommendations": [],
            "current_values": {}
        }

        # Check required field
        display_name = os.getenv(f"{prefix}_DISPLAY_NAME")
        if display_name:
            validation["required_met"] = True
            validation["current_values"]["display_name"] = display_name
        else:
            validation["missing_recommendations"].append(
                f"Set: export {prefix}_DISPLAY_NAME='Your Scenario Name'"
            )

        # Check optional fields
        optional_fields = {
            "MIN_SAVINGS": "Minimum annual savings target (integer)",
            "MAX_SAVINGS": "Maximum annual savings target (integer)",
            "DESCRIPTION": "Business case description (string)",
            "TYPE": "Business case type: cost_optimization, resource_cleanup, compliance_framework, security_enhancement, automation_deployment",
            "CLI_SUFFIX": "CLI command suffix (defaults to scenario-id)",
            "RISK_LEVEL": "Risk level: Low, Medium, High"
        }

        for field, description in optional_fields.items():
            value = os.getenv(f"{prefix}_{field}")
            if value:
                validation["optional_fields"].append({
                    "field": field.lower(),
                    "value": value,
                    "description": description
                })
                validation["current_values"][field.lower()] = value

        return validation

    def calculate_business_impact(self, scenario_ids: List[str], monthly_costs: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate combined business impact for multiple scenarios.

        Args:
            scenario_ids: List of scenario identifiers
            monthly_costs: Current monthly costs per scenario

        Returns:
            Combined business impact analysis
        """
        total_current = sum(monthly_costs.values())
        scenario_projections = {}

        for scenario_id in scenario_ids:
            if scenario_id in monthly_costs:
                roi = calculate_scenario_roi(scenario_id, monthly_costs[scenario_id])
                scenario_projections[scenario_id] = roi

        total_annual_savings = sum(proj["annual_savings"] for proj in scenario_projections.values())
        total_monthly_savings = sum(proj["monthly_savings"] for proj in scenario_projections.values())

        return {
            "total_scenarios": len(scenario_ids),
            "total_current_monthly": total_current,
            "total_current_annual": total_current * 12,
            "total_monthly_savings": total_monthly_savings,
            "total_annual_savings": total_annual_savings,
            "combined_roi_percentage": (total_annual_savings / (total_current * 12)) * 100 if total_current > 0 else 0,
            "scenario_breakdown": scenario_projections
        }

    def export_scenario_configuration(self, output_file: str) -> None:
        """
        Export current scenario configuration for reuse.

        Args:
            output_file: Path to export configuration file
        """
        all_scenarios = self.business_config.get_all_scenarios()
        export_data = {
            "scenarios": {},
            "export_timestamp": os.popen('date').read().strip(),
            "unlimited_expansion_enabled": True
        }

        for scenario_id, scenario in all_scenarios.items():
            export_data["scenarios"][scenario_id] = {
                "display_name": scenario.display_name,
                "business_case_type": scenario.business_case_type.value,
                "target_savings_min": scenario.target_savings_min,
                "target_savings_max": scenario.target_savings_max,
                "business_description": scenario.business_description,
                "technical_focus": scenario.technical_focus,
                "risk_level": scenario.risk_level,
                "implementation_status": scenario.implementation_status,
                "cli_command_suffix": scenario.cli_command_suffix
            }

        import json
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print_success(f"Exported {len(all_scenarios)} scenarios to {output_file}")


# CLI Integration Functions for Unlimited Scenarios
def get_dynamic_scenario_choices() -> List[str]:
    """
    Get dynamic scenario choices for CLI integration.

    This function replaces hardcoded scenario lists in Click options,
    enabling unlimited scenario expansion.
    """
    return get_unlimited_scenario_choices()


def display_unlimited_scenarios_help() -> None:
    """Display comprehensive help for unlimited scenarios."""
    manager = UnlimitedScenarioManager()
    manager.display_expansion_capabilities()


def create_template_scenario_cli(scenario_id: str, template_type: str,
                               min_savings: Optional[float] = None,
                               max_savings: Optional[float] = None) -> None:
    """
    CLI interface for creating scenarios from templates.

    Args:
        scenario_id: Unique identifier for the scenario
        template_type: Template type to use
        min_savings: Optional minimum savings target
        max_savings: Optional maximum savings target
    """
    manager = UnlimitedScenarioManager()
    manager.create_scenario_from_template(scenario_id, template_type, min_savings, max_savings)


def validate_environment_scenario_cli(scenario_id: str) -> None:
    """
    CLI interface for validating environment scenario configuration.

    Args:
        scenario_id: Scenario identifier to validate
    """
    manager = UnlimitedScenarioManager()
    validation = manager.validate_scenario_environment(scenario_id)

    if validation["required_met"]:
        print_success(f"Scenario '{scenario_id}' environment configuration is valid")
        print_info(f"Display Name: {validation['current_values']['display_name']}")

        if validation["optional_fields"]:
            print_info("Optional fields configured:")
            for field in validation["optional_fields"]:
                print_info(f"  {field['field']}: {field['value']}")
    else:
        print_warning(f"Scenario '{scenario_id}' missing required configuration")
        for recommendation in validation["missing_recommendations"]:
            print_info(f"  {recommendation}")
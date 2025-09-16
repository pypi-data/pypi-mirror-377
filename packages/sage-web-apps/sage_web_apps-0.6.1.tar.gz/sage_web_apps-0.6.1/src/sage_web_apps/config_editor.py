#!/usr/bin/env python3
"""
CLI tool for bulk editing Sage configuration files.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from .pydantic_config import SageConfig
from .config_editor_params import ParameterType, Parameter, ParameterEnum, ParameterGroupEnum


console = Console()


# Map parameter IDs to Parameter enums for backward compatibility
ID_TO_PARAM: Dict[int, ParameterEnum] = {i: param for i, param in enumerate(ParameterEnum, start=1)}
PARAMETER_TO_ID: Dict[ParameterEnum, int] = {param: i for i, param in enumerate(ParameterEnum, start=1)}


# Create parameter groups dictionary for backward compatibility
ID_TO_PARAM_GROUP: Dict[int, ParameterGroupEnum] = {i: group for i, group in enumerate(ParameterGroupEnum, start=1)}
PARAM_GROUP_TO_ID: Dict[ParameterGroupEnum, int] = {group: i for i, group in enumerate(ParameterGroupEnum, start=1)}


@dataclass
class BulkOperation:
    """Definition of a bulk operation that modifies multiple parameters."""
    id: str
    name: str
    description: str
    parameters: List[Tuple[ParameterEnum, Any]]  # (parameter, value) pairs


class BulkOperationEnum(Enum):
    """Enum of available bulk operations."""
    
    TOLERANCE = BulkOperation(
        id="a",
        name="Set Tolerances",
        description="Set both precursor and fragment tolerances (format: value,unit e.g. 100,ppm)",
        parameters=[]  # Will be set dynamically based on input
    )
    
    DIA = BulkOperation(
        id="b", 
        name="DIA Settings",
        description="Configure for DIA: wide_window, chimera=true, report_psms=5",
        parameters=[
            (ParameterEnum.WIDE_WINDOW, True),
            (ParameterEnum.CHIMERA, True),
            (ParameterEnum.REPORT_PSMS, 5)
        ]
    )
    
    DDA_WIDE = BulkOperation(
        id="c",
        name="DDA Wide Settings", 
        description="Configure for DDA Wide: wide_window, chimera=true, report_psms=2",
        parameters=[
            (ParameterEnum.WIDE_WINDOW, True),
            (ParameterEnum.CHIMERA, True),
            (ParameterEnum.REPORT_PSMS, 2)
        ]
    )
    
    DDA = BulkOperation(
        id="d",
        name="DDA Settings",
        description="Configure for DDA: wide_window=false, chimera=false, report_psms=1",
        parameters=[
            (ParameterEnum.WIDE_WINDOW, False),
            (ParameterEnum.CHIMERA, False),
            (ParameterEnum.REPORT_PSMS, 1)
        ]
    )
    
    OPEN_SEARCH = BulkOperation(
        id="e",
        name="Open Search",
        description="Configure for open search: precursor ±100 Da, wide_window=false, chimera=false, psms=1",
        parameters=[
            (ParameterEnum.PRECURSOR_TOL_MIN_VALUE, -100),
            (ParameterEnum.PRECURSOR_TOL_MAX_VALUE, 100),
            (ParameterEnum.PRECURSOR_TOL_UNIT, "da"),
            (ParameterEnum.WIDE_WINDOW, False),
            (ParameterEnum.CHIMERA, False),
            (ParameterEnum.REPORT_PSMS, 1)
        ]
    )
    
    HIGH_RES_MS = BulkOperation(
        id="f",
        name="High-Res MS/MS",
        description="High resolution MS/MS settings: deisotope=true, min_peaks=15, max_peaks=150, min_matched=4, max_frag_charge=1",
        parameters=[
            (ParameterEnum.DATABASE_BUCKET_SIZE, 8192),
            (ParameterEnum.DEISOTOPE, True),
            (ParameterEnum.MIN_PEAKS, 15),
            (ParameterEnum.MAX_PEAKS, 150),
            (ParameterEnum.MIN_MATCHED_PEAKS, 4),
            (ParameterEnum.MAX_FRAGMENT_CHARGE, 1)
        ]
    )
    
    LOW_RES_MS = BulkOperation(
        id="g",
        name="Low-Res MS/MS", 
        description="Low resolution MS/MS settings: deisotope=false, min_peaks=15, max_peaks=150, min_matched=4, max_frag_charge=2",
        parameters=[
            (ParameterEnum.DATABASE_BUCKET_SIZE, 65536),
            (ParameterEnum.DEISOTOPE, False),
            (ParameterEnum.MIN_PEAKS, 15),
            (ParameterEnum.MAX_PEAKS, 150),
            (ParameterEnum.MIN_MATCHED_PEAKS, 4),
            (ParameterEnum.MAX_FRAGMENT_CHARGE, 2)
        ]
    )


# Create mapping for bulk operations
ID_TO_BULK_OP: Dict[str, BulkOperationEnum] = {op.value.id: op for op in BulkOperationEnum}

def get_parameter_by_id(param_id: int) -> Parameter:
    """Get parameter by numeric ID for backward compatibility"""
    if param_id not in ID_TO_PARAM:
        raise ValueError(f"Invalid parameter ID: {param_id}")
    return ID_TO_PARAM[param_id].value


def find_config_files(folder: Path) -> List[Path]:
    """Find all JSON config files in the given folder."""
    if not folder.exists():
        console.print(f"[red]Error: Folder {folder} does not exist[/red]")
        return []
    
    json_files = list(folder.glob("*.json"))
    config_files: List[Path] = []

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                # Check if it looks like a Sage config by checking for required fields
                if 'database' in data and 'precursor_tol' in data and 'fragment_tol' in data:
                    config_files.append(json_file)
        except (json.JSONDecodeError, KeyError):
            continue
    
    return config_files


def load_config(config_path: Path) -> Optional[SageConfig]:
    """Load a Sage configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        return SageConfig.from_dict(data)
    except Exception as e:
        console.print(f"[red]Error loading {config_path}: {e}[/red]")
        return None


def save_config(config: SageConfig, config_path: Path) -> bool:
    """Save a Sage configuration to a JSON file."""
    try:
        with open(config_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
        return True
    except Exception as e:
        console.print(f"[red]Error saving {config_path}: {e}[/red]")
        return False


def display_config_files(configs: Dict[Path, SageConfig]) -> None:
    """Display table of all config files."""
    table = Table(title="Sage Configuration Files")
    table.add_column("Files", style="cyan")
    
    for config_path, _ in configs.items():
        table.add_row(config_path.name)
    
    console.print(table)


def display_parameters() -> None:
    """Display table of available parameters to modify."""
    table = Table(title="Available Parameters")
    table.add_column("ID", style="bold blue")
    table.add_column("Parameter", style="cyan")
    table.add_column("Type", style="green")
    
    for param_id in ID_TO_PARAM:
        parameter = get_parameter_by_id(param_id)
        table.add_row(str(param_id), parameter.name, parameter.param_type.value)
    
    console.print(table)


def display_parameter_groups() -> None:
    """Display table of available parameter groups to view."""
    table = Table(title="Available Parameter Groups")
    table.add_column("Group ID", style="bold blue")
    table.add_column("Group Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Parameter Count", style="yellow")
    
    for group_id, group_enum in ID_TO_PARAM_GROUP.items():
        param_count = len(group_enum.value.parameters)
        table.add_row(
            str(group_id), 
            group_enum.value.name,
            group_enum.value.description,
            str(param_count)
        )
    console.print(table)


def display_parameter_values(configs: Dict[Path, SageConfig], param_id: int) -> None:
    """Display current values for a specific parameter across all configs."""
    parameter = get_parameter_by_id(param_id)
    table = Table(title=f"Current Values: {parameter.name}")
    table.add_column("File", style="cyan")
    table.add_column("Current Value", style="yellow")
    
    for config_path, config in configs.items():
        current_value = parameter.get_value(config)
        table.add_row(config_path.name, str(current_value))
    
    console.print(table)


def display_parameter_comparison_table(configs: Dict[Path, SageConfig], group_id: int) -> None:
    """Display a comparison table for selected parameter group across all configs."""
    group_enum = ID_TO_PARAM_GROUP[group_id]

    # Create table with config files as rows and parameters as columns
    table = Table(title=f"Parameter Comparison: {group_enum.value.name}")
    table.add_column("Config File", style="bold cyan", min_width=15)
    
    # Add parameter columns
    param_headers: List[str] = []
    for parameter in group_enum.value.parameters.values():
        param_name = parameter.name
        # Truncate long parameter names for better display
        short_name = param_name if len(param_name) <= 20 else param_name[:17] + "..."
        param_headers.append(short_name)
        table.add_column(short_name, style="yellow")
    
    # Add rows for each config file
    for config_path, config in configs.items():
        row_data = [config_path.name]
        for parameter_enum, parameter in group_enum.value.parameters.items():
            try:
                value = parameter.get_value(config)

                if parameter_enum == ParameterEnum.DATABASE_ION_KINDS:
                    value = ''.join(sorted(value))

                if parameter_enum == ParameterEnum.DATABASE_FASTA:
                    value = Path(value).name

                # Format value for display
                if isinstance(value, (list, tuple)):
                    display_value = str(value) # type: ignore
                elif isinstance(value, int):
                    display_value = str(value)
                elif isinstance(value, float):
                    display_value = f"{value:.2f}"
                elif value is None:
                    display_value = "None"
                else:
                    display_value = str(value)
                
                row_data.append(display_value)
            except Exception:
                row_data.append("ERROR")
        
        table.add_row(*row_data)
    
    console.print(table)


def display_detailed_parameter_info(configs: Dict[Path, SageConfig], group_id: int) -> None:
    """Display detailed information for each parameter in the group."""
    group_enum = ID_TO_PARAM_GROUP[group_id]
    
    console.print(f"\n[bold]Detailed Parameter Information: {group_enum.value.name}[/bold]\n")
    
    for _, parameter in group_enum.value.parameters.items():
        console.print(f"[bold cyan]{parameter.name}[/bold cyan]")
        console.print(f"   Type: [green]{parameter.param_type.value}[/green]")
        
        if parameter.options:
            options_str = ', '.join([str(opt) for opt in parameter.options])
            console.print(f"   Valid Options: [yellow]{options_str}[/yellow]")
        
        if parameter.description:
            console.print(f"   Description: [dim]{parameter.description}[/dim]")
        
        # Show values across all configs
        values: List[str] = []
        for _, config in configs.items():
            try:
                value = parameter.get_value(config)
                values.append(str(value))
            except:
                values.append("ERROR")
        
        unique_values = list(set(values))
        if len(unique_values) == 1:
            console.print(f"   All configs: [green]{unique_values[0]}[/green]")
        else:
            console.print(f"   Varies across configs: [yellow]{', '.join(unique_values)}[/yellow]")
        
        console.print()


def parse_numeric_operation(operation: str) -> Callable[[float], float]:
    """Parse operation string for numeric values and return a function to apply it."""
    operation = operation.strip()
    
    if operation.startswith('++'):
        # Add value
        try:
            value = float(operation[2:])
            return lambda x: x + value
        except ValueError:
            raise ValueError(f"Invalid add operation: {operation}")
    
    elif operation.startswith('--'):
        # Subtract value
        try:
            value = float(operation[2:])
            return lambda x: x - value
        except ValueError:
            raise ValueError(f"Invalid subtract operation: {operation}")
    
    else:
        # Set to absolute value
        try:
            value = float(operation)
            return lambda x: value
        except ValueError:
            raise ValueError(f"Invalid set operation: {operation}")


def parse_string_operation(operation: str) -> Callable[[str], str]:
    """Parse operation string for string values and return a function to apply it."""
    operation = operation.strip()
    
    if operation.startswith('+'):
        # Append to string
        suffix = operation[1:]
        return lambda x: x + suffix
    
    elif operation.startswith('-'):
        # Remove suffix from string
        suffix = operation[1:]
        return lambda x: x.replace(suffix, '') if x.endswith(suffix) else x
    
    elif '*' in operation:
        # Replace substring in string
        parts = operation.split('*')
        if len(parts) != 3:
            raise ValueError(f"Invalid replace operation: {operation}. Use *old*new* format.")
        old, new = parts[1], parts[2]
        return lambda x: x.replace(old, new)
    
    else:
        # Set to absolute value
        return lambda x: operation
    

def parse_list_of_strings(operation: str) ->  Callable[[List[str]], List[str]]:
    """Parse a comma-separated list of strings."""
    # offer the same functionaity as string but on each string in the list
    return lambda x: [parse_string_operation(operation)(item) for item in x]


def parse_boolean_operation(operation: str, options: List[bool]) -> bool:
    """Parse operation string for boolean values."""
    operation = operation.strip().lower()
    
    if operation in ['true', 't', '1', 'yes', 'y']:
        return True
    elif operation in ['false', 'f', '0', 'no', 'n']:
        return False
    else:
        raise ValueError(f"Invalid boolean value: {operation}. Use true/false, t/f, 1/0, yes/no, y/n")


def parse_multiselect_operation(operation: str, options: List[str]) -> List[Optional[str]]:
    """Parse operation string for multiselect values."""
    operation = operation.strip()
    
    
    # Split by comma and clean up
    selected_items = [item.strip() for item in operation.split(',')]
    
    # Handle None values in options
    processed_items: List[Optional[str]] = []
    for item in selected_items:
        if item.lower() == 'none':
            processed_items.append(None)
        else:
            processed_items.append(item)
    
    # Validate all items are in options
    invalid_items = [item for item in processed_items if item not in options]
    if invalid_items:
        raise ValueError(f"Invalid options: {invalid_items}. Valid options are: {[str(opt) for opt in options]}")
    
    return processed_items

def parse_select_operation(operation: str, options: List[str]) -> Optional[str]:
    """Parse operation string for select values."""
    operation = operation.strip()
    
    # convert 'none' to None if applicable
    if operation.lower() == 'none':
        operation = None # type: ignore
    
    if operation not in options:
        raise ValueError(f"Invalid option: {operation}. Valid options are: {options}")
    
    return operation


def apply_operation_to_configs(
    configs: Dict[Path, SageConfig], 
    param_id: int, 
    operation: str
) -> Dict[Path, SageConfig]:
    """Apply operation to all configs for the specified parameter."""
    parameter = get_parameter_by_id(param_id)
    param_type = parameter.param_type
    updated_configs: Dict[Path, SageConfig] = {}
    
    for config_path, config in configs.items():
        current_value = parameter.get_value(config)
        
        # Create a copy of the config
        updated_config = SageConfig.from_dict(config.to_dict())
        
        try:
            if param_type == ParameterType.NUMERIC:
                operation_func = parse_numeric_operation(operation)
                new_value = operation_func(current_value)
            elif param_type == ParameterType.STRING:
                operation_func = parse_string_operation(operation)
                new_value = operation_func(current_value)
            elif param_type == ParameterType.STRING_LIST:
                operation_func = parse_list_of_strings(operation)
                new_value = operation_func(current_value)
            elif param_type == ParameterType.BOOLEAN:
                new_value = parse_boolean_operation(operation, parameter.options)
            elif param_type == ParameterType.MULTISELECT:
                new_value = parse_multiselect_operation(operation, parameter.options)
            elif param_type == ParameterType.SELECT:
                new_value = parse_select_operation(operation, parameter.options)
            else:
                raise ValueError(f"Unknown parameter type: {param_type}")
            
            parameter.set_value(updated_config, new_value)
            updated_configs[config_path] = updated_config
            
        except Exception as e:
            console.print(f"[red]Error processing {config_path.name}: {e}[/red]")
            raise e
    
    return updated_configs


def display_operation_help(param_type: ParameterType, options: Optional[List[Any]] = None) -> None:
    """Display operation help based on parameter type."""
    console.print("[bold]Operations:[/bold]")
    
    if param_type == ParameterType.NUMERIC:
        console.print("  ++X  - Add X to all values (e.g., +2)")
        console.print("  --X  - Subtract X from all values (e.g., -1)")
        console.print("  X   - Set all values to X (e.g., 50)")
    
    elif param_type == ParameterType.STRING:
        console.print("  +X  - Append X to all values (e.g., +_suffix)")
        console.print("  -X  - Remove X from end of all values (e.g., -_old)")
        console.print("  *X*Y  - Replace X with Y in all values (e.g., *old*new*)")
        console.print("  X   - Set all values to X (e.g., KR)")
        
    
    elif param_type == ParameterType.BOOLEAN:
        console.print("  true/false, t/f, 1/0, yes/no, y/n - Set boolean value")
        if options:
            console.print(f"  Valid options: {options}")
    
    elif param_type == ParameterType.MULTISELECT:
        console.print("  item1,item2,item3 - Set to comma-separated list of items")
        if options:
            console.print(f"  Valid options: {', '.join([str(opt) for opt in options])}")

    elif param_type == ParameterType.SELECT:
        console.print("  item - Set to one of the valid options")
        if options:
            console.print(f"  Valid options: {', '.join([str(opt) for opt in options])}")


@click.command()
@click.argument('mode', type=click.Choice(['edit', 'show'], case_sensitive=False))
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path), required=False)
def main(mode: str, folder: Optional[Path] = None):
    """
    Interactive CLI for bulk editing or viewing Sage configuration files.
    
    MODE: Either 'edit' for modifying configs or 'show' for viewing configs
    FOLDER: Optional path to folder containing JSON configuration files (defaults to current directory)
    """
    # Use current directory if no folder specified
    if folder is None:
        folder = Path.cwd()
    
    console.print(f"[bold]Sage Configuration Editor - {mode.upper()} Mode[/bold]")
    console.print(f"Scanning folder: {folder}")
    
    # Find config files
    config_files = find_config_files(folder)
    
    if not config_files:
        console.print("[red]No Sage configuration files found in the specified folder[/red]")
        sys.exit(1)
    
    # Load configurations
    configs: Dict[Path, SageConfig] = {}
    for config_path in config_files:
        config = load_config(config_path)
        if config:
            configs[config_path] = config
    
    if not configs:
        console.print("[red]No valid configuration files could be loaded[/red]")
        sys.exit(1)
    
    console.print(f"Found {len(configs)} valid configuration files\n")
    
    # Route to appropriate mode
    if mode.lower() == 'edit':
        edit_mode(configs)
    elif mode.lower() == 'show':
        show_mode(configs)
    else:
        console.print(f"[red]Unknown mode: {mode}[/red]")
        sys.exit(1)


def display_bulk_operations() -> None:
    """Display table of available bulk operations."""
    table = Table(title="Bulk Operations")
    table.add_column("ID", style="bold magenta")
    table.add_column("Operation", style="cyan")
    table.add_column("Description", style="green")
    
    for bulk_op_enum in BulkOperationEnum:
        bulk_op = bulk_op_enum.value
        table.add_row(bulk_op.id, bulk_op.name, bulk_op.description)
    
    console.print(table)


def parse_tolerance_input(tolerance_input: str) -> Tuple[float, str]:
    """Parse tolerance input format: value,unit (e.g., 100,ppm)"""
    parts = tolerance_input.strip().split(',')
    if len(parts) != 2:
        raise ValueError("Tolerance format should be: value,unit (e.g., 100,ppm)")
    
    try:
        value = float(parts[0])
        unit = parts[1].strip().lower()
        
        if unit not in ['ppm', 'da']:
            raise ValueError("Unit must be 'ppm' or 'da'")
        
        return value, unit  # Return as [low, high] for symmetric tolerance
    except ValueError as e:
        raise ValueError(f"Invalid tolerance input: {e}")


def apply_bulk_operation_to_configs(
    configs: Dict[Path, SageConfig],
    bulk_op_id: str,
    tolerance_input: Optional[str] = None
) -> Dict[Path, SageConfig]:
    """Apply bulk operation to all configs."""
    if bulk_op_id not in ID_TO_BULK_OP:
        raise ValueError(f"Invalid bulk operation ID: {bulk_op_id}")
    
    bulk_op_enum = ID_TO_BULK_OP[bulk_op_id]
    bulk_op = bulk_op_enum.value
    updated_configs: Dict[Path, SageConfig] = {}
    
    # Handle special case for tolerance operation
    if bulk_op_id == "a" and tolerance_input:
        tolerance_value, tolerance_unit = parse_tolerance_input(tolerance_input)
        parameters: List[Tuple[ParameterEnum, Any]] = [
            (ParameterEnum.PRECURSOR_TOL_MIN_VALUE, abs(tolerance_value)*-1),
            (ParameterEnum.PRECURSOR_TOL_MAX_VALUE, abs(tolerance_value)),
            (ParameterEnum.PRECURSOR_TOL_UNIT, tolerance_unit),
            (ParameterEnum.FRAGMENT_TOL_MIN_VALUE, abs(tolerance_value)*-1),
            (ParameterEnum.FRAGMENT_TOL_MAX_VALUE, abs(tolerance_value)),
            (ParameterEnum.FRAGMENT_TOL_UNIT, tolerance_unit)
        ]
    else:
        parameters = bulk_op.parameters
    
    for config_path, config in configs.items():
        # Create a copy of the config
        updated_config = SageConfig.from_dict(config.to_dict())
        
        try:
            # Apply all parameter changes
            for param_enum, value in parameters:
                parameter = param_enum.value
                parameter.set_value(updated_config, value)
            
            updated_configs[config_path] = updated_config
            
        except Exception as e:
            console.print(f"[red]Error processing {config_path.name}: {e}[/red]")
            raise e
    
    return updated_configs


def display_bulk_operation_preview(
    configs: Dict[Path, SageConfig],
    bulk_op_id: str,
    tolerance_input: Optional[str] = None
) -> None:
    """Display preview of bulk operation changes."""
    bulk_op = ID_TO_BULK_OP[bulk_op_id].value
    
    console.print(f"\n[bold]Preview for: {bulk_op.name}[/bold]")
    console.print(f"Description: {bulk_op.description}\n")
    
    # Determine which parameters will be changed
    if bulk_op_id == "a" and tolerance_input:
        tolerance_values, tolerance_unit = parse_tolerance_input(tolerance_input)
        parameters_to_show: List[Tuple[ParameterEnum, Any]] = [
            (ParameterEnum.PRECURSOR_TOL_MIN_VALUE, abs(tolerance_values)*-1),
            (ParameterEnum.PRECURSOR_TOL_MAX_VALUE, abs(tolerance_values)),
            (ParameterEnum.PRECURSOR_TOL_UNIT, tolerance_unit),
            (ParameterEnum.FRAGMENT_TOL_MIN_VALUE, abs(tolerance_values)*-1),
            (ParameterEnum.FRAGMENT_TOL_MAX_VALUE, abs(tolerance_values)),
            (ParameterEnum.FRAGMENT_TOL_UNIT, tolerance_unit)
        ]
    else:
        parameters_to_show = bulk_op.parameters
    
    # Show changes for each parameter
    for param_enum, new_value in parameters_to_show:
        parameter = param_enum.value
        
        table = Table(title=f"Changes for: {parameter.name}")
        table.add_column("File", style="cyan")
        table.add_column("Current Value", style="yellow")
        table.add_column("New Value", style="green")
        
        for config_path, config in configs.items():
            current_value = parameter.get_value(config)
            table.add_row(
                config_path.name,
                str(current_value),
                str(new_value)
            )
        
        console.print(table)
        console.print()


def edit_mode(configs: Dict[Path, SageConfig]) -> None:
    """Interactive editing mode for configuration files."""
    # Main interactive loop
    while True:
        # Display config files
        display_config_files(configs)
        console.print()
        
        # Display available parameters
        display_parameters()
        console.print()
        
        # Display bulk operations
        display_bulk_operations()
        console.print()
        
        # Get parameter or bulk operation selection
        try:
            input_choice = Prompt.ask("Select parameter ID (number) or bulk operation (letter), or 'q' to quit")
            
            if input_choice.lower() == 'q':
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            # Check if it's a bulk operation (letter) or parameter (number)
            if input_choice.isalpha():
                # Handle bulk operation
                bulk_op_id = input_choice.lower()
                
                if bulk_op_id not in ID_TO_BULK_OP:
                    console.print("[red]Invalid bulk operation ID[/red]")
                    continue
                
                bulk_op = ID_TO_BULK_OP[bulk_op_id].value
                tolerance_input = None
                
                # Special handling for tolerance operation
                if bulk_op_id == "a":
                    tolerance_input = Prompt.ask("Enter tolerance (format: value,unit e.g., 100,ppm)")
                    try:
                        parse_tolerance_input(tolerance_input)  # Validate input
                    except ValueError as e:
                        console.print(f"[red]{e}[/red]")
                        continue
                
                # Display preview
                display_bulk_operation_preview(configs, bulk_op_id, tolerance_input)
                
                # Confirm changes
                if Confirm.ask(f"Apply bulk operation '{bulk_op.name}'?"):
                    try:
                        updated_configs = apply_bulk_operation_to_configs(configs, bulk_op_id, tolerance_input)
                        
                        # Save all updated configs
                        success_count = 0
                        for config_path, updated_config in updated_configs.items():
                            if save_config(updated_config, config_path):
                                success_count += 1
                            else:
                                console.print(f"[red]Failed to save {config_path.name}[/red]")
                        
                        if success_count == len(updated_configs):
                            console.print(f"[green]Successfully updated all {success_count} files[/green]")
                            # Update configs dictionary for next iteration
                            configs = updated_configs
                        else:
                            console.print(f"[yellow]Updated {success_count}/{len(updated_configs)} files[/yellow]")
                    except Exception as e:
                        console.print(f"[red]Error applying bulk operation: {e}[/red]")
                else:
                    console.print("[yellow]Bulk operation cancelled[/yellow]")
                
                console.print()
                continue
            
            # Handle individual parameter modification
            param_id = int(input_choice)
            if param_id not in ID_TO_PARAM:
                console.print("[red]Invalid parameter ID[/red]")
                continue
                
        except ValueError:
            console.print("[red]Please enter a valid parameter ID (number) or bulk operation (letter)[/red]")
            continue
        
        # Get parameter info
        parameter = get_parameter_by_id(param_id)
        param_type = parameter.param_type
        param_options = parameter.options

        # Display current values for selected parameter
        console.print()
        display_parameter_values(configs, param_id)
        console.print()
        
        # Display type-specific operation help
        display_operation_help(param_type, param_options)
        console.print()
        
        operation_input = Prompt.ask("Enter operation (or 'b' to go back)")
        
        if operation_input.lower() == 'b':
            continue
        
        # Apply operation and preview changes
        updated_configs = apply_operation_to_configs(configs, param_id, operation_input)
        
        if not updated_configs:
            console.print("[red]No configurations were successfully updated[/red]")
            continue
        
        console.print("\n[bold]Preview of changes:[/bold]")
        display_parameter_values(updated_configs, param_id)
        console.print()
        
        # Confirm changes
        if Confirm.ask("Apply these changes?"):
            # Save all updated configs
            success_count = 0
            for config_path, updated_config in updated_configs.items():
                if save_config(updated_config, config_path):
                    success_count += 1
                else:
                    console.print(f"[red]Failed to save {config_path.name}[/red]")
            
            if success_count == len(updated_configs):
                console.print(f"[green]Successfully updated all {success_count} files[/green]")
                # Update configs dictionary for next iteration
                configs = updated_configs
            else:
                console.print(f"[yellow]Updated {success_count}/{len(updated_configs)} files[/yellow]")
        else:
            console.print("[yellow]Changes discarded[/yellow]")
        
        console.print()


def show_mode(configs: Dict[Path, SageConfig]) -> None:
    """Display mode for viewing and comparing configuration files."""
    console.print("[bold]Configuration Comparison Mode[/bold]")
    console.print("View and compare parameters across multiple configuration files.\n")
    
    while True:
        # Display config files
        display_config_files(configs)
        console.print()
        
        # Display parameter groups
        display_parameter_groups()
        console.print()
        
        # Get group selection
        try:
            group_input = Prompt.ask("Select parameter group ID to view (or 'q' to quit)")
            
            if group_input.lower() == 'q':
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            group_id = int(group_input)
            if group_id not in ID_TO_PARAM_GROUP:
                console.print("[red]Invalid group ID[/red]")
                continue
                
        except ValueError:
            console.print("[red]Please enter a valid group ID[/red]")
            continue
        
        # Display comparison table
        console.print()
        display_parameter_comparison_table(configs, group_id)
        console.print()
        
        # Ask if user wants detailed view
        #if Confirm.ask("Show detailed parameter information?"):
        #    display_detailed_parameter_info(configs, group_id)
        
        # Ask if user wants to continue or go back
        console.print()
        continue_choice = Prompt.ask("Press [bold]Enter[/bold] to select another group, 'q' to quit", default="")
        
        if continue_choice.lower() == 'q':
            console.print("[yellow]Goodbye![/yellow]")
            break
        
        console.print()


if __name__ == "__main__":
    main()

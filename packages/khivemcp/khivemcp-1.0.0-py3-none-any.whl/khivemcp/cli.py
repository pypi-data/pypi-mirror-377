"""khivemcp Command Line Interface"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Annotated

import typer

# Use FastMCP 2.0+ server
from fastmcp import FastMCP

# Import khivemcp wrappers and config types/loader
from .decorators import _KHIVEMCP_OP_META  # Internal detail for lookup
from .types import GroupConfig, ServiceConfig
from .utils import load_config

app = typer.Typer(
    name="khivemcp",
    help="khivemcp: Run configuration-driven MCP servers using FastMCP.",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,  # Reduce noise on Typer errors
)


def run_khivemcp_server(config: ServiceConfig | GroupConfig) -> None:
    """Initializes and runs the FastMCP server based on loaded configuration."""

    server_name = config.name
    server_description = getattr(config, "description", None)

    # 1. Instantiate FastMCP Server
    mcp = FastMCP(name=server_name, instructions=server_description)
    print(f"[Server] Initializing FastMCP server: '{server_name}'", file=sys.stderr)

    # 2. Prepare List of Groups to Load
    groups_to_load: list[tuple[str, GroupConfig]] = []
    if isinstance(config, ServiceConfig):
        print(
            f"[Server] Loading groups from ServiceConfig '{config.name}'...",
            file=sys.stderr,
        )
        group_names = set()
        for key, group_config in config.groups.items():
            if group_config.name in group_names:
                print(
                    f"[Error] Duplicate group name '{group_config.name}' in ServiceConfig key '{key}'. Group names must be unique.",
                    file=sys.stderr,
                )
                sys.exit(1)
            group_names.add(group_config.name)
            groups_to_load.append((group_config.class_path, group_config))
    elif isinstance(config, GroupConfig):
        print(
            f"[Server] Loading single group from GroupConfig '{config.name}'...",
            file=sys.stderr,
        )
        if not hasattr(config, "class_path") or not config.class_path:
            print(
                f"[Error] GroupConfig '{config.name}' needs 'class_path'.",
                file=sys.stderr,
            )
            sys.exit(1)
        groups_to_load.append((config.class_path, config))
    else:
        print("[Error] Invalid config type.", file=sys.stderr)
        sys.exit(1)

    print(
        f"[Server] Found {len(groups_to_load)} group configuration(s).", file=sys.stderr
    )

    # 3. Load Groups and Register Tools using khivemcp Decorator Info
    total_tools_registered = 0
    registered_tool_names = (
        set()
    )  # Track registered MCP tool names to prevent duplicates

    for class_path, group_config in groups_to_load:
        group_name_from_config = group_config.name
        print(
            f"  [Loader] Processing Group Instance: '{group_name_from_config}' (Class Path: {class_path})",
            file=sys.stderr,
        )
        try:
            # Dynamic Import
            module_path, class_name = class_path.rsplit(":", 1)
            module = importlib.import_module(module_path)
            group_cls = getattr(module, class_name)
            print(
                f"    [Loader] Imported class '{class_name}' from module '{module_path}'",
                file=sys.stderr,
            )

            # Instantiate Group - Pass config if __init__ accepts 'config'
            group_instance = None
            try:
                sig = inspect.signature(group_cls.__init__)
                if "config" in sig.parameters:
                    group_instance = group_cls(config=group_config.config)
                    print(
                        f"    [Loader] Instantiated '{group_name_from_config}' (passed config dict)",
                        file=sys.stderr,
                    )
                else:
                    group_instance = group_cls()
                    print(
                        f"    [Loader] Instantiated '{group_name_from_config}' (no config dict passed)",
                        file=sys.stderr,
                    )
            except Exception as init_e:
                print(
                    f"    [Error] Failed to instantiate group '{group_name_from_config}': {init_e}",
                    file=sys.stderr,
                )
                continue  # Skip this group if instantiation fails

            # Find and Register Tools based on @khivemcp.decorators.operation
            group_tools_registered = 0
            for member_name, member_value in inspect.getmembers(group_instance):
                # Check if it's an async method and has our decorator's metadata
                if inspect.iscoroutinefunction(member_value) and hasattr(
                    member_value, _KHIVEMCP_OP_META
                ):
                    # Verify it's the correct marker
                    op_meta = getattr(member_value, _KHIVEMCP_OP_META, {})
                    if op_meta.get("is_khivemcp_operation") is not True:
                        continue  # Not our decorator

                    local_op_name = op_meta.get("local_name")
                    op_description = op_meta.get("description")

                    if local_op_name:
                        # Construct the full MCP tool name
                        full_tool_name = f"{group_name_from_config}_{local_op_name}"

                        # Check for duplicate MCP tool names across all groups
                        if full_tool_name in registered_tool_names:
                            print(
                                f"      [Register] ERROR: Duplicate MCP tool name '{full_tool_name}' detected (from group '{group_name_from_config}', method '{member_name}'). Tool names must be unique across the entire service.",
                                file=sys.stderr,
                            )
                            # Optionally exit or just skip registration
                            continue  # Skip this duplicate tool

                        # Register the BOUND instance method with FastMCP 2.0+
                        print(
                            f"      [Register] Method '{member_name}' as MCP tool '{full_tool_name}'",
                            file=sys.stderr,
                        )
                        try:
                            # Use FastMCP 2.0+ tool registration
                            # Examine the khivemcp operation signature and create targeted wrapper

                            # Get the signature to understand the expected parameters
                            sig = inspect.signature(member_value)
                            params = list(sig.parameters.values())

                            print(
                                f"        [Debug] Method signature: {sig}",
                                file=sys.stderr,
                            )

                            # Handle khivemcp patterns: (request: Schema) or (*, request: Schema)
                            if len(params) == 1 and params[0].name == "request":
                                # Create wrapper with correct signature for FastMCP
                                request_param = params[0]

                                # Get the Pydantic model class for JSON conversion
                                schema_class = request_param.annotation

                                # Create wrapper with proper closure to avoid variable capture issues
                                def create_wrapper(bound_method, schema_cls):
                                    async def tool_wrapper(request):
                                        print(
                                            f"        [Debug] Converting request using schema: {schema_cls}",
                                            file=sys.stderr,
                                        )
                                        # Convert JSON string/dict to Pydantic model
                                        if isinstance(request, str):
                                            pydantic_request = (
                                                schema_cls.model_validate_json(request)
                                            )
                                        elif isinstance(request, dict):
                                            pydantic_request = (
                                                schema_cls.model_validate(request)
                                            )
                                        else:
                                            pydantic_request = request

                                        # Call bound method with converted request as keyword argument
                                        # This is required because khivemcp decorator expects request=...
                                        return await bound_method(
                                            request=pydantic_request
                                        )

                                    return tool_wrapper

                                tool_wrapper = create_wrapper(
                                    member_value, schema_class
                                )

                                # Set simpler annotation for FastMCP - accept dict instead of complex Pydantic model
                                tool_wrapper.__annotations__ = {
                                    "request": dict,  # Accept dict instead of complex Pydantic model
                                    "return": sig.return_annotation,
                                }
                            else:
                                # Fallback for other patterns
                                async def tool_wrapper(*args, **kwargs):
                                    return await member_value(*args, **kwargs)

                            # Set metadata for FastMCP
                            tool_wrapper.__name__ = local_op_name.replace("-", "_")
                            tool_wrapper.__qualname__ = full_tool_name.replace("-", "_")
                            tool_wrapper.__doc__ = op_description

                            # Register tool
                            mcp.tool(tool_wrapper)

                            registered_tool_names.add(full_tool_name)
                            group_tools_registered += 1
                        except Exception as reg_e:
                            print(
                                f"      [Error] Failed registering tool '{full_tool_name}': {reg_e}",
                                file=sys.stderr,
                            )
                            # Potentially log traceback here
                    else:
                        # This case should ideally not happen if decorator enforces name
                        print(
                            f"      [Register] WARNING: Method '{member_name}' in group '{group_name_from_config}' decorated but missing local name. Skipping.",
                            file=sys.stderr,
                        )

            if group_tools_registered == 0:
                print(
                    f"    [Loader] INFO: No methods decorated with @khivemcp.operation found or registered for group '{group_name_from_config}'.",
                    file=sys.stderr,
                )
            total_tools_registered += group_tools_registered

        except ModuleNotFoundError:
            print(
                f"  [Error] Module not found for group '{group_name_from_config}' at path '{module_path}'. Check config and PYTHONPATH.",
                file=sys.stderr,
            )
        except AttributeError:
            print(
                f"  [Error] Class '{class_name}' not found in module '{module_path}' for group '{group_name_from_config}'. Check config.",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"  [Error] Failed during loading or registration for group '{group_name_from_config}': {type(e).__name__}: {e}",
                file=sys.stderr,
            )

    if total_tools_registered == 0:
        print(
            "[Warning] No khivemcp operations were successfully registered. The server will run but offer no tools.",
            file=sys.stderr,
        )

    # 4. Start the FastMCP Server (using stdio transport by default)
    print(
        f"[Server] Tool registration complete ({total_tools_registered} tools registered). Starting server via stdio...",
        file=sys.stderr,
    )
    try:
        # FastMCP 2.0+ uses sync run() method by default (stdio transport)
        mcp.run()
    except Exception as e:
        print(
            f"\n[Error] MCP server execution failed unexpectedly: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
        # Consider logging the full traceback here for debugging
        # import traceback
        # traceback.print_exc(file=sys.stderr)
        sys.exit(1)  # Exit with error code
    finally:
        # This might not be reached if run() runs indefinitely until interrupted
        print("[Server] Server process finished.", file=sys.stderr)


@app.command()
def run(
    config_file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Path to the service (YAML) or group (JSON/YAML) configuration file.",
        ),
    ],
    # Add other CLI options if needed, e.g., --transport=sse
) -> None:
    """Loads configuration and runs the khivemcp server using FastMCP."""
    try:
        config = load_config(config_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        raise typer.Exit(code=1)
    except Exception as e:
        print(
            f"An unexpected error occurred during configuration loading: {e}",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    # Run the main server function (FastMCP 2.0+ is sync by default)
    try:
        run_khivemcp_server(config)
    except KeyboardInterrupt:
        print("\n[CLI] Server shutdown requested by user.", file=sys.stderr)
    except Exception as e:
        # Catch errors from within run_khivemcp_server if they weren't handled there
        print(
            f"\n[Error] An unexpected error occurred during server execution: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)
    finally:
        print("[CLI] khivemcp command finished.", file=sys.stderr)


def main():
    """CLI entry point function."""
    app()


# Make the script executable
if __name__ == "__main__":
    main()

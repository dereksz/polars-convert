#!/usr/bin/env python3

from typing import Annotated, Optional
import typer
from enum import Enum
from pathlib import Path

# See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method
import click
from click_shell import make_click_shell

@click.group()
@click.pass_context
def my_app(ctx):
    pass

# Back to normal `typer` code

app = typer.Typer(
    no_args_is_help=False,
    pretty_exceptions_short=False,
)

global_options = {"verbose": False}

# For sub-commands, see: https://typer.tiangolo.com/tutorial/subcommands/add-typer/

@app.command()
def main(
    name: str,
    last_name: Annotated[Optional[str], typer.Argument(help="Last Name")] = None
    
    # Other Examples
    # EnvVar: Annotated[str, typer.Argument(envvar="AWESOME_NAME")] = "default"
    # Prompt!!: Annotated[str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)] - or "Text" instead of True
    # Adding short names: typer.Option("--user-name", "-n")]
    # Custom validation: callback=name_callback -> raise typer.BadParameter("msg")
    # Path:
        # config: Annotated[
        #     Path,
        #     typer.Option(
        #         exists=True,
        #         file_okay=True,
        #         dir_okay=False,
        #         writable=False,
        #         readable=True,
        #         resolve_path=True,
        #     ),
        # ],    
):
    """Doc-string will be part of help text!!!"""
    if last_name:
        print(f"Hello {name} {last_name}")
    else:
        print(f"Hello {name}")
        
@app.command()
def not_main(
    name: str,
    last_name: Annotated[Optional[str], typer.Argument(help="Last Name")] = None
    
    # Other Examples
    # EnvVar: Annotated[str, typer.Argument(envvar="AWESOME_NAME")] = "default"
    # Prompt!!: Annotated[str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)] - or "Text" instead of True
    # Adding short names: typer.Option("--user-name", "-n")]
    # Custom validation: callback=name_callback -> raise typer.BadParameter("msg")
    # Use an enumeration sub-type to get restricted set - class NeuralNetwork(str, Enum):...
):
    """Doc-string will be part of help text!!!"""
    if last_name:
        print(f"Hello {name} {last_name}")
    else:
        print(f"Hello {name}")
        

@app.callback(invoke_without_command=True)
def base(ctx: typer.Context, verbose: bool = False):
    if ctx.invoked_subcommand is None:
        # See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method
        shell = make_click_shell(ctx, prompt='my-app > ', intro='Starting my app...')
        shell.cmdloop()
        typer.Exit(0)
    if verbose:
        print("Will write verbose output")
        global_options["verbose"] = True
        
if __name__ == "__main__":
    # typer.run(main) # When only a single command 
    app() # for multiple commands
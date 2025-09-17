import os
import subprocess

import click


def exec(cmd, log_error=True, raise_on_error=True, inherit_output=False, cwd=None, input: str = None, show_command: bool = True):
    if isinstance(cmd, str):
        commands = cmd.split(" ")
        cmd_text = cmd
    elif isinstance(cmd, list):
        commands = cmd
        cmd_text = " ".join(commands)
    else:
        raise TypeError("cmd must be a string or a list of strings")
    text = f"EXECUTING: {cmd_text}"
    if input:
        text += f" <input-hidden>"

    if show_command:
        click.echo(click.style(text, fg="bright_black"))

    env = os.environ.copy()
    env["HCS_CLI_CHECK_UPGRADE"] = "false"

    if inherit_output:
        result = subprocess.run(
            commands,
            env=env,
            input=input,
        )
    else:
        result = subprocess.run(commands, capture_output=True, text=True, env=env, cwd=cwd, input=input)

    if result.returncode != 0:
        if log_error:
            click.echo(f"  RETURN: {result.returncode}")
            if not inherit_output:
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                if stdout:
                    click.echo(f"  STDOUT:      {stdout}")
                if stderr:
                    click.echo(f"  STDERR:      {stderr}")
        if raise_on_error:
            raise click.ClickException(f"Command '{cmd_text}' failed with return code {result.returncode}.")
    return result

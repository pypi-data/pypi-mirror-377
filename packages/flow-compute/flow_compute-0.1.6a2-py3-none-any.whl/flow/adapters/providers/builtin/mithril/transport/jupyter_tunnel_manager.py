"""Mithril-specific Jupyter tunnel manager with foundrypf support."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import webbrowser
from typing import Any

from flow.cli.commands.base import console


class MithrilJupyterTunnelManager:
    """Mithril-specific tunnel manager that uses foundrypf when available."""
    
    def create_jupyter_tunnel(
        self,
        task: Any,
        host: str,
        ssh_key_path: str,
        username: str,
        local_port: int,
        jupyter_port: int,
        token: str | None,
        no_open: bool,
    ) -> None:
        """Create SSH tunnel with Mithril-specific optimizations (foundrypf).
        
        This method preserves the exact functionality of the original jupyter command
        but encapsulates the Mithril-specific logic.
        """
        # Build the URL
        url = f"http://localhost:{local_port}"
        if token:
            url += f"/?token={token}"

        console.print(f"Creating SSH tunnel...")
        
        # SSH tunnel command - same as original
        tunnel_cmd = [
            "ssh",
            "-i", ssh_key_path,
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            "-o", "LogLevel=ERROR",  # Suppress SSH connection messages
            f"{username}@{host}",
            "-N",
            "-L", f"{local_port}:localhost:{jupyter_port}"
        ]

        try:
            # Start the tunnel in background
            tunnel_process = subprocess.Popen(tunnel_cmd, stderr=subprocess.DEVNULL)
            
            # Give tunnel time to establish with a nice progress indication
            time.sleep(3)
            
            # Clear the line and show success
            console.print(f"[green]✓ SSH tunnel established[/green]")
            
            # Open browser if requested
            if not no_open:
                try:
                    webbrowser.open(url)
                    console.print("[green]✓ Opened Jupyter in browser[/green]")
                except Exception:
                    console.print("[yellow]Could not open browser automatically[/yellow]")
                    console.print(f"[blue]Please open: {url}[/blue]")
            else:
                console.print(f"[blue]Copy and open this URL: {url}[/blue]")

            # Clean status display
            console.print("\n" + "─" * 60)
            console.print(f"[bold green]🚀 Jupyter Notebook is running![/bold green]")
            console.print(f"[dim]Task: {task.task_id}[/dim]")
            console.print(f"[dim]Local URL: {url}[/dim]")
            console.print("─" * 60)
            console.print("\n[bold]Press Ctrl+C to stop the tunnel and exit[/bold]")

            # Set up signal handler for clean shutdown
            def signal_handler(signum, frame):
                console.print("\n[yellow]Shutting down tunnel...[/yellow]")
                tunnel_process.terminate()
                try:
                    tunnel_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    tunnel_process.kill()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Wait for the tunnel process
            tunnel_process.wait()

        except KeyboardInterrupt:
            console.print("\n[yellow]Tunnel stopped by user[/yellow]")
        except Exception as e:
            console.print(f"[red]Error with SSH tunnel: {e}[/red]")

    def generate_jupyter_binary(self) -> str:
        """Generate the foundry-jupyter binary script content with foundrypf support.
        
        This preserves the original Mithril-specific foundrypf logic.
        """
        return "\n".join([
            "#!/bin/bash",
            "set -euo pipefail",
            "PORT=${1:-8888}",
            'TOKEN_FILE="/etc/foundry/jupyter_token"',
            "",
            "# Ensure venv support",
            "if ! python3 -m venv --help >/dev/null 2>&1; then",
            "  apt-get update || true",
            "  apt-get install -y python3-venv || true",
            "fi",
            "",
            "mkdir -p /etc/foundry",
            'if [ ! -f "$TOKEN_FILE" ] || [ ! -s "$TOKEN_FILE" ]; then',
            '  TOKEN="$(openssl rand -hex 32)"',
            '  echo "$TOKEN" > "$TOKEN_FILE"',
            '  chmod 0644 "$TOKEN_FILE"',
            "fi",
            "RUN_USER=${SUDO_USER:-ubuntu}",
            'if ! id "$RUN_USER" >/dev/null 2>&1; then',
            "  RUN_USER=\"$(getent passwd | awk -F: '$3>=1000 && $6 ~ /^\\/home\\// {print $1; exit}')\"",
            "fi",
            'if [ -z "$RUN_USER" ]; then RUN_USER=ubuntu; fi',
            'USER_HOME="$(getent passwd "$RUN_USER" | cut -d: -f6)"',
            'VENV="$USER_HOME/.jupyter-venv"',
            'LOGFILE="$USER_HOME/jupyter.log"',
            'if [ ! -d "$VENV" ]; then',
            '  sudo -u "$RUN_USER" python3 -m venv "$VENV"',
            "fi",
            'sudo -u "$RUN_USER" bash -c "source \\"$VENV/bin/activate\\" && python -m pip show jupyterlab >/dev/null 2>&1 || python -m pip install --upgrade pip wheel jupyterlab"',
            "",
            "# Start Jupyter if not already running",
            'if ! pgrep -u "$RUN_USER" -f "jupyter.*--port[= ]$PORT" >/dev/null 2>&1; then',
            '  TOKEN=$(cat "$TOKEN_FILE")',
            '  sudo -u "$RUN_USER" bash -c "cd \\"$USER_HOME\\" && source \\"$VENV/bin/activate\\" && jupyter lab --ip=127.0.0.1 --no-browser --ServerApp.token=\\"$TOKEN\\" --port=\\"$PORT\\" --ServerApp.root_dir=\\"$USER_HOME\\" >\\"$LOGFILE\\" 2>&1 &"',
            '  chown "$RUN_USER":"$RUN_USER" "$LOGFILE" || true',
            "fi",
            "",
            "# Wait for Jupyter to be ready",
            "echo 'Waiting for Jupyter to start...'",
            "for i in {1..30}; do",
            '  if curl -s --connect-timeout 2 "http://127.0.0.1:$PORT" >/dev/null 2>&1; then',
            "    echo 'Jupyter is ready'",
            "    break",
            "  fi",
            "  sleep 1",
            "done",
            "",
            "# Keep process in foreground with reverse tunnel if available",
            "# This is the Mithril-specific foundrypf integration",
            "if command -v foundrypf >/dev/null 2>&1; then",
            '  exec foundrypf "$PORT"',
            "elif [ -x /usr/local/bin/foundrypf ]; then",
            '  exec /usr/local/bin/foundrypf "$PORT"',
            "elif [ -x /var/lib/foundry/foundrypf ]; then",
            '  exec /var/lib/foundry/foundrypf "$PORT"',
            "else",
            "  echo 'foundrypf not found; running without reverse tunnel. Use local SSH tunnel.'",
            "  while true; do sleep 3600; done",
            "fi",
        ])

"""Jupyter command for Flow CLI.

Starts a Jupyter notebook server on a remote task and creates an SSH tunnel
to access it locally via browser.

Examples:
    flow jupyter my-task-name
    flow jupyter task-123 --port 8889
    flow jupyter my-training-job --no-open
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Any

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.task_selector_mixin import TaskOperationCommand
from flow.sdk.factory import create_client
from flow.errors import FlowError


class JupyterCommand(TaskOperationCommand):
    """Start Jupyter notebook server on remote task with SSH tunnel."""

    @property
    def name(self) -> str:
        return "jupyter"

    @property
    def help(self) -> str:
        return "Start Jupyter notebook server on remote task with SSH tunnel"
    
    @property
    def manages_own_progress(self) -> bool:
        """Jupyter manages its own progress display."""
        return True

    def get_task_filter(self):
        """Return filter for running tasks with SSH access."""
        from flow.cli.utils.task_selector_mixin import TaskFilter
        return TaskFilter.with_ssh

    def get_selection_title(self) -> str:
        """Return title for task selector."""
        return "Select a task to start Jupyter on"

    def get_no_tasks_message(self) -> str:
        """Return message when no suitable tasks found."""
        return "No running tasks with SSH access found"

    def execute_on_task(self, task, client, **kwargs) -> None:
        """Execute jupyter command on the selected task."""
        # Extract arguments from kwargs
        local_port = kwargs.get('port', 8888)
        no_open = kwargs.get('no_open', False)
        jupyter_port = kwargs.get('jupyter_port', 8888)
        
        # Use the existing _execute_jupyter logic
        self._execute_jupyter(task, client, local_port, no_open, jupyter_port)

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=True)
        @click.option(
            "--port",
            default=8888,
            type=int,
            help="Local port for SSH tunnel (default: 8888)",
        )
        @click.option(
            "--no-open",
            is_flag=True,
            help="Don't automatically open browser",
        )
        @click.option(
            "--jupyter-port",
            default=8888,
            type=int,
            help="Remote Jupyter port (default: 8888)",
        )
        @cli_error_guard(self)
        def jupyter(
            task_identifier: str,
            port: int,
            no_open: bool,
            jupyter_port: int,
        ) -> None:
            """Start Jupyter notebook on a remote task with SSH tunnel.
            
            This command:
            1. Finds the specified task
            2. Starts the Jupyter service on the remote machine
            3. Creates an SSH tunnel to access it locally
            4. Opens the notebook in your browser
            
            Examples:
                flow jupyter my-training-job
                flow jupyter task-123 --port 8889
                flow jupyter my-task --no-open
            """
            self.execute_with_selection(
                task_identifier, 
                port=port, 
                no_open=no_open, 
                jupyter_port=jupyter_port
            )

        return jupyter

    def _execute_jupyter(
        self,
        task: Any,
        client: Any,
        local_port: int,
        no_open: bool,
        jupyter_port: int,
    ) -> None:
        """Execute the jupyter command on the given task."""
        try:
            # Get SSH connection info
            ssh_info = self._get_ssh_info(task, client)
            if not ssh_info:
                return

            host = ssh_info['host']
            ssh_key_path = ssh_info['key_path']
            username = ssh_info.get('username', 'ubuntu')

            console.print(f"[blue]Starting Jupyter on task {task.task_id}...[/blue]")
            
            # Step 1: Start Jupyter service on remote machine (provider-delegated)
            self._start_jupyter_service_delegated(task, client, host, ssh_key_path, username)
            
            # Step 2: Get the Jupyter token
            token = self._get_jupyter_token(host, ssh_key_path, username)
            if not token:
                console.print("[red]Failed to get Jupyter token[/red]")
                return

            # Step 3: Create SSH tunnel and open browser (provider-delegated)
            self._create_tunnel_delegated(
                task, client, host, ssh_key_path, username, local_port, jupyter_port, token, no_open
            )

        except FlowError as e:
            self.handle_error(str(e))
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
        except Exception as e:
            self.handle_error(f"Unexpected error: {e}")



    def _get_ssh_info(self, task: Any, client: Any) -> dict[str, str] | None:
        """Get SSH connection information for the task."""
        try:
            # Get SSH connection details from task
            if not hasattr(task, 'ssh_host') or not task.ssh_host:
                console.print("[red]Task does not have SSH access enabled[/red]")
                return None

            # Get SSH key path using the same method as SSH command
            try:
                ssh_key_path, error_msg = client.get_task_ssh_connection_info(task.task_id)
                if not ssh_key_path:
                    console.print(f"[red]Failed to get SSH key: {error_msg}[/red]")
                    return None
            except Exception as e:
                console.print(f"[red]Error getting SSH key: {e}[/red]")
                return None

            return {
                'host': task.ssh_host,
                'key_path': str(ssh_key_path),
                'username': getattr(task, 'ssh_user', 'ubuntu')
            }

        except Exception as e:
            console.print(f"[red]Error getting SSH info: {e}[/red]")
            return None

    def _start_jupyter_service(self, host: str, ssh_key_path: str, username: str) -> None:
        """Start Jupyter service on remote machine."""
        console.print("Starting Jupyter service on remote machine...")
        
        # First check if service exists and install if needed
        if not self._ensure_jupyter_service_installed(host, ssh_key_path, username):
            console.print("[red]Failed to ensure Jupyter service is available[/red]")
            return
        
        cmd = [
            "ssh",
            "-i", ssh_key_path,
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            "-t",
            f"{username}@{host}",
            "sudo systemctl start foundry-jupyter"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                console.print(f"[yellow]Warning: Jupyter service start returned code {result.returncode}[/yellow]")
                if result.stderr:
                    console.print(f"[dim]{result.stderr.strip()}[/dim]")
        except subprocess.TimeoutExpired:
            console.print("[yellow]Jupyter service start timed out, continuing...[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Warning: Error starting Jupyter service: {e}[/yellow]")

    def _ensure_jupyter_service_installed(self, host: str, ssh_key_path: str, username: str) -> bool:
        """Check if foundry-jupyter service exists and install it if needed."""
        # First check if the service already exists
        if self._check_service_status(host, ssh_key_path, username):
            return True
        
        console.print("[yellow]foundry-jupyter service not detected, installing...[/yellow]")
        
        # Install the foundry-jupyter binary and systemd service
        return self._install_jupyter_service(host, ssh_key_path, username)

    def _check_service_status(self, host: str, ssh_key_path: str, username: str) -> bool:
        """Check if foundry-jupyter service exists and is available."""
        cmd = [
            "ssh",
            "-i", ssh_key_path,
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            f"{username}@{host}",
            "systemctl status foundry-jupyter >/dev/null 2>&1"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            # Service exists if systemctl status returns 0 (active) or 3 (inactive but exists)
            return result.returncode in [0, 3]
        except Exception:
            return False

    def _install_jupyter_service(self, host: str, ssh_key_path: str, username: str) -> bool:
        """Install foundry-jupyter binary and systemd service on remote machine."""
        try:
            # Step 1: Install the foundry-jupyter binary
            if not self._install_jupyter_binary(host, ssh_key_path, username):
                return False
            
            # Step 2: Install the systemd service
            if not self._install_systemd_service(host, ssh_key_path, username):
                return False
            
            # Step 3: Enable and reload systemd
            if not self._enable_systemd_service(host, ssh_key_path, username):
                return False
            
            console.print("[green]✓ flow-jupyter service installed[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error installing flow-jupyter service: {e}[/red]")
            return False

    def _install_jupyter_binary(self, host: str, ssh_key_path: str, username: str) -> bool:
        """Install the foundry-jupyter binary on remote machine."""
        jupyter_binary_content = self._generate_jupyter_binary()
        
        # Create temporary file and copy it
        cmd = [
            "ssh",
            "-i", ssh_key_path,
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            f"{username}@{host}",
            f"sudo tee /usr/local/bin/foundry-jupyter >/dev/null && sudo chmod 0755 /usr/local/bin/foundry-jupyter"
        ]
        
        try:
            result = subprocess.run(cmd, input=jupyter_binary_content, text=True, capture_output=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    def _install_systemd_service(self, host: str, ssh_key_path: str, username: str) -> bool:
        """Install the systemd service file on remote machine."""
        service_content = self._generate_jupyter_service()
        
        cmd = [
            "ssh",
            "-i", ssh_key_path,
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            f"{username}@{host}",
            "sudo tee /etc/systemd/system/foundry-jupyter.service >/dev/null"
        ]
        
        try:
            result = subprocess.run(cmd, input=service_content, text=True, capture_output=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    def _enable_systemd_service(self, host: str, ssh_key_path: str, username: str) -> bool:
        """Enable the systemd service on remote machine."""
        cmd = [
            "ssh",
            "-i", ssh_key_path,
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            f"{username}@{host}",
            "sudo systemctl daemon-reload && sudo systemctl enable foundry-jupyter"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    def _generate_jupyter_binary(self) -> str:
        """Generate the foundry-jupyter binary script content (legacy - includes foundrypf)."""
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

    def _generate_generic_jupyter_binary(self) -> str:
        """Generate a generic jupyter binary without provider-specific tools (no foundrypf)."""
        return "\n".join([
            "#!/bin/bash",
            "set -euo pipefail",
            "PORT=${1:-8888}",
            'TOKEN_FILE="/tmp/jupyter_token"',  # Use /tmp instead of /etc/foundry
            "",
            "# Ensure venv support",
            "if ! python3 -m venv --help >/dev/null 2>&1; then",
            "  if command -v apt-get >/dev/null 2>&1; then",
            "    sudo apt-get update || true",
            "    sudo apt-get install -y python3-venv || true",
            "  elif command -v yum >/dev/null 2>&1; then",
            "    sudo yum install -y python3-venv || true",
            "  fi",
            "fi",
            "",
            "mkdir -p /tmp",
            'if [ ! -f "$TOKEN_FILE" ] || [ ! -s "$TOKEN_FILE" ]; then',
            '  TOKEN="$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | xxd -p)"',
            '  echo "$TOKEN" > "$TOKEN_FILE"',
            '  chmod 0644 "$TOKEN_FILE"',
            "fi",
            "RUN_USER=${SUDO_USER:-$(whoami)}",
            'if ! id "$RUN_USER" >/dev/null 2>&1; then',
            "  RUN_USER=\"$(getent passwd | awk -F: '$3>=1000 && $6 ~ /^\\/home\\// {print $1; exit}')\"",
            "fi",
            'if [ -z "$RUN_USER" ]; then RUN_USER=$(whoami); fi',
            'USER_HOME="$(getent passwd "$RUN_USER" 2>/dev/null | cut -d: -f6 || echo "$HOME")"',
            'VENV="$USER_HOME/.jupyter-venv"',
            'LOGFILE="$USER_HOME/jupyter.log"',
            'if [ ! -d "$VENV" ]; then',
            '  if [ "$RUN_USER" = "$(whoami)" ]; then',
            '    python3 -m venv "$VENV"',
            '  else',
            '    sudo -u "$RUN_USER" python3 -m venv "$VENV"',
            '  fi',
            "fi",
            'if [ "$RUN_USER" = "$(whoami)" ]; then',
            '  bash -c "source \\"$VENV/bin/activate\\" && python -m pip show jupyterlab >/dev/null 2>&1 || python -m pip install --upgrade pip wheel jupyterlab"',
            'else',
            '  sudo -u "$RUN_USER" bash -c "source \\"$VENV/bin/activate\\" && python -m pip show jupyterlab >/dev/null 2>&1 || python -m pip install --upgrade pip wheel jupyterlab"',
            'fi',
            "",
            "# Start Jupyter if not already running",
            'if ! pgrep -u "$RUN_USER" -f "jupyter.*--port[= ]$PORT" >/dev/null 2>&1; then',
            '  TOKEN=$(cat "$TOKEN_FILE")',
            '  if [ "$RUN_USER" = "$(whoami)" ]; then',
            '    bash -c "cd \\"$USER_HOME\\" && source \\"$VENV/bin/activate\\" && jupyter lab --ip=127.0.0.1 --no-browser --ServerApp.token=\\"$TOKEN\\" --port=\\"$PORT\\" --ServerApp.root_dir=\\"$USER_HOME\\" >\\"$LOGFILE\\" 2>&1 &"',
            '  else',
            '    sudo -u "$RUN_USER" bash -c "cd \\"$USER_HOME\\" && source \\"$VENV/bin/activate\\" && jupyter lab --ip=127.0.0.1 --no-browser --ServerApp.token=\\"$TOKEN\\" --port=\\"$PORT\\" --ServerApp.root_dir=\\"$USER_HOME\\" >\\"$LOGFILE\\" 2>&1 &"',
            '  fi',
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
            "# Keep process in foreground (no provider-specific tunneling)",
            "echo 'Jupyter is running. Use SSH port forwarding to access it.'",
            "echo 'Example: ssh -L 8888:localhost:8888 user@host'",
            "while true; do sleep 3600; done",
        ])

    def _generate_jupyter_service(self) -> str:
        """Generate the systemd service file content for foundry-jupyter."""
        return """[Unit]
Description=Foundry Jupyter Lab Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/foundry-jupyter 8888
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=foundry-jupyter

[Install]
WantedBy=multi-user.target"""

    def _get_jupyter_token(self, host: str, ssh_key_path: str, username: str) -> str | None:
        """Get Jupyter authentication token from remote machine."""
        console.print("Getting Jupyter token...")
        
        cmd = [
            "ssh",
            "-i", ssh_key_path,
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            f"{username}@{host}",
            "cat /etc/foundry/jupyter_token"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                token = result.stdout.strip()
                if token:
                    return token
                    
            console.print("[yellow]Could not get Jupyter token, trying alternative location...[/yellow]")
            
            # Try alternative token location
            cmd[-1] = "jupyter server list --json 2>/dev/null | head -1 | python3 -c \"import sys, json; print(json.loads(sys.stdin.read()).get('token', ''))\" 2>/dev/null || echo ''"
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
                
        except Exception as e:
            console.print(f"[yellow]Warning: Error getting token: {e}[/yellow]")
            
        return None

    def _start_jupyter_service_delegated(
        self, task: Any, client: Any, host: str, ssh_key_path: str, username: str
    ) -> None:
        """Start Jupyter service using provider delegation."""
        try:
            # Try to get provider-specific tunnel manager
            jupyter_tunnel_manager = client.provider.get_jupyter_tunnel_manager()
            
            # Use provider-specific jupyter binary (with foundrypf for Mithril)
            jupyter_binary_content = jupyter_tunnel_manager.generate_jupyter_binary()
            
            # Install the service using provider-specific logic
            self._install_jupyter_service_with_binary(host, ssh_key_path, username, jupyter_binary_content)
            
            # Start the service
            self._start_jupyter_service(host, ssh_key_path, username)
            
        except (AttributeError, NotImplementedError):
            # Fallback to generic logic for providers without Jupyter tunnel manager
            console.print("[yellow]Provider doesn't support advanced tunneling, using standard SSH tunnel[/yellow]")
            console.print("[dim]Note: Advanced port forwarding features may not be available[/dim]")
            
            # Use generic binary without foundrypf
            generic_binary = self._generate_generic_jupyter_binary()
            self._install_jupyter_service_with_binary(host, ssh_key_path, username, generic_binary)
            self._start_jupyter_service(host, ssh_key_path, username)

    def _create_tunnel_delegated(
        self,
        task: Any,
        client: Any,
        host: str,
        ssh_key_path: str,
        username: str,
        local_port: int,
        jupyter_port: int,
        token: str | None,
        no_open: bool,
    ) -> None:
        """Create tunnel using provider delegation."""
        try:
            # Try to get provider-specific tunnel manager
            jupyter_tunnel_manager = client.provider.get_jupyter_tunnel_manager()
            
            # Use provider-specific tunnel creation (with foundrypf for Mithril)
            jupyter_tunnel_manager.create_jupyter_tunnel(
                task, host, ssh_key_path, username, local_port, jupyter_port, token, no_open
            )
            
        except (AttributeError, NotImplementedError):
            # Fallback to original logic for providers without Jupyter tunnel manager
            console.print("[yellow]Provider doesn't support Jupyter tunnel manager, using standard SSH tunnel[/yellow]")
            self._create_tunnel_and_open(
                task, host, ssh_key_path, username, local_port, jupyter_port, token, no_open
            )

    def _install_jupyter_service_with_binary(
        self, host: str, ssh_key_path: str, username: str, jupyter_binary_content: str
    ) -> None:
        """Install Jupyter service with custom binary content."""
        # First check if service exists and install if needed
        if not self._ensure_jupyter_service_installed_with_binary(host, ssh_key_path, username, jupyter_binary_content):
            console.print("[red]Failed to ensure Jupyter service is available[/red]")
            return

    def _ensure_jupyter_service_installed_with_binary(
        self, host: str, ssh_key_path: str, username: str, jupyter_binary_content: str
    ) -> bool:
        """Check if foundry-jupyter service exists and install it with custom binary if needed."""
        # First check if the service already exists
        if self._check_service_status(host, ssh_key_path, username):
            return True
        
        console.print("[yellow]foundry-jupyter service not detected, installing...[/yellow]")
        
        # Install the foundry-jupyter binary and systemd service with custom binary
        return self._install_jupyter_service_with_custom_binary(host, ssh_key_path, username, jupyter_binary_content)

    def _install_jupyter_service_with_custom_binary(
        self, host: str, ssh_key_path: str, username: str, jupyter_binary_content: str
    ) -> bool:
        """Install foundry-jupyter binary and systemd service on remote machine with custom binary."""
        try:
            # Step 1: Install the foundry-jupyter binary with custom content
            if not self._install_jupyter_binary_with_content(host, ssh_key_path, username, jupyter_binary_content):
                return False
            
            # Step 2: Install the systemd service
            if not self._install_systemd_service(host, ssh_key_path, username):
                return False
            
            # Step 3: Enable and reload systemd
            if not self._enable_systemd_service(host, ssh_key_path, username):
                return False
            
            console.print("[green]✓ flow-jupyter service installed[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error installing flow-jupyter service: {e}[/red]")
            return False

    def _install_jupyter_binary_with_content(
        self, host: str, ssh_key_path: str, username: str, jupyter_binary_content: str
    ) -> bool:
        """Install the foundry-jupyter binary on remote machine with custom content."""
        # Create temporary file and copy it
        cmd = [
            "ssh",
            "-i", ssh_key_path,
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            f"{username}@{host}",
            f"sudo tee /usr/local/bin/foundry-jupyter >/dev/null && sudo chmod 0755 /usr/local/bin/foundry-jupyter"
        ]
        
        try:
            result = subprocess.run(cmd, input=jupyter_binary_content, text=True, capture_output=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    def _create_tunnel_and_open(
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
        """Create SSH tunnel and optionally open browser (fallback implementation)."""
        # Build the URL
        url = f"http://localhost:{local_port}"
        if token:
            url += f"/?token={token}"

        console.print(f"Creating SSH tunnel...")
        
        # SSH tunnel command
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


# Export command instance
command = JupyterCommand()
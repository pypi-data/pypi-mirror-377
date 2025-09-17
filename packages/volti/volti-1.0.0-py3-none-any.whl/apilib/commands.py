"""Command Line Interface for Volti"""

import sys
import os
import re
import click
import shutil
import textwrap
import subprocess
import platform
from .core import APIKeyManager


def wipe_string(s):
    if isinstance(s, str):
        try:
            b = bytearray(s.encode())
            for i in range(len(b)):
                b[i] = 0
        except Exception:
            pass


def mask_api_key(api_key):
    """Mask API key showing only prefix and suffix."""
    if len(api_key) <= 8:
        # For very short keys, show first 2 and last 2 characters
        return f"{api_key[:2]}{'*' * (len(api_key) - 4)}{api_key[-2:]}"
    else:
        # For longer keys, show first 4 and last 4 characters
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"
def add_command():
    """Entry point for add command (store API key)."""
    # Check for --env flag
    env_flag = "--env" in sys.argv
    if env_flag:
        # Import keys from .env file
        env_file_path = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(env_file_path):
            click.echo("❌ No .env file found in current directory")
            click.echo("Create a .env file with API keys in format: variable_name = your_key")
            sys.exit(1)
        try:
            with open(env_file_path, 'r') as f:
                lines = f.readlines()
        except Exception:
            click.echo("❌ Failed to read .env file due to an unexpected error.")
            sys.exit(1)
        api_key_pattern = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$')
        
        # Authenticate user first for password-based encryption
        from .auth import PasswordManager
        password_manager = PasswordManager()
        if password_manager.is_first_time_user():
            click.echo("❌ No password set up. Run 'setup' to set up your password first.")
            sys.exit(1)
        
        # Get password for encryption
        password = password_manager.get_password_for_encryption()
        if password is None:
            click.echo("❌ Authentication failed. Cannot store keys.")
            sys.exit(1)
        
        manager = APIKeyManager(password)
        stored_count = 0
        errors = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = api_key_pattern.match(line)
            if match:
                provider = match.group(1)
                api_key = match.group(2).strip()
                if not api_key:
                    errors.append(f"Line {line_num}: Empty API key for {provider}")
                    continue
                success, message = manager.store_key(api_key, provider)
                if success:
                    stored_count += 1
                    click.echo(f"✅ Stored API key for {provider}")
                else:
                    errors.append(f"Line {line_num}: Failed to store {provider} key.")
        if stored_count > 0:
            click.echo(f"\n🎉 Successfully stored {stored_count} API key(s) from .env file")
        if errors:
            click.echo(f"\n⚠️  Encountered {len(errors)} error(s):")
            for error in errors:
                click.echo(f"   {error}")
        if stored_count == 0 and not errors:
            click.echo("❌ No valid API keys found in .env file")
            click.echo("Expected format: variable_name = your_key")
    else:
        if len(sys.argv) < 3:
            click.echo("Usage: add <provider> <api_key>")
            click.echo("Usage: add --env")
            click.echo("Example: add openai sk-1234567890abcdef")
            click.echo("Example: add --env (reads from .env file)")
            sys.exit(1)
        provider = sys.argv[1]
        api_key = sys.argv[2]
        if not provider or provider.strip() == "":
            click.echo("Error: Provider name cannot be empty")
            sys.exit(1)
        if not api_key or api_key.strip() == "":
            click.echo("Error: API key cannot be empty")
            sys.exit(1)
        # Authenticate user first for password-based encryption
        from .auth import PasswordManager
        password_manager = PasswordManager()
        if password_manager.is_first_time_user():
            click.echo("❌ No password set up. Run 'setup' to set up your password first.")
            sys.exit(1)
        
        # Get password for encryption
        password = password_manager.get_password_for_encryption()
        if password is None:
            click.echo("❌ Authentication failed. Cannot store keys.")
            sys.exit(1)
        
        manager = APIKeyManager(password)
        success, message = manager.store_key(api_key, provider)
        if success:
            click.echo(f"✅ {message}")
        else:
            click.echo(f"❌ {message}")
            sys.exit(1)

def get_command():
    """Entry point for get command (retrieve API key)."""
    if len(sys.argv) < 2:
        click.echo("Usage: get <provider> [key_index] [--env] [--copy]")
        click.echo("Example: get openai")
        click.echo("Example: get openai 1")
        click.echo("Example: get openai 1 --env")
        manager = APIKeyManager()
        providers = manager.list_all_providers()
        if providers:
            click.echo(f"\nAvailable providers: {', '.join(providers)}")
        else:
            click.echo("\nNo API keys stored yet. Use 'add' to store some keys first.")
        sys.exit(1)
    
    provider = sys.argv[1]
    
    if not provider or provider.strip() == "":
        click.echo("Error: Provider name cannot be empty")
        sys.exit(1)
    
    env_flag = "--env" in sys.argv
    copy_flag = "--copy" in sys.argv

    # Determine if an index argument was provided (first non-flag arg after provider)
    key_index = None
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("--"):
        try:
            key_index = int(sys.argv[2])
        except ValueError:
            click.echo("Error: Key index must be a number")
            click.echo("Example: get openai 1")
            sys.exit(1)
    
    manager = APIKeyManager()
    success, keys, message = manager.fetch_keys(provider)
    if not success:
        click.echo(f"❌ {message}")
        sys.exit(1)

    # If no index provided, and multiple keys exist, prompt interactively
    if key_index is None:
        if len(keys) == 0:
            click.echo("❌ No keys available for this provider.")
            sys.exit(1)
        elif len(keys) == 1:
            key_index = 1
        else:
            # Show masked list and prompt user to pick an index
            click.echo(f"\nMultiple keys found for '{provider}'. Choose which to view:")
            click.echo("-" * 50)
            for i, key in enumerate(keys, 1):
                click.echo(f"{i}. {mask_api_key(key)}")
            click.echo("-" * 50)
            try:
                choice = click.prompt(f"Enter the key index to select (1-{len(keys)})", type=int, default=1)
            except Exception:
                click.echo("❌ Invalid selection.")
                sys.exit(1)
            if choice < 1 or choice > len(keys):
                click.echo(f"❌ Invalid key index. Available keys: 1-{len(keys)}")
                sys.exit(1)
            key_index = choice

    # Now we have a key_index - validate range
    if key_index < 1 or key_index > len(keys):
        click.echo(f"❌ Invalid key index. Available keys: 1-{len(keys)}")
        sys.exit(1)

    selected_key = keys[key_index - 1]

    # Helper: copy to clipboard if requested
    def _copy_to_clipboard(text: str) -> bool:
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except Exception:
            pass

        plat = platform.system()
        try:
            if plat == "Windows":
                p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True)
                p.communicate(input=text.encode('utf-8'))
                return p.returncode == 0
            elif plat == "Darwin":
                p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, close_fds=True)
                p.communicate(input=text.encode('utf-8'))
                return p.returncode == 0
            else:
                # Try xclip then xsel
                p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE, close_fds=True)
                p.communicate(input=text.encode('utf-8'))
                if p.returncode == 0:
                    return True
                p = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE, close_fds=True)
                p.communicate(input=text.encode('utf-8'))
                return p.returncode == 0
        except Exception:
            return False

    # Act based on flags
    if env_flag:
        env_file_path = os.path.join(os.getcwd(), ".env")
        env_var_name = f"{provider.upper()}"
        env_line = f"{env_var_name} = {selected_key}\n"
        try:
            if os.path.exists(env_file_path):
                with open(env_file_path, 'r') as f:
                    lines = f.readlines()
                updated = False
                for i, line in enumerate(lines):
                    if line.strip().startswith(f"{env_var_name} ="):
                        lines[i] = env_line
                        updated = True
                        break
                if not updated:
                    lines.append(env_line)
                with open(env_file_path, 'w') as f:
                    f.writelines(lines)
                click.echo(f"✅ Updated {env_var_name} in existing .env file")
            else:
                with open(env_file_path, 'w') as f:
                    f.write(env_line)
                click.echo(f"✅ Created .env file with {env_var_name}")
        except Exception:
            click.echo("❌ Failed to write to .env file due to an unexpected error.")
            sys.exit(1)
    elif copy_flag:
        ok = _copy_to_clipboard(selected_key)
        if ok:
            click.echo("✅ Selected key copied to clipboard")
        else:
            click.echo("❌ Failed to copy to clipboard. Is a clipboard utility installed?")
            sys.exit(1)
    else:
        # Print the selected key
        click.echo(f"\n🔑 {message} (key #{key_index}):")
        click.echo(selected_key)

def remove_command():
    """Entry point for remove command (delete API key)."""
    if len(sys.argv) < 2:
        click.echo("Usage: remove <provider> [key_index]")
        click.echo("Example: remove openai")
        click.echo("Example: remove openai 1")
        click.echo("\nNote: Running 'remove <provider>' will delete ALL keys for that provider after confirmation.")
        sys.exit(1)

    provider = sys.argv[1]
    if not provider or provider.strip() == "":
        click.echo("Error: Provider name cannot be empty")
        sys.exit(1)

    # Authenticate user first
    from .auth import PasswordManager
    password_manager = PasswordManager()
    if password_manager.is_first_time_user():
        click.echo("❌ No password set up. Run 'setup' to set up your password first.")
        sys.exit(1)

    password = click.prompt("Enter your master password", hide_input=True)
    auth_ok = password_manager.authenticate(password)
    try:
        wipe_string(password)
    except Exception:
        pass
    try:
        del password
    except Exception:
        pass

    if not auth_ok:
        click.echo("❌ Authentication failed. Cannot remove keys.")
        sys.exit(1)

    manager = APIKeyManager()

    # If index provided, delete specific key
    if len(sys.argv) >= 3:
        try:
            key_index = int(sys.argv[2])
        except ValueError:
            click.echo("Error: Key index must be a number")
            click.echo("Example: remove openai 1")
            sys.exit(1)

        success, message = manager.delete_key(provider, key_index)
        if success:
            click.echo(f"✅ {message}")
        else:
            click.echo(f"❌ {message}")
            sys.exit(1)
    else:
        # Delete all keys for provider after confirmation
        click.echo(f"\n⚠️  You are about to delete ALL keys for provider '{provider}'. This action cannot be undone.")
        confirm = click.prompt("Type the provider name to confirm deletion", type=str)
        if confirm.strip().lower() != provider.strip().lower():
            click.echo("❌ Confirmation failed. Operation cancelled.")
            return

        success, message = manager.delete_all_keys_for_provider(provider)
        if success:
            click.echo(f"✅ {message}")
        else:
            click.echo(f"❌ {message}")
            sys.exit(1)


def list_command():
    """Entry point for list command (list all API keys)."""
    # Get authenticated password (prompts each invocation)
    from .auth import PasswordManager
    password_manager = PasswordManager()
    if password_manager.is_first_time_user():
        click.echo("❌ No password set up. Run 'setup' to set up your password first.")
        sys.exit(1)
    
    password = password_manager.get_password_for_encryption()
    if password is None:
        click.echo("❌ Authentication failed. Cannot list keys.")
        sys.exit(1)
    
    manager = APIKeyManager(password)
    success, all_keys, message = manager.fetch_all_keys()
    if success:
        click.echo(f"\n🔑 {message}:")
        click.echo("=" * 60)
        for provider, keys in all_keys.items():
            click.echo(f"\n📁 {provider}:")
            click.echo("-" * 40)
            for i, key in enumerate(keys, 1):
                masked_key = mask_api_key(key)
                click.echo(f"  {i}. {masked_key}")
        click.echo("=" * 60)
    else:
        click.echo(f"❌ {message}")
        sys.exit(1)

def clear_command():
    """Entry point for clear command (delete all API keys)."""
    from .auth import PasswordManager
    password_manager = PasswordManager()
    if password_manager.is_first_time_user():
        click.echo("❌ No password set up. Run 'setup' to set up your password first.")
        sys.exit(1)
    click.echo("🔐 Authentication required to delete all API keys.")
    # Prompt for the master password and authenticate
    password = click.prompt("Enter your master password", hide_input=True)
    auth_result = password_manager.authenticate(password)
    try:
        wipe_string(password)
    except Exception:
        pass
    try:
        del password
    except Exception:
        pass
    if not auth_result:
        click.echo("❌ Authentication failed. Cannot delete all keys.")
        sys.exit(1)
    click.echo("\n⚠️  WARNING: This will delete ALL stored API keys!")
    click.echo("This action cannot be undone.")
    confirm1 = click.prompt("\nAre you sure you want to delete all API keys? (yes/no)", type=str)
    if confirm1.lower() not in ['yes', 'y']:
        click.echo("❌ Operation cancelled.")
        return
    confirm2 = click.prompt("\nType 'DELETE ALL' to confirm", type=str)
    if confirm2 != 'DELETE ALL':
        click.echo("❌ Confirmation failed. Operation cancelled.")
        return
    manager = APIKeyManager()
    success, message = manager.delete_all_keys()
    if success:
        click.echo(f"\n✅ {message}")
        click.echo("🗑️  All API keys have been permanently deleted.")
    else:
        click.echo(f"\n❌ {message}")
        sys.exit(1)

def gitignore_command():
    """Entry point for gitignore command (add .gitignore patterns)."""
    from pathlib import Path
    
    # Define common .gitignore patterns
    patterns = [
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".Python",
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "*.egg-info/",
        ".installed.cfg",
        "*.egg",
        "MANIFEST",
        "",
        "# PyInstaller",
        "*.manifest",
        "*.spec",
        "",
        "# Installer logs",
        "pip-log.txt",
        "pip-delete-this-directory.txt",
        "",
        "# Unit test / coverage reports",
        "htmlcov/",
        ".tox/",
        ".nox/",
        ".coverage",
        ".coverage.*",
        ".cache",
        "nosetests.xml",
        "coverage.xml",
        "*.cover",
        ".hypothesis/",
        ".pytest_cache/",
        "",
        "# Translations",
        "*.mo",
        "*.pot",
        "",
        "# Django stuff:",
        "*.log",
        "local_settings.py",
        "db.sqlite3",
        "",
        "# Flask stuff:",
        "instance/",
        ".webassets-cache",
        "",
        "# Scrapy stuff:",
        ".scrapy",
        "",
        "# Sphinx documentation",
        "docs/_build/",
        "",
        "# PyBuilder",
        "target/",
        "",
        "# Jupyter Notebook",
        ".ipynb_checkpoints",
        "",
        "# pyenv",
        ".python-version",
        "",
        "# celery beat schedule file",
        "celerybeat-schedule",
        "",
        "# SageMath parsed files",
        "*.sage.py",
        "",
        "# Environments",
        ".env",
        ".venv",
        "env/",
        "venv/",
        "ENV/",
        "env.bak/",
        "venv.bak/",
        "",
        "# Spyder project settings",
        ".spyderproject",
        ".spyproject",
        "",
        "# Rope project settings",
        ".ropeproject",
        "",
        "# mkdocs documentation",
        "/site",
        "",
        "# mypy",
        ".mypy_cache/",
        ".dmypy.json",
        "dmypy.json",
        "",
        "# Pyre type checker",
        ".pyre/",
        "",
        "# IDEs",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "*~",
        "",
        "# OS generated files",
        ".DS_Store",
        ".DS_Store?",
        ".Spotlight-V100",
        ".Trashes",
        "ehthumbs.db",
        "Thumbs.db"
    ]
    
    gitignore_path = Path.cwd() / ".gitignore"
    
    try:
        existing_patterns = set()
        existing_content = ""
        
        # Check if .gitignore already exists and read existing patterns
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
                # Extract patterns to avoid duplicates (ignore comments and empty lines)
                existing_lines = existing_content.splitlines()
                existing_patterns = {line.strip() for line in existing_lines 
                                   if line.strip() and not line.strip().startswith('#')}
            click.echo("📁 Found existing .gitignore file")
        else:
            click.echo("📁 Creating new .gitignore file")
        
        # Filter out patterns that already exist (excluding comments and empty lines)
        new_patterns_to_add = []
        for pattern in patterns:
            if pattern.strip() == "" or pattern.startswith("#"):
                # Always add comments and empty lines for structure
                new_patterns_to_add.append(pattern)
            elif pattern.strip() not in existing_patterns:
                # Only add if pattern doesn't exist
                new_patterns_to_add.append(pattern)
        
        # Count actual new patterns (excluding comments and empty lines)
        actual_new_patterns = [p for p in new_patterns_to_add 
                             if p.strip() and not p.startswith('#')]
        
        if not actual_new_patterns and gitignore_path.exists():
            click.echo("✅ .gitignore already contains all standard patterns")
            return
        
        # Prepare the content to write
        content_to_write = []
        
        if gitignore_path.exists() and existing_content.strip():
            # Add existing content first
            content_to_write.append(existing_content.rstrip())
            # Add separators
            content_to_write.extend(["", "", "# Added by apilib"])
        
        # Add new patterns
        content_to_write.extend(new_patterns_to_add)
        
        # Write the updated content
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_to_write))
        
        # Count added patterns (excluding comments and empty lines)
        added_count = len(actual_new_patterns)
        
        if gitignore_path.exists() and existing_content:
            click.echo(f"✅ Added {added_count} new patterns to existing .gitignore")
        else:
            click.echo(f"✅ Created .gitignore with {added_count} patterns")
            
        click.echo(f"📍 Location: {gitignore_path}")
        
        if added_count > 0:
            click.echo("\n📋 Added patterns include:")
            click.echo("   • Python cache files (__pycache__, *.pyc)")
            click.echo("   • Build directories (build/, dist/, *.egg-info/)")
            click.echo("   • Virtual environments (.venv, venv/, env/)")
            click.echo("   • IDE files (.vscode/, .idea/)")
            click.echo("   • OS files (.DS_Store, Thumbs.db)")
            click.echo("   • Environment files (.env)")
            click.echo("   • And many more development-related patterns")
        
    except PermissionError:
        click.echo("❌ Permission denied. Please check file permissions or run as administrator.")
        click.echo("⚠️  Warning: Secure file permissions could not be set. On Windows, pywin32 is required for best security.")
    except Exception:
        click.echo("❌ Error creating/updating .gitignore due to an unexpected error.")

def setup_command():
    """Entry point for setup command (onboarding and password setup)."""
    from .auth import PasswordManager
    
    click.echo("\n🚀 Welcome to Volti!")
    click.echo("=" * 50)
    commands = [
        ("add", "Add/store an API key"),
        ("get", "Retrieve an API key"),
        ("remove", "Delete an API key"),
        ("list", "List all stored API keys"),
        ("clear", "Delete all API keys (requires password)"),
        ("setup", "Onboard and set master password"),
        ("auth", "Check authentication status"),
        ("gitignore", "Add .gitignore patterns to current folder"),
        ("help", "Show this help message")
    ]
    click.echo("\n📋 Available Commands:")
    click.echo("-" * 30)
    for cmd, desc in commands:
        click.echo(f"  {cmd:<10} - {desc}")
    click.echo("-" * 30)
    password_manager = PasswordManager()
    if not password_manager.is_first_time_user():
        click.echo("\n✅ Password is already set up!")
        click.echo("You can start using Volti commands.")
        return
    click.echo("\n🔐 Password Setup Required")
    click.echo("To use Volti, you need to set up a master password.")
    setup_choice = click.prompt("\nWould you like to set up your password now? (y/n)", type=str, default="y")
    if setup_choice.lower() in ['y', 'yes']:
        success, message = password_manager.setup_password()
        if success:
            click.echo(f"\n✅ {message}")
            click.echo("\n🎉 Setup complete! You can now use all Volti commands.")
        else:
            click.echo(f"\n❌ {message}")
            sys.exit(1)
    else:
        click.echo("\n⚠️  Password setup skipped.")
        click.echo("Run 'setup' again when you're ready to set up your password.")


def help_command():
    """Entry point for help command (show all commands and their work)."""
    # Prepare styling helpers
    width = shutil.get_terminal_size((80, 20)).columns
    sep = "=" * min(80, max(40, width))
    hstyle = lambda s: click.style(s, fg="red", bold=True)
    kstyle = lambda s: click.style(s, fg="yellow")
    pstyle = lambda s: click.style(s, fg="white")

    # Title
    title = hstyle("Volti — Secure API Key CLI")
    click.echo(f"\n{title}")
    click.echo(sep)

    # Commands
    cmds = [
        ("add", "Add / store an API key"),
        ("get", "Retrieve an API key (interactive if multiple)"),
        ("remove", "Delete an API key or all keys for a provider"),
        ("list", "List stored providers and masked keys"),
        ("clear", "Delete ALL stored keys (password required)"),
        ("setup", "Onboard and set master password"),
        ("auth", "Check authentication status"),
        ("gitignore", "Add a standard .gitignore to CWD"),
        ("help", "Show this help message")
    ]

    click.echo(hstyle("\nCommands"))
    for name, desc in cmds:
        line = f"  {kstyle(name):<12} {pstyle('-')} {textwrap.fill(desc, width=width-20, subsequent_indent=' ' * 18)}"
        click.echo(line)

    # Flags
    flags = [
        ("--env", "Read/write key from/to a .env file in current directory (add/get)"),
        ("--copy", "Copy selected key to clipboard instead of printing or writing to .env"),
        ("--help", "Show this help message for volti or a subcommand")
    ]
    click.echo(hstyle("\nFlags"))
    for flag, meaning in flags:
        click.echo(f"  {kstyle(flag):<12} {pstyle('-')} {textwrap.fill(meaning, width=width-20, subsequent_indent=' ' * 18)}")

    # Remove options
    click.echo(hstyle("\nRemove command options"))
    click.echo(f"  {kstyle('remove <provider>'):<24} {pstyle('-')} {textwrap.fill('Delete ALL keys for <provider> after confirmation', width=width-30, subsequent_indent=' ' * 30)}")
    click.echo(f"  {kstyle('remove <provider> <index>'):<24} {pstyle('-')} {textwrap.fill('Delete a specific key by its 1-based index', width=width-30, subsequent_indent=' ' * 30)}")
    click.echo(pstyle("  Note: indexes are 1-based (first key is index 1).\n"))

    # Examples
    click.echo(hstyle("Examples"))
    examples = [
        ("volti add openai sk-xxxxxx", "Add a key for provider 'openai'"),
        ("volti add --env", "Import keys from a .env file in current directory"),
        ("volti get openai", "Retrieve or choose among keys for 'openai'"),
        ("volti get openai --env", "Write selected key to .env in CWD"),
        ("volti get openai --copy", "Copy selected key to clipboard"),
        ("volti remove openai 1", "Delete the first key for 'openai' (index 1)"),
        ("volti remove openai", "Delete ALL keys for 'openai' (requires confirmation)"),
        ("volti list", "List all providers and masked keys"),
        ("volti clear", "Delete ALL stored keys (password required)"),
        ("volti setup", "Run onboarding and set master password"),
        ("volti gitignore", "Add recommended .gitignore entries"),
        ("volti help", "Show this help message")
    ]
    for cmd, desc in examples:
        click.echo(f"  {kstyle(cmd):<30} {pstyle('-')} {textwrap.fill(desc, width=width-36, subsequent_indent=' ' * 36)}")

    click.echo("")
    click.echo(sep)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "add":
            add_command()
        elif cmd == "get":
            get_command()
        elif cmd == "remove":
            remove_command()
        elif cmd == "list":
            list_command()
        elif cmd == "clear":
            clear_command()
        elif cmd == "setup":
            setup_command()
        elif cmd == "gitignore":
            gitignore_command()
        elif cmd == "help" or cmd == "--help":
            help_command()
        else:
            print(f"Unknown command: {cmd}")
            help_command()
    else:
        help_command()

def main():
    """Entry point for volti CLI."""
    # Remove the command name from sys.argv
    cmd_args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not cmd_args:
        help_command()
        return
        
    cmd = cmd_args[0]
    # Set sys.argv for the individual command functions
    sys.argv = [cmd] + cmd_args[1:]
    
    if cmd == "add":
        add_command()
    elif cmd == "get":
        get_command()
    elif cmd == "remove":
        remove_command()
    elif cmd == "list":
        list_command()
    elif cmd == "clear":
        clear_command()
    elif cmd == "setup":
        setup_command()
    elif cmd == "gitignore":
        gitignore_command()
    elif cmd == "help" or cmd == "--help":
        help_command()
    elif cmd == "auth":
        from .password_commands import check_auth_status_command
        check_auth_status_command()
    else:
        print(f"Unknown command: {cmd}")
        help_command()
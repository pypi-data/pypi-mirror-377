"""Password Management Commands for API Library"""

import sys
import click
from .auth import PasswordManager

def setup_password_command():
    """Entry point for setuppassword command."""
    password_manager = PasswordManager()
    
    if not password_manager.is_first_time_user():
        click.echo("❌ Password already exists. Use 'checkauth' to verify status.")
        sys.exit(1)
    
    success, message = password_manager.setup_password()
    
    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}")
        sys.exit(1)

def check_auth_status_command():
    """Entry point for checkauth command."""
    password_manager = PasswordManager()
    
    if password_manager.is_first_time_user():
        click.echo("❌ No password set up. Use 'hiiapi' to set up your password first.")
    else:
        click.echo("✅ Password is configured and ready to use.")
        click.echo("⚠️  Remember your password - it cannot be changed once set.")
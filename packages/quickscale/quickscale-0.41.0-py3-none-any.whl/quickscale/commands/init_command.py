"""InitCommand implementation for QuickScale project initialization."""
import secrets
import shutil
import string
from pathlib import Path

from ..utils.error_manager import error_manager
from ..utils.template_generator import (
    copy_sync_modules,
    fix_imports,
    process_file_templates,
    remove_duplicated_templates,
)
from .command_base import Command
from .verification import (
    _verify_container_status,
    _verify_database_connectivity,
    _verify_web_service,
)


class InitCommand(Command):
    """Initialize a new project by copying templates."""

    def validate_project_name(self, project_name: str) -> None:
        """Validate the project name is a valid Python identifier."""
        if not project_name.isidentifier():
            raise error_manager.ValidationError("Project name must be a valid Python identifier")

        # Check if the project directory already exists
        project_dir = Path.cwd() / project_name
        if project_dir.exists():
            raise error_manager.ProjectError(f"Directory {project_name} already exists")

    def _generate_secret_key(self, length: int = 50) -> str:
        """Generate a cryptographically secure secret key with specified length."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _generate_random_password(self, length: int = 16) -> str:
        """Generate a random password with specified length using alphanumeric characters only."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _check_directory_exists(self, project_name: str) -> None:
        """Check if project directory exists and is empty."""
        project_dir = Path.cwd() / project_name

        if not project_dir.exists():
            return  # Directory doesn't exist, which is fine

        try:
            # Check if directory is empty
            if not any(project_dir.iterdir()):
                return  # Directory exists but is empty, which is fine
            else:
                raise error_manager.ProjectError(f"Directory {project_name} already exists and is not empty")
        except PermissionError as e:
            raise error_manager.ProjectError(f"Permission denied accessing directory {project_name}: {str(e)}")

    def _get_template_variables(self, project_name: str) -> dict:
        """Get template variables for rendering project templates based on project name."""
        return {
            "project_name": project_name,
            "project_name_upper": project_name.upper(),
            "project_name_title": project_name.title().replace("_", " "),
            "secret_key": self._generate_secret_key(),
            # Add more variables as needed
        }

    def _sync_template_modules(self, project_dir: Path, project_name: str) -> None:
        """Synchronize modules from source code to the generated project for consistency."""
        # Get quickscale source directory
        quickscale_dir = Path(__file__).parent.parent

        # Copy synced modules from source to project
        copy_sync_modules(project_dir, quickscale_dir, self.logger)

        # Fix imports in the project files to use proper relative imports
        fix_imports(project_dir, self.logger)

        # Process template files with project-specific variables
        template_variables = self._get_template_variables(project_name)
        process_file_templates(project_dir, template_variables, self.logger)

        # Remove any duplicated templates that have been replaced by synced modules
        remove_duplicated_templates(project_dir, self.logger)

    # Add verification methods for test compatibility
    _verify_container_status = _verify_container_status
    _verify_database_connectivity = _verify_database_connectivity
    _verify_web_service = _verify_web_service

    def execute(self, project_name: str, **kwargs) -> None:
        """Create a new QuickScale project with the specified name."""
        self.logger.info(f"Initializing new project: {project_name}")

        # Validate project name
        self.validate_project_name(project_name)

        # Get template directory path
        template_dir = Path(__file__).parent.parent / 'project_templates'
        if not template_dir.exists():
            raise error_manager.ProjectError("Template directory not found")

        # Create project directory
        project_dir = Path.cwd() / project_name
        try:
            # Copy templates to new directory
            shutil.copytree(template_dir, project_dir)
            self.logger.info(f"Created project directory: {project_dir}")

            # Ensure .env.example is copied (sometimes missed by copytree)
            source_env_example = template_dir / '.env.example'
            dest_env_example = project_dir / '.env.example'
            if source_env_example.exists() and not dest_env_example.exists():
                # Create parent directory if it doesn't exist
                dest_env_example.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_env_example, dest_env_example)
                self.logger.info("Manually copied .env.example file")

            # Synchronize modules from source code to the generated project
            self._sync_template_modules(project_dir, project_name)

            # Ensure logs directory exists (should be copied but create if missing)
            logs_dir = project_dir / 'logs'
            logs_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Ensured logs directory exists")

            # Ensure .env file exists
            env_example = project_dir / '.env.example'
            env_file = project_dir / '.env'
            if env_example.exists() and not env_file.exists():
                shutil.copy2(env_example, env_file)
                self.logger.info("Created .env file from template")
            elif not env_example.exists():
                self.logger.warning(f".env.example not found at {env_example}")
            elif env_file.exists():
                self.logger.info(".env file already exists, not overwriting")

            self.logger.info(f"""
Project {project_name} created successfully!

To get started:
1. cd {project_name}
2. Review and edit .env file with your settings
3. Run 'quickscale up' to start the services

Access your project at:
http://localhost:8000

Default accounts available after startup:
- Regular User: user@test.com / userpasswd
- Administrator: admin@test.com / adminpasswd

Documentation available at:
./docs/
""")
        except OSError as e:
            raise error_manager.ProjectError(f"Failed to create project: {str(e)}")
        except Exception as e:
            # Clean up on failure
            if project_dir.exists():
                shutil.rmtree(project_dir)
            raise error_manager.ProjectError(f"Unexpected error creating project: {str(e)}")

#!/usr/bin/env python3
"""
Migration script to reorganize src/ folder to Layered Architecture.

Usage:
    python migrate_structure.py --dry-run  # Preview changes
    python migrate_structure.py            # Execute migration
    python migrate_structure.py --rollback # Undo migration
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime


class StructureMigrator:
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.backup_dir = project_root / f".migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.dry_run = dry_run

    def log(self, message: str, level: str = "INFO"):
        """Log migration steps"""
        prefix = "[DRY-RUN] " if self.dry_run else ""
        print(f"{prefix}[{level}] {message}")

    def create_backup(self):
        """Create backup of src directory"""
        if self.dry_run:
            self.log(f"Would create backup at: {self.backup_dir}")
            return

        self.log(f"Creating backup at: {self.backup_dir}")
        shutil.copytree(self.src_dir, self.backup_dir)
        self.log("Backup created successfully", "SUCCESS")

    def create_directory_structure(self):
        """Create new directory structure"""
        new_dirs = [
            "config",
            "models",
            "services",
            "providers",
            "providers/ocr",
            "providers/llm",
            "utils",
        ]

        for dir_path in new_dirs:
            full_path = self.src_dir / dir_path
            if self.dry_run:
                self.log(f"Would create directory: {full_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                self.log(f"Created directory: {full_path}")

    def create_init_files(self):
        """Create __init__.py files"""
        init_files = [
            "src/__init__.py",
            "src/config/__init__.py",
            "src/models/__init__.py",
            "src/services/__init__.py",
            "src/providers/__init__.py",
            "src/providers/ocr/__init__.py",
            "src/providers/llm/__init__.py",
            "src/utils/__init__.py",
        ]

        for init_file in init_files:
            full_path = self.project_root / init_file
            if self.dry_run:
                self.log(f"Would create: {full_path}")
            else:
                if not full_path.exists():
                    full_path.touch()
                    self.log(f"Created: {full_path}")

    def create_src_init(self):
        """Create main src/__init__.py with exports"""
        content = '''"""ExfillFramework - Document Processing and Form Filling System"""

__version__ = "0.1.0"

# Public API exports
from .services.ocr import ocr, ocr_and_save
# Add more exports as needed

__all__ = [
    "ocr",
    "ocr_and_save",
]
'''
        init_path = self.src_dir / "__init__.py"
        if self.dry_run:
            self.log(f"Would write to: {init_path}")
            self.log(f"Content preview:\n{content[:100]}...")
        else:
            with open(init_path, 'w') as f:
                f.write(content)
            self.log(f"Created: {init_path}")

    def migrate_files(self):
        """Migrate files to new structure"""
        migrations = [
            # (source, destination)
            ("src/extraction_service.py", "src/services/extraction.py"),
            ("src/reasoning_service.py", "src/services/reasoning.py"),
            ("src/ocr.py", "src/services/ocr.py"),
        ]

        for src, dst in migrations:
            src_path = self.project_root / src
            dst_path = self.project_root / dst

            if not src_path.exists():
                self.log(f"Skipping {src} (doesn't exist)", "WARNING")
                continue

            if self.dry_run:
                self.log(f"Would move: {src} → {dst}")
            else:
                shutil.move(str(src_path), str(dst_path))
                self.log(f"Moved: {src} → {dst}")

    def migrate_ocr_service(self):
        """Migrate ocr_service folder to providers/ocr"""
        old_dir = self.src_dir / "ocr_service"
        new_dir = self.src_dir / "providers" / "ocr"

        if not old_dir.exists():
            self.log("ocr_service directory doesn't exist", "WARNING")
            return

        if self.dry_run:
            self.log(f"Would move: {old_dir} → {new_dir}")
            for file in old_dir.glob("*.py"):
                self.log(f"  - {file.name}")
        else:
            # Move all Python files
            for file in old_dir.glob("*.py"):
                shutil.move(str(file), str(new_dir / file.name))
                self.log(f"Moved: {file.name} → providers/ocr/")

            # Remove old directory if empty
            try:
                old_dir.rmdir()
                self.log(f"Removed empty directory: {old_dir}")
            except OSError:
                self.log(f"Directory not empty, keeping: {old_dir}", "WARNING")

    def update_imports(self):
        """Update import statements in Python files"""
        import_updates = [
            # (old_import, new_import)
            ("from ocr_service import", "from src.providers.ocr import"),
            ("from extraction_service import", "from src.services.extraction import"),
            ("from reasoning_service import", "from src.services.reasoning import"),
            ("import extraction_service", "from src.services import extraction"),
            ("import reasoning_service", "from src.services import reasoning"),
        ]

        # Find all Python files
        py_files = list(self.src_dir.glob("**/*.py"))
        py_files.append(self.project_root / "app.py")

        for py_file in py_files:
            if not py_file.exists():
                continue

            if self.dry_run:
                self.log(f"Would update imports in: {py_file.name}")
                continue

            # Read file content
            with open(py_file, 'r') as f:
                content = f.read()

            # Update imports
            modified = False
            for old_import, new_import in import_updates:
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    modified = True
                    self.log(f"Updated import in {py_file.name}: {old_import} → {new_import}")

            # Write back if modified
            if modified:
                with open(py_file, 'w') as f:
                    f.write(content)

    def create_config_file(self):
        """Create config/settings.py"""
        content = '''"""Application configuration settings"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings"""

    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    CHANDRA_API_URL: str = os.getenv("CHANDRA_API_URL", "http://localhost:8000")

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    INPUT_DIR: Path = DATA_DIR / "input"
    OUTPUT_DIR: Path = DATA_DIR / "output"
    TEMP_DIR: Path = DATA_DIR / "temp"
    PROMPTS_DIR: Path = Path(__file__).parent.parent / "prompts"

    # OCR Settings
    OCR_SERVICE: str = os.getenv("OCR_SERVICE", "gemini")
    OCR_TIMEOUT: int = 300

    # LLM Settings
    LLM_MODEL: str = "gemini-3-flash-preview"
    LLM_TEMPERATURE: float = 0.0


# Global settings instance
settings = Settings()
'''
        config_path = self.src_dir / "config" / "settings.py"
        if self.dry_run:
            self.log(f"Would create: {config_path}")
        else:
            with open(config_path, 'w') as f:
                f.write(content)
            self.log(f"Created: {config_path}")

    def create_env_example(self):
        """Create .env.example file"""
        content = '''# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# OCR Service Configuration
OCR_SERVICE=gemini
CHANDRA_API_URL=http://localhost:8000

# LLM Configuration
LLM_MODEL=gemini-3-flash-preview
'''
        env_example_path = self.project_root / ".env.example"
        if self.dry_run:
            self.log(f"Would create: {env_example_path}")
        else:
            if not env_example_path.exists():
                with open(env_example_path, 'w') as f:
                    f.write(content)
                self.log(f"Created: {env_example_path}")

    def run_migration(self):
        """Execute full migration"""
        self.log("=" * 60)
        self.log("Starting Structure Migration")
        self.log("=" * 60)

        steps = [
            ("Creating backup", self.create_backup),
            ("Creating directory structure", self.create_directory_structure),
            ("Creating __init__ files", self.create_init_files),
            ("Creating src/__init__.py", self.create_src_init),
            ("Migrating service files", self.migrate_files),
            ("Migrating OCR service", self.migrate_ocr_service),
            ("Updating imports", self.update_imports),
            ("Creating config file", self.create_config_file),
            ("Creating .env.example", self.create_env_example),
        ]

        for step_name, step_func in steps:
            self.log(f"\n--- {step_name} ---")
            try:
                step_func()
            except Exception as e:
                self.log(f"Error in {step_name}: {e}", "ERROR")
                if not self.dry_run:
                    self.log("Migration failed. Check backup at: {self.backup_dir}", "ERROR")
                raise

        self.log("\n" + "=" * 60)
        if self.dry_run:
            self.log("DRY RUN COMPLETE - No changes made", "SUCCESS")
        else:
            self.log("MIGRATION COMPLETE!", "SUCCESS")
            self.log(f"Backup saved at: {self.backup_dir}")
        self.log("=" * 60)

    def rollback(self):
        """Rollback to most recent backup"""
        # Find most recent backup
        backups = sorted(self.project_root.glob(".migration_backup_*"))
        if not backups:
            self.log("No backups found!", "ERROR")
            return

        latest_backup = backups[-1]
        self.log(f"Rolling back to: {latest_backup}")

        if self.dry_run:
            self.log("Would restore from backup")
            return

        # Remove current src
        shutil.rmtree(self.src_dir)

        # Restore from backup
        shutil.copytree(latest_backup, self.src_dir)
        self.log("Rollback complete!", "SUCCESS")


def main():
    parser = argparse.ArgumentParser(description="Migrate src folder structure")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    parser.add_argument("--rollback", action="store_true", help="Rollback to previous backup")
    args = parser.parse_args()

    project_root = Path(__file__).parent
    migrator = StructureMigrator(project_root, dry_run=args.dry_run)

    if args.rollback:
        migrator.rollback()
    else:
        migrator.run_migration()


if __name__ == "__main__":
    main()

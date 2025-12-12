#!/usr/bin/env python3
"""
AnkiDungeon Addon Builder

This script builds the AnkiDungeon addon into an .ankiaddon package.
It provides a simplified interface to the anki-addon-builder library
while also supporting simple local builds.

Usage:
    python build.py                    # Simple local build
    python build.py --aab              # Use anki-addon-builder library
    python build.py --version 1.0.0    # Build specific version
    python build.py --clean            # Clean build directory
"""

import argparse
import json
import logging
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


class AnkiAddonBuilder:
    """Builder for AnkiDungeon addon packages."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the builder.
        
        Args:
            project_root: Root directory of the project (defaults to script location)
        """
        self.project_root = (project_root or Path(__file__).parent).resolve()
        self.src_dir = self.project_root / "src"
        self.build_dir = self.project_root / "build"
        self.addon_json = self.project_root / "addon.json"
        
        # Load addon configuration
        self._load_config()
        
        # Set module directory - use ankiweb_id as the folder name if available
        self.module_name = self.config.get("ankiweb_id", self.config.get("module_name", "ankiaddon"))
        self.repo_name = self.config.get("repo_name", "ankiaddon")
    
    def _load_config(self) -> None:
        """Load addon.json configuration."""
        if not self.addon_json.exists():
            raise FileNotFoundError(f"addon.json not found at {self.addon_json}")
        
        try:
            with open(self.addon_json) as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in addon.json: {e}")
        
        self.display_name = self.config.get("display_name", "ankiaddon")
    
    def validate(self) -> bool:
        """
        Validate project structure.
        
        Returns:
            True if valid
            
        Raises:
            FileNotFoundError: If required directories/files are missing
        """
        if not self.src_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.src_dir}")
        
        module_dir = self.src_dir / self.module_name
        if not module_dir.exists():
            raise FileNotFoundError(f"Module directory not found: {module_dir}")
        
        init_file = module_dir / "__init__.py"
        if not init_file.exists():
            raise FileNotFoundError(f"__init__.py not found: {init_file}")
        
        logger.info(f"✓ Project structure valid")
        logger.info(f"  Module: {self.module_name}")
        logger.info(f"  Source: {module_dir}")
        return True
    
    def clean(self) -> None:
        """Clean the build directory."""
        if self.build_dir.exists():
            logger.info(f"Cleaning build directory: {self.build_dir}")
            shutil.rmtree(self.build_dir)
        else:
            logger.info("Build directory not found, nothing to clean")
    
    def build_simple(self, version: str = "dev") -> Path:
        """
        Build addon using simple method (direct ZIP packaging).
        
        Args:
            version: Version string for the package
            
        Returns:
            Path to the created .ankiaddon file
        """
        self.validate()
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        module_dir = self.src_dir / self.module_name
        output_file = self.build_dir / f"{self.repo_name}-{version}.ankiaddon"
        
        # Remove existing package
        if output_file.exists():
            output_file.unlink()
            logger.info(f"Removed existing package")
        
        logger.info(f"\nBuilding addon package (simple method)...")
        logger.info(f"  Version: {version}")
        logger.info(f"  Output: {output_file}")
        
        # Create ZIP file
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            files_added = 0
            
            # Add all files from module directory
            # Per Anki documentation, the top-level folder should NOT be included in the zip
            for root, dirs, files in os.walk(module_dir):
                for file in files:
                    if file.startswith('.') or file.endswith('.pyc'):
                        continue
                    
                    file_path = Path(root) / file
                    # Calculate archive name relative to module directory (not src directory)
                    # This ensures files are at root of archive, not in a subfolder
                    arcname = str(file_path.relative_to(module_dir))
                    
                    zipf.write(file_path, arcname)
                    files_added += 1
        
        # Verify package
        if not output_file.exists():
            raise RuntimeError(f"Failed to create package")
        
        package_size = output_file.stat().st_size
        logger.info(f"\n✓ Build successful!")
        logger.info(f"  Files added: {files_added}")
        logger.info(f"  Package size: {package_size:,} bytes")
        
        return output_file
    
    def build_with_aab(self, version: str = "dev") -> Path:
        """
        Build addon using anki-addon-builder library.
        
        Args:
            version: Version string for the package
            
        Returns:
            Path to the created .ankiaddon file
            
        Raises:
            ImportError: If anki-addon-builder is not installed
        """
        try:
            # Import AAB components
            sys.path.insert(0, str(self.project_root))
            from aab.builder import AddonBuilder
            from aab.ui import QtVersion
        except ImportError as e:
            raise ImportError(
                f"anki-addon-builder not found. "
                f"Install it or use --simple flag instead. Error: {e}"
            )
        
        self.validate()
        
        logger.info(f"\nBuilding addon package (with anki-addon-builder)...")
        logger.info(f"  Version: {version}")
        
        try:
            builder = AddonBuilder(version=version)
            # Build with Qt5 and Qt6 targets
            output = builder.build(
                qt_versions=[QtVersion.qt5, QtVersion.qt6],
                disttype="local"
            )
            
            if output.exists():
                logger.info(f"✓ Build successful!")
                return output
            else:
                raise RuntimeError("AAB build failed, output file not found")
                
        except Exception as e:
            logger.error(f"AAB build failed: {e}")
            raise
    
    def list_contents(self, ankiaddon_file: Path) -> None:
        """
        List contents of an .ankiaddon package.
        
        Args:
            ankiaddon_file: Path to the .ankiaddon file
        """
        if not ankiaddon_file.exists():
            logger.error(f"File not found: {ankiaddon_file}")
            return
        
        logger.info(f"\nContents of {ankiaddon_file.name}:")
        try:
            with zipfile.ZipFile(ankiaddon_file, 'r') as zipf:
                for info in zipf.filelist:
                    logger.info(f"  {info.filename} ({info.file_size:,} bytes)")
        except zipfile.BadZipFile:
            logger.error(f"Invalid ZIP file: {ankiaddon_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build ankiaddon addon package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Simple build
  python build.py --clean            # Clean build directory
  python build.py --version 1.0.0    # Build with specific version
  python build.py --aab              # Use anki-addon-builder
  python build.py --list build/ankiaddon-dev.ankiaddon  # List contents
        """
    )
    
    parser.add_argument(
        "--simple",
        action="store_true",
        default=True,
        help="Use simple build method (default)"
    )
    parser.add_argument(
        "--aab",
        action="store_true",
        help="Use anki-addon-builder library for build"
    )
    parser.add_argument(
        "--version",
        default="dev",
        help="Version string for the package (default: dev)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directory before building"
    )
    parser.add_argument(
        "--list",
        metavar="FILE",
        help="List contents of an existing .ankiaddon package"
    )
    
    args = parser.parse_args()
    
    try:
        project_root = Path(__file__).parent
        builder = AnkiAddonBuilder(project_root)
        
        # Handle list operation
        if args.list:
            builder.list_contents(Path(args.list))
            return 0
        
        # Handle clean operation
        if args.clean:
            builder.clean()
        
        # Build addon
        if args.aab:
            logger.info("Using anki-addon-builder for build\n")
            output = builder.build_with_aab(version=args.version)
        else:
            logger.info("Using simple build method\n")
            output = builder.build_simple(version=args.version)
        
        logger.info(f"\nBuild complete: {output}")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Build failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

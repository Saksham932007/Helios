#!/usr/bin/env python3
"""
Helios Backup and Recovery Tool
Backup configurations, models, and restore system state
"""

import os
import json
import shutil
import tarfile
import argparse
from datetime import datetime
from pathlib import Path

class HeliosBackup:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.backup_dir = self.workspace_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, name=None):
        """Create a complete backup"""
        if not name:
            name = f"helios_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / f"{name}.tar.gz"
        
        print(f"Creating backup: {backup_path}")
        
        with tarfile.open(backup_path, "w:gz") as tar:
            # Backup configurations
            self._backup_configs(tar)
            
            # Backup extension source (compiled)
            self._backup_extension(tar)
            
            # Backup server code
            self._backup_server(tar)
            
            # Create manifest
            self._create_manifest(tar, name)
        
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    def _backup_configs(self, tar):
        """Backup configuration files"""
        config_files = [
            ".vscode/settings.json",
            ".vscode/launch.json", 
            ".vscode/tasks.json",
            "extension/package.json",
            "extension/tsconfig.json",
            "server/requirements.txt",
            "server/pyproject.toml"
        ]
        
        for config_file in config_files:
            file_path = self.workspace_path / config_file
            if file_path.exists():
                tar.add(file_path, arcname=f"configs/{config_file}")
    
    def _backup_extension(self, tar):
        """Backup extension files"""
        extension_dir = self.workspace_path / "extension"
        
        # Backup source
        src_dir = extension_dir / "src"
        if src_dir.exists():
            tar.add(src_dir, arcname="extension/src")
        
        # Backup compiled output
        out_dir = extension_dir / "out"
        if out_dir.exists():
            tar.add(out_dir, arcname="extension/out")
        
        # Backup package files
        for file in ["package.json", "tsconfig.json", ".eslintrc.json"]:
            file_path = extension_dir / file
            if file_path.exists():
                tar.add(file_path, arcname=f"extension/{file}")
    
    def _backup_server(self, tar):
        """Backup server files"""
        server_dir = self.workspace_path / "server"
        
        # Backup Python source
        python_files = [
            "main.py", "models.py", "inference.py", 
            "model_manager.py", "benchmark.py", "test_main.py"
        ]
        
        for py_file in python_files:
            file_path = server_dir / py_file
            if file_path.exists():
                tar.add(file_path, arcname=f"server/{py_file}")
        
        # Backup requirements and config
        for file in ["requirements.txt", "pyproject.toml", "Dockerfile"]:
            file_path = server_dir / file
            if file_path.exists():
                tar.add(file_path, arcname=f"server/{file}")
    
    def _create_manifest(self, tar, name):
        """Create backup manifest"""
        manifest = {
            "backup_name": name,
            "created_at": datetime.now().isoformat(),
            "workspace_path": str(self.workspace_path),
            "helios_version": "0.1.0",
            "contents": {
                "configs": True,
                "extension_source": True,
                "extension_compiled": True,
                "server_source": True
            }
        }
        
        manifest_path = self.backup_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        tar.add(manifest_path, arcname="manifest.json")
        manifest_path.unlink()  # Remove temp file
    
    def list_backups(self):
        """List available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.tar.gz"):
            try:
                with tarfile.open(backup_file, "r:gz") as tar:
                    if "manifest.json" in tar.getnames():
                        manifest_file = tar.extractfile("manifest.json")
                        manifest = json.load(manifest_file)
                        backups.append({
                            "file": backup_file.name,
                            "name": manifest.get("backup_name", "Unknown"),
                            "created_at": manifest.get("created_at", "Unknown"),
                            "size": backup_file.stat().st_size
                        })
            except Exception as e:
                print(f"Warning: Could not read backup {backup_file}: {e}")
        
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    def restore_backup(self, backup_name, target_path=None):
        """Restore from backup"""
        if target_path is None:
            target_path = self.workspace_path
        else:
            target_path = Path(target_path)
        
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        if not backup_file.exists():
            # Try to find by partial name
            matches = list(self.backup_dir.glob(f"*{backup_name}*.tar.gz"))
            if matches:
                backup_file = matches[0]
            else:
                raise FileNotFoundError(f"Backup not found: {backup_name}")
        
        print(f"Restoring backup from: {backup_file}")
        print(f"Restoring to: {target_path}")
        
        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)
        
        with tarfile.open(backup_file, "r:gz") as tar:
            # Extract all files
            tar.extractall(target_path)
        
        print("✅ Backup restored successfully")
        
        # Show manifest info
        manifest_path = target_path / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            print(f"Restored backup: {manifest.get('backup_name', 'Unknown')}")
            print(f"Created: {manifest.get('created_at', 'Unknown')}")
            print(f"Original path: {manifest.get('workspace_path', 'Unknown')}")
    
    def cleanup_old_backups(self, keep_count=5):
        """Remove old backups, keeping only the most recent ones"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            print(f"Only {len(backups)} backups found, nothing to clean up")
            return
        
        to_remove = backups[keep_count:]
        
        for backup in to_remove:
            backup_path = self.backup_dir / backup["file"]
            backup_path.unlink()
            print(f"Removed old backup: {backup['file']}")
        
        print(f"✅ Cleaned up {len(to_remove)} old backups")

def main():
    parser = argparse.ArgumentParser(description="Helios Backup and Recovery")
    parser.add_argument("--workspace", default=".", 
                       help="Workspace path (default: current directory)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create backup
    create_parser = subparsers.add_parser("create", help="Create backup")
    create_parser.add_argument("--name", help="Backup name")
    
    # List backups
    subparsers.add_parser("list", help="List backups")
    
    # Restore backup
    restore_parser = subparsers.add_parser("restore", help="Restore backup")
    restore_parser.add_argument("backup_name", help="Backup name to restore")
    restore_parser.add_argument("--target", help="Target path for restoration")
    
    # Cleanup backups
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup old backups")
    cleanup_parser.add_argument("--keep", type=int, default=5,
                               help="Number of backups to keep (default: 5)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    backup_tool = HeliosBackup(args.workspace)
    
    if args.command == "create":
        backup_tool.create_backup(args.name)
    
    elif args.command == "list":
        backups = backup_tool.list_backups()
        if backups:
            print("Available backups:")
            print("-" * 50)
            for backup in backups:
                size_mb = backup["size"] / (1024 * 1024)
                print(f"{backup['name']}")
                print(f"  File: {backup['file']}")
                print(f"  Created: {backup['created_at']}")
                print(f"  Size: {size_mb:.1f} MB")
                print()
        else:
            print("No backups found")
    
    elif args.command == "restore":
        backup_tool.restore_backup(args.backup_name, args.target)
    
    elif args.command == "cleanup":
        backup_tool.cleanup_old_backups(args.keep)

if __name__ == "__main__":
    main()
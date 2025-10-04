"""
Script de migração para mover arquivos da estrutura antiga para a nova estrutura centralizada.
Executa a migração de forma segura com backup e validação.
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.utils.centralized_file_manager import CentralizedFileManager, FileLocations


class FileMigrationScript:
    """Script para migração segura de arquivos para nova estrutura."""
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize migration script.
        
        Args:
            dry_run: If True, only reports what would be done without making changes
        """
        self.dry_run = dry_run
        self.base_path = Path(".")
        self.file_manager = CentralizedFileManager()
        self.migration_log = []
        
        # Define migration mappings
        self.migrations = [
            {
                "name": "Azure Figures Images",
                "source": "tests/images/by_provider/azure_figures",
                "target": FileLocations.DOCUMENTS_IMAGES_AZURE_ENDPOINT,
                "description": "Move Azure Document Intelligence extracted images"
            },
            {
                "name": "Manual PDF Images", 
                "source": "tests/images/by_provider/azure_manual",
                "target": FileLocations.DOCUMENTS_IMAGES_AZURE_MANUAL,
                "description": "Move manual PDF cropped images"
            },
            {
                "name": "Manual PDF Images (Alternative)",
                "source": "tests/images/by_provider/manual_pdf", 
                "target": FileLocations.DOCUMENTS_IMAGES_AZURE_MANUAL,
                "description": "Move alternative manual PDF images"
            },
            {
                "name": "Azure Responses",
                "source": "tests/responses/azure",
                "target": FileLocations.DOCUMENTS_RESPONSES,
                "description": "Move Azure processing responses"
            },
            {
                "name": "Legacy Documents",
                "source": "tests/documents",
                "target": FileLocations.DOCUMENTS_ORIGINAL,
                "description": "Consolidate document files",
                "merge_mode": True  # Don't overwrite existing structure
            }
        ]
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "error"
    
    def log_action(self, action: str, source: str, target: str, status: str, details: str = ""):
        """Log migration action."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "source": source,
            "target": target,
            "status": status,
            "details": details
        }
        self.migration_log.append(entry)
        
        # Print to console
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "📋"
        print(f"  {status_icon} {action}: {source} → {target}")
        if details:
            print(f"      {details}")
    
    def migrate_directory(self, migration: dict) -> dict:
        """
        Migrate a directory according to migration configuration.
        
        Returns:
            Dictionary with migration results
        """
        source_path = Path(migration["source"])
        target_location = migration["target"]
        merge_mode = migration.get("merge_mode", False)
        
        results = {
            "migration_name": migration["name"],
            "files_found": 0,
            "files_migrated": 0,
            "files_skipped": 0,
            "files_failed": 0,
            "total_size": 0
        }
        
        print(f"\n📂 {migration['name']}: {migration['description']}")
        print(f"   Source: {source_path}")
        print(f"   Target: {target_location}")
        
        if not source_path.exists():
            print(f"   ⚠️  Source directory does not exist, skipping...")
            self.log_action("skip_directory", str(source_path), target_location, "info", "Source does not exist")
            return results
        
        # Get target directory
        target_path = self.file_manager.get_path(target_location)
        
        # Find all files in source
        all_files = []
        for root, dirs, files in os.walk(source_path):
            for file in files:
                file_path = Path(root) / file
                all_files.append(file_path)
        
        results["files_found"] = len(all_files)
        print(f"   📄 Found {len(all_files)} files to migrate")
        
        if len(all_files) == 0:
            print(f"   ℹ️  No files to migrate")
            return results
        
        # Process each file
        for file_path in all_files:
            try:
                # Calculate relative path from source
                rel_path = file_path.relative_to(source_path)
                target_file_path = target_path / rel_path
                
                # Get file size
                file_size = file_path.stat().st_size
                results["total_size"] += file_size
                
                # Check if target already exists
                if target_file_path.exists():
                    if merge_mode:
                        # In merge mode, compare checksums
                        source_checksum = self.calculate_checksum(file_path)
                        target_checksum = self.calculate_checksum(target_file_path)
                        
                        if source_checksum == target_checksum:
                            results["files_skipped"] += 1
                            self.log_action("skip_file", str(file_path), str(target_file_path), "info", "Identical file exists")
                            continue
                        else:
                            # Create backup of existing file
                            backup_path = target_file_path.with_suffix(f"{target_file_path.suffix}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                            if not self.dry_run:
                                shutil.copy2(target_file_path, backup_path)
                            self.log_action("backup_file", str(target_file_path), str(backup_path), "success", "Existing file backed up")
                    else:
                        results["files_skipped"] += 1
                        self.log_action("skip_file", str(file_path), str(target_file_path), "info", "Target already exists")
                        continue
                
                # Create target directory if needed
                target_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                if not self.dry_run:
                    # Copy file (don't move, keep original as backup)
                    shutil.copy2(file_path, target_file_path)
                    
                    # Verify copy
                    if target_file_path.exists():
                        source_checksum = self.calculate_checksum(file_path)
                        target_checksum = self.calculate_checksum(target_file_path)
                        
                        if source_checksum == target_checksum:
                            results["files_migrated"] += 1
                            self.log_action("migrate_file", str(file_path), str(target_file_path), "success", f"{file_size} bytes")
                        else:
                            results["files_failed"] += 1
                            self.log_action("migrate_file", str(file_path), str(target_file_path), "error", "Checksum mismatch")
                    else:
                        results["files_failed"] += 1
                        self.log_action("migrate_file", str(file_path), str(target_file_path), "error", "File not created")
                else:
                    # Dry run - just log what would be done
                    results["files_migrated"] += 1
                    self.log_action("would_migrate", str(file_path), str(target_file_path), "info", f"{file_size} bytes (DRY RUN)")
                
            except Exception as e:
                results["files_failed"] += 1
                self.log_action("migrate_file", str(file_path), "unknown", "error", str(e))
        
        return results
    
    def generate_report(self, all_results: list):
        """Generate migration report."""
        
        print("\n" + "=" * 60)
        print("📊 MIGRATION REPORT")
        print("=" * 60)
        
        total_files_found = sum(r["files_found"] for r in all_results)
        total_files_migrated = sum(r["files_migrated"] for r in all_results)
        total_files_skipped = sum(r["files_skipped"] for r in all_results)
        total_files_failed = sum(r["files_failed"] for r in all_results)
        total_size = sum(r["total_size"] for r in all_results)
        
        print(f"📄 Total files found: {total_files_found}")
        print(f"✅ Files migrated: {total_files_migrated}")
        print(f"⏭️  Files skipped: {total_files_skipped}")
        print(f"❌ Files failed: {total_files_failed}")
        print(f"💾 Total size: {total_size / 1024 / 1024:.2f} MB")
        print(f"🔧 Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        
        print(f"\n📋 Details by migration:")
        for result in all_results:
            print(f"  {result['migration_name']}:")
            print(f"    Found: {result['files_found']}, Migrated: {result['files_migrated']}, Skipped: {result['files_skipped']}, Failed: {result['files_failed']}")
        
        # Save detailed log
        log_filename = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_filename, 'w') as f:
            json.dump({
                "summary": {
                    "total_files_found": total_files_found,
                    "total_files_migrated": total_files_migrated,
                    "total_files_skipped": total_files_skipped,
                    "total_files_failed": total_files_failed,
                    "total_size_bytes": total_size,
                    "dry_run": self.dry_run,
                    "timestamp": datetime.now().isoformat()
                },
                "results": all_results,
                "detailed_log": self.migration_log
            }, f, indent=2)
        
        print(f"\n📄 Detailed log saved to: {log_filename}")
        
        return total_files_failed == 0
    
    def run_migration(self):
        """Execute the complete migration process."""
        
        print("🚀 FILE STRUCTURE MIGRATION")
        print("=" * 60)
        print(f"🔧 Mode: {'DRY RUN (no changes will be made)' if self.dry_run else 'LIVE MIGRATION'}")
        print(f"📁 Base path: {self.base_path.absolute()}")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Ensure centralized directory structure exists
        print(f"\n📂 Ensuring centralized directory structure...")
        storage_info = self.file_manager.get_storage_info()
        for dir_name, dir_info in storage_info["directories"].items():
            if dir_info["exists"]:
                print(f"  ✅ {dir_name}: {dir_info['path']}")
            else:
                print(f"  ❌ {dir_name}: {dir_info['path']} (missing)")
        
        # Execute migrations
        all_results = []
        for migration in self.migrations:
            result = self.migrate_directory(migration)
            all_results.append(result)
        
        # Generate report
        success = self.generate_report(all_results)
        
        if self.dry_run:
            print(f"\n🔍 This was a DRY RUN. To execute the migration, run:")
            print(f"    python {__file__} --live")
        elif success:
            print(f"\n🎉 Migration completed successfully!")
            print(f"\n📋 Next steps:")
            print(f"   1. Set USE_CENTRAL_FILE_MANAGER=true")
            print(f"   2. Test applications with centralized file system")
            print(f"   3. Verify all files are accessible")
            print(f"   4. Archive old directory structure when satisfied")
        else:
            print(f"\n⚠️  Migration completed with errors. Check the log for details.")
        
        return success


def main():
    """Main execution function."""
    
    import argparse
    parser = argparse.ArgumentParser(description="Migrate file structure to centralized system")
    parser.add_argument("--live", action="store_true", help="Execute live migration (default is dry run)")
    parser.add_argument("--base-path", type=str, help="Base path for migration (default: current directory)")
    
    args = parser.parse_args()
    
    # Create migration script
    dry_run = not args.live
    migration_script = FileMigrationScript(dry_run=dry_run)
    
    if args.base_path:
        migration_script.base_path = Path(args.base_path)
    
    # Execute migration
    success = migration_script.run_migration()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
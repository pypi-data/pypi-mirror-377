"""
ProServe API Storage - Storage Management for Manifest Projects
Handles storage, retrieval, and persistence of manifest projects
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import structlog

from .models import ManifestProject, ProjectFilter, ProjectStats, calculate_project_stats


logger = structlog.get_logger(__name__)


class ManifestStore:
    """In-memory storage for manifest projects with persistence support"""
    
    def __init__(self, persist_dir: Optional[Path] = None):
        self._projects: Dict[str, ManifestProject] = {}
        self._persist_dir = persist_dir
        
        if self._persist_dir:
            self._persist_dir.mkdir(parents=True, exist_ok=True)
            self._load_persisted_projects()
    
    def create_project(self, project: ManifestProject) -> None:
        """Store a new project"""
        if project.id in self._projects:
            raise ValueError(f"Project with ID {project.id} already exists")
        
        self._projects[project.id] = project
        logger.info(f"Created project: {project.name} ({project.id})")
        
        if self._persist_dir:
            self._persist_project(project)
    
    def get_project(self, project_id: str) -> Optional[ManifestProject]:
        """Retrieve project by ID"""
        return self._projects.get(project_id)
    
    def update_project(self, project: ManifestProject) -> bool:
        """Update existing project"""
        if project.id not in self._projects:
            return False
        
        project.update_timestamp()
        self._projects[project.id] = project
        logger.info(f"Updated project: {project.name} ({project.id})")
        
        if self._persist_dir:
            self._persist_project(project)
        
        return True
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project by ID"""
        if project_id not in self._projects:
            return False
        
        project = self._projects[project_id]
        del self._projects[project_id]
        logger.info(f"Deleted project: {project.name} ({project_id})")
        
        if self._persist_dir:
            self._remove_persisted_project(project_id)
        
        return True
    
    def list_projects(self, filter_criteria: Optional[ProjectFilter] = None) -> List[ManifestProject]:
        """List all projects with optional filtering"""
        projects = list(self._projects.values())
        
        if filter_criteria:
            projects = [p for p in projects if filter_criteria.matches(p)]
        
        # Sort by updated_at descending (most recent first)
        projects.sort(key=lambda p: p.updated_at, reverse=True)
        
        return projects
    
    def get_project_summaries(self, filter_criteria: Optional[ProjectFilter] = None) -> List[Dict[str, Any]]:
        """Get project summaries without full manifests"""
        projects = self.list_projects(filter_criteria)
        return [p.get_summary() for p in projects]
    
    def search_projects(self, query: str) -> List[ManifestProject]:
        """Search projects by name, description, or tags"""
        query_lower = query.lower()
        matching_projects = []
        
        for project in self._projects.values():
            # Search in name
            if query_lower in project.name.lower():
                matching_projects.append(project)
                continue
            
            # Search in description
            if query_lower in project.description.lower():
                matching_projects.append(project)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in project.tags):
                matching_projects.append(project)
                continue
            
            # Search in author
            if query_lower in project.author.lower():
                matching_projects.append(project)
                continue
        
        return matching_projects
    
    def get_projects_by_status(self, status: str) -> List[ManifestProject]:
        """Get all projects with specific status"""
        return [p for p in self._projects.values() if p.status == status]
    
    def get_projects_by_author(self, author: str) -> List[ManifestProject]:
        """Get all projects by specific author"""
        return [p for p in self._projects.values() if p.author == author]
    
    def get_projects_by_tag(self, tag: str) -> List[ManifestProject]:
        """Get all projects containing specific tag"""
        return [p for p in self._projects.values() if tag in p.tags]
    
    def get_all_tags(self) -> Set[str]:
        """Get all unique tags across projects"""
        tags = set()
        for project in self._projects.values():
            tags.update(project.tags)
        return tags
    
    def get_all_authors(self) -> Set[str]:
        """Get all unique authors across projects"""
        return {p.author for p in self._projects.values() if p.author}
    
    def get_statistics(self) -> ProjectStats:
        """Get storage statistics"""
        return calculate_project_stats(list(self._projects.values()))
    
    def duplicate_project(self, project_id: str, new_name: str = None) -> Optional[ManifestProject]:
        """Create a duplicate of an existing project"""
        original = self.get_project(project_id)
        if not original:
            return None
        
        # Create new project with copied data
        duplicate = ManifestProject(
            id="",  # Will be auto-generated
            name=new_name or f"{original.name} (Copy)",
            description=original.description,
            version=original.version,
            created_at="",  # Will be auto-generated
            updated_at="",  # Will be auto-generated
            author=original.author,
            tags=original.tags.copy(),
            manifest=original.manifest.copy(),
            status='draft'  # Always start as draft
        )
        
        self.create_project(duplicate)
        logger.info(f"Duplicated project {original.name} -> {duplicate.name}")
        return duplicate
    
    def export_all_projects(self) -> Dict[str, Any]:
        """Export all projects to a dictionary"""
        return {
            'export_timestamp': datetime.now().isoformat(),
            'total_projects': len(self._projects),
            'projects': [p.to_dict() for p in self._projects.values()]
        }
    
    def import_projects(self, data: Dict[str, Any], overwrite: bool = False) -> Dict[str, Any]:
        """Import projects from exported data"""
        imported_count = 0
        skipped_count = 0
        error_count = 0
        errors = []
        
        projects_data = data.get('projects', [])
        
        for project_data in projects_data:
            try:
                project = ManifestProject.from_dict(project_data)
                
                # Check if project already exists
                if project.id in self._projects:
                    if overwrite:
                        self.update_project(project)
                        imported_count += 1
                    else:
                        skipped_count += 1
                else:
                    self.create_project(project)
                    imported_count += 1
                    
            except Exception as e:
                error_count += 1
                errors.append(f"Failed to import project: {str(e)}")
        
        result = {
            'imported': imported_count,
            'skipped': skipped_count,
            'errors': error_count,
            'error_details': errors
        }
        
        logger.info(f"Import completed: {result}")
        return result
    
    def clear_all_projects(self):
        """Clear all projects (use with caution!)"""
        count = len(self._projects)
        self._projects.clear()
        
        if self._persist_dir:
            # Remove all persisted project files
            for project_file in self._persist_dir.glob("*.json"):
                project_file.unlink()
        
        logger.warning(f"Cleared all {count} projects")
    
    def _persist_project(self, project: ManifestProject):
        """Persist project to disk"""
        if not self._persist_dir:
            return
        
        project_file = self._persist_dir / f"{project.id}.json"
        try:
            with open(project_file, 'w') as f:
                json.dump(project.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist project {project.id}: {e}")
    
    def _remove_persisted_project(self, project_id: str):
        """Remove persisted project file"""
        if not self._persist_dir:
            return
        
        project_file = self._persist_dir / f"{project_id}.json"
        try:
            if project_file.exists():
                project_file.unlink()
        except Exception as e:
            logger.error(f"Failed to remove persisted project {project_id}: {e}")
    
    def _load_persisted_projects(self):
        """Load persisted projects from disk"""
        if not self._persist_dir or not self._persist_dir.exists():
            return
        
        loaded_count = 0
        error_count = 0
        
        for project_file in self._persist_dir.glob("*.json"):
            try:
                with open(project_file, 'r') as f:
                    data = json.load(f)
                
                project = ManifestProject.from_dict(data)
                self._projects[project.id] = project
                loaded_count += 1
                
            except Exception as e:
                logger.error(f"Failed to load project from {project_file}: {e}")
                error_count += 1
        
        logger.info(f"Loaded {loaded_count} persisted projects, {error_count} errors")


class AsyncManifestStore:
    """Async wrapper for ManifestStore with concurrent access support"""
    
    def __init__(self, persist_dir: Optional[Path] = None):
        self._store = ManifestStore(persist_dir)
        self._lock = asyncio.Lock()
    
    async def create_project(self, project: ManifestProject) -> None:
        """Async create project"""
        async with self._lock:
            self._store.create_project(project)
    
    async def get_project(self, project_id: str) -> Optional[ManifestProject]:
        """Async get project"""
        async with self._lock:
            return self._store.get_project(project_id)
    
    async def update_project(self, project: ManifestProject) -> bool:
        """Async update project"""
        async with self._lock:
            return self._store.update_project(project)
    
    async def delete_project(self, project_id: str) -> bool:
        """Async delete project"""
        async with self._lock:
            return self._store.delete_project(project_id)
    
    async def list_projects(self, filter_criteria: Optional[ProjectFilter] = None) -> List[ManifestProject]:
        """Async list projects"""
        async with self._lock:
            return self._store.list_projects(filter_criteria)
    
    async def get_project_summaries(self, filter_criteria: Optional[ProjectFilter] = None) -> List[Dict[str, Any]]:
        """Async get project summaries"""
        async with self._lock:
            return self._store.get_project_summaries(filter_criteria)
    
    async def search_projects(self, query: str) -> List[ManifestProject]:
        """Async search projects"""
        async with self._lock:
            return self._store.search_projects(query)
    
    async def get_statistics(self) -> ProjectStats:
        """Async get statistics"""
        async with self._lock:
            return self._store.get_statistics()
    
    async def duplicate_project(self, project_id: str, new_name: str = None) -> Optional[ManifestProject]:
        """Async duplicate project"""
        async with self._lock:
            return self._store.duplicate_project(project_id, new_name)
    
    async def export_all_projects(self) -> Dict[str, Any]:
        """Async export all projects"""
        async with self._lock:
            return self._store.export_all_projects()
    
    async def import_projects(self, data: Dict[str, Any], overwrite: bool = False) -> Dict[str, Any]:
        """Async import projects"""
        async with self._lock:
            return self._store.import_projects(data, overwrite)
    
    # Expose synchronous methods for simple operations
    def get_all_tags(self) -> Set[str]:
        """Get all tags (synchronous)"""
        return self._store.get_all_tags()
    
    def get_all_authors(self) -> Set[str]:
        """Get all authors (synchronous)"""
        return self._store.get_all_authors()


# Utility functions for storage operations
def create_in_memory_store() -> ManifestStore:
    """Create in-memory store without persistence"""
    return ManifestStore()


def create_persistent_store(data_dir: Path) -> ManifestStore:
    """Create persistent store with file system storage"""
    return ManifestStore(persist_dir=data_dir)


def create_async_store(data_dir: Optional[Path] = None) -> AsyncManifestStore:
    """Create async store with optional persistence"""
    return AsyncManifestStore(persist_dir=data_dir)


def migrate_storage_format(old_store: ManifestStore, new_store: ManifestStore) -> Dict[str, Any]:
    """Migrate projects from one store format to another"""
    export_data = old_store.export_all_projects()
    return new_store.import_projects(export_data, overwrite=True)

"""
ProServe API Models - Data Models for Manifest API
Defines data structures and models used by the manifest API server
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class ManifestProject:
    """Represents a manifest project with metadata"""
    id: str
    name: str
    description: str
    version: str
    created_at: str
    updated_at: str
    author: str
    tags: List[str]
    manifest: Dict[str, Any]
    status: str = 'draft'  # draft, published, archived
    
    def __post_init__(self):
        """Validate project data after initialization"""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.status not in ['draft', 'published', 'archived']:
            raise ValueError(f"Invalid status: {self.status}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'author': self.author,
            'tags': self.tags,
            'manifest': self.manifest,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ManifestProject':
        """Create from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
            author=data.get('author', ''),
            tags=data.get('tags', []),
            manifest=data.get('manifest', {}),
            status=data.get('status', 'draft')
        )
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()
    
    def add_tag(self, tag: str):
        """Add a tag if not already present"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.update_timestamp()
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag if present"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.update_timestamp()
            return True
        return False
    
    def update_manifest(self, manifest: Dict[str, Any]):
        """Update the manifest and timestamp"""
        self.manifest = manifest
        self.update_timestamp()
    
    def change_status(self, new_status: str):
        """Change project status"""
        if new_status not in ['draft', 'published', 'archived']:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
        self.update_timestamp()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get project summary without full manifest"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'author': self.author,
            'tags': self.tags,
            'status': self.status,
            'manifest_size': len(json.dumps(self.manifest))
        }
    
    def export_to_file(self, file_path: Path, format_type: str = 'json'):
        """Export project to file"""
        if format_type.lower() == 'json':
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    @classmethod
    def import_from_file(cls, file_path: Path) -> 'ManifestProject':
        """Import project from file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass
class APIResponse:
    """Standard API response structure"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        result = {
            'success': self.success,
            'timestamp': self.timestamp
        }
        
        if self.data is not None:
            result['data'] = self.data
        if self.error:
            result['error'] = self.error
        if self.message:
            result['message'] = self.message
            
        return result
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = None) -> 'APIResponse':
        """Create success response"""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error_response(cls, error: str, message: str = None) -> 'APIResponse':
        """Create error response"""
        return cls(success=False, error=error, message=message)


@dataclass
class ProjectFilter:
    """Filter criteria for project queries"""
    status: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    name_contains: Optional[str] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None
    
    def matches(self, project: ManifestProject) -> bool:
        """Check if project matches filter criteria"""
        if self.status and project.status != self.status:
            return False
        
        if self.author and self.author.lower() not in project.author.lower():
            return False
        
        if self.tags:
            if not any(tag in project.tags for tag in self.tags):
                return False
        
        if self.name_contains and self.name_contains.lower() not in project.name.lower():
            return False
        
        if self.created_after:
            try:
                created_dt = datetime.fromisoformat(project.created_at)
                filter_dt = datetime.fromisoformat(self.created_after)
                if created_dt < filter_dt:
                    return False
            except ValueError:
                pass  # Skip invalid date filters
        
        if self.created_before:
            try:
                created_dt = datetime.fromisoformat(project.created_at)
                filter_dt = datetime.fromisoformat(self.created_before)
                if created_dt > filter_dt:
                    return False
            except ValueError:
                pass  # Skip invalid date filters
        
        return True
    
    @classmethod
    def from_query_params(cls, params: Dict[str, str]) -> 'ProjectFilter':
        """Create filter from query parameters"""
        tags = []
        if 'tags' in params:
            tags = [tag.strip() for tag in params['tags'].split(',') if tag.strip()]
        
        return cls(
            status=params.get('status'),
            author=params.get('author'),
            tags=tags,
            name_contains=params.get('name_contains'),
            created_after=params.get('created_after'),
            created_before=params.get('created_before')
        )


@dataclass
class ProjectStats:
    """Statistics about projects"""
    total_projects: int
    draft_projects: int
    published_projects: int
    archived_projects: int
    unique_authors: int
    unique_tags: int
    total_endpoints: int
    avg_endpoints_per_project: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_projects': self.total_projects,
            'draft_projects': self.draft_projects,
            'published_projects': self.published_projects,
            'archived_projects': self.archived_projects,
            'unique_authors': self.unique_authors,
            'unique_tags': self.unique_tags,
            'total_endpoints': self.total_endpoints,
            'avg_endpoints_per_project': self.avg_endpoints_per_project
        }


@dataclass
class ValidationResult:
    """Result of manifest validation"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'valid': self.valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions
        }
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)
    
    def add_suggestion(self, suggestion: str):
        """Add validation suggestion"""
        self.suggestions.append(suggestion)


# Utility functions for model operations
def create_project_from_manifest(manifest: Dict[str, Any], 
                                author: str = "Unknown",
                                name: str = None,
                                description: str = None) -> ManifestProject:
    """Create a ManifestProject from a manifest dictionary"""
    project_name = name or manifest.get('name', 'Untitled Project')
    project_description = description or manifest.get('description', '')
    
    return ManifestProject(
        id=str(uuid.uuid4()),
        name=project_name,
        description=project_description,
        version=manifest.get('version', '1.0.0'),
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        author=author,
        tags=[],
        manifest=manifest,
        status='draft'
    )


def calculate_project_stats(projects: List[ManifestProject]) -> ProjectStats:
    """Calculate statistics for a list of projects"""
    if not projects:
        return ProjectStats(0, 0, 0, 0, 0, 0, 0, 0.0)
    
    total = len(projects)
    draft = sum(1 for p in projects if p.status == 'draft')
    published = sum(1 for p in projects if p.status == 'published')
    archived = sum(1 for p in projects if p.status == 'archived')
    
    authors = set(p.author for p in projects if p.author)
    all_tags = set()
    total_endpoints = 0
    
    for project in projects:
        all_tags.update(project.tags)
        endpoints = project.manifest.get('endpoints', [])
        total_endpoints += len(endpoints) if isinstance(endpoints, list) else 0
    
    avg_endpoints = total_endpoints / total if total > 0 else 0.0
    
    return ProjectStats(
        total_projects=total,
        draft_projects=draft,
        published_projects=published,
        archived_projects=archived,
        unique_authors=len(authors),
        unique_tags=len(all_tags),
        total_endpoints=total_endpoints,
        avg_endpoints_per_project=avg_endpoints
    )


def validate_project_data(data: Dict[str, Any]) -> ValidationResult:
    """Validate project data"""
    result = ValidationResult(valid=True)
    
    # Required fields
    required_fields = ['name']
    for field in required_fields:
        if not data.get(field):
            result.add_error(f"Required field '{field}' is missing or empty")
    
    # Name validation
    name = data.get('name', '')
    if name and len(name) > 100:
        result.add_warning("Project name is very long (>100 characters)")
    
    # Version validation
    version = data.get('version', '1.0.0')
    if version and not isinstance(version, str):
        result.add_error("Version must be a string")
    
    # Tags validation
    tags = data.get('tags', [])
    if tags and not isinstance(tags, list):
        result.add_error("Tags must be a list")
    elif tags:
        for tag in tags:
            if not isinstance(tag, str):
                result.add_error("All tags must be strings")
                break
    
    # Status validation
    status = data.get('status', 'draft')
    if status not in ['draft', 'published', 'archived']:
        result.add_error(f"Invalid status: {status}")
    
    # Manifest validation
    manifest = data.get('manifest')
    if manifest and not isinstance(manifest, dict):
        result.add_error("Manifest must be a dictionary")
    elif manifest:
        # Basic manifest structure validation
        if 'name' not in manifest:
            result.add_suggestion("Consider adding a 'name' field to the manifest")
        if 'version' not in manifest:
            result.add_suggestion("Consider adding a 'version' field to the manifest")
    
    return result

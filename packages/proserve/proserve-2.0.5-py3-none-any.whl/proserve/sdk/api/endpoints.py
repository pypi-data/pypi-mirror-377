"""
ProServe API Endpoints - HTTP API Endpoint Handlers
Handles all HTTP endpoints for the manifest API server
"""

import json
import yaml
from typing import Dict, Any, Optional
from aiohttp import web
from aiohttp.web import Request, Response, json_response
import structlog

from .models import ManifestProject, ProjectFilter, APIResponse, ValidationResult, validate_project_data
from .storage import AsyncManifestStore
from ..builders.manifest_builder import ManifestBuilder, from_template, TEMPLATES
from ..validators.manifest_validator import validate_manifest_comprehensive


logger = structlog.get_logger(__name__)


class ManifestAPIEndpoints:
    """HTTP endpoint handlers for manifest API"""
    
    def __init__(self, store: AsyncManifestStore):
        self.store = store
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        stats = await self.store.get_statistics()
        
        response_data = {
            'status': 'healthy',
            'service': 'ProServe Manifest API',
            'version': '1.0.0',
            'timestamp': APIResponse.success_response().timestamp,
            'projects': {
                'total': stats.total_projects,
                'draft': stats.draft_projects,
                'published': stats.published_projects
            }
        }
        
        return json_response(APIResponse.success_response(response_data).to_dict())
    
    async def list_projects(self, request: Request) -> Response:
        """List all projects with optional filtering"""
        try:
            # Parse query parameters for filtering
            query_params = dict(request.query)
            project_filter = ProjectFilter.from_query_params(query_params)
            
            # Check if only summaries are requested
            summaries_only = query_params.get('summaries', '').lower() in ['true', '1', 'yes']
            
            if summaries_only:
                projects = await self.store.get_project_summaries(project_filter)
            else:
                projects_list = await self.store.list_projects(project_filter)
                projects = [p.to_dict() for p in projects_list]
            
            # Add pagination info if requested
            page = int(query_params.get('page', 1))
            per_page = int(query_params.get('per_page', 50))
            
            if page > 1 or per_page < len(projects):
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                paginated_projects = projects[start_idx:end_idx]
                
                response_data = {
                    'projects': paginated_projects,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': len(projects),
                        'total_pages': (len(projects) + per_page - 1) // per_page
                    }
                }
            else:
                response_data = {
                    'projects': projects,
                    'total': len(projects)
                }
            
            return json_response(APIResponse.success_response(response_data).to_dict())
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to list projects").to_dict(),
                status=500
            )
    
    async def create_project(self, request: Request) -> Response:
        """Create new project"""
        try:
            data = await request.json()
            
            # Validate project data
            validation = validate_project_data(data)
            if not validation.valid:
                return json_response(
                    APIResponse.error_response("Validation failed", str(validation.errors)).to_dict(),
                    status=400
                )
            
            # Create project
            project = ManifestProject.from_dict(data)
            await self.store.create_project(project)
            
            logger.info(f"Created new project: {project.name} ({project.id})")
            
            return json_response(
                APIResponse.success_response(
                    project.to_dict(), 
                    f"Project '{project.name}' created successfully"
                ).to_dict(),
                status=201
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to create project").to_dict(),
                status=500
            )
    
    async def get_project(self, request: Request) -> Response:
        """Get project by ID"""
        try:
            project_id = request.match_info['project_id']
            project = await self.store.get_project(project_id)
            
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            return json_response(APIResponse.success_response(project.to_dict()).to_dict())
            
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to get project").to_dict(),
                status=500
            )
    
    async def update_project(self, request: Request) -> Response:
        """Update existing project"""
        try:
            project_id = request.match_info['project_id']
            data = await request.json()
            
            # Get existing project
            existing_project = await self.store.get_project(project_id)
            if not existing_project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            # Validate updated data
            validation = validate_project_data(data)
            if not validation.valid:
                return json_response(
                    APIResponse.error_response("Validation failed", str(validation.errors)).to_dict(),
                    status=400
                )
            
            # Update project (preserve ID and creation time)
            data['id'] = existing_project.id
            data['created_at'] = existing_project.created_at
            
            updated_project = ManifestProject.from_dict(data)
            success = await self.store.update_project(updated_project)
            
            if not success:
                return json_response(
                    APIResponse.error_response("Update failed", "Failed to update project").to_dict(),
                    status=500
                )
            
            logger.info(f"Updated project: {updated_project.name} ({project_id})")
            
            return json_response(
                APIResponse.success_response(
                    updated_project.to_dict(),
                    f"Project '{updated_project.name}' updated successfully"
                ).to_dict()
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to update project").to_dict(),
                status=500
            )
    
    async def delete_project(self, request: Request) -> Response:
        """Delete project by ID"""
        try:
            project_id = request.match_info['project_id']
            
            # Check if project exists
            project = await self.store.get_project(project_id)
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            success = await self.store.delete_project(project_id)
            
            if not success:
                return json_response(
                    APIResponse.error_response("Delete failed", "Failed to delete project").to_dict(),
                    status=500
                )
            
            logger.info(f"Deleted project: {project.name} ({project_id})")
            
            return json_response(
                APIResponse.success_response(
                    None,
                    f"Project '{project.name}' deleted successfully"
                ).to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to delete project").to_dict(),
                status=500
            )
    
    async def update_manifest(self, request: Request) -> Response:
        """Update project manifest"""
        try:
            project_id = request.match_info['project_id']
            manifest_data = await request.json()
            
            # Get existing project
            project = await self.store.get_project(project_id)
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            # Update manifest
            project.update_manifest(manifest_data)
            success = await self.store.update_project(project)
            
            if not success:
                return json_response(
                    APIResponse.error_response("Update failed", "Failed to update manifest").to_dict(),
                    status=500
                )
            
            logger.info(f"Updated manifest for project: {project.name} ({project_id})")
            
            return json_response(
                APIResponse.success_response(
                    project.manifest,
                    "Manifest updated successfully"
                ).to_dict()
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error updating manifest: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to update manifest").to_dict(),
                status=500
            )
    
    async def export_yaml(self, request: Request) -> Response:
        """Export manifest as YAML"""
        try:
            project_id = request.match_info['project_id']
            project = await self.store.get_project(project_id)
            
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            # Convert to YAML
            yaml_content = yaml.dump(project.manifest, default_flow_style=False, indent=2)
            
            return Response(
                text=yaml_content,
                headers={
                    'Content-Type': 'application/x-yaml',
                    'Content-Disposition': f'attachment; filename="{project.name}.yml"'
                }
            )
            
        except Exception as e:
            logger.error(f"Error exporting YAML: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to export YAML").to_dict(),
                status=500
            )
    
    async def export_json(self, request: Request) -> Response:
        """Export manifest as JSON"""
        try:
            project_id = request.match_info['project_id']
            project = await self.store.get_project(project_id)
            
            if not project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            # Convert to formatted JSON
            json_content = json.dumps(project.manifest, indent=2)
            
            return Response(
                text=json_content,
                headers={
                    'Content-Type': 'application/json',
                    'Content-Disposition': f'attachment; filename="{project.name}.json"'
                }
            )
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to export JSON").to_dict(),
                status=500
            )
    
    async def list_templates(self, request: Request) -> Response:
        """List available templates"""
        try:
            templates_info = {}
            
            for name, template_class in TEMPLATES.items():
                templates_info[name] = {
                    'name': name,
                    'description': getattr(template_class, '__doc__', f'Template for {name} services'),
                    'class': template_class.__name__
                }
            
            return json_response(
                APIResponse.success_response({
                    'templates': templates_info,
                    'total': len(templates_info)
                }).to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to list templates").to_dict(),
                status=500
            )
    
    async def create_from_template(self, request: Request) -> Response:
        """Create project from template"""
        try:
            data = await request.json()
            template_name = data.get('template')
            
            if not template_name or template_name not in TEMPLATES:
                return json_response(
                    APIResponse.error_response(
                        "Invalid template", 
                        f"Template '{template_name}' not found"
                    ).to_dict(),
                    status=400
                )
            
            # Get template parameters
            template_params = data.get('parameters', {})
            
            # Create manifest from template
            manifest_builder = from_template(template_name, **template_params)
            manifest_dict = manifest_builder.build()
            
            # Create project
            project = ManifestProject(
                id="",  # Will be auto-generated
                name=data.get('name', f"{template_name}-project"),
                description=data.get('description', f"Project created from {template_name} template"),
                version=data.get('version', '1.0.0'),
                created_at="",  # Will be auto-generated
                updated_at="",  # Will be auto-generated
                author=data.get('author', 'Unknown'),
                tags=data.get('tags', [template_name]),
                manifest=manifest_dict,
                status='draft'
            )
            
            await self.store.create_project(project)
            
            logger.info(f"Created project from template '{template_name}': {project.name}")
            
            return json_response(
                APIResponse.success_response(
                    project.to_dict(),
                    f"Project created from {template_name} template"
                ).to_dict(),
                status=201
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error creating from template: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to create project from template").to_dict(),
                status=500
            )
    
    async def validate_manifest(self, request: Request) -> Response:
        """Validate manifest configuration"""
        try:
            manifest_data = await request.json()
            
            # Perform comprehensive validation
            validation_result = validate_manifest_comprehensive(manifest_data)
            
            return json_response(
                APIResponse.success_response(validation_result).to_dict()
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error validating manifest: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to validate manifest").to_dict(),
                status=500
            )
    
    async def search_projects(self, request: Request) -> Response:
        """Search projects by query"""
        try:
            query = request.query.get('q', '').strip()
            
            if not query:
                return json_response(
                    APIResponse.error_response("Missing query", "Search query parameter 'q' is required").to_dict(),
                    status=400
                )
            
            projects = await self.store.search_projects(query)
            
            # Check if only summaries are requested
            summaries_only = request.query.get('summaries', '').lower() in ['true', '1', 'yes']
            
            if summaries_only:
                results = [p.get_summary() for p in projects]
            else:
                results = [p.to_dict() for p in projects]
            
            return json_response(
                APIResponse.success_response({
                    'query': query,
                    'results': results,
                    'total': len(results)
                }).to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error searching projects: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to search projects").to_dict(),
                status=500
            )
    
    async def duplicate_project(self, request: Request) -> Response:
        """Duplicate an existing project"""
        try:
            project_id = request.match_info['project_id']
            data = await request.json() if request.has_body else {}
            
            new_name = data.get('name')
            duplicated_project = await self.store.duplicate_project(project_id, new_name)
            
            if not duplicated_project:
                return json_response(
                    APIResponse.error_response("Not found", f"Project {project_id} not found").to_dict(),
                    status=404
                )
            
            logger.info(f"Duplicated project {project_id} -> {duplicated_project.id}")
            
            return json_response(
                APIResponse.success_response(
                    duplicated_project.to_dict(),
                    f"Project duplicated successfully"
                ).to_dict(),
                status=201
            )
            
        except Exception as e:
            logger.error(f"Error duplicating project: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to duplicate project").to_dict(),
                status=500
            )
    
    async def get_statistics(self, request: Request) -> Response:
        """Get API statistics"""
        try:
            stats = await self.store.get_statistics()
            
            additional_stats = {
                'all_tags': list(self.store.get_all_tags()),
                'all_authors': list(self.store.get_all_authors()),
                'available_templates': list(TEMPLATES.keys())
            }
            
            return json_response(
                APIResponse.success_response({
                    **stats.to_dict(),
                    **additional_stats
                }).to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to get statistics").to_dict(),
                status=500
            )
    
    async def export_all(self, request: Request) -> Response:
        """Export all projects"""
        try:
            export_data = await self.store.export_all_projects()
            
            return json_response(
                APIResponse.success_response(export_data, "All projects exported").to_dict()
            )
            
        except Exception as e:
            logger.error(f"Error exporting all projects: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to export projects").to_dict(),
                status=500
            )
    
    async def import_all(self, request: Request) -> Response:
        """Import projects from JSON"""
        try:
            data = await request.json()
            overwrite = request.query.get('overwrite', '').lower() in ['true', '1', 'yes']
            
            import_result = await self.store.import_projects(data, overwrite=overwrite)
            
            return json_response(
                APIResponse.success_response(import_result, "Projects imported").to_dict()
            )
            
        except json.JSONDecodeError:
            return json_response(
                APIResponse.error_response("Invalid JSON", "Request body must be valid JSON").to_dict(),
                status=400
            )
        except Exception as e:
            logger.error(f"Error importing projects: {e}")
            return json_response(
                APIResponse.error_response(str(e), "Failed to import projects").to_dict(),
                status=500
            )

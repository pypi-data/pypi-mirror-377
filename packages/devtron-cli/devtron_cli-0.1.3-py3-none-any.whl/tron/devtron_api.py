import requests
import json
import yaml
from tron.core.app import *
from tron.utils    import DevtronUtils

class DevtronApplication:
    def __init__(self, base_url, api_token):
        """
        Initialize the Devtron API client.
        
        Args:
            base_url (str): The base URL of the Devtron instance
            api_token (str): The API token for authentication
        """
        self.base_url  = base_url.rstrip('/')
        self.api_token = api_token
        self.headers   = {
            'token': api_token,
            'Content-Type': 'application/json'
        }
        # Initialize handler/helper objects with required arguments
        self.base_config         = BaseConfiguration(self.base_url,  self.headers)
        self.build_config        = BuildConfig(self.base_url,        self.headers)
        self.git_handler         = GitHandler(self.base_url,         self.headers)
        self.update_git_handler  = UpdateGitHandler(self.base_url,   self.headers)
        self.utils               = DevtronUtils(self.base_url,       self.headers)
        self.workflow            = Workflow(self.base_url,           self.headers)
        self.metadata            = DevtronAppMetadata(self.base_url, self.headers)
        self.update_build_config = UpdateBuildConfig(self.base_url,  self.headers, self.git_handler)

    def create_application(self, config_data):
        """
        Create a new application in Devtron.
        
        Args:
            config_data (dict): Configuration data from YAML file
            
        Returns:
            dict: Result of the operation with success status and app ID or error message
        """
        try:
            print("Creating application...")
            
            # Extract application details from config
            app_name         = config_data.get('app_name')
            project_name     = config_data.get('project_name')
            description      = config_data.get('description', '')
            labels           = config_data.get('labels', [])
            git_repositories = config_data.get('git_repositories', [])
            
            if not app_name or not project_name:
                return {
                    'success': False,
                    'error': 'app_name and project_name are required in config'
                }
            
            # Get team ID from project name
            print(f"Getting team ID for project: {project_name}")
            team_result = self.utils.get_team_id_by_project_name(project_name)
            if not team_result['success']:
                return {
                    'success': False,
                    'error': f'Could not get team ID for project {project_name}: {team_result["error"]}'
                }
            
            team_id = team_result['team_id']
            print(f"Found team ID: {team_id}")
            
            # Prepare payload for application creation
            payload = {
                'appName': app_name,
                'teamId': team_id,
                'description': description,
                'labels': labels,
                'appType': None
            }
            
            # Make API call to create application
            print(f"Creating application: {app_name}")
            response = requests.post(
                f'{self.base_url}/orchestrator/app',
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # Check response status
            if response.status_code == 200:
                result = response.json()
                # Extract app ID from the result field
                app_id = result.get('result', {}).get('id')
                if app_id:
                    print(f"Application created successfully with ID: {app_id}")

                    # If git repositories are provided, add them to the application
                    if git_repositories:
                        print(f"Adding {len(git_repositories)} git repositories to the application")
                        git_config = {
                            'app_id': app_id,
                            'git_repositories': git_repositories
                        }
                        git_result = self.git_handler.add_git_material(git_config)
                        if not git_result['success']:
                            return {
                                'success': False,
                                'error': f'Application created but failed to add git material: {git_result["error"]}'
                            }
                        print("All git repositories added successfully")
                    
                    # Fetch application details
                    print("Fetching application details...")
                    app_details = self.utils.get_application_details(app_id)
                    if not app_details["success"]:
                        return {
                            "success": False,
                            "error": f"Application created but failed to fetch details: {app_details['error']}"
                        }
                    print("Git details fetched successfully!!! ")
                    
                    material_ids = app_details["material_ids"]
                    if not material_ids:
                        return {
                            "success": False,
                            "error": "No Git Material IDs found to configure CI pipeline."
                        }

                    build_configuration_result = self.build_config.configure_ci_pipeline(app_id, material_ids[0],config_data)
                    if not build_configuration_result["success"]:
                        return {
                            "success": False,
                            "error": f"Application created but failed to configure buildconfig: {build_configuration_result['error']}"
                        }

                    # Setup base configurations if config provided
                    if config_data.get('base_configurations'):
                        print("Setting up base configurations...")
                        base_config_result = self.base_config.setup_base_configurations(app_id, config_data)
                        if not base_config_result['success']:
                            return {
                                'success': False,
                                'error': f"Application created but failed to setup base configurations: {base_config_result['error']}"
                            }
                    workflows = config_data.get('workflows')

                    if workflows:
                        print("Setting up workflows...")
                        for w in workflows:
                            ci_pipeline = w.get("ci_pipeline", {})
                            pre_build = ci_pipeline.get("pre_build_configs", [])
                            pre_build_configs = self.workflow.create_pre_build_payload(pre_build)
                            pipeline_name  = w["ci_pipeline"]["name"]
                            is_manual   = w["ci_pipeline"]["is_manual"]
                            build_type = w["ci_pipeline"]["type"]
                            source_app = w["ci_pipeline"].get("source_app")
                            source_pipeline = w["ci_pipeline"].get("source_pipeline")
                            
                            # For LINKED builds, branches are not required
                            branch_data = []
                            if build_type != "LINKED":
                                branch_data = w["ci_pipeline"]["branches"]
                            
                            if not pipeline_name:
                                return {
                                    'success': False,
                                    'error': 'ci_pipeline.name is required in config'
                                }
                            
                            workflow_creation = self.workflow.create_ci_pipeline(
                                app_id=app_id,
                                pipeline_name=pipeline_name,
                                branches=branch_data,
                                is_manual=is_manual,
                                build_type=build_type,
                                pre_build_configs=pre_build_configs,
                                source_app=source_app,
                                source_pipeline=source_pipeline
                            )

                            if workflow_creation["code"] != 200:
                                return {
                                    "success": False,
                                    "error": f"Application created but failed to create workflow: {workflow_creation['error']}"
                                }
                            print(f"Workflow '{pipeline_name}' created successfully.")

                            cd_pipelines = w.get("cd_pipelines", [])
                            if cd_pipelines:
                                workflow_id = workflow_creation.get("result", {}).get("appWorkflowId", 0)
                                ci_pipelines = workflow_creation.get("result", {}).get("ciPipelines", [])
                                ci_pipeline_id = ci_pipelines[0].get("id", 0) if ci_pipelines else 0
                                
                                # Handle CD pipeline creation with dependency management
                                cd_creation_result = self.workflow.create_cd_pipelines_with_dependencies(
                                    app_id=app_id,
                                    workflow_id=workflow_id,
                                    ci_pipeline_id=ci_pipeline_id,
                                    cd_pipelines=cd_pipelines
                                )
                                
                                if not cd_creation_result['success']:
                                    return cd_creation_result



                    return {
                        'success': True,
                        'app_id': app_id
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Could not extract app ID from response'
                    }
            else:
                # Handle error response
                try:
                    error_result = response.json()
                    error_message = error_result.get('errors', [{}])[0].get('userMessage', '')
                    if error_message:
                        return {
                            'success': False,
                            'error': f'API request failed: {error_message}'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'API request failed with status {response.status_code}: {response.text}'
                        }
                except:
                    # If we can't parse the error response, return the raw error
                    return {
                        'success': False,
                        'error': f'API request failed with status {response.status_code}: {response.text}'
                    }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred: {str(e)}'
            }

    def _extract_ci_branches(self, ci_pipeline_details):
        """
        Extract branch information from CI pipeline details.
        
        Args:
            ci_pipeline_details (dict): CI pipeline details from API
            
        Returns:
            list: List of branch configurations
        """
        branches = []
        ci_material = ci_pipeline_details.get('ciMaterial', [])
        
        for material in ci_material:
            source = material.get('source', {})
            if source:
                branch_config = {
                    'type': source.get('type'),
                    'branch': source.get('value'),
                    'regex': source.get('regex')
                }
                # Remove None values
                branch_config = {k: v for k, v in branch_config.items() if v is not None}
                if branch_config:
                    branches.append(branch_config)
        
        return branches
    
    def delete_application(self, app_name, approve=False):
        """
        Delete an application and all its associated pipelines following the correct deletion order.
        
        Args:
            app_name (str): Name of the application to delete
            approve (bool): Whether to proceed with deletion (safety mechanism)
            
        Returns:
            dict: Result of the operation with success status or error message
        """
        try:
            if not approve:
                return {
                    'success': False,
                    'error': 'Deletion requires explicit approval. Please add --approve flag to confirm deletion.'
                }
            
            print(f"Starting deletion process for application: {app_name}")
            
            # Get application ID by name
            app_id_result = self.utils.get_application_id_by_name(app_name)
            if not app_id_result['success']:
                return {
                    'success': False,
                    'error': f'Could not find application {app_name}: {app_id_result["error"]}'
                }
            
            app_id = app_id_result['app_id']
            print(f"Found application ID: {app_id}")
            
            # Get all CI pipelines for the application
            ci_pipelines_result = self.utils.get_ci_pipelines(app_id)
            if not ci_pipelines_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to fetch CI pipelines: {ci_pipelines_result["error"]}'
                }
            
            ci_pipelines = ci_pipelines_result['ci_pipelines']
            print(f"Found {len(ci_pipelines)} CI pipelines")
            
            # Create a map of CI pipeline ID to CI pipeline details for easy lookup
            ci_pipeline_map = {pipeline['id']: pipeline for pipeline in ci_pipelines}
            
            # Get all workflows for the application to find CD pipelines and their relationships
            workflows_result = self.utils.get_workflows(app_id)
            if not workflows_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to fetch workflows: {workflows_result["error"]}'
                }
            
            workflows = workflows_result['workflows']
            print(f"Found {len(workflows)} workflows to process")
            
            # Process workflows and categorize pipelines according to deletion order
            linked_cd_pipelines = []  # CD pipelines attached to LINKED_CD CI pipelines
            linked_cd_ci_pipelines = []  # LINKED_CD CI pipelines
            linked_pipelines = []  # CD pipelines attached to LINKED CI pipelines
            linked_ci_pipelines = []  # LINKED CI pipelines
            webhook_cd_pipelines = []  # CD pipelines attached to WEBHOOK
            ci_job_pipelines = []  # CI_JOB CI pipelines
            ci_build_pipelines = []  # CI_BUILD CI pipelines
            cd_pipeline_details = []  # All CD pipeline details for ordering
            
            # Process workflows to categorize pipelines
            for workflow in workflows:
                workflow_id = workflow['id']
                workflow_name = workflow['name']
                print(f"Processing workflow: {workflow_name} (ID: {workflow_id})")
                
                # Process tree nodes
                tree = workflow.get('tree', [])
                
                # First pass: Identify CI pipeline types
                ci_pipeline_types = {}
                for node in tree:
                    if node.get('type') == 'CI_PIPELINE':
                        ci_pipeline_id = node.get('componentId')
                        # Find the CI pipeline in our map to get its type
                        ci_pipeline = ci_pipeline_map.get(ci_pipeline_id)
                        if ci_pipeline:
                            pipeline_type = ci_pipeline.get('pipelineType', '')
                            ci_pipeline_types[ci_pipeline_id] = {
                                'type': pipeline_type,
                                'name': ci_pipeline.get('name', ''),
                                'workflow_id': workflow_id
                            }
                
                # Second pass: Categorize CD pipelines based on their parent types
                for node in tree:
                    if node.get('type') == 'CD_PIPELINE':
                        parent_type = node.get('parentType', '')
                        parent_id = node.get('parentId', 0)
                        cd_pipeline_id = node.get('componentId')
                        is_last = node.get('isLast', False)
                        
                        cd_detail = {
                            'id': cd_pipeline_id,
                            'parent_type': parent_type,
                            'parent_id': parent_id,
                            'is_last': is_last,
                            'workflow_id': workflow_id
                        }
                        cd_pipeline_details.append(cd_detail)
                        
                        # Check if this CD pipeline is attached to a LINKED_CD CI pipeline
                        if parent_type == 'CI_PIPELINE' and parent_id in ci_pipeline_types:
                            parent_ci = ci_pipeline_types[parent_id]
                            if parent_ci['type'] == 'LINKED_CD':
                                linked_cd_pipelines.append(cd_detail)
                                # Also track the CI pipeline for later deletion
                                if parent_id not in [p['id'] for p in linked_cd_ci_pipelines]:
                                    linked_cd_ci_pipelines.append({
                                        'id': parent_id,
                                        'name': parent_ci['name'],
                                        'workflow_id': parent_ci['workflow_id']
                                    })
                            elif parent_ci['type'] == 'LINKED':
                                linked_pipelines.append(cd_detail)
                                # Also track the CI pipeline for later deletion
                                if parent_id not in [p['id'] for p in linked_ci_pipelines]:
                                    linked_ci_pipelines.append({
                                        'id': parent_id,
                                        'name': parent_ci['name'],
                                        'workflow_id': parent_ci['workflow_id']
                                    })
                        
                        # Check for WEBHOOK parent type
                        elif parent_type == 'WEBHOOK':
                            webhook_cd_pipelines.append(cd_detail)
                        
                        # Other CD pipelines will be handled in the general deletion order
                
                # Categorize remaining CI pipelines
                for ci_pipeline_id, ci_info in ci_pipeline_types.items():
                    # Skip CI pipelines we've already identified for special handling
                    linked_cd_ids = [p['id'] for p in linked_cd_ci_pipelines]
                    linked_ids = [p['id'] for p in linked_ci_pipelines]
                    
                    if ci_pipeline_id in linked_cd_ids or ci_pipeline_id in linked_ids:
                        continue
                    
                    if ci_info['type'] == 'CI_JOB':
                        ci_job_pipelines.append({
                            'id': ci_pipeline_id,
                            'name': ci_info['name'],
                            'workflow_id': ci_info['workflow_id']
                        })
                    elif ci_info['type'] == 'CI_BUILD':
                        ci_build_pipelines.append({
                            'id': ci_pipeline_id,
                            'name': ci_info['name'],
                            'workflow_id': ci_info['workflow_id']
                        })
            
            # Now perform deletions in the correct order:
            # 1. Delete CD pipelines attached to LINKED_CD CI pipelines first
            print(f"Deleting {len(linked_cd_pipelines)} CD pipelines attached to LINKED_CD CI pipelines...")
            for cd_pipeline in linked_cd_pipelines:
                delete_result = self.workflow.delete_cd_pipeline(
                    base_url=self.base_url,
                    headers=self.headers,
                    app_id=app_id,
                    cd_pipeline_id=cd_pipeline['id']
                )
                if not delete_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to delete CD pipeline {cd_pipeline["id"]}: {delete_result["error"]}'
                    }
                print(f"  Deleted CD pipeline: {cd_pipeline['id']}")
            
            # 2. Delete LINKED_CD CI pipelines
            print(f"Deleting {len(linked_cd_ci_pipelines)} LINKED_CD CI pipelines...")
            for ci_pipeline in linked_cd_ci_pipelines:
                delete_result = self.workflow.delete_ci_pipeline(
                    base_url=self.base_url,
                    headers=self.headers,
                    app_id=app_id,
                    app_workflow_id=ci_pipeline['workflow_id'],
                    ci_pipeline_id=ci_pipeline['id'],
                    ci_pipeline_name=ci_pipeline['name']
                )
                if not delete_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to delete CI pipeline {ci_pipeline["id"]}: {delete_result["error"]}'
                    }
                print(f"  Deleted CI pipeline: {ci_pipeline['id']} (Name: {ci_pipeline['name']})")
            
            # 3. Delete CD pipelines attached to LINKED CI pipelines
            print(f"Deleting {len(linked_pipelines)} CD pipelines attached to LINKED CI pipelines...")
            for cd_pipeline in linked_pipelines:
                delete_result = self.workflow.delete_cd_pipeline(
                    base_url=self.base_url,
                    headers=self.headers,
                    app_id=app_id,
                    cd_pipeline_id=cd_pipeline['id']
                )
                if not delete_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to delete CD pipeline {cd_pipeline["id"]}: {delete_result["error"]}'
                    }
                print(f"  Deleted CD pipeline: {cd_pipeline['id']}")
            
            # 4. Delete LINKED CI pipelines
            print(f"Deleting {len(linked_ci_pipelines)} LINKED CI pipelines...")
            for ci_pipeline in linked_ci_pipelines:
                delete_result = self.workflow.delete_ci_pipeline(
                    base_url=self.base_url,
                    headers=self.headers,
                    app_id=app_id,
                    app_workflow_id=ci_pipeline['workflow_id'],
                    ci_pipeline_id=ci_pipeline['id'],
                    ci_pipeline_name=ci_pipeline['name']
                )
                if not delete_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to delete CI pipeline {ci_pipeline["id"]}: {delete_result["error"]}'
                    }
                print(f"  Deleted CI pipeline: {ci_pipeline['id']} (Name: {ci_pipeline['name']})")
            
            # 5. Delete CD pipelines attached to WEBHOOK (in order: is_last true + parentType webhook, then parentType webhook)
            print(f"Deleting {len(webhook_cd_pipelines)} CD pipelines attached to WEBHOOK...")
            # Sort webhook CD pipelines: is_last=True first
            webhook_cd_pipelines.sort(key=lambda x: not x['is_last'])
            for cd_pipeline in webhook_cd_pipelines:
                delete_result = self.workflow.delete_cd_pipeline(
                    base_url=self.base_url,
                    headers=self.headers,
                    app_id=app_id,
                    cd_pipeline_id=cd_pipeline['id']
                )
                if not delete_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to delete CD pipeline {cd_pipeline["id"]}: {delete_result["error"]}'
                    }
                print(f"  Deleted CD pipeline: {cd_pipeline['id']}")
            
            # 6. Delete remaining CD pipelines in the specified order with dependency handling
            print("Deleting remaining CD pipelines...")
            # Get remaining CD pipelines that haven't been deleted yet
            all_cd_pipeline_ids = [cd_detail['id'] for cd_detail in cd_pipeline_details]
            already_deleted_cd_ids = (
                [p['id'] for p in linked_cd_pipelines] +
                [p['id'] for p in linked_pipelines] +
                [p['id'] for p in webhook_cd_pipelines]
            )
            remaining_cd_pipeline_ids = [cd_id for cd_id in all_cd_pipeline_ids if cd_id not in already_deleted_cd_ids]
            
            # Keep trying to delete CD pipelines in the correct order until all are deleted or no progress is made
            max_iterations = 10
            iteration = 0
            while remaining_cd_pipeline_ids and iteration < max_iterations:
                iteration += 1
                print(f"  Iteration {iteration} - Processing {len(remaining_cd_pipeline_ids)} remaining CD pipelines...")
                
                # Refresh workflow data to get current state after previous deletions
                workflows_result = self.utils.get_workflows(app_id)
                if not workflows_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to refresh workflows: {workflows_result["error"]}'
                    }
                
                workflows = workflows_result['workflows']
                
                # Rebuild CD pipeline details with current workflow data
                current_cd_pipeline_details = []
                for workflow in workflows:
                    tree = workflow.get('tree', [])
                    for node in tree:
                        if node.get('type') == 'CD_PIPELINE':
                            cd_detail = {
                                'id': node.get('componentId'),
                                'parent_type': node.get('parentType', ''),
                                'parent_id': node.get('parentId', 0),
                                'is_last': node.get('isLast', False),
                                'workflow_id': workflow['id']
                            }
                            # Only include pipelines that are still remaining to be deleted
                            if cd_detail['id'] in remaining_cd_pipeline_ids:
                                current_cd_pipeline_details.append(cd_detail)
                
                # Categorize CD pipelines based on current state
                cd_pipelines_is_last_cd_parent = []
                cd_pipelines_cd_parent = []
                cd_pipelines_is_last_ci_parent = []
                
                for cd_detail in current_cd_pipeline_details:
                    if cd_detail['id'] in already_deleted_cd_ids:
                        continue
                    
                    if cd_detail['is_last'] and cd_detail['parent_type'] == 'CD_PIPELINE':
                        cd_pipelines_is_last_cd_parent.append(cd_detail)
                    elif cd_detail['parent_type'] == 'CD_PIPELINE':
                        cd_pipelines_cd_parent.append(cd_detail)
                    elif cd_detail['is_last'] and cd_detail['parent_type'] == 'CI_PIPELINE':
                        cd_pipelines_is_last_ci_parent.append(cd_detail)
                
                # Track progress in this iteration
                deleted_in_this_iteration = 0
                
                # Delete in order
                for cd_pipeline in cd_pipelines_is_last_cd_parent:
                    if cd_pipeline['id'] in already_deleted_cd_ids:
                        continue
                    delete_result = self.workflow.delete_cd_pipeline(
                        base_url=self.base_url,
                        headers=self.headers,
                        app_id=app_id,
                        cd_pipeline_id=cd_pipeline['id']
                    )
                    if delete_result['success']:
                        print(f"  Deleted CD pipeline: {cd_pipeline['id']}")
                        already_deleted_cd_ids.append(cd_pipeline['id'])
                        deleted_in_this_iteration += 1
                    else:
                        print(f"  Failed to delete CD pipeline {cd_pipeline['id']}: {delete_result['error']}")
                
                for cd_pipeline in cd_pipelines_cd_parent:
                    if cd_pipeline['id'] in already_deleted_cd_ids:
                        continue
                    delete_result = self.workflow.delete_cd_pipeline(
                        base_url=self.base_url,
                        headers=self.headers,
                        app_id=app_id,
                        cd_pipeline_id=cd_pipeline['id']
                    )
                    if delete_result['success']:
                        print(f"  Deleted CD pipeline: {cd_pipeline['id']}")
                        already_deleted_cd_ids.append(cd_pipeline['id'])
                        deleted_in_this_iteration += 1
                    else:
                        print(f"  Failed to delete CD pipeline {cd_pipeline['id']}: {delete_result['error']}")
                
                for cd_pipeline in cd_pipelines_is_last_ci_parent:
                    if cd_pipeline['id'] in already_deleted_cd_ids:
                        continue
                    delete_result = self.workflow.delete_cd_pipeline(
                        base_url=self.base_url,
                        headers=self.headers,
                        app_id=app_id,
                        cd_pipeline_id=cd_pipeline['id']
                    )
                    if delete_result['success']:
                        print(f"  Deleted CD pipeline: {cd_pipeline['id']}")
                        already_deleted_cd_ids.append(cd_pipeline['id'])
                        deleted_in_this_iteration += 1
                    else:
                        print(f"  Failed to delete CD pipeline {cd_pipeline['id']}: {delete_result['error']}")
                
                # Update remaining CD pipeline IDs
                remaining_cd_pipeline_ids = [cd_id for cd_id in all_cd_pipeline_ids if cd_id not in already_deleted_cd_ids]
                
                # If no progress was made in this iteration, break to avoid infinite loop
                if deleted_in_this_iteration == 0:
                    print(f"  No progress made in iteration {iteration}, stopping CD pipeline deletion")
                    break
            
            # Check if all CD pipelines were deleted
            if remaining_cd_pipeline_ids:
                return {
                    'success': False,
                    'error': f'Failed to delete CD pipelines {remaining_cd_pipeline_ids} after {iteration} iterations. They may have unresolvable dependencies.'
                }
            
            # 7. Delete CI_JOB CI pipelines
            print(f"Deleting {len(ci_job_pipelines)} CI_JOB CI pipelines...")
            for ci_pipeline in ci_job_pipelines:
                delete_result = self.workflow.delete_ci_pipeline(
                    base_url=self.base_url,
                    headers=self.headers,
                    app_id=app_id,
                    app_workflow_id=ci_pipeline['workflow_id'],
                    ci_pipeline_id=ci_pipeline['id'],
                    ci_pipeline_name=ci_pipeline['name']
                )
                if not delete_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to delete CI pipeline {ci_pipeline["id"]}: {delete_result["error"]}'
                    }
                print(f"  Deleted CI pipeline: {ci_pipeline['id']} (Name: {ci_pipeline['name']})")
            
            # 8. Delete CI_BUILD CI pipelines
            print(f"Deleting {len(ci_build_pipelines)} CI_BUILD CI pipelines...")
            for ci_pipeline in ci_build_pipelines:
                delete_result = self.workflow.delete_ci_pipeline(
                    base_url=self.base_url,
                    headers=self.headers,
                    app_id=app_id,
                    app_workflow_id=ci_pipeline['workflow_id'],
                    ci_pipeline_id=ci_pipeline['id'],
                    ci_pipeline_name=ci_pipeline['name']
                )
                if not delete_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to delete CI pipeline {ci_pipeline["id"]}: {delete_result["error"]}'
                    }
                print(f"  Deleted CI pipeline: {ci_pipeline['id']} (Name: {ci_pipeline['name']})")
            
            # 9. Delete empty workflows
            print(f"Deleting {len(workflows)} workflows...")
            for workflow in workflows:
                workflow_id = workflow['id']
                delete_result = self.workflow.delete_workflow(
                    base_url=self.base_url,
                    headers=self.headers,
                    app_id=app_id,
                    workflow_id=workflow_id
                )
                # Workflow deletion might fail if workflow is not empty, which is expected
                # We still try to delete all workflows
                if delete_result['success']:
                    print(f"  Deleted workflow: {workflow_id}")
                else:
                    print(f"  Failed to delete workflow {workflow_id} (might not be empty): {delete_result['error']}")
            
            # Now delete the application itself
            print(f"Deleting application: {app_name} (ID: {app_id})")
            response = requests.delete(
                f'{self.base_url}/orchestrator/app/{app_id}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                print(f"Application {app_name} deleted successfully!")
                return {
                    'success': True,
                    'message': f'Application {app_name} and all associated pipelines deleted successfully!'
                }
            else:
                try:
                    error_result = response.json()
                    error_message = error_result.get('errors', [{}])[0].get('userMessage', '')
                    if error_message:
                        return {
                            'success': False,
                            'error': f'Failed to delete application: {error_message}'
                        }
                    else:
                        return {
                            'success': False,
                            'error': f'Failed to delete application with status {response.status_code}: {response.text}'
                        }
                except:
                    return {
                        'success': False,
                        'error': f'Failed to delete application with status {response.status_code}: {response.text}'
                    }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred: {str(e)}'
            }
    
    def update_application(self, config_data):
        """
        Update an existing application's git materials and container registry in Devtron.
        Args:
            config_data (dict): Configuration data from YAML file
        Returns:
            dict: Result of the operation with success status and message or error
        """
        try:
            print("Updating application metadata...")
            metadata_save_result = self.metadata.save_metadata(config_data)
            if not metadata_save_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to save metadata: {metadata_save_result["error"]}'
                }

            print("Updating application git materials...")
            git_result = self.update_git_handler.update_git_materials(config_data)
            if not git_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to update git materials: {git_result["error"]}'
                }
            registry_result = self.update_build_config.update_container_registry(config_data)
            if not registry_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to update container registry: {registry_result["error"]}'
                }
            update_base_configurations_result = self.base_config.update_base_configurations(config_data)
            if not update_base_configurations_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to update base configurations: {update_base_configurations_result["error"]}'
                }
            return {
                'success': True,
                'message': 'Application updated: git materials and container registry and base configurations.'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred: {str(e)}'
            }

    def get_application(self, app_name):
        """
        Get application configuration from Devtron.
        Args:
            app_name (str): Name of the application to fetch
        Returns:
            dict: Application configuration in the same format as used for create-app
        """
        try:
            print(f"Fetching application: {app_name}")
            
            # Get application ID by name
            app_id_result = self.utils.get_application_id_by_name(app_name)
            if not app_id_result['success']:
                return {
                    'success': False,
                    'error': f'Could not find application {app_name}: {app_id_result["error"]}'
                }
            
            app_id = app_id_result['app_id']
            print(f"Found application ID: {app_id}")
            
            # Fetch application details
            app_details_result = self.utils.get_application_details(app_id)
            if not app_details_result['success']:
                return {
                    'success': False,
                    'error': f'Failed to fetch application details: {app_details_result["error"]}'
                }
            
            app_data = app_details_result['data']
            
            # Build configuration data structure
            config_data = {
                'app_name': app_name
            }
            
            # Add description if available
            if 'description' in app_data:
                config_data['description'] = app_data['description']
            
            # Add labels if available
            if 'labels' in app_data and app_data['labels']:
                config_data['labels'] = app_data['labels']
            
            # Add git repositories if available
            if 'material' in app_data and app_data['material']:
                git_repositories = []
                for material in app_data['material']:
                    git_repo = {
                        'url': material.get('url'),
                        'git_account_name': self.git_handler.get_git_account_name_by_id(app_id, material.get('gitProviderId'))['git_account_name'] if material.get('gitProviderId') is not None else '',
                        'checkout_path': material.get('checkoutPath', './')
                    }
                    
                    # Add optional fields if they exist
                    if 'fetchSubmodules' in material:
                        git_repo['fetch_submodules'] = material['fetchSubmodules']
                    if 'filterPattern' in material and material['filterPattern']:
                        git_repo['filter_pattern'] = material['filterPattern']
                        
                    git_repositories.append(git_repo)
                
                config_data['git_repositories'] = git_repositories
            
            # Fetch CI pipeline configuration
            try:
                pipeline_response = requests.get(
                    f'{self.base_url}/orchestrator/app/ci-pipeline/{app_id}',
                    headers=self.headers
                )
                
                if pipeline_response.status_code == 200:
                    pipeline_data = pipeline_response.json().get('result', {})
                    
                    # Add build configurations if available
                    build_config = {}
                    ci_build_config = pipeline_data.get('ciBuildConfig', {})
                    
                    if 'dockerRegistry' in pipeline_data:
                        build_config['container_registry_name'] = pipeline_data['dockerRegistry']
                    if 'dockerRepository' in pipeline_data:
                        build_config['repository_name'] = pipeline_data['dockerRepository']
                        
                    # Add build type specific configurations
                    # Map Devtron API build types to configuration file build types
                    build_type_mapping = {
                        'self-dockerfile-build': 'DockerfileExists',
                        'managed-dockerfile-build': 'CreateDockerfile',
                        'buildpack-build': 'Buildpacks'
                    }
                    
                    build_type = ci_build_config.get('ciBuildType')
                    if build_type:
                        # Map to the configuration file build type
                        config_build_type = build_type_mapping.get(build_type, build_type)
                        build_config['build_type'] = config_build_type
                        
                        if build_type == 'self-dockerfile-build':
                            docker_config = ci_build_config.get('dockerBuildConfig', {})
                            if 'dockerfileRelativePath' in docker_config:
                                build_config['dockerfile_path'] = docker_config['dockerfileRelativePath']
                            if 'targetPlatform' in docker_config:
                                build_config['target_platform'] = docker_config['targetPlatform']
                            if 'buildContext' in docker_config:
                                build_config['build_context'] = docker_config['buildContext']
                            if 'dockerfileRepository' in docker_config:
                                build_config['dockerfile_repository'] = docker_config['dockerfileRepository']
                            if 'args' in docker_config and docker_config['args']:
                                # Convert args to docker_build_args format
                                build_config['docker_build_args'] = docker_config['args']
                                
                        elif build_type == 'managed-dockerfile-build':
                            docker_config = ci_build_config.get('dockerBuildConfig', {})
                            if 'dockerfileRelativePath' in docker_config:
                                build_config['dockerfile_path'] = docker_config['dockerfileRelativePath']
                            if 'targetPlatform' in docker_config:
                                build_config['target_platform'] = docker_config['targetPlatform']
                            if 'language' in docker_config:
                                build_config['language'] = docker_config['language']
                            if 'languageFramework' in docker_config:
                                build_config['language_framework'] = docker_config['languageFramework']
                            if 'dockerfileContent' in docker_config:
                                build_config['dockerfile_content'] = docker_config['dockerfileContent']
                                
                        elif build_type == 'buildpack-build':
                            buildpack_config = ci_build_config.get('buildPackConfig', {})
                            if 'builderId' in buildpack_config:
                                build_config['builder_image'] = buildpack_config['builderId']
                            if 'language' in buildpack_config:
                                build_config['language'] = buildpack_config['language']
                            if 'languageVersion' in buildpack_config:
                                build_config['version'] = buildpack_config['languageVersion']
                            if 'projectPath' in buildpack_config:
                                build_config['build_context'] = buildpack_config['projectPath']
                    
                    if build_config:
                        config_data['build_configurations'] = build_config
                        
            except Exception as e:
                print(f"Warning: Could not fetch CI pipeline configuration: {str(e)}")
            
            # Fetch base configurations if they exist
            base_configurations = {}
            
            # Fetch deployment template
            try:
                # Get latest chart reference ID
                latest_chart_ref_id = self.base_config.bdt.get_latest_chart_ref_id(app_id)
                if latest_chart_ref_id:
                    deployment_template_result = self.base_config.bdt.get_deployment_template_yaml(app_id, latest_chart_ref_id)
                    if deployment_template_result['success']:
                        deployment_template = deployment_template_result['yaml'].get('globalConfig', {})
                        if deployment_template:
                            # If chart name is not available in deployment template, get it from chart reference API
                            chart_name = self.utils._get_chart_name_from_id(app_id, latest_chart_ref_id)
                            
                            base_configurations['deployment_template'] = {
                                'version': deployment_template.get('refChartTemplateVersion'),
                                'chart_type': chart_name,
                                'show_application_metrics': deployment_template.get('isAppMetricsEnabled', False)
                            }
                            
                            # Save defaultAppOverride to a file instead of including it directly
                            default_app_override = deployment_template.get('defaultAppOverride', {})
                            if default_app_override:
                                # Create filename based on app name
                                values_filename = f"base-{app_name}-values.yaml"
                                
                                # Write the values to the file
                                with open(values_filename, 'w') as f:
                                    yaml.dump(default_app_override, f, default_flow_style=False, allow_unicode=True)
                                
                                # Reference the file instead of including the values directly
                                base_configurations['deployment_template']['values_path'] = values_filename
            except Exception as e:
                print(f"Warning: Could not fetch deployment template: {str(e)}")
            
            # Fetch config maps and secrets
            try:
                cm_cs_result = self.base_config.devtron_config_map_secret.get_base_cm_cs_details(app_id)
                if cm_cs_result['success']:
                    cm_cs_data = cm_cs_result['result']
                    
                    # Fetch detailed config map data
                    config_maps = []
                    if cm_cs_data.get('cm_list'):
                        for cm_name in cm_cs_data['cm_list']:
                            cm_details_result = self.base_config.devtron_config_map_secret.get_config_map_details(app_id, cm_name)
                            if cm_details_result['success']:
                                # Remove global and overriden fields from config map
                                config_map_data = cm_details_result['config_map']
                                config_map_data.pop('global', None)
                                config_map_data.pop('overridden', None)
                                
                                # Remove subPath field if type is environment
                                if config_map_data.get('type') == 'environment':
                                    config_map_data.pop('subPath', None)
                                    
                                # Handle reverse logic for external config maps with mountPath and subPath
                                # Extract subPath from data object if special conditions are met
                                if (config_map_data.get('external') is True and 
                                    config_map_data.get('mountPath') and 
                                    config_map_data.get('data')):
                                    
                                    # Check if any key in data has an empty string value (indicating it was a subPath)
                                    sub_path_key = None
                                    for key, value in config_map_data['data'].items():
                                        if value == "":
                                            sub_path_key = key
                                            break
                                    
                                    if sub_path_key:
                                        # Set the subPath field and remove the empty entry from data
                                        config_map_data['subPath'] = sub_path_key
                                        del config_map_data['data'][sub_path_key]
                                        
                                        # If data becomes empty after removal, remove the data field entirely
                                        if not config_map_data['data']:
                                            config_map_data.pop('data', None)
                                    
                                config_maps.append(config_map_data)
                            else:
                                print(f"Warning: Could not fetch details for config map {cm_name}: {cm_details_result['error']}")
                                config_maps.append({'name': cm_name})
                    
                    # Fetch detailed secret data  
                    secrets = []
                    if cm_cs_data.get('cs_list'):
                        for cs_name in cm_cs_data['cs_list']:
                            secret_details_result = self.base_config.devtron_config_map_secret.get_secret_details(app_id, cs_name)
                            if secret_details_result['success']:
                                # Remove global and overriden fields from secret
                                secret_data = secret_details_result['secret']
                                secret_data.pop('global', None)
                                secret_data.pop('overridden', None)
                                
                                # Remove subPath field if type is environment
                                if secret_data.get('type') == 'environment':
                                    secret_data.pop('subPath', None)
                                
                                # Handle reverse logic for external secrets with mountPath and subPath
                                # Extract subPath from data object if special conditions are met
                                if (secret_data.get('external') is True and 
                                    secret_data.get('mountPath') and 
                                    secret_data.get('data')):
                                    
                                    # Check if any key in data has an empty string value (indicating it was a subPath)
                                    sub_path_key = None
                                    for key, value in secret_data['data'].items():
                                        if value == "":
                                            sub_path_key = key
                                            break
                                    
                                    if sub_path_key:
                                        # Set the subPath field and remove the empty entry from data
                                        secret_data['subPath'] = sub_path_key
                                        del secret_data['data'][sub_path_key]
                                        
                                        # If data becomes empty after removal, remove the data field entirely
                                        if not secret_data['data']:
                                            secret_data.pop('data', None)
                                
                                # Base64 decode secret data if present
                                if 'data' in secret_data and secret_data['data']:
                                    decoded_data = {}
                                    for key, encoded_value in secret_data['data'].items():
                                        try:
                                            import base64
                                            decoded_value = base64.b64decode(encoded_value).decode('utf-8')
                                            decoded_data[key] = decoded_value
                                        except Exception as e:
                                            print(f"Warning: Failed to decode base64 value for key '{key}': {e}")
                                            decoded_data[key] = encoded_value  # Keep original if decoding fails
                                    secret_data['data'] = decoded_data
                                    
                                secrets.append(secret_data)
                            else:
                                print(f"Warning: Could not fetch details for secret {cs_name}: {secret_details_result['error']}")
                                secrets.append({'name': cs_name})
                    
                    if config_maps:
                        base_configurations['config_maps'] = config_maps
                    if secrets:
                        base_configurations['secrets'] = secrets
            except Exception as e:
                print(f"Warning: Could not fetch config maps and secrets: {str(e)}")
            
            # Add base configurations to config data if any were found
            if base_configurations:
                config_data['base_configurations'] = base_configurations
            
            # Fetch workflows if they exist
            workflows_data = []
            try:
                workflows_result = self.utils.get_workflows(app_id)
                if workflows_result['success']:
                    workflows = workflows_result['workflows']
                    
                    for workflow in workflows:
                        workflow_info = {}
                        
                        # Process tree nodes to extract pipeline information
                        tree = workflow.get('tree', [])
                        
                        # Find CI pipelines in this workflow
                        for node in tree:
                            if node.get('type') == 'CI_PIPELINE':
                                ci_pipeline_id = node.get('componentId')
                                # Get CI pipeline details
                                ci_pipeline_result = self.utils.get_ci_pipeline_details(app_id, ci_pipeline_id)
                                if ci_pipeline_result['success']:
                                    ci_pipeline_details = ci_pipeline_result['pipeline_details']
                                    
                                    # Extract CI pipeline configuration
                                    ci_pipeline_config = {
                                        'type': ci_pipeline_details.get('pipelineType'),
                                        'is_manual': ci_pipeline_details.get('isManual', False),
                                        'name': ci_pipeline_details.get('name')
                                    }
                                    
                                    # Handle LINKED pipeline source
                                    if ci_pipeline_config['type'] == 'LINKED':
                                        source_app_id = ci_pipeline_details.get('parentAppId')
                                        source_pipeline_id = ci_pipeline_details.get('parentCiPipelineId')
                                        if source_app_id and source_pipeline_id:
                                            # Get source app and pipeline names
                                            source_app_result = self.utils.get_application_details(source_app_id)
                                            if source_app_result['success']:
                                                ci_pipeline_config['source_app'] = source_app_result['data'].get('appName')
                                            
                                            source_pipeline_result = self.utils.get_ci_pipeline_details(source_app_id, source_pipeline_id)
                                            if source_pipeline_result['success']:
                                                ci_pipeline_config['source_pipeline'] = source_pipeline_result['pipeline_details'].get('name')
                                    
                                    # Extract branches information
                                    branches = []
                                    ci_material = ci_pipeline_details.get('ciMaterial', [])
                                    for material in ci_material:
                                        source = material.get('source', {})
                                        if source:
                                            # Use the git material ID as the repo identifier
                                            # This matches the pattern in test.yaml where repo names are simple identifiers
                                            git_material_id = material.get('gitMaterialId')
                                            repo_identifier = f"repo-{git_material_id}" if git_material_id else "unknown-repo"
                                            
                                            branch_config = {
                                                'repo': repo_identifier,
                                                'branch': source.get('value'),
                                                'type': source.get('type'),
                                                'regex': source.get('regex')
                                            }
                                            # Remove None values
                                            branch_config = {k: v for k, v in branch_config.items() if v is not None}
                                            if branch_config:
                                                branches.append(branch_config)
                                    
                                    if branches:
                                        ci_pipeline_config['branches'] = branches
                                    
                                    # Extract pre-build and post-build configurations
                                    pre_build_stages = ci_pipeline_details.get('preBuildStage', {})
                                    post_build_stages = ci_pipeline_details.get('postBuildStage', {})
                                    
                                    pre_build_configs = []
                                    post_build_configs = []
                                    
                                    # Process pre-build stages
                                    if pre_build_stages.get('steps'):
                                        for step in pre_build_stages['steps']:
                                            if step.get('stepType') in ['PLUGIN_REF', 'INLINE']:
                                                config = {
                                                    'type': 'plugin' if step.get('stepType') == 'PLUGIN_REF' else 'custom_script',
                                                    'name': step.get('name'),
                                                    'task_name': step.get('stepType') == 'PLUGIN_REF' and step.get('refPluginId') or '',
                                                    'version': step.get('stepType') == 'PLUGIN_REF' and step.get('refPluginVersion') or '',
                                                    'input_variables': step.get('inputVars', {})
                                                }
                                                # Remove empty values
                                                config = {k: v for k, v in config.items() if v}
                                                pre_build_configs.append(config)
                                    
                                    # Process post-build stages
                                    if post_build_stages.get('steps'):
                                        for step in post_build_stages['steps']:
                                            if step.get('stepType') in ['PLUGIN_REF', 'INLINE']:
                                                config = {
                                                    'type': 'plugin' if step.get('stepType') == 'PLUGIN_REF' else 'custom_script',
                                                    'name': step.get('name'),
                                                    'task_name': step.get('stepType') == 'PLUGIN_REF' and step.get('refPluginId') or '',
                                                    'version': step.get('stepType') == 'PLUGIN_REF' and step.get('refPluginVersion') or '',
                                                    'input_variables': step.get('inputVars', {})
                                                }
                                                # Remove empty values
                                                config = {k: v for k, v in config.items() if v}
                                                post_build_configs.append(config)
                                    
                                    if pre_build_configs:
                                        ci_pipeline_config['pre_build_configs'] = pre_build_configs
                                    if post_build_configs:
                                        ci_pipeline_config['post_build_configs'] = post_build_configs
                                    
                                    workflow_info['ci_pipeline'] = ci_pipeline_config
                        
                        # Find CD pipelines in this workflow
                        cd_pipelines = []
                        for node in tree:
                            if node.get('type') == 'CD_PIPELINE':
                                cd_pipeline_id = node.get('componentId')
                                # Get CD pipeline details
                                cd_pipeline_result = self.utils.get_cd_pipeline_details(app_id, cd_pipeline_id)
                                if cd_pipeline_result['success']:
                                    cd_pipeline_details = cd_pipeline_result['pipeline_details']
                                    
                                    cd_pipeline_config = {
                                        'name': cd_pipeline_details.get('name'),
                                        'environment_name': cd_pipeline_details.get('environmentName'),
                                        'is_manual': cd_pipeline_details.get('isManual', False),
                                        'deployment_type': cd_pipeline_details.get('deploymentAppType', 'helm').lower()
                                    }
                                    
                                    # Extract deployment strategies
                                    strategies = cd_pipeline_details.get('strategies', [])
                                    if strategies:
                                        deployment_strategies = []
                                        for strategy in strategies:
                                            strategy_config = {
                                                'name': strategy.get('strategy'),
                                                'strategy': strategy.get('config', {}),
                                                'default': strategy.get('default', False)
                                            }
                                            # Remove empty strategy config
                                            if not strategy_config['strategy']:
                                                strategy_config.pop('strategy')
                                            deployment_strategies.append(strategy_config)
                                        cd_pipeline_config['deployment_strategies'] = deployment_strategies
                                    
                                    # Extract pre-CD and post-CD configurations
                                    pre_cd_stages = cd_pipeline_details.get('preStage', {})
                                    post_cd_stages = cd_pipeline_details.get('postStage', {})
                                    
                                    pre_cd_configs = []
                                    post_cd_configs = []
                                    
                                    # Process pre-CD stages
                                    if pre_cd_stages.get('steps'):
                                        for step in pre_cd_stages['steps']:
                                            if step.get('stepType') in ['PLUGIN_REF', 'INLINE']:
                                                config = {
                                                    'type': 'plugin' if step.get('stepType') == 'PLUGIN_REF' else 'custom_script',
                                                    'name': step.get('name'),
                                                    'task_name': step.get('stepType') == 'PLUGIN_REF' and step.get('refPluginId') or '',
                                                    'version': step.get('stepType') == 'PLUGIN_REF' and step.get('refPluginVersion') or '',
                                                    'input_variables': step.get('inputVars', {})
                                                }
                                                # Remove empty values
                                                config = {k: v for k, v in config.items() if v}
                                                pre_cd_configs.append(config)
                                    
                                    # Process post-CD stages
                                    if post_cd_stages.get('steps'):
                                        for step in post_cd_stages['steps']:
                                            if step.get('stepType') in ['PLUGIN_REF', 'INLINE']:
                                                config = {
                                                    'type': 'plugin' if step.get('stepType') == 'PLUGIN_REF' else 'custom_script',
                                                    'name': step.get('name'),
                                                    'task_name': step.get('stepType') == 'PLUGIN_REF' and step.get('refPluginId') or '',
                                                    'version': step.get('stepType') == 'PLUGIN_REF' and step.get('refPluginVersion') or '',
                                                    'input_variables': step.get('inputVars', {})
                                                }
                                                # Remove empty values
                                                config = {k: v for k, v in config.items() if v}
                                                post_cd_configs.append(config)
                                    
                                    if pre_cd_configs:
                                        cd_pipeline_config['pre_cd_configs'] = pre_cd_configs
                                    if post_cd_configs:
                                        cd_pipeline_config['post_cd_configs'] = post_cd_configs
                                    
                                    cd_pipelines.append(cd_pipeline_config)
                        
                        if cd_pipelines:
                            workflow_info['cd_pipelines'] = cd_pipelines
                        
                        if workflow_info:  # Only add if we have pipeline data
                            workflows_data.append(workflow_info)
                
                if workflows_data:
                    config_data['workflows'] = workflows_data
                    
            except Exception as e:
                print(f"Warning: Could not fetch workflows: {str(e)}")
            
            # Clean up the config data by removing empty values
            cleaned_config_data = self.utils.remove_empty_values(config_data)
            
            
            
            return {
                'success': True,
                'config_data': cleaned_config_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred: {str(e)}'
            }

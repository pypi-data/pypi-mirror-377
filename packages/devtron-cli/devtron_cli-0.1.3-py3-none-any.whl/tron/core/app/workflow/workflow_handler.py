import base64
import json
import os

import requests
import copy

import yaml

from tron.core.app import BuildConfig
from tron.utils import DevtronUtils



class Workflow:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers
        self.DevtronUtils = DevtronUtils(self.base_url, self.headers)
        self.build_config = BuildConfig(self.base_url, self.headers)

    def create_ci_pipeline(self, app_id: int, branches: list, is_manual: bool, pipeline_name: str, build_type: str, pre_build_configs: dict, source_app: str = None, source_pipeline: str = None) -> dict:
        if not app_id or not pipeline_name:
            raise ValueError("app_id and pipeline_name are required parameters.")
        
        # For LINKED builds, branches are not required as they come from source pipeline
        if build_type != "LINKED" and (not branches or not branches):
            raise ValueError("branches are required for non-LINKED build types.")

        api_url = f"{self.base_url.rstrip('/')}/orchestrator/app/ci-pipeline/patch"
        
        # For non-LINKED builds, get git material from current app
        ci_material = []
        if build_type != "LINKED":
            app_details = self.DevtronUtils.get_application_details(app_id)
            if not app_details or "data" not in app_details or "material" not in app_details["data"]:
                raise RuntimeError(f"Failed to fetch git material for app_id {app_id}. Response: {app_details}")
            
            git_material = app_details["data"]["material"]
            ci_material = self.build_ci_material(git_material, branches)
            
            if not ci_material:
                raise RuntimeError("No CI material found. Check your branches and git material configuration.")

        payload = self.build_ci_payload(app_id, ci_material, is_manual, pipeline_name, build_type, pre_build_configs, source_app, source_pipeline)

        try:
            print(f"Sending request to create CI pipeline '{pipeline_name}' for app ID {app_id}...")
            response = requests.post(api_url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            print("Successfully created CI pipeline.")
            return response.json()
        except requests.exceptions.RequestException as err:
            print(f"Request error: {err}")
            raise

    def get_env_id(self, environment_name):
        try:
            print(f"Getting environment ID for: {environment_name}")
            response = requests.get(f'{self.base_url}/orchestrator/env/autocomplete', headers=self.headers)
            if response.status_code == 200:
                environments = response.json().get('result', [])
                for e in environments:
                    if e.get("environment_name") == environment_name:
                        return {
                            'success': True,
                            'environment_id': e.get("id"),
                            'namespace': e.get("namespace")
                        }
                return {'success': False, 'error': f'Environment "{environment_name}" not found'}
            return {'success': False, 'error': f'API request failed: {response.status_code} {response.text}'}
        except Exception as e:
            return {'success': False, 'error': f'Exception occurred: {str(e)}'}

    def get_deployment_strategies(self, app_id: int) -> dict:
        """
        Fetch deployment strategies for an application from the Devtron API.
        
        Args:
            app_id (int): The ID of the application
            
        Returns:
            dict: Result containing the strategies or error message
        """
        try:
            api_url = f"{self.base_url.rstrip('/')}/orchestrator/app/cd-pipeline/strategies/{app_id}"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'strategies': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to fetch deployment strategies: {response.status_code} {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred while fetching deployment strategies: {str(e)}'
            }

    def create_cd_pipeline(self, app_id: int, workflow_id: int, ci_pipeline_id: int, environment_id: int, namespace: str, pipeline_name: str, pre_deploy: dict, post_deploy: dict, deployment_strategies: list = None, deployment_type: str = "helm", is_manual: bool = True, placement: str = "parallel", depends_on: str = None, parent_pipeline_type: str = None, parent_pipeline_id: int = None) -> dict:
        api_url = f"{self.base_url.rstrip('/')}/orchestrator/app/cd-pipeline"
        payload = self.build_cd_pipeline_payload(app_id, workflow_id, ci_pipeline_id, environment_id, namespace, pipeline_name, pre_deploy, post_deploy, deployment_strategies, deployment_type, is_manual, placement, depends_on, parent_pipeline_type, parent_pipeline_id)
        try:
            response = requests.post(api_url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            raise err
    
    def create_cd_pipelines_with_dependencies(self, app_id: int, workflow_id: int, ci_pipeline_id: int, cd_pipelines: list) -> dict:
        """
        Create CD pipelines in the correct order based on their dependencies.
        
        Args:
            app_id (int): Application ID
            workflow_id (int): Workflow ID
            ci_pipeline_id (int): CI Pipeline ID
            cd_pipelines (list): List of CD pipeline configurations
            
        Returns:
            dict: Result of the operation with success status or error message
        """
        try:
            # Build dependency graph and validate dependencies
            dependency_graph = {}
            cd_pipeline_configs = {}
            
            # First pass: Parse all CD pipeline configurations
            for i, c in enumerate(cd_pipelines):
                environment_name = c.get("environment_name")
                if not environment_name:
                    return {
                        'success': False,
                        'error': f'CD pipeline at index {i} is missing environment_name'
                    }
                
                # Store configuration for later use
                cd_pipeline_configs[environment_name] = c
                depends_on = c.get("depends_on")
                
                # Build dependency graph
                if depends_on:
                    if depends_on not in dependency_graph:
                        dependency_graph[depends_on] = []
                    dependency_graph[depends_on].append(environment_name)
                else:
                    if environment_name not in dependency_graph:
                        dependency_graph[environment_name] = []
            
            # Validate that all dependencies exist in the same workflow
            for c in cd_pipelines:
                depends_on = c.get("depends_on")
                environment_name = c.get("environment_name")
                if depends_on and depends_on not in cd_pipeline_configs:
                    return {
                        'success': False,
                        'error': f'CD pipeline for environment "{environment_name}" depends on environment "{depends_on}" which is not defined in the same workflow'
                    }
            
            # Topological sort to determine creation order
            creation_order = self._topological_sort(dependency_graph)
            if not creation_order:
                return {
                    'success': False,
                    'error': 'Circular dependency detected in CD pipeline configurations'
                }
            
            # Create CD pipelines in the correct order
            created_pipelines = {}
            
            for environment_name in creation_order:
                c = cd_pipeline_configs[environment_name]
                
                # Get environment details
                env_result = self.get_env_id(environment_name)
                if not env_result['success']:
                    return {
                        'success': False,
                        'error': f'Could not get environment ID for {environment_name}: {env_result["error"]}'
                    }
                
                environment_id = env_result.get("environment_id", None)
                namespace = env_result.get("namespace", None)
                print(f"Getting environment ID for {environment_name}: {environment_id}")
                
                # Prepare pre and post deploy configurations
                pre_deploy = {}
                post_deploy = {}
                pre_deploy_config = c.get("pre_cd_configs", [])
                post_deploy_config = c.get("post_cd_configs", [])
                if pre_deploy_config:
                    pre_deploy_result = self.create_pre_build_payload(pre_deploy_config)
                    if not pre_deploy_result.get("success", True):
                        return pre_deploy_result
                    pre_deploy = pre_deploy_result
                if post_deploy_config:
                    post_deploy_result = self.create_pre_build_payload(post_deploy_config)
                    if not post_deploy_result.get("success", True):
                        return post_deploy_result
                    post_deploy = post_deploy_result
                
                # Get deployment strategies from CD pipeline configuration
                deployment_strategies = c.get("deployment_strategies", None)
                deployment_type = c.get("deployment_type", "helm")
                is_manual = c.get("is_manual", True)
                placement = c.get("placement", "parallel")
                depends_on = c.get("depends_on", None)
                
                # If this pipeline depends on another, get the parent pipeline ID
                parent_pipeline_id = ci_pipeline_id
                parent_pipeline_type = "CI_PIPELINE"
                if depends_on:
                    if depends_on in created_pipelines:
                        parent_pipeline_id = created_pipelines[depends_on]
                        parent_pipeline_type = "CD_PIPELINE"
                    else:
                        # This shouldn't happen with proper topological sort, but just in case
                        return {
                            'success': False,
                            'error': f'Parent pipeline for environment "{depends_on}" not found during creation of "{environment_name}"'
                        }
                
                # Create the CD pipeline
                try:
                    creat_pipeline_status = self.create_cd_pipeline(
                        app_id=app_id,
                        workflow_id=workflow_id,
                        ci_pipeline_id=ci_pipeline_id,
                        environment_id=environment_id,
                        namespace=namespace,
                        pipeline_name=c.get("name", f"cd-pipeline-{environment_name}"),
                        pre_deploy=pre_deploy,
                        post_deploy=post_deploy,
                        deployment_strategies=deployment_strategies,
                        deployment_type=deployment_type,
                        is_manual=is_manual,
                        placement=placement,
                        parent_pipeline_type=parent_pipeline_type,
                        parent_pipeline_id=parent_pipeline_id
                    )
                    
                    # Store the created pipeline ID for dependencies
                    if creat_pipeline_status.get("code") == 200:
                        pipeline_id = creat_pipeline_status.get("result", {}).get("pipelines", [{}])[0].get("id")
                        if pipeline_id:
                            created_pipelines[environment_name] = pipeline_id
                            env_configuration = cd_pipeline_configs[environment_name].get("env_configuration", {})
                            if env_configuration:
                                if env_configuration.get("deployment_template", {}).get("type", "") == "override":
                                    version = env_configuration.get("deployment_template", {}).get("version", "")
                                    if not version:
                                        return {
                                            'success': False,
                                            'error': f'Version must be specified for override deployment template in environment {environment_name}'
                                        }

                                    patch_override_deployement = self.patch_deployment(environment_name, env_configuration, environment_id, namespace, app_id, version)
                                    if not patch_override_deployement.get("success", True):
                                        return {
                                            'success': False,
                                            'error': "The pipeline has been created but could not patch the override deployment template"
                                        }
                                    else:
                                        print(f"Successfully patched override deployment template for environment {environment_name}")

                                if env_configuration.get("config_maps", []):
                                    config_maps = env_configuration.get("config_maps", [])
                                    for config_map in config_maps:
                                        if config_map.get("config_type", "") == "override" or config_map.get("config_type", "") == "":
                                            patch_override_config = self.patch_cm_cs(app_id, environment_id, "cm", config_map)
                                            if not patch_override_config.get("success", True):
                                                return {
                                                    'success': False,
                                                    'error': "The pipeline has been created but could not patch the override config map"
                                                }
                                            else:
                                                print(f"Successfully patched override config map for environment {environment_name}")
                                if env_configuration.get("secrets", []):
                                    secrets = env_configuration.get("secrets", [])
                                    for secret in secrets:
                                        if secret.get("config_type", "") == "override":
                                            patch_override_secret = self.patch_cm_cs(app_id, environment_id, "cs", secret)
                                            if not patch_override_secret.get("success", True):
                                                return {
                                                    'success': False,
                                                    'error': "The pipeline has been created but could not patch the override secret"
                                                }
                                            else:
                                                print(f"Successfully patched override secret for environment {environment_name}")

                        else:
                            return {
                                'success': False,
                                'error': f'Failed to get pipeline ID for environment {environment_name}'
                            }
                    else:
                        return {
                            'success': False,
                            'error': f'Failed to create CD pipeline for environment {environment_name}: {creat_pipeline_status.get("error", "Unknown error")}'
                        }
                        
                except ValueError as e:
                    return {
                        'success': False,
                        'error': f'Failed to create CD pipeline for environment {environment_name}: {str(e)}'
                    }
            
            return {
                'success': True,
                'message': f'Successfully created {len(cd_pipelines)} CD pipelines in dependency order'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred while creating CD pipelines with dependencies: {str(e)}'
            }
    
    def _topological_sort(self, dependency_graph: dict) -> list:
        """
        Perform topological sort on the dependency graph to determine creation order.
        
        Args:
            dependency_graph (dict): Graph representing dependencies between environments
            
        Returns:
            list: Sorted list of environment names in creation order, or empty list if circular dependency
        """
        # Kahn's algorithm for topological sorting
        in_degree = {node: 0 for node in dependency_graph}
        
        # Calculate in-degrees
        for node in dependency_graph:
            for dependent in dependency_graph[node]:
                in_degree[dependent] = in_degree.get(dependent, 0) + 1
        
        # Find all nodes with no incoming edges
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Decrease in-degree for all dependents
            for dependent in dependency_graph.get(node, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check for circular dependencies
        if len(result) != len(in_degree):
            return []  # Circular dependency detected
        
        return result

    def get_plugin_details_by_name(self, plugin_name: str) -> dict:
        try:
            new_plugin_name = plugin_name.replace(" ", "+")
            api_url = f"{self.base_url.rstrip('/')}/orchestrator/plugin/global/list/v2?searchKey={new_plugin_name}&offset=0"
            response = requests.get(api_url, headers=self.headers)
            data = response.json()
            status_code = data.get("code", 0)
            if status_code == 200:
                plugin_search_result = data.get("result", {})
                if plugin_search_result:
                    plugin_list = plugin_search_result.get("parentPlugins", [])
                    for plugin in plugin_list:
                        if plugin.get("name") == plugin_name:
                            return {'success': True, 'plugin': plugin}
            return {}
        except Exception as e:
            return {'success': False, 'error': f'Exception occurred: {str(e)}'}

    @staticmethod
    def build_ci_material(git_material: list, branches: list) -> list:
        return [
            {
                "gitMaterialId": git_material[i].get("id"),
                "id": 0,
                "source": {
                    "type": branches[i].get("type"),
                    "value": branches[i].get("branch"),
                    "regex": branches[i].get("regex")
                }
            }
            for i in range(len(branches))
        ]

    def build_ci_payload(self, app_id: int, ci_material: list, is_manual: bool, pipeline_name: str, build_type: str, pre_build_configs: dict, source_app: str = None, source_pipeline: str = None) -> dict:
        """
        Build CI pipeline payload with support for LINKED build type.
        
        Args:
            app_id (int): The ID of the application
            ci_material (list): CI material configuration
            is_manual (bool): Whether the pipeline is manual
            pipeline_name (str): Name of the pipeline
            build_type (str): Type of build (LINKED, etc.)
            pre_build_configs (dict): Pre-build configurations
            source_app (str): Source application name for LINKED builds
            source_pipeline (str): Source pipeline name for LINKED builds
            
        Returns:
            dict: CI pipeline payload
        """
        payload = {
            "appId": app_id,
            "appWorkflowId": 0,
            "action": 0,
            "ciPipeline": {
                "active": True,
                "ciMaterial": ci_material,
                "dockerArgs": {},
                "externalCiConfig": {},
                "id": 0,
                "isExternal": False,
                "isManual": is_manual,
                "name": pipeline_name,
                "linkedCount": 0,
                "scanEnabled": False,
                "pipelineType": build_type,
                "customTag": {"tagPattern": "", "counterX": 0},
                "workflowCacheConfig": {"type": "INHERIT", "value": True, "globalValue": True},
                "preBuildStage": pre_build_configs,
                "postBuildStage": {},
                "dockerConfigOverride": {}
            }
        }
        
        # Handle LINKED build type
        if build_type == "LINKED":
            if not source_pipeline:
                raise ValueError("source_pipeline is required for LINKED build type")
            
            # If source_app is not provided, assume the current app is the source
            source_app_id = app_id
            if source_app:
                # Get source app ID if source_app is provided
                source_app_result = self.DevtronUtils.get_application_id_by_name(source_app)
                if not source_app_result['success']:
                    raise ValueError(f"Could not find source application: {source_app_result['error']}")
                source_app_id = source_app_result['app_id']
            
            # Get source CI pipeline ID
            source_pipeline_result = self.DevtronUtils.get_ci_pipeline_id_by_name(source_app_id, source_pipeline)
            if not source_pipeline_result['success']:
                raise ValueError(f"Could not find source CI pipeline: {source_pipeline_result['error']}")
            source_pipeline_id = source_pipeline_result['ci_pipeline_id']
            
            # Get source CI pipeline details
            pipeline_details_result = self.DevtronUtils.get_ci_pipeline_details(source_app_id, source_pipeline_id)
            if not pipeline_details_result['success']:
                raise ValueError(f"Could not fetch source CI pipeline details: {pipeline_details_result['error']}")
            
            pipeline_details = pipeline_details_result['pipeline_details']
            
            # Get CI material from source pipeline
            source_ci_material = pipeline_details.get('ciMaterial', [])
            if not source_ci_material:
                raise ValueError(f"No CI material found in source pipeline {source_pipeline}")
            
            # Get dockerConfigOverride as-is from pipeline_details
            docker_config_override = pipeline_details.get('dockerConfigOverride', {})
            
            # Update payload for LINKED build type
            payload["ciPipeline"]["isExternal"] = True
            payload["ciPipeline"]["ciMaterial"] = source_ci_material
            payload["ciPipeline"]["dockerConfigOverride"] = docker_config_override
            payload["ciPipeline"]["ciPipelineName"] = source_pipeline
            payload["ciPipeline"]["isDockerConfigOverridden"] = True
            payload["ciPipeline"]["lastTriggeredEnvId"] = -1
            payload["ciPipeline"]["linkedCount"] = 0
            payload["ciPipeline"]["parentAppId"] = 0
            payload["ciPipeline"]["parentCiPipeline"] = source_pipeline_id
            payload["ciPipeline"]["enableCustomTag"] = False
            
            # Add externalCiConfig structure
            payload["ciPipeline"]["externalCiConfig"] = {
                "id": 0,
                "webhookUrl": "",
                "payload": "",
                "accessKey": "",
                "payloadOption": None,
                "schema": None,
                "responses": None,
                "projectId": 0,
                "projectName": "",
                "environmentId": "",
                "environmentName": "",
                "environmentIdentifier": "",
                "appId": 0,
                "appName": "",
                "role": ""
            }
        
        return payload

    def build_cd_pipeline_payload(self, app_id: int, workflow_id: int, ci_pipeline_id: int, environment_id: int, namespace: str, pipeline_name: str, pre_deploy: dict, post_deploy: dict, deployment_strategies: list = None, deployment_type: str = "helm", is_manual: bool = True, placement: str = "parallel", depends_on: str = None, parent_pipeline_type: str = None, parent_pipeline_id: int = None) -> dict:
        # If deployment_strategies is not provided, fetch from API
        if deployment_strategies is None:
            strategies_result = self.get_deployment_strategies(app_id)
            if strategies_result['success']:
                api_strategies = strategies_result['strategies'].get('result', {}).get('pipelineStrategy', [])
                # Find the default strategy
                default_strategy = None
                for strategy in api_strategies:
                    if strategy.get('default', False):
                        default_strategy = strategy
                        break
                
                # If no default strategy found, use the first one
                if default_strategy is None and api_strategies:
                    default_strategy = api_strategies[0]
                # Convert to the format expected by the API
                if default_strategy:
                    strategies = [self._convert_strategy_format(default_strategy, is_default=True)]
                else:
                    # Fallback to hardcoded ROLLING strategy if API doesn't return any strategies
                    strategies = [self._get_default_rolling_strategy()]
            else:
                # Fallback to hardcoded ROLLING strategy if API call fails
                strategies = [self._get_default_rolling_strategy()]
        else:
            # Validate that only one strategy is marked as default
            default_count = sum(1 for strategy in deployment_strategies if strategy.get('default', False))
            if default_count > 1:
                raise ValueError("Only one strategy can be set to default. Please set only one strategy with default: true")
            
            # Use provided deployment_strategies and convert to API format
            strategies = []
            default_found = False
            for i, strategy in enumerate(deployment_strategies):
                is_default = strategy.get('default', False)
                if is_default:
                    default_found = True
                strategies.append(self._convert_user_strategy(strategy, app_id, is_default))
            
            # If no default strategy was specified, make the first one default
            if strategies and not default_found:
                strategies[0]['default'] = True

        # Set triggerType based on is_manual value
        trigger_type = "MANUAL" if is_manual else "AUTOMATIC"
        
        # Set addType based on placement value, convert to uppercase, default to PARALLEL
        add_type = placement.upper() if placement else "PARALLEL"
        if add_type not in ["SEQUENTIAL", "PARALLEL"]:
            add_type = "PARALLEL"
        
        # Set parent pipeline type and ID
        # If parent_pipeline_type and parent_pipeline_id are provided directly, use them
        # Otherwise, use the depends_on parameter for backward compatibility
        if parent_pipeline_type is not None and parent_pipeline_id is not None:
            final_parent_pipeline_type = parent_pipeline_type
            final_parent_pipeline_id = parent_pipeline_id
        else:
            # Set parent pipeline type and ID based on depends_on parameter
            final_parent_pipeline_type = "CI_PIPELINE"
            final_parent_pipeline_id = ci_pipeline_id
            
            # If depends_on is specified, we need to get the CD pipeline ID for that environment
            # This is for backward compatibility when calling create_cd_pipeline directly
            if depends_on:
                # Get the CD pipeline ID for the environment it depends on
                depends_on_result = self.DevtronUtils.get_cd_pipeline_id_by_environment_name(app_id, depends_on)
                if depends_on_result['success']:
                    final_parent_pipeline_type = "CD_PIPELINE"
                    final_parent_pipeline_id = depends_on_result['pipeline_id']
                else:
                    # If we can't find the CD pipeline, fail the creation
                    raise ValueError(f"Could not find CD pipeline for environment '{depends_on}' that this pipeline depends on. Please ensure the dependent pipeline is created first.")
        
        payload = {
            "appId": app_id,
            "pipelines": [
                {
                    "name": pipeline_name,
                    "appWorkflowId": workflow_id,
                    "ciPipelineId": ci_pipeline_id,
                    "environmentId": environment_id,
                    "namespace": namespace,
                    "id": 0,
                    "strategies": strategies,
                    "parentPipelineType": final_parent_pipeline_type,
                    "parentPipelineId": final_parent_pipeline_id,
                    "isClusterCdActive": False,
                    "deploymentAppType": deployment_type,
                    "deploymentAppName": "",
                    "releaseMode": "create",
                    "deploymentAppCreated": False,
                    "triggerType": trigger_type,
                    "environmentName": namespace,
                    "preStageConfigMapSecretNames": {"configMaps": [], "secrets": []},
                    "postStageConfigMapSecretNames": {"configMaps": [], "secrets": []},
                    "containerRegistryName": "",
                    "repoName": "",
                    "manifestStorageType": "helm_repo",
                    "runPreStageInEnv": False,
                    "runPostStageInEnv": False,
                    "preDeployStage": pre_deploy,
                    "postDeployStage": post_deploy,
                    "customTag": {},
                    "enableCustomTag": False,
                    "isDigestEnforcedForPipeline": True,
                    "isDigestEnforcedForEnv": False,
                    "addType": add_type
                }
            ]
        }
        
        return payload

    @staticmethod
    def _get_default_rolling_strategy() -> dict:
        """Get the default ROLLING strategy as a fallback."""
        config = {
            "deployment": {
                "strategy": {
                    "rolling": {
                        "maxSurge": "25%",
                        "maxUnavailable": 1
                    }
                }
            }
        }
        return {
            "deploymentTemplate": "ROLLING",
            "defaultConfig": config,
            "config": config,
            "isCollapsed": True,
            "default": True,
            "jsonStr": json.dumps(config, indent=4),
            "yamlStr": "deployment:\n  strategy:\n    rolling:\n      maxSurge: 25%\n      maxUnavailable: 1\n"
        }

    def _convert_strategy_format(self, strategy: dict, is_default: bool = False) -> dict:
        """Convert API strategy format to the format expected by the CD pipeline API."""
        deployment_template = strategy.get('deploymentTemplate', 'ROLLING')
        config = strategy.get('config', {})
        
        # Create defaultConfig from the strategy's default configuration
        default_config = config.copy()
        
        # Convert config to JSON string
        json_str = json.dumps(config, indent=4)
        
        # Convert config to YAML string using the Utils function
        yaml_str = DevtronUtils.convert_dict_to_yaml(config)
        
        return {
            "deploymentTemplate": deployment_template,
            "defaultConfig": default_config,
            "config": config,
            "isCollapsed": True,
            "default": is_default,
            "jsonStr": json_str,
            "yamlStr": yaml_str
        }

    def _convert_user_strategy(self, strategy: dict, app_id: int, is_default: bool = False) -> dict:
        """Convert user-provided strategy to the format expected by the CD pipeline API."""
        
        # Strategy name mapping to handle special cases like BLUE-GREEN
        strategy_name_mapping = {
            'BLUE-GREEN': 'blueGreen',
            'CANARY': 'canary',
            'RECREATE': 'recreate',
            'ROLLING': 'rolling'
        }
        
        # Get strategies from API to get default configurations
        strategies_result = self.get_deployment_strategies(app_id)
        api_strategies = []
        if strategies_result['success']:
            api_strategies = strategies_result['strategies'].get('result', {}).get('pipelineStrategy', [])
        
        name = strategy.get('name', 'ROLLING').upper()  # Convert to uppercase as required
        strategy_config = strategy.get('strategy', {})
        
        # Find the matching strategy in API strategies to get default config
        default_config = {}
        for api_strategy in api_strategies:
            if api_strategy.get('deploymentTemplate', '').upper() == name:
                default_config = api_strategy.get('config', {})
                break
        
        # If no matching API strategy found, we can't proceed
        if not default_config:
            raise ValueError(f"Could not find default configuration for strategy {name} from API")
        
        # Create config by starting with the default config and updating it with user's strategy config
        config = copy.deepcopy(default_config)
        
        # Get the correct strategy key name (camelCase)
        strategy_key = strategy_name_mapping.get(name, name.lower())
        
        # Update the config with user's strategy configuration
        # The user's strategy config should be merged into deployment.strategy.{strategy_name}
        if 'deployment' in config and 'strategy' in config['deployment']:
            if strategy_key in config['deployment']['strategy']:
                # Update the specific strategy configuration with user's values
                for key, value in strategy_config.items():
                    config['deployment']['strategy'][strategy_key][key] = value
            # If the strategy name is not found, we'll use the default config as is
        
        # Convert config to JSON string
        json_str = json.dumps(config, indent=4)
        
        # Convert config to YAML string using the Utils function
        yaml_str = DevtronUtils.convert_dict_to_yaml(config)
        
        result = {
            "deploymentTemplate": name,
            "defaultConfig": default_config,
            "config": config,
            "isCollapsed": False,
            "default": is_default,
            "jsonStr": json_str,
            "yamlStr": yaml_str
        }
        return result

    @staticmethod
    def _merge_user_config_with_default(default_config: dict, user_config: dict, strategy_name: str) -> dict:
        """Merge user configuration with default configuration properly."""
        # Strategy name mapping to handle special cases like BLUE-GREEN
        strategy_name_mapping = {
            'BLUE-GREEN': 'blueGreen',
            'CANARY': 'canary',
            'RECREATE': 'recreate',
            'ROLLING': 'rolling'
        }
        
        merged = copy.deepcopy(default_config)
        
        # For deployment strategies, we need to merge the strategy-specific configuration
        # into the deployment.strategy section
        if strategy_name and user_config:
            # Navigate to the deployment.strategy section
            if 'deployment' in merged and 'strategy' in merged['deployment']:
                strategy_section = merged['deployment']['strategy']
                # Get the correct strategy key name (camelCase)
                strategy_key = strategy_name_mapping.get(strategy_name.upper(), strategy_name.lower())
                # Merge the user config into the specific strategy section
                if strategy_key in strategy_section:
                    strategy_section[strategy_key].update(user_config)
        
        return merged

    @staticmethod
    def build_pre_build_payload(task_name: str, plugin: dict, index: int, plugin_version: int, input_list: dict) -> dict:
        plugin_id = 0
        plugin_versions = plugin.get("pluginVersions", {})
        detailed_plugin_versions = plugin_versions.get("detailedPluginVersionData", []) if plugin_versions else []
        minimal_plugin_versions  = plugin_versions.get("minimalPluginVersionData", []) if plugin_versions else []
        input_variables = []
        for p in minimal_plugin_versions:
            if p.get("pluginVersion", None) == plugin_version:
                plugin_id = p.get("id", 0)
                break
        for p in detailed_plugin_versions:
            if p.get("id", 0) == plugin_id:
                input_variables = p.get("inputVariables", [])
                break
        input_var_data = Workflow.create_input_variable_payload(input_variables, input_list)

        plugin_description = plugin.get("description", "") if plugin else ""

        return {
                    "id": index,
                    "index": index,
                    "name": task_name,
                    "description": plugin_description,
                    "stepType": "REF_PLUGIN",
                    "directoryPath": "",
                    "pluginRefStepDetail": {
                        "id": 0,
                        "pluginId": plugin_id,
                        "conditionDetails": [],
                        "inputVariables": input_var_data,
                        "outputVariables": []
                    }
                }


    def create_pre_build_payload(self, pre_build: dict):

        pre_build_configs = []
        for i in range(len(pre_build)):

            plugin_name    = pre_build[i].get("name", "")
            task_name      = pre_build[i].get("task_name", "")
            plugin_version = pre_build[i].get("version", "")
            input_list     = pre_build[i].get("input_variables", {})

            plugin_req = Workflow.get_plugin_details_by_name(self, plugin_name)
            if not plugin_req.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to fetch plugin details for {plugin_name}: {plugin_req.get('error', 'Unknown error')}"
                }
            plugin = plugin_req.get("plugin", {})
            if not plugin:
                return {
                    "success": False,
                    "error": f"Plugin {plugin_name} not found"
                }
            pre_build_config = Workflow.build_pre_build_payload(task_name, plugin, i+1, plugin_version, input_list)
            pre_build_configs.append(pre_build_config)
        return {
            "id": 0,
            "steps": pre_build_configs
        }

    @staticmethod
    def create_input_variable_payload(input_variables: list, input_list: dict) -> list:

        input_var_data = []
        if not input_variables:
            return input_var_data

        for _input in input_variables:
            _id = _input.get("id", 0)
            name  = _input.get("name", "")
            value  = input_list.get(name, "")
            description = _input.get("description", "")
            allow_empty_value = _input.get("allowEmptyValue", True)

            i = {
                "allowEmptyValue": allow_empty_value,
                "refVariableName": "",
                "refVariableStage": None,
                "valueConstraint": {
                    "choices": None,
                    "blockCustomValue": False
                },
                "isRuntimeArg": False,
                "defaultValue": "",
                "id": _id,
                "value": value,
                "format": "STRING",
                "name": name,
                "description": description,
                "variableType": "NEW"
            }
            input_var_data.append(i)

        return input_var_data

    def delete_workflow(self, base_url: str, headers: dict, app_id: int, workflow_id: int) -> dict:
        """
        Delete a workflow by ID (only works if workflow is empty).

        Args:
            base_url (str): The base URL of the Devtron instance
            headers (dict): The headers for authentication
            app_id (int): The ID of the application
            workflow_id (int): The ID of the workflow to delete

        Returns:
            dict: Result of the operation with success status or error message
        """
        try:
            api_url = f"{base_url.rstrip('/')}/orchestrator/app/app-wf/{app_id}/{workflow_id}"
            print(f"Deleting workflow ID {workflow_id} for app ID {app_id}...")

            response = requests.delete(api_url, headers=headers)

            if response.status_code == 200:
                print(f"Successfully deleted workflow ID {workflow_id}")
                return {
                    'success': True,
                    'message': f'Workflow ID {workflow_id} deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to delete workflow {workflow_id}: {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred: {str(e)}'
            }

    def delete_ci_pipeline(self, base_url: str, headers: dict, app_id: int, app_workflow_id: int, ci_pipeline_id: int,
                           ci_pipeline_name: str) -> dict:
        """
        Delete a CI pipeline using PATCH endpoint.

        Args:
            base_url (str): The base URL of the Devtron instance
            headers (dict): The headers for authentication
            app_id (int): The ID of the application
            app_workflow_id (int): The ID of the workflow
            ci_pipeline_id (int): The ID of the CI pipeline to delete
            ci_pipeline_name (str): The name of the CI pipeline to delete

        Returns:
            dict: Result of the operation with success status or error message
        """
        try:
            api_url = f"{base_url.rstrip('/')}/orchestrator/app/ci-pipeline/patch"
            print(f"Deleting CI pipeline ID {ci_pipeline_id} for app ID {app_id}...")

            payload = {
                "action": 2,  # Delete action
                "appId": app_id,
                "appWorkflowId": app_workflow_id,
                "ciPipeline": {
                    "id": ci_pipeline_id,
                    "name": ci_pipeline_name
                }
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                result = response.json()
                ci_pipelines = result.get('result', {}).get('ciPipelines', [])
                deleted_pipeline = None
                for pipeline in ci_pipelines:
                    if pipeline.get('id') == ci_pipeline_id and pipeline.get('deleted', False):
                        deleted_pipeline = pipeline
                        break

                if deleted_pipeline:
                    print(f"Successfully deleted CI pipeline ID {ci_pipeline_id}")
                    return {
                        'success': True,
                        'message': f'CI pipeline ID {ci_pipeline_id} deleted successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to confirm deletion of CI pipeline {ci_pipeline_id}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Failed to delete CI pipeline: {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred: {str(e)}'
            }

    def delete_cd_pipeline(self, base_url: str, headers: dict, app_id: int, cd_pipeline_id: int) -> dict:
        """
        Delete a CD pipeline using PATCH endpoint.

        Args:
            base_url (str): The base URL of the Devtron instance
            headers (dict): The headers for authentication
            app_id (int): The ID of the application
            cd_pipeline_id (int): The ID of the CD pipeline to delete

        Returns:
            dict: Result of the operation with success status or error message
        """
        try:
            api_url = f"{base_url.rstrip('/')}/orchestrator/app/cd-pipeline/patch"
            print(f"Deleting CD pipeline ID {cd_pipeline_id} for app ID {app_id}...")

            payload = {
                "action": 1,  # Delete action
                "appId": app_id,
                "pipeline": {
                    "id": cd_pipeline_id
                }
            }

            response = requests.post(api_url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                result = response.json()
                pipelines = result.get('result', {}).get('pipelines', [])
                if pipelines and 'deleteResponse' in result.get('result', {}):
                    delete_response = result['result']['deleteResponse']
                    if delete_response.get('deleteInitiated', False):
                        print(f"Successfully deleted CD pipeline ID {cd_pipeline_id}")
                        return {
                            'success': True,
                            'message': f'CD pipeline ID {cd_pipeline_id} deleted successfully'
                        }

                return {
                    'success': False,
                    'error': f'Failed to confirm deletion of CD pipeline {cd_pipeline_id}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to delete CD pipeline: {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception occurred: {str(e)}'
            }
    def patch_deployment(self, environment_name, env_configuration: dict, environment_id, namespace, app_id, version: str) -> dict:
        try:

            app_metrics     = env_configuration.get("deployment_template", {}).get("show_application_metrics", False)
            merge_strategy  = env_configuration.get("deployment_template", {}).get("merge_strategy", "patch")
            current_chart_ref_id = self.get_chart_ref_id_by_environment_id(app_id, environment_id)

            if current_chart_ref_id == -1:
                return {'success': False, 'error': f"Failed to fetch chart ref ID for environment ID {environment_id}"}
            chart_ref_id = self.get_chart_ref_id_by_version(version, current_chart_ref_id, app_id, environment_id)
            config_id = self.get_config_id(app_id, environment_id, chart_ref_id)
            values_patch = env_configuration.get("deployment_template", {}).get("values_patch", {})
            values_path = env_configuration.get("deployment_template", {}).get("values_path", "")
            env_override = {}
            if values_patch:
                env_override  = values_patch
            elif values_path:
                if not os.path.isfile(values_path):
                    return {'success': False, 'error': f"Custom values.yaml file not found: {values_path}"}
                with open(values_path, 'r') as f:
                    env_override = yaml.safe_load(f)
                env_override = self._remove_newlines_from_strings(env_override)
            else:
                return {'success': False, 'error': "Either values_patch or values_path must be provided for override deployment template"}


            payload = self.build_configuration_payload(environment_name, environment_id, chart_ref_id, is_override=True, app_metrics=app_metrics, merge_strategy=merge_strategy, env_override=env_override, namespace=namespace, config_id=config_id)
            if config_id:
                api_url = f"{self.base_url.rstrip('/')}/orchestrator/app/env"
                response = requests.put(api_url, headers=self.headers, data=json.dumps(payload))
            else:
                api_url = f"{self.base_url.rstrip('/')}/orchestrator/app/env/{app_id}/{environment_id}"
                response = requests.post(api_url, headers=self.headers, data=json.dumps(payload))

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print("Successfully patched deployment template override")
                    return {'success': True, 'message': 'Deployment template override patched successfully'}
                else:
                    return {'success': False, 'error': f"Failed to patch deployment template override: {result.get('error', 'Unknown error')}"}
            else:
                return {'success': False, 'error': f"Failed to patch deployment template override: {response.text}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}



    def _remove_newlines_from_strings(self, obj):
            if isinstance(obj, dict):
                return {k: self._remove_newlines_from_strings(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [self._remove_newlines_from_strings(i) for i in obj]
            elif isinstance(obj, str):
                return obj.replace('\n', '')
            else:
                return obj


    def get_chart_ref_id_by_version(self, version, current_chart_ref_id, app_id, environment_id):
        try:
            api_url = f"{self.base_url.rstrip('/')}/orchestrator/chartref/autocomplete/{app_id}/{environment_id}"
            response = requests.get(api_url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    chart_refs = result.get('result', {}).get("chartRefs", [])
                    chart_name = ""
                    for chart in chart_refs:
                        if chart.get("id", "") == current_chart_ref_id:
                            chart_name = chart.get("name", "")
                    for chart in chart_refs:
                        if chart.get("version", "") == version and chart.get("name", "") == chart_name:
                            return chart.get("id", 0)

            return 0
        except Exception as e:
            print(f"Exception occurred while fetching chart versions: {str(e)}")
            return 0


    def get_config_id(self, app_id, environment_id, chart_ref_id):
        try:
            api_url = f"{self.base_url.rstrip('/')}/orchestrator/app/env/{app_id}/{environment_id}/{chart_ref_id}"
            response = requests.get(api_url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    config_data = result.get('result', {}).get("environmentConfig", {})
                    return config_data.get("id", 0)
            return 0
        except Exception as e:
            print(f"Exception occurred while fetching config ID: {str(e)}")
            return 0

    def get_chart_ref_id_by_environment_id(self, app_id, environment_id):
        try:
            api_url = f"{self.base_url.rstrip('/')}/orchestrator/app/other-env/min?app-id={app_id}"
            response = requests.get(api_url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    chart_ref_data = result.get('result', [])
                    for data in chart_ref_data:
                        if data.get("environmentId", -1) == environment_id:
                            return data.get("chartRefId", 0)
            return -1
        except Exception as e:
            print(f"Exception occurred while fetching chart ref ID: {str(e)}")
            return -1

    @staticmethod
    def build_configuration_payload(environment_name: str, environment_id: int, chart_ref_id: int, is_override: bool,  app_metrics: bool, merge_strategy: str, env_override: dict, namespace: str, config_id: int, save_eligible_changes:bool = True, status: int = 1) -> dict:
        if config_id != 0:
            return {
                "environmentId": environment_id,
                "chartRefId": chart_ref_id,
                "IsOverride": is_override,
                "isAppMetricsEnabled": app_metrics,
                "saveEligibleChanges": save_eligible_changes,
                "id": config_id,
                "status": status,
                "manualReviewed": True,
                "active": True,
                "namespace": namespace,
                "mergeStrategy": merge_strategy,
                "envOverrideValues": env_override,
                "isExpressEdit": False,
                "resourceName": f"{environment_name}-DeploymentTemplateOverride"
            }
        else:
            return {
                "environmentId": environment_id,
                "chartRefId": chart_ref_id,
                "IsOverride": is_override,
                "isAppMetricsEnabled": app_metrics,
                "saveEligibleChanges": save_eligible_changes,
                "mergeStrategy": merge_strategy,
                "envOverrideValues": env_override,
                "isExpressEdit": False,
                "resourceName": f"{environment_name}-DeploymentTemplateOverride"
            }
    @staticmethod
    def encode_values_to_base64(data: dict) -> dict:

        encoded_data = {}
        for key, value in data.items():
            value_str = str(value)
            encoded_value = base64.b64encode(value_str.encode("utf-8")).decode("utf-8")
            encoded_data[key] = encoded_value
        return encoded_data

    def patch_cm_cs(self, app_id: int, environment_id: int, config_type: str, cm_cs_data: dict) -> dict:
        try:
            api_url = f"{self.base_url.rstrip('/')}/orchestrator/config/environment/{config_type}"
            cm_cs_name = cm_cs_data.get("name", "")
            cm_cs_type = cm_cs_data.get("type", "environment")
            is_external = cm_cs_data.get("external", False)
            from_file = cm_cs_data.get("from_file", "")
            config_data  = cm_cs_data.get("data", {})
            mount_path = cm_cs_data.get("mountPath", None)
            subpath =  cm_cs_data.get("subPath", None)
            file_permission = cm_cs_data.get("filePermission", None)
            merge_strategy = cm_cs_data.get("merge_strategy", None)
            role_arn = cm_cs_data.get("roleARN", "")
            external_type = cm_cs_data.get("externalType", "")
            eso_secret_data = cm_cs_data.get("esoSecretData", None)
            eso_subpath = cm_cs_data.get("esoSubPath", None)
            if from_file:
                if not os.path.isfile(from_file):
                    return {'success': False, 'error': f"File not found: {from_file}"}
                with open(from_file, 'r') as f:
                        config_data = yaml.safe_load(f)
            if config_type == "cs":
                config_data = self.encode_values_to_base64(config_data)
            cm_cs_payload = self.build_cm_cs_payload(app_id, environment_id, cm_cs_name, cm_cs_type, is_external, config_data, role_arn=role_arn, external_type=external_type, eso_secret_data=eso_secret_data, mount_path=mount_path, subpath=subpath, file_permission=file_permission, eso_subpath=eso_subpath, merge_strategy=merge_strategy)
            response = requests.post(api_url, headers=self.headers, data=json.dumps(cm_cs_payload))
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print("Successfully patched ConfigMap/Secret override")
                    return {'success': True, 'message': 'ConfigMap/Secret override patched successfully'}
                else:
                    return {'success': False, 'error': f"Failed to patch ConfigMap/Secret override: {result.get('error', 'Unknown error')}"}
            else:
                return {'success': False, 'error': f"Failed to patch ConfigMap/Secret override: {response.text}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}


    @staticmethod
    def build_cm_cs_payload(
        app_id: int,
        environment_id: int,
        cm_cs_name: str,
        cm_cs_type: str,
        is_external: bool,
        config_data: dict,
        role_arn: str,
        external_type: str,
        eso_secret_data: dict,
        mount_path: str,
        subpath: bool,
        file_permission: str,
        eso_subpath: str,
        merge_strategy: str
    ) -> dict:
        return {
            "appId": app_id,
            "environmentId": environment_id,
            "configData": [
                {
                    "name": cm_cs_name,
                    "type": cm_cs_type,
                    "external": is_external,
                    "data": config_data,
                    "roleARN": role_arn,
                    "externalType": external_type,
                    "esoSecretData": eso_secret_data,
                    "mountPath": mount_path,
                    "subPath": subpath,
                    "filePermission": file_permission,
                    "esoSubPath": eso_subpath,
                    "mergeStrategy": merge_strategy
                }
            ],
            "isExpressEdit": False
        }

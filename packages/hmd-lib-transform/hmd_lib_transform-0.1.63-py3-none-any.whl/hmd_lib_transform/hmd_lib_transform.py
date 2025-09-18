import datetime
import os
from json import loads
from pathlib import Path
from typing import List
from urllib.parse import urljoin
from hmd_graphql_client.hmd_rest_client import RestClient
from requests import request


class HmdLibTransform:
    def __init__(self, base_url: str, api_key: str = None, auth_token: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.auth_token = auth_token
        assert (
            self.api_key or self.auth_token
        ), "Authorization required. Provide a valid api key or auth token."
        if self.api_key:
            self.base_client = RestClient(
                base_url=base_url, loader=None, api_key=self.api_key
            )
            self.headers = {"x-api-key": self.api_key}
        else:
            self.base_client = RestClient(
                base_url=base_url, loader=None, auth_token=self.auth_token
            )
            self.headers = {"Authorization": self.auth_token}

    def _send_request(self, endpoint: str, payload: dict = None, method: str = "POST"):
        resp = request(
            method=method,
            url=urljoin(self.base_url, endpoint),
            json=payload,
            headers=self.headers,
        )
        if resp.status_code != 200:
            raise Exception(f"{resp.status_code}: {resp.json()}")
        return resp.json()

    def get(self, nid: str, entity_name: str):
        """
        Retrieves an entity with its attributes from the transform manager.

        :param nid: identifier for the entity
        :param entity_name: the name of the entity (without namespace); Values accepted: ``transform``,
        ``transform_version``, ``transform_instance``, ``entity_query``, ``transform_engine`` (note: relationships
        can also be retrieved if needed - ``transform_has_transform_version``, ``transform_instance_depends_on_entity``,
        ``transform_instance_depends_on_transform_instance``, ``transform_instance_has_transform_instance_retry``,
        ``transform_instance_runs_on_transform_engine``, ``transform_version_has_entity_query``,
        ``transform_version_has_transform_instance``)

        :return: Entity
        """
        entity_name = "hmd_lang_transform." + entity_name
        return self._send_request(endpoint=f"api/{entity_name}/{nid}", method="GET")

    def load_local_transform_configs(
        self, project_name: str = None, transform_name: str = None
    ):
        """
        Loads transform configs from the local project service. This method can only be used with the local
        transform service and will only load transform configs from a project containing transform definitions
        under ``src/transforms``. A transform name may also be provided if only a subset of the transforms from a
        given project need to be reloaded.

        :param project_name: The name of the project to load transform configs from
        :param transform_name: The name of a transform within the project that should be loaded. (Note: the beginning
        of a transform name may be provided in order to load a subset of the transforms, e.g. "01-" would load any
        transforms that are named starting with "01-")

        :return: List of transform entities (dict) loaded
        """
        payload = {}
        if project_name:
            payload.update({"project_name": project_name})
        if transform_name:
            payload.update({"transform_name": transform_name})
        return self._send_request(f"apiop/get_local_transform_configs", payload)

    def deploy_transform_config(self, artifact_path: str, force: bool = False):
        """
        (Available when running service version 0.1.275 or higher).
        Deploys transform artifacts to the service. Transform projects can be deployed
        like any other repo class.

        :param artifact_path: the artifact content_item_path where the transform build artifact
        is stored

        :return: Mapping of transforms and shared schedules deployed.
        """
        payload = (
            {"artifact_path": artifact_path, "force": force}
            if force
            else {"artifact_path": artifact_path}
        )
        try:
            resp = self._send_request("apiop/deploy_transform_config", payload)
        except Exception as e:
            resp = f"Error deploying configs: {e}"
        return resp

    def load_transform_configs(self):
        """
        Deploys transform configs that have been tagged in the artifact librarian.
        This method can only be used in the local running service in order to test deploying
        transform builds; the corresponding cloud operation is deprecated in version 0.1.275 and later.

        :return: List of transforms loaded into the service.
        """
        env = os.environ.get("HMD_ENVIRONMENT")
        if env and env == "local":
            return self._send_request("apiop/get_transform_configs", {})
        elif not self.base_url.startswith("https"):
            return self._send_request("apiop/get_transform_configs", {})
        else:
            return "This endpoint can only be called from the client for the local service."

    def define_provider_transform(
        self,
        provider_package: str,
        provider_class: str,
        name: str,
        params: dict,
        version: str = "0.1.1",
        run_params: dict = None,
        query_config: dict = None,
    ):
        """
        Defines a new provider transform from arguments. The name and version must be unique in the target service,
        otherwise the config will not be processed. This method is recommended for design iterations; however, a
        transform artifact should be used for promotion up to production environments.

        :param provider_package: The python package that defines the transform execution engine
        :param provider_class: The class name within the provider package used to execute the transform
        :param name: The name of the transform
        :param params: The parameters used by the execution engine to complete the transform
        :param version: The version of the transform (must be greater than any versions under the same transform name
        that have already been deployed to the service)
        :param run_params: (Optional) Parameters that are applied to the code prior to execution. This field is used
        to apply a given transform to different contexts (e.g. a transform that creates a new database table might
        pass the table name as a run parameter so that the table names are dynamically generated according to the
        metadata for a given batch of files, such as the date when the data was generated)
        :param query_config: (Optional) Query configuration that defines what conditions should automatically trigger
        a new instance of the transform being defined. This takes the form of a mapping with the following format:

            .. code-block::

                {
                    "query_name": <named query>,
                    "query_value": {
                        <param1 name>: <param1 value>,
                        <param2 name>: <param2 value>
                    }
                }

        Where the ``query_name`` and ``query_value`` fields are defined as follows:

        - *query_name*: Named graph query defined in the service configuration. This query is executed against the
          global graph database that is shared among NeuronSphere services, which allows transforms to be triggered
          by any service defined in the platform. The most commonly used queries are defined in the service by default
          and are described in detail within the NeuronSphere knowledge base (see 'How to Define Transforms')
        - *query_value*: Values to apply to the named query template. These values allow a given graph query to be
          used for a variety of different use cases, reducing the number of named queries that need to be defined.

        :return: Transform entities added to the service.
        """
        payload = {
            "name": name,
            "version": version,
            "config": {
                "provider_package": provider_package,
                "provider_class": provider_class,
                "params": params,
                "run_params": run_params,
            },
            "query_config": query_config,
        }
        try:
            return self._send_request("apiop/define_provider_transform", payload)
        except Exception as e:
            print(f"Error defining provider transform: {e}")

    def define_trino_transform(
        self,
        name: str,
        version: str = "0.1.1",
        run_params: dict = None,
        query_config: dict = None,
        sql: str = None,
    ):
        """
        Defines a new provider transform using the trino operator from arguments. This method aligns closely with the
        ``define_provider_transform`` endpoint, but with a simplified set of arguments that are specific to the trino
        execution context. Similarly, this method is recommended for design iterations; however, a transform artifact
        should be used for promotion up to production environments.

        :param name: The name of the transform
        :param version: Refer to the definition under ``define_provider_transform``
        :param run_params: Refer to the definition under ``define_provider_transform``
        :param query_config: Refer to the definition under ``define_provider_transform``
        :param sql: The sql statement to execute against the hive metastore using the Trino query engine

        :return: Transform entities added to the service.
        """
        template_folder = os.environ.get("TX_SQL_TEMPLATES")
        if template_folder:
            with open(Path(template_folder) / f"{name}.sql.jinja", "r") as template:
                sql = template.read()
        if sql:
            payload = {
                "name": name,
                "version": version,
                "config": {
                    "provider_package": "hmd_operators.trino",
                    "provider_class": "TrinoOperator",
                    "params": {
                        "sql": sql,
                        "trino_conn_id": "trino_conn",
                        "autocommit": True,
                    },
                    "run_params": run_params,
                },
                "query_config": query_config,
            }
            try:
                return self._send_request("apiop/define_provider_transform", payload)
            except Exception as e:
                print(f"Error defining Trino transform: {e}")
        else:
            # TODO: add template_name and pull from shared lib
            return "Template folder name is required (under TX_SQL_TEMPLATES) or 'sql' parameter must be defined."

    def query_transform_instance(self, instance_nids: List[str]):
        """
        Retrieves a transform_instance entity with its attributes from the transform manager.

        :param instance_nids: List of transform instance identifiers to retrieve.

        :return: Transform instance entities
        """
        inner_payload = (
            '\\"[\\\\\\"' + ('\\\\\\", \\\\\\"'.join(instance_nids)) + '\\\\\\"]\\"'
        )
        request_payload = (
            '{"query":"{ get_hmd_lang_transform_transform_instance_instances( payload: '
            + inner_payload
            + ' ) { identifier instance_name status } }"}'
        )
        try:
            response = self._send_request("graphql", loads(request_payload))
            return response["data"][
                "get_hmd_lang_transform_transform_instance_instances"
            ]
        except Exception as e:
            print(f"Error querying transform instance: {e}")

    def search_transform_instances(self, status: str = None, name: str = None):
        """
        Search for transform instances by status, instance_name or search all.

        :param status: transform instance status to use in the search (one of: "created", "ready", "scheduled",
        "scheduling_failed", "complete_failed", "complete_successful", "cancelled")
        :param name: transform instance_name to use in search filter

        :return: Transform instances
        """
        if status:
            payload = {"attribute": "status", "operator": "=", "value": status}
        elif name:
            payload = {"attribute": "instance_name", "operator": "=", "value": name}
        else:
            payload = {}
        try:
            return self._send_request(
                "api/hmd_lang_transform.transform_instance", payload
            )
        except Exception as e:
            print(f"Error querying transform instance: {e}")

    def search_instances_by_transform_name(self, transform_name: str):
        """
        Search for all transform instances created from a base transform configuration.

        :param transform_name: The name of the base transform to pull instances of.

        :return: List of Transform instances
        """
        payload = {"transform_name": transform_name}
        try:
            return self._send_request(
                "apiop/search_instances_by_transform_name", payload
            )
        except Exception as e:
            print(f"Error retrieving instances: {e}")

    def run_provider_transform(
        self, name: str, run_params: dict = None, priority: int = None
    ):
        """
        Creates and schedules an instance of a provider transform. Run parameters can be provided to validate the
        transform configuration against different use cases. This method can also be used to re-trigger a chain of
        transforms that are created as a result of the successful completion of the original instance (e.g. this is
        often used to re-run transform chains that are not automatically triggered when new data is uploaded, typically
        transforms that define the base schemas and table definitions, or DDL).

        :param name: The name of the transform to instantiate
        :param run_params: A mapping of parameter names and values that should be applied to the transform execution.

        :return: The Transform instance scheduled
        """
        payload = {"name": name}
        if run_params:
            payload.update({"run_params": run_params})
        if priority:
            if priority < 0:
                raise ValueError("Priority must be a non-negative integer.")
            elif priority > 10:
                raise ValueError("Priority must be less than or equal to 10.")
            payload.update({"priority": priority})
        try:
            return self._send_request("apiop/run_provider_transform", payload)
        except Exception as e:
            print(f"Error running transform: {e}")

    def submit_transform(
        self, name: str, entity_nids: List[str] = None, priority: int = None
    ):
        """
        Creates and schedules an instance of a transform. A list of dependent entities (another transform instance, or
        an entity from a different NeuronSphere service, such as a librarian content item) can optionally be provided
        that will be linked as dependencies to the transform instances created. The number of instances created is
        directly proportional to the number of dependencies provided in the list. This method is often useful for
        re-scheduling transform instances that have already been run for the provided dependency, but may need to be
        run with an updated configuration or re-run for validation purposes (e.g. to reprocess data from librarian
        content items, or to re-run one transform within a larger transform chain).

        :param name: The name of the transform to instantiate
        :param entity_nids: The list of dependent entities to create an instance for

        :return: List of Transform instances scheduled
        """
        instances = []
        if entity_nids:
            for nid in entity_nids:
                payload = {"name": name, "entity_nids": [nid]}
                if priority:
                    if priority < 0:
                        raise ValueError("Priority must be a non-negative integer.")
                    elif priority > 10:
                        raise ValueError("Priority must be less than or equal to 10.")
                try:
                    response = self._send_request("apiop/submit_transform", payload)
                    print(response)
                    instances.extend(response)
                except Exception as e:
                    print(f"Error submitting transform: {e}")
                    continue
        else:
            payload = {"name": name}
            if priority:
                if priority < 0:
                    raise ValueError("Priority must be a non-negative integer.")
                elif priority > 10:
                    raise ValueError("Priority must be less than or equal to 10.")
            try:
                response = self._send_request("apiop/submit_transform", payload)
                print(response)
                instances.extend(response)
            except Exception as e:
                print(f"Error submitting transform: {e}")
        return instances

    def get_transforms(self, is_active: str = None):
        """
        Retrieves the name, version and status of all transforms deployed to the transform service.

        :return: List of mappings for each transform in the following format:

            .. code-block::

                [
                    {<transform1 name>: {"version": <deployed config version>, "status": <transform1 status>}},
                    {<transform2 name>: {"version": <deployed config version>, "status": <transform2 status>}}
                    ...
                ]

        Where the status of the transform may be one of the following:

        - *pending*: The transform has been deployed, but is still being prepared for execution.
        - *active*: The transform has been deployed and is ready for execution.
        """
        payload = {"is_active": is_active} if is_active else {}
        try:
            transforms = self._send_request("apiop/get_transforms", payload, "GET")
            transform_info = []
            for transform in transforms:
                payload = {"transform": transform}
                tfv_version = self._send_request(
                    "apiop/get_transform_version", payload, "GET"
                )
                transform_info.append(
                    {
                        transform["name"]: {
                            "status": transform["is_active"],
                            "version": tfv_version,
                        }
                    }
                )
            return transform_info
        except Exception as e:
            print(f"Error getting transforms: {e}")

    def check_dag_status(self):
        """
        Checks the state of deployed transforms in 'pending' state and moves them to active based on the state
        reported back from the associated compute engine (Note: this service operation is run periodically by default
        every three minutes, however, the period can be configured longer or shorter in the service deployment as needed
        and this method can be used to check the state before the next scheduled period on an ad-hoc basis).

        :return: List of transforms moved to active state and/or transform still not yet ready for execution
        """
        try:
            dags = self._send_request("apiop/check_dag_status", {})
            if isinstance(dags, list):
                for dag in dags:
                    print(dag)
            else:
                print(dags)
        except Exception as e:
            print(f"Error getting transform: {e}")

    def get_transforms_ready(self):
        """
        Checks for any transform instances with ``instance_status`` = "ready" and submits the transform for execution
        (Note: deprecated since version 0.1.266; previous versions of the service would run this operation periodically
        and this method was primarily used for submitting instances before the next scheduled period).

        :return: List of transform instances scheduled
        """
        try:
            return self._send_request("apiop/get_transforms_ready", {})
        except Exception as e:
            print(f"Error scheduling transforms: {e}")

    def get_transform_inst_logs(self, instance_nid: str):
        """
        Retrieves execution logs for a given transform instance. This method is primarily used to debug instances
        in state ``complete_failed`` (Note: if an instance is in state ``scheduling_failed``, this indicates the
        transform instance failed during submission of the instance to the respective compute engine and execution
        logs will not be available. In order to debug an instance in ``scheduling_failed`` state, the transform
        service logs should be reviewed in datadog and filtered for any errors).

        :param instance_nid: The identifier for the Transform instance

        :return: Formatted execution logs
        """
        payload = {"instance_nid": instance_nid}
        try:
            logs = self._send_request("apiop/logs", payload)
            print(f"TRANSFORM - {list(logs.keys())[0]}: ")
            logs = list(logs.values())[0]
            if not isinstance(logs, list):
                logs = logs.split("\n")
            for log in logs:
                print(log)
            return "Logs complete."
        except Exception as e:
            print(f"Error retrieving transform logs: {e}")

    def add_output_to_instance(self, instance_nid: str, entity: dict):
        """
        Adds a link between an output entity and the transform instance that generated it. This method is primarily
        used by the compute engines to communicate this association back to the transform service and does not need
        to be called by end users.

        :param instance_nid: The transform instance identifier
        :param entity: Entity information used to create the association. This value should be a mapping in the
        following format:

            .. code-block::

                {
                    "name": <fully qualified entity name>,
                    "id": <entity identifier>
                }

        Where the fields in the mapping are defined as follows:

        - *name*: Fully qualified namespace name that allows the service to pull the entity definition and create
          association (e.g. hmd_lang_transform.transform_instance, hmd_lang_librarian.content_item)
        - *id*: Global unique identifier for the entity

        :return: None
        """
        payload = {"instance_nid": instance_nid, "entity": entity}
        try:
            return self._send_request("apiop/add_output_to_instance", payload)
        except Exception as e:
            print(f"Error upserting relationship: {e}")

    def update_instance_status(
        self, instance_nid: str, status: str, error_message: str = None
    ):
        """
        Updates the status of a Transform instance. This is primarily used to communicate the status of a transform
        execution from the associated compute engine back to the service; however, it may be used by end users
        in case the communication between the compute engine and the service gets interrupted.

        :param instance_nid: Instance identifier
        :param status: a valid instance status ("created", "ready", "scheduled", "scheduling_failed", "complete_failed",
        "complete_successful", "cancelled")
        :param error_message: (Optional) Error message to provide in case the instance status is set to
        "scheduling_failed" or "complete_failed". This message will be logged in the transform service logs and
        will be available in the execution logs for the instance.

        :return: TransformInstance
        """
        payload = {
            "instance_nid": instance_nid,
            "status": status,
            "error_message": error_message,
        }
        try:
            return self._send_request("apiop/update_instance_status", payload)
        except Exception as e:
            print(f"Error updating instance status: {e}")

    def decommission_transform(self, transform_name):
        """
        Updates the status of a base transform entity to "inactive". Once moved to inactive, the configured query
        will no longer be executed to automatically create new instances and instances will no longer be able to be
        created and scheduled ad-hoc (Note: inactive transforms can be reactivated at any time using the
        ``reactivate_transform`` method. This method is never run automatically and must be run manually in order to
        decommission transforms.

        :param transform_name: The name of the transform to decommission.

        :return: Transform entity with updated status
        """
        payload = {"transform_name": transform_name}
        try:
            return self._send_request("apiop/decommission_transform", payload)
        except Exception as e:
            print(f"Error decommissioning transform: {e}")

    def reactivate_transform(self, transform_name):
        """
        Updates the status of a base transform entity to "active". Once moved to active, any configured queries will
        be executed in order to automatically create new instances and instances will be able to be created and
        scheduled ad-hoc using the methods defined in this client library. This method is never run automatically and
        must be run manually in order to reactivate a transform that has been decommissioned.

        :param transform_name: The name of the transform to reactivate.

        :return: Transform entity with updated status
        """
        payload = {"transform_name": transform_name}
        try:
            return self._send_request("apiop/reactivate_transform", payload)
        except Exception as e:
            print(f"Error reactivating transform: {e}")

    def get_schedules(self, entity_name: str = None):
        """
        Used to retrieve all schedule entities defined in NeuronSphere within the target environment. The entity
        name can optionally be provided in order to specify which schedule types to return.

        :param entity_name: (Optional) The type of schedule entity to filter results by (options include: ``daily``,
        ``weekly``, ``monthly``, ``yearly``

        :return: Schedule entities
        """
        payload = {"entity_name": entity_name} if entity_name else {}
        try:
            return self._send_request("apiop/get_schedules", payload)
        except Exception as e:
            print(f"Error getting schedules: {e}")

    def pull_instances_diagram(self, nids: List[str], depth_limit: int = None):
        """
        Used to retrieve all instances and their dependencies for a given pipeline execution. This is compiled into
        a diagram that can be rendered directly within the NeuronSphere Studio or viewed in an image file written
        under ``${HMD_HOME}/transform/diagram`` (Note: these diagrams can be generated from the first transform
        instance in a pipeline or from an entity from a different NeuronSphere service that was used to trigger
        the pipeline).

        :param nids: List of nids to generate dependency diagrams from
        :param depth_limit: The depth to which the dependencies should be queried (this may be useful for large
        dependency trees that may otherwise timeout)

        :return: PlantUML files that can be converted into image files or rendered directly in the studio
        """
        puml_path = Path(os.environ["HMD_HOME"]) / "transform" / "diagrams"
        if "HMD_TRANSFORM_DIAGRAM_PATH" in os.environ:
            puml_path = Path(
                os.environ.get(
                    "HMD_TRANSFORM_DIAGRAM_PATH",
                )
            )
        puml_path.mkdir(exist_ok=True, parents=True)
        diagram_paths = []
        for nid in nids:
            payload = {"nid": nid, "depth_limit": depth_limit}
            try:
                result, name = self._send_request(
                    "apiop/pull_instances_diagram", payload
                )
                print("Diagram pulled. Writing to file..")
                diagram_path = puml_path / f"{name}.puml"
                with diagram_path.open("w") as puml:
                    print(result, file=puml)
                print(f"File write complete. Diagram available at: {diagram_path}")
                diagram_paths.append(diagram_path)
            except Exception as e:
                print(f"Error generating diagrams for {nid}: {e}")
        print("Diagrams generation complete.")
        return diagram_paths

    # Backfill Operations
    def backfill_transform_query(
        self, transform_name: str, filter_: str, dry_run: bool = True, priority: int = 5
    ):
        """
        Creates a backfill instance to reprocess entities that match the provided filter for a given transform.
        This method is typically used when a transform's logic has changed and data that has already been processed
        needs to be reprocessed with the updated logic. The filter should be defined in the same format as the
        filters used in the named queries defined in the service configuration (see 'How to Define Transforms' in
        the NeuronSphere knowledge base for more information on defining these filters).

        :param transform_name: The name of the transform to create a backfill instance for
        :param filter_: A filter defined in the same format as those used in named queries defined in the service
        configuration (e.g. ``{"attribute": "created_at", "operator": ">=", "value": "2024-01-01T00:00:00Z"}``)
        :param priority: The priority to assign to the backfill instances created (default: 5; must be between 0 and 10)

        :return: BackfillInstance created
        """
        if priority < 0 or priority > 10:
            raise ValueError("Priority must be an integer between 0 and 10.")
        payload = {
            "backfill_type": "entity_query",
            "transform_name": transform_name,
            "filter": filter_,
            "priority": priority,
            "dry_run": dry_run,
        }
        try:
            return self._send_request("apiop/backfill_transform", payload)
        except Exception as e:
            print(f"Error creating backfill instance: {e}")

    def backfill_instances(
        self,
        transform_name: str,
        status: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        dry_run: bool = True,
        priority: int = 5,
    ):
        """
        Creates backfill instances for a given transform and status within a specific time range.
        """
        if priority < 0 or priority > 10:
            raise ValueError("Priority must be an integer between 0 and 10.")
        payload = {
            "backfill_type": "instance_query",
            "transform_name": transform_name,
            "instance_status": status,
            "start_time": start_time,
            "end_time": end_time,
            "dry_run": dry_run,
            "priority": priority,
        }
        try:
            return self._send_request("apiop/backfill_transform", payload)
        except Exception as e:
            print(f"Error creating backfill instances: {e}")

    def run_backfill(self, backfill_id: str, priority: int = 5):
        """
        Starts the backfill process for a given backfill instance.
        """
        payload = {"backfill_id": backfill_id, "priority": priority}
        try:
            return self._send_request("apiop/backfill/run", payload)
        except Exception as e:
            print(f"Error starting backfill: {e}")

    def get_backfill_status(self, backfill_id: str):
        """
        Retrieves the status of a given backfill instance.
        """
        try:
            return self._send_request(
                f"apiop/backfill/{backfill_id}/status", {}, method="GET"
            )
        except Exception as e:
            print(f"Error retrieving backfill status: {e}")

    def get_backfill_results(self, backfill_id: str):
        """
        Retrieves the results of a given backfill instance.
        """
        try:
            return self._send_request(
                f"apiop/backfill/{backfill_id}/results", {}, method="GET"
            )
        except Exception as e:
            print(f"Error retrieving backfill results: {e}")

    def list_backfill_events(self, since_date: str = None):
        """
        Lists backfill events that have been created in the transform service. An optional date can be provided
        to filter events that were created after the specified date.

        :param since_date: (Optional) A date string in ISO 8601 format (e.g. "2024-01-01T00:00:00Z") to filter
        events created after the specified date.

        :return: List of BackfillEvent entities
        """
        try:
            return self._send_request(
                f"apiop/backfill_event/list", {"since_date": since_date}, method="POST"
            )
        except Exception as e:
            print(f"Error retrieving backfill results: {e}")

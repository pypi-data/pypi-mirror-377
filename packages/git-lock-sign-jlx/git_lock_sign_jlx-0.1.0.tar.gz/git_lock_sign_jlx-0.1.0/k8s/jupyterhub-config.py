import os, sys
import string
import pickle
import escapism
import random
from kubespawner import KubeSpawner
from oauthenticator.generic import GenericOAuthenticator
import nativeauthenticator
from nativeauthenticator import NativeAuthenticator
from jupyterhub.auth import DummyAuthenticator
from tornado import gen
from textwrap import dedent

# secret object definition
class secret:
    def __init__(self, secret_path, mount_path, type):
        self.secret_path = secret_path
        self.mount_path = mount_path
        self.type = type

    def __str__(self) -> str:
        return f"{self.secret_path}, {self.mount_path}, {self.type}"

# function to generate templating string for Vault secrets
def construct_env_secret_string(secret_path):
    return """{{{{- with secret \"% s\" -}}}}
export {{{{ .Data.key }}}}={{{{ .Data.value }}}}
{{{{- end }}}}""" % secret_path

def construct_ssh_secret_string(secret_path):
    return """{{{{- with secret \"% s\" -}}}}
{{{{ .Data.value }}}}
{{{{- end }}}}""" % secret_path

# function to generate unique and random string
def generate_random_string(length): 
    characters = string.ascii_letters + string.digits 
    random_list = random.sample(characters, length) 
    random_string = ''.join(random_list) 
    return random_string

# Make sure that modules placed in the same directory as the jupyterhub config are added to the pythonpath
configuration_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, configuration_directory)

from z2jh import get_config, get_secret_value

release_name = get_config("Release.Name")
chart_name = get_config("Chart.Name")
compute_enabled = get_config("hub.compute.enabled")
polus_notebooks_hub_enabled = get_config("hub.polusNotebooksHub.enabled")
monitoring_enabled = get_config("hub.monitoring.enabled")
token_service_enabled = get_config("hub.tokenService.enabled")

class ModularKubeSpawner(KubeSpawner):
    def _options_form_default(self):
        return """
        <div style="text-align: center; margin-top: 20px;">
            <h2>JupyterHub UI is disabled</h2>
            <p>Please use Notebooks Hub to start new servers.</p>
        </div>
        """

c.JupyterHub.spawner_class = ModularKubeSpawner
c.ModularKubeSpawner.start_timeout = 1000

c.ModularKubeSpawner.uid = 1000  # uid 1000 corresponds to jovyan, uid 0 to root
c.ModularKubeSpawner.working_dir = "/home/jovyan"
c.ModularKubeSpawner.service_account = f"{release_name}-{chart_name}-user"
c.ModularKubeSpawner.image_pull_policy = "Always"
c.ModularKubeSpawner.pod_name_template = (
    f"{release_name}-{chart_name}-lab-{{username}}--{{servername}}"
)

# Volumes to attach to Pod
c.ModularKubeSpawner.volumes = [
    {
        "name": "notebooks-volume",
        "persistentVolumeClaim": {
            "claimName": f'{release_name}-{chart_name}-hub-{get_config("hub.storage.notebooksClaimName")}'
        },
    },
    {
        "name": "dshm",
        "emptyDir": {"medium": "Memory"},
    }
]

if compute_enabled:
    c.ModularKubeSpawner.volumes.append(
        {
            "name": "compute-volume",
            "persistentVolumeClaim": {
                "claimName": get_config("hub.compute.storageClaimName")
            },
        }
    )

# Mount default volumes
c.ModularKubeSpawner.volume_mounts = [
    {
        "mountPath": "/home/jovyan/work",
        "name": "notebooks-volume",
        "subPath": f"{{username}}",
    },
    {
        "mountPath": "/opt/shared/notebooks",
        "name": "notebooks-volume",
        "subPath": "shared",
    },
    {
        "mountPath": "/dev/shm",
        "name": "dshm",
    }
]

# Parse user options to get Module and Secret data
def parse_user_options(spawner):

    if 'dashboard' in spawner.user_options:
        spawner.user_options["dashboard"] = spawner.user_options["dashboard"].replace("$HOME", "/home/jovyan")

    if 'modules' in spawner.user_options:
        if len(spawner.user_options['modules']) > 0:
            spawner.volumes.append(
                {
                    "name": "modules-volume",
                    "persistentVolumeClaim": {
                        "claimName": f'{release_name}-{chart_name}-hub-{get_config("hub.storage.modulesClaimName")}'
                    },
                }
            )
        lmod_modules = []
        for module in spawner.user_options['modules']:
            spawner.volume_mounts.append(
                {
                    "mountPath": f"/opt/modules/binaries/{module['id']}",
                    "name": "modules-volume", 
                    "subPath": f"binaries/{module['id']}", 
                    "readOnly": not module["write_access"]
                }
            )
            spawner.volume_mounts.append(
                {
                    "mountPath": f"/opt/modules/modulefiles/{module['owner']}/{module['name']}", 
                    "name": "modules-volume", 
                    "subPath": f"modulefiles/{module['owner']}/{module['name']}", 
                    "readOnly": True
                }  
            )

            lmod_modules.append(f"{module['owner']}/{module['module_path']}")
            
        # join array of modules by comma
        lmod_modules = ",".join(lmod_modules)

        spawner.environment.update(
            {"LMOD_SYSTEM_DEFAULT_MODULES": lmod_modules}
        )

    if 'datasets' in spawner.user_options:
        if len(spawner.user_options['datasets']) > 0:
            spawner.volumes.append(
                {
                    "name": "datasets-volume",
                    "persistentVolumeClaim": {
                        "claimName": f'{release_name}-{chart_name}-hub-{get_config("hub.storage.datasetsClaimName")}'
                    },
                }
            )
        for dataset in spawner.user_options['datasets']:
            spawner.volume_mounts.append(
                {
                    "mountPath": f"/opt/datasets/{dataset['name']}",
                    "name": "datasets-volume",
                    "subPath": f"{dataset['id']}",
                    "readOnly": not dataset["write_access"]
                }
            )

    # build on base_annotations with annotations for each secret send from USER_OPTIONS
    # USER_OPTIONS sends secret_path and mount_path for each secret 
    
    if spawner.user_options.get('secrets'):

        base_annotations = {
            "vault.hashicorp.com/agent-inject": "true",
            "vault.hashicorp.com/tls-skip-verify": "true",
            "vault.hashicorp.com/role": f"{{username}}"
        }
    
        spawner.extra_annotations.update(base_annotations)
        
        for data in spawner.user_options['secrets']:
            secret_object = secret(data.get('secret_path'),data.get('mount_path'), data.get('type'))
            random_string = generate_random_string(5)

            # Create unique annotation keys for each secret

            spawner.extra_annotations[f"vault.hashicorp.com/agent-inject-secret-{random_string}"] = f"{secret_object.secret_path}"

            # if the secret is meant to be SSH key for Github
            if secret_object.type == 'raw':
                spawner.extra_annotations[f"vault.hashicorp.com/agent-inject-file-{random_string}"] = "id_rsa"

                more_annotations = {
                        f"vault.hashicorp.com/agent-inject-template-{random_string}": construct_ssh_secret_string(secret_object.secret_path)
                }
                spawner.extra_annotations.update(more_annotations)
                spawner.extra_annotations[f"vault.hashicorp.com/secret-volume-path-{random_string}"] = f"{secret_object.mount_path}"

            # if the secret is meant to be an environment variable
            elif secret_object.type == 'env_var':
                more_annotations = {
                        f"vault.hashicorp.com/agent-inject-template-{random_string}": construct_env_secret_string(secret_object.secret_path)
                }
                spawner.extra_annotations.update(more_annotations)
            
                spawner.extra_annotations[f"vault.hashicorp.com/agent-inject-file-{random_string}"] = f"{random_string}.sh"
                spawner.extra_annotations[f"vault.hashicorp.com/secret-volume-path-{random_string}"] = "/vault/env_scripts"

            else:
                if not secret_object.mount_path:
                    spawner.extra_annotations[f"vault.hashicorp.com/secret-volume-path-{random_string}"] = f"/opt/secret/{secret_object.secret_path}"
                else:
                    spawner.extra_annotations[f"vault.hashicorp.com/secret-volume-path-{random_string}"] = f"{secret_object.mount_path}"

# try and create the extra_containers for the user
def modify_extra_containers(spawner):
    username = spawner.user.name  # <-- dynamic, actual username
    # unescape the username for the git user email
    unescaped_email = username.replace("-40", "@").replace("-2e", ".") # replace -40 with @ and -2e with .

    # now trim the username to exclude the @website.com part
    unescaped_username = unescaped_email.split("@")[0]

    # dynamically build env vars with access to username
    env_vars = [
        {"name": "LOG_LEVEL", "value": "INFO"},
        {"name": "GIT_SSL_VERIFY", "value": "false"},
        {"name": "HOME", "value": "/home/jovyan"},
        {"name": "GPG_KEY", "value": ""},
        {"name": "GIT_USER_EMAIL", "value": f"{unescaped_email}"},
        {"name": "GIT_USER_NAME", "value": f"{unescaped_username}"},
        {"name": "TERM", "value": "xterm"},
        {"name": "GIT_SERVER", "value": "gitea"},
        {"name": "GIT_SERVER_URL", "value": "http://gitea-http.default.svc.cluster.local:3000"},
        {"name": "LANG", "value": "C.UTF-8"},
        {"name": "SIDECAR_DEBUG", "value": "false"},
        {"name": "PYTHON_VERSION", "value": "3.11.13"},
        {"name": "GITEA_ADMIN_EMAIL", "value": "admin@polusai.com"},
        {"name": "PWD", "value": "/app"},
        {"name": "SIDECAR_PORT", "value": "8001"},
        {"name": "DIR", "value": "/home/jovyan/work"},
        {"name": "CREATE_WORK_SUBDIRECTORY", "value": "true"},
        {"name": "SIDECAR_HOST", "value": "localhost"},
        {
            "name": "GITEA_ADMIN_TOKEN",
            "valueFrom": {
                "secretKeyRef": {
                    "name": "gitea-secret",
                    "key": "GITEA_SERVER_ADMIN_TOKEN"
                }
            }
        },
        {
            "name": "GIT_SERVER_ADMIN_TOKEN",
            "valueFrom": {
                "secretKeyRef": {
                    "name": "gitea-secret",
                    "key": "GITEA_SERVER_ADMIN_TOKEN"
                }
            }
        }
    ]
    
    spawner.extra_containers = [{
        "name": "extension-sidecar",
        "image": "liuji1031/celn-sidecar:0.1.4",
        "ports": [
            {
                "containerPort": 8001,
                "name": "sidecar-api"
            }
        ],
        "env": list(env_vars),
        "volumeMounts": [
            {
                "mountPath": "/home/jovyan/work",
                "name": "notebooks-volume",
                "subPath": f"{{username}}"
            }
        ],
        "securityContext": {
            "runAsUser": 1000,
            "allowPrivilegeEscalation": True
        }
    }]

if compute_enabled:
    c.ModularKubeSpawner.volume_mounts.append(
        {"mountPath": get_config("hub.compute.mountPath"), "name": "compute-volume"}
    )

# TODO: safely remove this
c.ModularKubeSpawner.image = "polusai/notebook:" + get_config("hub.appVersions.notebook")

# Create Hub profiles
profile_list = []

jupyterlab_profile = {
    "display_name": f"JupyterLab",
    "slug": f"jupyterlab",
    "profile_options": {},
    "default": True,
    "kubespawner_override": {
        "image": "polusai/notebook:" + get_config("hub.appVersions.notebook"),
        "url": "/lab",
    },
}

notebook_profile = {
    "display_name": f"Jupyter Notebook",
    "slug": f"notebook",
    "profile_options": {},
    "kubespawner_override": {
        "image": "polusai/notebook:" + get_config("hub.appVersions.notebook"),
        "url": "/tree",
        "environment": {
            "DOCKER_STACKS_JUPYTER_CMD": "notebook",
            "NOTEBOOK_ARGS": "--ip=::" if get_config("hub.ipv6.enabled") else "--ip=0.0.0.0",
        }
    },
}

profile_list.extend([jupyterlab_profile, notebook_profile])

if polus_notebooks_hub_enabled:
    profile_list.extend(
        [
            {
                "display_name": "RStudio",
                "slug": "rstudio",
                "kubespawner_override": {"image": "polusai/hub-rstudio:" + get_config("hub.appVersions.rstudio")},
            },
            {
                "display_name": "Streamlit Dashboard",
                "slug": "streamlit",
                "kubespawner_override": {"image": "polusai/hub-streamlit:" + get_config("hub.appVersions.streamlit")},
            },
            {
                "display_name": "Voila Dashboard",
                "slug": "voila",
                "kubespawner_override": {"image": "polusai/hub-voila:" + get_config("hub.appVersions.voila")},
            },
            {
                "display_name": "RShiny Dashboard",
                "slug": "rshiny",
                "kubespawner_override": {"image": "polusai/hub-rshiny:" + get_config("hub.appVersions.rshiny")},
            },
            {
                "display_name": "PyShiny Dashboard",
                "slug": "pyshiny",
                "kubespawner_override": {"image": "polusai/hub-pshiny:" + get_config("hub.appVersions.pshiny")},
            },
            {
                "display_name": "Dash Dashboard",
                "slug": "dash",
                "kubespawner_override": {"image": "polusai/hub-dash:" + get_config("hub.appVersions.dash")},
            },
            {
                "display_name": "VSCode",
                "slug": "vscode",
                "kubespawner_override": {"image": "polusai/hub-vscode:" + get_config("hub.appVersions.vscode")},
            },
            {
                "display_name": "Solara Dashboard",
                "slug": "solara",
                "kubespawner_override": {"image": "polusai/hub-solara:" + get_config("hub.appVersions.solara")},
            }
        ]
    )

# Create profile options based on hardware options
for profile in profile_list:
    hardware_options = {}
    if get_config("hub.hardwareOptions"):
        for hardwareOptionName, hardwareOption in get_config("hub.hardwareOptions").items():
            hardware_options.update(
                {
                    hardwareOptionName: {
                        "display_name": hardwareOption["name"],
                        "slug": f'{profile["slug"]}{hardwareOption["slugSuffix"]}',
                        "default": hardwareOption.get("default", False),
                        "kubespawner_override": {
                            "image": f'{profile["kubespawner_override"]["image"]}{hardwareOption["imageTagSuffix"]}',
                            **(lambda name, slugSuffix, imageTagSuffix, **kw: kw)(
                                **hardwareOption
                            ),
                        },
                    }
                }
            )

    if hardware_options:
        # Single hardware option
        if len(hardware_options) == 1:
            single_hardware_option = next(iter(hardware_options.values()))
            profile["slug"] = single_hardware_option["slug"]
            profile["kubespawner_override"] = single_hardware_option["kubespawner_override"]
        # Multiple hardware options
        if len(hardware_options) > 1:
            profile["profile_options"] =  {"hardwareOptions": {"display_name": "Hardware", "choices": hardware_options}}

c.ModularKubeSpawner.profile_list = profile_list

c.JupyterHub.allow_named_servers = True

if get_config("hub.ipv6.enabled"):
    c.JupyterHub.ip = "::"
    c.JupyterHub.hub_ip = "::"
    c.JupyterHub.hub_bind_url = "http://[::]:8081"
    c.ConfigurableHTTPProxy.api_url = "http://[::1]:8001"
else:
    c.JupyterHub.ip = "0.0.0.0"
    c.JupyterHub.hub_ip = "0.0.0.0"
    c.ConfigurableHTTPProxy.api_url = "http://127.0.0.1:8001"

c.JupyterHub.base_url = get_config("hub.ingress.urlPrefix")

# Required for AWS
c.JupyterHub.hub_connect_ip = f"{release_name}-{chart_name}-internal"

# configure the JupyterHub database
if get_config("postgresql.enabled"):
    postgres_db = get_config("postgresql.auth.database")
    postgres_user = get_config("postgresql.auth.username")
    postgres_password = get_config("postgresql.auth.password")
    c.JupyterHub.db_url = (
        "postgresql://"
        + postgres_user
        + ":"
        + postgres_password
        + "@"
        + release_name
        + "-postgresql-hl"
        + "/"
        + postgres_db
    )
else:
    c.JupyterHub.db_url = "sqlite:///jupyterhub.sqlite"

c.JupyterHub.cleanup_servers = False
c.JupyterHub.cookie_secret_file = "/srv/jupyterhub/jupyterhub_cookie_secret"

if get_config("hub.auth.enabled"):
    ADMIN_USERS = os.getenv("ADMIN_USERS")

    if get_config("hub.auth.type") == "oauth":
        # Default authenticator in production is OAuth with LabShare
        c.JupyterHub.authenticator_class = GenericOAuthenticator

        # Need to persist auth state in database.
        c.Authenticator.enable_auth_state = True
        OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
        OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
        ADMIN_SERVICE_ACC = os.getenv("ADMIN_SERVICE_ACC")

        c.Authenticator.admin_users = set(ADMIN_USERS.split(";"))

        c.GenericOAuthenticator.client_id = OAUTH_CLIENT_ID
        c.GenericOAuthenticator.client_secret = OAUTH_CLIENT_SECRET
        c.GenericOAuthenticator.username_key = "email"
        c.GenericOAuthenticator.userdata_method = "GET"
        c.GenericOAuthenticator.scope = ["openid", "profile", "email"]
        c.GenericOAuthenticator.extra_params = dict(
            client_id=OAUTH_CLIENT_ID, client_secret=OAUTH_CLIENT_SECRET
        )
        c.GenericOAuthenticator.basic_auth = False
        c.GenericOAuthenticator.auto_login = True

        c.GenericOAuthenticator.allow_all = True
    
    elif get_config("hub.auth.type") == "password":
        # NativeAuthenticator is used for environments where Labshare Auth is not available
        c.JupyterHub.authenticator_class = NativeAuthenticator
        c.Authenticator.admin_users = set(ADMIN_USERS.split(";"))
        c.JupyterHub.template_paths = [f"{os.path.dirname(nativeauthenticator.__file__)}/templates/"]
        c.NativeAuthenticator.check_common_password = True
        c.NativeAuthenticator.minimum_password_length = 10
        c.NativeAuthenticator.allowed_failed_logins = 3
    else:
        raise ValueError("Invalid auth type")
else:
    # Fallback to DummyAuthenticator if no auth is configured
    c.JupyterHub.authenticator_class = DummyAuthenticator

# Configure JupyterHub services
services = [
    {
        # Service to shutdown inactive Notebook servers after --timeout seconds
        "name": "cull-idle",
        "command": [
            sys.executable,
            "-m",
            "jupyterhub_idle_culler",
            f"--timeout={3600 * int(get_config('hub.culling.timeout'))}",
            "--remove-named-servers",
        ],
    },
    {
        # Admin service (used in Notebooks Hub and config-wrapper)
        "name": "service-token",
        "api_token": get_secret_value("adminToken"),
    },
]

if monitoring_enabled:
    services.append(
        {
            # Monitoring service (used in Notebooks Hub and config-wrapper)
            "name": "monitoring",
            "api_token": get_secret_value("monitoringToken"),
        }
    )

if token_service_enabled:
    services.append(
        {
            # LabShare Token service
            "name": "token",
            "admin": True,
            "url": f"http://{release_name}-{chart_name}-token",
            "api_token": get_secret_value("tokenServiceToken"),
        }
    )

c.JupyterHub.services = services

# Create RBAC groups and roles
roles = []

roles.append(
    {
        "name": "admin-role",
        "scopes": ["admin:users", "admin:groups", "admin:servers", "shares"],
        "services": ["service-token"],
    }
)

if monitoring_enabled:
    roles.append(
        {
            "name": "monitoring-role",
            "scopes": ["read:metrics"],
            "services": ["monitoring"],
        }
    )

roles.append(
    {
        "name": "cull-idle-role",
        "scopes": [
            "list:users",
            "read:users:activity",
            "read:servers",
            "delete:servers",
        ],
        "services": ["cull-idle",],
    }
)

roles.append(
    {
        "name": "user",
        "scopes": ["self", "shares!user", "read:users:name", "read:groups:name"],
    }
)

c.JupyterHub.load_roles = roles

c.ModularKubeSpawner.server_token_scopes = [
    "shares!server",  # manage shares
    "servers!server",  # start/stop itself
    "users:activity!server",  # report activity
]

# Set up environment variables
environment = {
    "MODULEPATH": "/opt/modules/modulefiles",
    "DASHBOARD_PATH":lambda spawner: str(
        spawner.user_options.get("dashboard")
    ),  # Get the path to dashboard  
    "DASHBOARD_TYPE":lambda spawner: str(
        spawner.user_options.get("dashboard_type", "file")
    ),  # Get the directory type (file vs folder)
    "USER_OPTIONS": lambda spawner: str(spawner.user_options),
    "DOCK8R_NAMESPACE": get_config("hub.dock8r.namespace"),
    "DOCK8R_NOTEBOOKS_PVC": f'{release_name}-{chart_name}-hub-{get_config("hub.storage.notebooksClaimName")}',
    "DASHBOARD_PORT": "8888",
    "NOTEBOOK_ARGS": lambda spawner: "--ip=::" if get_config("hub.ipv6.enabled") else "--ip=0.0.0.0",
    "SIDECAR_HOST": "localhost",
    "SIDECAR_PORT": "8001",
    "GIT_SERVER_URL": "http://gitea:3000",
}

additional_tracked_paths = []
if compute_enabled:
    additional_tracked_paths.append(f'("{get_config("hub.compute.mountPath")}", "{get_config("hub.compute.storageClaimName")}", "")')
additional_tracked_paths = "[" + ",".join(additional_tracked_paths) + "]"

if additional_tracked_paths:
    environment.update(
        {
            "DOCK8R_ADDITIONAL_TRACKED_PATHS": additional_tracked_paths,
        }
    )

# Set up Polus Notebooks Hub environment variables
if polus_notebooks_hub_enabled:
    environment.update(
        {
            "POLUS_NOTEBOOKS_HUB_API": get_config("hub.polusNotebooksHub.apiURL"),
            "POLUS_NOTEBOOKS_HUB_FILE_LOGGING_ENABLED": "True",
        }
    )

if token_service_enabled:
    environment.update(
        {"TOKEN_SERVICE_URL": f"http://{release_name}-{chart_name}/services/token/new",}
    )

def combine_hooks(spawner):
    parse_user_options(spawner)
    modify_extra_containers(spawner)

c.ModularKubeSpawner.environment = environment
c.ModularKubeSpawner.pre_spawn_hook = combine_hooks

import re

# Special inventory filter keys that use NornFlow provided custom filter functions
NORNFLOW_SPECIAL_FILTER_KEYS = ["hosts", "groups"]

# used to track the mandatory kwargs for a NornFlowSettings object
NONRFLOW_SETTINGS_MANDATORY = ("nornir_config_file",)

# used to track the optional kwargs for a NornFlowSettings object
NONRFLOW_SETTINGS_OPTIONAL = {
    "local_tasks_dirs": [],
    "local_workflows_dirs": [],
    "local_filters_dirs": [],
    "imported_packages": [],
    "processors": [],
    "vars_dir": "vars",
}

# Used to check if the kwargs passed to a NornFlow initializer are valid.
# The args listed here are can only be passed through a nornflow settings YAML file
# that will be used to initialize a NornFlowSettings object
NORNFLOW_INVALID_INIT_KWARGS = (
    "nornir_config_file",
    "local_tasks_dirs",
    "local_workflows_dirs",
    "local_filters_dirs",
    "imported_packages",
)

# Supported extensions
NORNFLOW_SUPPORTED_YAML_EXTENSIONS = (".yaml", ".yml")

# Default inventory filter keys
JINJA_PATTERN = re.compile(r"({{.*?}}|{%-?.*?-%?})")

from typing import Any

from coverage import CoveragePlugin
from coverage.config import CoverageConfig, DEFAULT_EXCLUDE
from coverage.plugin_support import Plugins

from smart_covdefaults.defaults import DEFAULT_EXCLUSION, DEFAULT_OPTIONS
from smart_covdefaults.exclusion.conditional import exclude_for_conditions
from smart_covdefaults.exclusion.plaform_based import exclude_for_platform
from smart_covdefaults.exclusion.py_version import exclude_for_py_version


class SmartCovDefaults(CoveragePlugin):
    def __init__(self, **options: Any) -> None:
        self.options = options

    def configure(self, config: CoverageConfig) -> None:
        for option, option_value in DEFAULT_OPTIONS.items():
            if config.get_option(option) is None:
                config.set_option(option, option_value)
        # remove DEFAULT_EXCLUDE, we add a more-strict casing
        exclude = set(config.get_option('report:exclude_lines'))
        exclude.difference_update(DEFAULT_EXCLUDE)
        # add our default exclusion list
        exclude.update(DEFAULT_EXCLUSION)
        exclude.update(exclude_for_py_version())
        exclude.update(exclude_for_platform())
        if "exclude_conditional" in self.options:
            exclude.update(
                exclude_for_conditions(
                    self.options["exclude_conditional"].splitlines()
                )
            )
        config.set_option('report:exclude_lines', sorted(exclude))


def coverage_init(reg: Plugins, options: dict[str, str]) -> None:
    """Coverage init entrypoint."""
    reg.add_configurer(SmartCovDefaults(**options))

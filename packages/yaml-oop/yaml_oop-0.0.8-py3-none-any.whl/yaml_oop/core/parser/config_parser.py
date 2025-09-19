import sys
import os
import yaml
from typing import Any, Optional, Dict
from yaml_oop.core.custom_errors import (
    KeySealedError,
    ConflictingDeclarationError,
    NoOverrideError,
    InvalidVariableError,
    InvalidInstantiationError,
    CircularInheritanceError
)

import yaml_oop.core.parser.inherit_parser as inherit_parser
import yaml_oop.core.parser.next_parser as next_parser
from yaml_oop.core.parser.variable_parser import process_variables
from yaml_oop.core.declarations import DeclarationType
from yaml_oop.core.parser.context import ProcessingContext
from yaml_oop.core.parser.parse_functions import remove_all_key_declarations


# To do: test loaders
# TO DO: yaml anchors and special stuff
# TO DO: (default) values for variables
def process_root_yaml(yaml_data: Any, directory: str, injected_variables: Dict, loader: type) -> Any:
    """Process the root YAML config file inplace."""

    if DeclarationType.ABSTRACT_CONFIG in yaml_data:
        raise NotImplementedError(
            "Cannot process an abstract YAML file. "
            "Abstract objects must be inherited in (base_config) declarations.")
    if DeclarationType.SEALED_CONFIG in yaml_data:
        yaml_data.pop(DeclarationType.SEALED_CONFIG)

    _config_to_root_key_declarations(yaml_data)

    unprocessed_yaml_data = None
    while yaml_data != unprocessed_yaml_data:
        unprocessed_yaml_data = yaml_data.copy() if (type(yaml_data) is dict or type(yaml_data) is list) else yaml_data
        global_variables = {}
        for key in list(injected_variables.keys()):
            if DeclarationType.GLOBAL in key:
                global_variables[key] = injected_variables.pop(key)
        injected_variables = process_variables(
            data=yaml_data,
            base_config={},
            global_variables=global_variables,
            injected_variables=injected_variables
        )

    context = ProcessingContext(
        directory=directory,
        loader=loader,
        variables=injected_variables,
        sub_files=set())
    next_data: Optional[Any] = next_parser.process_next(
        yaml_data=yaml_data,
        context=context)
    yaml_data = next_data if next_data is not None else yaml_data

    # Removes base declarations that are a part of the root config.
    # Removes sub declarations that were not found earlier.
    # Process_dictionary does not compare sub keys that have no equivalent base keys.
    for declaration in DeclarationType.BASE_KEY_DECLARATIONS | DeclarationType.SUB_KEY_DECLARATIONS:
        remove_all_key_declarations(yaml_data, "declaration", declaration)

    return yaml_data


def process_base_config_declaration(
    yaml_data: dict,
    context: ProcessingContext
) -> Optional[Any]:
    """Find the base_config declaration in yaml_data and inherit.
    Returns a replacement node if yaml_data should be replaced by another object (e.g., a list).
    Returns none if yaml_data should remain unmodified."""

    if DeclarationType.BASE_CONFIG not in yaml_data:
        return

    base_config_data = yaml_data.pop(DeclarationType.BASE_CONFIG)
    base_configs: list[Any] = []
    if type(base_config_data) is list:  # Multiple inheritance case.
        for base_config in base_config_data:
            base_configs.append(base_config)
    else:  # Single inheritance case.
        base_configs.append(base_config_data)

    for config_info in base_configs:
        base_data: Any
        instantiation_variables: Dict[str, Any] = {}
        if type(config_info) is str:  # Only file path
            base_config_path: str = config_info
            base_data = _read_yaml(file_path=os.path.join(context.directory, config_info), loader=context.loader)
        elif type(config_info) is dict:  # File path and variables
            if (DeclarationType.BASE_CONFIG_PATH not in config_info.keys() or
                    len(config_info.keys()) != 2 or not
                    any(DeclarationType.VARIABLES in key for key in config_info)):
                raise InvalidInstantiationError(
                    f"Instantiation with {DeclarationType.BASE_CONFIG} must include only "
                    f"{DeclarationType.BASE_CONFIG_PATH} key with string value and "
                    f"{DeclarationType.VARIABLES} key with a dict value."
                )
            base_config_path: str = config_info[DeclarationType.BASE_CONFIG_PATH]
            if type(base_config_path) is not str:
                raise InvalidInstantiationError(
                    f"Instantiation with {DeclarationType.BASE_CONFIG} must include only "
                    f"{DeclarationType.BASE_CONFIG_PATH} key with string value and "
                    f"{DeclarationType.VARIABLES} key with a dict value."
                )
            base_data = _read_yaml(file_path=os.path.join(context.directory, base_config_path), loader=context.loader)
            for config_key in config_info:
                if DeclarationType.VARIABLES in config_key:
                    instantiation_variables = config_info[config_key]

        _config_to_root_key_declarations(base_data)
        global_variables = {key: value for key, value in context.variables.items() if DeclarationType.GLOBAL in key}
        config_info = config_info if type(config_info) is dict else {}
        instantiation_variables = process_variables(
            data=base_data,
            base_config=config_info,
            global_variables=global_variables,
            injected_variables={}
        )

        # Catch circular inheritance
        new_sub_files = context.sub_files.copy()
        if base_config_path in new_sub_files:
            raise CircularInheritanceError(f"Circular inheritance detected with file '{base_config_path}'.")
        new_sub_files.add(base_config_path)
        # Inherit
        new_context: ProcessingContext = ProcessingContext(
            directory=context.directory,
            loader=context.loader,
            variables=instantiation_variables,
            sub_files=new_sub_files,
        )
        if type(base_data) is list and type(yaml_data) is dict and yaml_data != {}:
            raise TypeError(f"Base config '{base_data}' is a list, but yaml_data is a dictionary.")
        elif type(base_data) is dict and type(yaml_data) is dict:
            inherit_parser.process_inherit(
                sub_data=yaml_data,
                base_data=base_data,
                context=new_context,
            )
        elif type(base_data) is list and yaml_data == {}:
            return base_data
        else:
            # Should not reach this point
            raise TypeError(f"Type mismatch for {base_data}. Cannot parse type {type(base_data)}.")
    return None


def _read_yaml(file_path: str, loader: type) -> Any:
    """Read a YAML file and return its content."""

    yaml_data: Any = {}
    try:
        with open(file_path, 'r') as file:
            yaml_data = yaml.load(file, Loader=loader)
    except Exception as e:
        raise Exception(f"Error reading YAML file: {e}")
    return yaml_data


def _config_to_root_key_declarations(yaml_data: Any) -> None:
    """Replaces all yaml_file's config declarations to key declarations inplace."""
    
    if type(yaml_data) is not dict:
        return

    abstract_config: bool
    sealed_config: bool
    override_config: bool
    abstract_config, sealed_config, override_config = False, False, False
    if DeclarationType.ABSTRACT_CONFIG in yaml_data:
        abstract_config = True
        yaml_data.pop(DeclarationType.ABSTRACT_CONFIG)
    if DeclarationType.SEALED_CONFIG in yaml_data:
        sealed_config = True
        yaml_data.pop(DeclarationType.SEALED_CONFIG)
    if DeclarationType.OVERRIDE_CONFIG in yaml_data:
        override_config = True
        yaml_data.pop(DeclarationType.OVERRIDE_CONFIG)

    for key in list(yaml_data.keys()):
        if key == DeclarationType.BASE_CONFIG:
            continue
        if key == DeclarationType.VARIABLES:
            continue

        if abstract_config:
            key = _add_key_declaration(yaml_data, key, DeclarationType.ABSTRACT)
        if sealed_config:
            key = _add_key_declaration(yaml_data, key, DeclarationType.SEALED)
        if override_config:
            key = _add_key_declaration(yaml_data, key, DeclarationType.OVERRIDE)


def _add_key_declaration(data: dict, key: str, declaration: str): 
    """Adds a declaration to a key in the YAML data."""
    new_key = declaration + " " + key
    new_data = data[key]
    data.pop(key)
    data[new_key] = new_data
    return new_key


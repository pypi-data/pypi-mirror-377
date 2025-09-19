import sys
import os
import yaml
from typing import Tuple, Any, Dict, Optional, Set
from yaml_oop.core.custom_errors import (
    KeySealedError,
    ConflictingDeclarationError,
    NoOverrideError,
    InvalidVariableError
)
from .parse_functions import remove_key_declaration
from .parse_functions import remove_all_key_declarations
from ..declarations import DeclarationType


def process_variables(data: Any, base_config: Dict, global_variables: Dict, injected_variables: Dict) -> Dict[str, Set[str]]:
    """Processes variables in data inplace."""
    
    extracted_injected_variables = _extract_variable_declarations(injected_variables, set())
    extracted_global_variables = _extract_variable_declarations(global_variables, set())

    # Extract instantiation variable and declarations from base_config variables declaration
    instantiation_variables = {}
    instantiation_declarations = set()
    if type(base_config) is dict:
        for key in base_config:
            if DeclarationType.VARIABLES in key:
                instantiation_variables = base_config[key]
                instantiation_declarations = _find_variable_key_declarations(key)[0]
                base_config.pop(key)
                break
    extracted_instantiation_variables = _extract_variable_declarations(instantiation_variables, instantiation_declarations)

    # Extract data variables and declarations from data variables declaration
    data_variables = {}
    data_declarations = set()
    if type(data) is dict:
        for key in data:
            if DeclarationType.VARIABLES in key:
                data_variables = data[key]
                data_declarations = _find_variable_key_declarations(key)[0]
                data.pop(key)
                break
    elif type(data) is list:
        for item in data:
            if type(item) is dict and \
               len(item) == 1:
                for key in item:
                    if DeclarationType.VARIABLES in key:
                        data_variables = item[key]
                        data_declarations = _find_variable_key_declarations(key)[0]
                        data.remove(item)
                        break
    extracted_data_variables = _extract_variable_declarations(data_variables, data_declarations)

    _inherit_variables(extracted_instantiation_variables, extracted_injected_variables)
    _inherit_variables(extracted_instantiation_variables, extracted_global_variables)
    _inherit_variables(extracted_data_variables, extracted_instantiation_variables)

    if type(data) is dict:
        _process_dict(data, extracted_data_variables, False)
    elif type(data) is list:
        _process_list(data, extracted_data_variables, False)
    
    # Transform extracted variables back to dict format
    return_variables = {}
    for key, value in extracted_data_variables.items():
        return_key = ""
        for declaration in value[1]:
            return_key += declaration + " " 
        return_key += key
        return_variables[return_key] = value[0]
    return return_variables


def _process_dict(data: dict, variables: Dict[str, Tuple[Any, Set[str]]], is_base_config: bool):
    """Processes a dict for variable DFS replacement inplace."""
    for key in list(data.keys()):
        if key == DeclarationType.BASE_CONFIG:
            is_base_config = True

        if not data[key]:
            continue
        elif is_base_config and DeclarationType.VARIABLES in key:
            carryover_variables = {variable_key: value for variable_key, value in data[key].items() if DeclarationType.CARRYOVER in variable_key}
            for carryover_key in carryover_variables:
                carryover_key_declarations, parsed_carryover_key = _find_variable_key_declarations(carryover_key)
                if parsed_carryover_key in variables:
                    data[key][carryover_key] = variables[parsed_carryover_key][0]
                    carryover_key = remove_key_declaration(data[key], carryover_key, DeclarationType.CARRYOVER)
                    if DeclarationType.ABSTRACT in carryover_key_declarations:
                        remove_key_declaration(data[key], carryover_key, DeclarationType.ABSTRACT)
        elif DeclarationType.OPTIONAL in key:
            key = remove_key_declaration(data, key, DeclarationType.OPTIONAL)
            if type(data[key]) is not str:
                raise InvalidVariableError(f"Optional declaration must be associated with a string value. Key {key} is type: {type(data[key])}")
            if data[key] in variables:
                _replace_value(data, key, variables)
            else:
                data.pop(key)
        elif type(data[key]) is dict:
            _process_dict(data[key], variables.copy(), is_base_config)
            if not data[key]:
                data.pop(key)
        elif type(data[key]) is list:
            _process_list(data[key], variables.copy(), is_base_config)
            if not data[key]:
                data.pop(key)
        else:  # Scalar value
            _replace_value(data, key, variables)


def _process_list(data: list, variables: Dict[str, Tuple[Any, Set[str]]], is_base_config: bool):
    """Processes a list for variable DFS replacement inplace."""
    i = 0
    while i < len(data):
        if not data[i]:
            i += 1
        elif type(data[i]) is str and DeclarationType.OPTIONAL in data[i]:
            data[i] = data[i].replace(DeclarationType.OPTIONAL + " ", "")
            if data[i] in variables:
                _replace_value(data, i, variables)
                i += 1
            else:
                data.pop(i)
        elif type(data[i]) is dict:
            if is_base_config and type(data[i]) is str and DeclarationType.VARIABLES in data[i]:
                for j in data[i]:
                    if j == DeclarationType.BASE_CONFIG:
                        _replace_value(data[i], j, variables)
                        i += 1
            else:
                _process_dict(data[i], variables.copy(), is_base_config)
                if not data[i]:
                    data.pop(i)
                else:
                    i += 1
        elif type(data[i]) is list:
            _process_list(data[i], variables.copy(), is_base_config)
            if not data[i]:
                data.pop(i)
            else:
                i += 1
        else:  # Scalar value
            _replace_value(data, i, variables)
            i += 1


def _extract_variable_declarations(variables: dict, existing_declarations: Set) -> Dict[str, Tuple[Any, Set[str]]]:
    """Returns variable dict with keys without declarations and set of declarations as value.
    Appends existing declarations (declarations declared alongside varaibles declaration) to each variable.
    Return key = key without declaration (key is the substring to be replaced in YAML)
    Return value = (replacement substring, declarations set)"""
    if not variables:
        return {}
    
    extracted_variables = {}
    for key in variables:
        declarations, parsed_key = _find_variable_key_declarations(key)
        declarations = declarations.union(existing_declarations)
        # TO DO: Check for conflicting declarations
        extracted_variables[parsed_key] = (variables[key], declarations)
    return extracted_variables


def _inherit_variables(variables: Dict[str, Tuple[Any, Set[str]]], new_variables: Dict[str, Tuple[Any, Set[str]]]):
    """Inherits variables from new_variables to variables inplace."""
    for new_key in new_variables:
        if new_key in variables and DeclarationType.OVERRIDE not in new_variables[new_key][1]:
            raise NoOverrideError(f"Cannot override variable: '{new_key}' when new variable does not declare override.")
        if new_key in variables and DeclarationType.SEALED in variables[new_key][1]:
            raise KeySealedError(f"Cannot override variable: '{new_key}' when parent variable is sealed.")
        variables[new_key] = new_variables[new_key]


def _replace_value(data: Any, key_or_index: Any, variables: Dict[str, Tuple[Any, Set[str]]]) -> None:
    """For non-string value in data, replaces any matching data_value with variable value inplace.
       For string value in data, replaces any matching substring of data_value with variable value inplace.
       Returns replaced value."""
    if type(data[key_or_index]) is str:
        for variable_key, variable_value in variables.items():
            if type(data[key_or_index]) is not str:
                break  # value was replaced with a non-string; multiple replacements not possible
            elif variable_key in data[key_or_index]:
                if DeclarationType.ABSTRACT in variable_value[1]:
                    raise NotImplementedError(f"Abstract variable {variable_key} cannot be used before being overriden.")
                if type(variable_value[0]) is str:  # TO DO: Multiple string replacements possible. But what if string replacements are ambiguous?
                    data[key_or_index] = data[key_or_index].replace(variable_key, variable_value[0])
                else:
                    data[key_or_index] = variable_value[0]
                    break  # value was replaced with a non-string; multiple replacements not possible
    else:
        if data[key_or_index] in variables.items():
            data[key_or_index] = variables[data[key_or_index]][0]
    

def _find_variable_key_declarations(key: str) -> tuple[set, str]:
    """Returns all declarations and key with no declarations within a variable key."""
    if key == "" or key is None:
        return set(), key
    else:
        declarations = set()
        for item in key.split(" "):
            if item in DeclarationType.VARIABLE_DECLARATIONS:
                declarations.add(item)
                key = key.replace(item + " ", "")
        return declarations, key

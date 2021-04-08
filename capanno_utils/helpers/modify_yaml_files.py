"""
Functions to add, delete, or modify fields in yaml files.
"""

from pathlib import Path
from ruamel.yaml import round_trip_load, YAML
from capanno_utils.helpers.get_paths import get_types_from_path
from capanno_utils.validate import validate_subtool_metadata
from capanno_utils.content_maps import make_tools_map_dict


def add_field_to_to_yaml_file(dict_to_add, yaml_file, after_key=None):
    """
    Add a new field, specified by 'dict_to_add' to the file specified by 'yaml_file' at a position after the key 'after_key'.
    """
    yaml_file = Path(yaml_file)
    assert yaml_file.is_absolute()
    yaml = YAML()
    with yaml_file.open('r') as f:
        file_contents = yaml.load(f)
    if after_key:
        key_position = list(file_contents.keys()).index(after_key)
        i = 1
        for k, v in dict_to_add.items():
            file_contents.insert(key_position + i, k, v)
            i += 1
    else:
        file_contents.update(dict_to_add)
    with yaml_file.open('w') as f:
        yaml.dump(file_contents, f)
    return


def update_subtool_metadata_files(directory_or_file, dict_to_add, after_key=None, base_dir=None):
    """
    Use with caution, this can change the contents of all metadata files in a content repository.
    """
    base_type, specific_type = get_types_from_path(directory_or_file)

    if base_type == 'tool':
        if specific_type == 'metadata':  # update a single metadata file.
            add_field_to_to_yaml_file(dict_to_add, directory_or_file, after_key=after_key)
            validate_subtool_metadata(directory_or_file)
        elif specific_type == 'base_dir':  # update all subtool metadata with new fields.
            tool_map = make_tools_map_dict(base_dir)
            for identifier, values in tool_map.items():
                if values['type'] == 'subtool':
                    metadata_path = values['metadataPath']
                    # Wrap next two lines in try/except?
                    add_field_to_to_yaml_file(dict_to_add, metadata_path,after_key=after_key)
                    validate_subtool_metadata(metadata_path)
                else: # parent metadata
                    pass
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError(f"Have not implemented updating metadata files for {base_type}")
    return
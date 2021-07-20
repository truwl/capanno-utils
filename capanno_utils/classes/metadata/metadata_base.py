#
# * This file is subject to the terms and conditions defined in
# * file 'LICENSE.txt', which is part of this source code package.


from abc import ABC, abstractmethod
from tempfile import NamedTemporaryFile
import logging
from pathlib import Path
import semantic_version
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml import YAML
from ...classes.metadata.common_functions import mk_empty_prop_object, is_attr_empty
from ...classes.metadata.shared_properties import object_attributes
    # CodeRepository, Person, Publication, WebSite, Keyword, ApplicationSuite, ParentScript, Tool, IOObjectItem, CallMap
#
# object_attributes = (CodeRepository, Person, Publication, WebSite, Keyword, ApplicationSuite, ParentScript, Tool, IOObjectItem, CallMap)

class MetadataBase(ABC):
    """Factor stuff out to here."""

    @staticmethod
    @abstractmethod
    def _init_metadata():
        return dict([('name', None), ('metadataStatus', None)])

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        # Can put validators here.
        self._name = new_name

    @property
    def root_repo_path(self):
        return self._root_repo_path

    @root_repo_path.setter
    def root_repo_path(self, new_root_repo_path):
        if new_root_repo_path:
            self._root_repo_path = Path(new_root_repo_path)
        else:
            self._root_repo_path = None
        return

    @property
    def repo_map_dict(self):
        return self._repo_map_dict

    @repo_map_dict.setter
    def repo_map_dict(self, new_repo_map_dict):
        self._repo_map_dict = new_repo_map_dict
        return

    @property
    def metadataStatus(self):
        return self._metadataStatus

    @metadataStatus.setter
    def metadataStatus(self, metadata_status):
        allowed_statuses = ('Incomplete', 'Draft', 'Released')
        if not metadata_status:
            raise ValueError(f"metadataStatus must be set.")
        elif metadata_status not in allowed_statuses:
            raise ValueError(f"metadataStatus cannot be '{metadata_status}' must be one of {allowed_statuses}")
        else:
            self._metadataStatus = metadata_status


    def _get_metafile_keys(self):
        return list(self._init_metadata())

    def __init__(self, **kwargs):
        init_metadata = self._init_metadata()
        ignore_empties = kwargs.pop('ignore_empties', None)  # if not there will be None which is falsey so default is not to ignore.
        # kwargs.pop('ignore_empties', None)
        for k, v in kwargs.items():
            if not k in init_metadata:
                raise AttributeError(f"{k} is not a valid key for {type(self)}")

        for k, v in init_metadata.items():
            if k in kwargs:
                setattr(self, k, kwargs[k])  # Highest priority.
            else:
                try:
                    if getattr(self, k):  # value has already been set by derived class __init__. Second highest priority.
                        continue
                    elif getattr(self, k) == None:  # None values are okay.
                        continue
                    else:  # Have an empty dict, list, or something.
                        raise NotImplementedError(f"Figure out what's happening here and fix it.")
                except AttributeError:
                    setattr(self, k, v)  # Set to default value provided in self._init_metadata. Last resort.
            if ignore_empties:   # Set attribute to None rather than have empty subfields.
                attribute = getattr(self, k)
                if is_attr_empty(attribute):
                    # print(f"Setting {k} to None for {self.name}")
                    setattr(self, k, None)

        return

    def mk_file(self, file_path, keys=None, replace_none=True):
        """

        :param file_path:
        :param keys: if provided, only the keys specified will be included in the file.
        :param replace_none: Will replace None values with empty objects (keys without values) so values can be easily added in the file.
        :return:
        """
        file_path = Path(file_path)
        meta_map = CommentedMap()
        if not keys:
            keys = self._get_metafile_keys()
        for key in keys:
            if key.startswith('_'):
                continue
            if key in ('root_repo_path', 'repo_map_dict', 'check_index', 'tool_identifiers'):
                continue
            if getattr(self, key) is None:
                if replace_none:
                    setattr(self, key, mk_empty_prop_object(key))
                else:
                    continue  # Don't include keys with None values in the file.
            attr_value = getattr(self, key)
            if isinstance(attr_value, object_attributes):
                meta_map[key] = attr_value.dump()
            elif isinstance(attr_value, list):
                if not attr_value:  # empty list
                    meta_map[key] = attr_value
                elif isinstance(attr_value[0], object_attributes):  # Will not work for nested lists.
                    meta_map[key] = [item.dump() for item in attr_value]
                else:
                    meta_map[key] = attr_value
            else:
                meta_map[key] = attr_value
        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)

        with file_path.open('w') as yaml_file:
                yaml.dump(meta_map, yaml_file)
        assert file_path.exists()
        with file_path.open('r') as blah:
            logging.debug(f"{file_path} contents: {blah.readlines()}")
            # print(f"{file_path} contents: {blah.readlines()}")
        return file_path

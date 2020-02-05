# Classes to represent metadata for command line tools.
from pathlib import Path
from collections import OrderedDict
from abc import abstractmethod
import re
from ruamel.yaml import safe_load
from ...helpers.get_paths import get_tool_metadata, get_parent_tool_relative_path_string
from ...classes.metadata.metadata_base import MetadataBase
from ...classes.metadata.shared_properties import CodeRepository, Person, WebSite, Keyword
from ...helpers.get_metadata_from_biotools import make_tool_metadata_kwargs_from_biotools
from ...classes.metadata.common_functions import _mk_hashes, CommonPropsMixin


class ToolMetadataBase(MetadataBase):
    """Factor stuff out to here."""

    @abstractmethod
    def _mk_identifier(self, **kwargs):
        pass

    @abstractmethod
    def _check_identifier(self, identifier):
        pass

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, new_identifier=None, **kwargs):
        if new_identifier:
            identifier = self._check_identifier(new_identifier)
        else:
            identifier = self._mk_identifier(**kwargs)
        self._identifier = identifier

    @property
    def keywords(self):
        return self._keywords

    @keywords.setter
    def keywords(self, keywords_list):
        if keywords_list:
            keywords = []
            for keyword in keywords_list:
                if isinstance(keyword, Keyword):
                    keywords.append(keyword)
                else:
                    if isinstance(keyword, dict):
                        keywords.append(Keyword(**keyword))
                    else:
                        keywords.append(Keyword(keyword))
        else:
            keywords = None
        self._keywords = keywords



class ParentToolMetadata(CommonPropsMixin, ToolMetadataBase):

    @staticmethod
    def _init_metadata():
        """
        Can set default values here.
        :return:
        """
        return OrderedDict([
            ('name', None),
            ('softwareVersion', None),
            ('identifier', None),
            ('featureList', None),
            ('metadataStatus', 'Incomplete'),
            ('description', None),
            ('codeRepository', None),
            ('license', None),
            ('WebSite', None),
            ('contactPoint', None),
            ('publication', None),
            ('keywords', None),
            ('alternateName', None),
            ('creator', None),
            ('programmingLanguage', None),
            ('datePublished', None),
            ('downloadURL', None),
            ('extra', None)
        ])

    def _check_identifier(self, identifier):
        if not identifier[:3] == "TL_":
            raise ValueError(f"Tool identifiers must start with 'TL_' you provided {identifier}")
        else:
            hex_pattern = r'[0-9a-f]{6}\.[0-9a-f]{2}$'
            match_obj = re.match(hex_pattern, identifier[3:])
            if not match_obj:
                raise ValueError(f"Tool identifier not formatted correctly: {identifier}")
        return identifier

    def _mk_identifier(self, start=0):
        if not (self.name and self.softwareVersion.versionName):
            raise ValueError(f"Name and softwareVersion must be provided to make an identifier.")
        name_hash, version_hash = _mk_hashes(self.name, self.softwareVersion.versionName)
        identifier = f"TL_{name_hash[start:start + 6]}.{version_hash[:2]}"
        return identifier

    def make_subtool_metadata(self, subtool_name):
        if not self.featureList:
            raise ValueError(f"Cannot create subtool. featureList of {self.name} is not populated.")
        if subtool_name not in self.featureList:
            raise ValueError(f"{subtool_name} must be in the parent featureList")
        subtool_metadata = SubtoolMetadata(name=subtool_name, _parentMetadata=self)
        return subtool_metadata

    @classmethod
    def load_from_file(cls, file_path, ignore_empties=False):
        file_path = Path(file_path)
        with file_path.open('r') as file:
            file_dict = safe_load(file)
        return cls(**file_dict, ignore_empties=ignore_empties)

    @classmethod
    def create_from_biotools(cls, biotools_id, softwareVersion, subtools, tool_name=None, version='0.1.0'):
        kwargs = make_tool_metadata_kwargs_from_biotools(biotools_id, tool_name=tool_name)
        if not subtools:  # Assume it is a 'standalone' type tool
            subtools = ["__main__"]
        kwargs['featureList'] = list(subtools)  # A lot more to do here.
        kwargs['softwareVersion'] = softwareVersion
        kwargs['version'] = version
        return cls(**kwargs)

    def mk_file(self, base_dir, keys=None, replace_none=True):
        file_path = get_tool_metadata(self.name, self.softwareVersion.versionName, subtool_name=None, parent=True, base_dir=base_dir)
        super().mk_file(file_path, keys, replace_none)


class SubtoolMetadata(CommonPropsMixin, ToolMetadataBase):

    @staticmethod
    def _init_metadata():
        return OrderedDict([
            ('name', None),
            ('metadataStatus', 'Incomplete'),
            ('cwlStatus', 'Incomplete'),
            ('version', '0.1'),
            ('identifier', None),
            ('description', None),
            ('keywords', None),
            ('alternateName', None),
            ('parentMetadata', '../common/common-metadata.yaml'),  # relative path to parentMetadata
            ('_parentMetadata', None),  # ParentMetadata instance. Can be loaded from parentMetadata or set directly.
            ('_primary_file_attrs', None), # Keep track of attributes that are set directly from kwargs and not inherited from parent.
        ])

    def __init__(self, _metadata_file_path=None, **kwargs):
        """
        Initialize SubtoolMetadata.
        :param _metadata_file_path(Path):  Path of yaml file that SubtoolMetadata is loaded from. Should not be used directly. Only used if class is initiated using 'load_from_file' method.
        :param kwargs(dict): Key:value pairs that describe subtool metadata.
        """
        ignore_empties = kwargs.pop('ignore_empties', None)
        self._parentMetadata = kwargs.get('_parentMetadata')
        if self._parentMetadata:
            assert isinstance(self._parentMetadata, ParentToolMetadata)
        else:
            self.parentMetadata = kwargs['parentMetadata']  # must have a path if it isn't set directly.
            self._load_parent_metadata(_metadata_file_path, ignore_empties=ignore_empties)  # sets self._parentMetadata
        self._primary_file_attrs = []
        for k, value in kwargs.items():  # populate _primary_file_attrs
            if value:
                self._primary_file_attrs.append(k)  # keep track of kwargs supplied.
        # self._load_attrs_from_parent()
        super().__init__(**kwargs, ignore_empties=ignore_empties)


    @property
    def name(self):
        """Name of the subtool."""
        return self._name

    @name.setter
    def name(self, value):
        if not value in self._parentMetadata.featureList:
            raise ValueError(f"{value} is not in {self._parentMetadata.name} metadata featureList")
        self._name = value


    @classmethod
    def load_from_file(cls, file_path, ignore_empties=False):
        """Load subtool metadata into SubtoolMetadata from a yaml file."""
        file_path = Path(file_path)
        with file_path.open('r') as file:
            file_dict = safe_load(file)
        return cls(**file_dict, _metadata_file_path=file_path, ignore_empties=ignore_empties)

    def _load_parent_metadata(self, subtool_metadata_file_path, ignore_empties=False):
        """
        Populate SubtoolMetadata._parentMetadata
        :param subtool_metadata_file_path(Path):
        :param ignore_empties(Bool):
        :return:
        """
        dir_name = subtool_metadata_file_path.parent
        full_path = dir_name / self.parentMetadata
        with full_path.resolve().open('r') as f:
            parent_metadata_dict = safe_load(f)
        self._parentMetadata = ParentToolMetadata(**parent_metadata_dict, ignore_empties=ignore_empties)

    def _load_attrs_from_parent(self):
        # initialize everything from parent. Will be overwritten anything supplied in kwargs. Doesn't do much anymore.
        parent_meta = self._parentMetadata
        self.parentMetadata = '../common/common-metadata.yaml'
        # self.identifier = self._mk_identifier()
        # self.keywords = parent_meta.keywords
        return

    def _mk_identifier(self):
        identifier_str, version_str = self._parentMetadata.identifier.split('.', 1)
        subtool_hash = _mk_hashes(self.name)[0][:2]
        identifier = f"{identifier_str}_{subtool_hash}.{version_str}"
        return identifier

    def _check_identifier(self, identifier):
        parent_identifier = self._parentMetadata.identifier
        if not identifier.startswith(parent_identifier[:9]):
            raise ValueError(f"Subtool identifier {identifier} does not properly correspond to parent identifier {parent_identifier}")
        if not identifier.endswith(parent_identifier[-3:]):  # should be '.xx'
            raise ValueError(
                f"Subtool identifier {identifier} does not properly correspond to parent identifier {parent_identifier}")
        hex_pattern = r'[0-9a-f]{6}_[0-9a-f]{2}\.[0-9a-f]{2}$'
        match_obj = re.match(hex_pattern, identifier[3:])
        if not match_obj:
            raise ValueError(f"Tool identifier not formatted correctly: {identifier}")

        return identifier

    @classmethod
    def initialize_from_parent(cls, parent_metadata, subtool_name):
        subtool_dict = {}
        if not subtool_name in parent_metadata.featureList:
            raise ValueError(
                f"Cannot create subtool metadata. {subtool_name} is not in featureList of {parent_metadata.name}")
        subtool_dict['name'] = subtool_name
        return cls(**subtool_dict)

    def mk_completed_file(self):
        raise NotImplementedError

    def mk_instance(self):
        raise NotImplementedError

    def mk_file(self, base_dir, keys=None, replace_none=True):
        try:
            file_path = get_tool_metadata(self._parentMetadata.name, self._parentMetadata.softwareVersion.versionName, subtool_name=self.name, parent=False, base_dir=base_dir)
        except AttributeError:
            print(self)
            raise
        if not file_path.parent.exists():
            file_path.parent.mkdir()
        super().mk_file(file_path, keys, replace_none)

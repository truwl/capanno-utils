# Classes to represent metadata for command line tools.
from pathlib import Path
from collections import OrderedDict
from abc import abstractmethod
import re
import uuid
from ruamel.yaml import safe_load
from capanno_utils.repo_config import *
from capanno_utils.exceptions import InIndexError, NotInIndexError
from ...helpers.get_paths import *
from ...classes.metadata.metadata_base import MetadataBase
from ...classes.metadata.shared_properties import CodeRepository, Person, WebSite, Keyword, IOObjectItem, IOArrayItem
from ...helpers.get_metadata_from_biotools import make_tool_metadata_kwargs_from_biotools
from ...classes.metadata.common_functions import _mk_hashes, CommonPropsMixin, WorkflowLanguageStatusMixin, SoftwarePropsMixin


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
    def identifier(self, new_identifier):
        """
        Assign an identifier to a tool. If tools_map_dict or base_dir is provided, assign an identifier that isn't in use.
        :param new_identifier:
        :return:
        """
        if self.check_index:
            if not self.tool_identifiers and self.root_repo_path:  # Populate self.tool_identifiers if possible.
                self.populate_repo_identifiers_list()
            elif not self.tool_identifiers and not self.root_repo_path:
                raise AttributeError(f"Cannot check identifiers without a root_repo_path or list of identifiers.")
            else:  # self.tool_identifiers is already set.
                pass  # debug message
        if new_identifier:
            identifier = self._check_identifier(new_identifier)  # Let it error if duplicate identifier explicitly passed.
        else:
            identifier = self._mk_identifier()
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

    def populate_repo_identifiers_list(self):
        if not self.root_repo_path:
            raise AttributeError(f"{self} does not have a root_repo_path set.")
        identifiers_index_path = Path(self.root_repo_path) / tool_index_path
        try:
            with identifiers_index_path.open('r') as identifiers_index:
                self.tool_identifiers = identifiers_index.read().splitlines()
        except FileNotFoundError:
            raise


class ParentToolMetadata(CommonPropsMixin, SoftwarePropsMixin, ToolMetadataBase):

    @staticmethod
    def _init_metadata():
        """
        Can set default values here.
        :return:
        """
        return OrderedDict([
            ('name', None),
            ('_in_index', False),  # Specify if a supplied identifier when initializing is already expected to be in the index file. If so, it will avoid an error when using _check_identifier
            ('softwareVersion', None),
            ('root_repo_path', None),  # These need to be set before identifier.
            ('check_index', False),
            ('tool_identifiers', None),
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
            ('extra', None),
        ])

    def _loop_mk_identifier(self, name_hash, version_hash, name_hash_start_index=0, version_hash_start_index=1):
        # Very unlikely that main part of an identifier will be repeated. Version hash is most likely culprit. Can refine later if that's a problem.
        identifier = f"{tool_identifier_prefix}_{name_hash[name_hash_start_index: name_hash_start_index + 6]}.{version_hash[version_hash_start_index:version_hash_start_index + 2]}"
        try:
            self._check_identifier(identifier)
        except AssertionError:
            identifier = self._loop_mk_identifier(name_hash, version_hash, name_hash_start_index=0, version_hash_start_index=version_hash_start_index + 1)
        return identifier

    def _check_identifier(self, identifier):
        if not parent_tool_identifier_pattern.match(identifier):
            raise ValueError(f"Tool identifier not formatted correctly: {identifier}")
        if self.check_index:
            if self._in_index:
                if not identifier in self.tool_identifiers:
                    raise NotInIndexError(f"{identifier} not found in {self.tool_identifiers}")
            else:
                if identifier in self.tool_identifiers:
                    raise InIndexError(f"")
        return identifier

    def _mk_identifier(self, name_hash_start_index=0, version_hash_start_index=0):
        if not (self.name and self.softwareVersion.versionName):
            raise ValueError(f"Name and softwareVersion must be provided to make an identifier.")
        name_hash, version_hash = _mk_hashes(self.name, self.softwareVersion.versionName)
        identifier = f"{tool_identifier_prefix}_{name_hash[name_hash_start_index:name_hash_start_index + 6]}.{version_hash[version_hash_start_index:version_hash_start_index + 2]}"
        try:
            self._check_identifier(identifier)
        except AssertionError:
            identifier = self._loop_mk_identifier(name_hash, version_hash)
        return identifier

    def make_subtool_metadata(self, subtool_name, **kwargs):
        if not self.featureList:
            raise ValueError(f"Cannot create subtool. featureList of {self.name} is not populated.")
        if subtool_name not in self.featureList:
            raise ValueError(f"{subtool_name} must be in the parent featureList")
        subtool_metadata = SubtoolMetadata(name=subtool_name, _parentMetadata=self, **kwargs)
        return subtool_metadata

    @classmethod
    def load_from_file(cls, file_path, ignore_empties=False, **kwargs):
        """

        :param file_path (Path/str): path to the file to load ParentMetadata from.
        :param ignore_empties (bool): If specified, will set empty attributes (those with subkeys but no values) to None.
        :param kwargs:
        :return:
        """
        file_path = Path(file_path)
        with file_path.open('r') as file:
            file_dict = safe_load(file)
        file_dict.update(kwargs)
        file_dict['check_index'] = kwargs.get('check_index', True)  # If not provided in kwargs. Assume metadata loaded from a file is already in the index.
        file_dict['_in_index'] = kwargs.get('_in_index', True)  # Expect is to already be indexed when loading from a file.
        try:
            file_dict['root_repo_path'] = kwargs['root_repo_path']
        except KeyError:
            if file_dict.get('check_index'):
                file_dict['root_repo_path'] = Path(*file_path.parts[:-5])  # This should be the root_repo_path relative to a parent metadata file.
        return cls(**file_dict, ignore_empties=ignore_empties)

    @classmethod
    def create_from_biotools(cls, biotools_id, version_name, subtools, **kwargs):
        biotools_kwargs = make_tool_metadata_kwargs_from_biotools(biotools_id)
        biotools_kwargs.update(kwargs)  # Overwrite any biotools kwargs with kwargs that were provided.
        biotools_kwargs['featureList'] = subtools
        biotools_kwargs['softwareVersion'] = {}
        biotools_kwargs['softwareVersion']['versionName'] = version_name
        return cls(**biotools_kwargs)

    def mk_file(self, base_dir, keys=None, replace_none=True, update_index=True):
        """

        :param base_dir: The root repo path of the repository to make the file in.
        :param keys: If specified, only the indicated keys will be written to the file.
        :param replace_none: If specified, None values will be replaced with default field such as an
        :param update_index: If specified, then the identifier will be added the index file when the file is made.
        :return:
        """
        file_path = get_tool_metadata(self.name, self.softwareVersion.versionName, subtool_name=None, parent=True, base_dir=base_dir)
        returned_path = super().mk_file(file_path, keys, replace_none)
        if update_index:
            index_file_path = self.root_repo_path / tool_index_path
            with index_file_path.open('a') as index_file:
                index_file.write(self.identifier)
                index_file.write('\n')
        return returned_path


class SubtoolMetadata(CommonPropsMixin, WorkflowLanguageStatusMixin, ToolMetadataBase):

    @staticmethod
    def _init_metadata():
        return OrderedDict([
            ('name', None),
            ('check_index', None),  # Will be set to False (default) in __init__
            ('_in_index', False),  # Only used if check_index is True. Will be set to False (default) in __init__
            ('current', False),
            ('metadataStatus', 'Incomplete'),
            ('cwlStatus', 'Incomplete'),
            ('nextflowStatus', 'Incomplete'),
            ('snakemakeStatus', 'Incomplete'),
            ('wdlStatus', 'Incomplete'),
            ('root_repo_path', None),  # These need to be set before identifier.
            ('tool_identifiers', None),
            ('identifier', None),
            ('description', None),
            ('keywords', None),
            ('alternateName', None),
            ('extra', dict(
                [
                    ('sha1', None),
                    ('dockerImage', None),
                ])),# the sha1 hash of the cwlfile associated with this subtool # the docker image pulled or referenced from this subtool's cwlfile
            ('parentMetadata', '../common/common-metadata.yaml'),  # relative path to parentMetadata
            ('_parentMetadata', None),  # ParentMetadata instance. Can be loaded from parentMetadata or set directly.
            ('_primary_file_attrs', None),  # Keep track of attributes that are set directly from kwargs and not inherited from parent.
        ])

    def __init__(self, _metadata_file_path=None, **kwargs):
        """
        Initialize SubtoolMetadata.
        :param _metadata_file_path(Path):  Path of yaml file that SubtoolMetadata is loaded from. Should not be used directly. Only used if class is initiated using 'load_from_file' method.
        :param kwargs(dict): Key:value pairs that describe subtool metadata.
        """
        ignore_empties = kwargs.pop('ignore_empties', None)
        self._parentMetadata = kwargs.get('_parentMetadata')
        check_index = kwargs.get('check_index', False)  # default value needs to be set to same as in _init_metadata.
        in_index = kwargs.get('_in_index', False)
        if self._parentMetadata:  # Will be the case if Subtool is intialized from ParentMetadata.make_subtool_metadata().
            assert isinstance(self._parentMetadata, ParentToolMetadata)
        else:
            self.parentMetadata = kwargs['parentMetadata']  # must have a path if it isn't set directly.
            self._load_parent_metadata(_metadata_file_path, root_repo_path=kwargs.get('root_repo_path'), ignore_empties=ignore_empties, check_index_parent=kwargs.get('check_index'),
                                       parent_in_index=kwargs.get('_in_index'))  # sets self._parentMetadata
        self._primary_file_attrs = []
        for k, value in kwargs.items():  # populate _primary_file_attrs
            if value:
                self._primary_file_attrs.append(k)  # keep track of kwargs supplied. ignore_empties and base_dir were popped off.
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
    def load_from_file(cls, file_path, ignore_empties=False, **kwargs):
        """Load subtool metadata into SubtoolMetadata from a yaml file.
        The Subtool populates it's metadata from ParentMetadata
        """
        file_path = Path(file_path)
        with file_path.open('r') as file:
            file_dict = safe_load(file)
        file_dict.update(kwargs)
        file_dict['parentMetadata'] = kwargs.get('parentMetadata', SubtoolMetadata._init_metadata()['parentMetadata'])  # This needs to be set when initializing. If not specified, set to default.
        file_dict['check_index'] = kwargs.get('check_index',
                                              True)  # Usually expect the identifier to be in the index already if loading from file.
        file_dict['_in_index'] = kwargs.get('_in_index',
                                            True)  # Usually expect the identifier to be in the index already if loading from file.
        try:
            file_dict['root_repo_path'] = kwargs['root_repo_path']
        except KeyError:
            if file_dict.get('check_index'):
                # file_dict['root_repo_path'] = get_base_dir_from_abs_path(file_path)
                file_dict['root_repo_path'] = Path(*file_path.parts[:-5])

        return cls(**file_dict, _metadata_file_path=file_path, ignore_empties=ignore_empties)

    def _load_parent_metadata(self, subtool_metadata_file_path, root_repo_path, ignore_empties=False, check_index_parent=True, parent_in_index=True):
        """
        Populate SubtoolMetadata._parentMetadata
        :param subtool_metadata_file_path(Path):
        :param ignore_empties(Bool):
        :return:
        """
        dir_name = subtool_metadata_file_path.parent
        full_path = dir_name / self.parentMetadata
        full_path = full_path.resolve()
        with full_path.open('r') as f:
            parent_metadata_dict = safe_load(f)
        parent_metadata_dict['root_repo_path'] = root_repo_path
        self._parentMetadata = ParentToolMetadata(**parent_metadata_dict, ignore_empties=ignore_empties, check_index=check_index_parent, _in_index=parent_in_index)

    def _load_attrs_from_parent(self):
        # initialize everything from parent. Will be overwritten anything supplied in kwargs. Doesn't do much anymore.
        parent_meta = self._parentMetadata
        self.parentMetadata = '../common/common-metadata.yaml'
        # self.identifier = self._mk_identifier()
        # self.keywords = parent_meta.keywords
        return

    def _loop_mk_identifier(self, parent_name_str, version_str, subtool_name_hash, hash_split_index=1):
        subtool_hash = subtool_name_hash[hash_split_index:hash_split_index + 2]  # shift hash slice if identifier already exists.
        identifier = f"{parent_name_str}_{subtool_hash}.{version_str}"
        try:
            self._check_identifier(identifier)
        except AssertionError:
            identifier = self._loop_mk_identifier(parent_name_str, version_str, subtool_name_hash, hash_split_index=hash_split_index + 1)
        return identifier

    def _mk_identifier(self):
        parent_name_str, version_str = self._parentMetadata.identifier.split('.', 1)
        subtool_name_hash = _mk_hashes(self.name)[0]
        subtool_hash = subtool_name_hash[:2]
        identifier = f"{parent_name_str}_{subtool_hash}.{version_str}"
        try:
            self._check_identifier(identifier)  # Can only hit AssertionError if tool_map_dict provided.
        except InIndexError:
            identifier = self._loop_mk_identifier(parent_name_str, version_str, subtool_name_hash)
        return identifier

    def _check_identifier(self, identifier):
        if self.check_index:
            if self.tool_identifiers:  # Check to make sure identifiers are not duplicated.
                if self._in_index:
                    try:
                        assert identifier in self.tool_identifiers
                    except AssertionError:
                        raise NotInIndexError(identifier)
                else:
                    try:
                        assert identifier not in self.tool_identifiers
                    except AssertionError:
                        raise InIndexError

        parent_identifier = self._parentMetadata.identifier
        if not identifier.startswith(parent_identifier[:9]):
            raise ValueError(f"Subtool identifier {identifier} does not properly correspond to parent identifier {parent_identifier}")
        if not identifier.endswith(parent_identifier[-3:]):  # should be '.xx'
            raise ValueError(
                f"Subtool identifier {identifier} does not properly correspond to parent identifier {parent_identifier}")
        if not subtool_identifier_pattern.match(identifier):
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

    def mk_instance(self, **kwargs):
        tool_name = f"{self._parentMetadata.name} {self.name}"
        tool_instance_dict = {'toolName': tool_name, 'toolVersion': self._parentMetadata.softwareVersion.versionName, 'toolIdentifier': self.identifier, '_subtoolMetadata': self}
        tool_instance_metadata = ToolInstanceMetadata(**tool_instance_dict, **kwargs)
        return tool_instance_metadata

    def mk_file(self, keys=None, replace_none=True, update_index=True):
        file_path = get_tool_metadata(self._parentMetadata.name, self._parentMetadata.softwareVersion.versionName, subtool_name=self.name, parent=False, base_dir=self.root_repo_path)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
        returned_path = super().mk_file(file_path, keys, replace_none)  # File is made here. Now need to add the key to the identifiers.
        if update_index:
            index_file_path = self.root_repo_path / tool_index_path
            with index_file_path.open('a') as index_file:
                index_file.write(self.identifier)
                index_file.write('\n')
        return returned_path


class ToolInstanceMetadata(MetadataBase):
    @staticmethod
    def _init_metadata():  # Todo: Look at cwlProv to see what kind of metadata they use for CommandLineTool run.
        return OrderedDict([
            ('toolName', None),
            ('toolVersion', None),
            ('name', None),
            ('metadataStatus', 'Incomplete'),
            ('jobStatus', 'Incomplete'),  # Describes status of a job file
            ('toolIdentifier', None),  # Identifier for subtool that this is an instance of.
            ('identifier', None),  # Identifier for the instance
            ('description', None),  # Description of what the instance does.
            ('command', None),  # Generated command. Decide on whether to implement here.
            ('inputObjects', None),
            ('outputObjects', None),
            ('extra', None),
            ('_tool_instance_file_path', None),  # Populated if class is initialized from a file.
            ('_subtoolMetadata', None)  # Store the SubtoolMetadata instance that this is an instance of.
        ])

    def __init__(self, _tool_instance_metadata_file_path=None, **kwargs):
        """
        Initialize ToolInstanceMetadata
        :param _metadata_file_path(Path): Absolute path of yaml file that SubtoolMetadata is loaded from. Should not be used directly. Only used if class is initiated using 'load_from_file' method.
        :param kwargs: Key:value pairs that describe tool instance metadata.
        """
        self._subtoolMetadata = kwargs.get('_subtoolMetadata')
        if self._subtoolMetadata:
            assert isinstance(self._subtoolMetadata, SubtoolMetadata)
        else:
            self._load_subtool_metadata(_tool_instance_metadata_file_path)
        super().__init__(**kwargs)

    def _load_subtool_metadata(self, tool_instance_metadata_path, ignore_empties=False):
        try:
            base_dir = get_base_dir_from_abs_path(tool_instance_metadata_path)
        except TypeError:
            raise
        subtool_metadata_path = get_subtool_metadata_path_from_tool_instance_metadata_path(tool_instance_metadata_path, base_dir=base_dir)

        self._subtoolMetadata = SubtoolMetadata.load_from_file(subtool_metadata_path, root_repo_path=base_dir)

        # with subtool_metadata_path.open('r') as f:
        #     subtool_metadata_dict = safe_load(f)
        # self._subtoolMetadata = SubtoolMetadata(**subtool_metadata_dict)

    @classmethod
    def load_from_file(cls, file_path, ignore_empties=False):
        file_path = Path(file_path)
        with file_path.open('r') as f:
            file_dict = safe_load(f)
        return cls(**file_dict, _tool_instance_metadata_file_path=file_path, ignore_empties=ignore_empties)

    def _mk_identifier(self):
        instance_hash = uuid.uuid4().hex[:4]
        instance_identifier = f"{self.toolIdentifier}.{instance_hash}"
        self._check_identifier(instance_identifier)  # Makes sure the toolIdentifier was correct too.
        return instance_identifier

    def _check_identifier(self, identifier):
        if not identifier.startswith(self.toolIdentifier):
            raise ValueError(f"Tool instance identifier {identifier} does not properly correspond to tool identifer {self.toolIdentifier}")
        if not tool_instance_identifier_pattern.match(identifier):
            raise ValueError(f"Tool instance identifier not formatted correctly: {identifier}")

        return identifier

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, new_identifier=None):
        if new_identifier:
            identifier = self._check_identifier(new_identifier)
        else:
            identifier = self._mk_identifier()
        self._identifier = identifier

    @property
    def inputObjects(self):
        return self._inputObjects

    @inputObjects.setter
    def inputObjects(self, input_objects_list):
        if input_objects_list:
            input_objects = []
            for input_object in input_objects_list:
                if isinstance(input_object, (IOObjectItem, IOArrayItem)):
                    pass  # ready to append
                elif isinstance(input_object, dict):
                    inp_object_keys = input_object.keys()
                    if 'identifier' in inp_object_keys:
                        input_object = IOObjectItem(**input_object)
                    elif 'objects' in inp_object_keys:
                        input_object = IOArrayItem(**input_object)
                    else:
                        raise ValueError(f"")
                else:
                    raise ValueError(f"{input_object} is not a valid value for an input object.")
                input_objects.append(input_object)
        else:
            input_objects = None
        self._inputObjects = input_objects

    @property
    def outputObjects(self):
        return self._outputObjects

    @outputObjects.setter
    def outputObjects(self, output_objects_list):
        if output_objects_list:
            output_objects = []
            for outputput_object in output_objects_list:
                if isinstance(outputput_object, (IOObjectItem, IOArrayItem)):
                    pass  # ready to append
                elif isinstance(outputput_object, dict):
                    output_object_keys = outputput_object.keys()
                    if 'identifier' in output_object_keys:
                        outputput_object = IOObjectItem(**outputput_object)
                    elif 'objects' in output_object_keys:
                        outputput_object = IOArrayItem(**outputput_object)
                    else:
                        raise ValueError(f"")
                else:
                    raise ValueError(f"{outputput_object} is not a valid value for an output object.")
                output_objects.append(outputput_object)
        else:
            output_objects = None
        self._outputObjects = output_objects

    def mk_file(self, base_dir, keys=None, replace_none=True):
        input_hash = self.identifier[-4:]
        file_path = get_tool_instance_metadata_path(self._subtoolMetadata._parentMetadata.name, self.toolVersion, input_hash=input_hash, subtool_name=self._subtoolMetadata.name, base_dir=base_dir)
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)
        return super().mk_file(file_path, keys, replace_none)

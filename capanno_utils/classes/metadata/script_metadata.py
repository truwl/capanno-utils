from pathlib import Path
import re
from collections import OrderedDict
from ruamel.yaml import safe_load
from capanno_utils.repo_config import *
from ...classes.metadata.common_functions import is_attr_empty, CommonPropsMixin, WorkflowLanguageStatusMixin, SoftwarePropsMixin, _mk_hashes
from ...classes.metadata.shared_properties import WebSite, CodeRepository, Person, Publication, Keyword, ParentScript, \
    Tool
from ...classes.metadata.metadata_base import MetadataBase


class ScriptMetadataBase(MetadataBase):
    """Factor stuff out to here if there is more than one ScriptMetadata class."""

    @property
    def parentScripts(self):
        return self._parentScripts

    @parentScripts.setter
    def parentScripts(self, parent_script_list):
        if parent_script_list:
            parent_scripts = []
            for parent_script in parent_script_list:
                if isinstance(parent_script, ParentScript):
                    parent_scripts.append(parent_script)
                else:
                    parent_scripts.append(ParentScript(**parent_script))
        else:
            parent_scripts = None
        self._parentScripts = parent_scripts

    @property
    def programmingLanguage(self):
        return self._programmingLanguage

    @programmingLanguage.setter
    def programmingLanguage(self,programming_language):
        if not isinstance(programming_language, (str, type(None))):
            raise ValueError(f"programmingLanguage must be set to a string. You provided {programming_language}")
        self._programmingLanguage = programming_language


    @property
    def tools(self):
        return self._tools

    @tools.setter
    def tools(self, tools_list):
        if tools_list:
            tools = []
            for tool in tools_list:
                if isinstance(tool, Tool):
                    tools.append(tool)
                else:
                    tools.append(Tool(**tool))
        else:
            tools = None
        self._tools = tools




class ScriptMetadata(CommonPropsMixin, WorkflowLanguageStatusMixin, SoftwarePropsMixin, ScriptMetadataBase):


    @staticmethod
    def _init_metadata():
        return OrderedDict([
            ('name', None),
            ('softwareVersion', None),
            ('identifier', None),
            ('current', False),
            ('metadataStatus', 'Incomplete'),
            ('cwlStatus', 'Incomplete'),
            ('nextflowStatus', 'Incomplete'),
            ('snakemakeStatus', 'Incomplete'),
            ('wdlStatus', 'Incomplete'),
            ('description', None),
            ('codeRepository', None),
            ('WebSite', None),
            ('license', None),
            ('contactPoint', None),
            ('publication', None),
            ('keywords', [Keyword()]),
            ('parentScripts', None),
            ('tools', None),
            ('alternateName', None),
            ('creator', None),
            ('programmingLanguage', None),
            ('datePublished', None),
            ('isCallable', True),  # specify whether the script is meant to be called. If False, just contains attribute_value for importing to other scripts.
            ('parentMetadata', None),
            ('_parentMetadata', None),  # Place to store list of parent ScriptMetadata objects. Different than parentScripts!!
            ('_primary_file_attrs', None),
            # List to store attributes that are not inherited from a parent metadata file or attribute_value.
        ])

    def __init__(self, file_path=Path.cwd(), **kwargs):
        """
        What it's gotta do: see if there's anything in parentMetadata. If so, load it into _parentMetadata. Check for values in kwargs.
        If value is there, leave it alone and put key in _primary_file_attrs. If it is not there, check for highest priority value in _parent_metadada and set to that value.
        The main question. How to do this with the base class init which only expects kwargs as arguments. What if value already set... Think this is taken care of.
        :param file_path:
        :param kwargs:
        """

        ignore_empties = kwargs.pop('ignore_empties', None)
        # Get parent metadata first.
        master_common_metadata = None  # Set to None so nothing happens if no common metadata.
        if kwargs.get('parentMetadata'):
            self.parentMetadata = kwargs['parentMetadata']
            self._load_common_metadata(file_path)  # Will set self._parentMetadata
            master_common_metadata = self._mk_master_common_metadata()

            # populate _primary_attrs and populate required values from common_metadata where required.
            self._primary_file_attrs = []
            for k, value in kwargs.items():
                if value:
                    self._primary_file_attrs.append(k)

        super().__init__(ignore_empties=ignore_empties, **kwargs)
        if master_common_metadata:
            self._update_attributes(master_common_metadata)

    def _check_identifier(self, identifier):
        if not identifier[:3] == f"{script_identifier_prefix}_":
            raise ValueError(f"Script identifiers must start with '{script_identifier_prefix}_' you provided {identifier}")
        else:
            hex_pattern = r'[0-9a-f]{6}\.[0-9a-f]{2}$'
            match_obj = re.match(hex_pattern, identifier[3:])
            if not match_obj:
                raise ValueError(f"Script identifier not formatted correctly: {identifier}")

        return identifier

    def _mk_identifier(self, start=0):
        if not (self.name and self.softwareVersion.versionName):
            raise ValueError(f"Name and softwareVersion must be provided to make an identifier.")
        name_hash, version_hash = _mk_hashes(self.name, self.softwareVersion.versionName)
        identifier = f"{script_identifier_prefix}_{name_hash[start:start + 6]}.{version_hash[:2]}"
        return identifier

    def _load_common_metadata(self, file_path):
        """
        :param file_path: path of the original file that specifies parent/commonMetadata. parentMetadata file paths are relative to this.
        :return:
        """
        self._parentMetadata = []  # List of parent CommonScriptMetadata objects.
        if self.parentMetadata:
            dirname = file_path.parent
            for rel_path in self.parentMetadata:
                full_path = dirname / rel_path
                with full_path.resolve().open('r') as f:
                    common_meta_dict = safe_load(f)
                self._parentMetadata.append(CommonScriptMetadata(**common_meta_dict))
        return

    @classmethod
    def load_from_file(cls, file_path, ignore_empties=False):
        file_path = Path(file_path)
        with file_path.open('r') as file:
            file_dict = safe_load(file)
        return cls(file_path=file_path, ignore_empties=ignore_empties, **file_dict)


    def _update_attributes(self, update_instance):
        """
        Update self with attribute values in update_instance for attributes in self that have not been set.
        :param update_instance:
        :return:
        """
        for attribute_name in self._init_metadata().keys():
            orig_attribute_value = getattr(self, attribute_name)  # See if it's already set on self. If it is, leave it alone.
            try:
                update_instance_attribute_value = getattr(update_instance, attribute_name)
            except AttributeError:
                continue  # Attribute doesn't exist for update_instance so can't be used to update. Move on.

            if orig_attribute_value:  # There's already something there, leave it alone. Might combine data at some point.
                continue
            if is_attr_empty(orig_attribute_value):
                assert True  # Nothing present initally
                if is_attr_empty(update_instance_attribute_value):
                    continue  # Nothing to do here. Move along.
                else:
                    setattr(self, attribute_name, update_instance_attribute_value)
        return

    def _mk_master_common_metadata(self):
        # Combine all common metadata files into a master CommonScriptMetadata instance where lower priority metadata is overwritten by higher priority metadata.
        # This will be used to update the ScriptMetadata instance.
        len_parent_metadata = len(self._parentMetadata)
        if len_parent_metadata == 0:
            master_common_metadata =  None
        elif len_parent_metadata == 1:
            master_common_metadata = self._parentMetadata[0]
        else:
            master_common_metadata = self._parentMetadata[0]    # initialize
            for common_script_metadata in self._parentMetadata[1:]:  # skip first entry since it is used to initialize.
                master_common_metadata.update_from_other_instance(common_script_metadata)
        return master_common_metadata


    def mk_file(self, file_path):
        return super().mk_file(file_path, keys=self._primary_file_attrs)


    def mk_completed_file(self, file_path):
        # substitute in parent metadata fields for fields not specified by the script's own metadata.
        return super().mk_file(file_path)

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, identifier=None, **kwargs):
        if identifier:
            identifier = self._check_identifier(identifier)
        else:
            identifier = self._mk_identifier(**kwargs)
        self._identifier = identifier


    @property
    def isCallable(self):
        return self._is_callable

    @isCallable.setter
    def isCallable(self, callable_value):
        if not isinstance(callable_value, (bool, type(None))):
            assert True
            raise TypeError(f"callable must be a boolean, you provided {callable_value}")
        self._is_callable = callable_value



class CommonScriptMetadata(CommonPropsMixin, SoftwarePropsMixin, ScriptMetadataBase):


    @staticmethod
    def _init_metadata():
        # Only attributes which can be common to multiple scripts. Skips validation of codeRepository
        return OrderedDict([
            ('softwareVersion', None),
            ('description', None),
            ('codeRepository', None),
            ('WebSite', None),
            ('license', None),
            ('contactPoint', None),
            ('publication', None),
            ('keywords', None),
            ('creator', None),
            ('programmingLanguage', None),
            ('datePublished', None),
            ('parentScripts', None),
            ('tools', None),
        ])

    def update_from_other_instance(self, common_script_metadata_instance):
        # Update self from common_script_metadata_instance
        for attribute in self._init_metadata():
            if is_attr_empty(getattr(self, attribute)):
                update_value = getattr(common_script_metadata_instance, attribute)
                if is_attr_empty(update_value):
                    continue
                else:
                    setattr(self, attribute, update_value)
            else:
                continue
        return

    # override softwareVersion so it is not required for CommonScriptMetadata
    @property
    def softwareVersion(self):
        return super().softwareVersion

    @softwareVersion.setter
    def softwareVersion(self, software_version_info):
        if not software_version_info:
            self._softwareVersion = None  # Allows softwar
        else:
            super(CommonScriptMetadata, type(self)).softwareVersion.fset(self, software_version_info)

    @classmethod
    def load_from_file(cls, file_path):
        file_path = Path(file_path)
        with file_path.open('r') as file:
            file_dict = safe_load(file)
        new_instance = cls(**file_dict)
        return new_instance
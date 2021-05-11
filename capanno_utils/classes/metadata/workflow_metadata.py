#
# * This file is subject to the terms and conditions defined in
# * file 'LICENSE.txt', which is part of this source code package.

from collections import OrderedDict
from pathlib import Path
import re
from abc import abstractmethod
from ruamel.yaml import safe_load
from capanno_utils.repo_config import *
from ...classes.metadata.shared_properties import CodeRepository, WebSite, Person, Publication, Keyword, CallMap
from ...classes.metadata.common_functions import _mk_hashes, CommonPropsMixin
from ...classes.metadata.metadata_base import MetadataBase

class WorkflowMetadataBase(MetadataBase):
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
    def identifier(self, identifier=None, **kwargs):
        if identifier:
            identifier = self._check_identifier(identifier)
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
            keywords = [Keyword()]
        self._keywords = keywords



class WorkflowMetadata(CommonPropsMixin, WorkflowMetadataBase):

    @staticmethod
    def _init_metadata():
        return OrderedDict([
        ('name', None),
        ('softwareVersion', None),
        ('description', None),
        ('identifier', None),
        ('metadataStatus', 'Incomplete'),
        ('cwlStatus', 'Incomplete'),
        ('callMap', None),
        ('codeRepository', None),
        ('WebSite', None),
        ('license', None),
        ('contactPoint', None),
        ('publication', None),
        ('keywords', None),
        ('alternateName', None),
        ('creator', None),
        ('programmingLanguage', None),
        ('datePublished', None),
    ])

    def _check_identifier(self, identifier):
        if not identifier[:3] == f"{worklfow_identifier_prefix}_":
            raise ValueError(f"Workflow identifiers must start with '{worklfow_identifier_prefix}_' you provided {identifier}")
        else:
            hex_pattern = r'[0-9a-f]{6}\.[0-9a-f]{2}$'
            match_obj = re.match(hex_pattern, identifier[3:])
            if not match_obj:
                raise ValueError(f"Tool identifier not formatted correctly: {identifier}")
        return identifier

    def _mk_identifier(self, start=0):
        if not (self.name and self.softwareVersion):
            raise ValueError(f"Name and softwareVersion must be provided to make an identifier.")
        name_hash, version_hash = _mk_hashes(self.name, self.softwareVersion)
        identifier = f"{worklfow_identifier_prefix}_{name_hash[start:start + 6]}.{version_hash[:2]}"
        return identifier

    def _make_workflow_inst_identifier(self):
        uuid_string = uuid.uuid4().hex[:4]
        workflowid = self._mk_identifier
        return f"{workflowid}.{uuid_string}"

    @classmethod
    def load_from_file(cls, file_path, ignore_empties=False):
        file_path = Path(file_path)
        with file_path.open('r') as file:
            file_dict = safe_load(file)
        return cls(**file_dict, ignore_empties=ignore_empties)

    def make_instance(self):
        raise NotImplementedError
#
# * This file is subject to the terms and conditions defined in
# * file 'LICENSE.txt', which is part of this source code package.

from collections import OrderedDict
import uuid
from pathlib import Path
import re
from abc import abstractmethod
from ruamel.yaml import safe_load
from capanno_utils.repo_config import *
from ...classes.metadata.shared_properties import CodeRepository, WebSite, Person, Publication, Keyword, CallMap
from ...classes.metadata.common_functions import _mk_hashes, CommonPropsMixin, SoftwarePropsMixin
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



class WorkflowMetadata(CommonPropsMixin, SoftwarePropsMixin, WorkflowMetadataBase):

    @staticmethod
    def _init_metadata():
        return OrderedDict([
        ('name', None),
        ('softwareVersion', None),
        ('current', False),
        ('description', None),
        ('identifier', None),
        ('metadataStatus', 'Incomplete'),
        ('workflowStatus', 'Incomplete'),
        ('workflowLanguage', 'wdl'),
        ('workflowFile', None), # Workflow file.
        ('repoName', None),
        ('gitTag', None),
        ('inputsTemplate', None),
        ('callMap', None),  # This field is to make associations between called tasks/steps and underlying tools/scripts.
        ('graphStatus', 'Incomplete'),
        ('executable', False),  # if configured to execute on Truwl.
        ('codeRepository', None),
        ('WebSite', None),
        ('license', None),
        ('contactPoint', None),
        ('publication', None),
        ('keywords', None),
        ('alternateName', None),
        ('creator', None),
        ('datePublished', None),
    ])

    def _check_identifier(self, identifier):
        if not identifier[:3] == f"{worklfow_identifier_prefix}_":
            raise ValueError(f"Workflow identifiers must start with '{worklfow_identifier_prefix}_' you provided {identifier}")
        else:
            hex_pattern = r'[0-9a-f]{6}\.[0-9a-f]{2,3}$'
            match_obj = re.match(hex_pattern, identifier[3:])
            if not match_obj:
                raise ValueError(f"Workflow identifier not formatted correctly: {identifier}")
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

    @property
    def workflowStatus(self):
        return self._workflowStatus

    @workflowStatus.setter
    def workflowStatus(self, wf_status):
        allowed_statuses = ('Incomplete', 'Draft', 'Released')
        if not wf_status:
            raise ValueError("workflowStatus must be set.")
        elif wf_status not in allowed_statuses:
            raise ValueError(f"worflowStatus must be on of  {allowed_statuses}, not {wf_status}")
        else:
            self._workflowStatus = wf_status

    @property
    def workflowLanguage(self):
        return self._workflowLanguage

    @workflowLanguage.setter
    def workflowLanguage(self, wf_language):
        allowed_languages = ('cwl', 'wdl', 'nextflow', 'snakemake')
        if not wf_language:
            raise ValueError("workflowLanguage must be set.")
        elif wf_language not in allowed_languages:
            raise ValueError(f"workflowLanguage must be on of  {allowed_languages}, not {wf_language}")
        else:
            self._workflowLanguage = wf_language


    @classmethod
    def load_from_file(cls, file_path, ignore_empties=False):
        file_path = Path(file_path)
        with file_path.open('r') as file:
            file_dict = safe_load(file)
        try:
            return cls(**file_dict, ignore_empties=ignore_empties)
        except AttributeError as e:
            raise Exception(f"{e.args} in {file_path}") from e

    def make_instance(self):
        raise NotImplementedError
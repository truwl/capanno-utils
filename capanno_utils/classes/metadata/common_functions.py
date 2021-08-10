#
# * This file is subject to the terms and conditions defined in
# * file 'LICENSE.txt', which is part of this source code package.

from .shared_properties import Publication, Person, CodeRepository, WebSite, Keyword, SoftwareVersion, object_attributes
from hashlib import md5
import uuid




def _mk_hashes(arg1, *args):
    arg1 = str(arg1)
    hashes = [md5(arg1.encode(encoding='utf-8')).hexdigest()]
    for arg in args:
        arg = str(arg)
        hashes.append(md5(arg.encode(encoding='utf-8')).hexdigest())
    return hashes


def mk_empty_prop_object(property_name):
    """
    Should only call this to override a None value for a property.
    :param property_name:
    :return:
    """
    prop_map = {'codeRepository': {'name': None}, 'publication': [{'identifier': None}],
                'contactPoint': [{'name': None}], 'creator': [{'name': None}], 'WebSite': [{'name': None}], 'keywords': [Keyword()], 'applicationSuite': {'name': None, 'softwareVersion': None, 'identifier': None}}
    if not property_name in prop_map:
        return None

    return prop_map[property_name]


def is_attr_empty(attribute):
    # Need to check for lists.
    if isinstance(attribute, list):
        is_empty = True
        for item in attribute:
            if not is_attr_empty(item):
                is_empty = False
                break
    elif isinstance(attribute, object_attributes):
        is_empty = attribute.is_empty()
    elif isinstance(attribute, bool):  # True or False has been provided.
        is_empty = False
    else:
        if attribute:
            is_empty = False
        else:
            is_empty = True
    return is_empty


class WorkflowLanguageStatusMixin:

    @property
    def cwlStatus(self):
        return self._cwlStatus

    @cwlStatus.setter
    def cwlStatus(self, cwl_status):
        allowed_statuses = ('Incomplete', 'Draft', 'Released')
        if not cwl_status:
            raise ValueError("cwlStatus must be set.")
        elif cwl_status not in allowed_statuses:
            raise ValueError(f"cwlStatus must be on of  {allowed_statuses}, not {cwl_status}")
        else:
            self._cwlStatus = cwl_status

    @property
    def snakemakeStatus(self):
        return self._snakemakeStatus

    @snakemakeStatus.setter
    def snakemakeStatus(self, snakemake_status):
        allowed_statuses = ('Incomplete', 'Draft', 'Released')
        if not snakemake_status:
            raise ValueError("snakemakeStatus must be set.")
        elif snakemake_status not in allowed_statuses:
            raise ValueError(f"snakemakeStatus must be on of  {allowed_statuses}, not {snakemake_status}")
        else:
            self._snakemakeStatus = snakemake_status

    @property
    def wdlStatus(self):
        return self._wdlStatus

    @wdlStatus.setter
    def wdlStatus(self, wdl_status):
        allowed_statuses = ('Incomplete', 'Draft', 'Released')
        if not wdl_status:
            raise ValueError("wdlStatus must be set.")
        elif wdl_status not in allowed_statuses:
            raise ValueError(f"wdlStatus must be on of  {allowed_statuses}, not {wdl_status}")
        else:
            self._wdlStatus = wdl_status

    @property
    def nextflowStatus(self):
        return self._nextflowStatus

    @nextflowStatus.setter
    def nextflowStatus(self, nf_status):
        allowed_statuses = ('Incomplete', 'Draft', 'Released')
        if not nf_status:
            raise ValueError("nextflowStatus must be set.")
        elif nf_status not in allowed_statuses:
            raise ValueError(f"nextflowStatus must be on of  {allowed_statuses}, not {nf_status}")
        else:
            self._nextflowStatus = nf_status

class SoftwarePropsMixin:
    """
    This is used by ParentToolMetadata, ScriptMetadata, and WorkflowMetadata
    """
    @property
    def softwareVersion(self):
        return (self._softwareVersion)

    @softwareVersion.setter
    def softwareVersion(self, software_version_info):

        if not software_version_info:  # softwareVersion not defined. Check in parentMetadata
            raise ValueError(f"'softwareVersion must be set.")
        if isinstance(software_version_info, SoftwareVersion):
            software_version = software_version_info
        elif isinstance(software_version_info, dict):
            software_version = SoftwareVersion(**software_version_info)
            # software_version = SoftwareVersion() # Don't initialize directly with **software_version_info. Skips setters.
            # software_version.versionName, software_version.includedVersions = software_version_info['versionName'], software_version_info['includedVersions']
        else:
            raise TypeError(f"Cannot create softwareVersion with {software_version_info}")
        self._softwareVersion = software_version
        return

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, is_current):
        if not isinstance(is_current, bool):
            raise ValueError(f"current must be a boolean value, you specified {is_current}")
        self._current = is_current
        return


    @property
    def publication(self):
        return self._publication

    @publication.setter
    def publication(self, publication_list):
        if publication_list:
            publications = [Publication(**pub) for pub in publication_list]
        else:
            publications = None
        self._publication = publications

    @property
    def contactPoint(self):
        return self._contactPoint

    @contactPoint.setter
    def contactPoint(self, person_list):
        if person_list:
            if isinstance(person_list[0], dict):
                people = [Person(**person) for person in person_list]
            elif isinstance(person_list[0], Person):
                people = person_list
        else:
            people = None
        self._contactPoint = people

    @property
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, person_list):
        if person_list:
            if isinstance(person_list[0], dict):
                people = [Person(**person) for person in person_list]
            elif isinstance(person_list[0], Person):
                people = person_list
            else:
                raise NotImplementedError
        else:
            people = None
        self._creator = people

    @property
    def codeRepository(self):
        return self._codeRepository

    @codeRepository.setter
    def codeRepository(self, code_repo_info):
        if code_repo_info:
            if isinstance(code_repo_info, CodeRepository):
                code_repo = code_repo_info
            elif isinstance(code_repo_info, dict):
                code_repo = CodeRepository(**code_repo_info)
            else:
                raise TypeError(f"Cannot create codeRepository with {code_repo_info}")
        else:
            code_repo = None
        self._codeRepository = code_repo

    @property
    def WebSite(self):
        return self._website

    @WebSite.setter
    def WebSite(self, website_list):
        if website_list:
            if isinstance(website_list[0], WebSite):
                websites = website_list
            elif isinstance(website_list[0], dict):
                websites = [WebSite(**website_dict) for website_dict in website_list]
            else:
                raise TypeError(f"Cannot create WebSite with {website_list}")
        else:
            websites = None
        self._website = websites

    @property
    def license(self):
        return self._license

    @license.setter
    def license(self, license_identifier):
        self._license = license_identifier  # use spdx identifiers

class CommonPropsMixin:
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if not new_name:
            raise ValueError(f"'name'' must be set.")
        self._name = new_name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description_):
        # Accept markdown
        self._description = description_

    @property
    def keywords(self):
        return self._keywords

    @keywords.setter
    def keywords(self, keywords_list):
        if keywords_list:
            keywords = []
            for keyword in keywords_list:
                if isinstance(keyword, Keyword):
                    new_keyword = keyword
                else:
                    if isinstance(keyword, dict):
                        new_keyword  =  Keyword(**keyword)
                    else:
                        new_keyword = Keyword(keyword)  # Should be a uri.
                keywords.append(new_keyword)
        else:
            keywords = None
        self._keywords = keywords

    @property
    def metadataStatus(self):
        return self._metadataStatus

    @metadataStatus.setter
    def metadataStatus(self, metadata_status):
        allowed_statuses = ('Incomplete', 'Draft', 'Released')
        if not metadata_status:
            raise ValueError("metadataStatus must be set.")
        elif metadata_status not in allowed_statuses:
            raise ValueError(f"metadataStatus must be on of  {allowed_statuses}, not {metadata_status}")
        else:
            self._metadataStatus = metadata_status


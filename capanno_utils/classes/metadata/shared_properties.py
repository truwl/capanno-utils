#
# * This file is subject to the terms and conditions defined in
# * file 'LICENSE.md', which is part of this source code package.

from abc import abstractmethod, ABC
from urllib.parse import urlparse
from ruamel.yaml.comments import CommentedMap

class AttributeBase(ABC):

    def __init__(self, *args, **kwargs):
        __slots__ = list(self.attrs)

    def is_empty(self):
        _is_empty = True
        for attribute in self.attrs:
            if isinstance(attribute, list):
                for item in attribute:
                    if getattr(item, 'attrs'):
                        if not item.is_empty():
                            _is_empty = False
                            break
                    elif item:
                        _is_empty = False
                        break
            elif getattr(self, attribute):
                _is_empty = False
                break
            else:
                pass
        return _is_empty

    @staticmethod
    @abstractmethod
    def _attrs():
        return tuple()


    @property
    def attrs(self):
        return self._attrs()



    def dump(self):  # dump a shared property class into a Commented Map which can be written to a file as yaml.
        map_object = CommentedMap()
        for attribute in self.attrs:
            attr_value = getattr(self, attribute)
            if isinstance(attr_value, list):
                attribute_list = []
                for list_item in attr_value:
                    if isinstance(list_item, object_attributes):
                        attribute_list.append(list_item.dump())
                    else:
                        attribute_list.append(list_item)
                map_object[attribute] = attribute_list
            elif isinstance(attr_value, object_attributes):
                map_object[attribute] = attr_value.dump()
            else:
                map_object[attribute] = getattr(self, attribute)
        return map_object



class CodeRepository(AttributeBase):
    def __init__(self, name=None, URL=None):
        super().__init__()
        self._name = name
        self._URL = URL
        return

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        return

    @property
    def URL(self):
        return self._URL

    @URL.setter
    def URL(self, new_URL):
        if new_URL:
            valid_schemes = ['https', 'http', 'git']
            parse_result = urlparse(new_URL)
            if parse_result.scheme not in valid_schemes:
                raise ValueError(f"URL scheme should be in {valid_schemes}")
        else:
            new_URL = None
        self._URL = new_URL
        return


    @staticmethod
    def _attrs():
        return ('name', 'URL')


class WebSite(AttributeBase):
    def __init__(self, name=None, description=None, URL=None):
        super().__init__()
        self._name = name
        self._description = description
        self._URL = URL

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description):
        self._description = new_description

    @property
    def URL(self):
        return self._URL

    @URL.setter
    def URL(self, new_URL):
        if new_URL:
            valid_schemes = ['https', 'http']
            parse_result = urlparse(new_URL)
            if parse_result.scheme not in valid_schemes:
                raise ValueError(f"URL scheme should be in {valid_schemes}")
        else:
            new_URL = None
        self._URL = new_URL
        return

    @staticmethod
    def _attrs():
        return ('name', 'description', 'URL')


class Publication(AttributeBase):
    def __init__(self, identifier=None, headline=None):
        super().__init__()
        self._identifier = identifier
        self._headline = headline
        return

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, new_identifier):
        self._identifier = new_identifier
        return

    @property
    def headline(self):
        return self._headline

    @headline.setter
    def headline(self, new_headline):
        self._headline = new_headline
        return

    @staticmethod
    def _attrs():
        return ('identifier', 'headline')


class Person(AttributeBase):
    def __init__(self, name=None, email=None, identifier=None):
        super().__init__()
        self._name = name
        self._email = email
        self._identifier = identifier

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, new_email):
        self._email = new_email
        return

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, new_identifier):
        self._identifier = new_identifier

    @staticmethod
    def _attrs():
        return ('name', 'email', 'identifier')


class Keyword(AttributeBase):
    def __init__(self, *args, **kwargs):  # Need to initialize off of *args and **kwargs to handle both forms.
        super().__init__()
        args_len = len(args)
        if args_len == 0:
            self._uri = kwargs.get('uri', None)
        elif args_len == 1:
            self._uri = args[0]
        else:
            raise ValueError(f"Expected only one argument for uri for keyword. Got {args}")
        self._name = kwargs.get('name', None)
        self._category = kwargs.get('category', None)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, new_category):
        category_values = (None, 'topic', 'operation')
        if new_category not in category_values:
            raise ValueError(f"{new_category} is not a valid category for a keyword. Must be one of {category_values}")
        self._category = new_category

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, new_uri):
        self._uri = new_uri

    def dump(self):
        if self.uri:
            return self.uri
        else:
            keyword = CommentedMap([('name', self.name), ('category', self.category)])
            return keyword

    @staticmethod
    def _attrs():
        return ('name', 'category', 'uri')


class SoftwareVersion(AttributeBase):
    def __init__(self, versionName=None, includedVersions=None):
        super().__init__()
        self.versionName = versionName
        self.includedVersions = includedVersions

    @property
    def versionName(self):
        return self._versionName

    @versionName.setter
    def versionName(self, new_versionName):
        if not new_versionName:
            raise TypeError(f"versionName must be set.")
        self._versionName = str(new_versionName)

    @property
    def includedVersions(self):
        return self._includedVersions

    @includedVersions.setter
    def includedVersions(self, includedVersions_list):
        if includedVersions_list:
            self._includedVersions = [str(specific_version) for specific_version in includedVersions_list]
        else:
            self._includedVersions = []


    @staticmethod
    def _attrs():
        return ('versionName', 'includedVersions')


class ParentScript(AttributeBase):

    def __init__(self, name=None, version=None, identifier=None):
        super().__init__()
        self._name = name
        self._version = version
        self._identifier = identifier

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name


    @property
    def version(self):
        return str(self._version)

    @version.setter
    def version(self, new_version):
        self._version = str(new_version)

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, new_identifier):
        self._identifier = new_identifier

    @staticmethod
    def _attrs():
        return ('name','version', 'identifier')


class Tool(AttributeBase):

    def __init__(self, name=None, version=None, identifier=None, alternateName=None):
        super().__init__()
        self._name = name
        self._alternateName = alternateName
        self._version = version
        self._identifier = identifier

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def alternateName(self):
        return self._alternateName

    @alternateName.setter
    def alternateName(self, value):
        self._alternateName = value

    @property
    def version(self):
        return str(self._version)

    @version.setter
    def version(self, new_version):
        self._version = str(new_version)

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, new_identifier):
        self._identifier = new_identifier


    @staticmethod
    def _attrs():
        return ('name', 'alternateName', 'version', 'identifier')


class CallMap(AttributeBase):

    def __init__(self, id_=None, identifier=None):
        super().__init__()

        self._id = id_
        self._identifier = identifier

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, new_identifier):
        self._identifier = new_identifier

    @staticmethod
    def _attrs():
        return ('id', 'identifier')


class IOObject(AttributeBase):
    """
    An input or output File or Directory.
    """
    def __init__(self, identifier=None, path=None, uri=None):
        super().__init__()
        self.identifier = identifier
        self.path = path
        self.uri = uri

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, new_identifier):
        self._identifier = new_identifier

    @property
    def path(self):
        """Path on a local machine. Can generate uri from this. Not needed if """
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, new_uri):
        self._uri = new_uri

    @staticmethod
    def _attrs():
        return ('identifier', 'path', 'uri')

class IOObjectItem(AttributeBase):
    """
    Represents an individual file or file_collection/directory object associated with an id in a tool or workflow file.
    """
    def __init__(self, id, new_io_object=None, **io_object_kwargs):
        super().__init__()

        self.id = id
        if new_io_object:
            self.io_object = new_io_object
        else:
            self.io_object = IOObject(**io_object_kwargs)




    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def path(self):
        return self._io_object._path

    @path.setter
    def path(self, new_path):
        self._io_object._path = new_path

    @property
    def io_object(self):
        return self._io_object

    @io_object.setter
    def io_object(self, new_io_object):
        assert isinstance(new_io_object, IOObject)
        self._io_object = new_io_object



    @staticmethod
    def _attrs():
        return ('id', 'io_object')

    def dump(self):
        map_object = CommentedMap()
        map_object['id'] = getattr(self, 'id')
        map_object.update(self.io_object.dump())
        return map_object

class IOArrayItem(AttributeBase):
    def __init__(self, id, objects=None):
        super().__init__()
        self._id = id
        if not objects:
            objects = [IOObject()]
        for index, object in enumerate(objects):
            if isinstance(object, IOObject):
                continue
            elif isinstance(object, dict):
                objects[index] = IOObject(**object)
            else:
                raise ValueError

        self.objects = objects

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def objects(self):
        return self._objects

    @objects.setter
    def objects(self, new_objects):
        for object in new_objects:
            assert isinstance(object, IOObject)
        self._objects = new_objects

    @staticmethod
    def _attrs():
        return ('id', 'objects')





object_attributes = (
CodeRepository, Person, Publication, WebSite, Keyword, Tool, ParentScript, IOObjectItem, CallMap, SoftwareVersion, IOObject, IOObjectItem, IOArrayItem)
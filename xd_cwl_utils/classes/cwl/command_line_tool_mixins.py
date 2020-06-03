
from urllib.parse import urlparse
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from cwltool.process import shortname

def get_short_name(url_string):
    """
    Return the part of a uri after the '#'
    """
    url_parse = urlparse(url_string)
    if url_parse.fragment:
        short_name = url_parse.fragment
    else:
        short_name = url_parse.path.split('#')[-1]
    return short_name



class CommandLineToolMixin:
    """Mixin methods for working with cwl_classes.CommandLineTool objects. These objects should be preprocessed and
    validated before using these methods"""

    cwl_types = ('null', 'boolean', 'int', 'long', 'float', 'double', 'string', 'File', 'Directory')

    def get_schema_def_requirement(self):
        """
        Checks for SchemaDefRequirment in requirements, and if it is there returns it.
        :return: SchemaDefRequirement | None
        """
        schema_def_requirement = None
        if self.requirements:
            for requirement in self.requirements:
                try:
                    requirement.__getattribute__('types')  # Only the SchemaDefRequirment has the types attribute.
                    schema_def_requirement = requirement
                except AttributeError:
                    pass  # Requirement is not SchemaDefRequirement. Ignore it.
        return schema_def_requirement

    def create_cwl_commented_map(self):
        """
        Create a CWL CommentedMap with preferred formatting from CommandLineTool object.
        """

        cwl_map = CommentedMap()
        cwl_map['cwlVersion'] = self.cwlVersion
        cwl_map['class'] = 'CommandLineTool'
        cwl_map['baseCommand'] = self.baseCommand
        if self.requirements:
            cwl_map['requirements'] = [requirement.save() for requirement in self.requirements]
        if self.hints:
            cwl_map['hints'] = self.hints
        optional_class_fields = ['arguments']  # List non-required fields represented as classes that can be handled generically.
        for optional_field_name in optional_class_fields:
            optional_class_value = getattr(self, optional_field_name)
            if optional_class_value:
                cwl_map[optional_field_name] = optional_class_value

            # Non-required fields represented as basic python data types. Order of list determines order in CWL file.
            optional_simple_fields = ['stdin', 'stdout', 'stderr', 'temporaryFailCodes', 'permanentFailCodes',
                                      'successCodes', 'label', 'doc']

            for optional_simple_field in optional_simple_fields:
                optional_field_value = getattr(self, optional_simple_field)
                if optional_field_value:
                    cwl_map[optional_simple_field] = optional_field_value
        cwl_map['inputs'] = self.inputs
        cwl_map['outputs'] = self.outputs

        return cwl_map

    def dump_cwl(self, filename):
        """
        Create a formatted CWL file.
        """
        file_path = Path(filename)
        cwl_yaml = self.create_cwl_commented_map()

        yaml = YAML(pure=True)
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        with file_path.open('w') as cwl_file:
            yaml.dump(cwl_yaml, cwl_file)
            assert True
        return


class CommandInputParameterMixin:

    def _handle_str_input_type(self, _type, schema_def_requirement):
        """
        Should be the terminating function of walking CommandInputParameter.type fields. Return type if type is CWLType,
        otherwise return type from SchemaDefRequirement dict.
        :param _type:
        :param schema_def_dict:
        :return:
        """
        if _type in ('null', 'boolean', 'int', 'long', 'float', 'double', 'string', 'File', 'Directory'):
            _type = _type
        else:
            schema_def_dict = schema_def_requirement._make_schema_def_dict()
            schema_def_name = shortname(_type)
            _type = schema_def_dict[schema_def_name]
        return _type

    def _handle_input_type_field(self, type_field, schema_def_requirement):
        if isinstance(type_field, str):
            input_type = self._handle_str_input_type(type_field, schema_def_requirement)

        elif isinstance(type_field, list):  # got a list of types.
            input_type = []
            for _type in type_field:
                if isinstance(_type, str):
                    input_type.append(self._handle_str_input_type(_type, schema_def_requirement))
                else:  # Need to handle record, enum, and array types here.
                    input_type.append(_type.save())
        else:
            input_type = type_field.save()  # Takes care of CommandInput[Array/Enum/Record]Schmema. Can deal with separately later if we want to.

        return input_type

    def initialize_cwl_file(self, path):
        path = Path(path)


class SchemaDefRequirementMixin:

    def _make_schema_def_dict(self):
        """
        Make dictionary from SchemaDefRequirement to populate inputs parameters fully.

        :param schema_def_requirement: SchemaDefRequirement object.
        :return: keys are input names, values are input parameter fields to drop into inputs section.
        :rtype: dict
        """
        schema_def_types = self.types  # list of InputRecordSchema | InputArraySchema | InputEnumSchema objects.
        if not isinstance(schema_def_types, list):
            raise NotImplementedError
        schema_def_dict = {}
        for type_def in schema_def_types:
            type_def_name = shortname(type_def.name)
            schema_def_dict[type_def_name] = type_def.save()
            schema_def_dict[type_def_name]['name'] = shortname(schema_def_dict[type_def_name]['name'])
            if type_def.type == 'record':
                pass
            elif type_def.type == 'array':
                pass
            elif type_def.type == 'enum':
                raise NotImplementedError("EnumRecordSchema puts long id's in for symbols. Make sure this is handled.")
            else:
                raise ValueError(f"Unexpected InputSchema type {repr(type_def)}")
        return schema_def_dict

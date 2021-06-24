import io
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.representer import RepresenterError
from ruamel.yaml.scalarstring import PreservedScalarString
import logging, sys
import pickle
from capanno_utils.helpers.string_tools import get_shortened_id
from capanno_utils.helpers.file_management import dump_dict_to_yaml_output

logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

cwl_types = ('null', 'boolean', 'int', 'long', 'float', 'double', 'string', 'File', 'Directory')

class CommandLineToolMixin:
    """Mixin methods for working with cwl_classes.CommandLineTool objects. These objects should be preprocessed and
    validated before using these methods"""

    def get_input_parameter_by_short_id(self, id_):
        input_parameter = None
        for command_input_parameter in self.inputs:
            if get_shortened_id(command_input_parameter.id) == id_:
                input_parameter = command_input_parameter
                break
        return input_parameter

    def get_output_parameter_by_short_id(self, id_):
        output_parameter = None
        for command_output_parameter in self.outputs:
            if get_shortened_id(command_output_parameter.id) == id_:
                output_parameter = command_output_parameter
                break
        return output_parameter

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

    @staticmethod
    def _make_sorted_input_names(inputs_list):
        """
        Sort inputs according to their command line binding order.
        :return: list of input ids (names) sorted by command line binding order order.
        :rtype: list
        """
        sort_key_dict = {}
        for input in inputs_list:
            command_line_binding = input.inputBinding
            if not command_line_binding:  # Will not appear on command line.
                continue
            position = command_line_binding.position  # Will be None if not specified.
            if not position:
                position = 999
            input_id = get_shortened_id(input.id)
            sort_key = [position, input_id]
            sort_key_dict[input_id] = sort_key
        sorted_ids = sorted(sort_key_dict.keys(),
                            key=lambda sort_key: (sort_key_dict[sort_key][0], sort_key_dict[sort_key][1]))
        return sorted_ids

    def get_sorted_inputs_dict(self):
        """
        Transform CommandLineTool.inputs into a nested dict attribute_value sorted based on CommandLineBinding.
        CommandInputParameter objects cannot be represented by yaml (I could register it I guess???).

        """
        clt_inputs_list = self.inputs
        unsorted_inputs_dict = {}
        sort_keys_list = self._make_sorted_input_names(clt_inputs_list)
        schema_def_requirement = self.get_schema_def_requirement()
        for command_input in clt_inputs_list:
            input_id = get_shortened_id(command_input.id)
            ordered_input_field = command_input.get_ordered_input_map(schema_def_requirement)
            unsorted_inputs_dict[input_id] = ordered_input_field
        sorted_inputs_dict = CommentedMap((input_name, unsorted_inputs_dict[input_name]) for input_name in sort_keys_list)
        return sorted_inputs_dict

    def get_outputs_dict(self):
        """
        Transform CommandLineTool.outputs into a nested dict.
        """
        outputs_dict = CommentedMap()
        for output in self.outputs:
            output_id = get_shortened_id(output.id)
            outputs_dict[output_id] = output.get_ordered_output()
        return outputs_dict


    def create_cwl_commented_map(self):
        """
        Create a CWL CommentedMap with preferred formatting from CommandLineTool attribute_value.
        """

        cwl_map = CommentedMap()
        cwl_map['cwlVersion'] = self.cwlVersion
        cwl_map['class'] = 'CommandLineTool'
        cwl_map['baseCommand'] = self.baseCommand
        if self.requirements:
            cwl_map['requirements'] = [requirement.save() for requirement in self.requirements]
            logger.debug("reqs: {}".format(cwl_map['requirements']))
        if self.hints:
            cwl_map['hints'] = self.hints
            logger.debug("hints: {}".format(cwl_map['hints']))
        optional_class_fields = ['arguments']  # List non-required fields represented as classes that can be handled generically.
        for optional_field_name in optional_class_fields:
            optional_class_values = getattr(self, optional_field_name)
            if type(optional_class_values) is list:
                cwl_map[optional_field_name] = []
                for optional_class_value in optional_class_values:
                    if isinstance(optional_class_value, str):
                        logger.debug("list member noninstance: {}".format(optional_class_value))
                        cwl_map[optional_field_name] += [optional_class_value]
                    else:
                       try:
                           if 'position' in optional_class_value.attrs:  # Only CommandLineBinding has position in attrs. Avoids cirucular import with using isinstance()
                               logger.debug("list member instance: {}".format(optional_class_value))
                               # TODO: deal with this CommandLineBinding effectively
                               # cwl_map[optional_field_name] = optional_class_value.get_ordered_input_binding()
                           else:
                               raise NotImplementedError  # Something else going on that we'll have to deal with.
                       except AttributeError as e:
                                logging.error(f"Need to deal with {optional_class_value} of type {optional_class_value}")
                                raise
            else:
                if optional_class_values:
                    logger.debug("scalar noninstance: {}".format(optional_class_values))
                    cwl_map[optional_field_name] = optional_class_values

            # Non-required fields represented as basic python data types. Order of list determines order in CWL file.
            optional_simple_fields = ['stdin', 'stdout', 'stderr', 'temporaryFailCodes', 'permanentFailCodes',
                                      'successCodes', 'label', 'doc']

        for optional_simple_field in optional_simple_fields:
            optional_field_value = getattr(self, optional_simple_field)
            if optional_field_value:
                cwl_map[optional_simple_field] = optional_field_value
        cwl_map['inputs'] = self.get_sorted_inputs_dict()
        cwl_map['outputs'] = self.get_outputs_dict()

        return cwl_map

    def dump_cwl_str(self):
        """

        :return:
        """
        cwl_yaml = self.create_cwl_commented_map()
        cwl_string = dump_dict_to_yaml_output(cwl_yaml)
        return cwl_string


    def dump_cwl(self, filename):
        """
        Create a formatted CWL file.
        """
        cwl_yaml = self.create_cwl_commented_map()
        logger.debug("cwl: {}".format(cwl_yaml))
        dump_dict_to_yaml_output(cwl_yaml, filename)
        return


class CommandInputParameterMixin:

    def _handle_str_input_type(self, type_, schema_def_requirement):
        """
        Should be the terminating function of walking CommandInputParameter.type fields.
        The value of _type must be a string here.
        Return type if type is CWLType,
        otherwise return type from SchemaDefRequirement dict.
        :param _type:
        :param schema_def_dict:
        :return:
        """
        if type_ in cwl_types:
            type_ = type_
        else:
            schema_def_dict = schema_def_requirement._make_schema_def_dict()
            schema_def_name = get_shortened_id(type_)
            type_ = schema_def_dict[schema_def_name]
        return type_

    def _handle_input_type_field(self, schema_def_requirement):
        """
        Returns the type, replacing any schema_def_requirement types with the actual type. Also removes 'name' keys for array types.
        Does not handle records and enums yet.

        :param schema_def_requirement:
        :return:
        """
        def format_complex_type(complex_type_field):
            """
            Deal with record, enum, and array types here. Convert these to map types (OrderedDict) without extra stuff (name fields)
            :param complex_type_field:
            :return:
            """
            if hasattr(complex_type_field, 'type'):
                complex_type_field_dict = complex_type_field.save()
                if complex_type_field.type in ('array', 'enum'):
                    del complex_type_field_dict['name']

            else:
                complex_type_field_dict = complex_type_field.save()
            return complex_type_field_dict

        type_field = self.type
        if isinstance(type_field, str):
            input_type = self._handle_str_input_type(type_field, schema_def_requirement)

        elif isinstance(type_field, list):  # got a list of types.
            input_type = []
            for _type in type_field:
                if isinstance(_type, str):
                    input_type.append(self._handle_str_input_type(_type, schema_def_requirement))
                else:  # Need to handle record, enum, and array types here.
                    input_type.append(format_complex_type(_type))
        else:
            input_type = format_complex_type(type_field)  # Takes care of CommandInput[Array/Enum/Record]Schmema. Can deal with separately later if we want to.

        return input_type



    @staticmethod
    def _make_base_input_value_field(input_type, default_value, is_optional=False, comment=None):
        """
        Make a value for a single field in an input template. Terminating function for make_input_value_field.
        :param input_type:
        :param default_value:
        :return:
        """
        defaults = {
            'boolean': False,
            'int': None,
            'long': None,
            'float': None,
            'double': None,
            'string': None,
            'File': {'class': 'File', 'path': None, 'location': None},
            'Directory': {'class': 'File', 'path': None, 'location': None}
        }

        if isinstance(input_type, list):
            if 'null' in input_type:
                is_optional = True
                input_type.remove('null')
            if len(input_type) == 1:
                template_param_value, comment = CommandInputParameterMixin._make_base_input_value_field(input_type[0], default_value, is_optional=is_optional, comment=comment)
            else: # Have an input that accepts multiple types. Have not seen this case yet.
               for input_type_entry in input_type:
                   raise NotImplementedError
        elif isinstance(input_type, dict) and 'type' in input_type:  # includes arrays, enums, and records.
            if input_type['type'] == 'array':
                if input_type['items'] in cwl_types:
                    comment = 'array'
                    template_param_value, comment = CommandInputParameterMixin._make_base_input_value_field(input_type['items'], default_value, is_optional=is_optional, comment=comment)
                    if not isinstance(template_param_value, list):
                        template_param_value = [template_param_value]  # Array should be a list. Make it one if not already.

                else:
                    raise NotImplementedError  # Have an array of records or enums or something.
            elif input_type['type'] == 'enum':
                raise NotImplementedError
            elif input_type['type'] == 'record':
                raise NotImplementedError
            else:
                raise NotImplementedError # type could be 'default' or who knows.

        elif input_type in cwl_types:  # Terminating. Should always hit this eventually.
            if not default_value:
                default_value = defaults[input_type]
            template_param_value = default_value
            if is_optional:
                comment = f"Optional {comment if comment else ''} {input_type}"
            else:
                comment = f"Required {comment if comment else ''}{input_type}"
        else:
            raise ValueError(f"Input type is not a cwl type, list, or dict.")




        return template_param_value, comment

    def make_input_value_field(self, schema_def_requirement):
        """
        Make a key: value pair for the input to use in a job file.
        :return:
        """

        default_value = self.default
        input_type = self._handle_input_type_field(schema_def_requirement)  # takes care of schema_def_requirment stuff.
        template_param_value, comment = self._make_base_input_value_field(input_type, default_value)
        return template_param_value, comment



    def get_ordered_input_map(self, schema_def_requirement):
        """
        Turn a CommandInputParameter into a CommentedMap with a consistent order.
        """
        input_map = CommentedMap()
        if self.label:
            input_map['label'] = self.label
        if self.type:  # type is not required for CommandInputParameter. Never seen this case, but...
            input_map['type'] = self._handle_input_type_field(schema_def_requirement)
        if self.default:
            input_map['default'] = self.default
        if self.inputBinding:
            input_map['inputBinding'] = self.inputBinding.get_ordered_input_binding()
        if self.format:
            input_map['format'] = self.format
        if self.streamable:
            input_map['streamable'] = self.streamable
        if self.secondaryFiles:
            input_map['secondaryFiles'] = self.secondaryFiles
        if self.doc:
            input_map['doc'] = PreservedScalarString(self.doc)
        return input_map


class SchemaDefRequirementMixin:

    def _make_schema_def_dict(self):
        """
        Make dictionary from SchemaDefRequirement to populate inputs parameters fully.

        :param schema_def_requirement: SchemaDefRequirement attribute_value.
        :return: keys are input names, values are input parameter fields to drop into inputs section.
        :rtype: dict
        """
        schema_def_types = self.types  # list of InputRecordSchema | InputArraySchema | InputEnumSchema objects.
        if not isinstance(schema_def_types, list):
            raise NotImplementedError
        schema_def_dict = {}
        for type_def in schema_def_types:
            type_def_name = get_shortened_id(type_def.name)
            schema_def_dict[type_def_name] = type_def.save()
            schema_def_dict[type_def_name]['name'] = get_shortened_id(schema_def_dict[type_def_name]['name'])
            if type_def.type == 'record':
                pass
            elif type_def.type == 'array':
                pass
            elif type_def.type == 'enum':
                raise NotImplementedError("EnumRecordSchema puts long id's in for symbols. Make sure this is handled.")
            else:
                raise ValueError(f"Unexpected InputSchema type {repr(type_def)}")
        return schema_def_dict


class CommandLineBindingMixin:
    def get_ordered_input_binding(self):
        """

        :return:
        """
        input_binding = CommentedMap()
        input_binding_fields = ('prefix', 'position', 'loadContents', 'separate', 'itemSeparator', 'valueFrom')
        for binding_field in input_binding_fields:
            binding_field_value = getattr(self, binding_field)
            if binding_field_value:
                input_binding[binding_field] = binding_field_value
        return input_binding


class CommandOutputParameterMixin:


    def _handle_output_type_field(self):

        def format_complex_type(complex_type_field):  # Duplicated from CommandInputParameterMixin._handle_input_type_field. Refactor someday.
            """
            Deal with record, enum, and array types here. Convert these to map types (OrderedDict) without extra stuff (name fields)
            :param complex_type_field:
            :return:
            """
            if hasattr(complex_type_field, 'type'):
                complex_type_field_dict = complex_type_field.save()
                if complex_type_field.type in ('array', 'enum'):
                    del complex_type_field_dict['name']

            else:
                complex_type_field_dict = complex_type_field.save()
            return complex_type_field_dict
        type_field = self.type
        if isinstance(type_field, str):
            try:
                assert type_field in (*cwl_types, 'stdout')
            except AssertionError:
                raise NotImplementedError(f"Need to handle output type {type_field}")
            output_type = type_field
        elif isinstance(type_field, list):
            output_type = []
            for _type in type_field:
                if isinstance(_type, str):
                    try:
                        assert _type in (*cwl_types, 'stdout')
                    except AssertionError:
                        raise NotImplementedError(f"Need to handle output type {_type}")
                    output_type.append(_type)
                else:
                    output_type.append(format_complex_type(_type))
        else:
            output_type = format_complex_type(type_field)
        return output_type

    def get_ordered_output(self):
        output_map = CommentedMap()
        if self.label:
            output_map['label'] = self.label
        if self.type:
            output_map['type'] = self._handle_output_type_field()
        if self.outputBinding:
            output_map['outputBinding'] = self.outputBinding.save()
        if self.format:
            output_map['format'] = self.format
        if self.streamable:
            output_map['streamable'] = self.streamable
        if self.secondaryFiles:
            output_map['secondaryFiles'] = self.secondaryFiles
        if self.doc:
            output_map['doc'] = self.doc
        return output_map


class WorkflowMixin:

    def get_wf_inputs(self):
        wf_inputs = self.inputs
        inputs_dict = CommentedMap()
        for input in wf_inputs:
            single_input_dict = input.to_dict_with_id_key()
            inputs_dict.update(single_input_dict)
        return inputs_dict

    def get_wf_outputs(self):
        wf_outputs = self.outputs
        outputs_dict = CommentedMap()
        for output in wf_outputs:
            individual_output_dict = output.to_dict_with_id_key()  # output is instance of WorkflowOutputParameter
            outputs_dict.update(individual_output_dict)
        return outputs_dict

    def get_wf_steps(self):
        wf_steps = self.steps
        steps_dict = CommentedMap()
        for step in wf_steps:
            individual_step_dict = step.to_dict_with_id_key()
            steps_dict.update(individual_step_dict)
        return steps_dict

    def get_input_parameter_by_short_id(self, id_):
        for input_parameter in self.inputs:
            if get_shortened_id(input_parameter.id) == id_:
                return input_parameter
        return



    def dump_cwl(self, filename):
        cwl_map = CommentedMap()
        cwl_map['cwlVersion'] = self.cwlVersion
        cwl_map['class'] = 'Workflow'
        requirements = self.requirements
        if requirements:
            cwl_map['requirements'] = [requirement.save() for requirement in requirements]
        hints = self.hints
        if hints:
            cwl_map['hints'] = hints  # No idea why hints aren't stored as classes.
        # optional_simple_fields list determines order of these fields if they are present.
        optional_simple_fields = ['label', 'doc']
        for optional_field in optional_simple_fields:
            optional_field_value = getattr(self, optional_field)
            if optional_field_value:
                cwl_map[optional_field] = optional_field_value
        cwl_map['inputs'] = self.get_wf_inputs()  # list of InputParameter objects.
        cwl_map['outputs'] = self.get_wf_outputs()
        cwl_map['steps'] = self.get_wf_steps()
        dump_dict_to_yaml_output(cwl_map, filename)
        return


class InputParameterMixin:

    def to_dict_with_id_key(self):
        input_dict = CommentedMap()
        input_id = get_shortened_id(self.id)
        input_dict[input_id] = CommentedMap()
        input_dict[input_id]['type'] = self.type
        return input_dict

class WorkflowOutputParameterMixin:

    def to_dict_with_id_key(self):
        output_dict = CommentedMap()
        output_id = get_shortened_id(self.id)
        output_dict[output_id] = CommentedMap()
        output_dict[output_id]['type'] = self.type
        output_source_id = self.outputSource
        rel_output_source_id = '/'.join(output_source_id.split('#')[-1].split('/')[1:])
        output_dict[output_id]['outputSource'] = rel_output_source_id
        return output_dict

class WorkflowStepMixin:

    def to_dict_with_id_key(self):
        step_dict = CommentedMap()
        step_id = get_shortened_id(self.id)
        step_dict[step_id] = CommentedMap()
        step_dict[step_id]['run'] = get_shortened_id(self.run)
        step_dict[step_id]['in'] = CommentedMap()
        for step_input in self.in_:  # list of WorkflowStepInput instances.
            step_dict[step_id]['in'].update(step_input.get_workflow_step_inputs())  # WorkflowStepInput class
        # step_dict[step_id]['in'] = [step_input.return_workflow_step_input_dict() for step_input in self.in_]
        step_dict[step_id]['out'] = [get_shortened_id(output) for output in self.out]
        return step_dict

class WorkflowStepInputMixin:

    def get_shortened_source_ids(self): # Might need to rename this if it needs to do more.
        if isinstance(self.source, str):
            source_shortname = get_shortened_id(self.source)
        elif isinstance(self.source, list):
            source_shortname = [get_shortened_id(source) for source in self.source]
        else:
            raise NotImplementedError(f"Deal with WorflowStepInput.source of {self.source}")
        return source_shortname


    def get_workflow_step_inputs(self):
        step_input_dict = CommentedMap()
        input_id = get_shortened_id(self.id)
        step_input_attrs = list(self.attrs)
        step_input_attrs.remove('id')  # Handled explicitly
        step_input_attrs.remove('source')  # Handled explicitly
        step_input_dict[input_id] = CommentedMap()
        step_input_dict[input_id]['source'] = self.get_shortened_source_ids()
        step_input_dict[input_id].update({step_input_attr: getattr(self, step_input_attr) for step_input_attr in step_input_attrs if getattr(self, step_input_attr)})
        return step_input_dict


import tempfile
from pathlib import Path
from urllib.parse import urlparse
from copy import deepcopy
from ruamel.yaml import YAML
from schema_salad.ref_resolver import file_uri, Loader
from schema_salad.jsonld_context import salad_to_jsonld_context
from schema_salad.schema import get_metaschema, validate_doc, collect_namespaces, make_avro, make_avro_schema_from_avro
from xd_cwl_utils.classes.cwl.command_line_tool import load_document
from xd_cwl_utils.helpers.string_tools import uri_name
from xd_cwl_utils.helpers.dict_tools import get_dict_from_list



class SaladSchemaBase:
    metaschema_base = {'$base': 'https://w3id.org/cwl/salad#',
                       '$graph': [{'doc': '# Schema\n', 'name': 'Schema', 'type': 'documentation'},
                                  {'doc': ['Salad data types are based on Avro schema declarations.  '
                                           'Refer to the\n'
                                           '[Avro schema declaration '
                                           'documentation](https://avro.apache.org/docs/current/spec.html#schemas) '
                                           'for\n'
                                           'detailed information.\n',
                                           'null: no value',
                                           'boolean: a binary value',
                                           'int: 32-bit signed integer',
                                           'long: 64-bit signed integer',
                                           'float: single precision (32-bit) IEEE 754 floating-point '
                                           'number',
                                           'double: double precision (64-bit) IEEE 754 '
                                           'floating-point number',
                                           'string: Unicode character sequence'],
                                   'name': 'PrimitiveType',
                                   'symbols': ['sld:null',
                                               'xsd:boolean',
                                               'xsd:int',
                                               'xsd:long',
                                               'xsd:float',
                                               'xsd:double',
                                               'xsd:string'],
                                   'type': 'enum'},
                                  {'doc': 'The **Any** type validates for any non-null value.\n',
                                   'docAfter': '#PrimitiveType',
                                   'name': 'Any',
                                   'symbols': ['#Any'],
                                   'type': 'enum'},
                                  {'doc': 'A field of a record.',
                                   'fields': [{'doc': 'The name of the field\n',
                                               'jsonldPredicate': '@id',
                                               'name': 'name',
                                               'type': 'string'},
                                              {'doc': 'A documentation string for this field\n',
                                               'jsonldPredicate': 'rdfs:comment',
                                               'name': 'doc',
                                               'type': 'string?'},
                                              {'doc': 'The field type\n',
                                               'jsonldPredicate': {'_id': 'sld:type',
                                                                   '_type': '@vocab',
                                                                   'refScope': 2,
                                                                   'typeDSL': True},
                                               'name': 'type',
                                               'type': ['PrimitiveType',
                                                        'RecordSchema',
                                                        'EnumSchema',
                                                        'ArraySchema',
                                                        'string',
                                                        {'items': ['PrimitiveType',
                                                                   'RecordSchema',
                                                                   'EnumSchema',
                                                                   'ArraySchema',
                                                                   'string'],
                                                         'type': 'array'}]}],
                                   'name': 'RecordField',
                                   'type': 'record'},
                                  {'fields': {'fields': {'doc': 'Defines the fields of the record.',
                                                         'jsonldPredicate': {'_id': 'sld:fields',
                                                                             'mapPredicate': 'type',
                                                                             'mapSubject': 'name'},
                                                         'type': 'RecordField[]?'},
                                              'type': {'doc': 'Must be `record`',
                                                       'jsonldPredicate': {'_id': 'sld:type',
                                                                           '_type': '@vocab',
                                                                           'refScope': 2,
                                                                           'typeDSL': True},
                                                       'type': {'name': 'Record_symbol',
                                                                'symbols': ['sld:record'],
                                                                'type': 'enum'}}},
                                   'name': 'RecordSchema',
                                   'type': 'record'},
                                  {'doc': 'Define an enumerated type.\n',
                                   'fields': {'symbols': {'doc': 'Defines the set of valid symbols.',
                                                          'jsonldPredicate': {'_id': 'sld:symbols',
                                                                              '_type': '@id',
                                                                              'identity': True},
                                                          'type': 'string[]'},
                                              'type': {'doc': 'Must be `enum`',
                                                       'jsonldPredicate': {'_id': 'sld:type',
                                                                           '_type': '@vocab',
                                                                           'refScope': 2,
                                                                           'typeDSL': True},
                                                       'type': {'name': 'Enum_symbol',
                                                                'symbols': ['sld:enum'],
                                                                'type': 'enum'}}},
                                   'name': 'EnumSchema',
                                   'type': 'record'},
                                  {'fields': {'items': {'doc': 'Defines the type of the array '
                                                               'elements.',
                                                        'jsonldPredicate': {'_id': 'sld:items',
                                                                            '_type': '@vocab',
                                                                            'refScope': 2},
                                                        'type': ['PrimitiveType',
                                                                 'RecordSchema',
                                                                 'EnumSchema',
                                                                 'ArraySchema',
                                                                 'string',
                                                                 {'items': ['PrimitiveType',
                                                                            'RecordSchema',
                                                                            'EnumSchema',
                                                                            'ArraySchema',
                                                                            'string'],
                                                                  'type': 'array'}]},
                                              'type': {'doc': 'Must be `array`',
                                                       'jsonldPredicate': {'_id': 'sld:type',
                                                                           '_type': '@vocab',
                                                                           'refScope': 2,
                                                                           'typeDSL': True},
                                                       'type': {'name': 'Array_symbol',
                                                                'symbols': ['sld:array'],
                                                                'type': 'enum'}}},
                                   'name': 'ArraySchema',
                                   'type': 'record'}],
                       '$namespaces': {'dct': 'http://purl.org/dc/terms/',
                                       'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                                       'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                                       'sld': 'https://w3id.org/cwl/salad#',
                                       'xsd': 'http://www.w3.org/2001/XMLSchema#'}}
    def __init__(self):
        pass



class InputsSchema:
    template_dict = {'$base': 'https://w3id.org/cwl/cwl#',
                     '$namespaces': {'cwl': 'https://w3id.org/cwl/cwl#',
                                     'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                                     'sld': 'https://w3id.org/cwl/salad#'},
                     '$graph': [ {'$import': 'null'},  # Replace with path to metaschema-base temp file.
                                {'extends': 'sld:PrimitiveType',
                                 'name': 'CWLType',
                                 'symbols': ['cwl:File', 'cwl:Directory'],
                                 'type': 'enum'},
                                {'doc': None,
                                 'docParent': '#CWLType',
                                 'fields': [{'jsonldPredicate': {'_id': '@type', '_type': '@vocab'},
                                             'name': 'class',
                                             'type': {'name': 'File_class',
                                                      'symbols': ['cwl:File'],
                                                      'type': 'enum'}},
                                            {'jsonldPredicate': {'_id': '@id', '_type': '@id'},
                                             'name': 'location',
                                             'type': 'string?'},
                                            {'jsonldPredicate': {'_id': 'cwl:path', '_type': '@id'},
                                             'name': 'path',
                                             'type': 'string?'},
                                            {'jsonldPredicate': 'cwl:basename',
                                             'name': 'basename',
                                             'type': 'string?'},
                                            {'name': 'dirname', 'type': 'string?'},
                                            {'name': 'nameroot', 'type': 'string?'},
                                            {'name': 'nameext', 'type': 'string?'},
                                            {'name': 'checksum', 'type': 'string?'},
                                            {'name': 'size', 'type': 'long?'},
                                            {'jsonldPredicate': 'cwl:secondaryFiles',
                                             'name': 'secondaryFiles',
                                             'type': ['null',
                                                      {'items': ['File', 'Directory'],
                                                       'type': 'array'}]},
                                            {'jsonldPredicate': {'_id': 'cwl:format',
                                                                 '_type': '@id',
                                                                 'identity': True},
                                             'name': 'format',
                                             'type': 'string?'},
                                            {'name': 'contents', 'type': 'string?'}],
                                 'name': 'File',
                                 'type': 'record'},
                                {'fields': [{'jsonldPredicate': {'_id': '@type', '_type': '@vocab'},
                                             'name': 'class',
                                             'type': {'name': 'Directory_class',
                                                      'symbols': ['cwl:Directory'],
                                                      'type': 'enum'}},
                                            {'jsonldPredicate': {'_id': '@id', '_type': '@id'},
                                             'name': 'location',
                                             'type': 'string?'},
                                            {'jsonldPredicate': {'_id': 'cwl:path', '_type': '@id'},
                                             'name': 'path',
                                             'type': 'string?'},
                                            {'jsonldPredicate': 'cwl:basename',
                                             'name': 'basename',
                                             'type': 'string?'},
                                            {'jsonldPredicate': {'_id': 'cwl:listing'},
                                             'name': 'listing',
                                             'type': ['null',
                                                      {'items': ['File', 'Directory'],
                                                       'type': 'array'}]}],
                                 'name': 'Directory',
                                 'type': 'record'},
                                {'documentRoot': True,
                                 'fields': None,
                                 'name': 'InputsField',
                                 'type': 'record'}],
                    }

    def __init__(self, cwl_path):
        if not isinstance(cwl_path, Path):
            cwl_path = Path(cwl_path)
        self.cwl_path = cwl_path
        cwl_document = load_document(str(self.cwl_path))
        self._cwl_inputs = cwl_document.inputs
        self._cwl_schema_def_requirement = cwl_document._get_schema_def_requirement()

    @property
    def cwl_inputs(self):
        return self._cwl_inputs

    @property
    def cwl_schema_def_requirement(self):
        return self._cwl_schema_def_requirement

    def validate_inputs(self, document_path):
        metaschema_path = self._make_metaschema_base_file()
        inputs_schema_path = self._make_temp_schema_file(metaschema_path)
        self._schema_salad_validate(inputs_schema_path, document_path)
        return

    def _make_schema_dict(self):
        inputs_fields = {}
        for input in self.cwl_inputs:
            inputs_fields[uri_name(input.id)] = {'type': input._handle_input_type_field(input.type, self.cwl_schema_def_requirement)}

        schema_dict = deepcopy(InputsSchema.template_dict)
        _, inputs_field_index = get_dict_from_list(schema_dict['$graph'], 'name', 'InputsField')
        schema_dict['$graph'][inputs_field_index]['fields'] = inputs_fields
        return  schema_dict

    def _make_metaschema_base_file(self):
        yaml = YAML(pure=True)
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        metaschema_file = tempfile.NamedTemporaryFile(delete=False, prefix='metaschema_base', suffix='.yml')
        with metaschema_file as tempf:
            yaml.dump(SaladSchemaBase.metaschema_base, tempf)
        return metaschema_file.name


    def _make_temp_schema_file(self, metaschema_path):
        schema_dict = self._make_schema_dict()
        import_dict, import_index = get_dict_from_list(schema_dict['$graph'], '$import', 'null')
        schema_dict['$graph'][import_index] = {'$import': metaschema_path}
        yaml = YAML(pure=True)
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        schema_file = tempfile.NamedTemporaryFile(delete=False, prefix='inputs_schema', suffix='.yml')
        with schema_file as tempf:
            yaml.dump(schema_dict, tempf)
        return schema_file.name

    def _schema_salad_validate(self, schema_path, document_path):
        '''
        Adapted from schema_salad main().
        :param schema_path:
        :param document_path:
        :return:
        '''

        strict_foreign_properties = False
        strict = True
        metaschema_names, metaschema_doc, metaschema_loader = get_metaschema()
        schema_uri = str(schema_path)
        if not (urlparse(schema_uri)[0] and urlparse(schema_uri)[0] in ['http', 'https', 'file']):
            schema_uri = file_uri(schema_uri)
        schema_raw_doc = metaschema_loader.fetch(schema_uri)

        schema_doc, schema_metadata = metaschema_loader.resolve_all(schema_raw_doc, schema_uri)

        # Validate schema against metaschema
        validate_doc(metaschema_names, schema_doc, metaschema_loader, True)

        # Get the json-ld context and RDFS representation from the schema
        metactx = collect_namespaces(schema_metadata)
        if "$base" in schema_metadata:
            metactx["@base"] = schema_metadata["$base"]

        (schema_ctx, rdfs) = salad_to_jsonld_context(
            schema_doc, metactx)

        # Create the loader that will be used to load the target document.
        document_loader = Loader(schema_ctx, skip_schemas=False)

        # Make the Avro validation that will be used to validate the target
        # document

        avsc_obj = make_avro(schema_doc, document_loader)

        avsc_names = make_avro_schema_from_avro(avsc_obj)

        # Load target document and resolve refs
        uri = str(document_path)
        document, doc_metadata = document_loader.resolve_ref(uri, strict_foreign_properties=strict_foreign_properties,
                                                             checklinks=False)  # This is what's getting us around file link checking.

        validate_doc(avsc_names, document, document_loader, strict=strict,
                                              strict_foreign_properties=strict_foreign_properties)

        return

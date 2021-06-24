cwlVersion: v1.0
class: CommandLineTool
baseCommand: test_command_line_tool
stdout: $(inputs.outputName)
label: |
  Some label info
doc: >
  Some clt doc info

# Things to include CommandInputRecordSchema, CommandInputEnumSchema, CommandInputArraySchema, SchemaDefRequirement, secondaryFiles, params with and without defaults, stdin,

inputs:

  string_input:
    type: string
    inputBinding:
      position: 1
      prefix: -A
    doc: |
      string_input doc


  string_input_optional:
    type: ["null", string]
    inputBinding:
      position: 1
      prefix: -b
    doc: |
      -b, --number-nonblank
              number nonempty output lines, overrides -n

  string_input_default:
    type: string
    inputBinding:
      position: 6
      prefix: -e
    default: string_default

    doc: -e     equivalent to -vE

  file_input:
    type: File
    inputBinding:
      position: 1
    doc: |
      A file input.

  file_input_optional:
    type: ["null", File]
    inputBinding:
      position: 1
    doc: |
      optional file input


  file_input_default:
    type: File
    inputBinding:
      position: 1
      prefix: -s
    default:
      class: File
      path: ./
    doc: |
      -s, --squeeze-blank
              suppress repeated empty output lines


  string_array:
    type:
      type: array
      items: string
    inputBinding:
      position: 1
    doc: |
       -t     equivalent to -vT

  string_array_optional:
    type:
      - "null"
      - type: array
        items: string
    inputBinding:
      position: 1
    doc:
      An example optinal string array.

  string_array_default:
    type:
      type: array
      items: string
    inputBinding:
      position: 3
    default: Not a list but should be.
    doc:
      a required string array with a default value.

  string_array_with_list_default:
    type:
      type: array
      items: string
    inputBinding:
      position: 3
    default:
    - list item 1
    - list item 2
    doc:
      a required string array with a default value.


  optional_boolean:
    type: ["null", boolean]
    inputBinding:
      position: 1
      prefix: -T
    doc: |
      some optional boolean

  output_name:
    type: string
    default: some_name

outputs:
  file_output:
    type: File
    outputBinding:
      glob: '*'
    doc:
      Some output file
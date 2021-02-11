Tools actively under development. Documentation will be updated when ready for outside use!

## Create the parser using the latest and greatest CWL and schema-salad versions
```
schema-salad-tool --codegen python https://github.com/common-workflow-language/common-workflow-language/raw/master/v1.0/CommonWorkflowLanguage.yml > capanno_utils/classes/cwl/common_workflow_language.py
```
or
```
curl https://raw.githubusercontent.com/common-workflow-language/cwl-utils/main/cwl_utils/parser_v1_2.py > capanno_utils/classes/cwl/common_workflow_language.py
```
## Add the 10 mixins by hand
```
perl -p -i -e 'print "from capanno_utils.classes.cwl.common_workflow_language_mixins import CommandLineToolMixin, \\
CommandInputParameterMixin, SchemaDefRequirementMixin, CommandLineBindingMixin, \\
CommandOutputParameterMixin, WorkflowMixin, InputParameterMixin, WorkflowOutputParameterMixin, \\
WorkflowStepMixin, WorkflowStepInputMixin\n" if $. == 1' capanno_utils/classes/cwl/common_workflow_language.py

perl -p -i -e 's/SchemaDefRequirement\(/SchemaDefRequirement(SchemaDefRequirementMixin,/; \
               s/CommandLineBinding\(/CommandLineBinding(CommandLineBindingMixin,/; \
               s/CommandInputParameter\(/CommandInputParameter(CommandInputParameterMixin,/; \
               s/CommandOutputParameter\(/CommandOutputParameter(CommandOutputParameterMixin,/; \
               s/CommandLineTool\(/CommandLineTool(CommandLineToolMixin,/; \
               s/Workflow\(/Workflow(WorkflowMixin,/; \
               s/class InputParameter\(/class InputParameter(InputParameterMixin,/; \
               s/WorkflowOutputParameter\(/WorkflowOutputParameter(WorkflowOutputParameterMixin,/; \
               s/class WorkflowStep\(/class WorkflowStep(WorkflowStepMixin,/; \
               s/class WorkflowStepInput\(/class WorkflowStepInput(WorkflowStepInputMixin,/;' capanno_utils/classes/cwl/common_workflow_language.py
```

## Adding a tool
Usage:
```
capanno-add tool kallisto 0.45.x --biotoolsID kallisto  #This will initialize a directory for kallisto
cwl-tools/
└── kallisto
    └── 0.45.x
        ├── common
        │   └── common-metadata.yaml
        └── kallisto
            ├── instances
            └── kallisto-metadata.yaml
```
If you don't provide a `biotoolsID`, capanno-utils will just make a blank template.
```
capanno-add tool kallisto 0.45.x
cwl-tools/
└── kallisto
    └── 0.45.x
        └── common
            └── common-metadata.yaml
```
 


## Adding a subtool
```
#remote
capanno-add subtool kallisto 0.45.x index -u --init-cwl https://github.com/common-workflow-library/bio-cwl-tools/raw/release/Kallisto/Kallisto-Index.cwl
#local
capanno-add subtool kallisto 0.45.x index -u --init-cwl bio-cwl-tools-submodule/Kallisto/Kallisto-Index.cwl 
cwl-tools/
└── kallisto
    └── 0.45.x
        ├── common
        │   └── common-metadata.yaml
        ├── kallisto
        │   ├── instances
        │   └── kallisto-metadata.yaml
        └── kallisto_index
            ├── instances
            ├── kallisto-index-metadata.yaml
            └── kallisto-index.cwl
```

If ``--init_cwl`` is not provided, no cwl file is initialized and capanno-utils will make a blank template.
Can also initialize all subtool directories when first initialize the tool directory but haven't made a way to specify cwl urls to initialize each one doing it that way yet.
```
capanno-add subtool kallisto 0.45.x index -u
cwl-tools/
└── kallisto
    └── 0.45.x
        ├── common
        │   └── common-metadata.yaml
        └── kallisto_index
            ├── instances
            └── kallisto-index-metadata.yaml
```


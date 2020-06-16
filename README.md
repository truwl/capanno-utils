Tools actively under development. Documentation will be updated when ready for outside use!

## Adding a tool
Usage:
```
xd-cwl-add tool kallisto 0.45.x --biotoolsID kallisto  #This will initialize a directory for kallisto
cwl-tools/
└── kallisto
    └── 0.45.x
        ├── common
        │   └── common-metadata.yaml
        └── kallisto
            ├── instances
            └── kallisto-metadata.yaml
```
If you don't provide a `biotoolsID`, xd-cwl-utils will just make a blank template.
```
xd-cwl-add tool kallisto 0.45.x
cwl-tools/
└── kallisto
    └── 0.45.x
        └── common
            └── common-metadata.yaml
```
 


## Adding a subtool
```
xd-cwl-add subtool kallisto 0.45.x index -u --init_cwl https://github.com/common-workflow-library/bio-cwl-tools/raw/release/Kallisto/Kallisto-Index.cwl
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

If ``--init_cwl`` is not provided, no cwl file is initialized and xd-cwl-utils will make a blank template.
Can also initialize all subtool directories when first initialize the tool directory but haven't made a way to specify cwl urls to initialize each one doing it that way yet.
```
xd-cwl-add subtool kallisto 0.45.x index -u
cwl-tools/
└── kallisto
    └── 0.45.x
        ├── common
        │   └── common-metadata.yaml
        └── kallisto_index
            ├── instances
            └── kallisto-index-metadata.yaml
```
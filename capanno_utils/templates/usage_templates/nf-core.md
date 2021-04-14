to install:
```
curl -s https://get.nextflow.io | bash

pip install nf-core # or conda install nf-core

nf-core create -n mypipeline -d "this is a sample" -a "$USER"

nf-core modules install -t {{tool}}/{{subtool}} nf-core-mypipeline
```

in `main.nf`:
```
#!/usr/bin/env nextflow
include { {{tool |upper }}_{{subtool |upper}} } from './modules/nf-core/software/{{tool}}/{{subtool}}/main'
```
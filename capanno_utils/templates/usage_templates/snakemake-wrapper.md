Usage:
```
rule samtools_index:
    input:
        "{sample}.<<input suffix>>"
    output:
        "{sample}.<<output suffix>>"
    params:
        "" # optional params string
    wrapper:
        "master/bio/{{tool.tool}}/{{tool.subtool}}"
```
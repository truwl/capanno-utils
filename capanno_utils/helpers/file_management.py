from ruamel.yaml import YAML

def dump_dict_to_yaml_file(dict_, outfile):
    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    with open(outfile, 'w') as yaml_file:
        yaml.dump(dict_, yaml_file)
    return
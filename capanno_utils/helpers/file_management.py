import io
import pickle
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.representer import RepresenterError

def dump_yaml(yaml_object, map_object, target):
    try:
        yaml_object.dump(map_object, target)
    except RepresenterError:
        print(f"pickle: {pickle.dumps(map_object)}")
        raise
    return

def dump_dict_to_yaml_output(dict_, output=None):
    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    if output:
        return_output = Path(output)
        with return_output.open('w') as yaml_file:
            dump_yaml(yaml, dict_, yaml_file)
    else:
        text_stream = io.StringIO()
        dump_yaml(yaml, dict_, text_stream)
        return_output = text_stream.getvalue()
    return return_output
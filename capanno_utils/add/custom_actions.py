from argparse import Action
from capanno_utils.repo_config import main_tool_subtool_name


def parse_kv_list(list, delimiter='='):
    kv_dict = {}
    for item in list:
        key, value = item.split(delimiter)
        kv_dict[key] = value

    return kv_dict

class keyvalueparse(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if values == []: # option was specified without arguments.
            setattr(namespace, self.dest, True)
        elif values == None: # option was not specified.
            setattr(namespace, self.dest, False)
        else:
            assert isinstance(values, list)
            if namespace.has_primary and len(namespace.subtool_names) == 0: # There is only a main tool.
                # import pdb; pdb.set_trace()
                if len(values) == 1:
                    values = [f"{main_tool_subtool_name}={values[0]}"]

            parsed_values = parse_kv_list(values)
            setattr(namespace, self.dest, parsed_values)

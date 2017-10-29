from node.config.config_support import get_list_of_sites,get_list_of_devices,get_list_of_variables


time_col = 'ReceptionTime'
sites = get_list_of_sites()
# getting rid of "site". req: node IDs are unique across "site" folders.
devices = []
for site in sites:
    devices.extend(get_list_of_devices(site))


def validate_id(node,var=None):
    if node not in devices:
        return False,'Error: Unknown node'

    if var is not None and var not in get_list_of_variables(node):
        return False,'Error: Unknown variable'
    return True,''

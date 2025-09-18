import logging
from diffsync import Adapter, Diff, DiffSyncFlags
from .models import Manufacturer, DeviceType, InterfaceTemplate, ModuleType, PowerPortTemplate, ConsolePortTemplate, ModuleBayTemplate, VirtualChassis, Device, Interface, IPAddress, Site, DeviceRole

from pprint import pprint


class NetboxDeviceTypeAdapter(Adapter):

    manufacturer = Manufacturer
    device_type = DeviceType
    module_type = ModuleType
    interface_template = InterfaceTemplate
    power_port_template = PowerPortTemplate
    console_port_template = ConsolePortTemplate
    module_bay_template = ModuleBayTemplate
    site = Site
    # TODO https://demo.netbox.dev/static/docs/release-notes/version-4.0/#breaking-changes
    # device_role = DEPRICATED and removed in > 4.0.0 ()
    device_role = DeviceRole

    # TODO https://demo.netbox.dev/static/docs/release-notes/version-4.0/#breaking-changes
    # device_role = DEPRICATED and removed in > 4.0.0 ()
    top_level = ["manufacturer", "site", "device_role"]

    def __init__(self, netbox, type='customer'):
        self.netbox = netbox
        self.type = type
        logging.basicConfig(filename='device-type-sync.log', level=logging.DEBUG)
        self.logger = logging.getLogger()
        super().__init__(self)

    def load(self):
        manufacturers = self.netbox._get('/api/dcim/manufacturers/')
        for man in manufacturers:
            item = self.manufacturer(name=man['name'], display=man['display'], description=man['description'], slug = man['slug'], database_pk = man['id'], device_types = [])
            self.add(item)

        device_types = self.netbox._get('/api/dcim/device-types/')
        for dt in device_types:
            item = self.device_type(
                model = dt['model'],
                slug = dt['slug'],
                manufacturer_name = dt['manufacturer']['name'],
                part_number = dt['part_number'],
                is_full_depth = dt['is_full_depth'],
                airflow = dt['airflow'],
                weight = dt['weight'],
                weight_unit = dt['weight_unit'],
                description = dt['description'],
                comments = dt['comments'],
                database_pk = dt['id']
                
            )
            self.add(item)
            manufacturer_name = dt['manufacturer']['name']
            self.store._data['manufacturer'][manufacturer_name].add_child(item)

        module_types = self.netbox._get('/api/dcim/module-types/')
        for mt in module_types:
            item = self.module_type(
                model = mt['model'],
                manufacturer_name = mt['manufacturer']['name'],
                part_number = mt['part_number'],
                weight = mt['weight'],
                weight_unit = mt['weight_unit'],
                description = mt['description'],
                comments = mt['comments'],
                database_pk = mt['id']
                
            )
            self.add(item)
            manufacturer_name = mt['manufacturer']['name']
            self.store._data['manufacturer'][manufacturer_name].add_child(item)
        
        interface_templates = self.netbox._get('/api/dcim/interface-templates/')
        for it in interface_templates:
            item = self.interface_template(
                device_type = it['device_type']['model'] if it['device_type'] else '',
                module_type = it['module_type']['model'] if it['module_type'] else '',
                name = it['name'],
                interface_type = it['type'],
                enabled = it['enabled'],
                mgmt_only = it['mgmt_only'],
                description = it['description'],
                bridge = it['bridge'],
                poe_mode = it['poe_mode'],
                poe_type = it['poe_type'],
                rf_role = it['rf_role'],
                database_pk = it['id'],
            )
            self.add(item)
            device_type_name = it['device_type']['model'] if it['device_type'] else ''
            if device_type_name:
                self.store._data['device_type'][device_type_name].add_child(item)

        power_port_templates = self.netbox._get('/api/dcim/power-port-templates/')
        for pt in power_port_templates:
            item = self.power_port_template(
                device_type = pt['device_type']['model'] if pt['device_type'] else '',
                module_type = pt['module_type']['model'] if pt['module_type'] else '',
                name = pt['name'],
                type = pt['type']['value'],
                maximum_draw = pt['maximum_draw'],
                allocated_draw = pt['allocated_draw'],
                description = pt['description'],
                database_pk = pt['id'],
            )
            self.add(item)
            device_type_name = pt['device_type']['model'] if pt['device_type'] else ''
            if device_type_name:
                self.store._data['device_type'][device_type_name].add_child(item)

        console_port_templates = self.netbox._get('/api/dcim/console-port-templates/')
        for ct in console_port_templates:
            item = self.console_port_template(
                device_type = ct['device_type']['model'] if ct['device_type'] else '',
                module_type = ct['module_type']['model'] if ct['module_type'] else '',
                name = ct['name'],
                type = ct['type']['value'],
                description = ct['description'],
                database_pk = ct['id'],
            )
            self.add(item)
            device_type_name = ct['device_type']['model'] if ct['device_type'] else ''
            if device_type_name:
                self.store._data['device_type'][device_type_name].add_child(item)

        module_bay_templates = self.netbox._get("/api/dcim/module-bay-templates/")
        for mb in module_bay_templates:
            item = self.module_bay_template(
                device_type = mb['device_type']['model'] if mb['device_type'] else '',
                name = mb['name'],
                label = mb['label'],
                position = mb['position'],
                description = mb['description'],
                database_pk = mb['id'],
            )
            self.add(item)
            device_type_name = mb['device_type']['model'] if mb['device_type'] else ''
            if device_type_name:
                self.store._data['device_type'][device_type_name].add_child(item)

        sites = self.netbox._get("/api/dcim/sites/")
        for site in sites:
            item = self.site(
                name = site['name'],
                slug = site['slug'],
                status = site['status']['value'],
                comments = site['comments'],
                description = site['description'],
                database_pk = site['id'],
            )
            self.add(item)

        device_roles = self.netbox._get("/api/dcim/device-roles/")
        for dr in device_roles:
            item = self.device_role(
                name = dr['name'],
                slug = dr['slug'],
                color = dr['color'],
                vm_role = dr['vm_role'],
                description = dr['description'],
                database_pk = dr['id'],
            )
            self.add(item)

    def sync_complete(self, source: Adapter, diff: Diff, flags: DiffSyncFlags, logger):
        ## TODO add your own logic to update the remote system now.
        # The various parameters passed to this method are for your convenience in implementing more complex logic, and
        # can be ignored if you do not need them.
        #
        # The default DiffSync.sync_complete() method does nothing, but it's always a good habit to call super():
        manufacturers_to_add = []
        manufacturers_to_change = []
        device_type_to_add = []
        device_type_to_change = []
        module_bay_template_to_add = []
        module_bay_template_to_change = []
        module_type_to_add = []
        module_type_to_change = []
        interface_template_to_add = []
        interface_template_to_change = []
        power_port_template_to_add = []
        power_port_template_to_change = []
        console_port_template_to_add = []
        console_port_template_to_change = []

        sites_to_add = []
        sites_to_change = []
        device_roles_to_add = []
        device_roles_to_change = []

        def add_diff(diff):
            if diff.action == 'create':
                if diff.type == 'manufacturer':
                    manufacturers_to_add.append(dict(**diff.keys, **diff.source_attrs))
                elif diff.type == 'device_type':
                    device_type = dict(**diff.keys, **diff.source_attrs)
                    # device_type['manufacturer'] = self.store._data['manufacturer'][device_type['manufacturer_name']].database_pk
                    # del(device_type['manufacturer_name'])
                    
                    
                    # GET api returns a dict:
                    #   "airflow": {
                    #       "value": "passive",
                    #       "label": "Passive"
                    #   } OR
                    #   "airflow": null
                    # But the POST api only accepts:
                    #   "airflow": "passive"
                    #   OR
                    #   "airflow": ""
                    # 
                    device_type['airflow'] = '' if device_type.get('airflow', {}) == None else device_type.get('airflow', {}).get('value', None)
                    # Same as with airflow
                    device_type['weight_unit'] = '' if device_type.get('weight_unit', {}) == None else device_type.get('weight_unit', {}).get('value', None)
                    device_type_to_add.append(device_type)
                elif diff.type == 'module_type':
                    module_type = dict(**diff.keys, **diff.source_attrs)
                    module_type['manufacturer'] = self.store._data['manufacturer'][module_type['manufacturer_name']].database_pk
                    del(module_type['manufacturer_name'])
                    module_type['weight_unit'] = '' if module_type.get('weight_unit', {}) == None else module_type.get('weight_unit', {}).get('value', None)
                    module_type_to_add.append(module_type)
                elif diff.type == 'interface_template':
                    diff_object = dict(**diff.keys, **diff.source_attrs)
                    diff_object['type'] = diff_object['interface_type']['value']
                    del(diff_object['interface_type'])
                    diff_object['bridge'] = None
                    diff_object['poe_mode'] = '' if diff_object.get('poe_mode', {}) == None else diff_object.get('poe_mode', {}).get('value', None)
                    diff_object['poe_type'] = '' if diff_object.get('poe_type', {}) == None else diff_object.get('poe_type', {}).get('value', None)
                    diff_object['rf_role'] = '' if diff_object.get('rf_role', {}) == None else diff_object.get('rf_role', {}).get('value', None)
                    interface_template_to_add.append(diff_object)
                elif diff.type == 'power_port_template':
                    diff_object = dict(**diff.keys, **diff.source_attrs)
                    power_port_template_to_add.append(diff_object)
                elif diff.type == 'console_port_template':
                    diff_object = dict(**diff.keys, **diff.source_attrs)
                    if diff_object['device_type']:
                        diff_object['device_type'] = self.store._data['device_type'][diff_object['device_type']].database_pk
                    else:
                        diff_object['device_type'] = None
                    if diff_object['module_type']:
                        diff_object['module_type'] = self.store._data['module_type'][diff_object['module_type']].database_pk
                    else:
                        diff_object['module_type'] = None
                    console_port_template_to_add.append(diff_object)
                elif diff.type == 'module_bay_template':
                    diff_object = dict(**diff.keys, **diff.source_attrs)
                    if diff_object['device_type']:
                        diff_object['device_type'] = self.store._data['device_type'][diff_object['device_type']].database_pk
                    module_bay_template_to_add.append(diff_object)
                elif diff.type == 'site':
                    diff_object = dict(**diff.keys, **diff.source_attrs)
                    sites_to_add.append(diff_object)
                # TODO https://demo.netbox.dev/static/docs/release-notes/version-4.0/#breaking-changes
                # device_role = DEPRICATED and removed in > 4.0.0
                elif diff.type == 'device_role':
                    diff_object = dict(**diff.keys, **diff.source_attrs)
                    device_roles_to_add.append(diff_object)
            elif diff.action == 'update':
                # Issue reported in https://github.com/networktocode/diffsync/issues/259
                pk = self.store._data[diff.type][diff.name].database_pk
                if diff.type == 'manufacturer':
                    manufacturers_to_change.append(dict(**diff.source_attrs, **{'id': pk}))
                elif diff.type == 'device_type':
                    device_type = dict(**diff.source_attrs, **{'id': pk})
                    device_type['airflow'] = '' if device_type.get('airflow', {}) == None else device_type.get('airflow', {}).get('value', None)
                    # Same as with airflow
                    device_type['weight_unit'] = '' if device_type.get('weight_unit', {}) == None else device_type.get('weight_unit', {}).get('value', None)
                    device_type['manufacturer'] = self.store._data['manufacturer'][device_type['manufacturer_name']].database_pk
                    del(device_type['manufacturer_name'])
                    device_type_to_change.append(device_type)
                elif diff.type == 'module_type':
                    module_type = dict(**diff.source_attrs, **{'id': pk})
                    module_type['weight_unit'] = '' if module_type.get('weight_unit', {}) == None else module_type.get('weight_unit', {}).get('value', None)
                    module_type['manufacturer'] = self.store._data['manufacturer'][module_type['manufacturer_name']].database_pk
                    del(module_type['manufacturer_name'])
                    module_type_to_change.append(module_type)
                elif diff.type == 'interface_template':
                    interface_template = dict(**diff.keys, **diff.source_attrs, **{'id': pk})
                    if interface_template['device_type']:
                        interface_template['device_type'] = self.store._data['device_type'][interface_template['device_type']].database_pk
                    interface_template['module_type'] = None if interface_template['module_type'] == '' else interface_template['module_type']
                    interface_template['bridge'] = None
                    interface_template['poe_mode'] = '' if interface_template.get('poe_mode', {}) == None else interface_template.get('poe_mode', {}).get('value', None)
                    interface_template['poe_type'] = '' if interface_template.get('poe_type', {}) == None else interface_template.get('poe_type', {}).get('value', None)
                    interface_template['rf_role'] = '' if interface_template.get('rf_role', {}) == None else interface_template.get('rf_role', {}).get('value', None)
                    interface_template_to_change.append(interface_template)
                elif diff.type == 'power_port_template':
                    diff_object = dict(**diff.keys, **diff.source_attrs, **{'id': pk})
                    if diff_object['device_type']:
                        diff_object['device_type'] = self.store._data['device_type'][diff_object['device_type']].database_pk
                    else:
                        diff_object['device_type'] = None
                    if diff_object['module_type']:
                        diff_object['module_type'] = self.store._data['module_type'][diff_object['module_type']].database_pk
                    else:
                        diff_object['module_type'] = None
                    power_port_template_to_change.append(diff_object)
                elif diff.type == 'console_port_template':
                    diff_object = dict(**diff.keys, **diff.source_attrs, **{'id': pk})
                    if diff_object['device_type']:
                        diff_object['device_type'] = self.store._data['device_type'][diff_object['device_type']].database_pk
                    else:
                        diff_object['device_type'] = None
                    if diff_object['module_type']:
                        diff_object['module_type'] = self.store._data['module_type'][diff_object['module_type']].database_pk
                    else:
                        diff_object['module_type'] = None
                    console_port_template_to_change.append(diff_object)
                elif diff.type == 'module_bay_template':
                    diff_object = dict(**diff.keys, **diff.source_attrs, **{'id': pk})
                    if diff_object['device_type']:
                        diff_object['device_type'] = self.store._data['device_type'][diff_object['device_type']].database_pk
                    module_bay_template_to_change.append(diff_object)
                elif diff.type == 'site':
                    diff_object = dict(**diff.keys, **diff.source_attrs, **{'id': pk})
                    sites_to_change.append(diff_object)
                # TODO https://demo.netbox.dev/static/docs/release-notes/version-4.0/#breaking-changes
                # device_role = DEPRICATED and removed in > 4.0.0
                elif diff.type == 'device_role':
                    diff_object = dict(**diff.keys, **diff.source_attrs, **{'id': pk})
                    device_roles_to_change.append(diff_object)


        for diff1 in diff.get_children():
            add_diff(diff1)
            for child in diff1.child_diff.get_children():
                add_diff(child)
                for child2 in child.child_diff.get_children():
                    add_diff(child2)
            

        manufacturers = self.netbox._post("/api/dcim/manufacturers/", manufacturers_to_add)
        self.netbox._patch("/api/dcim/manufacturers/", manufacturers_to_change)

        for manufacturer in manufacturers:
            self.store._data['manufacturer'][manufacturer['name']].database_pk=manufacturer['id']

        for device_type in device_type_to_add:
            device_type['manufacturer'] = self.store._data['manufacturer'][device_type['manufacturer_name']].database_pk
            del device_type['manufacturer_name']

        for module_type in module_type_to_add:
            module_type['manufacturer'] = self.store._data['manufacturer'][module_type['manufacturer_name']].database_pk
            del module_type['manufacturer_name']

        device_types = self.netbox._post("/api/dcim/device-types/", device_type_to_add)
        self.netbox._patch("/api/dcim/device-types/", device_type_to_change)

        module_types = self.netbox._post("/api/dcim/module-types/", module_type_to_add)
        self.netbox._patch("/api/dcim/module-types/", module_type_to_change)

        for device_type in device_types:
            self.store._data['device_type'][device_type['model']].database_pk=device_type['id']

        for module_type in module_types:
            self.store._data['module_type'][module_type['model']].database_pk=module_type['id']

        for template in interface_template_to_add:
            if template['device_type']:
                if not isinstance(template['device_type'], int):
                    template['device_type'] = self.store._data['device_type'][template['device_type']].database_pk
            else:
                template['device_type'] = None
            if template['module_type']:
                if not isinstance(template['module_type'], int):
                    template['module_type'] = self.store._data['module_type'][template['module_type']].database_pk
            else:
                template['module_type'] = None

        self.netbox._post("/api/dcim/interface-templates/", interface_template_to_add)
        self.netbox._patch("/api/dcim/interface-templates/", interface_template_to_change)

        for template in power_port_template_to_add:
            if template['device_type']:
                if not isinstance(template['device_type'], int):
                    template['device_type'] = self.store._data['device_type'][template['device_type']].database_pk
            else:
                template['device_type'] = None
            if template['module_type']:
                if not isinstance(template['module_type'], int):
                    template['module_type'] = self.store._data['module_type'][template['module_type']].database_pk
            else:
                template['module_type'] = None

        self.netbox._post("/api/dcim/power-port-templates/", power_port_template_to_add)
        self.netbox._patch("/api/dcim/power-port-templates/", power_port_template_to_change)

        for template in console_port_template_to_add:
            if template['device_type']:
                if not isinstance(template['device_type'], int):
                    template['device_type'] = self.store._data['device_type'][template['device_type']].database_pk
            else:
                template['device_type'] = None
            if template['module_type']:
                if not isinstance(template['module_type'], int):
                    template['module_type'] = self.store._data['module_type'][template['module_type']].database_pk
            else:
                template['module_type'] = None

        self.netbox._post("/api/dcim/console-port-templates/", console_port_template_to_add)
        self.netbox._patch("/api/dcim/console-port-templates/", console_port_template_to_change)

        self.netbox._post("/api/dcim/module-bay-templates/", module_bay_template_to_add)
        self.netbox._patch("/api/dcim/module-bay-templates/", module_bay_template_to_change)

        self.netbox._post("/api/dcim/sites/", sites_to_add)
        self.netbox._patch("/api/dcim/sites/", sites_to_change)

        self.netbox._post("/api/dcim/device-roles/", device_roles_to_add)
        self.netbox._patch("/api/dcim/device-roles/", device_roles_to_change)

        super().sync_complete(source, diff, flags, logger)



class NetboxDeviceAdapter(Adapter):

    device = Device
    virtual_chassis = VirtualChassis
    interface = Interface
    ip = IPAddress
    
    top_level = ["virtual_chassis","device", "ip"]

    def __init__(self, netbox):
        self.netbox = netbox
        logging.basicConfig(filename='device-sync.log', level=logging.DEBUG)
        self.logger = logging.getLogger()
        super().__init__(self)

    def load(self):
        # Add virtual chassis to compare db
        virtual_chassis = self.netbox.get_all_virtual_chassis()
        for vc in virtual_chassis:
            item = self.virtual_chassis(
                name=vc.get('name').lower(),
                domain = vc.get('domain', ''),
                description=vc.get('description', ''),
                database_pk=vc['id'],
            )
            member_devices = vc.get('members', [])
            self.add(item)

        # Add devices to compare db
        devices = self.netbox.get_all_devices()
        for device in devices:
            try:
                item = self.device(
                    hostname=device['name'].lower(), 
                    serial=device['serial'],
                    mgmt_ip=device.get('primary_ip', {}).get('address', '') if device.get('primary_ip', {}) else '',
                    device_type=device['device_type']['model'], 
                    status = device['status']['value'],
                    virtual_chassis = device.get('virtual_chassis', {}).get('name') if device.get('virtual_chassis') else None,
                    vc_position = device.get('vc_position'),
                    database_pk = device['id'],
                )
                self.add(item)
            except Exception as e:
                print(f"could not add: {device['name']} -> {e}")
                pass

        # Add interfaces to compare db
        self.interfaces = {}
        interfaces = self.netbox.get_all_interfaces()
        for interface in interfaces:
            interface_item = self.interface(
                hostname=interface.get('device', {}).get('name').lower(),
                interface=interface.get('name'),
                database_pk=interface.get('id'),
            )
            self.add(interface_item)
            parent_device_id = interface.get('device', {}).get('name').lower()
            self.store._data['device'][parent_device_id].add_child(interface_item)

        # Add ips to compare db
        ips = self.netbox.get_all_ips()
        for ip in ips:
            if ip.get('assigned_object_type', '') == 'dcim.interface':
                assigned_object_device_name = ip.get('assigned_object', {}).get('device', {}).get('name', '').lower()
                assigned_object_name = ip.get('assigned_object', {}).get('name', '')

                parent_interface_id = f'{assigned_object_device_name}__{assigned_object_name}'
            else:
                parent_interface_id = None
            ip_item = self.ip(
                ip = ip.get('address').split('/')[0],
                subnet= ip.get('address').split('/')[1],
                database_pk=ip.get('id'),
                #TODO Add logic to find parent
                parent=parent_interface_id,
            )
            self.add(ip_item)

    def sync_complete(self, source: Adapter, diff: Diff, flags: DiffSyncFlags, logger):
        devices_to_add = []
        devices_to_change = []

        vcs_to_add = []
        unique_vcs = set()


        interfaces_to_add = []
        interfaces_to_change = []

        ips_to_add = []
        ips_to_change = []

        def procces_layer(diff):
            for diff1 in diff.get_children():
                if diff1.action == 'create':
                    if diff1.type == 'device':
                        item = dict(**diff1.keys, **diff1.source_attrs)
                        item['device_type'] = {'model': item['device_type']}
                        item['name'] = item['hostname']
                        item['site'] = {'name':'Unknown'}
                        item['role'] = {'name':'Unknown'}
                        unique_vcs.add(item['virtual_chassis'])
                        devices_to_add.append(item)
                    elif diff1.type == 'virtual_chassis':
                        item = dict(**diff1.keys, **diff1.source_attrs)
                        vcs_to_add.append(item)
                    elif diff1.type == 'interface':
                        item = dict(**diff1.keys, **diff1.source_attrs)
                        item['name'] = item['interface']
                        item['type'] = 'virtual'
                        interfaces_to_add.append(item)
                    elif diff1.type == 'ip':
                        item = dict(**diff1.keys, **diff1.source_attrs)
                        item['address'] = item['ip'] +"/"+ item['subnet']
                        item['status'] = 'active'
                        ips_to_add.append(item)
                elif diff1.action == 'update':
                    # Issue reported in https://github.com/networktocode/diffsync/issues/259
                    pk = self.store._data[diff1.type][diff1.name].database_pk
                    item = dict(**diff1.keys, **diff1.source_attrs, **{'id': pk})
                    if diff1.type == 'device':
                        mgmt_ip = item.pop('mgmt_ip', None)
                        if mgmt_ip:
                            intf = source.store._data['device'][item['hostname']].mgmt_interface
                            if intf:
                                if not self.interfaces.get(f'{diff1.name}-{intf}'):
                                    new_interface = {
                                        'device': self.store._data[diff1.type][diff1.name].database_pk,
                                        'name': intf,
                                        'type': 'other',
                                    }
                                    interfaces_to_add.append(new_interface)
                                    results = self.netbox._post("/api/dcim/interfaces/", new_interface)
                                    self.logger.debug(results)
                                else:
                                    results = self.interfaces.get(f'{diff1.name}-{intf}')
                                if not self.ips.get(f'{diff1.name}-{mgmt_ip}'):
                                    new_ip = {
                                        'address': mgmt_ip,
                                        'status': 'active',
                                        "assigned_object_type": "dcim.interface",
                                        "assigned_object_id": results['id'],
                                    }

                                    ips_to_add.append(new_ip)
                                    results = self.netbox._post("/api/ipam/ip-addresses/", new_ip)
                                    self.logger.debug(results)
                                else:
                                    results = self.ips.get(f'{diff1.name}-{mgmt_ip}')
                                item['primary_ip4'] = results['id']
                                self.logger.debug(f"Creating interface: {item['hostname']}: {intf} > {mgmt_ip}")
                        item['device_type'] = {'model': item['device_type']}
                        item['name'] = item['hostname']
                        devices_to_change.append(item)
                    elif diff1.type == 'interface':
                        pass
                    elif diff1.type == 'ip':
                        # interface_name = source.store._data['ip'][item['ip']+"__"+item['subnet']].parent
                        item['parent'] = source.store._data['ip'][item['ip']+"__"+item['subnet']].parent
                        # interface = source.store._data['interface'][interface_name]
                        item['assigned_object_type'] = "dcim.interface"
                        # item['assigned_object_id'] = interface.database_pk
                        ips_to_change.append(item)
                procces_layer(diff1) # Recursive function to process all diff children
        procces_layer(diff)

        # Adding Virtual Chassis
        self.logger.debug(f"Adding virtual chassis's: {vcs_to_add}")
        if len(vcs_to_add) > 0:
            added_vcs = self.netbox._post("/api/dcim/virtual-chassis/", vcs_to_add)
            for vc in added_vcs:
                self.store._data['virtual_chassis'][vc['name']].database_pk=vc['id']

        # Adding devices 
        self.logger.debug("Adding devices")
        for device in devices_to_add:
            if device.get('virtual_chassis'):
                device['virtual_chassis'] = [y.database_pk for x,y in self.store._data['virtual_chassis'].items() if x == device['virtual_chassis']][0]
        from pprint import pprint
        self.logger.debug(devices_to_add)
        if len(devices_to_add) > 0:
            added_devices = self.netbox._post("/api/dcim/devices/", devices_to_add)
            self.logger.debug(f"Response for adding devices: {added_devices}")
            for device in added_devices:
                self.store._data['device'][device['name']].database_pk=device['id']

        # Adding interfaces
        self.logger.debug("Adding interfaces")
        if len(interfaces_to_add) > 0:
            for interface in interfaces_to_add:
                interface['device'] = self.store._data['device'][interface.get('hostname')].database_pk
            added_interfaces = self.netbox._post("/api/dcim/interfaces/", interfaces_to_add)
            self.logger.debug(f"Response for adding interfaces: {added_interfaces}")
            for interface in added_interfaces:
                self.store._data['interface'][interface.get('device', {}).get('name')+"__"+interface['name']].database_pk=interface['id']
        # Updating interfaces
        # self.logger.debug(self.netbox._patch("/api/dcim/interfaces/", interfaces_to_change))

        # Adding ip addresses
        self.logger.debug("Adding ips")
        pprint(ips_to_add)
        if len(ips_to_add) > 0:
            for ip in ips_to_add:
                # if ip.get('parent'):
                ip['assigned_object_type'] = 'dcim.interface'
                ip['assigned_object_id'] = self.store._data['interface'][ip['parent']].database_pk
            pprint(ips_to_add)
            added_ips = self.netbox._post("/api/ipam/ip-addresses/", ips_to_add)
            self.logger.debug(f"Response for adding ips: {added_ips}")
            for ip in added_ips:
                self.store._data['ip'][ip['address'].split('/')[0] + "__" + ip['address'].split('/')[1]].database_pk=ip['id']
        # Updating ip addresses
        for ip in ips_to_change:
            ip['assigned_object_id'] = self.store._data['interface'][ip['parent']].database_pk
        self.logger.debug(self.netbox._patch("/api/ipam/ip-addresses/", ips_to_change))
        
        self.logger.debug(self.netbox._patch("/api/dcim/devices/", devices_to_change))

        

class LibreNMSDeviceAdapter(Adapter):

    device = Device
    virtual_chassis = VirtualChassis
    interface = Interface
    ip = IPAddress
    
    top_level = ["virtual_chassis","device", "ip"]

    def __init__(self, librenms):
        self.librenms = librenms
        super().__init__(self)

    def load(self):
        devices = self.librenms.get_all_devices()
        devices_by_id = {}
        raw_ports = self.librenms.get_all_ports()
        ports = {}
        for port in raw_ports:
            ports[port['port_id']] = port
        raw_ips = self.librenms.get_all_ips()
        ips = {}
        for ip in raw_ips:
            try:
                # combines info of ip and port in dict
                # {'ip':{portinfo+ipinfo}}
                ips[ip['ipv4_address']] = ip | ports[ip['port_id']]
            except:
                # IP is probably ipv6
                pass
        
        for device in devices:
            devices_by_id[device['device_id']] = device
            extended_info = self.librenms.get_extended_device_info(device['device_id'])
            try:
                if device['os'] != 'ping' and device['hardware']:
                    try:
                        ip_info = ips[device['ip']]
                        if ip_info.get('ipv4_prefixlen') == 0:
                            ip_info['ipv4_prefixlen'] = 32
                    except:
                        ip_info = {}
                        
                    interface_name = ip_info.get('ifName', 'unknown') # interface name
                    
                    # try:
                    #     ip = device['ip']+ '/' +str(ips[device['ip']]['ipv4_prefixlen'])
                    # except:
                    #     ip = device['ip']+'/32'

                    if len(extended_info.get('stacks', [])) > 1:
                        # Device is a stack of multiple members
                        for stack_id, stack_member in enumerate(extended_info.get('stacks', [])):
                            # Prevents unknown devicetypes being created
                            if stack_member['entPhysicalDescr'] not in self.librenms.device_mapping_to_netbox.keys():
                                print(f"Not adding {device['sysName'].lower()}-member-{stack_id}. Devicetype not known: {stack_member['entPhysicalDescr']}")
                                continue
                            item = self.device(
                                hostname=f"{device['sysName'].lower()}-member-{stack_id}", 
                                serial=stack_member['entPhysicalSerialNum'] if stack_member['entPhysicalSerialNum'] != None else '', 
                                device_type=self.librenms.device_mapping_to_netbox[stack_member['entPhysicalDescr']] if stack_member['entPhysicalDescr'] in self.librenms.device_mapping_to_netbox.keys() else 'Unknown', 
                                status = 'active' if device['status'] == 1 else 'offline',
                                database_pk = device['device_id'],
                                virtual_chassis = device['sysName'].lower(),
                                vc_position = stack_id,

                            )
                            self.add(item)
                            if stack_id == 0:
                                interface_item = self.interface(
                                    hostname=f"{device['sysName'].lower()}-member-{stack_id}", 
                                    interface=interface_name,
                                )
                                ip_item = self.ip(
                                    ip = device['ip'],
                                    subnet = str(ip_info.get('ipv4_prefixlen', '32')),
                                    parent = interface_item.hostname+"__"+interface_item.interface,
                                )
                                self.add(interface_item)
                                self.add(ip_item)
                                item.add_child(interface_item)
                        vc = self.virtual_chassis(
                            name=device['sysName'].lower(),
                        )
                        self.add(vc)
                    else:
                        if device['hardware'] not in self.librenms.device_mapping_to_netbox.keys():
                            print(f"Not adding {device['sysName'].lower()}. Devicetype not known: {device['hardware']}")
                            continue
                        interface_item = self.interface(
                            hostname=device['sysName'].lower(),
                            interface=interface_name,
                        )
                        ip_item = self.ip(
                            ip = device['ip'],
                            subnet = str(ip_info.get('ipv4_prefixlen', '32')),
                            parent = interface_item.hostname+"__"+interface_item.interface,
                        )
                        item = self.device(
                            hostname=device['sysName'].lower(), 
                            mgmt_interface = interface_name,
                            serial=device['serial'] if device['serial'] != None else '', 
                            device_type=self.librenms.device_mapping_to_netbox[device['hardware']] if device['hardware'] in self.librenms.device_mapping_to_netbox.keys() else 'Unknown', 
                            status = 'active' if device['status'] == 1 else 'offline',
                            database_pk = device['device_id'],
                        )

                        self.add(interface_item)
                        self.add(ip_item)
                        self.add(item)
                        item.add_child(interface_item)
            except Exception as e:
                print(f"Device: {device} -> {e}")
            
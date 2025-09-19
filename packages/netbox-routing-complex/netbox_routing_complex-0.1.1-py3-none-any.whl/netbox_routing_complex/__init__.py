from netbox.plugins import PluginConfig

class NetBoxRoutingComplexConfig(PluginConfig):
    name = 'netbox_routing_complex'
    verbose_name = ' NetBox Complex Routing'
    description = 'Manage complex routing in Netbox'
    version = '0.1'
    base_url = 'netbox-routing-complex'

config = NetBoxRoutingComplexConfig
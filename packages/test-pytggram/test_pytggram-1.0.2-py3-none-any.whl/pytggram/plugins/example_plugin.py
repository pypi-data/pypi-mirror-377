"""
Example plugin for PyTgGram
"""
from ..client import Client
from ..filters import Command

def setup_plugin(client: Client):
    """Setup function for the plugin"""
    
    @client.command(['example'])
    async def example_command(client, message):
        await message.reply("This is an example plugin command!")
    
    @client.on_message(Command('plugin_info'))
    async def plugin_info(client, message):
        await message.reply(
            "This is an example plugin for PyTgGram.\n"
            "Plugins allow you to extend the framework with custom functionality."
        )
    
    return {
        'name': 'Example Plugin',
        'version': '1.0.0',
        'description': 'An example plugin for PyTgGram'
    }

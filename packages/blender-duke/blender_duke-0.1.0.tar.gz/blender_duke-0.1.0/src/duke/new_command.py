"""
generates a new project using one of the templates
"""

from cleo.commands.command import Command
from . import global_config
import os


class NewCommand(Command):
    name = 'new'
    description = 'generate new blender add-on project using one of the templates'

    def handle(self) -> int:
        duke_config = global_config.get()
        if len(duke_config.blender_instances) == 0:
            self.line_error('you must configure at least one blender instance to use this command, see "add-blender"',
                            style='error')
            return 1

        print(os.getcwd())
        return 0

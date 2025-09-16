from cleo.helpers import argument
from cleo.commands.command import Command
from pathlib import Path
from . import global_config
import plumbum


class AddBlenderCommand(Command):
    name = 'add-blender'
    description = 'Informs duke about a new blender instance'
    arguments = [
        argument(
            'path',
            description='Path to the blender executable'
        )
    ]

    def handle(self) -> int:
        supplied_exe_path = Path(self.argument('path'))
        if not supplied_exe_path.exists() or not str(supplied_exe_path).endswith('blender.exe'):
            self.line_error(f'expected path to blender executable, received {supplied_exe_path} instead', style='error')
            return 1

        # attempt to extract blender and blender python versions using the blender's executable
        try:
            blender_exe = plumbum.local[self.argument('path')]

            commands = [
                'import bpy, sys',
                'print(f"blender_version={bpy.app.version[0]},{bpy.app.version[1]},{bpy.app.version[2]}")',
                'print(f"python_version={sys.version_info.major},{sys.version_info.minor},{sys.version_info.micro}")'
            ]

            stdout = blender_exe(
                '--background',
                '--python-expr',
                ';'.join(commands)
            )

        except Exception as e:
            raise RuntimeError(f'could not retrieve blender info: {e}')

        # parse the values from std-out
        stdout_lines = stdout.splitlines()

        blender_version = (-1, -1, -1)
        blender_python_version = (-1, -1, -1)

        for line in stdout_lines:
            if line.startswith('blender_version'):
                blender_version = line.replace('blender_version=', '')
                blender_version = blender_version.split(',')
                blender_version = tuple([int(v) for v in blender_version])
            elif line.startswith('python_version'):
                blender_python_version = line.replace('python_version=', '')
                blender_python_version = blender_python_version.split(',')
                blender_python_version = tuple([int(v) for v in blender_python_version])

        if blender_version == (-1, -1, -1) or blender_python_version == (-1, -1, -1):
            raise RuntimeError('could not extract blender version and/or blender python version: blender executable returned unexpected results')

        blender_instance = global_config.BlenderInstance(
            id='.'.join([str(v) for v in blender_version]),
            blender_version=blender_version,
            blender_python_version=blender_python_version,
            executable=self.argument('path')
        )

        duke_config = global_config.get()
        if any([existing_blender.id == blender_instance.id for existing_blender in duke_config.blender_instances]):
            self.line_error('this blender version is already configured. if you want to re-add, please remove first and then add again', style='error')
            return 1

        duke_config.blender_instances.append(blender_instance)
        global_config.update(duke_config)

        self.line(f'successfully added a new blender instance with id={blender_instance.id}')
        return 0


class ListBlenderCommand(Command):
    name = 'list-blender'
    description = 'List blender instances duke knows about'

    def handle(self) -> int:
        duke_config = global_config.get()

        if len(duke_config.blender_instances) == 0:
            self.line('no blender instances found')
            return 0

        self.line('found following blender instances:')
        for blender_instance in duke_config.blender_instances:
            self.line(f'{blender_instance.id}: {blender_instance.executable}')
        return 0


class RemoveBlenderCommand(Command):
    name = 'remove-blender'
    description = "Remove existing blender instance from duke's db"
    arguments = [
        argument(
            name='id',
            description='id of the blender instance to remove'
        )
    ]

    def handle(self) -> int:
        duke_config = global_config.get()
        if len(duke_config.blender_instances) == 0:
            self.line_error('cannot remove, there are no blender instances configured', style='error')
            return 1

        if not any([blender_instance.id == self.argument('id') for blender_instance in duke_config.blender_instances]):
            self.line_error(f'cannot remove, no blender instance with id "{self.argument("id")}" found', style='error')
            return 1

        instance_to_remove = [blender_instance for blender_instance in duke_config.blender_instances if blender_instance.id == self.argument('id')][0]
        duke_config.blender_instances.remove(instance_to_remove)

        global_config.update(duke_config)
        self.line(f'successfully removed blender instance with id "{self.argument("id")}"')
        return 0

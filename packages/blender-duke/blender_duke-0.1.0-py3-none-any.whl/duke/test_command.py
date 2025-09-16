from cleo.commands.command import Command
from . import global_config
import plumbum
from importlib.resources import files


class TestCommand(Command):
    name = 'test'
    description = 'Run unit tests with blender (headless)'

    def report_blender_test_result(self, blender_version: str, test_exit_code: int):
        if test_exit_code == 0:
            test_result = 'PASSED'
        elif test_exit_code in (1, 3, 4):
            test_result = 'FAILED'
        elif test_exit_code == 2:
            test_result = 'INTERRUPTED'
        elif test_exit_code == 3:
            test_result = 'FAILED'
        elif test_exit_code == 5:
            test_result = 'NO TESTS'
        else:
            raise ValueError(f'unexpected pytest exit code: {test_exit_code}')

        self.line(f'Blender {blender_version}: {test_result}')

    def handle(self) -> int:
        test_run_stats = dict()  # blender version - test result mapping

        # run tests for all blender instances configured (TODO to be reworked later)
        for blender_instance in global_config.get().blender_instances:
            blender_exe = plumbum.local[blender_instance.executable]
            blender_pytest = blender_exe[
                '--background',
                '--python',
                files('duke.resources') / 'unit_test_utility.py'
            ]

            tests_return_code, _, _ = blender_pytest.run(retcode=None, stdout=None, stderr=None)
            test_run_stats[blender_instance.id] = tests_return_code

        self.line('')
        self.line('')

        self.line('Test run results:')
        for blender_id, test_exit_code in test_run_stats.items():
            self.report_blender_test_result(blender_id, test_exit_code)

        return 0 if all([exit_code == 0 for exit_code in test_run_stats.values()]) else 1


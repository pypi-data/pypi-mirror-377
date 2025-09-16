"""
duke's global config, to be stored under the platformdirs
"""

from dataclasses import dataclass, asdict, field
from pathlib import Path

import platformdirs
import tomli
import dacite
import tomli_w


@dataclass
class BlenderInstance:
    """
    points to blender instance on the hard drive
    """
    id: str
    blender_version: tuple[int, int, int]
    blender_python_version: tuple[int, int, int]
    executable: str


@dataclass
class DukeConfiguration:

    """
    global configuration of duke
    """
    blender_instances: list[BlenderInstance] = field(
        default_factory=list
    )


def _get_create_config_file() -> Path:
    duke_conf_path = platformdirs.user_config_path('duke', 'summerane')
    if not duke_conf_path.exists():
        duke_conf_path.mkdir(parents=True)

    config_file_path = duke_conf_path / 'duke.toml'
    if not config_file_path.exists():
        config_file_path.write_text('', encoding='utf-8')

    return config_file_path


def get() -> DukeConfiguration:
    with open(_get_create_config_file(), 'rb') as config_file:
        raw = tomli.load(config_file)
    return dacite.from_dict(DukeConfiguration, raw, config=dacite.Config(type_hooks={tuple[int, int, int]: tuple}))


def update(new_config: DukeConfiguration):
    conf_dict = asdict(new_config)
    txt = tomli_w.dumps(conf_dict)
    _get_create_config_file().write_text(txt, encoding='utf-8')

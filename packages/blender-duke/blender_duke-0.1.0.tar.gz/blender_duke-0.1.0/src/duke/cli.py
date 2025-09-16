from cleo.application import Application
from .add_blender_command import *
from .new_command import *
from .test_command import *


def main():
    app = Application()
    app.add(AddBlenderCommand())
    app.add(ListBlenderCommand())
    app.add(RemoveBlenderCommand())
    app.add(NewCommand())
    app.add(TestCommand())
    app.run()


if __name__ == '__main__':
    main()

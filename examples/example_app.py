from components import Component
from components.cli import CLI


class LogWriter(Component):
    def __init__(self, path: str = "logs/logfile.txt"):
        self.path = path


class RotationalLogWriter(LogWriter):
    def __init__(self, path: str = "logs/logfile.txt", rotations: int = 5):
        super().__init__(path)
        self.rotations = rotations


class Application(Component):
    def __init__(self, logger: LogWriter, parameter1: int = 42):
        self.parameter1 = parameter1
        self.logger = logger

    def run(self):
        print("paramter1:", self.parameter1)
        print("logger:", type(self.logger))
        print("log path:", self.logger.path)


class CustomApplication(Application):
    logger: RotationalLogWriter
    parameter1 = 8

    def run(self):
        super().run()
        print("log rotations:", self.logger.rotations)


cli = CLI()


class ApplicationAsCommand(Application, cli.Command):
    logger: RotationalLogWriter

    def run(self):
        super().run()
        print("log rotations:", self.logger.rotations)


if __name__ == "__main__":
    app = Application.resolve()
    print("app.run")
    app.run()

    custom_app = CustomApplication.resolve()
    print("\ncustom_app.run")
    custom_app.run()

    print("\ncli.run")
    cli.run()

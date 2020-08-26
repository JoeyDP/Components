from components import Component


class LogWriter(Component):
    def __init__(self, path: str = "logs/logfile.txt"):
        self.path = path


class RotationalLogWriter(LogWriter):
    def __init__(self, path: str = "logs/logfile.txt", rotations: int = 5):
        suoer().__init__(path)
        self.rotations = rotations


class Application(Component):
    def __init__(self, logger: LogWriter, parameter1: int = 42):
        self.parameter1 = parameter1
        self.logger = logger

    def run(self):
        pass


if __name__ == "__main__":
    app = Application.resolve()
    app.run()

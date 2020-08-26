# Components
Python library to facilitate modular components that can be combined through dependency injection.

# Example
Define your components by subclassing from `Component`. Then you can use them in other components through dependency injection as follows:
```python
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
```

Components and parameter can all be supplied to the `resolve` function, including parameters of subcomponents. In this example you can also instantiate `app` as follows:
 - `app = Application.resolve(parameter1=9)`
 - `app = Application.resolve(path="output/logs/stdout.log")`
 - `app = Application.resolve(logger_path="output/logs/stdout.log")`

> Note that parameters of subcomponents can be addressed by their own name (when no conflicts are present) or by their more defined name which includes the subcomponent's name(s) separated with underscores. In some cases, when conflicting paramter names occur, the more defined name is be required.

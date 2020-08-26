# Components
Python library to facilitate modular components that can be combined through dependency injection.

# Example
Define your components by subclassing from `Component`. Then you can use them in other components through dependency injection as follows:
```python
from components import Component


class LogWriter(Component):
    def __init__(self, path: str = "logs/logfile.txt"):
        self.path = path


class Application(Component):
    def __init__(self, logger: LogWriter, parameter1: int = 42):
        self.parameter1 = parameter1
        self.logger = logger

    def run(self):
        print("paramter1:", self.parameter1)
        print("logger:", type(self.logger))
        print("log path:", self.logger.path)


if __name__ == "__main__":
    app = Application.resolve()
    app.run()
```

Components and parameter can all be supplied to the `resolve` function, including parameters of subcomponents. In this example you can also instantiate `app` as follows:
 - `app = Application.resolve(parameter1=9)`
 - `app = Application.resolve(path="output/logs/stdout.log")`
 - `app = Application.resolve(logger_path="output/logs/stdout.log")`

> Note that parameters of subcomponents can be addressed by their own name (when no conflicts are present) or by their more defined name which includes the subcomponent's name(s) separated with underscores. In some cases, when conflicting paramter names occur, the more defined name is be required.


Additionally, paramters can be supplied through class attributes. Consider the following example:
```python
class RotationalLogWriter(LogWriter):
    def __init__(self, path: str = "logs/logfile.txt", rotations: int = 5):
        super().__init__(path)
        self.rotations = rotations


class CustomApplication(Application):
    logger: RotationalLogWriter
    parameter1 = 8

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
```

Which gives the output:
```
app.run
paramter1: 42
logger: <class '__main__.LogWriter'>
log path: logs/logfile.txt

custom_app.run
paramter1: 8
logger: <class '__main__.RotationalLogWriter'>
log path: logs/logfile.txt
log rotations: 5
```

Finally, it is also possible to turn Components into commands for a command line interface (CLI).
```python
from components.cli import CLI
cli = CLI()


class ApplicationAsCommand(Application, cli.Command):
    logger: RotationalLogWriter

    def run(self):
        super().run()
        print("log rotations:", self.logger.rotations)


if __name__ == "__main__":
    print("cli.run")
    cli.run()
```

In the command line, this gives:
```console
> python3 example/example_app.py ApplicationAsCommand --parameter1 80
cli.run
paramter1: 80
logger: <class '__main__.RotationalLogWriter'>
log path: logs/logfile.txt
log rotations: 5

> python3 example/example_app.py ApplicationAsCommand -h
usage: example_app.py ApplicationAsCommand [-h] [--path str] [--rotations int] [--parameter1 int]

optional arguments:
  -h, --help            show this help message and exit
  --path str, --logger-path str
                        (default: logs/logfile.txt)
  --rotations int, --logger-rotations int
                        (default: 5)
  --parameter1 int      (default: 42)

```

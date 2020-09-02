# Components
Python library to facilitate modular components that can be combined through dependency injection.

## Getting Started
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

Finally, it is also possible to turn Components into commands for a command line interface (CLI). Simply create a `cli = components.cli.CLI()` object and have your `Component` extend from `cli.Command`. Then the command will be registered and its `run` function will be called when the command is used from the command line.
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


## Advanced Usage

### Lists of Components

In addition to providing single `Components`, the resolver will also instantiate lists of `Components` when requested with the `Tuple` type hint. This can be useful for supplying a variable amount of `Components` for example, for the `Listener` pattern.

This example illustrates the usage of `Tuple` with `Components`.

```python
from typing import Tuple

class SubComp1(Component):
    def __init__(self, par=42, par1: int=3):
        self.par = par
        self.par1 = par1

class SubComp2(Component):
    def __init__(self, par=9, par2: str="Test"):
        self.par = par
        self.par2 = par2

class Comp(Component):
    def __init__(self, components: Tuple[Component, ...]):
        self.components = components

class ParentComp(Comp):
    components: Tuple[SubComp1, SubComp2]
```

`Comp.resolve()` will result in an empty list for the `components` variable, whereas calling `ParentComp.resolve()` will provide a list with two components of the following types: `[SubComp1, SubComp2]` to be filled into the `components` parameter.

### Non-identifying parameters

The default `__repr__` of `Components` calls the function `identifier` which shows the component name with its parameters between round braces. Additionally there is `name` and `full_identifier` to respectively only return the name or to recursively include subcomponent identifiers.

However, some parameters should not be listed in the `__repr__` of an object. These can be indicated by prefixing them with an underscore (`_`) as if they were private/protected members. The parameter can then be provided using the name without underscore or with underscore.


## Technical Details
WIP
 - Explain semantics of conflicting param names
 - Explain that creating an object without `resolve` does not take attributes into account
 - ...

## Future Work
 - Add `@argument` annotation to indicate class attributes that are arguments for parameters (allows to detect mistyped names for example).
 - Add support for lists in command line.
 - Suggestions? Contact [me](mailto:joeydepauw@gmail.com)!

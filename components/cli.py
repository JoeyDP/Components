from abc import ABC, abstractmethod
import argparse
import inspect

from components import Component


class MyHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """ Custom help formatter for argparse. """

    def _get_help_string(self, action):
        print("action", action)
        print("type", action.type)
        if isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreFalseAction):
            return action.help
        return super()._get_help_string(action)

    def _get_default_metavar_for_optional(self, action):
        if action.type is None:
            return ""
        return action.type.__name__

    def _get_default_metavar_for_positional(self, action):
        if action.type is None:
            return ""
        return action.type.__name__


class CLI:
    def __init__(self, description=""):
        self.commands = dict()
        self.parser = argparse.ArgumentParser(description=description)
        self.subparsers = self.parser.add_subparsers(
            help="Select one of the following subcommands:",
            dest='command',
            metavar="subcommand"
        )
        self.subparsers.required = True

    def __call__(self):
        self.run()

    def run(self):
        if len(self.commands) > 0:
            self.setup()
            cls, kwargs = self.parse_args()
            obj = cls.resolve(**kwargs)
            obj.run()

    @property
    def Command(self):
        class Command(ABC):
            """ Resolves parameters from command line arguments. """

            def __init_subclass__(cls, **kwargs):
                """ Hooks the subclass as a runnable command. """
                super().__init_subclass__()
                if not issubclass(cls, Component):
                    raise TypeError("cli.Command should only be used on Components")
                self.commands[cls.__name__] = cls

            @abstractmethod
            def run(self):
                pass

        return Command

    def setup(self):
        for cls in self.commands.values():
            self.setup_command(cls)

    def setup_command(self, cls):
        sub_parser = self.subparsers.add_parser(
            cls.__name__,
            help=cls.__doc__,
            description=cls.__doc__,
            formatter_class=MyHelpFormatter
        )

        def add_bool_param(name, dest, default):
            """
            Add boolean parameter as two flags (--name/--no-name).
            default indicates default value or None for a required boolean parameter.
            """
            required = default is None
            group = sub_parser.add_mutually_exclusive_group(required=required)
            group.add_argument('--' + name, help="(default)" if default is True else "", dest=dest,
                               action='store_true')
            group.add_argument('--no-' + name, help="(default)" if default is False else "",
                               dest=dest, action='store_false')
            if default is not None:
                group.set_defaults(**{dest: default})

        for param in cls.get_requested_params(flatten=True):
            param_name = param.name[1:] if param.name[0] == "_" else param.minimal_name
            param_name = param_name.replace('_', '-')
            prefix = "-" if len(param_name) == 1 else "--"
            required = param.default is inspect.Parameter.empty

            if param.type == bool:
                add_bool_param(param_name, param.full_name, None if required else param.default)
            else:
                print(param.type)
                sub_parser.add_argument(prefix + param_name, type=param.type, default=param.default,
                                        help=" ",
                                        dest=param.full_name,
                                        required=required)

    def parse_args(self):
        cmd_args = self.parser.parse_args()
        fName = cmd_args.command
        cls = self.commands[fName]

        kwargs = {n: v for n, v in cmd_args._get_kwargs() if n != "command"}

        return cls, kwargs

import inspect
import warnings
from abc import ABC, abstractmethod

from components.param import Param, ComponentParam


class Component(object):
    """
    A component is a part of the system. It can request parameters through its __init__ function.
    Components can also consist of other components.
    """

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.__params = kwargs
        params = iter(inspect.signature(cls.__init__).parameters.values())
        next(params)  # skip self
        for index, param in enumerate(params):
            # skip keyword args that were already provided
            if param.name in obj.__params:
                continue
            # skip *args and **kwargs
            if param.kind == inspect.Parameter.VAR_POSITIONAL or param.kind == inspect.Parameter.VAR_KEYWORD:
                continue

            # fill in positional arguments
            if index < len(args):
                obj.__params[param.name] = args[index]
            # fill in default values
            else:
                obj.__params[param.name] = param.default

        return obj

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name}({', '.join(f'{key}={value}' for key, value in self.get_params().items())})"

    @classmethod
    def get_requested_params(cls):
        return cls._get_requested_params(dict(), [])

    @classmethod
    def _get_requested_params(cls, parent_provided_types, prefixes):
        """
        Returns a list of the requested parameters. Includes their type and default value from __init__ and
        additionally, alternative names are provided.
        """
        # first do a pass to resolve names
        params = cls._resolve_requested_names(prefixes)

        # check consistency
        current_component_param = ComponentParam("__main__", cls, None, params=params)
        current_component_param.enforce_consistency()

        # Then do a pass to resolve types
        params = cls._update_requested_types(params, parent_provided_types, prefixes)
        return params

    @classmethod
    def _resolve_requested_names(cls, prefixes):
        requested = list()
        param_iter = iter(inspect.signature(cls.__init__).parameters.items())
        next(param_iter)  # skip self
        for parname, param in param_iter:
            tpe = param.annotation
            default = param.default

            if tpe == inspect.Parameter.empty:
                if default != inspect.Parameter.empty:
                    tpe = type(default)
                else:
                    tpe = None

            aliases = {param.name}
            for prefix in reversed(prefixes):
                aliases = aliases | {prefix + '_' + alias for alias in aliases}

            if tpe is not None and issubclass(tpe, Component):
                sub_params = tpe._resolve_requested_names([param.name] + prefixes)
                param = ComponentParam(parname, tpe, default, params=sub_params, aliases=aliases)
            else:
                param = Param(parname, tpe, default, aliases)

            requested.append(param)

        return requested

    @classmethod
    def _update_requested_types(cls, params, parent_provided_types, prefixes):
        provided_types = cls.get_provided_types()
        provided_types.update(parent_provided_types)

        for param in params:
            # Change type based on type hint in annotation
            if provided_types.keys() & param.aliases:
                old_type = param.type
                key = param.aliases & provided_types.keys()
                if len(key) > 1:
                    raise TypeError(
                        f"Type for parameter {param.full_name} supplied multiple times: {key}")
                key = list(key)[0]
                param.type = provided_types.pop(key)
                print(f"change type of {param.full_name} to {param.type}")
                print(provided_types)

                # if component type changed, refresh hierarchy
                if old_type is not None and issubclass(old_type, Component) or issubclass(param.type, Component):
                    sub_params = param.type._get_requested_params(provided_types, [param.name] + prefixes)
                    param.params = sub_params
                    # param = ComponentParam(parname, tpe, default, params=sub_params, aliases=aliases)
            elif isinstance(param, ComponentParam):
                param.type._update_requested_types(param.params, provided_types, [param.name] + prefixes)

        return params

    @classmethod
    def get_provided_parameters(cls):
        """ Returns provided parameters as a dict. Type changes should have been taken care of.
        """
        attributes = {name: var for name, var in vars(cls).items() if not name.startswith('__')}
        return attributes

    @classmethod
    def get_provided_types(cls):
        """ Returns provided parameters as a dict.
        """
        if hasattr(cls, '__annotations__'):
            return cls.__annotations__.copy()
        return dict()

    @classmethod
    def resolve(cls, **params):
        """
        Resolves the components and subcomponents recursively.
        Uses `cls.get_provided_parameters` first to set default values, then overrides with strict **params.
        """
        requested_params = cls.get_requested_params()
        object = cls._resolve(params, dict(), requested_params)

        # Check if all params were used
        if len(params) > 0:
            raise TypeError(f"Unexpected parameter(s): {params}")

        return object

    @classmethod
    def _resolve(cls, params, parent_provided_params, requested_params):
        """
        Resolves the components and subcomponents recursively.
        Uses `provided_params` first to set default values, then overrides with params.
        Need to pop from params to check if they were all used.
        """
        # TODO: Add warning for class attributes that were unused? (might indicate name change or typo)
        provided_params = cls.get_provided_parameters()
        provided_params.update(parent_provided_params)
        kwargs = dict()
        for param in requested_params:
            found = False
            value = None
            # first try to find it in the user params
            if param.aliases & params.keys():
                found = True
                key = param.aliases & params.keys()
                if len(key) > 1:
                    raise TypeError(f"Value for parameter {param.full_name} supplied multiple times: {key}")
                key = list(key)[0]
                value = params.pop(key)
            # then try to find it in the attribute provided params
            elif param.aliases & provided_params.keys():
                found = True
                key = param.aliases & provided_params.keys()
                if len(key) > 1:
                    raise TypeError(f"Attribute override for parameter {param.full_name} supplied multiple times: {key}")
                key = list(key)[0]
                value = provided_params.pop(key)
            # finally in the case of a component: see if the type is a component and try to resolve it.
            elif param.type is not None and issubclass(param.type, Component):
                # param is of type ComponentParam
                found = True
                value = param.type._resolve(params, provided_params, param.params)
            elif param.default is not inspect.Parameter.empty:
                # no worries, there is a default
                found = True
                value = param.default

            if found:
                if param.type is not None and not isinstance(value, param.type):
                    warnings.warn(f"Parameter '{param.full_name}' expected type {param.type}, but got {type(value)} instead",
                                  RuntimeWarning)
                kwargs[param.name] = value
            else:
                # no default and no provided parameter: can't instantiate component.
                #  error will be raised when trying to instantiate.
                warnings.warn(f"Missing parameter for resolve: {param.name}", RuntimeWarning)
        return cls(**kwargs)

    def get_params(self):
        """ Returns a dictionary of the parameters and their values that were supplied through __init__. """
        return self.__params


class ComponentResolver(ABC):
    @classmethod
    @abstractmethod
    def get_provided_parameters(cls):
        """ Returns provided parameters as a dict. Type changes should have been taken care of. """
        pass

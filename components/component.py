from abc import ABC, abstractmethod


class Component(object):
    """
    A component is a part of the system. It can request parameters through its __init__ function.
    Components can also consist of other components.
    """
    def __new__(cls, *args, **kwargs):
        print(args)
        print(kwargs)
        obj = super().__new__(cls)
        obj.__params = kwargs
        return obj

    def __init_subclass__(cls, **kwargs):
        # TODO: check if names can all be resolved (for get_requested_params).
        pass

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name}({', '.join(f'{key}={value}' for key, value in self.get_params().items())})"

    @classmethod
    def get_requested_params(cls):
        """ Returns a dictionary of the requested parameters and their type and default value from __init__. """
        # TODO: Implement
        pass

    @classmethod
    def resolve(cls, **params):
        """
        Resolves the components and subcomponents recursively.
        Uses `cls.get_provided_parameters` first to set default values, then overrides with provided **params.
        """
        pass

    def get_params(self):
        """ Returns a dictionary of the parameters and their values that were supplied through __init__. """
        # TODO: Implement
        return dict()


class ComponentResolver(ABC):

    @classmethod
    @abstractmethod
    def get_provided_parameters(cls):
        """ Returns provided parameters as a dict. Type changes should have been taken care of. """
        pass


class AttributeComponentResolver(ComponentResolver):
    """ Default resolver that fetches parameters from class attributes. """

    def __init_subclass__(cls, **kwargs):
        """
            Scans attributes of subclass and matches parameters to components.
            This class is responsible for creating Components with the right parameters based on get_provided_parameters.
        """
        # TODO: implement
        super().__init_subclass__()
        print("AttributeComponentResolver", cls)
        print(cls.get_provided_parameters())

    @classmethod
    def get_provided_parameters(cls):
        print("AttributeComponentResolver.get_provided_parameters")
        return {
            "par1": 1,
            "par2": 2
        }

# TODO: Warning for class attributes that were unused (might indicate name change or typo)

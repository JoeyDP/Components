

class Param(object):
    def __init__(self, name, tpe, default):
        # original name of the parameter
        self.name = name
        self.type = tpe
        self.default = default
        # aliases need to be unique within the component hierarchy
        self.aliases = {name}

    @property
    def minimal_name(self):
        """ Shortest name that still uniquely identifies the parameter. """
        return min(self.aliases, key=len)

    @property
    def full_name(self):
        """ Fully defined name in component hierarchy. """
        return max(self.aliases, key=len)

    def add_prefix(self, prefix, concat_symb='_'):
        """ Add a variant of each alias with the given prefix (and concatenation symbol). """
        self.aliases = self.aliases | {prefix + "_" + alias for alias in self.aliases}

    def _remove_shadowed(self, defined):
        self.aliases -= defined

    def _remove_conflicting(self, name_map):
        for alias in list(self.aliases):
            if alias in name_map:
                # name already defined
                other_param = name_map[alias]
                other_param.aliases.remove(alias)
                self.aliases.remove(alias)
            else:
                name_map[alias] = self

    def check_valid(self):
        """ Check if parameter still has at least one name. """
        if len(self.aliases) == 0:
            raise AttributeError(f"No valid identifier for parameter {self.name}")


class ComponentParam(Param):
    def __init__(self, name, tpe, default, params=None):
        super().__init__(name, tpe, default)
        self.params = params

    def add_prefix(self, prefix, concat_symb='_'):
        super().add_prefix(prefix, concat_symb=concat_symb)
        for param in self.params:
            param.add_prefix(prefix, concat_symb=concat_symb)

    def enforce_consistency(self):
        # 1. remove all shadowed variable names
        self.remove_shadowed()
        # 2. resolve all conflicting names
        self.remove_conflicting()
        # 3. if param without valid identifier, raise error
        self.check_valid()

    def remove_shadowed(self):
        """ Remove all variable names that conflict with a parent name. """
        self._remove_shadowed(set())

    def _remove_shadowed(self, defined):
        all_param_names = self.aliases.copy()
        for param in self.params:
            all_param_names |= param.aliases

        for param in self.params:
            param._remove_shadowed(defined)
            if isinstance(param, ComponentParam):
                param._remove_shadowed(defined | all_param_names)

    def remove_conflicting(self):
        """ Remove all names that occur multiple times, without a parent-child relation. """
        name_map = dict()
        self._remove_conflicting(name_map)

    def _remove_conflicting(self, name_map):
        super()._remove_conflicting(name_map)
        for param in self.params:
            param._remove_conflicting(name_map)

    def check_valid(self):
        """ Check if every parameter still has at least one name. """
        super().check_valid()
        for param in self.params:
            param.check_valid()

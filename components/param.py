

class Param(object):
    def __init__(self, name, tpe, default, aliases=None):
        # original name of the parameter
        self.name = name
        self.type = tpe
        self.default = default
        # aliases need to be unique within the component hierarchy. ComponentParam.enforce_consistency() checks this.
        if aliases is None:
            self.aliases = {self.name}
        else:
            self.aliases = set(aliases)

    @property
    def minimal_name(self):
        """ Shortest name that still uniquely identifies the parameter. """
        return min(self.aliases, key=len)

    @property
    def full_name(self):
        """ Fully defined name in component hierarchy. """
        return max(self.aliases, key=len)

    def __repr__(self):
        return f"Param: {self.full_name}"

    def _remove_shadowed(self, defined):
        self.aliases -= defined

    def _remove_conflicting(self, name_map):
        for alias in list(self.aliases):
            if alias in name_map:
                # name already defined
                other_param = name_map[alias]
                # use discard iso remove, because it may have already been deleted from the mapped param
                other_param.aliases.discard(alias)
                self.aliases.remove(alias)
                # Note: do not remove param from name_map, because conflict can occur more than 2 times
            else:
                name_map[alias] = self

    def check_valid(self):
        """ Check if parameter still has at least one name. """
        if len(self.aliases) == 0:
            raise AttributeError(f"No valid identifier for parameter {self.name}")

    def flatten(self):
        """ Return flattened version of params, without components. """
        return [self]


class ComponentParam(Param):
    def __init__(self, name, tpe, default, params=None, aliases=None):
        super().__init__(name, tpe, default, aliases=aliases)
        if params is None:
            self.params = list()
        else:
            self.params = params

    def __repr__(self):
        return f"ComponentParam: {self.full_name}"

    def enforce_consistency(self):
        # 1. remove all shadowed variable names
        self.remove_shadowed()
        # 2. resolve all conflicting names
        self.remove_conflicting()
        # 3. if param without valid identifier, raise error
        self.check_valid()

    def remove_shadowed(self):
        """
        Remove all variable names that conflict with a parent name.
        Uses depth first traversal to remove parent names from children.
        """
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
        """
        Remove all names that occur multiple times, without a parent-child relation.
        Uses in-order traversal with map from names to components to detect conflicts.
        """
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

    def flatten(self):
        """ Return flattened version of params, without components. """
        return sum(map(lambda x: x.flatten(), self.params), [])



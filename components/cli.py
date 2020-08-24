from components import ComponentResolver


class CLI:
    class Command(ComponentResolver):
        """ Resolves parameters from command line arguments. """

        # inherits from AttributeComponentResolver to ensure correct MRO.

        def __init_subclass__(cls, **kwargs):
            """ Hooks the subclass as a runnable command and set up command line arg parsing. """
            # TODO: implement
            super().__init_subclass__()
            print("Command", cls)

        @classmethod
        def get_provided_parameters(self):
            print("Command.get_provided_parameters")
            d = super().get_provided_parameters()
            mydata = {
                "par1": 42,
            }
            d.update(mydata)
            return d

    def run(self):
        pass
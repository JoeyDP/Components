from components import Component


class DataSource(Component):
    def __init__(self, path=None):
        self.path = path

    def load_data(self):
        return [66, 63, 13, 70, 44, 45, 22, 35, 3, 75, 54, 4, 14, 72, 67, 6, 45, 97, 40, 78]


class Algorithm(Component):
    def __init__(self):
        pass

    def fit(self, x):
        self.cutoff_ = sum(x) / len(x)
        return self

    def predict(self, x):
        return [xx >= self.cutoff_ for xx in x]


class Algorithm2(Algorithm):
    def __init__(self, par1: float = 0.1):
        super().__init__()
        self.par1 = par1

    def fit(self, x):
        self.cutoff_ = self.par1 * max(x)
        return self


class CrossValidation(Component):
    def __init__(self, ratio: float = 0.8):
        self.ratio = ratio

    def split_data(self, data):
        train_samples = int(len(data) * self.ratio)
        return data[:train_samples], data[train_samples:]


class Experiment(Component):
    """ A machine learning experiment. """

    def __init__(self, algorithm: Algorithm, splitter: CrossValidation, datasource: DataSource):
        """ Components for the experiment are supplied. """
        self.algorithm = algorithm
        self.splitter = splitter
        self.datasource = datasource

    def run(self):
        data = self.datasource.load_data()
        train, test = self.splitter.split_data(data)
        self.algorithm.fit(train)
        labels = self.algorithm.predict(test)
        print(f"Amount positive: {sum(labels)}")


class ExperimentVariant(Experiment):
    """ A variant of the experiment by overriding parameters and even components. """

    # change the algorithm to Algorithm2
    algorithm: Algorithm2

    # change default params
    par1 = 0.2
    ratio = 0.7


if __name__ == "__main__":
    # Run the experiment with default parameters:
    print("Run the experiment")
    exp = Experiment.resolve()
    exp.run()

    # Or provide parameters of components:
    print("Experiment variant one")
    exp_var1 = Experiment.resolve(ratio=0.5)
    exp_var1.run()

    # or use another defined variant of the experiment:
    print("Experiment variant two")
    exp_var2 = ExperimentVariant.resolve()
    exp_var2.run()


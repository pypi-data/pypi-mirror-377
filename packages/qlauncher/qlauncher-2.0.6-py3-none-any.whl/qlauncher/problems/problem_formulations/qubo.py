""" Basic problems for Orca """
import numpy as np
from pyqubo import Array
from qlauncher.problems.problem_formulations.jssp.pyqubo_scheduler import get_jss_bqm
import qlauncher.problems.problem_initialization as problem

from qlauncher.base import formatter, adapter


@adapter('qubo', 'qubo_fn')
def qubo_to_fn(qubo):
    # TODO check
    def qubo_fn(bin_vec):
        return np.dot(bin_vec, np.dot(qubo, bin_vec))
    return qubo_fn


@formatter(problem.MaxCut, 'qubo')
def get_maxcut_qubo(problem: problem.MaxCut):
    """ Returns Qubo function """
    n = len(problem.instance)
    Q = np.zeros((n, n))
    for (i, j) in problem.instance.edges:
        Q[i, i] += -1
        Q[j, j] += -1
        Q[i, j] += 1
        Q[j, i] += 1

    return Q, 0


@formatter(problem.EC, 'qubo')
class ECOrca:
    gamma = 1
    delta = 0.05

    def Jrr(self, route1, route2):
        s = len(set(route1).intersection(set(route2)))
        return s / 2

    def hr(self, route1, routes):
        i_sum = 0
        for r in routes:
            i_sum += len(set(r).intersection(set(route1)))
        s = i_sum - len(route1) * 2
        return s / 2

    def calculate_jrr_hr(self, problem: problem.EC):
        Jrr_dict = dict()
        indices = np.triu_indices(len(problem.instance), 1)
        for i1, i2 in zip(indices[0], indices[1]):
            Jrr_dict[(i1, i2)] = self.Jrr(
                problem.instance[i1], problem.instance[i2])

        hr_dict = dict()
        for i in range(len(problem.instance)):
            hr_dict[i] = self.hr(problem.instance[i], problem.instance)

        return Jrr_dict, hr_dict

    def calculate_lengths_tab(self, problem: problem.EC):
        tab = []
        for route in problem.instance:
            tab.append(len(route))
        return tab

    def calculate_num_elements(self, problem: problem.EC):
        d = dict()
        for route in problem.instance:
            for el in route:
                d[el] = 1
        return len(d)

    def calculate_instance_size(self, problem: problem.EC):
        # Calculate instance size for training
        return len(problem.instance)

    def __call__(self, problem: problem.EC):
        self.num_elements = self.calculate_num_elements(problem)
        self.len_routes = self.calculate_lengths_tab(problem)
        Q = np.zeros((len(problem.instance), len(problem.instance)))
        self.Jrr_dict, self.hr_dict = self.calculate_jrr_hr(problem)
        for i in self.Jrr_dict:
            Q[i[0]][i[1]] = self.Jrr_dict[i]
            Q[i[1]][i[0]] = Q[i[0]][i[1]]

        for i in self.hr_dict:
            Q[i][i] = -self.hr_dict[i]

        return Q, 0


@formatter(problem.JSSP, 'qubo')
class JSSPOrca:
    gamma = 1
    lagrange_one_hot = 1
    lagrange_precedence = 2
    lagrange_share = 5

    def _fix_get_jss_bqm(self, instance, max_time, config,
                         lagrange_one_hot=0,
                         lagrange_precedence=0,
                         lagrange_share=0) -> tuple[dict, list, None]:
        pre_result = get_jss_bqm(instance, max_time, config,
                                 lagrange_one_hot=lagrange_one_hot,
                                 lagrange_precedence=lagrange_precedence,
                                 lagrange_share=lagrange_share)
        result = (pre_result.spin.linear, pre_result.spin.quadratic,
                  pre_result.spin.offset)  # I need to change it into dict somehow
        return result, list(result[0].keys()), None

    def calculate_instance_size(self, problem: problem.JSSP):
        # Calculate instance size for training
        _, variables, _ = self._fix_get_jss_bqm(problem.instance, problem.max_time, self.config,
                                                lagrange_one_hot=self.lagrange_one_hot,
                                                lagrange_precedence=self.lagrange_precedence,
                                                lagrange_share=self.lagrange_share)
        return len(variables)

    def get_len_all_jobs(self, problem: problem.JSSP):
        result = 0
        for job in problem.instance.values():
            result += len(job)
        return result

    def one_hot_to_jobs(self, binary_vector, problem: problem.JSSP):
        actually_its_qubo, variables, model = self._fix_get_jss_bqm(problem.instance, problem.max_time, self.config,
                                                                    lagrange_one_hot=self.lagrange_one_hot,
                                                                    lagrange_precedence=self.lagrange_precedence,
                                                                    lagrange_share=self.lagrange_share)
        result = [variables[i]
                  for i in range(len(variables)) if binary_vector[i] == 1]
        return result

    def _set_config(self):
        self.config = {}
        self.config['parameters'] = {}
        self.config['parameters']['job_shop_scheduler'] = {}
        self.config['parameters']['job_shop_scheduler']['problem_version'] = "optimization"

    def __call__(self, problem: problem.JSSP):
        # Define the matrix Q used for QUBO
        self.config = {}
        self.instance_size = self.calculate_instance_size(problem)
        self._set_config()
        actually_its_qubo, variables, model = self._fix_get_jss_bqm(problem.instance, problem.max_time, self.config,
                                                                    lagrange_one_hot=self.lagrange_one_hot,
                                                                    lagrange_precedence=self.lagrange_precedence,
                                                                    lagrange_share=self.lagrange_share)
        reverse_dict_map = {v: i for i, v in enumerate(variables)}

        Q = np.zeros((self.instance_size, self.instance_size))

        for (label_i, label_j), value in actually_its_qubo[1].items():
            i = reverse_dict_map[label_i]
            j = reverse_dict_map[label_j]
            Q[i, j] += value
            Q[j, i] = Q[i, j]

        for label_i, value in actually_its_qubo[0].items():
            i = reverse_dict_map[label_i]
            Q[i, i] += value
        return Q / max(np.max(Q), -np.min(Q)), 0


@formatter(problem.Raw, 'qubo')
def get_raw_qubo(problem: problem.Raw):
    return problem.instance


@formatter(problem.GraphColoring, 'qubo')
def get_graph_coloring_qubo(problem: problem.GraphColoring):
    """ Returns Qubo function """
    num_qubits = problem.instance.number_of_nodes() * problem.num_colors
    x = Array.create('x', shape=(problem.instance.number_of_nodes(), problem.num_colors), vartype='BINARY')
    qubo = 0
    for node in problem.instance.nodes:
        qubo += (1 - sum(x[node, i] for i in range(problem.num_colors))) ** 2
    for n1, n2 in problem.instance.edges:
        for c in range(problem.num_colors):
            qubo += (x[n1, c] * x[n2, c])
    model = qubo.compile()
    qubo_dict, offset = model.to_qubo()
    Q_matrix = np.zeros((num_qubits, num_qubits))
    for i in range(num_qubits):
        for j in range(num_qubits):
            n1, c1 = i//problem.num_colors, i % problem.num_colors
            n2, c2 = j//problem.num_colors, j % problem.num_colors
            key = ("x["+str(n1)+"]["+str(c1)+"]", "x["+str(n2)+"]["+str(c2)+"]")
            if key in qubo_dict:
                Q_matrix[i, j] = qubo_dict[key]
    return Q_matrix, offset

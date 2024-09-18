import itertools
import numpy as np
import networkx as nx
from pandas import DataFrame
from csv_generator import probsHelper

class UAIParser:
    """
    A class to parse a UAI file and generate data from it.
    
    Attributes:
        filepath (str): path to the UAI file
        nodes (list[str]): list of node names in order of appearance in the UAI file
        network_type: type of network
        num_variables: number of variables
        domain_sizes: list of domain sizes
        parents: list of parents for each variable
        tables: list of conditional probability tables
        graph: networkx DiGraph object representing the network
        data: pandas DataFrame with the generated data
    """
    def __init__(self, filepath: str, nodes: list[str]) -> None:
        """
        Initialize the parser with the file path and node names.

        Args:
            filepath (str): path to the UAI file
            nodes (list[str]): list of node names in order of appearance in the UAI file
        """
        self.filepath = filepath
        self.nodes = nodes
        self.network_type = None
        self.num_variables = None
        self.domain_sizes = []
        self.parents = []
        self.tables = []
        self.graph = nx.DiGraph()
        self.data = []
    
    def parse(self) -> None:
        """
        Parse the UAI file and store the network information.
        """
        with open(self.filepath, 'r') as file:
            info = file.read().replace('\n', ' ').split()
            index = 0

            # Cabeçalho: tipo de rede
            self.network_type = info[index]
            index += 1
            
            # Número de variáveis
            self.num_variables = int(info[index])
            index += 1
            
            # Tamanhos dos domínios
            self.domain_sizes = list(map(int, info[2:2+self.num_variables]))
            index += self.num_variables
            
            # Lendo a lista de pais
            num_factors = int(info[index])
            index += 1
            self.parents = []
            for _ in range(num_factors):
                num_parents = int(info[index]) - 1
                index += 1
                self.parents.append(list(map(int, info[index:index + num_parents])))
                index += num_parents + 1
            
            # Lendo as tabelas de probabilidades condicionais
            self.tables = []
            for i in range(self.num_variables):
                num_entries = int(info[index])  # Quantidade de entradas na tabela
                index += 1
                flat_table = list(map(float, info[index:index + num_entries]))
                index += num_entries

                # Obtenha o número de dimensões da tabela (pais + nó)
                num_parents = len(self.parents[i])
                dims = [self.domain_sizes[parent] for parent in self.parents[i]] + [self.domain_sizes[i]]

                # Reformatar a tabela plana em uma matriz multidimensional
                table = np.array(flat_table).reshape(dims)
                self.tables.append(table)
                
        # Gerar o grafo        
        self.graph = nx.DiGraph()
        for i in range(self.num_variables):
            self.graph.add_node(i)
        for i, parents in enumerate(self.parents):
            for parent in parents:
                self.graph.add_edge(parent, i)
                
        for i, title in enumerate(self.nodes):
            nx.relabel_nodes(self.graph, {i: title}, copy=False)
            
    def calculate_probability(self, outcome: list[int]) -> float:
        """
        Calculate the probability of a given outcome.

        Args:
            outcome (list[int]): list of variable values

        Returns:
            float: probability of the outcome
        """
        probability = 1.0

        for i, value in enumerate(outcome):
            if len(self.parents[i]) == 0:
                probability *= self.tables[i][value]
            else:
                parent_values = tuple(outcome[parent] for parent in self.parents[i])
                probability *= self.tables[i][parent_values + (value,)]

        return probability
    
    def calculate_probabilities_for_outcomes(self, outcomes: list[list[int]]) -> list[float]:
        """
        Calculate the probabilities of a list of outcomes.

        Args:
            outcomes (list[list[int]]): list of outcomes

        Returns:
            list[float]: list of probabilities
        """
        probabilities = []
        for outcome in outcomes:
            prob = self.calculate_probability(outcome)
            probabilities.append(prob)
        return probabilities
            
    def generate_data(self) -> DataFrame:
        """
        Generate data from the network.

        Returns:
            DataFrame: DataFrame with the generated data
        """
        values = [list(range(size)) for size in self.domain_sizes]
        outcomes = list(itertools.product(*values))
        probs = self.calculate_probabilities_for_outcomes(outcomes)
        probabilities = [[sublist, val] for sublist, val in zip(outcomes, probs)]
        self.data = probsHelper(self.nodes, probabilities, csv_flag=False)
        return self.data
        
    def display(self) -> None:
        """
        Display the network information.
        """
        print(f"Tipo de rede: {self.network_type}")
        print(f"Número de variáveis: {self.num_variables}")
        print(f"Tamanhos dos domínios: {self.domain_sizes}")
        print(f"Pais das variáveis:")
        for parents in self.parents:
            print(f"  {parents}")
        print(f"Tabelas de probabilidades condicionais:")
        for table in self.tables:
            print(table, end="\n\n\n")
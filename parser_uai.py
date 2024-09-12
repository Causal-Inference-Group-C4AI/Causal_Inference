import numpy as np
import networkx as nx
import pandas as pd

def prob_to_distribution(p: list[float], n: int = 1000) -> list[int]:
    """Gera uma distribuição de valores baseada nas probabilidades marginais fornecidas.
    Garante que o número de ocorrências de cada valor seja muito próximo das probabilidades dadas.

    Args:
        p (list[float]): Lista de probabilidades para cada valor (marginal).
        n (int, optional): Número de amostras. Defaults to 1000.

    Returns:
        list[int]: Dados gerados com base nas probabilidades marginais, randomicamente embaralhados.
    """
    # Calcula o número de ocorrências de cada valor baseado nas probabilidades marginais
    occurrences = [int(prob * n) for prob in p]

    # Corrige o número total de amostras (pode ser que a soma dos arredondamentos não dê exatamente n)
    while sum(occurrences) < n:
        # Adiciona uma ocorrência ao valor com a maior diferença fracionária
        diff = [prob * n - occ for prob, occ in zip(p, occurrences)]
        occurrences[np.argmax(diff)] += 1

    while sum(occurrences) > n:
        # Remove uma ocorrência ao valor com a menor diferença fracionária
        diff = [occ - prob * n for prob, occ in zip(p, occurrences)]
        occurrences[np.argmin(diff)] -= 1

    # Gera a lista de valores baseada nas ocorrências calculadas
    values = []
    for i, occ in enumerate(occurrences):
        values.extend([i] * occ)

    # Embaralha a lista de valores para garantir aleatoriedade
    np.random.shuffle(values)

    return values

class UAIParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.network_type = None
        self.num_variables = None
        self.domain_sizes = []
        self.parents = []
        self.tables = []
        self.marginals = []
        self.graph = nx.DiGraph()
        self.data = []
        
    def parse(self):
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

    def generate_graph(self):
        self.graph = nx.DiGraph()
        for i in range(self.num_variables):
            self.graph.add_node(i)
        for i, parents in enumerate(self.parents):
            for parent in parents:
                self.graph.add_edge(parent, i)
        return self.graph
    
    def set_nodes(self, lables):
        if not self.graph:
            self.generate_graph()
        
        new_graph = self.graph.copy()
        for i, title in enumerate(lables):
            nx.relabel_nodes(new_graph, {i: title}, copy=False)
            
        return new_graph
    
    def calculate_marginals(self):
        self.marginals = [None] * self.num_variables  # Inicializa marginais vazias
        
        # Construir grafo da rede bayesiana para determinar a ordem topológica
        if self.graph.number_of_nodes() == 0:
            self.generate_graph()
        
        # Obter a ordem topológica dos nós
        topo_order = list(nx.topological_sort(self.graph))

        # Calcular as marginais seguindo a ordem topológica
        for i in topo_order:
            if len(self.parents[i]) == 0:
                # Variável sem pais: a tabela já é a marginal
                marginal = self.tables[i]
            else:
                # Variável com pais: calcular a marginal
                marginal = np.zeros(self.domain_sizes[i])
                table = self.tables[i]
                
                # Iterar sobre todas as combinações de pais
                parent_sizes = [self.domain_sizes[parent] for parent in self.parents[i]]
                parent_marginals = [self.marginals[parent] for parent in self.parents[i]]

                # Para cada combinação dos valores dos pais
                for parent_combination in np.ndindex(*parent_sizes):
                    # Calcular a probabilidade dos pais
                    prob_parent = 1.0
                    for p, parent_idx in enumerate(self.parents[i]):
                        prob_parent *= parent_marginals[p][parent_combination[p]]
                    
                    # Somar para a marginal da variável
                    for value in range(self.domain_sizes[i]):
                        marginal[value] += table[parent_combination + (value,)] * prob_parent
            
            # Normalizar as probabilidades marginais
            marginal /= np.sum(marginal)
            self.marginals[i] = marginal
    
    def generate_data(self, n=1000):
        if not self.marginals:
            self.calculate_marginals()
        
        distributions = []
        for marginal in self.marginals:
            distributions.append(prob_to_distribution(marginal, n))
            
        self.data = pd.DataFrame(distributions).T
        
        return self.data
    
    def display_marginals(self):
        print("Probabilidades marginais:")
        for i, marginal in enumerate(self.marginals):
            print(f"Marginal de {i}: {marginal}")
            
    def display(self):
        print(f"Tipo de rede: {self.network_type}")
        print(f"Número de variáveis: {self.num_variables}")
        print(f"Tamanhos dos domínios: {self.domain_sizes}")
        print(f"Pais das variáveis:")
        for parents in self.parents:
            print(f"  {parents}")
        print(f"Tabelas de probabilidades condicionais:")
        for table in self.tables:
            print(table, end="\n\n\n")
        if self.marginals:
            self.display_marginals()
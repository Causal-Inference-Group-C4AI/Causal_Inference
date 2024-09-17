import networkx as nx, numpy as np, pandas as pd
import dowhy
import dowhy.gcm as gcm
import statsmodels.api as sm
import logging
import os

os.environ['OMP_NUM_THREADS'] = '1'

logging.basicConfig(level=logging.WARNING)

# ================================================================================

# Tentativa usando GCM (falha: não suporta variaveis latentes):

# df = pd.read_csv('test-ijar.csv')
# X1 = df['X1']
# X2 = df['X2']
# data = pd.DataFrame(dict(X1=X1, X2=X2))

# causal_model = gcm.ProbabilisticCausalModel(nx.DiGraph([('U1', 'X1'), ('U2', 'X1'), ('U3', 'X1'), ('U1', 'X2'), ('X1', 'X2')]))
# gcm.auto.assign_causal_mechanisms(causal_model, data)
# gcm.fit(causal_model, data)

# gcm.average_causal_effect(causal_model,
#                          'X2',
#                          interventions_alternative={'X1': lambda x: 1},
#                          interventions_reference={'X1': lambda x: 0},
#                          num_samples_to_draw=1000)

# ================================================================================

# Tentativa usando GCM, sem variaveis latentes (nao printa ACE):

# df = pd.read_csv('test-ijar.csv')
# X1 = df['X1']
# X2 = df['X2']
# data = pd.DataFrame(dict(X1=X1, X2=X2))

# causal_model = gcm.ProbabilisticCausalModel(nx.DiGraph([('X1', 'X2')]))
# gcm.auto.assign_causal_mechanisms(causal_model, data)
# gcm.fit(causal_model, data)

# gcm.average_causal_effect(causal_model,
#                          'X2',
#                          interventions_alternative={'X1': lambda x: 1},
#                          interventions_reference={'X1': lambda x: 0},
#                          num_samples_to_draw=100)

# ================================================================================

# Sem usar GCM
# Output: Estimation failed! No relevant identified estimand available for this estimation method.

data = pd.read_csv('test-ijar.csv')

# Define causal graph
causal_graph = """
digraph {
    X1 -> X2;
    U1 -> X1;
    U2 -> X1;
    U3 -> X1;
    U1 -> X2;
}
"""

# Test: simple confouder example (also fails)
simple_confounder_graph = """
digraph {
    X1 -> X2;
    U1 -> X1;
    U1 -> X2;
}
"""

# Test: no confouder example (success)
no_confounder_graph = """
digraph {
    X1 -> X2;
    U1 -> X1;
}
"""

# Conclusion: dowhy seems to not support confounders

# Create causal model
model = dowhy.CausalModel(
    data=data,
    graph=causal_graph,
    treatment='X1',
    outcome='X2',
    common_causes=['U1']
)

# Identify the effect
identified_estimand = model.identify_effect()

# Estimate the effect using Generalized Causal Model
estimate = model.estimate_effect(
    identified_estimand,
    method_name="backdoor.generalized_linear_model",
    method_params={'glm_family': sm.families.Binomial()}
)

# Print the estimated ATE
print("Average Treatment Effect (ATE):")
print(estimate)
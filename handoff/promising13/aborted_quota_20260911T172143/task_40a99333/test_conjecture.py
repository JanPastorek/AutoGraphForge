import networkx as nx
import numpy as np
import scipy.optimize
import random

def check_graph(G):
    nodes = list(G.nodes())
    n = len(nodes)
    if n < 2 or any(G.degree(v) == 0 for v in nodes):
        return None, None
    
    # 1. Total domination
    c_t = np.ones(n)
    adj_matrix = np.zeros((n, n))
    for i, u in enumerate(nodes):
        for v in G.neighbors(u):
            adj_matrix[i, nodes.index(v)] = 1
    
    res_t = scipy.optimize.milp(c=c_t, constraints=scipy.optimize.LinearConstraint(adj_matrix, 1, np.inf),
                                integrality=np.ones(n), bounds=scipy.optimize.Bounds(0, 1))
    gt = int(round(res_t.fun))
    
    # 2. Roman domination
    c_R = np.concatenate([np.ones(n), 2*np.ones(n)])
    A1 = np.hstack([np.eye(n), np.eye(n) + adj_matrix])
    A2 = np.hstack([np.eye(n), np.eye(n)])
    
    A_R = np.vstack([A1, A2])
    b_l = np.concatenate([np.ones(n), np.zeros(n)])
    b_u = np.concatenate([np.full(n, np.inf), np.ones(n)])
    
    res_R = scipy.optimize.milp(c=c_R, constraints=scipy.optimize.LinearConstraint(A_R, b_l, b_u),
                                integrality=np.ones(2*n), bounds=scipy.optimize.Bounds(0, 1))
    gr = int(round(res_R.fun))
    return gt, gr

print("Testing various families and random graphs...")
count = 0
for n in range(3, 16):
    for trial in range(50):
        for p in [0.1, 0.2, 0.3, 0.5, 0.7]:
            G = nx.erdos_renyi_graph(n, p)
            gt, gr = check_graph(G)
            if gt is not None:
                count += 1
                if gt > gr:
                    print(f"COUNTEREXAMPLE! n={n}, p={p}, gt={gt}, gr={gr}, edges={list(G.edges())}")
                    exit(0)

print(f"Successfully checked {count} graphs, 0 counterexamples found!")

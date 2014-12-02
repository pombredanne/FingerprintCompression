'''
2 Wavelet packets
2.4 Best basis (1D)
@author     Matthias Moulin & Vincent Peeters
@version    1.0
'''

import node
import numpy as np
import pywt

###############################################################################
# COST FUNCTIONS
############################################################################### 

def cost_threshold(C, threshold):
    def cost_fixed_threshold(C):
        cost = 0
        for i in range(C.shape[0]):
          if (abs(C[i]) > threshold):
            cost = cost + 1
        return cost
    return cost_fixed_threshold
        
def cost_shannon(C):
    cost = 0
    for i in range(C.shape[0]):
        if (C[i] != 0):
            cost = cost - C[i]*C[i]*np.log2(abs(C[i]))
    return cost

###############################################################################
# ANALYSIS ALGORITHM FUNCTIONS
###############################################################################        
def wp(S, cost, wavelet="db4", mode=pywt.MODES.ppd, level=4):
    #Data collection step
    Nodes = collect(S, wavelet=wavelet, mode=mode, level=level)
    #Dynamic programming upstream traversal
    mark(Nodes, cost)
    #node.print_nodes(Nodes)
    #Dynamic programming downstream traversal
    Result = []
    traverse(Nodes[0][0], Nodes, Result)
    traverse(Nodes[0][1], Nodes, Result)
    return sorted(Result, cmp=node.compare_low_level_first, reverse=False)
                     
def collect(S, wavelet, mode, level):
    Nodes = [[] for i in range(level)]
    (Cl, Cr) = pywt.dwt(S, wavelet=wavelet, mode=mode)
    Nodes[0] = [node.Node(Cl, 0, 0), node.Node(Cr, 0, 1)]
    for l in range(0, level-1):
        Parents = Nodes[l]
        Childs = []
        for p in range(len(Parents)):
            (Cl, Cr) = pywt.dwt(Parents[p].C, wavelet=wavelet, mode=mode)
            Childs.append(node.Node(Cl, l+1, 2*p))
            Childs.append(node.Node(Cr, l+1, 2*p+1))
        Nodes[l+1] = Childs 
    return Nodes
    
def mark(Nodes, cost):
    for p in range(len(Nodes[-1])):
        Node = Nodes[-1][p]
        cp = cost(Node.C)
        Node.cost = cp
        Node.best = cp
    for l in range(len(Nodes)-2, -1, -1):
        for p in range(len(Nodes[l])):
            Node = Nodes[l][p]
            cc = Nodes[l+1][2*p].best + Nodes[l+1][2*p+1].best
            cp = cost(Node.C)
            Node.cost = cp
            if cp <= cc:
                Node.best = cp
            else:
                Node.best = cc 
          
def traverse(Node, Nodes, Result):
    if (Node.best == Node.cost):
        Result.append(Node)
    else:
        i = Node.level + 1
        j = 2 * Node.index
        traverse(Nodes[i][j], Nodes, Result)
        traverse(Nodes[i][j+1], Nodes, Result)                   

###############################################################################
# SYNTHESIS ALGORITHM FUNCTIONS
###############################################################################        
def iwp(Nodes, wavelet="db4", mode=pywt.MODES.ppd):
    while len(Nodes) != 1:
        Nodes = sorted(Nodes, cmp=node.compare_high_level_first, reverse=False)
        Node1 = Nodes[0]
        Node2 = Nodes[1] 
        S = pywt.idwt(Node1.C, Node2.C, wavelet=wavelet, mode=mode, correct_size=True)
        Merged = node.Node(S, (Node1.level-1), (Node1.index / 2))
        Nodes = Nodes[2:]
        Nodes.append(Merged)
    return Nodes[0].C

###############################################################################
# TESTS
###############################################################################                                          
def h(x):
    if x<0:
        return 1+x
    else:
        return -1+x   

def samples(nb_samples=1000):
    t = (np.linspace(-1,1,nb_samples+1))[:-1]
    return np.vectorize(h)(x=t)  
      
def get_smooth_func():
    time = np.linspace(1,40,1000)
    freq = 500
    freqs = 8000
    return np.sin(2*np.pi*freq/freqs*time)     
      
if __name__ == "__main__":
    S = get_smooth_func()
    Nodes=wp(S, cost_shannon)
    node.print_flattened_nodes(Nodes)
    R = iwp(Nodes)
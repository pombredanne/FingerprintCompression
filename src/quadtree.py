'''
2 Wavelet packets
2.4 Best basis (2D)
@author     Matthias Moulin & Vincent Peeters
@version    1.0
'''
import cost
import heapq
import node
import numpy as np
import pywt

###############################################################################
# ANALYSIS ALGORITHM FUNCTIONS
###############################################################################        

def wp2(S, costf, wavelet="db4", mode=pywt.MODES.ppd, level=4):
    '''
    Returns the 2D discrete wavelet packet transformation, with the best basis according
    to the given cost function, for the given 2D input signal.
    @param S:         Input signal.
                      Both single and double precision floating-point data types are supported
                      and the output type depends on the input type. If the input data is not
                      in one of these types it will be converted to the default double precision
                      data format before performing computations.
    @param costf:      The (single parameter) cost function that must be used while
                      searching for the best basis.
    @param wavelet:   Wavelet to use in the transform. 
                      This must be a name of the wavelet from the wavelist() list.
    @param mode:      Signal extension mode to deal with the border distortion problem.
                      The default mode is periodic-padding.
    @param level:     Number of decomposition steps to perform.
    @return:          A list containing the nodes of the 2D discrete wavelet packet transformation,
                      with the best basis according to the given cost function, for the given input signal. 
    '''
    #Data collection step
    Nodes = collect(S, wavelet=wavelet, mode=mode, level=level)
    #Dynamic programming upstream traversal
    mark(Nodes, costf)
    #node.print_nodes(Nodes)
    #Dynamic programming downstream traversal
    Result = []
    traverse(Nodes[0][0], Nodes, Result)
    traverse(Nodes[0][1], Nodes, Result)
    traverse(Nodes[0][2], Nodes, Result)
    traverse(Nodes[0][3], Nodes, Result)
    return sorted(Result, cmp=node.compare_low_level_first, reverse=False)
                     
def collect(S, wavelet, mode, level):
    '''
    Returns the full quad tree of wavelet packets.
    @param S:         Input signal.
                      Both single and double precision floating-point data types are supported
                      and the output type depends on the input type. If the input data is not
                      in one of these types it will be converted to the default double precision
                      data format before performing computations.
    @param wavelet:   Wavelet to use in the transform. 
                      This must be a name of the wavelet from the wavelist() list.
    @param mode:      Signal extension mode to deal with the border distortion problem.
    @param level:     Number of decomposition steps to perform. If the level is None, then the
                      full decomposition up to the level computed with dwt_max_level() function for
                      the given data and wavelet lengths is performed.
    @return:          The full quad tree of wavelet packets.
    '''
    Nodes = [[] for i in range(level)]
    (CA, (CH, CV, CD)) = pywt.dwt2(S, wavelet=wavelet, mode=mode)
    Nodes[0] = [node.Node(CA, 0, 0), node.Node(CH, 0, 1), node.Node(CV, 0, 2), node.Node(CD, 0, 3)]
    for l in range(0, level-1):
        Parents = Nodes[l]
        Childs = []
        for p in range(len(Parents)):
            (CA, (CH, CV, CD)) = pywt.dwt2(Parents[p].C, wavelet=wavelet, mode=mode)
            Childs.append(node.Node(CA, l+1, 4*p))
            Childs.append(node.Node(CH, l+1, 4*p+1))
            Childs.append(node.Node(CV, l+1, 4*p+2))
            Childs.append(node.Node(CD, l+1, 4*p+3))
        Nodes[l+1] = Childs 
    return Nodes
    
def mark(Nodes, costf):
    '''
    Marks every node of nodes with the best cost seen so far. 
    @param Nodes:     List containing the nodes of the 2D discrete wavelet packet
                      transformation.
    @param costf:      The (single parameter) cost function that must be used while
                      searching for the best basis.
    '''
    for p in range(len(Nodes[-1])):
        Node = Nodes[-1][p]
        cp = costf(Node.C)
        Node.cost = cp
        Node.best = cp
    for l in range(len(Nodes)-2, -1, -1):
        for p in range(len(Nodes[l])):
            Node = Nodes[l][p]
            cc = Nodes[l+1][4*p].best + Nodes[l+1][4*p+1].best + Nodes[l+1][4*p+2].best + Nodes[l+1][4*p+3].best
            cp = costf(Node.C)
            Node.cost = cp
            if cp <= cc:
                Node.best = cp
            else:
                Node.best = cc 
          
def traverse(Node, Nodes, Result):
    '''
    Traverses the given node.
    The node will be added to the result if it belongs to the best basis.
    Otherwise the node childs will be traversed recursively.
    @param Node:      The current node to traverse.
    @param Nodes:     List containing the nodes of the 2D discrete wavelet packet
                      transformation.
    @param Result:    Buffer containing the nodes traversed so far that belong
                      to the best basis.
    '''
    if (Node.best == Node.cost):
        Result.append(Node)
    else:
        i = Node.level + 1
        j = 4 * Node.index
        traverse(Nodes[i][j], Nodes, Result)
        traverse(Nodes[i][j+1], Nodes, Result)
        traverse(Nodes[i][j+2], Nodes, Result)  
        traverse(Nodes[i][j+3], Nodes, Result) 
        
###############################################################################
# SYNTHESIS ALGORITHM FUNCTIONS
###############################################################################
        
def iwp2(Nodes, wavelet="db4", mode=pywt.MODES.ppd):
    '''
    Returns the inverse 2D discrete wavelet packet transformation for the given
    list containing the nodes of the 2D discrete wavelet packet transformation.
    @param Nodes:     List containing the nodes of the 2D discrete wavelet packet
                      transformation.
    @param wavelet:   Wavelet to use in the transform. 
                      This must be a name of the wavelet from the wavelist() list.
    @param mode:      Signal extension mode to deal with the border distortion problem.
                      The default mode is periodic-padding.
    @return:          The inverse 2D discrete wavelet packet transformation for the given
                      list containing the nodes of the 2D discrete wavelet packet transformation.
    '''
    heapq.heapify(Nodes)
    while len(Nodes) != 1:
        Node1 = heapq.heappop(Nodes)
        Node2 = heapq.heappop(Nodes)
        Node3 = heapq.heappop(Nodes)
        Node4 = heapq.heappop(Nodes) 
        
        try:
            S = pywt.idwt2((Node1.C, (Node2.C, Node3.C, Node4.C)), wavelet=wavelet, mode=mode)
        except ValueError:
            print("Id: " + str(Node1.level) + "," + str(Node1.index))
            print(Node1.C.shape)
            print("Id: " + str(Node2.level) + "," + str(Node2.index))
            print(Node2.C.shape)
            print("Id: " + str(Node3.level) + "," + str(Node3.index))
            print(Node3.C.shape)
            print("Id: " + str(Node4.level) + "," + str(Node4.index))
            print(Node4.C.shape)
            raise ValueError
          
        Merged = node.Node(S, (Node1.level-1), (Node1.index / 4))
        heapq.heappush(Nodes, Merged)
    return Nodes[0].C
        
###############################################################################
# TESTS
###############################################################################
                                          
def matrix(size = 100):
    S = np.zeros(np.array([size, size]), dtype=float)
    half = int(size / 2) - 1
    S[half, half] = 1
    return S      
    
def matrix2(size = 100):
    S = np.zeros(np.array([size, size]), dtype=float)
    half = int(size / 2) - 1
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            if (i-half)*(i-half) + (j-half)*(j-half) <= 10:
                S[i,j] = 1
    return S
    
def matrix3(size = 100):
    S = np.zeros(np.array([size, size]), dtype=float)
    half = int(size / 2) - 1
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            if (abs(i-half) <= 3 and abs(j-half) <= 6):
                S[i,j] = 1
    return S

import configuration as c
import cv2
def house():
    fname = c.get_dir_fingerprints() + "house.tif"
    return cv2.imread(fname, 0)

def fingerprint():
    fname = c.get_dir_fingerprints() + "cmp00001.pgm"
    return cv2.imread(fname, 0)   
      
if __name__ == "__main__":
    S = matrix(64)
    #S = matrix2(64)
    #S = matrix3(64)
    Nodes=wp2(S, cost.cost_shannon)
    #Nodes=wp2(S, cost.cost_threshold(0.01))
    node.print_flattened_nodes(Nodes)
    #R = iwp2(Nodes)
    
    #S = house()
    #S = fingerprint()
    #Nodes=wp2(S, cost.cost_shannon)
    #Nodes=wp2(S, cost.cost_threshold(0.01))
    #node.print_flattened_nodes(Nodes)
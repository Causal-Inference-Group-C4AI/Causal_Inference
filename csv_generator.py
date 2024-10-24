#!/usr/bin/python3

import csv

from typing import List, Tuple

ArrayType = List[Tuple[List[int], float]]

def probsHelper(header: str, probCombinations: ArrayType, filename: str):
    maxDecimals: int = 0
    for _sublist, val in probCombinations:
        probStr: str = str(val)
        if "." in probStr:
            maxDecimals = max(maxDecimals, len(probStr.split(".")[1]))    

    with open("./csv_data_examples/" + filename + ".csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for sublist, val in probCombinations:
            numberOfRows: int = (int)(val * pow(10, maxDecimals))            
            for _ in range(numberOfRows):
                writer.writerow(sublist)

if __name__ == "__main__":
    """
    Generate a dataset in the csv format which is consistent with the specified distribution. As input, it needs: a header
    row for the csv, the probability of each outcome of the variables and the csv filename.     
    """    
    m = [[0, 0, 0, 0, 0, 0, 0], 
        [1, 0, 1, 0, 0, 0, 0], 
        [1, 0, 0, 0, 0, 0, 0], 
        [1, 0, 0, 0, 0, 0, 0], 
        [1, 0, 0, 0, 0, 0, 0], 
        [1, 0, 0, 0, 1, 0, 0], 
        [0, 0, 0, 0, 1, 0, 0]]
    edges = ""
    mapping = dict()
    for i, l in enumerate(m):
        n1 = chr(ord('A') + i)
        vi = f"V{i}"
        mapping[vi] = n1
        for j, node in enumerate(l):
            if node:
                n2 = chr(ord('A') + j)
                edges = f"{edges}{n1} -> {n2}, "
    edges=edges[:len(edges)-2]
    print(edges)
    print(str(mapping))

#     probabilities_z_x_y: ArrayType = [
#         [[0, 0, 0], 0.288],
#         [[0, 0, 1], 0.036],
#         [[0, 1, 0], 0.288],
#         [[0, 1, 1], 0.288],
#         [[1, 0, 0], 0.002],
#         [[1, 0, 1], 0.067],
#         [[1, 1, 0], 0.017],
#         [[1, 1, 1], 0.014],
#     ]

#     probsHelper(["Z", "X", "Y"], probabilities_z_x_y, "balke_pearl")


#     probabilities_x_y: ArrayType = [
#         [[0, 0], 0.250],
#         [[0, 1], 0.250],
#         [[1, 0], 0.250],
#         [[1, 1], 0.250],
#     ]

#     probsHelper(["X", "Y"], probabilities_x_y, "trivial")


#     probabilities_exemplo_7 = [
#     [[0, 0, 0, 0, 0], 0.5**3],
#     [[0, 0, 1, 0, 0], 0.5**3],
#     [[0, 1, 0, 0, 0], 0.5**3],
#     [[0, 1, 1, 1, 1], 0.5**3],
#     [[1, 0, 0, 0, 1], 0.5**3],
#     [[1, 0, 1, 0, 1], 0.5**3],
#     [[1, 1, 0, 0, 1], 0.5**3],
#     [[1, 1, 1, 0, 1], 0.5**3],
# ]
    
    # probabilities_exemplo_7: ArrayType = [
    #     [[0, 0, 0, 0, 0], 0.125],
    #     [[0, 0, 1, 0, 0], 0.125],
    #     [[0, 1, 0, 0, 0], 0.125],
    #     [[0, 1, 1, 1, 1], 0.125],
    #     [[1, 0, 0, 0, 1], 0.125],
    #     [[1, 0, 1, 0, 1], 0.125],
    #     [[1, 1, 0, 0, 1], 0.125],
    #     [[1, 1, 1, 0, 1], 0.125],
    # ]

    # probsHelper(["X", "Y", "U1", "U2", "U3"], probabilities_exemplo_7, "slide_exemplo_7")


    
    # probabilities_x_y: ArrayType = [
    #     [[0, 0], 0.375],
    #     [[0, 1], 0.5],
    #     [[1, 0], 0.0],
    #     [[1, 1], 0.125],
    # ]

    # probsHelper(["X", "Y"], probabilities_x_y, "7_nao_obs")

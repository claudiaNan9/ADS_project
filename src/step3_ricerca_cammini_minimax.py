# Kruskal’s Algorithm is a Greedy algorithm used to find the  Minimum Spanning Tree (MST).
# It works by sorting all edges in increasing order of weight and adding them one by one, ensuring no cycles are formed.

# Explanation

# Let’s break down how Kruskal’s Algorithm works step-by-step:

# Sort all edges of the graph based on their weights in ascending order.

# Initialize a disjoint set (Union-Find) to keep track of connected components.

# Iterate through sorted edges:

# If the edge connects two different components, include it in the MST.

# If it forms a cycle, skip it.

# Repeat until you have V−1 edges in your MST (where V is the number of vertices).

# The total weight of included edges gives the minimum cost.


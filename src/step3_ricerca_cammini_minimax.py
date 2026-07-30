# Kruskal's Algorithm is a Greedy algorithm used to find the Minimum Spanning Tree (MST).
# It works by sorting all edges in increasing order of weight and adding them one by one, ensuring no cycles are formed.

# Explanation

# Let's break down how Kruskal's Algorithm works step-by-step:

# Sort all edges of the graph based on their weights in ascending order.

# Initialize a disjoint set (Union-Find) to keep track of connected components.

# Iterate through sorted edges:

# If the edge connects two different components, include it in the MST.

# If it forms a cycle, skip it.

# Repeat until you have V−1 edges in your MST (where V is the number of vertices).

# The total weight of included edges gives the minimum cost.

## Union-Find ottimizzata con:
## - path compression: anzichè formare una fila lunghissima di nodi attaccati a quella radice (per cui poi per trovarlo devo andare a ritroso tantissimo) 
## attaco direttamente i nuovi elementi alla radice 

from step2_costruzione_grafo import Graph
import time
from time import perf_counter

class UnionFind:
    def __init__(self, n):
        #inizializza una lista di n elementi (dove n è il numero di nodi) per tenere traccia del parent di quel nodo (all'inizio ogni nodo è parent di se stesso)
        self.parent = [i for i in range(n)] 
        self.rank = [0] * n # inizializza a 0 il rank (altezza) di ogni nodo

    def find(self, x):
        if self.parent[x] != x:  # se x non è la root (non è parent di sè stesso)
            # Path compression: risale ricorsivamente fino alla root e tornando indietro collega direttamente tutti i nodi incontrati lungo il percorso
            self.parent[x] = self.find(self.parent[x])

        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)

        # Union by rank 
        if rootX != rootY: # se le root sono diverse (set diversi)
            if self.rank[rootX] < self.rank[rootY]: #se il rango è minore
                self.parent[rootX] = rootY #assegna la root col rango maggiore
            elif self.rank[rootX] > self.rank[rootY]: # viceversa
                self.parent[rootY] = rootX
            else:
                self.parent[rootY] = rootX #se sono uguali incrementa il rango
                self.rank[rootX] += 1
            return True # unione eseguita
        return False # erano nello stesso set


def kruskal(graph):
    if graph.directed: # kruskal va bene solo per un grafo non orientato, quindi mettiamo un check sulla tipologia
        raise ValueError(
            "Kruskal richiede un grafo non orientato."
        )

    nodes = graph.get_nodes()
    n = len(nodes)

    if n == 0:
        return Graph(directed=False), 0 # il grafo è vuoto e ha 0 come peso totale

    # Gli identificatori AS non sono 0, 1, 2, quindi li associamo a indici consecutivi così UnionFind può usare liste
    node_to_index = {
        node: index
        for index, node in enumerate(nodes)
    }

    # Ogni arco ha la forma: (from_node, to_node, frequenza)
    edges = graph.get_edges()

    for u, v, weight in edges:
        if weight is None:
            raise ValueError(
                f"L'arco ({u}, {v}) non ha una frequenza valida."
            )

    # Ordine crescente di frequenza per costruire il MST
    edges.sort(key=lambda edge: edge[2]) #scorre la lista e prende il terzo elemento (indice 2) che sarebbe la frequenza

    union_find = UnionFind(n)  # chiamo union find sui nodi 
    # crea l'mst come oggetto Graph
    mst = Graph(directed=False)
    for node in nodes:
       mst.add_node(node)

    mst_weight = 0 # costo totale MST
    selected_edges = 0 # numero di archi selezionati

    for u, v, weight in edges:
        index_u = node_to_index[u]
        index_v = node_to_index[v]

        if union_find.union(index_u, index_v):  # se l'arco non crea un ciclo viene aggiunto, altrimenti no
            # Salva l'arco in entrambe le direzioni nell'oggetto Graph
            mst.add_edge(u,v,weight) # questo metodo della classe Graph lo aggiunge in entrambe le direzioni
            #mst.adjacency_list[u][v] = weight
            #mst.adjacency_list[v][u] = weight

            mst_weight += weight # somma il peso
            selected_edges += 1 # aumenta il numero di archi

            if selected_edges == n - 1:   # il grafo deve contenere n nodi - 1 archi
                break

    if selected_edges != n - 1:  # se non è così vuol dire che il grafo non era connesso
        raise ValueError(
            "Il grafo non è connesso. Usare prima la componente connessa più grande."
        )

    return mst, mst_weight


## dfs per rispondere alle query

def minimax_query_dfs(mst, start, target):

    if start not in mst.adjacency_list:
        raise ValueError(f"Il nodo {start} non esiste nell'MST.")

    if target not in mst.adjacency_list:
        raise ValueError(f"Il nodo {target} non esiste nell'MST.")

    if start == target:  
        return 0, [start], []

    visited = {start} # insieme dei visitati

    # Ogni elemento dello stack (lista di tuple) contiene: (nodo corrente, massimo peso incontrato, percorso seguito)
    stack = [(start, 0, [start])]

    while stack: 
        node, current_max, path = stack.pop() # tira fuori l'ultimo elemento (lifo)

        if node == target:
            # trovato il target, ricostruisce i pesi del percorso
            weights = []

            for u, v in zip(path, path[1:]): # accoppia nodi consecutivi nella lista del percorso e ne estrae il peso corrispondente
                weights.append(mst.adjacency_list[u][v])

            return current_max, path, weights

        # mst.adjacency_list[node] è un dizionario {vicino: peso} quindi la visita segue l'ordine in cui gli elementi compaiono nel dizionario
        for neighbor, weight in mst.adjacency_list[node].items(): 
            if neighbor not in visited:
                visited.add(neighbor)

                new_max = max(current_max, weight) # aggiorna il massimo peso incontrato lungo il cammino corrente
                new_path = path + [neighbor] # aggiunge altro nodo al percorso

                stack.append(( # aggiorna lo stack
                    neighbor,
                    new_max,
                    new_path
                ))

    raise ValueError(
        f"Non esiste un cammino tra {start} e {target}."
    )



if __name__ == "__main__":


        ### qui usiamo per_counter al posto di time che dicono sia meglio per il calcolo dei tempi ####
        
        # grafo di test più piccolo 

        # grafo = Graph.load_graph(
                #     "/code/ADSproject/data/grafo_largest_test.pkl"
                # )

        grafo = Graph.load_graph( "/code/ADSproject/data/grafo.pkl") # carichiamo direttamente tutto il grafo se è connesso 
        #largest_component = Graph.load_graph("/code/ADSproject/data/grafo_largest_component.pkl") # il largest component se il grafo non è connesso e abbiamo trovato la componente più grande

        inizio = perf_counter()
        mst, mst_weight = kruskal(grafo)
        fine = perf_counter()

        print(f"Tempo Kruskal: {fine - inizio:.6f} secondi")
        print(f"Peso totale MST: {mst_weight}")
        print(f"Nodi MST: {len(mst.get_nodes())}")
        print(f"Archi MST: {len(mst.get_edges())}")


        # due nodi di esempio 

        start = 702
        target = 4436

        costo, cammino, pesi = minimax_query_dfs(mst, start, target)

        print(f"\nQuery minimax da {start} a {target}:")
        print(f"Costo: {costo}")
        print(f"Cammino: {cammino}")
        print(f"Pesi attraversati: {pesi}")

        if pesi:
            pesi_stringa = ", ".join(map(str, pesi))
            print(f"Calcolo del costo: max({pesi_stringa}) = {costo}")
        else:
            print("Calcolo del costo: 0")
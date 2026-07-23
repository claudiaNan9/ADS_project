import os
import pickle
import argparse
import bz2
import time

class Graph:

    def __init__(self, directed=False):

        self.adjacency_list = {}  # il grafo sarà un dizionario di dizionari: {nodo: {vicino: peso}} (non usiamo defaultdict per avere più controllo)
        self.directed = directed  # default è False, quindi il grafo è non orientato

## Converte l'identificatore del nodo AS che è una stringa in un intero.

    def _convert_node(self, node):

        try:
            return int(node)
        except (TypeError, ValueError):
            raise ValueError(f"Node {node} is not a valid integer identifier.")

## Definisce come stampare il grafo in modo leggibile

    def __repr__(self):
        graph_str = ""
        for node, neighbors in self.adjacency_list.items():
            graph_str += f" Node {node}: Neighbors and weights {neighbors} \n"
        return graph_str

## Aggiunge un nodo al grafo. Se il nodo esiste già, solleva un'eccezione.

    def add_node(self, node):
        node = self._convert_node(node)

        if node not in self.adjacency_list:
            self.adjacency_list[node] = {}  # aggiunge il nodo con un dizionario (lista di adiacenza e pesi) vuoto
        else:
            raise ValueError(f"Node {node} already exists in the graph.")

## Rimuove un nodo dal grafo. Se il nodo non esiste, solleva un'eccezione.

    def remove_node(self, node):
        node = self._convert_node(node)

        if node not in self.adjacency_list:
            raise ValueError(f"Node {node} does not exist in the graph.")

        for neighbors in self.adjacency_list.values(): ## rimuove il nodo da tutte le liste di adiacenza dei vicini
            neighbors.pop(node, None)

        del self.adjacency_list[node]

## Aggiunge un arco al grafo. Questo arco può essere arbitrario e non proveniente dai cammini BGP (il suo peso sarà None o specificato arbitrariamente dall'utente)

    def add_edge(self, from_node, to_node, weight=None):
        

        #from_node = self._convert_node(from_node) ##ridondanti, lo fa già add_node
        #to_node = self._convert_node(to_node)

        if from_node == to_node:  # elimina i self-loop
            return

        if from_node not in self.adjacency_list:
            self.add_node(from_node)

        if to_node not in self.adjacency_list:
            self.add_node(to_node)

      
        self.adjacency_list[from_node][to_node] = weight

        if not self.directed: ## aggiunge arco in entrambe le direzioni se è undirected
                self.adjacency_list[to_node][from_node] = weight
    
## Rimuove un arco dal grafo. Se i nodi A e B non esistono o se l'arco stesso non esiste (magari i nodi sì ma non sono collegati) lancia un errore.

    def remove_edge(self, from_node, to_node):

        from_node = self._convert_node(from_node)
        to_node = self._convert_node(to_node)

        if from_node not in self.adjacency_list:
            raise ValueError(
                f"Node {from_node} does not exist in the graph."
            )

        if to_node not in self.adjacency_list:
            raise ValueError(
                f"Node {to_node} does not exist in the graph."
            )

        if to_node not in self.adjacency_list[from_node]:
            raise ValueError(
                f"Edge ({from_node}, {to_node}) does not exist in the graph."
            )

        del self.adjacency_list[from_node][to_node]

        if not self.directed:  ## elimina anche l'arco inverso 
            if from_node in self.adjacency_list.get(to_node, {}): ## fa un check se esiste (non dovrebbe servire teoricamente)
                del self.adjacency_list[to_node][from_node]


## Aggiorna la frequenza degli archi

    def update_frequency(self, from_node, to_node):

        from_node = self._convert_node(from_node)
        to_node = self._convert_node(to_node)

        if from_node == to_node:  # elimina i self-loop
            return
        
        ## ho il dubbio che non sia giusto crearli, vediamo

        if from_node not in self.adjacency_list:
            self.add_node(from_node)

        if to_node not in self.adjacency_list:
            self.add_node(to_node)

        #legge la frequenza attuale con .get(...); se l’arco ancora non esiste restituisce 0 come frequenza iniziale e poi aggiunge 1 
        # assegna il nuovo valore a self.adjacency_list[from_node][to_node].

        self.adjacency_list[from_node][to_node] = (                      
            self.adjacency_list[from_node].get(to_node, 0) + 1
        )

        if not self.directed:
            self.adjacency_list[to_node][from_node] = (
                self.adjacency_list[to_node].get(from_node, 0) + 1
            )
    
    def get_neighbors(self, node):
        node = self._convert_node(node)

        if node in self.adjacency_list:
            return self.adjacency_list[node]
        else:
            raise ValueError(f"Node {node} does not exist in the graph.")

    def has_node(self, node):
        node = self._convert_node(node)
        return node in self.adjacency_list

    def has_edge(self, from_node, to_node):
        from_node = self._convert_node(from_node)
        to_node = self._convert_node(to_node)

        if from_node in self.adjacency_list:
            return to_node in self.adjacency_list[from_node]

        return False

    def get_nodes(self):
        return list(self.adjacency_list.keys())

    def get_edges(self):
        edges = []
        seen = set()

        for from_node, neighbors in self.adjacency_list.items():
            for to_node, weight in neighbors.items():

                if not self.directed:
                    arco = (min(from_node, to_node), max(from_node, to_node)) ## prende una unica entry tra (2,3) (3,2)

                    if arco not in seen:
                        seen.add(arco)
                        edges.append((from_node, to_node, weight))

        return edges

    def delete_consecutive_duplicates(self, path): # per esempio path = [10, 10, 20] , conserva solo il primo 10 e 20
        return [
            path[i]
            for i in range(len(path))
            if i == 0 or path[i] != path[i - 1]
        ]

    def add_bgp_path(self, path):
        # converte tutti gli identificatori AS in interi
        path = [self._convert_node(node) for node in path]

        path = self.delete_consecutive_duplicates(path)

        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]

            if u == v:  # elimina i self-loop
                continue

            if not self.has_node(u):
                self.add_node(u)

            if not self.has_node(v):
                self.add_node(v)

            self.update_frequency(u, v)
    

    def largest_connected_component(self):  # Cerchiamo la componente connessa più grande tramite una DFS iterativa.

        visited = set() # nodi già visti

        largest_component = set() # insieme che conterrà i nodi della componente connessa più grande trovata fino a questo momento

        for start_node in self.adjacency_list:

            if start_node in visited:
                continue
                # Saltiamo il resto dell'iterazione e passiamo al nodo successivo se é stato già visto

            component = set() # insieme che conterrà i nodi della componente che stiamo esplorando in questo momento.

            stack = [start_node]
            # Pila utilizzata per eseguire la DFS.
            # Inizialmente contiene solo il nodo di partenza.

            visited.add(start_node)

            while stack:
                # Continuiamo la visita finché ci sono nodi nella pila.

                node = stack.pop()
                # Estraiamo l'ultimo nodo inserito nella pila.
                # Questo comportamento LIFO realizza una DFS.

                component.add(node)
                # Aggiungiamo il nodo alla componente connessa corrente.

                for neighbor in self.adjacency_list[node]:
                    # Scorriamo tutti i vicini del nodo.
                    # Il dizionario interno ha la forma:
                    # {vicino: peso}
                    # Qui vengono considerate solo le chiavi, cioè i vicini.
                    # I pesi non servono per trovare le componenti connesse.

                    if neighbor not in visited:
                        # Consideriamo solo i vicini
                        # che non sono ancora stati visitati.

                        visited.add(neighbor)
                        # Segniamo il vicino come visitato.

                        stack.append(neighbor)
                        # Inseriamo il vicino nella pila,
                        # così verrà esplorato successivamente.

            if len(component) > len(largest_component):
                # Quando la DFS termina, abbiamo trovato
                # un'intera componente connessa.
                # Confrontiamo il suo numero di nodi
                # con quello della componente più grande trovata finora.

                largest_component = component
                # Se la componente corrente è più grande,
                # la salviamo come nuova componente più grande.

        return largest_component
        # Restituiamo l'insieme dei nodi appartenenti
        # alla componente connessa più grande.


    def get_largest_connected_subgraph(self):
        # Troviamo i nodi appartenenti
        # alla componente connessa più grande.

        component_nodes = self.largest_connected_component()

        # Creiamo un nuovo oggetto Graph.
        # Il nuovo grafo mantiene la stessa proprietà del grafo originale:
        # orientato se self.directed è True,
        # non orientato se self.directed è False.

        subgraph = Graph(directed=self.directed)

        for node in component_nodes:
            # Scorriamo tutti i nodi della componente più grande.

            subgraph.add_node(node)
            # Aggiungiamo ogni nodo al nuovo sottografo.
            # In questa fase ogni nodo viene creato
            # con un dizionario dei vicini inizialmente vuoto.

        for from_node in component_nodes:
            # Scorriamo nuovamente tutti i nodi
            # della componente connessa più grande.

            for to_node, weight in self.adjacency_list[from_node].items():
                # Per ogni nodo, scorriamo tutti i suoi vicini
                # e i relativi pesi nel grafo originale.

                if to_node in component_nodes:
                    # Copiamo l'arco soltanto se anche il vicino
                    # appartiene alla componente connessa più grande.

                    subgraph.adjacency_list[from_node][to_node] = weight
                    # Copiamo direttamente l'arco e il suo peso.
                    # Il peso non viene modificato né ricalcolato:
                    # resta uguale a quello presente nel grafo originale.

        return subgraph
        # Restituiamo un nuovo oggetto Graph contenente soltanto
        # la componente connessa più grande.
        # Il grafo originale non viene modificato.

    @staticmethod
    def load_paths(filepath_bz2=None, filepath_pkl=None, max_paths=None):
        
        if filepath_bz2:
            # legge direttamente dal bz2 fermandosi a max_paths
            cammini = []
            contatore = 0
            with bz2.open(filepath_bz2, "rt") as f:
                for riga in f:
                    if contatore >= max_paths:
                        break
                    if riga.startswith("#"):
                        continue
                    parti = riga.strip().split()
                    cammino = []
                    for p in parti[1:]:
                        if "/" in p or "." in p or ":" in p:
                            break
                        nodi = p.split("|")
                        cammino.extend(nodi)
                    if len(cammino) > 1:
                        cammini.append(cammino)
                        contatore += 1
            print(f"cammini letti: {contatore}")
            return cammini
        else:
            # carica tutto dal pickle
            with open(filepath_pkl, "rb") as f:
                return pickle.load(f)

    def build_from_bz2(self, filepath, max_paths=None):

        contatore = 0
        with bz2.open(filepath, "rt") as f:
            for riga in f:
                if max_paths and contatore >= max_paths:
                    break
                if riga.startswith("#"):
                    continue
                parti = riga.strip().split()
                cammino = []
                for p in parti[1:]:
                    if "/" in p or "." in p or ":" in p:
                        break
                    nodi = p.split("|")
                    cammino.extend(nodi)
                if len(cammino) > 1:
                    self.add_bgp_path(cammino)
                    contatore += 1
        print(f"cammini letti: {contatore}")

    def build_from_paths(self, paths):
        for path in paths:
            self.add_bgp_path(path)

    def save_graph(self, filepath):

        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load_graph(filepath):

        with open(filepath, "rb") as f:
            return pickle.load(f)


import time

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_paths", type=int, default=None)
    args = parser.parse_args()

    graph_path = "/code/ADSproject/data/grafo.pkl"
    largest_path = "/code/ADSproject/data/grafo_largest.pkl"

    if args.max_paths:
        graph_path = "/code/ADSproject/data/grafo_test.pkl"
        largest_path = "/code/ADSproject/data/grafo_largest_test.pkl"

    if os.path.exists(largest_path):
        grafo = Graph.load_graph(largest_path)
    else:
        if os.path.exists(graph_path):
            grafo = Graph.load_graph(graph_path)
        else:
            grafo = Graph(directed=False)
            
            inizio = time.time()
            grafo.build_from_bz2(
                "/code/ADSproject/data/20110501.all-paths.bz2",
                max_paths=args.max_paths
            )
            fine = time.time()
            print(f"tempo costruzione grafo: {fine - inizio:.2f} secondi")
            
            grafo.save_graph(graph_path)

        inizio = time.time()
        grafo = grafo.get_largest_connected_subgraph()
        fine = time.time()
        print(f"tempo largest component: {fine - inizio:.2f} secondi")
        
        grafo.save_graph(largest_path)

    print(f"nodi: {len(grafo.get_nodes())}")
    print(f"archi: {len(grafo.get_edges())}")
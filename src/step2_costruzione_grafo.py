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

    # la barretta davanti indica un metodo interno della classe
    def _convert_node(self, node):

        try:
            return int(node)
        except (TypeError, ValueError):
            raise ValueError(f"Node {node} is not a valid integer identifier.")
        

## Definisce come stampare il grafo in modo leggibile

    def __repr__(self):
        lines = [
            f" Node {node}: Neighbors and weights {neighbors} "
            for node, neighbors in self.adjacency_list.items()
        ]
        return "\n".join(lines) + ("\n" if lines else "")


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
        
        from_node = self._convert_node(from_node) 
        to_node = self._convert_node(to_node)

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

        # if from_node not in self.adjacency_list:
        #     self.add_node(from_node)

        # if to_node not in self.adjacency_list:
        #     self.add_node(to_node)

        # update: non li creo perchè vengono già creati in add_bgp_path se non esistono, quindi qui mi limito a mettere un check e ad aggiornare la frequenza 

        if from_node not in self.adjacency_list:
            raise ValueError(f"Node {from_node} does not exist in the graph.")

        if to_node not in self.adjacency_list:
            raise ValueError(f"Node {to_node} does not exist in the graph.")
    
        #legge la frequenza attuale con .get(...); se l’arco ancora non esiste restituisce 0 come frequenza iniziale e poi aggiunge 1 
        # assegna il nuovo valore a self.adjacency_list[from_node][to_node].

        self.adjacency_list[from_node][to_node] = (                      
            self.adjacency_list[from_node].get(to_node, 0) + 1
        )

        if not self.directed:
            self.adjacency_list[to_node][from_node] = (
                self.adjacency_list[to_node].get(from_node, 0) + 1
            )


## Restituisce i vicini 

    
    def get_neighbors(self, node):
        node = self._convert_node(node)

        if node in self.adjacency_list:
            return self.adjacency_list[node]
        else:
            raise ValueError(f"Node {node} does not exist in the graph.")

## Controlla se un nodo esiste 

    def has_node(self, node):
        node = self._convert_node(node)
        return node in self.adjacency_list


## Controlla se un arco esiste 

    def has_edge(self, from_node, to_node):
        from_node = self._convert_node(from_node)
        to_node = self._convert_node(to_node)

        if from_node in self.adjacency_list:
            return to_node in self.adjacency_list[from_node]

        return False

## Restituisce i nodi 

    def get_nodes(self):
        return list(self.adjacency_list.keys())

## Restituisce gli archi nella forma [(from_node,to_node,frequenza)]. 

    def get_edges(self):
        edges = []

        if not self.directed:
            seen = set() 
            for from_node, neighbors in self.adjacency_list.items():
                for to_node, weight in neighbors.items():
                    arco = (min(from_node, to_node), max(from_node, to_node)) ## prende una unica entry tra (2,3) (3,2)
                    if arco not in seen:
                        seen.add(arco)
                        edges.append((from_node, to_node, weight))
        else:
            for from_node, neighbors in self.adjacency_list.items():  # grafo orientato, ci servono entrambi
                for to_node, weight in neighbors.items():
                    edges.append((from_node, to_node, weight))

        return edges

## Elimina i duplicati consecutivi nei cammini BGP. Per esempio path = [10, 10, 20] , conserva solo il primo 10 e 20

    def delete_consecutive_duplicates(self, path): 
        return [
            path[i]
            for i in range(len(path))
            if i == 0 or path[i] != path[i - 1]
        ]

## Aggiunge gli archi dai cammini BGP e aggiorna la frequenza

    def add_bgp_path(self, path):

        # converte tutti gli identificatori AS in interi
        path = [self._convert_node(node) for node in path]

        path = self.delete_consecutive_duplicates(path)

        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]

            if u == v:  # elimina i self-loop
                continue

            # se non esistono li crea 
            if not self.has_node(u):
                self.add_node(u)

            if not self.has_node(v):
                self.add_node(v)

            # aggiorna la frequenza 
            self.update_frequency(u, v)
    

## Cerca la componente connessa più grande nel grafo tramite una DFS (restituisce i nodi che appartengono alla componente connessa più grande)

    def largest_connected_component(self):  # Cerchiamo la componente connessa più grande tramite una DFS iterativa.

        visited = set() # nodi già visti

        largest_component = set() # insieme che conterrà i nodi della componente connessa più grande trovata fino a questo momento

        for start_node in self.adjacency_list:

            if start_node in visited:
                continue
                # passiamo al nodo successivo se é stato già visto

            component = set() # insieme che conterrà i nodi della componente che stiamo esplorando in questo momento.

            stack = [start_node] # stack utilizzato per eseguire la DFS, inizialmente contiene solo il nodo di partenza

            visited.add(start_node)

            while stack: # continuiamo la visita finché ci sono nodi nella pila

                node = stack.pop() # estraiamo l'ultimo nodo inserito nella pila (lifo)

                component.add(node) # aggiungiamo il nodo alla componente connessa corrente

                # scorriamo tutti i vicini del nodo. Il dizionario interno ha la forma: {vicino: peso}
                # qui vengono considerate solo le chiavi, cioè i vicini (perchè i pesi non servono per trovare le componenti connesse) 
                
                for neighbor in self.adjacency_list[node]:
                    
                    if neighbor not in visited:

                        # aggiungiamo 
                        visited.add(neighbor) 
                        stack.append(neighbor) 

            if len(component) > len(largest_component): # quando la DFS termina, abbiamo trovato un'intera componente connessa

                largest_component = component # confrontiamo il numero di nodi, se è più grande aggiorniamo la componente a quella più grande

        return largest_component # insieme di nodi della componente

## Costruisce il grafo della componente connessa più grande 

    def get_largest_connected_subgraph(self):

        component_nodes = self.largest_connected_component() # troviamo i nodi

        subgraph = Graph(directed=self.directed)    # creiamo un nuovo oggetto Graph

        for node in component_nodes:

            subgraph.add_node(node) # aggiunge ogni nodo, che viene creato con un dizionario di vicini vuoto

        for from_node in component_nodes:

            for to_node, weight in self.adjacency_list[from_node].items(): # per ogni nodo, scorriamo tutti i suoi vicini e i relativi pesi nel grafo originale

                if to_node in component_nodes: # copiamo l'arco soltanto se anche il vicino appartiene alla componente connessa più grande (dovrebbe di default)

                    subgraph.adjacency_list[from_node][to_node] = weight # copiamo direttamente l'arco e il suo peso. Il peso resta uguale a quello presente nel grafo originale.

        return subgraph


## Carica i paths in due modalità, o dal file bz2 e dal file pkl 
## Nota: il codice della lettura bz2 è ridondante nei due metodi ma in load_paths restituisce solo i cammini, nell'altra costruzione il grafo a partire dai cammini. 
## Magari si può creare una funzione a sè stante che itera sul file e viene invocata in entrambi 

    @staticmethod
    def load_paths(filepath_bz2=None, filepath_pkl=None, max_paths=None):
        
        if filepath_bz2:
            # legge direttamente dal bz2 (eventualmente fermandosi a max_paths)
            cammini = []
            contatore = 0
            with bz2.open(filepath_bz2, "rt") as f:
                for riga in f:
                    if max_paths is not None and contatore >= max_paths:
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
                if max_paths is not None and contatore >= max_paths:
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
                    self.add_bgp_path(cammino) ## aggiunta dei cammini 
                    contatore += 1
        print(f"cammini letti: {contatore}")

## Itera sui cammini e costruisce il grafo (puo farlo sia da file pkl che da bz2, basta passargli i cammini)

    def build_from_paths(self, paths):
        for path in paths:
            self.add_bgp_path(path)

## Salva il grafo in un file pkl 

    def save_graph(self, filepath):

        with open(filepath, "wb") as f:
            pickle.dump(self, f)

## Carica il file in memoria 

    @staticmethod
    def load_graph(filepath):

        with open(filepath, "rb") as f:
            return pickle.load(f)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_paths", type=int, default=None)
    parser.add_argument("--source", type=str, default="bz2", choices=["bz2", "pkl"],
                        help="Sorgente dei cammini: bz2 (default) o pkl")
    args = parser.parse_args()

    BZ2_PATH = "/code/ADSproject/data/20110501.all-paths.bz2"
    
    #PKL_PATH = "/code/ADSproject/data/cammini_test.pkl" ## quello da un milione lo utilizziamo per testing

    PKL_PATH = "/code/ADSproject/data/cammini.pkl" ## quello intero

    graph_path = "/code/ADSproject/data/grafo.pkl"
    largest_path = "/code/ADSproject/data/grafo_largest_component.pkl"

    if args.max_paths:
        graph_path = "/code/ADSproject/data/grafo_test.pkl"
        largest_path = "/code/ADSproject/data/grafo_largest_test.pkl"

    if os.path.exists(largest_path):
        print("carico il grafo largest dal pickle...")
        grafo = Graph.load_graph(largest_path)
    else:
        if os.path.exists(graph_path):
            print("carico il grafo dal pickle...")
            grafo = Graph.load_graph(graph_path)
        else:
            grafo = Graph(directed=False)

            if args.source == "bz2":
                print(f"costruisco il grafo dal bz2 (max_paths={args.max_paths})...")
                inizio = time.time()
                grafo.build_from_bz2(BZ2_PATH, max_paths=args.max_paths)
                fine = time.time()
                print(f"tempo costruzione grafo da bz2: {fine - inizio:.2f} secondi")

            else:  # pkl
                print(f"carico i cammini dal pkl (max_paths={args.max_paths})...")
                inizio = time.time()
                cammini = Graph.load_paths(filepath_pkl=PKL_PATH)
                fine = time.time()
                print(f"tempo caricamento pkl: {fine - inizio:.2f} secondi")

                if args.max_paths:
                    cammini = cammini[:args.max_paths]

                inizio = time.time()
                grafo.build_from_paths(cammini)
                fine = time.time()
                print(f"tempo costruzione grafo da pkl: {fine - inizio:.2f} secondi")

            grafo.save_graph(graph_path)

        inizio = time.time()
        grafo = grafo.get_largest_connected_subgraph()
        fine = time.time()
        print(f"tempo largest component: {fine - inizio:.2f} secondi")
        grafo.save_graph(largest_path)

    print(f"\nnodi: {len(grafo.get_nodes())}")
    print(f"archi: {len(grafo.get_edges())}")
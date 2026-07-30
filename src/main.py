import argparse
import os
import random
import time

from step2_costruzione_grafo import Graph
from step3_ricerca_cammini_minimax import kruskal, minimax_query_dfs

""" Punto di ingresso del programma: esegue l'intera pipeline

    1. Costruisce il grafo AS a partire dai cammini BGP (dal file bz2 o da un pkl già
       estratto), riusando i pickle già salvati su disco quando disponibili.
    2. Ne estrae la componente connessa più grande.
    3. Costruisce l'MST con Kruskal.
    4. Risponde a una query minimax (start, target) passata da riga di comando, oppure richiesta interattivamente se non fornita.

    Uso: python src/main.py --max_paths N --source bz2|pkl --start U --target V """


BZ2_PATH = "/code/ADSproject/data/20110501.all-paths.bz2"
PKL_PATH = "/code/ADSproject/data/cammini.pkl"
GRAPH_PATH = "/code/ADSproject/data/grafo.pkl"
LARGEST_PATH = "/code/ADSproject/data/grafo_largest_component.pkl"


def costruisci_grafo(max_paths=None, source="pkl"):

    if max_paths:
        graph_path = f"/code/ADSproject/data/grafo_test_{max_paths}.pkl"
        largest_path = f"/code/ADSproject/data/grafo_largest_test_{max_paths}.pkl"
    else:
        graph_path = GRAPH_PATH
        largest_path = LARGEST_PATH

    if os.path.exists(largest_path):
        print("carico il grafo largest dal file pickle...")
        return Graph.load_graph(largest_path)

    if os.path.exists(graph_path):
        print("carico il grafo dal file pickle...")
        grafo = Graph.load_graph(graph_path)
    else:
        grafo = Graph(directed=False)

        if source == "bz2":
            print(f"costruisco il grafo dal bz2 (max_paths={max_paths})...")
            grafo.build_from_bz2(BZ2_PATH, max_paths=max_paths)
        else:
            print(f"carico i cammini dal pkl (max_paths={max_paths})...")
            cammini = Graph.load_paths(filepath_pkl=PKL_PATH)
            if max_paths:
                cammini = cammini[:max_paths]
            grafo.build_from_paths(cammini)

        grafo.save_graph(graph_path)

    grafo = grafo.get_largest_connected_subgraph()
    grafo.save_graph(largest_path)
    return grafo


def main():

    parser = argparse.ArgumentParser(
        description="Pipeline completa: costruzione grafo AS, MST (Kruskal) e query minimax."
    )
    parser.add_argument("--max_paths", type=int, default=None,
                         help="Limita il numero di cammini letti (utile per test)")
    parser.add_argument("--source", type=str, default="pkl", choices=["bz2", "pkl"],
                         help="Sorgente dei cammini: pkl (default) o bz2")
    parser.add_argument("--start", type=int, default=None, help="Nodo di partenza della query minimax")
    parser.add_argument("--target", type=int, default=None, help="Nodo di destinazione della query minimax")
    args = parser.parse_args()

    inizio = time.time()

    grafo = costruisci_grafo(max_paths=args.max_paths, source=args.source)
    print(f"\nnodi: {len(grafo.get_nodes())}")
    print(f"archi: {len(grafo.get_edges())}")

    print("\ncostruzione MST con Kruskal...")
    mst, mst_weight = kruskal(grafo)
    print(f"peso totale MST: {mst_weight}")
    print(f"nodi MST: {len(mst.get_nodes())}")
    print(f"archi MST: {len(mst.get_edges())}")

    start, target = args.start, args.target
    if start is None or target is None:
        try:
            start = int(input("\nNodo di partenza (start): "))
            target = int(input("Nodo di destinazione (target): "))
        except (ValueError, EOFError):
            print("\nQuery non fornita, termino senza rispondere alla query minimax.")
            return

    nodi_mancanti = [n for n in (start, target) if not mst.has_node(n)]
    if nodi_mancanti:
        esempi = random.sample(mst.get_nodes(), min(5, len(mst.get_nodes())))
        print(f"\nErrore: nodo/i {nodi_mancanti} non presente/i nell'MST.")
        print(f"Alcuni nodi validi di esempio: {esempi}")
        return

    costo, cammino, pesi = minimax_query_dfs(mst, start, target)

    print(f"\nQuery minimax da {start} a {target}:")
    print(f"Costo: {costo}")
    print(f"Cammino: {cammino}")
    print(f"Pesi attraversati: {pesi}")

    fine = time.time()
    print(f"\nTempo totale pipeline: {fine - inizio:.2f} secondi")


if __name__ == "__main__":
    main()

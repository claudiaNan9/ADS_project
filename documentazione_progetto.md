# Progetto ASD – Cammini Minimax su Grafo AS

## Descrizione generale

Questo progetto ha l'obiettivo di implementare strutture dati ed algoritmi per risolvere il problema di cammino minimax su grafi. In particolare, vogliamo rispondere a query di cammino minimax su un grafo di Autonomous Systems (AS), costruito a partire da dati BGP reali.

Quindi, dato un grafo non orientato pesato G = (V, E), dove:
- ogni nodo rappresenta un Autonomous System (AS)
- ogni arco rappresenta una relazione di adiacenza osservata nei cammini BGP
- il peso di un arco è la sua frequenza con cui l'arco compare nei cammini BGP

La query a cui dobbiamo rispondere è del tipo: dati due nodi u e v, trovare il costo del cammino minimax ottimo da u a v, dove il costo di un cammino è il massimo peso tra gli archi attraversati.

## Dati

I dati provengono da due sorgenti:
- `*.all-paths.bz2` (RIPE/RouteViews): cammini BGP reali osservati, usati per calcolare le frequenze degli archi
- `*.as-rel.txt.bz2` (CAIDA): relazioni tra AS, usate per verificare la struttura del grafo

## Architettura

Il progetto puó essere organizzato idealmente nei seguenti script che svolgono i compiti necessari.

### 1. `parser` – Caricamento dei dataset
Legge i file `.bz2` e ne estrae le informazioni.
- Dal file `all-paths`: estrae i cammini BGP e aggiorna le frequenze degli archi
- Dal file `as-rel`: carica le relazioni tra AS 

### 2. `grafo` – Costruzione del grafo
Costruisce il grafo non orientato pesato G = (V, E) a partire dai cammini BGP.
- Struttura dati: liste di adiacenza implementate come vector per rappresentare il grafo
- Funzioni di gestione del grafo 

### 3. `minimum spanning tree` – Costruzione del Minimum Spanning Tree
Implementa l'algoritmo di Kruskal per costruire il MST del grafo.
- Union-Find per il rilevamento efficiente dei cicli
- Il MST è la struttura su cui vengono eseguite le query minimax

### 4. `query/ricerca` – Ricerca del cammino minimax
Data una coppia di nodi (u, v), trova il cammino minimax ottimo sul MST tramite DFS/BFS.
- Input: due nodi u e v
- Output: costo ottimo minimax e cammino corrispondente

### 5. `analisi` – Analisi sperimentale
Raccoglie e riporta le statistiche sperimentali:
- numero di nodi e archi del grafo
- distribuzione delle frequenze sugli archi
- costo ottimo per coppie di nodi campione
- tempi di esecuzione degli algoritmi

## Struttura del repository

```
progetto-as/
├── data/           # file .bz2 scaricati (non inclusi nel repository perchè troppo pesanti, verrà indicato il file corrispondente)
├── src/
│   ├── parser.py   # caricamento e parsing dei dataset
│   ├── grafo.py    # costruzione del grafo AS
│   ├── mst.py      # algoritmo di Kruskal + Union-Find
│   ├── query.py    # ricerca cammini minimax
│   └── analisi.py  # analisi sperimentale
── notebooks/       # jupyter notebook di prova per capire/visualizzare alcuni passaggi 
├── main.py         # punto di ingresso del programma
└── documentazione_progetto.md       # documento di progettazione delle varie fasi e delle scelte di implementazione
```

Il primo step è capire come sono fatti i file e ispezionare i dati, questi passaggi di verifica verranno fatti in appositi notebooks. In notebooks/inspect_data.ipynb apriamo i file per vedere come sono fatti dentro e stampare qualcosa. 

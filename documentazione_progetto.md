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
- Funzioni di gestione del grafo e degli archi

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

## Procedimento

Il primo step è capire come sono fatti i file e ispezionare i dati, questi passaggi di verifica verranno fatti in appositi notebooks. In notebooks/inspect_data.ipynb apriamo i file per vedere come sono fatti dentro e stampare qualcosa. 

Il risultato di questa fase di ispezione è lo script: step1_parser_cammini.py, che estrae dal file all paths i cammini BGP. Nello specifico, rimuove le parti inutili della stringa del tipo: routeviews/isc|5 4436|6762|21826 200.82.128.0/24 i 198.32.176.13 e restituisce solo la lista di nodi corrispondente. L'output dello script è un file pkl dove vengono salvati tutti i cammini (lista di liste).

Lo step successivo sarà estrarre da queste liste gli archi e le loro frequenze per la costruzione del grafo. Una possibile successione di passaggi potrebbe essere:
- estrazione degli archi e conteggio delle frequenze (struttura defaultdict di python): questa operazione dovrà gestire i self loop e la frequenza di archi uguali (1,2 e 2,1 ad esempio). Una soluzione semplice è stata testata in inspect_data, vediamo come adattarla alla fase successiva di costruzione del grafo.

Inspect_data riflette il flusso seguito a partire dai cammini estratti. Le frequenze sono state estrapolate e salvate come frequenze = defaultdict(int) 
(la differenza tra dict e defaultdict è che in defaultdict si può definire un caso di default e il tipo che prendono i valori, in questo caso int della frequenza. Se si fa frequenze[0] non dà key error perchè la chiave non esiste ma la crea di default con chiave 0 e valore 0). 

Poi ho provato da frequenze a costruire il grafo considerandolo come un dizionario di dizionari, dove la chiave è il nodo e il valore è un dizionario contenente i vicini e il peso (frequenza). Il risultato è del tipo: {4436: {6762: 1, 701: 1, 2914: 1} ..}. 

Partendo da questi tentativi possiamo abbozzare una classe Graph (fatta nel notebook ma da rifinire per lo script), con le seguenti funzioni generali:
- inizializza la struttura dati come dizionario di dizionari (liste di adiacenza)
- inserimento/rimozione di: nodi e archi 
- controlli vari (ha un nodo/arco)
- legge i nodi/archi e li restituisce
- converte gli ID AS in interi (sono stringhe). Decido di non trasformali in interi consecutivi perchè in Python stiamo usando i dizionari che non hanno problemi con valori sparsi e la differenza in efficienza non dovrebbe esserci (aveva senso trasformarli in c++ credo usando vector per accedere alle posizioni?)

poi ci sono le funzioni dedicate al fatto che stiamo leggendo direttamente i percorsi BGP quindi creiamo il grafo sulla base di quello. 
- aggiungere i percorsi 
- aggiornare la frequenza 
- trovare la componente connessa più grande (tramite DFS)

Questa fase di esplorazione ha portato alla costruzione della classe Graph implementata nello script step2_costruzione_grafo.py

## Modulo: Graph (costruzione_grafo.py) (prima bozza)

Classe che permette di creare un oggetto grafo non orientato e pesato, che implementa funzionalità di gestione generale e di costruzione attraverso la lettura di cammini BGP. Di seguito le specifiche.

### Input:
Sequenza di cammini BGP letti dal file cammini.pkl, che è stato generato dallo script dello step1. In realtà lo script di prova (script2.py) prevede anche la possibilità di leggere i cammini direttamente dal file bz2, ma una analisi di test ha prodotto tempi leggermente ridotti per il file pkl.
| Approccio | Tempo caricamento | Tempo costruzione grafo | Tempo largest component | Totale |
|---|---|---|---|---|
| bz2 | — | 7.86s | 0.08s | 7.94s |
| pkl | 0.61s | 4.32s | 0.08s | 5.01s |
Il pkl risulta più veloce perché il parsing del testo è già stato effettuato nello step1 e il file serializzato può essere deserializzato direttamente senza ulteriori elaborazioni.
(TO DO: decidere se mantenere il file di prova che permette di usare entrambe le possibilità o no).

### Output:
Lo script restituisce due file: 
- grafo.pkl: rappresenta l'intero grafo. 
- grafo_largest_component.pkl: rappresenta la componente connessa più grande del grafo.

### Strutture dati: 
Il grafo viene rappresentato come un dizionario di dizionari (dict) dove la chiave del dizionario esterno è un nodo AS e il dizionario interno è la sua lista di adiacenza pesata. Il risultato è del tipo: `{4436: {6762: 1, 701: 1, 2914: 1}, ...}`.

Gli identificatori AS sono convertiti da stringhe a interi tramite `_convert_node` — si è scelto di non mapparli in interi consecutivi perché in Python i dizionari non hanno problemi con valori sparsi, a differenza del C++ dove si usano i `vector` che richiedono indici consecutivi.

### Funzioni generali sul grafo:

- **`_convert_node(node)`**: converte l'identificatore AS da stringa a intero.
- **`add_node(node)`**: aggiunge un nodo con lista di adiacenza vuota. Solleva `ValueError` se esiste già. 
- **`remove_node(node)`**: rimuove il nodo e tutti i suoi archi dai vicini.
- **`add_edge(from_node, to_node, weight=None)`**: aggiunge un arco non orientato arbitrario con peso opzionale specificato dall'utente. I self-loop vengono ignorati. 
- **`remove_edge(from_node, to_node)`**: rimuove un arco in entrambe le direzioni. Solleva `ValueError` se il nodo o l'arco non esistono. 
- **`update_frequency(from_node, to_node)`**: aggiunge i nodi se non esistono, poi incrementa il peso dell'arco di 1 in entrambe le direzioni. Gestisce i self-loop.
- **`get_neighbors(node)`**: restituisce il dizionario dei vicini di un nodo con i relativi pesi. 
- **`has_node(node)`**: verifica se un nodo esiste. 
- **`has_edge(from_node, to_node)`**: verifica se un arco esiste. 
- **`get_nodes()`**: restituisce la lista di tutti i nodi. 
- **`get_edges()`**: restituisce la lista di tutti gli archi senza duplicati (u,v) e (v,u).
- **`delete_consecutive_duplicates(path)`**: rimuove i nodi ripetuti consecutivamente in un cammino, es. `[10, 10, 20]` → `[10, 20]`. 

### Funzioni dedicate alla costruzione del grafo dai cammini BGP:

- **`add_bgp_path(path)`**: converte gli AS in interi, elimina i duplicati consecutivi, poi per ogni coppia consecutiva chiama `update_frequency`. Costruisce il grafo dinamicamente. 
- **`build_from_paths(paths)`**: itera su una lista di cammini già caricati in memoria e chiama `add_bgp_path` per ognuno. 
- **`build_from_bz2(filepath, max_paths=None)`**: legge il file bz2 riga per riga, fa il parsing e chiama `add_bgp_path` direttamente senza caricare tutto in memoria. 
- **`load_paths(filepath_bz2, filepath_pkl, max_paths)`**: metodo statico che carica i cammini dal bz2 (con limite opzionale) o dal pkl.
- **`save_graph(filepath)`**: serializza il grafo in un file pickle. 
- **`load_graph(filepath)`**: metodo statico che deserializza il grafo da un file pickle.

### Funzioni per la componente connessa:

- **`largest_connected_component()`**: trova la componente connessa più grande tramite DFS iterativa. 
- **`get_largest_connected_subgraph()`**: restituisce un nuovo oggetto `Graph` contenente solo i nodi e gli archi della componente connessa più grande. Il grafo originale non viene modificato.




# Progetto ASD 2026 – Ricerca Cammini Minimax su Grafo Autonomous Systems

## Descrizione generale

Questo progetto ha l'obiettivo di implementare strutture dati ed algoritmi per risolvere il problema di cammino minimax su grafi. In particolare, vogliamo rispondere a query di ricerca del cammino minimax su un grafo di Autonomous Systems (AS), costruito a partire da dati BGP reali.

Più precisamente, dato un grafo non orientato pesato G = (V, E), dove:
- ogni nodo rappresenta un Autonomous System (AS);
- ogni arco rappresenta una relazione di adiacenza osservata nei cammini BGP;
- il peso di un arco è la frequenza con cui l'arco compare nei cammini BGP;

La query a cui dobbiamo rispondere è del tipo: dati due nodi u e v, trovare il costo del cammino minimax ottimo da u a v, dove il costo di un cammino è il massimo peso tra gli archi attraversati (si vuole quindi minimizzare il massimo peso attraversato).

## Dati

I dati provengono da due sorgenti:
- `*.all-paths.bz2` (RIPE/RouteViews): cammini BGP reali osservati, usati per calcolare le frequenze degli archi
- `*.as-rel.txt.bz2` (CAIDA): relazioni tra AS, usate per verificare la struttura del grafo

Nello specifico, quelli scelti per lo svolgimento di questo progetto sono: `20110501.all-paths.bz2` e `20110501.as-rel.txt.bz2`.

## Metodologia

Per affrontare il problema è stata scelta la seguente metodologia. 
1. Per prima cosa, il file contenente i cammini BGP viene inizialmente analizzato per estrarre solamente le sequenze di nodi Autonomous System e i relativi cammini, eliminando dati superflui delle righe del dataset. I dati elaborati vengono poi salvati in formato pickle, così da evitare di rileggere ogni volta il file compresso originale. A partire dai cammini viene costruito un grafo pesato e non orientato, in cui ogni nodo rappresenta un AS e ogni arco rappresenta una relazione di adiacenza. Il peso di un arco corrisponde alla frequenza con cui l'arco compare nel dataset dei cammini BGP. Poiché il grafo può essere disconnesso, si considera soltanto la componente connessa più grande, come richiesto dal problema.
2. Per rispondere alle query minimax viene costruito un Minimum Spanning Tree mediante l’algoritmo di Kruskal. Questa scelta deriva dalla proprietà per cui, nel cammino tra due nodi all’interno di un MST, il massimo peso attraversato è minimo rispetto a tutti i possibili cammini tra gli stessi nodi nel grafo originale. Kruskal ordina gli archi per frequenza crescente e li inserisce nell’albero solo se non generano cicli. Per controllare efficientemente la presenza di cicli viene utilizzata una struttura Union-Find con path compression e union by rank.
Nota: Dijkstra non è applicabile al problema del cammino minimax perché non vale la proprietà che un sottocammino di un cammino minimax sia anch'esso ottimo minimax. Per il minimax questa proprietà non vale. Kruskal invece garantisce il cammino minimax ottimo perché aggiunge sempre l'arco più  leggero disponibile. Di conseguenza, il cammino che si forma nell'MST tra due nodi usa automaticamente gli archi più leggeri possibili — minimizzando quindi il massimo peso attraversato. In altre parole, abbiamo automaticamente escluso i percorsi alternativi sapendo che avrebbero avuto un costo maggiore o uguale.
3. Una volta costruito l'MST, ogni query tra due nodi viene risolta tramite una DFS. Poiché l'MST è un albero (grafo connesso senza cicli), tra due nodi esiste un unico 
cammino possibile — quindi la DFS lo trova sempre in modo univoco. Ci verrà restituito un solo cammino minimax, che è uno dei cammini minimax ottimi presenti nel grafo originale (potrebbero esisterne altri con lo stesso costo - traccia 2 opzionale del progetto). Durante la visita si mantiene il massimo peso incontrato: tale valore rappresenta il costo minimax ottimo della query.
4. In ultimo viene effettuata un'analisi sperimentale, raccogliendo statistiche sul dataset e e verificando sperimentalmente le complessità attese degli algoritmi.


## Architettura del progetto 

Il progetto è organizzato nei seguenti script che svolgono task specifici per ogni fase del progetto. Verranno descritti nel dettaglio nelle sezioni successive.

```
progetto-asd/
├── data/           # file .bz2 scaricati (non inclusi nel repository perchè troppo pesanti)
├── src/
│   ├── step1_parser_cammini.py   # caricamento e parsing dei dataset
│   ├── step2_costruzione_grafo.py    # costruzione del grafo AS
│   ├── step3_ricerca_cammini_minimax.py      # algoritmo di Kruskal + Union-Find + DFS per query
│   └── step4_analisi_sperimentale.ipynb  # analisi sperimentale
|── notebooks/       # jupyter notebook di prova per capire/visualizzare alcuni passaggi 
├── main.py         # punto di ingresso del programma
└── documentazione_progetto.md       # documento di progettazione delle varie fasi e delle scelte di implementazione
```

## Procedimento
Di seguito viene illustrato il procedimento seguito e l'implementazione corrispondente per ogni script che abbiamo introdotto nella sezione Architettura del progetto. Ogni step è stato precedentemente testato nel notebook inspect_data.ipynb per capirne meglio il funzionamento. Questo notebook quindi segue il flusso complessivo del progetto.

## Primo step: Parsing dei cammini 

Il primo step è capire come sono fatti i file e ispezionare i dati. In notebooks/inspect_data.ipynb apriamo i file per vedere come sono fatti dentro e stampare le righe che ci interessa analizzare. Il risultato di questa fase di ispezione è lo script: step1_parser_cammini.py, che estrae dal file all paths i cammini BGP. Nello specifico, rimuove le parti inutili della stringa del tipo: routeviews/isc|5 4436|6762|21826 200.82.128.0/24 i 198.32.176.13 e restituisce solo la lista di nodi corrispondente. L'output dello script è un file pkl dove vengono salvati tutti i cammini (lista di liste).

### step1_parser_cammini.py

#### Input

Lo script utilizza come input il file compresso `20110501.all-paths.bz2`. Ogni riga del dataset contiene informazioni sulla sorgente, una sequenza di nodi e alcuni indirizzi di rete. Una riga del dataset è del tipo: `routeviews/isc|5 4436|6762|21826 200.82.128.0/24 i 198.32.176.13` e a noi interessa estrarre soltanto la parte relativi al cammino, ovvero la sequenza di nodi 4436|6762|21826. 
Lo script può essere lanciato col parametro opzionale --max_righe N, dove `N` indica il numero massimo di cammini validi da estrarre. Il limite riguarda i cammini salvati, non necessariamente il numero totale di righe esaminate. Questa opzione è utile per testing.

#### Output

Lo script restituisce una lista di cammini. Ogni cammino è rappresentato come una lista di liste di stringhe contenenti gli identificativi dei nodi:[["4436", "6762", "21826"],["6939", "15290", "2671", "2669"]]. I risultati vengono salvati nei seguenti file: cammini.pkl per l’elaborazione completa di tutti i cammini, oppure cammini_test.pkl quando viene utilizzato il parametro `--max_righe`. Al termine dell’esecuzione vengono stampati il numero totale di cammini e i primi cinque cammini estratti.

#### Funzionalità

La funzione `leggi_cammini` apre il file BZ2 in modalità testuale e lo legge progressivamente. Le righe di commento vengono ignorate.

Per ogni riga, lo script:

1. separa gli elementi tramite gli spazi;
2. ignora il primo elemento, che identifica la sorgente;
3. legge i nodi separati dal carattere `|`;
4. interrompe l’analisi quando incontra indirizzi IP o altri elementi contenenti `/`, `.` oppure `:`;
5. conserva soltanto i cammini formati da almeno due nodi.

La funzione `salva_cammini` restituisce il file pkl, mentre `carica_cammini` ricostruisce la struttura dati da un file pkl già esistente. Prima di analizzare il dataset, lo script controlla quindi se è disponibile una versione precedentemente salvata.

#### Strutture dati

La struttura principale è una lista di liste, cammini: list[list[str]]. La lista esterna contiene tutti i cammini validi. Ogni lista interna contiene, nell’ordine originale, gli identificativi dei nodi AS appartenenti a un singolo cammino.


#### Complessità

La funzione `leggi_cammini` ha complessità lineare O(N), dove N è la lunghezza totale in caratteri del file di input. Per ogni riga vengono eseguite operazioni di parsing (strip, split, extend) che hanno tutte tempo costante O(1), quindi il tempo totale è proporzionale al numero di righe lette. La complessità spaziale è O(C) dove C è il numero totale di cammini estratti, poiché vengono conservati interamente in memoria. Anche le operazioni di salvataggio e caricamento tramite pickle hanno complessità O(C) poiché dipendono dal numero di cammini serializzati.

## Secondo step: 

Lo step successivo riguarda la costruzione del grafo a partire dai cammini BGP estratti precedentemente dal file 20110501.all-paths.bz2. In sintesi, l'obiettivo di questo step è quello di estrarre dalle liste gli archi e le loro frequenze e a partire da queste costruire dinamicamente il grafo inserendo gli archi e aggiornando le frequenze dei cammini. Anche in questo caso abbiamo fatto qualche test preliminare nel notebook inspect_data.ipynb. 
Nel notebook, le frequenze sono state estrapolate e salvate come frequenze = defaultdict(int) (la differenza tra dict e defaultdict è che in defaultdict si può definire un caso di default e il tipo che prendono i valori, in questo caso int della frequenza. Se si fa frequenze[0] non dà key error perchè la chiave non esiste ma la crea di default con chiave 0 e valore 0). Poi ho provato a costruire il grafo considerandolo come un dizionario di dizionari, dove la chiave è il nodo e il valore è un dizionario contenente i vicini e il peso (frequenza), cioè la lista di adiacenza. Il risultato è del tipo: {4436: {6762: 1, 701: 1, 2914: 1} ..}. Partendo da queste strutture dati possiamo definire una classe Graph che permetta di inizializzare un oggetto Graph con le strutture dati dedicate e funzionalità per gestire il grafo stesso.

### step2_costruzione_grafo.py

Lo script step2_costruzione_grafo.py implementa una classe Graph che permette di inizializzare un oggetto grafo non orientato e pesato, che implementa funzionalità di gestione generale e di costruzione attraverso la lettura di cammini BGP. Di seguito le specifiche.

#### Input
L'input per la costruzione del grafo è la sequenza di cammini BGP. Lo script é configurato in modo tale da permettere due modalità: la lettura dal file cammini.pkl, creato nello step precedente, o direttamente dal file bz2. Teoricamente, i file pkl dovrebbe risultare più veloce perché il parsing del testo è già stato effettuato nello step1 e il file serializzato può essere deserializzato direttamente senza ulteriori elaborazioni. L'analisi sperimentale provvederà ad effettuare test di confronto tra le due modalità.

#### Output
Lo script restituisce due file: 
- grafo.pkl: rappresenta l'intero grafo. 
- grafo_largest_component.pkl: rappresenta la componente connessa più grande del grafo.

#### Strutture dati
Il grafo viene rappresentato come un dizionario di dizionari (dict) dove la chiave del dizionario esterno è un nodo AS e il dizionario interno è la sua lista di adiacenza pesata. Gli identificatori AS sono convertiti da stringhe a interi tramite la funzione `_convert_node` . Si è scelto di non mapparli in interi consecutivi perché in Python i dizionari non hanno problemi con valori sparsi. (La traccia suggeriva di mapparli in interi consecutivi, ma poteva essere una soluzione indicata principalmente per la struttura vector del C++). Non è stata usata una struttura dati separata per le frequenze degli archi perchè vengono aggiornate direttamente nella lista di adiacenza durante la costruzione del grafo. 

#### Inizializzazione e rappresentazione del grafo

- **`__init__(directed=False)`**: inizializza un grafo vuoto tramite un dizionario di adiacenza. Il grafo è non orientato di default.
- **`__repr__()`**: restituisce una rappresentazione testuale leggibile del grafo, mostrando per ogni nodo i vicini e i relativi pesi.

#### Funzioni generali sul grafo

- **`_convert_node(node)`**: converte l’identificatore AS da stringa a intero. 
- **`add_node(node)`**: aggiunge un nodo con lista di adiacenza vuota. 
- **`remove_node(node)`**: rimuove il nodo e tutti i suoi archi dai vicini.
- **`add_edge(from_node, to_node, weight=None)`**: aggiunge un arco non orientato arbitrario con peso opzionale specificato dall'utente. I self-loop vengono ignorati. 
- **`remove_edge(from_node, to_node)`**: rimuove un arco in entrambe le direzioni.
- **`update_frequency(from_node, to_node)`**: legge la frequenza attuale e la inizializza a zero se non esiste, incrementa il peso dell'arco di 1 in entrambe le direzioni. Gestisce i self-loop.
- **`get_neighbors(node)`**: restituisce il dizionario dei vicini di un nodo con i relativi pesi. 
- **`has_node(node)`**: verifica se un nodo esiste. 
- **`has_edge(from_node, to_node)`**: verifica se un arco esiste. 
- **`get_nodes()`**: restituisce la lista di tutti i nodi. 
- **`get_edges()`**: restituisce la lista di tutti gli archi senza duplicati (u,v) e (v,u).
- **`delete_consecutive_duplicates(path)`**: rimuove i nodi ripetuti consecutivamente in un cammino, es. `[10, 10, 20]` → `[10, 20]`. 

#### Funzioni dedicate alla costruzione del grafo dai cammini BGP:

- **`add_bgp_path(path)`**: converte gli AS in interi, elimina i duplicati consecutivi, poi per ogni coppia consecutiva chiama `update_frequency`. Costruisce il grafo dinamicamente. 
- **`build_from_paths(paths)`**: itera su una lista di cammini (già caricati in memoria o letti dal file bz2) e chiama `add_bgp_path` per ognuno. 
- **`build_from_bz2(filepath, max_paths=None)`**: legge il file bz2 riga per riga, fa il parsing e chiama `add_bgp_path` direttamente senza caricare tutto in memoria. 
- **`load_paths(filepath_bz2, filepath_pkl, max_paths)`**: metodo statico che carica i cammini dal bz2 (con limite opzionale) o dal pkl.
- **`save_graph(filepath)`**: serializza il grafo in un file pickle. 
- **`load_graph(filepath)`**: metodo statico che deserializza il grafo da un file pickle.

#### Funzioni per la componente connessa

- **`largest_connected_component()`**: trova i nodi che appartengono alla componente connessa più grande tramite DFS iterativa.
- **`get_largest_connected_subgraph()`**: restituisce un nuovo oggetto `Graph` contenente solo i nodi e gli archi della componente connessa più grande. Il grafo originale non viene modificato.

#### Complessità dei metodi principali

`add_node` ha complessità O(1) perché aggiunge semplicemente una chiave al dizionario. `remove_node` ha complessità O(V) perché deve scorrere tutti i nodi del grafo per rimuovere il nodo eliminato dalle loro liste di adiacenza — nel caso peggiore tocca tutti i V nodi. `add_edge` e `update_frequency` hanno complessità O(1) perché si limitano ad accedere e modificare voci in due dizionari (operazioni a tempo costante). `add_bgp_path` ha complessità O(k) dove k è la lunghezza del cammino — scorre le coppie consecutive e chiama `update_frequency` per ognuna.
Il totale è quindi proporzionale alla lunghezza del cammino. `build_from_paths` e `build_from_bz2` hanno complessità O(N) dove N è la lunghezza totale di tutti i cammini — chiamano `add_bgp_path` su ogni cammino, e la somma delle lunghezze è N. `largest_connected_component` ha complessità O(V+E) perché implementa una DFS che visita ogni nodo una volta sola O(V) e percorre ogni arco una volta sola O(E).

## Step 3: Ricerca cammino minimax ottimo
### Idea generale
L'obiettivo é trovare il costo del cammino minimax ottimo dati due nodi u e v. Quindi dobbiamo trovare il percorso che costa meno per andare da u a v, dove il costo è definito come la frequenza massima di un arco lungo quel percorso. dobbiamo minimizzare questo costo.

L'idea è quella di trovare il Minimum Spanning Tree dal punto A al punto B, che mi garantisce di trovare sempre il cammino ottimo, con costo minore. 
Usiamo l'algoritmo di Kruskal e non quello di Prim perchè il grafo sembra sparso (ad esempio sul testo che abbiamo fatto: nodi: 37020 e archi: 65910) quindi dovrebbe essere più efficiente.

Gli step da fare per implementare l'algoritmo sono: 

1. ordina tutti gli archi per peso crescente 
2. aggiunge un arco alla volta, saltando quelli che creerebbero un ciclo
3. si ferma quando tutti i nodi sono connessi

Per rilevare efficientemente i cicli, usiamo la struttura Union-Find (detta anche Disjoint Set Union). Se due nodi appartengono allo stesso set allora non li uniamo perchè formebbero un ciclo.

L'MST potrebbe essere salvato come oggetto Graph contenente solo gli archi dell'albero. Per rispondere a una query (u, v) si fa una BFS o DFS sull'MST — il cammino trovato è automaticamente il cammino minimax ottimo, e il suo costo è il massimo peso tra gli archi attraversati.

### Implementazione 

**Union-Find** è implementata come classe separata `UnionFind` in `step3_ricerca_cammini_minimax_v3.py`. Viene inizializzata con n elementi, dove n è il numero di nodi del grafo. Internamente usa due ottimizzazioni:

- **path compression**: quando si cerca la radice di un nodo, tutti i nodi incontrati lungo il percorso vengono collegati direttamente alla radice, rendendo le ricerche 
  future più veloci
- **union by rank**: quando si uniscono due insiemi, l'albero più basso viene attaccato a quello più alto, evitando di creare alberi sbilanciati

Nota: Union-Find lavora internamente con indici interi consecutivi 0, 1, 2... — quindi gli AS vengono mappati temporaneamente in indici tramite `node_to_index` solo per questa struttura, senza modificare il grafo.

**Kruskal** è implementato come funzione `kruskal(graph)` che:
- prende in input un oggetto `Graph` non orientato e connesso
- ordina gli archi per frequenza crescente con `edges.sort()` — 
- itera sugli archi e usa `union_find.union()` per decidere se aggiungere l'arco
- restituisce un oggetto `Graph` contenente solo gli archi dell'MST e il peso totale

**Query minimax** è implementata come funzione `minimax_query_dfs(mst, start, target)` che fa una DFS sull'MST. Ogni elemento dello stack contiene:
- il nodo corrente
- il massimo peso incontrato fino a quel punto
- il cammino seguito

Quando raggiunge il nodo target, restituisce il costo minimax (massimo peso sul cammino) e il cammino completo. 

import bz2
import pickle
import os
import argparse


""" Prende in input il file /code/ADSproject/data/20110501.all-paths.bz2 contenente i cammini. I cammini sono rappresentati in questo modo nel dataset:

                                     routeviews/isc|5 4436|6762|21826 200.82.128.0/24 i 198.32.176.13  

    quindi dobbiamo estrarre solo la parte relativa ai nodi (4436, 6762, 21826) e ignorare tutto il resto (indirizzi ip, ecc).  
    La funzione leggi_cammini restituisce una lista di cammini (lista di liste di nodi), es: [['4436', '6762', '21826'], ['6939', '15290', '2671', '2669'], ...].
    La funzione salva_cammini salva i cammini in un file pickle così da non doverli leggere ogni volta dal file bz2. La funzione carica_cammini carica i cammini da un file pickle.
      
    Uso: python src/step1_parser_cammini.py  """



def leggi_cammini(filepath, max_righe=None): ## max_righe serve per limitare il numero di cammini letti (utile per test)

    cammini = []
    contatore = 0

    with bz2.open(filepath, "rt") as f:
        for riga in f:
            if max_righe is not None and contatore >= max_righe:
                break
            if riga.startswith("#"):   # salta i commenti e passa alla riga successiva
                continue
            parti = riga.strip().split() # splitto la riga in parti separate da spazi
            cammino = []
            for p in parti[1:]: # salto la prima parte (routeviews/isc|5) 
                if "/" in p or "." in p or ":" in p:  ## ignora gli elementi che sono indirizzi ip ecc
                    break
                nodi = p.split("|")
                cammino.extend(nodi) # aggiunge un nodo alla volta
            if len(cammino) > 1:
                cammini.append(cammino) # aggiunge il cammino come singolo elemento 
                contatore += 1
    return cammini

## Salva e carica i cammini in un file pickle per evitare di doverli leggere ogni volta dal file bz2

def salva_cammini(cammini, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(cammini, f)
    print(f"cammini salvati in {filepath}")


## Caricamento dei cammini da un file pickle

def carica_cammini(filepath):
    with open(filepath, "rb") as f:
        cammini = pickle.load(f)
    print(f"cammini caricati: {len(cammini)}")
    return cammini


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--max_righe", type=int, default=None)
    args = parser.parse_args()

    if args.max_righe is not None:
        cache = "/code/ADSproject/data/cammini_test.pkl" # crea un file di test della dim che abbiamo definito (tipo 1M)
    else:
        cache = "/code/ADSproject/data/cammini.pkl"

    if os.path.exists(cache):
        cammini = carica_cammini(cache)
    else:
        cammini = leggi_cammini("/code/ADSproject/data/20110501.all-paths.bz2", max_righe=args.max_righe)
        salva_cammini(cammini, cache)

    print(f"cammini totali: {len(cammini)}")
    print("primi 5:", cammini[:5])
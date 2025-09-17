
# catalogpy :)

[![PyPI Version](https://img.shields.io/pypi/v/catalogpy)](https://pypi.org/project/catalogpy/)
[![Total Downloads](https://static.pepy.tech/badge/catalogpy)](https://pepy.tech/project/catalogpy)
[![License](https://img.shields.io/pypi/l/catalogpy)](https://pypi.org/project/catalogpy/)

catalogpy è una libreria che ti permette di ordinare le tue stringhe, e mantenere il tuo codice più pulito!

## Installazione
Come installarlo? Semplice basta usare **pip**!
```bash
pip install catalogpy
```
## Funzioni

In questa versione (v1.4) puoi:     
ordinare le parole in ordine alfabetico in un'elenco ```elencation()```  
ordinare le parole in ordine alfabetico in un'elenco numerato ```ordination()```  
ordinare le parole dalla più lunga alla più corta ```order_longer()```   
ordinare le parole dalla più corta alla più lunga ```order_shortest()```
filtrare le parole in base al numero delle lettere ```remove_words(words, min_len, max_len)```
rimuovere duplicati dalle tue liste ```unique_words()```
pulire le tue stringhe da spazi, caratteri speciali e numeri ```clean_words()```

I parametri ```min_len```, ```max_len``` e ```words``` filtrano le parole in base al numero di lettere scelto dall'utente, e sono opzionali 
in tutti i comandi tranne ```remove_words()``` il quale cancellerà tutte le parole in mancanza di parametri.
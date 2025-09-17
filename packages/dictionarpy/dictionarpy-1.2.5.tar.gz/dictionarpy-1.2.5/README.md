# DictionarPy

Extensible offline dictionary application

### Statistics regarding this version's included dictionary:

```sh
$ dictionarpy -ns
Words:               53224
Definitions:         118657
IPA Transcriptions:  29812
Disk size:           10.49MB
──────────────────────────────────────────
Parts of speech:
    nom │ auxiliary verb │ intransitive verb
    │ nom masculin │ conjuction │ transitive
    verb │ plural noun │ preposition │ nom
    féminin │ adjective │ pronoun │ verb
    conjunction │ phrase │ article
    transitive/intransitive verb │ verbe
    noun │ interjection │ idiom
    abréviation │ adverb │ abbreviation
    determiner │ definite article
```

---

## Examples

- Add a word/definition to the database
  
  ```sh
  $ dictionarpy -a -w "my new word" -p "my part of speech" -d "my definition!"
  ```

- Add or update the phonetic/phonemic transcription of a word

  ```sh
  $ dictionarpy -a -w "my new word" -i "/mj nu wɝd/"
  ```

- Show the definitions for a word (use `-n` to avoid ansi escape sequences)

  ```sh
  $ dictionarpy -n "my new word"                                                
  ┌──────────────────────┐
  │     my new word      │
  │     /mj nu wɝd/      │
  ├──────────────────────┤
  │ 1. my part of speech │
  │    my definition!    │
  └──────────────────────┘
  ```

- Remove a word/definition from the database

  ```sh
  $ dictionarpy -r 1 "my new word"
  ```

- Learn a random word!

  ```sh
  $ dictionarpy "$(dictionarpy -z)"
  ```

- Run `dpy -h` for help and additional functions

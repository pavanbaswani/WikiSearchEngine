# WikiSearch Engine
This repository consists of the codebase to build index files on wikipedia dump data and search plain and field queries.

## Required Libraries
Python libraries:

1) SnowballStemmer
2) xml.sax parser

## WikiIndexer
#### Preprocessing the wikidump
Each document in the wikidump file can be extracted as a string and performed the following operations to preprocess and clean the text for extracting tokens (words).
1) Casefolding: converting the entire string into lowercase to avoid the string matching issues.
2) Tokenization: splitting the text into tokens (words) based on the punctuations.
3) Stopword Removal: removing the unnecessary words (filler words) to robust the search results and reduce the size of index.
4) Stemming: finding out the root word by removing the suffixes in the words.
After applying all these operations, we get the list of stemmed tokens without stopwords. These tokens will be used to build the inverted index.

#### Creating Index Files
1) The tokens extracted from the preprocessing step are stored in the index files (to create the inverted index file(s)).
2) Each token will be stored in a file with their starting letter (check the description of index.py file) in ascending order along with their frequency.
3) Later these files will be used to generate the token information files (which are used to speed up the search for the tokens in the given query).

## WikiSearch
#### processing plain and field queries
1) Each query provided by the user will be checked (whether plain query or field query)
2) Plain query will be processed normally by applying all preprocessing steps mentioned above. Whereas, the field query will be processed separately by extracting the tokens of each field and search for the tokens in their respective fields.

#### Extracting the postings for each token
1) For each token in the plain or field query, index file information will be fetched from the token information file.
2) Once the index file information available, then binary search will be applied on the index file to get the postings of the given token.
3) Finally, all the postings of every token will be fetched from the index files and used for ranking.

#### Ranking the postings and returning top resutls
1) In this, the TF-IDF score will be computed for the documents and sorted in the descending order.
2) Based on the common documents with high score respective titles will be returned as the output for the given plain or field query.

## CodeBase
#### Main python files
1) index.py: This file contains the wikiparser class, that can read the xml contents with xml.sax library. The title, bodytext, infobox, category, references and links were extracted from each page present in the xml file given. It will apply casefolding (lowercase), tokenization (with punctuations), stopword removal and stemming to find the keywords. Finally, it will build the index files(pickle) in inverted_index folder to use it for searching a given query.
__Usage:__ *python3 index.py <wikidump_path> <inverted_index_folder_path> <inverted_index_stats>*
Initially, the inverted index is created for each 20000 documents in the wikidump. After completing the parsing of entire wikidump, each words starts with alphabet moved to the respective index file (for example the word starts with letter 'a' moved to '*a_index.pkl*' file likewise). All the numbers stored in '*num_index.pkl*' file. Remaining words will be stored in '*oth_index.pkl*' file. While searching the first letter of the word extracted and the respective file will be loaded to get the postings of the words.

2) search.py: This file contain the functions to load the index files as a dictionary object, rank the postings and finally display the top 10 relevant results (titles).
__Usage:__ *python3 search.py <inverted_index_folder_path>*

#### Other python files
1) textMining.py: This file contains the helper functions for *index.py* and *search.py*.

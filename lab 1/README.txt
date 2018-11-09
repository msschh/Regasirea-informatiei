The target of this lab is to implement a basic boolean retrieval method. The algoritm is described in IIR book, section 4.2 and in the course content.

The folder has a sub-folder toy_data - which you can start to play and debug first. Then, use the bigger corpus data (read_data subfolder) and check the correctness with the queries examples for input / output in sub-folder named example_queries.

Requirements:

Python implementation

Part A. 
-----------------
Target: Implement an Indexer program that takes two arguments: Indexer corpus_dir_path  out_index_path.
The out_index_path is the file where the entire index built from corpus will reside.

Steps:

 1. Implement the tokenizer.  

 2. Build efficiently the indexing and query in RAM.

     - Order the terms by postings lists length to optimize queries as described in the lecture notes !

 3. Consider a given memory RAM threshold then of T (let's say 512 MB) and use RAM to disk communication so solve the problem using constraint T.

Optional for bonus points:
 4. Use Apache Spark to build the index in a distributed environment
    Apply normalization techniques or thesaurus.
    Map of special tokens as a single token "San Francisco".
    Apply stemming and all other preprocessing techniques if you want using open source     python libraries.


Part B.
--------------

Same requirements and steps as above but this time use a compressed index using gap encoding with variable
byte encoding for each gap. 

Optional:
 5. Use Gamma-enconding

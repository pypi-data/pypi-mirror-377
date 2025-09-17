# CREA-Vectors

This is a package to access CREA vectors. Various data collection methods are also included.
Future updates will allow users to add their collected vectors to the main set.

## How to run the code
1. Clone the repository
2. Navigate to the crea_library folder and run python crea.py
3. In python import the library
   - from crea import CREA
   - c = CREA() # Automatically loads main dictionary or
   - c = CREA('path_to_file.json') # Load custom json file
   ### Usage
   - all_vectors = c.get_all_vectors()
   - vector = c.get_vector('word1')
   - vectors = c.get_vectors(['word1', 'word2'])
   - vectors_and_cols = c.select_cols(['word1', 'word2'], [1,3,5])
   - similarity = c.cosine_similarity('word1', 'word2')
   - n_similar = c.top_n_similar('word1', 5) # defaults to 5

   
## PsychoPy Data Collection
- Results are saved as a JSON file named 'results.json'
- Currently it is overwritten each time
- JSON file has the structure {'target_word': {'Rating Category 1': rating_1, ... 'Rating Category n': rating_n}}
- CREA.get_raw('results.json') gets the new raw data from results.json and adds a new row to raw results.csv
- CREA.calculate_averages('results.csv') calculates the average of results.csv and returns a DataFrame of the averages



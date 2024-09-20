/* Labb 2 i DD2350 Algoritmer, datastrukturer och komplexitet    */
/* Se labbinstruktionerna i kursrummet i Canvas                  */
/* Ursprunglig fÃ¶rfattare: Viggo Kann KTH viggo@nada.kth.se      */
import java.util.LinkedList;
import java.util.List;

public class ClosestWords {
  LinkedList<String> closestWords = null;


  int matrix_columns = 50;
  int matrix_rows = 50;
  int min_edit_distance = -1;
  int[][] create_levenshtein_matrix = new int [matrix_columns][matrix_rows];

  void intialize_matrix() {
    for (int i = 0; i < matrix_columns; i++) {
      create_levenshtein_matrix[i][0] = i;
    }
    for (int j = 0; j < matrix_rows; j++) {
      create_levenshtein_matrix[0][j] = j;
    }
  }

  int levenshtein_matrix (String misspelled_word, String currentWord,int number_of_characters_matched ){
    
    int misspelled_word_length = misspelled_word.length();
    int currentWord_length = currentWord.length();

    if (currentWord_length == 0) {
      return misspelled_word_length;
    } else if (misspelled_word_length == 0) {
      return currentWord_length;
    }

    for (int i = 1 + number_of_characters_matched; i <= currentWord_length; i++) {
      for (int j = 1; j <= misspelled_word_length; j++) {
          if (currentWord.charAt(i - 1) == misspelled_word.charAt(j - 1)) {
              create_levenshtein_matrix[i][j] = create_levenshtein_matrix[i - 1][j - 1];
          } else {
              create_levenshtein_matrix[i][j] = Math.min(
                  create_levenshtein_matrix[i - 1][j - 1], // substitution
                  Math.min(create_levenshtein_matrix[i][j - 1], create_levenshtein_matrix[i - 1][j]) // addition/removal
              ) + 1;
          }
      }
  }
  
    return create_levenshtein_matrix[currentWord_length][misspelled_word_length];
  }

  int prefixMatched(String misspelledWord, String currentWord) {
    int matchedCharacters = 0;
    int minimumWordLength = Math.min(misspelledWord.length(), currentWord.length());
    int i = 0;

    while (i < minimumWordLength) {
        if (misspelledWord.charAt(i) == currentWord.charAt(i)) {
            matchedCharacters++;
            i++;
        } else {
            return matchedCharacters;
        }
    }
    
    return matchedCharacters;
}


  public ClosestWords(String misspelled_word, List<String> wordList) {

    int levenshtein_distance = 0;
    intialize_matrix();
    String previous_word = "";
    for (String current_word : wordList) {
     
      if (min_edit_distance != -1 && min_edit_distance - Math.abs(misspelled_word.length() - current_word.length()) < 0) {
        continue; 
      }
      
      int number_of_characters_matched = prefixMatched (previous_word, current_word);
      levenshtein_distance = levenshtein_matrix(misspelled_word,current_word ,number_of_characters_matched );

  
      if (levenshtein_distance < min_edit_distance || min_edit_distance == -1) {
        min_edit_distance = levenshtein_distance;
        closestWords = new LinkedList<String>();
        closestWords.add(current_word);
      }
      else if (levenshtein_distance == min_edit_distance)
        closestWords.add(current_word);
        
      previous_word = current_word;
    }
  }

  int getMinDistance() {
    return min_edit_distance;
  }

  List<String> getClosestWords() {
    return closestWords;
  }
}



  


  
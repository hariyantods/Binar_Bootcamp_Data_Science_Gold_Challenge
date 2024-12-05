# CleanText-API <br>
API will be used to clean tweets and saved to database automatically. <br>
API will receive two endpoints both text and file. Text is cleaned by typing the sentence on the UI, however, for file, after uploding the file, column having column name **Tweet** will be cleaned, cencored, and subsitute with respective word. <br> <br>
In order to get the whole process, please find on the architecture <br>
## System Architecture
![image_alt](https://github.com/hariyantods/Binar_Bootcamp_Data_Science_Gold_Challenge/blob/8c95eb431a002afd35b17c02e28fa3b2457a2a71/workflow.png)

## File Explanation
1. app.py : the main program for cleaning text and file
2. re_dataset.csv : the sample input file to be cleaned
3. Data_Analysis.ipynb : code for analysis the result e.q visualization and statictical analysis
4. main.db : main database
5. docs : directory consisted yml file

## Result Example
Result of the cleaned data will be represented by Raw_text and Clean_text
### 1. Text clean
The abusive words will be cencored with *** and non-standarized words will be subsituted with standarized one
<br>
![image_alt](https://github.com/hariyantods/Data-Science-Wave-03/blob/e6db3ceffe6ef734dbe4df8ff5b45a5dd2782739/text2.png)
### 2. File clean
The result is the same with the text, the difference is only from the input file which is uploaded file.
<br>
![image_alt](https://github.com/hariyantods/Data-Science-Wave-03/blob/07bb12395b4131918f519dff53cdef5e3e38d7d8/file.png)

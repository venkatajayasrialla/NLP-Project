import os
import glob
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import spatial
import gensim.downloader as api
from gensim import corpora
from gensim.similarities import SparseTermSimilarityMatrix
from gensim.similarities import WordEmbeddingSimilarityIndex
from PyPDF2 import PdfReader

# Load Word2Vec model
model = api.load("glove-wiki-gigaword-300")

# Input text samples
ip_text1 = "Pre-requisites, Co-requisites, & other restrictions Prerequisite: ENCS majors only Course Description CS 5333 Discrete Structures (3 semester hours) Mathematical foundations of computer science. Logic, sets, relations, graphs and algebraic structures. Combinatorics and metrics for performance evaluation of algorithms. (3-0) S This is a fundamental course for CS. Everything else you learn in CS will relate to this course. Treat this course very seriously! Learning Outcomes Ability to use the Boolean Algebra properties of set theory Ability to construct valid proofs and recognize invalid ones, including proofs by induction Ability to use inclusion-exclusion and more advanced methods of counting Ability to set up and solve recurrence relations Ability to use the Master Theorem as estimations of time complexity Ability to understand and use basic properties of relations including equivalence relations and partial orders Ability to understand and use basic properties of finite graphs Required Texts & Materials Discrete Mathematics and Its Applications, Kenneth H. Rosen, McGraw Hill, 7th or 8th edition. Textbooks can be ordered online or purchased at the UT Dallas Bookstore."
ip_text2 = "Pre-requisites, Co-requisites, & other restrictions CS 5303 Computer Science I, CS 5333 Discrete Structures Prerequisite will be strictly enforced. Course Description Topics: Analysis of algorithms. Stacks, queues, and trees, including B-trees. Heaps, hashing, and advanced sorting techniques. Graphs, algorithms on graphs. Learning Outcomes Study efficient algorithms for a number of fundamental problems, learn techniques for designing algorithms, prove correctness and analyze running times. 1. Ability to understand asymptotic notations, recurrences, algorithm analysis 2. Ability to use/analyze Lists, stacks, queues, hashing, priority queues 3. Ability to use/analyze Binary search trees, balanced binary search trees 4. Ability to use/analyze Graphs, Depth-first search, Topological ordering 5. Ability to use/analyze Breadth-first search, Dijkstra's algorithm 6. Ability to use/analyze Algorithms of Prim and Kruskal, Disjoint-set Union-Find problem Required Texts & Materials Data Structures and Algorithms in C++ by M. T. Goodrich, R. Tamassia, D. M. Mount."
ip_text3 = "Pre-requisites, Corequisites, & other restrictions Prerequisite: CS 5330. Prerequisite or Corequisite: CS 5343, and a working knowledge of C and UNIX. All programming projects/exercises must be implemented only in C. Course Description Processes and threads. Concurrency issues including semaphores, monitors and deadlocks. Simple memory management. Virtual memory management. CPU scheduling algorithms. I/O management. File management. Introduction to distributed systems Learning Outcomes 1. An understanding of processes 2. An understanding of threads 3. An understanding of concurrent programs. 4. An understanding of simple memory management. 5. An understanding of virtual memory 6. An understanding of scheduling algorithms. 7. An understanding of I/O management 8. An understanding of file management. Required Texts & Materials The textbook (available for free at http://www.ostep.org ): Operating Systems: Three Easy Pieces Remzi H. Arpaci-Dusseau and Andrea C. Arpaci-Dusseau Arpaci-Dusseau For projects/exercises, the following book is useful (available for free at https://pdos.csail.mit.edu/6.828/2017/xv6/book-rev10.pdf ): xv6 - a simple, Unix-like teaching operating system Russ Cox, Frans Kaashoek, and Robert Morris"

# Correct labels for each subject
correct_list = {'DiscreteMaths':[1,0,0,0,1,1,1,1,1,1,1,1,0,0],'OperatingSystems':[1,1,1,1,0,1,1,0,1,1,1],'DataStructures':[0,0,1,0,1,1,1,1,1,1]}

# Path to PDF files
path = 'C:/Users/venka/Documents/NLP/Automated-Prerequisite-Waiver-Project-main/NLP_Project_Get_Model_Accuracy'

# Global variables
total_files = 0
correct_op_tf_idf = 0
correct_word_cosine = 0
correct_word_soft_cosine = 0

# Load stopwords for English
stop_words = set(stopwords.words('english')) 

def preprocess(text):
    # Tokenize, lowercase, and remove stopwords
    word_list = nltk.word_tokenize(text.lower())
    filtered_words = [word for word in word_list if word not in stop_words]
    return ' '.join(filtered_words)

def get_vector(text):
    # Get vector representation for text using Word2Vec model
    words = preprocess(text).split()
    vectors = [model[word] for word in words if word in model]
    return np.sum(vectors, axis=0)

def get_cosine_similarity(text1, text2):
    # Compute cosine similarity between two texts
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim[0, 1]

def get_soft_cosine_similarity(text1, text2):
    # Compute soft cosine similarity between two texts
    dictionary = corpora.Dictionary([preprocess(text1).split(), preprocess(text2).split()])
    soft_cosine_1 = dictionary.doc2bow(preprocess(text1).split())
    soft_cosine_2 = dictionary.doc2bow(preprocess(text2).split())
    similarity_index = WordEmbeddingSimilarityIndex(model)
    similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary)
    return similarity_matrix.inner_product(soft_cosine_1, soft_cosine_2, normalized=(True,True))

def getSubjectAccuracy(subject_path, ip_text, thresholds, subject):
    global total_files, correct_op_tf_idf, correct_word_cosine, correct_word_soft_cosine
    file_no = 0
    for filename in glob.glob(os.path.join(subject_path, '*.pdf')):
        with open(filename, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + " "
        
        sim1 = get_cosine_similarity(ip_text, text)
        sim2 = get_soft_cosine_similarity(ip_text, text)
        sim3 = get_cosine_similarity(ip_text, text)
        
        if (sim1 > thresholds[0] and correct_list[subject][file_no] == 1) or (sim1 < thresholds[0] and correct_list[subject][file_no] == 0):
            correct_word_cosine += 1 
        if (sim2 > thresholds[1] and correct_list[subject][file_no] == 1) or (sim2 < thresholds[1] and correct_list[subject][file_no] == 0):
            correct_word_soft_cosine += 1 
        if (sim3 > thresholds[2] and correct_list[subject][file_no] == 1) or (sim3 < thresholds[2] and correct_list[subject][file_no] == 0):
            correct_op_tf_idf += 1
        file_no += 1 
        total_files += 1

# Calculate accuracy for each subject
getSubjectAccuracy(os.path.join(path, 'DiscreteMaths'), ip_text1, (0.91, 0.53, 0.43), 'DiscreteMaths')
getSubjectAccuracy(os.path.join(path, 'DataStructures'), ip_text2, (0.84, 0.53, 0.29), 'DataStructures')
getSubjectAccuracy(os.path.join(path, 'OperatingSystems'), ip_text3, (0.92, 0.57, 0.31), 'OperatingSystems')

# Print accuracy results
if total_files == 0:
    print("Error: No PDF files found in the specified directories.")
else:
    print("Accuracy findings are: ")
    print("Word2Vec with Cosine similarity accuracy: ", correct_word_cosine * 100 / total_files)
    print("Word2Vec with Soft-cosine similarity accuracy: ", correct_word_soft_cosine * 100 / total_files)
    print("TF-IDF with Cosine similarity accuracy: ", correct_op_tf_idf * 100 / total_files)

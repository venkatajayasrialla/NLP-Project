from fileinput import filename
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import gensim.downloader as api
from gensim import corpora
from gensim.similarities import SparseTermSimilarityMatrix
from gensim.similarities import WordEmbeddingSimilarityIndex
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pymysql.cursors

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/check_prerequisite', methods=['POST'])
def check_prerequisite():
    try:
        if request.method == 'POST':
            extracted_text = request.form.get('extracted_text')
            student_id = request.form.get('student_id')
            selected_course = request.form.get('selected_course')
            print(extracted_text)

            model = api.load("glove-wiki-gigaword-300")

            course_description1 = "Pre-requisites, Co-requisites, & other restrictions Prerequisite: ENCS majors only Course Description CS 5333 Discrete Structures (3 semester hours) Mathematical foundations of computer science. Logic, sets, relations, graphs and algebraic structures. Combinatorics and metrics for performance evaluation of algorithms. (3-0) S This is a fundamental course for CS. Everything else you learn in CS will relate to this course. Treat this course very seriously! Learning Outcomes Ability to use the Boolean Algebra properties of set theory Ability to construct valid proofs and recognize invalid ones, including proofs by induction Ability to use inclusion-exclusion and more advanced methods of counting Ability to set up and solve recurrence relations Ability to use the Master Theorem as estimations of time complexity Ability to understand and use basic properties of relations including equivalence relations and partial orders Ability to understand and use basic properties of finite graphs Required Texts & Materials Discrete Mathematics and Its Applications, Kenneth H. Rosen, McGraw Hill, 7th or 8th edition. Textbooks can be ordered online or purchased at the UT Dallas Bookstore."
            course_description2 = "Pre-requisites, Co-requisites, & other restrictions CS 5303 Computer Science I, CS 5333 Discrete Structures Prerequisite will be strictly enforced. Course Description Topics: Analysis of algorithms. Stacks, queues, and trees, including B-trees. Heaps, hashing, and advanced sorting techniques. Graphs, algorithms on graphs. Learning Outcomes Study efficient algorithms for a number of fundamental problems, learn techniques for designing algorithms, prove correctness and analyze running times. 1. Ability to understand asymptotic notations, recurrences, algorithm analysis 2. Ability to use/analyze Lists, stacks, queues, hashing, priority queues 3. Ability to use/analyze Binary search trees, balanced binary search trees 4. Ability to use/analyze Graphs, Depth-first search, Topological ordering 5. Ability to use/analyze Breadth-first search, Dijkstra's algorithm 6. Ability to use/analyze Algorithms of Prim and Kruskal, Disjoint-set Union-Find problem Required Texts & Materials Data Structures and Algorithms in C++ by M. T. Goodrich, R. Tamassia, D. M. Mount."
            course_description3 = "Pre-requisites, Corequisites, & other restrictions Prerequisite: CS 5330. Prerequisite or Corequisite: CS 5343, and a working knowledge of C and UNIX. All programming projects/exercises must be implemented only in C. Course Description Processes and threads. Concurrency issues including semaphores, monitors and deadlocks. Simple memory management. Virtual memory management. CPU scheduling algorithms. I/O management. File management. Introduction to distributed systems Learning Outcomes 1. An understanding of processes 2. An understanding of threads 3. An understanding of concurrent programs. 4. An understanding of simple memory management. 5. An understanding of virtual memory 6. An understanding of scheduling algorithms. 7. An understanding of I/O management 8. An understanding of file management. Required Texts & Materials The textbook (available for free at http://www.ostep.org ): Operating Systems: Three Easy Pieces Remzi H. Arpaci-Dusseau and Andrea C. Arpaci-Dusseau Arpaci-Dusseau For projects/exercises, the following book is useful (available for free at https://pdos.csail.mit.edu/6.828/2017/xv6/book-rev10.pdf ): xv6 - a simple, Unix-like teaching operating system Russ Cox, Frans Kaashoek, and Robert Morris"

            stop_words = set(stopwords.words('english'))

            def remove_stop_words(sentence):
                words = sentence.split()
                filtered_words = [word for word in words if word not in stop_words]
                return ' '.join(filtered_words)

            def filter_words(lemmatized_output, model_keys):
                return [word for word in lemmatized_output if word in model_keys]

            def get_word2vec_soft_cosine_similarity(text1, text2):
                text1 = remove_stop_words(text1)
                text1 = text1.lower()
                text1.replace('\n', ' ')
                text1.replace('\t', ' ')
                temp_var = ""
                for i in text1:
                    if (i.isalnum() or i == ' '):
                        temp_var += i
                    text1 = temp_var
                text2 = remove_stop_words(text2)
                text2 = text2.lower()
                text2.replace('\n', ' ')
                text2.replace('\t', ' ')
                temp_var = ""
                for i in text2:
                    if (i.isalnum() or i == ' '):
                        temp_var += i
                    text2 = temp_var
                lemmatizer = WordNetLemmatizer()

                word_list = nltk.word_tokenize(text1)
                lemmatized_output1 = [lemmatizer.lemmatize(w) for w in word_list]
                lemmatized_output1 = filter_words(lemmatized_output1, model.key_to_index)
                lemmatized_output1 = ' '.join(lemmatized_output1)

                word_list = nltk.word_tokenize(text2)
                lemmatized_output2 = [lemmatizer.lemmatize(w) for w in word_list]
                lemmatized_output2 = filter_words(lemmatized_output2, model.key_to_index)
                lemmatized_output2 = ' '.join(lemmatized_output2)

                dictionary = corpora.Dictionary([lemmatized_output1.split(), lemmatized_output2.split()])
                soft_cosine_1 = dictionary.doc2bow(lemmatized_output1.split())
                soft_cosine_2 = dictionary.doc2bow(lemmatized_output2.split())

                similarity_index = WordEmbeddingSimilarityIndex(model)
                similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary)
                similarity = similarity_matrix.inner_product(soft_cosine_1, soft_cosine_2, normalized=(True, True))
                return similarity

            sim = 0
            prerequisite_waived = False

            if (selected_course == "6"):
                sim = get_word2vec_soft_cosine_similarity(course_description1, extracted_text)
                if (sim > 0.53):
                    prerequisite_waived = True
            elif (selected_course == "8"):
                sim = get_word2vec_soft_cosine_similarity(course_description2, extracted_text)
                if (sim > 0.53):
                    prerequisite_waived = True
            elif (selected_course == "7"):
                sim = get_word2vec_soft_cosine_similarity(course_description3, extracted_text)
                if (sim > 0.57):
                    prerequisite_waived = True
            else:
                print("Error occurred, please try again.")

            def delete_prerequisite(student_id, selected_course):
                connection = pymysql.connect(
                    host='localhost',
                    user='nlpUser',
                    password='12344321',
                    database='student_prerequisites',
                    cursorclass=pymysql.cursors.DictCursor
                )

                with connection.cursor() as cursor:
                    query = "DELETE FROM student_courses WHERE StudentID = %s AND PrerequisiteCourseID = %s"
                    cursor.execute(query, (student_id, selected_course))
                    connection.commit()

            print(prerequisite_waived)
            if (prerequisite_waived):
                delete_prerequisite(student_id, selected_course)
                return jsonify({'success': True, 'message': 'Prerequisite waived successfully.'})
            else:
                return jsonify({'success': False, 'message': 'Prerequisite not waived.'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

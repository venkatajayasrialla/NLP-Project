import subprocess
import sys

# Install packages
subprocess.run([sys.executable, "-m", "pip", "install", "numpy"])
subprocess.run([sys.executable, "-m", "pip", "install", "scikit-learn"])
subprocess.run([sys.executable, "-m", "pip", "install", "flask"])
subprocess.run([sys.executable, "-m", "pip", "install", "flask_cors"])
subprocess.run([sys.executable, "-m", "pip", "install", "scipy"])
subprocess.run([sys.executable, "-m", "pip", "install", "nltk"])
subprocess.run([sys.executable, "-m", "pip", "install", "gensim"])
subprocess.run([sys.executable, "-m", "pip", "install", "pypdf"])
subprocess.run([sys.executable, "-m", "pip", "install", "glob2"])
subprocess.run([sys.executable, "-m", "pip", "install", "flask", "pymysql"])

# Download NLTK data
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

import sqlite3

import chromadb

from kronik import DATA_DIR

DB_DIR = DATA_DIR.joinpath("db")
CHROMA_DIR = DB_DIR.joinpath("chroma")
SQL_FP = DB_DIR.joinpath("kronik.db")

chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
db = sqlite3.connect(SQL_FP)

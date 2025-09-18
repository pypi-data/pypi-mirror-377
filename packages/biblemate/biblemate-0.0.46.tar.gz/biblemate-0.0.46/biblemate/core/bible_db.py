import numpy as np
import sqlite3, apsw
import json, os
from agentmake import OllamaAI
from agentmake.utils.rag import get_embeddings, cosine_similarity_matrix
from prompt_toolkit.shortcuts import ProgressBar


class BibleVectorDatabase:
    """
    Sqlite Vector Database via `apsw`
    https://rogerbinns.github.io/apsw/pysqlite.html

    Requirement: Install `Ollama` separately

    ```usage
    from biblemate.core.bible_db import BibleVectorDatabase
    db = BibleVectorDatabase('my_bible.bible') # edit 'my_bible.bible' to your bible file path
    db.add_vectors() # add vectors to the database
    results = db.search_meaning("Jesus love", 10)
    ```
    """

    def __init__(self, uba_bible_path: str):
        # check if file exists
        if os.path.isfile(uba_bible_path) and uba_bible_path.endswith(".bible"):
            # Download embedding model
            self.embedding_model = "paraphrase-multilingual"
            OllamaAI.downloadModel(self.embedding_model) # requires installing Ollama
            # init
            self.conn = apsw.Connection(uba_bible_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA auto_vacuum = FULL;")
            self._create_table()

    def __del__(self):
        if not self.conn is None:
            self.conn.close()

    def clean_up(self):
        self.cursor.execute("VACUUM;")
        self.cursor.execute("PRAGMA auto_vacuum = FULL;")

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book INTEGER,
                chapter INTEGER,
                verse INTEGER,
                text TEXT,
                vector TEXT
            )
        """
        )

    def getAllVerses(self):
        query = "SELECT * FROM Verses ORDER BY Book, Chapter, Verse"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_vectors(self):
        allVerses = self.getAllVerses()

        with ProgressBar() as pb:
            for book, chapter, verse, scripture in pb(allVerses):
                vector = get_embeddings([scripture], self.embedding_model)
                self.add_vector(book, chapter, verse, scripture, vector)
        self.clean_up()

    def add_vector(self, book, chapter, verse, text, vector):
        vector_str = json.dumps(vector.tolist())
        self.cursor.execute("SELECT COUNT(*) FROM vectors WHERE text = ?", (text,))
        if self.cursor.fetchone()[0] == 0:  # Ensure no duplication
            try:
                self.cursor.execute("INSERT INTO vectors (book, chapter, verse, text, vector) VALUES (?, ?, ?, ?, ?)", (book, chapter, verse, text, vector_str))
            except sqlite3.IntegrityError:
                pass  # Ignore duplicate entries

    def search_vector(self, query_vector, top_k=3, book=0):
        q = "SELECT text, vector FROM vectors"
        if book:
            q += " WHERE book = ?"
            args = (book,)
        else:
            args = ()
        self.cursor.execute(q, args)
        rows = self.cursor.fetchall()
        if not rows:
            return []
        
        texts, vectors = zip(*[(row[0], np.array(json.loads(row[1]))) for row in rows])
        document_matrix = np.vstack(vectors)
        
        similarities = cosine_similarity_matrix(query_vector, document_matrix)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [texts[i] for i in top_indices]

    def search_meaning(self, query, top_k=3, book=0):
        queries = self.search_vector(get_embeddings([query], self.embedding_model)[0], top_k=top_k, book=book)
        return self.search_verses(queries)

    def search_verses(self, queries: list, book: int=0):
        allVerses = []
        for query in queries:
            allVerses += self.search_verse(query, book=book)
        return allVerses

    def search_verses_partial(self, queries: list, book: int=0):
        allVerses = []
        for query in queries:
            allVerses += self.search_verse(query, partial=True, book=book)
        return allVerses

    def search_verse(self, query: str, partial: bool=False, book: int=0):
        book_search = f"Book = {book} AND " if book else ""
        full_match = f'''SELECT * FROM Verses WHERE {book_search}Scripture = ? ORDER BY Book, Chapter, Verse'''
        partial_match = f'''SELECT * FROM Verses WHERE {book_search}Scripture LIKE ? ORDER BY Book, Chapter, Verse'''
        self.cursor.execute(partial_match if partial else full_match, (f"""%{query}%""" if partial else query,))
        return self.cursor.fetchall()
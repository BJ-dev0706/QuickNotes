import sqlite3

def setup_database():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM sections')
    if cursor.fetchone()[0] == 0:
        default_sections = ['Work', 'Personal', 'Ideas']
        cursor.executemany('INSERT INTO sections (name) VALUES (?)', [(section,) for section in default_sections])

    cursor.execute("PRAGMA table_info(notes)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'likes' not in columns or 'section_id' not in columns:
        cursor.execute('SELECT id, title, content FROM notes')
        notes_backup = cursor.fetchall()
        
        cursor.execute('DROP TABLE IF EXISTS notes')
        
        cursor.execute('''
            CREATE TABLE notes (
                id INTEGER PRIMARY KEY,
                title TEXT UNIQUE,
                content TEXT,
                likes INTEGER DEFAULT 0,
                section_id INTEGER,
                FOREIGN KEY(section_id) REFERENCES sections(id)
            )
        ''')
        
        for note in notes_backup:
            cursor.execute('INSERT INTO notes (id, title, content) VALUES (?, ?, ?)', note)

    conn.commit()
    conn.close() 
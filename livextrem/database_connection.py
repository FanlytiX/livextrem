import mariadb
from config import Config
import sys

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cur = None

    def connection(self):
        """Stellt eine Verbindung zur Datenbank her"""
        try:
            Config.validate()
            self.conn = mariadb.connect(
                user=Config.DB_USER,
                password=Config.DB_PASS,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME
            )
            self.cur = self.conn.cursor()
            print("Erfolgreich mit der Datenbank verbunden!")
            return True
        except mariadb.Error as e:
            print(f"Fehler bei der Verbindung: {e}")
            sys.exit(1)

    def execute_query(self, query, params=None):
        """Führt eine SQL-Abfrage aus und gibt die Ergebnisse zurück"""
        try:
            if params:
                self.cur.execute(query, params)
            else:
                self.cur.execute(query)
            
            # Für SELECT-Abfragen und SHOW-Befehle Ergebnisse zurückgeben
            if (query.strip().upper().startswith('SELECT') or 
                query.strip().upper().startswith('SHOW') or
                query.strip().upper().startswith('DESCRIBE')):
                result = self.cur.fetchall()
                # Spaltennamen abrufen
                if self.cur.description:
                    columns = [desc[0] for desc in self.cur.description]
                    return {"columns": columns, "data": result}
                return {"columns": [], "data": result}
            # Für INSERT, UPDATE, DELETE - Änderungen speichern
            else:
                self.conn.commit()
                return {"affected_rows": self.cur.rowcount}
                
        except mariadb.Error as e:
            print(f"Fehler bei der Abfrage: {e}")
            return None

    def get_all_tables(self):
        """Gibt alle Tabellen in der Datenbank zurück"""
        result = self.execute_query("SHOW TABLES")
        return result

    def get_tables_info(self):
        """Alternative Methode um Tabelleninformationen zu bekommen"""
        query = """
        SELECT TABLE_NAME 
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = 'livextrem'
        """
        return self.execute_query(query)

    def get_table_data(self, table_name):
        """Gibt alle Daten einer bestimmten Tabelle zurück"""
        return self.execute_query(f"SELECT * FROM {table_name}")

    def get_table_structure(self, table_name):
        """Gibt die Struktur einer Tabelle zurück"""
        return self.execute_query(f"DESCRIBE {table_name}")

    def connClose(self):
        """Schließt die Datenbankverbindung"""
        if self.conn:
            self.conn.close()
        print("Datenbankverbindung geschlossen")
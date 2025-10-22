from database_connection import DatabaseManager

def display_table_data(db, table_name):
    """Zeigt alle Daten einer Tabelle formatiert an"""
    print(f"\n=== TABELLE: {table_name} ===")
    
    # Tabellenstruktur anzeigen
    structure = db.get_table_structure(table_name)
    if structure and "data" in structure:
        print("Struktur:")
        for column in structure["data"]:
            null_info = "NULL" if column[2] == "YES" else "NOT NULL"
            default = f"DEFAULT {column[4]}" if column[4] else ""
            print(f"  - {column[0]} ({column[1]}) {null_info} {default}".strip())
    
    # Tabellendaten anzeigen
    data = db.get_table_data(table_name)
    if data and "data" in data and data["data"]:
        print(f"\nDaten ({len(data['data'])} Einträge):")
        
        # Spaltennamen anzeigen
        if data["columns"]:
            # Maximale Spaltenbreiten berechnen
            col_widths = []
            for i, col_name in enumerate(data["columns"]):
                max_width = len(str(col_name))
                for row in data["data"]:
                    max_width = max(max_width, len(str(row[i] if i < len(row) else "")))
                col_widths.append(min(max_width, 30))  # Maximale Breite begrenzen
            
            # Spaltenüberschriften anzeigen
            header = " | ".join(f"{col_name:<{col_widths[i]}}" for i, col_name in enumerate(data["columns"]))
            print(header)
            print("-" * len(header))
        
            # Alle Zeilen anzeigen
            for row in data["data"]:
                formatted_row = []
                for i, value in enumerate(row):
                    if value is None:
                        formatted_value = "NULL"
                    else:
                        formatted_value = str(value)
                    # Text auf maximale Breite kürzen
                    if len(formatted_value) > col_widths[i]:
                        formatted_value = formatted_value[:col_widths[i]-3] + "..."
                    formatted_row.append(f"{formatted_value:<{col_widths[i]}}")
                print(" | ".join(formatted_row))
    else:
        print("Keine Daten vorhanden")
    print("=" * 80)

def main():
    # Datenbank-Manager erstellen und verbinden
    db = DatabaseManager()
    db.connection()
    
    try:
        # Tabellen über information_schema abrufen (das funktioniert)
        print("Lade Datenbank-Struktur...")
        tables_result = db.get_tables_info()
        
        if tables_result and "data" in tables_result:
            table_names = [table[0] for table in tables_result["data"]]
            print(f"Gefundene Tabellen: {', '.join(table_names)}")
            
            # Für jede Tabelle die Daten anzeigen
            for table_name in table_names:
                display_table_data(db, table_name)
        else:
            print("Keine Tabellen in der Datenbank gefunden")
            
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
    finally:
        # Verbindung immer schließen
        db.connClose()

if __name__ == "__main__":
    main()
import sys
import os
import json
import pandas as pd
import streamlit as st
import logging
import uuid
import psycopg2

# Setzt die Konfiguration der Seite mit Titel und Symbol
st.set_page_config(page_title="Flottenelektrifizierung", page_icon="🚛", layout="wide")

# Verbindung zur PostgreSQL-Datenbank herstellen
DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Tabelle für Fahrzeugdaten erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    name TEXT,
    zul_gesamtgew REAL,
    max_zuladung REAL,
    kaufpreis REAL,
    progn_restwert REAL,
    gepl_laufzeit REAL,
    versicherungskosten REAL,
    kraftfahrzeugsteuer REAL,
    wartungskosten REAL,
    mautkosten REAL
)
''')
conn.commit()

# Tabelle für Routendaten erstellen
cursor.execute('''
CREATE TABLE IF NOT EXISTS routes (
    route_id SERIAL PRIMARY KEY,
    vehicle_id TEXT,
    km REAL,
    beladung REAL,
    verbrauch REAL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles (vehicle_id) ON DELETE CASCADE
)
''')
conn.commit()

# Fahrzeugdaten in die Datenbank speichern
def save_vehicle_to_db(vehicle_data):
    cursor.execute('''
    INSERT INTO vehicles (vehicle_id, name, zul_gesamtgew, max_zuladung, kaufpreis, progn_restwert, gepl_laufzeit, versicherungskosten, kraftfahrzeugsteuer, wartungskosten, mautkosten)
    VALUES (%(vehicle_id)s, %(name)s, %(zul_gesamtgew)s, %(max_zuladung)s, %(kaufpreis)s, %(progn_restwert)s, %(gepl_laufzeit)s, %(versicherungskosten)s, %(kraftfahrzeugsteuer)s, %(wartungskosten)s, %(mautkosten)s)
    ON CONFLICT (vehicle_id) DO NOTHING
    ''', vehicle_data)
    conn.commit()

# Routendaten in die Datenbank speichern
def save_route_to_db(route_data):
    cursor.execute('''
    INSERT INTO routes (vehicle_id, km, beladung, verbrauch)
    VALUES (%(vehicle_id)s, %(km)s, %(beladung)s, %(verbrauch)s)
    ''', route_data)
    conn.commit()

# Hauptfunktion der App
def run():
    st.title("Fahrzeugdaten")

    # Fahrzeugdaten-Eingabe
    st.write("### Neue Fahrzeugdaten eingeben")
    name = st.text_input("Fahrzeug Name")
    zul_gesamtgew = st.number_input("Zulässiges Gesamtgewicht [t]", min_value=0.0, format="%.0f", step=1.0)
    max_zuladung = st.number_input("Maximale Zuladung [t]", min_value=0.0, format="%.0f", step=1.0)
    kaufpreis = st.number_input("Kaufpreis [EUR]", min_value=0.0, format="%.0f", step=1.0)
    progn_restwert = st.number_input("Prognostizierter Restwert [EUR]", min_value=0.0, format="%.0f", step=1.0)
    gepl_laufzeit = st.number_input("Geplante Laufzeit [km oder Jahre]", min_value=0.0, format="%.0f", step=1.0)
    versicherungskosten = st.number_input("Versicherungskosten [Jährlich]", min_value=0.0, format="%.0f", step=1.0)
    kraftfahrzeugsteuer = st.number_input("Kraftfahrzeugsteuer [Jährlich]", min_value=0.0, format="%.0f", step=1.0)
    wartungskosten = st.number_input("Wartungskosten [Jährlich]", min_value=0.0, format="%.0f", step=1.0)
    mautkosten = st.number_input("Mautkosten [EUR]", min_value=0.0, format="%.0f", step=1.0)

    if st.button("Fahrzeugdaten speichern"):
        vehicle_data = {
            'vehicle_id': str(uuid.uuid4()),
            'name': name,
            'zul_gesamtgew': zul_gesamtgew,
            'max_zuladung': max_zuladung,
            'kaufpreis': kaufpreis,
            'progn_restwert': progn_restwert,
            'gepl_laufzeit': gepl_laufzeit,
            'versicherungskosten': versicherungskosten,
            'kraftfahrzeugsteuer': kraftfahrzeugsteuer,
            'wartungskosten': wartungskosten,
            'mautkosten': mautkosten
        }
        save_vehicle_to_db(vehicle_data)
        st.success("Fahrzeugdaten erfolgreich gespeichert!")

    # Routendaten-Eingabe
    st.write("### Routendaten eingeben")
    # Fahrzeugoptionen aus der Datenbank abrufen
    cursor.execute('SELECT vehicle_id, name FROM vehicles')
    vehicle_options = {row[0]: row[1] for row in cursor.fetchall()}

    if vehicle_options:
        selected_vehicle_id = st.selectbox("Fahrzeug auswählen", options=list(vehicle_options.keys()), format_func=lambda x: vehicle_options[x])

        km = st.number_input("Route [km]", min_value=0.0, step=1.0)
        beladung = st.number_input("Beladung [t]", min_value=0.0, step=0.1)
        verbrauch = st.number_input("Verbrauch [kWh/100 km]", min_value=0.0, step=0.1)
        if st.button("Route hinzufügen"):
            route_data = {
                'vehicle_id': selected_vehicle_id,
                'km': km,
                'beladung': beladung,
                'verbrauch': verbrauch
            }
            save_route_to_db(route_data)
            st.success("Routendaten erfolgreich gespeichert!")

    # Anzeige gespeicherter Routendaten
    st.write("### Temporär gespeicherte Routendaten")
    cursor.execute('''
    SELECT r.route_id, v.name, r.km, r.beladung, r.verbrauch
    FROM routes r
    JOIN vehicles v ON r.vehicle_id = v.vehicle_id
    ''')
    df_routes = pd.DataFrame(cursor.fetchall(), columns=["Route ID", "Fahrzeug Name", "Route [km]", "Beladung [t]", "Verbrauch [kWh/100 km]"])
    st.table(df_routes)

if __name__ == "__main__":
    run()

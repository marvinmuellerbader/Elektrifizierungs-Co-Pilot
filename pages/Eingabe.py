import sys
import os

# Füge das übergeordnete Verzeichnis zum Pythonpfad hinzu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importiere nun das Schema
from schema.set_schema import set_schema
import json
import pandas as pd
import streamlit as st
from streamlit.logger import get_logger
import pydgraph
import logging
import uuid

# Setzt die Konfiguration der Seite mit Titel und Symbol
st.set_page_config(page_title="Flottenelektrifizierung", page_icon="🚛", layout="wide")



# Initialisiert den Dgraph Client
client_stub = pydgraph.DgraphClientStub('localhost:9080')
client = pydgraph.DgraphClient(client_stub)

# Funktion zum Speichern von Fahrzeugdaten
def save_vehicle_data(client, data):
    txn = client.txn()
    try:
        mutation = txn.mutate(set_obj=data)
        txn.commit()
    except Exception as e:
        st.error(f"Fehler beim Speichern der Fahrzeugdaten: {e}")
    finally:
        txn.discard()

# Funktion zum Speichern von Routendaten
def save_route_data(client, data):
    txn = client.txn()
    try:
        mutation = txn.mutate(set_obj=data)
        txn.commit()
    except Exception as e:
        st.error(f"Fehler beim Speichern der Routendaten: {e}")
    finally:
        txn.discard()

# Funktion zum Abrufen von Fahrzeugdaten
def get_vehicle_data(client):
    query = """
    {
      allVehicles(func: type(Vehicle)) {
        uid
        name
        zul_gesamtgew
        max_zuladung
        kaufpreis
        progn_restwert
        gepl_laufzeit
      }
    }
    """
    txn = client.txn(read_only=True)
    try:
        res = txn.query(query)
        return json.loads(res.json).get("allVehicles", [])
    finally:
        txn.discard()

# Hauptfunktion der App
def run():
    st.title("Elektrifizieren Sie Ihre Lkw Flotte!⚡")
    
    # Initialisiere Session State für Fahrzeug und Routen, wenn sie noch nicht existieren
    if 'vehicle_counter' not in st.session_state:
        st.session_state['vehicle_counter'] = 1  # Startwert für Fahrzeugnummern
    
    if 'route_counter' not in st.session_state:
        st.session_state['route_counter'] = 1  # Startwert für Routennummern
    
    # Fahrzeugdaten-Eingabe
    st.write("## Fahrzeugdaten")

    with st.form("vehicle_data", clear_on_submit=False):
        name = st.text_input("Fahrzeug Name", value="", key='name')
        zul_gesamtgew = st.number_input("Zulässiges Gesamtgewicht [t]", min_value=0.0, format="%.0f", step=1.0, key='zul_gesamtgew')
        max_zuladung = st.number_input("Maximale Zuladung [t]", min_value=0.0, format="%.0f", step=1.0, key='max_zuladung')
        kaufpreis = st.number_input("Kaufpreis [EUR]", min_value=0.0, format="%.0f", step=1.0, key='kaufpreis')
        progn_restwert = st.number_input("Prognostizierter Restwert [EUR]", min_value=0.0, format="%.0f", step=1.0, key='progn_restwert')
        gepl_laufzeit = st.number_input("Geplante Laufzeit [km oder Jahre]", min_value=0.0, format="%.0f", step=1.0, key='gepl_laufzeit')
        versicherungskosten = st.number_input("Versicherungskosten [Jährlich]", min_value=0.0, format="%.0f", step=1.0, key='versicherungskosten')
        kraftfahrzeugsteuer = st.number_input("Kraftfahrzeugsteuer [Jährlich]", min_value=0.0, format="%.0f", step=1.0, key='kraftfahrzeugsteuer')
        wartungskosten = st.number_input("Wartungskosten [Jährlich]", min_value=0.0, format="%.0f", step=1.0, key='wartungskosten')
        mautkosten = st.number_input("Mautkosten [EUR]", min_value=0.0, format="%.0f", step=1.0, key='mautkosten')
        
        submit_vehicle_data = st.form_submit_button("Fahrzeugdaten speichern")
        if submit_vehicle_data:
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
                'mautkosten': mautkosten,
                'dgraph.type': 'Vehicle'
            }
            save_vehicle_data(client, vehicle_data)
            st.success(f"Fahrzeugdaten für Fahrzeugnummer {st.session_state['vehicle_counter']} erfolgreich gespeichert! Geben Sie Ihr nächstes Fahrzeug ein.")
            st.session_state['vehicle_counter'] += 1
            st.rerun()

    # Routendaten-Eingabe
    st.write("## Routendaten")
    with st.form("route_data", clear_on_submit=False):
        if st.session_state['vehicle_counter'] > 1:
            selected_vehicle = st.number_input("Fahrzeugnummer", min_value=1, max_value=st.session_state['vehicle_counter']-1, step=1, key='selected_vehicle')
        else:
            st.write("Keine Fahrzeuge vorhanden. Bitte zuerst ein Fahrzeug hinzufügen.")

        km = st.number_input("Strecke [km]", min_value=0.0, format="%.0f", step=1.0, key='km')
        verbrauch = st.number_input("Verbrauch [l/100km]", min_value=0.0, format="%.0f", step=1.0, key='verbrauch')
        fahrleistung = st.number_input("Fahrleistung [Jährlich km]", min_value=0.0, format="%.0f", step=1.0, key='fahrleistung')
        schichtzeiten = st.text_input("Schichtzeiten (konkrete Uhrzeiten oder Stunden)", value="", key='schichtzeiten')
        standzeiten = st.number_input("Standzeiten am Depot [h]", min_value=0.0, format="%.0f", step=1.0, key='standzeiten')
        depot_standort = st.text_input("Depot Standort", value="", key='depot_standort')

        submit_route_data = st.form_submit_button("Routendaten speichern")
        if submit_route_data:
            if st.session_state['vehicle_counter'] > 1:  # Speichere nur, wenn Fahrzeuge existieren
                route_data = {
                    'route_number': st.session_state['route_counter'],  # Routennummer automatisch vergeben
                    'vehicle_number': selected_vehicle,  # Zugehörige Fahrzeugnummer
                    'km': km,
                    'verbrauch': verbrauch,
                    'fahrleistung': fahrleistung,
                    'schichtzeiten': schichtzeiten,
                    'standzeiten': standzeiten,
                    'depot_standort': depot_standort,
                    'dgraph.type': 'Route'
                }
                save_route_data(client, route_data)
                st.success(f"Routendaten für Route {st.session_state['route_counter']} erfolgreich gespeichert!")
                st.session_state['route_counter'] += 1
                st.experimental_rerun()
            else:
                st.error("Keine Fahrzeuge vorhanden. Bitte zuerst ein Fahrzeug hinzufügen.")

    # Fahrzeugdaten anzeigen
    if st.button("Alle Fahrzeuge anzeigen"):
        vehicle_data = get_vehicle_data(client)
        df = pd.DataFrame(vehicle_data)
        st.dataframe(df)

if __name__ == "__main__":
    run()

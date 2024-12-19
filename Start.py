import sys
import os
import json
import pandas as pd
import streamlit as st
from streamlit.logger import get_logger
import pydgraph
import logging
import uuid

# Setzt die Konfiguration der Seite mit Titel und Symbol
st.set_page_config(page_title="Flottenelektrifizierung", page_icon="🚛", layout="wide")

# Initialisiere den Dgraph Client mit Fehlerbehandlung
def init_dgraph_client():
    try:
        client_stub = pydgraph.DgraphClientStub('localhost:9080')
        client = pydgraph.DgraphClient(client_stub)
        return client, client_stub
    except Exception as e:
        st.error(f"Fehler beim Herstellen der Verbindung zur Dgraph-Datenbank: {e}")
        return None, None

client, client_stub = init_dgraph_client()

def close_dgraph_client(client_stub):
    if client_stub:
        client_stub.close()

# Funktion zum Speichern der Fahrzeugdaten in der Session State
def save_vehicle_to_session(vehicle_data):
    if 'vehicle_list' not in st.session_state:
        st.session_state['vehicle_list'] = []
    st.session_state['vehicle_list'].append(vehicle_data)

# Funktion zum Speichern der Routendaten in der Session State
def save_route_to_session(route_data):
    if 'routes' not in st.session_state:
        st.session_state['routes'] = []
    st.session_state['routes'].append(route_data)

# Funktion zum Löschen von Fahrzeugdaten aus der Session State
def delete_vehicle_from_session(index):
    if 'vehicle_list' in st.session_state and len(st.session_state['vehicle_list']) > index:
        st.session_state['vehicle_list'].pop(index)

# Hauptfunktion der App
def run():
    st.title("Fahrzeugdaten")

    if not client:
        st.error("Dgraph-Client konnte nicht initialisiert werden. Bitte überprüfen Sie die Verbindung zur Datenbank.")
        return

    # Initialisiere Session State für Fahrzeuge und Routen
    if 'vehicle_data' not in st.session_state:
        st.session_state['vehicle_data'] = {
            'vehicle_id': str(uuid.uuid4()),
            'name': "",
            'zul_gesamtgew': 0.0,
            'max_zuladung': 0.0,
            'kaufpreis': 0.0,
            'progn_restwert': 0.0,
            'gepl_laufzeit': 0.0,
            'versicherungskosten': 0.0,
            'kraftfahrzeugsteuer': 0.0,
            'wartungskosten': 0.0,
            'mautkosten': 0.0,
            'dgraph.type': 'Vehicle'
        }

    if 'routes' not in st.session_state:
        st.session_state['routes'] = []

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
            'mautkosten': mautkosten,
            'dgraph.type': 'Vehicle'
        }
        save_vehicle_to_session(vehicle_data)
        st.success("Fahrzeugdaten temporär hinzugefügt!")

    # Anzeige gespeicherter Fahrzeuge
    if 'vehicle_list' in st.session_state and st.session_state['vehicle_list']:
        st.write("### Temporär gespeicherte Fahrzeugdaten")
        df = pd.DataFrame(st.session_state['vehicle_list'])
        df_display = df[['name', 'zul_gesamtgew', 'max_zuladung', 'kaufpreis', 'progn_restwert',
                 'gepl_laufzeit', 'versicherungskosten', 'kraftfahrzeugsteuer', 'wartungskosten', 'mautkosten']]

        # Spaltennamen anpassen
        df_display.columns = [
            "Name", 
            "Zulässiges Gesamtgewicht", 
            "Maximale Zuladung", 
            "Kaufpreis", 
            "Prognostizierter Restwert", 
            "Geplante Laufzeit", 
            "Versicherungskosten", 
            "Kraftfahrzeugsteuer", 
            "Wartungskosten", 
            "Mautkosten"
        ]

        st.table(df_display)


        for idx, row in df.iterrows():
            if st.button(f"Löschen {row['name']}", key=f"delete_{idx}"):
                delete_vehicle_from_session(idx)
                st.rerun()

    # Routendaten-Eingabe
    st.write("### Routendaten eingeben")
    if 'vehicle_list' in st.session_state and st.session_state['vehicle_list']:
        vehicle_options = {vehicle['vehicle_id']: vehicle['name'] for vehicle in st.session_state['vehicle_list']}
        selected_vehicle_id = st.selectbox("Fahrzeug auswählen", options=list(vehicle_options.keys()), format_func=lambda x: vehicle_options[x])

        km = st.number_input("Route [km]", min_value=0.0, step=1.0)
        beladung = st.number_input("Beladung [t]", min_value=0.0, step=0.1)
        verbrauch = st.number_input("Verbrauch [kWh/100 km]", min_value=0.0, step=0.1)
        if st.button("Route hinzufügen"):
            route_data = {
                'vehicle_id': selected_vehicle_id,
                'km': km,
                'beladung': beladung,
                'verbrauch': verbrauch,
                'dgraph.type': 'Route'
            }
            save_route_to_session(route_data)
            st.success("Routendaten temporär hinzugefügt!")

    # Anzeige gespeicherter Routendaten
    if 'routes' in st.session_state and st.session_state['routes']:
        st.write("### Temporär gespeicherte Routendaten")
        df_routes = pd.DataFrame(st.session_state['routes'])
        st.table(df_routes)

if __name__ == "__main__":
    try:
        run()
    finally:
        close_dgraph_client(client_stub)

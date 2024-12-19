import streamlit as st
import pandas as pd
import uuid
import pydgraph
from datetime import datetime

# Initialize Dgraph client
client_stub = pydgraph.DgraphClientStub.from_cloud(
    "https://nameless-brook-610132.eu-central-1.aws.cloud.dgraph.io/graphql", 
    "YzA0OGJlMDFkZGZhZjYzMjhjZmExYjhhOTg3M2ZjYWU="
)
client = pydgraph.DgraphClient(client_stub)

def calculate_costs(vehicle, route):
    arbeitstage = 250
    strompreis_depot = 0.21  # €/kWh
    strompreis_oeffentlich = 0.5  # €/kWh
    depot_laden_anteil = 1  # 100%
    dieselpreis = 1.73  # €/l
    maut_pro_km = 0.22  # €/km
    labour_costs = 25.56  # €/h
    average_speed_highway = 80  # km/h

    routenlaenge = route['km']
    jaehrliche_fahrleistung = vehicle.get('jaehrliche_fahrleistung', 100000)  # Default-Wert, falls nicht vorhanden

    maintenance_costs_diesel = vehicle['wartungskosten'] / jaehrliche_fahrleistung
    maintenance_costs_elkw = (vehicle['wartungskosten'] * (1 - 0.44)) / jaehrliche_fahrleistung

    durchschnittlicher_strompreis = depot_laden_anteil * strompreis_depot + (1 - depot_laden_anteil) * strompreis_oeffentlich

    mautkosten = maut_pro_km * (routenlaenge * 0.8)
    energiekosten_diesel = (route['verbrauch'] / 100) * routenlaenge * dieselpreis
    wartungs_kosten_diese_route = maintenance_costs_diesel * route['km']

    wartungs_kosten_elkw_route = maintenance_costs_elkw * route['km']
    energiekosten_elkw = (route['verbrauch'] / 100) * routenlaenge * durchschnittlicher_strompreis

    fahrerkosten = labour_costs * (1 / average_speed_highway) * route['km']

    Gesamtbetriebskosten_ELkw = energiekosten_elkw + wartungs_kosten_elkw_route
    gesamtbetriebskosten_diesellkw = energiekosten_diesel + mautkosten + wartungs_kosten_diese_route

    return {
        "Anteil Depot Ladevorgang ": [f"{depot_laden_anteil * 100}", "-", "%"],
        "Strompreis Depot Laden": [f"{strompreis_depot}", "-", "€/kWh"],
        "Strompreis öffentlich Laden": [f"{strompreis_oeffentlich} ", "-", "€/kWh"],
        "Durchschnittlicher Strompreis": [f"{durchschnittlicher_strompreis:.2f}", "-", "€/kWh"],
        "Diesel Kosten": ["-", f"{dieselpreis}", "€/l"],
        "Energiekosten": [f"{energiekosten_elkw:.2f}", f"{energiekosten_diesel:.2f} €", "€ pro Route"],
        "Wartungskosten": [f"{wartungs_kosten_elkw_route:.2f}", f"{wartungs_kosten_diese_route:.2f}", "€ pro Route"],
        "Maut Kosten": ["-", f"{mautkosten:.2f}", "€ pro Route"],
        "Gesamtbetriebskosten pro Jahr": [f"{Gesamtbetriebskosten_ELkw:.2f}",f"{gesamtbetriebskosten_diesellkw:.2f}", "€ pro Route"]
    }

def show_routes():
    st.header("Routenanalyse")

    fahrzeugdaten = st.session_state.get('vehicle_list', [])
    routendaten = st.session_state.get('routes', [])

    if not fahrzeugdaten or not routendaten:
        st.error("Es sind keine Fahrzeug- oder Routendaten verfügbar.")
        return

    all_data = []

    for vehicle in fahrzeugdaten:
        for route in routendaten:
            if route['vehicle_id'] == vehicle['vehicle_id']:
                data = calculate_costs(vehicle, route)
                all_data.append((vehicle, route, data))

    if not all_data:
        st.write("Keine Routen gefunden.")
    else:
        route_number = 1
        for vehicle, route, data in all_data:
            st.write(f"#### Fahrzeug: {vehicle['name']} - Route: {route['km']} km")
            st.write(f"#### Route {route_number}")
            df = pd.DataFrame(data, index=["E-Lkw", "Diesel Lkw", "Einheiten"]).transpose()

            def highlight_last_row(s):
                is_last_row = s.name == 'Gesamtbetriebskosten pro Jahr'
                return ['font-weight: bold; font-style: italic; color: #cce70c;' if is_last_row else '' for _ in s]

            styled_df = df.style.apply(highlight_last_row, axis=1)
            st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)

            route_number += 1

def run():
    st.set_page_config(page_title="Flottenelektrifizierung", page_icon="🚛")

    option = st.sidebar.selectbox(
        'Wählen Sie eine Option:',
        options=['', 'Routen'],
        index=0,
        format_func=lambda x: 'Bitte wählen' if x == '' else x
    )

    if option == 'Routen':
        show_routes()

if __name__ == "__main__":
    run()

import streamlit as st
import pandas as pd
from datetime import datetime

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
        "Mautkosten": ["-", f"{mautkosten:.2f}", "€ pro Route"],
        "Gesamtbetriebskosten pro Jahr": [f"{Gesamtbetriebskosten_ELkw:.2f}",f"{gesamtbetriebskosten_diesellkw:.2f}", "€ pro Route"]
    }

def generate_analysis(vehicle, route, data):
    st.write(f"### Fahrzeug: {vehicle['name']}")

    # Datenübersicht
    st.subheader("Datenübersicht")
    st.write("#### Allgemeine Daten")
    st.write(f"Name: {vehicle['name']}")
    st.write(f"Route Länge: {route['km']} km")
    st.write(f"Beladung: {route['beladung']} t")

    # Fahrzeugkosten OPEX
    st.subheader("Fahrzeugkosten (OPEX)")
    opex_data = {
        "Parameter": ["Energiekosten", "Wartungskosten", "Mautkosten"],
        "E-Lkw": [
            f"{data['Energiekosten'][0]}",
            f"{data['Wartungskosten'][0]}",
            f"{data['Mautkosten'][0]}"
        ],
        "Diesel-Lkw": [
            f"{data['Energiekosten'][1]}",
            f"{data['Wartungskosten'][1]}",
            f"{data['Mautkosten'][1]}"
        ]
    }
    st.table(pd.DataFrame(opex_data))

    # Fahrzeugkosten CAPEX
    st.subheader("Fahrzeugkosten (CAPEX)")
    st.write("CAPEX-Daten kommen bald...")

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
        for vehicle, route, data in all_data:
            generate_analysis(vehicle, route, data)

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

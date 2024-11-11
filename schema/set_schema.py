import pydgraph

def set_schema(client):
    schema = """
    id: uid .
    name: string @index(exact) .  
    kennzeichen: string @index(exact) . 
    zul_gesamtgew: float .  
    max_zuladung: float . 
    motorleistung: float . 
    kaufdatum: datetime .  
    progn_restwert: float .  
    kaufpreis: float .  
    gepl_laufzeit: float .  
    versicherungskosten: float .  
    kraftfahrzeugsteuer: float . 
    wartungskosten: float . 
    nebenverbraucher: string @index(fulltext) .  
    region: string @index(fulltext) .  
    jaehrliche_fahrleistung: float .
    vehicle_id: string .
    km: float .  
    beladung: float .  
    verbrauch: float .  
    energy_cost: float .
    type_of_contract: string .
    energy_consumption: float .
    charging_stations: int . 
    solar_panels: int .  
    battery_storage: float .  
    layout_date: datetime .  
    battery_weight: float .
    battery_capacity: float .
    powertrain_weight: float .
    useable_battery_capacity: float .
    gravimetric_density: float .
    charging_power: float .
    electricity_demand: float .
    vehicle_range: float .
    custom_type: string .

    type Vehicle {  
        id
        name
        kennzeichen
        zul_gesamtgew
        max_zuladung
        motorleistung
        kaufdatum
        progn_restwert
        kaufpreis
        gepl_laufzeit
        versicherungskosten
        kraftfahrzeugsteuer
        wartungskosten
        nebenverbraucher
        region
        jaehrliche_fahrleistung
    }

    type Route { 
        id
        vehicle_id
        km
        beladung
        verbrauch
    }

    type EnergyCost {  
        id
        energy_cost
        type_of_contract
        energy_consumption
    }

    type DepotLayout {  
        id
        vehicle_id
        charging_stations
        solar_panels
        battery_storage
        layout_date
    }

    type Truck {
        battery_weight
        battery_capacity
        powertrain_weight
        useable_battery_capacity
        gravimetric_density
        charging_power
        electricity_demand
        vehicle_range
        custom_type
    }
    """
    op = pydgraph.Operation(schema=schema, run_in_background=True)
    client.alter(op)

def main():
    # Establish connection to Dgraph
    client_stub = pydgraph.DgraphClientStub.from_cloud(
        "https://nameless-brook-610132.eu-central-1.aws.cloud.dgraph.io/graphql", 
        "YzA0OGJlMDFkZGZhZjYzMjhjZmExYjhhOTg3M2ZjYWU="
    )
    client = pydgraph.DgraphClient(client_stub)

    set_schema(client)
    print("Schema has been set.")

    # Close the client stub
    client_stub.close()

if __name__ == "__main__":
    main()

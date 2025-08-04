import streamlit as st
import requests

# ----- Function to fetch data -----
def fetch_pokemon_data(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{name.lower()}"

    try:
        poke_res = requests.get(url)
        poke_res.raise_for_status()
        poke_data = poke_res.json()

        species_res = requests.get(species_url)
        species_res.raise_for_status()
        species_data = species_res.json()

        desc = next((entry["flavor_text"].replace('\n', ' ').replace('\f', ' ')
                     for entry in species_data["flavor_text_entries"]
                     if entry["language"]["name"] == "en"), "No description available.")

        types = [t["type"]["name"].capitalize() for t in poke_data["types"]]
        img_url = poke_data["sprites"]["other"]["official-artwork"]["front_default"]

        return {
            "name": poke_data["name"].capitalize(),
            "types": types,
            "img_url": img_url,
            "description": desc
        }
    except:
        return None

# ----- Streamlit UI -----
st.set_page_config(page_title="Pokémon Search", layout="centered")
st.title("🔍 Pokémon Search")
st.caption("Find your favorite Pokémon with name, type, image and description.")

pokemon_name = st.text_input("Enter Pokémon name", value="pikachu")

if st.button("Search") or pokemon_name:
    with st.spinner("Fetching Pokémon..."):
        result = fetch_pokemon_data(pokemon_name)

    if result:
        st.image(result["img_url"], width=250)
        st.subheader(result["name"])
        st.markdown(f"**Type:** {', '.join(result['types'])}")
        st.markdown("**Description:**")
        st.info(result["description"])
    else:
        st.error(f"Could not find data for '{pokemon_name}'.")

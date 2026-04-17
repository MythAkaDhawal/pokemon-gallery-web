import streamlit as st
import requests

# ── Type colour palette (keeps it on-theme) ──────────────────────────────────
TYPE_COLORS = {
    "Fire":     "#FF6B3D", "Water":    "#4A9FE0", "Grass":    "#5DBD58",
    "Electric": "#F5D02E", "Psychic":  "#E95693", "Ice":      "#78D8D8",
    "Dragon":   "#6C4DE1", "Dark":     "#594A3A",  "Fairy":    "#EE99AC",
    "Normal":   "#A8A898", "Fighting": "#C03028",  "Flying":   "#7BBEFC",
    "Poison":   "#A040A0", "Ground":   "#E0C068",  "Rock":     "#B8A038",
    "Bug":      "#A8B820", "Ghost":    "#705898",  "Steel":    "#B8B8D0",
}

# ── Stat display name map ─────────────────────────────────────────────────────
STAT_NAMES = {
    "hp": "HP", "attack": "ATK", "defense": "DEF",
    "special-attack": "Sp. ATK", "special-defense": "Sp. DEF", "speed": "SPD",
}

# ── Data fetcher ──────────────────────────────────────────────────────────────
def fetch_pokemon_data(name: str):
    name = name.strip().lower()
    try:
        poke_res = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{name}", timeout=8
        )
        poke_res.raise_for_status()
        poke_data = poke_res.json()

        species_res = requests.get(
            f"https://pokeapi.co/api/v2/pokemon-species/{name}", timeout=8
        )
        species_res.raise_for_status()
        species_data = species_res.json()

        desc = next(
            (
                e["flavor_text"].replace("\n", " ").replace("\f", " ")
                for e in species_data["flavor_text_entries"]
                if e["language"]["name"] == "en"
            ),
            "No description available.",
        )

        types  = [t["type"]["name"].capitalize() for t in poke_data["types"]]
        stats  = {s["stat"]["name"]: s["base_stat"] for s in poke_data["stats"]}
        img_url = poke_data["sprites"]["other"]["official-artwork"]["front_default"]

        return {
            "name":        poke_data["name"].capitalize(),
            "id":          poke_data["id"],
            "types":       types,
            "img_url":     img_url,
            "description": desc,
            "height":      poke_data["height"] / 10,   # dm → m
            "weight":      poke_data["weight"] / 10,   # hg → kg
            "stats":       stats,
        }
    except requests.HTTPError:
        return None
    except Exception:
        return None

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pokémon Gallery",
    page_icon="🔴",
    layout="centered",
)

# ── Global style injection ────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

        html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

        /* Hide default Streamlit header / footer */
        #MainMenu, footer { visibility: hidden; }

        /* Page background */
        .stApp { background: #f0f4ff; }

        /* App header strip */
        .app-header {
            background: linear-gradient(135deg, #e63946 0%, #c1121f 100%);
            border-radius: 14px;
            padding: 22px 28px;
            color: white;
            margin-bottom: 24px;
        }
        .app-header h1 {
            font-size: 1.6rem;
            font-weight: 800;
            margin: 0 0 4px;
        }
        .app-header p { margin: 0; opacity: 0.88; font-size: 0.92rem; }

        /* Type badge */
        .type-badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 20px;
            color: white;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 6px;
            letter-spacing: 0.04em;
        }

        /* Pokémon card */
        .poke-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 28px 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.07);
        }

        /* Pokédex # */
        .poke-id {
            font-size: 0.8rem;
            font-weight: 700;
            color: #aaa;
            letter-spacing: 0.06em;
        }

        /* Stat row */
        .stat-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }
        .stat-label {
            width: 64px;
            font-size: 0.75rem;
            font-weight: 700;
            color: #666;
            text-align: right;
        }
        .stat-bar-bg {
            flex: 1;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
        }
        .stat-bar-fill {
            height: 100%;
            border-radius: 4px;
            background: linear-gradient(to right, #e63946, #457b9d);
        }
        .stat-val {
            width: 30px;
            font-size: 0.78rem;
            font-weight: 700;
            color: #444;
            text-align: left;
        }

        /* Info pills (height / weight) */
        .info-pill {
            display: inline-block;
            background: #f0f4ff;
            border: 1.5px solid #d0d8f0;
            border-radius: 12px;
            padding: 6px 16px;
            font-size: 0.82rem;
            font-weight: 700;
            color: #456;
            margin-right: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <h1>🔴 Pokémon Gallery</h1>
        <p>Search any Pokémon to see its artwork, types, stats & Pokédex entry.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Search input + button ─────────────────────────────────────────────────────
col_input, col_btn = st.columns([4, 1])
with col_input:
    pokemon_name = st.text_input(
        "Enter Pokémon name or Pokédex number",
        placeholder="e.g. pikachu, charizard, 25 …",
        label_visibility="collapsed",
    )
with col_btn:
    search_clicked = st.button("Search 🔍", use_container_width=True)

# ── Trigger search on button click OR Enter (name changed while non-empty) ───
if search_clicked and pokemon_name:
    with st.spinner("Fetching Pokémon data…"):
        result = fetch_pokemon_data(pokemon_name)

    if not result:
        st.error(
            f"⚠️ Couldn't find **'{pokemon_name}'**. "
            "Check the spelling or try a Pokédex number."
        )
    else:
        # ── Card ──
        st.markdown('<div class="poke-card">', unsafe_allow_html=True)

        img_col, info_col = st.columns([1, 1.4])

        with img_col:
            if result["img_url"]:
                st.image(result["img_url"], use_container_width=True)

        with info_col:
            # ID + name
            st.markdown(
                f'<p class="poke-id">#{result["id"]:04d}</p>'
                f'<h2 style="margin:2px 0 10px;font-size:1.6rem;font-weight:800">'
                f'{result["name"]}</h2>',
                unsafe_allow_html=True,
            )

            # Type badges
            badges = "".join(
                f'<span class="type-badge" style="background:{TYPE_COLORS.get(t, "#999")}">{t}</span>'
                for t in result["types"]
            )
            st.markdown(badges, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Height / Weight pills
            hw = (
                f'<span class="info-pill">📏 {result["height"]:.1f} m</span>'
                f'<span class="info-pill">⚖️ {result["weight"]:.1f} kg</span>'
            )
            st.markdown(hw, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Pokédex description
            st.markdown(
                f'<p style="font-size:0.88rem;color:#555;line-height:1.6">'
                f'{result["description"]}</p>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Base stats ────────────────────────────────────────────────────────
        st.markdown(
            "<h4 style='margin:24px 0 12px;font-weight:800'>Base Stats</h4>",
            unsafe_allow_html=True,
        )
        for raw_name, value in result["stats"].items():
            label = STAT_NAMES.get(raw_name, raw_name)
            pct   = min(int(value / 255 * 100), 100)
            st.markdown(
                f"""
                <div class="stat-row">
                    <span class="stat-label">{label}</span>
                    <div class="stat-bar-bg">
                        <div class="stat-bar-fill" style="width:{pct}%"></div>
                    </div>
                    <span class="stat-val">{value}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
elif not pokemon_name and search_clicked:
    st.warning("Please enter a Pokémon name or number first.")

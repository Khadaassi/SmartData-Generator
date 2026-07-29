import streamlit as st


def render_data_preview(result: dict) -> None:
    items = (result.get("generation") or {}).get("items", [])

    st.subheader("Données générées (valides)")
    if not items:
        st.warning("Aucune donnée valide générée.")
        return

    st.dataframe(items, use_container_width=True)

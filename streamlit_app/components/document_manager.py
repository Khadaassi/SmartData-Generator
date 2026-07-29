import streamlit as st

from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError


def render_document_manager(client: ApiClient, project_id: str) -> None:
    st.subheader("Documentation métier (corpus RAG)")
    st.caption(
        "Déposez vos fichiers Markdown (`.md`) avec en-tête YAML "
        "(`title`, `category`, `entity`) — cf. rag/corpus/README.md pour le format attendu."
    )

    uploaded_files = st.file_uploader(
        "Fichiers Markdown",
        type=["md"],
        accept_multiple_files=True,
        key=f"document_uploader_{project_id}",
    )

    if uploaded_files and st.button("Indexer les documents", key=f"index_documents_{project_id}"):
        files = [(uploaded_file.name, uploaded_file.read()) for uploaded_file in uploaded_files]
        try:
            result = client.upload_documents(project_id, files)
        except SmartDataGeneratorApiError as exc:
            st.error(exc.message)
        else:
            st.success(f"{len(result['uploaded'])} document(s) indexé(s).")
            st.rerun()

    st.markdown("**Documents actuellement indexés**")
    try:
        documents = client.list_documents(project_id)["documents"]
    except SmartDataGeneratorApiError as exc:
        st.error(exc.message)
        return

    if not documents:
        st.caption("Aucun document indexé pour ce projet.")
        return

    for document_id in documents:
        col_name, col_delete = st.columns([4, 1])
        col_name.write(document_id)
        if col_delete.button("Supprimer", key=f"delete_document_{project_id}_{document_id}"):
            try:
                client.delete_document(project_id, f"{document_id}.md")
            except SmartDataGeneratorApiError as exc:
                st.error(exc.message)
            else:
                st.rerun()

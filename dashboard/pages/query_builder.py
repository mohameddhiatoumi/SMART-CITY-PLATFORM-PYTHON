"""
Query Builder page for the Smart City Dashboard.
Natural language to SQL interface.
"""
from __future__ import annotations


def render() -> None:
    """Render the NL-to-SQL Query Builder page."""
    import streamlit as st
    from compiler.query_builder import QueryBuilder

    st.title("🔍 Natural Language Query Builder")
    st.markdown(
        "Convert natural language queries into SQL using the Smart City compiler. "
        "No database knowledge required!"
    )

    builder = QueryBuilder()

    # ── Example queries ──────────────────────────────────────────────────────
    st.subheader("📋 Example Queries")
    examples = builder.get_examples()

    cols = st.columns(3)
    selected_example = None
    for i, ex in enumerate(examples[:9]):
        with cols[i % 3]:
            if st.button(f"💡 {ex['query'][:40]}...", key=f"ex_{i}", use_container_width=True):
                selected_example = ex["query"]

    st.divider()

    # ── Query input ───────────────────────────────────────────────────────────
    st.subheader("✍️ Enter Your Query")
    default_query = selected_example or "Show the 5 most polluted zones"

    if "nl_query" not in st.session_state:
        st.session_state.nl_query = default_query
    if selected_example:
        st.session_state.nl_query = selected_example

    query = st.text_input(
        "Natural Language Query",
        value=st.session_state.nl_query,
        placeholder="e.g. Show the 5 most polluted zones",
        key="nl_query_input",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        compile_btn = st.button("🚀 Compile", type="primary", use_container_width=True)
    with col2:
        run_btn = st.button("▶️ Run Query", use_container_width=True)

    if compile_btn or run_btn:
        if not query.strip():
            st.warning("Please enter a query.")
            return

        result = builder.build(query)

        if result["success"]:
            # ── Generated SQL ─────────────────────────────────────────────────
            st.subheader("📄 Generated SQL")
            st.code(result["sql"], language="sql")

            # ── Token breakdown ───────────────────────────────────────────────
            with st.expander("🔤 Token Breakdown", expanded=False):
                tokens = result["tokens"]
                if tokens:
                    import pandas as pd
                    token_df = pd.DataFrame([
                        t for t in tokens if t.get("type") != "EOF"
                    ])
                    if not token_df.empty:
                        st.dataframe(token_df, use_container_width=True)

            # ── AST ───────────────────────────────────────────────────────────
            with st.expander("🌳 Abstract Syntax Tree", expanded=False):
                import json
                ast = result.get("ast", {})
                st.json(ast)

            # ── Run query ─────────────────────────────────────────────────────
            if run_btn:
                _run_query(result["sql"])

        else:
            st.error(f"❌ Compilation failed: {result.get('error', 'Unknown error')}")

    # ── Full example table ────────────────────────────────────────────────────
    with st.expander("📚 All Example Queries", expanded=False):
        import pandas as pd
        ex_df = pd.DataFrame(examples)[["query", "expected_sql", "description"]]
        ex_df.columns = ["Query", "Expected SQL", "Description"]
        st.dataframe(ex_df, use_container_width=True)


def _run_query(sql: str) -> None:
    """Execute query against DB or show demo results."""
    import streamlit as st
    import pandas as pd

    st.subheader("📊 Query Results")

    try:
        from config.settings import DATABASE_URL
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
            st.dataframe(df, use_container_width=True)
            st.caption(f"✅ {len(df)} rows returned from database")
    except Exception as e:
        st.info("📌 Database not available — showing demo results")
        _show_demo_results(sql)


def _show_demo_results(sql: str) -> None:
    """Show mock results when DB is not available."""
    import streamlit as st
    import pandas as pd

    sql_upper = sql.upper()

    if "ZONE" in sql_upper:
        demo = pd.DataFrame({
            "ID_Zone": [1, 2, 3, 4, 5],
            "Nom_Zone": ["Médina", "Zone Industrielle Nord", "Corniche", "Erriadh", "Hammam Sousse"],
            "Type_Zone": ["MIXED", "INDUSTRIAL", "COMMERCIAL", "RESIDENTIAL", "COMMERCIAL"],
            "Indice_Pollution": [52.3, 78.4, 44.1, 28.7, 38.2],
        })
    elif "CAPTEUR" in sql_upper:
        demo = pd.DataFrame({
            "ID_Capteur": [1, 2, 3, 4, 5],
            "Type_Capteur": ["AIR_QUALITY", "TEMPERATURE", "NOISE", "TRAFFIC", "HUMIDITY"],
            "Statut": ["ACTIVE", "ACTIVE", "MAINTENANCE", "ACTIVE", "FAULTY"],
            "etat_dfa": ["ACTIVE", "ACTIVE", "MAINTENANCE", "ACTIVE", "SIGNALED"],
        })
    elif "CITOYEN" in sql_upper:
        demo = pd.DataFrame({
            "ID_Citoyen": [1, 2, 3],
            "Nom": ["Ben Ali", "Trabelsi", "Chaabane"],
            "Prenom": ["Mohamed", "Fatma", "Karim"],
            "Score_Ecologique": [85.5, 92.1, 78.3],
        })
    elif "COUNT" in sql_upper:
        demo = pd.DataFrame({"total": [42]})
    else:
        demo = pd.DataFrame({"result": ["Demo result — connect a database for real data"]})

    st.dataframe(demo, use_container_width=True)
    st.caption("📌 Demo data — connect a PostgreSQL database for live results")

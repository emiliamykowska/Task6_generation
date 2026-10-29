import mysql.connector
import streamlit as st
import pandas as pd


@st.cache_resource
def get_db_connection():
    return mysql.connector.connect(
        username=st.secrets["username"],
        password=st.secrets["password"],
        host=st.secrets["host"],
        database=st.secrets["database"],
        port=st.secrets["port"],
    )


def on_generate():
    st.session_state.batch_index = 0
    st.session_state.disabled = False


locales = ("DEU", "USA")
batch_size = 10

if "batch_index" not in st.session_state:
    st.session_state.batch_index = 0

if "locale" not in st.session_state:
    st.session_state.locale = locales[0]

if "seed" not in st.session_state:
    st.session_state.seed = 0

if "rows" not in st.session_state:
    st.session_state.rows = pd.DataFrame()

if "disabled" not in st.session_state:
    st.session_state.disabled = True

st.header("Random person data generator")

seed = st.number_input("Select a seed", min_value=0, max_value=16777215, step=1)
locale = st.selectbox("Select a locale", options=locales)

if locale != st.session_state.locale or seed != st.session_state.seed:
    st.session_state.batch_index = 0
    st.session_state.locale = locale
    st.session_state.seed = seed
    st.session_state.disabled = True
    st.session_state.rows = pd.DataFrame()

column1, column2 = st.columns(2)
with column1:
    generate_clicked = st.button("Generate users", on_click=on_generate)
with column2:
    next_batch_clicked = st.button("Next batch", disabled=st.session_state.disabled)

if next_batch_clicked:
    st.session_state.batch_index += 1
    fetch_data = True

if generate_clicked or next_batch_clicked:
    args = (
        st.session_state.locale,
        st.session_state.seed,
        st.session_state.batch_index,
        batch_size,
    )

    cnx = get_db_connection()

    cursor = cnx.cursor()

    cursor.callproc("GenerateUserBatch", args)

    for result in cursor.stored_results():
        columns = [col[0] for col in result.description]
        rows = result.fetchall()
        st.session_state.rows = pd.DataFrame(rows, columns=columns)

    cursor.close()

if not st.session_state.rows.empty:
    st.subheader(
        f"Users generated for {st.session_state.locale}, seed {st.session_state.seed} and batch index {st.session_state.batch_index}"
    )
    st.dataframe(st.session_state.rows, hide_index=True)
else:
    st.subheader("Click generate to get 10 random users")

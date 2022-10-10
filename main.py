import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(layout='wide')

# Read validated technicians


@st.experimental_memo
def read_validated():
    file_name_validated = r"database_val.csv"
    validated_df = pd.read_csv(file_name_validated, index_col=0)
    validated_df = validated_df.rename(
        columns={"code": "EMPLOYEE", "specialty": "SPECIALTY", "level": "LEVEL"})
    return validated_df
# Read specialties


def group_specialty(skill, specialties):
    letter = {"STR": "E", "SYS": "S", "AVI": "A", "INT": "I"}
    filtered = filter(
        lambda specialty: specialty[0] == letter[skill], specialties)
    return filtered


# Group specialties

@st.experimental_memo
def merge_data(df_validated, df_history):
    join = pd.merge(df_history, df_validated, on=[
                    "EMPLOYEE", "SPECIALTY"], how="inner")
    return join


def select_specialty(specialty, df):
    filtered_data = df[df["SPECIALTY"] == specialty]
    filtered_data = filtered_data.sort_values(by="LEVEL")
    return filtered_data


def clean_raw(df, min_hours=1.0):
    df["ECODE"] = df["ECODE"].astype("string")
    df = df.groupby(["ECODE", "CODE"])["TTIME"].sum()
    dictionary = dict(df)
    new_data = {"ECODE": dictionary.keys(),
                "TTIME": dictionary.values()}
    new_data = pd.DataFrame(new_data)
    new_data = new_data[new_data.TTIME >= min_hours]
    new_data = new_data.reset_index(drop=True)
    expat = []
    for i in range(len(new_data["ECODE"])):
        if not new_data["ECODE"][i][0][:2] == "86":
            expat.append(i)
    new_data = new_data.drop(index=expat)
    new_data = new_data.reset_index(drop=True)
    code = []
    specialty = []
    for i in range(len(new_data["ECODE"])):
        code.append(new_data["ECODE"][i][0])
        specialty.append(new_data["ECODE"][i][1])
    new_data["EMPLOYEE"] = code
    new_data["SPECIALTY"] = specialty
    new_data = new_data.drop(columns=["ECODE"])
    return new_data


# Main Page
st.image("./img/aeroman.jpeg", width=250)
st.markdown("# Graphic Generator")
st.markdown("Please upload the file with the technicians' historical marks information with the following format: ")
st.markdown("## Upload your file: ")
uploaded_file = st.file_uploader(
    "Choose a file", type=["xlsx", "csv"])

if uploaded_file is not None:
    validated_df = read_validated()
    raw_data = pd.read_csv(uploaded_file, sep=";")
    st.write(raw_data)
    df = clean_raw(raw_data)
    st.dataframe(df)
    merge_df = merge_data(df_validated=validated_df, df_history=df)
    # Sidebar selection
    specialties = merge_df["SPECIALTY"].unique()
    skill = st.sidebar.selectbox("Skill", options=["SYS", "AVI", "INT", "STR"])
    specialty = st.sidebar.multiselect(
        "Select specialty", group_specialty(skill=skill, specialties=specialties))
    for graph in specialty:
        fig = px.scatter(select_specialty(graph, merge_df), x="EMPLOYEE", y="TTIME", color="LEVEL",
                         title=graph, color_continuous_scale=["orange", "red", "green", "blue", "purple"])
        st.plotly_chart(fig)

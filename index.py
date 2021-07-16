import streamlit as st

# Page Configuration
st.set_page_config(page_title="Carbonify Tool",page_icon="🌎",layout="wide",initial_sidebar_state="expanded")


from carbonify import BaseCarbone

#------------------------------------------------------------------------------------------
# PARAMETERS
#------------------------------------------------------------------------------------------


# Retrieving data from base carbone and caching the result for streamlit reuse
@st.cache(allow_output_mutation=True)
def get_basecarbone():
    PATH = "data/raw/base_carbone.csv"
    baca = BaseCarbone(PATH)
    return baca
baca = get_basecarbone()


#------------------------------------------------------------------------------------------
# SIDEBAR
#------------------------------------------------------------------------------------------

st.sidebar.image("docs/logo-blanc-jaune.svg")
st.sidebar.write("## CARBONIFY 🌎")

#------------------------------------------------------------------------------------------
# MAIN PAGE
#------------------------------------------------------------------------------------------

st.write("# Carbonify - Base Carbone")
st.write("## Rechercher une donnée carbone")
st.write("Recherchez une information particulière pour observer la visualisation et facilement trouver votre donnée carbone.\nEssayez avec *train* 🚅 ou *avion* ✈")
st.write("")



query = st.text_input("Recherche carbone")
if query != "":

    results,fig = baca.search(query,kind = "treemap",color_by_emissions = True,height = 600)
    st.plotly_chart(fig,use_container_width = True)
    st.write("Retrouvez ces mêmes informations dans un tableau")
    st.write(results)

st.write("## Exploration de la base carbone")
st.write("La [Base Carbone](https://data.ademe.fr/datasets/base-carbone(r)) de l'ADEME contient de nombreuses données carbone catégorisées dans une hiérarchie complexe:")

fig = baca.show_data(kind = "treemap",color_by_emissions = False,height = 800)
st.plotly_chart(fig,use_container_width = True)



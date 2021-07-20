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



st.write("## Comparateur d'émissions")

comp1 = st.text_input("Entrez un ID de la base carbone")
comp2 = st.text_input("Entrez un autre ID de la base carbone à comparer avec le premier")

if comp1 != "" and comp2 != "":
    comp1 = int(comp1)
    comp2 = int(comp2)

    comparison,element1,element2 = baca.compare(comp1,comp2,metadata = True,raise_unit_error = False)
    if comparison < 1:
        comparison = 1/comparison
        element1,element2 = element2,element1

    st.success(f"{element1['full_name']} ({element1['unit']}) émet {comparison:.3f} fois plus que {element2['full_name']} ({element2['unit']}) ")

st.write("## Calculateur d'émissions")
ratio_id = st.text_input("Entrez un ID de la base carbone à considérer pour le ratio_id")
factor = st.number_input("Entrez la valeur à multiplier au ratio_id pour obtenir les émissions (par exemple la distance pour des émissions / km")

if ratio_id != "":
    ratio_id = int(ratio_id)
    emissions_ratio = baca.search_by_id(ratio_id)
    emissions = emissions_ratio["emissions"] * factor

    st.success(f"**{emissions:.3f}** kCO2eq émis en utilisant le ratio **{emissions_ratio['full_name']}** *(en {emissions_ratio['unit']}*)")


st.write("## Exploration de la base carbone")
st.write("La [Base Carbone](https://data.ademe.fr/datasets/base-carbone(r)) de l'ADEME contient de nombreuses données carbone catégorisées dans une hiérarchie complexe:")

fig = baca.show_data(kind = "treemap",color_by_emissions = False,height = 800)
st.plotly_chart(fig,use_container_width = True)
import pandas as pd
import plotly.express as px
from nltk.tokenize import wordpunct_tokenize

class BaseCarbone:
    def __init__(self,path,lang = "français"):

        self.lang = lang
        self.data,self._category_cols = self._prepare_data(path,lang)

    @property
    def categories(self):
        return self.data[self._category_cols]

    def _prepare_data(self,path,lang):

        def clean_text_split(text):
            tokens = wordpunct_tokenize(text)
            tokens = [x for x in tokens if len(x) > 2]
            return tokens

        # Reading and filtering columns in other languages
        data = pd.read_csv(path,sep = ";",encoding = "latin1",low_memory = False)
        data = data[[x for x in data.columns if "espagnol" not in x and "anglais" not in x]]

        # Rename columns to more user friendly col names 
        data = data.rename(columns = {
            f"Tags {lang}":"tags",
            "Code de la catégorie":"category",
            f"Nom base {lang}":"name_base",
            f"Nom attribut {lang}":"name_attribute",
            f"Nom frontière {lang}":"name_attribute2",
            "Type de l'élément":"element_type",
            "Statut de l'élément":"element_status",
            "Structure":"structure",
            "Identifiant de l'élément":"element_id",
            "Type Ligne":"row_type",
            f"Unité {lang}":"unit",
            "Localisation géographique":"geography",
            f"Sous-localisation géographique {lang}":"subgeography",
            "Total poste non décomposé":"emissions",
        })

        # Filter archived rows
        data = data.loc[data["element_status"].str.lower().str.contains("valide")]
        data = data.reset_index(drop = True)

        # Clean text fields, concatenate and propertly tokenize for indexation
        data["name_base"] = data["name_base"].str.replace('"',"").str.strip()
        data["tags"] = data["tags"].str.replace('"',"").str.strip()
        data["text"] = data[["name_base","name_attribute","tags","category"]].apply(lambda x : " ".join(x.dropna()),axis = 1).str.lower()
        data["text_split"] = data["text"].map(clean_text_split)
        data["name"] = data[["name_base","name_attribute"]].apply(lambda x : " ".join(x.dropna()),axis = 1)
        data["full_name"] = data[["name_base","name_attribute","name_attribute2"]].apply(lambda x : " ".join(x.dropna()),axis = 1)
        data["emissions_clean"] = data[["unit","emissions"]].apply(lambda x : f"{x['emissions']} ({x['unit']})",axis = 1)

        # Convert emissions to numeric
        def convert_to_num(x):
            try:
                return float(x.replace(",","."))
            except:
                return x

        data["emissions"] = data["emissions"].map(convert_to_num)

        # Add categories to the columns
        categories = (data["category"]
            .str.split(" > ")
            .apply(pd.Series)
        )
        category_cols = [f"category{i+1}" for i in range(len(categories.columns))]
        categories.columns = category_cols
        data = pd.concat([data,categories],axis = 1)

        return data,category_cols

    def show_data(self,data = None,kind = "treemap",detailed_path = False,color_by_emissions=True,**kwargs):

        assert kind in ["treemap","sunburst","icicle"]

        # Take all data if not provided
        if data is None:
            data = self.data

        # Remove category cols with all NaNs
        all_nans = data[self._category_cols].isnull().sum() == len(data)
        all_nans = all_nans[all_nans].index.tolist()
        data = data.drop(columns = all_nans)
        category_cols = [x for x in self._category_cols if x not in all_nans]

        # Fill NaN for visualization
        data = data.fillna(" ")

        if detailed_path:
            path = [px.Constant("all")] + category_cols + ["name_base","name_attribute","name_attribute2","geography","subgeography"]
        else:
            path = [px.Constant("all")] + category_cols + ["name_base"]

        params = {
            # "values":"emissions",
            "hover_data":["emissions","unit"],
        }

        if color_by_emissions:
            params.update({
                "color":"emissions",
                "color_continuous_scale":"RdBu_r",
            })

        # Treemap visualization (also called Mondrian)
        if kind == "treemap":
            fig = px.treemap(data,path = path,maxdepth = 6,**params,**kwargs)
            
            if color_by_emissions:
                fig.update_traces(
                    root_color="lightgrey",
                    hovertemplate="<b>%{label}</b> - Count: %{value}<br>Emissions: %{color}"
                )

            return fig

        # Sunburst visualization (circular structure chart)
        elif kind == "sunburst":
            fig = px.sunburst(data,path = path[1:],maxdepth = 4,**params,**kwargs)
            return fig

        # icicle visualization (rectangular structure chart)
        elif kind == "icicle":
            fig = px.icicle(data,path = path[1:],maxdepth = 4,**params,**kwargs)
            fig.update_traces(root_color="lightgrey")
            return fig 


    def search(self,query,kind = None,without_split = True,color_by_emissions = True,**kwargs):

        results = self.data.loc[self.data["text_split"].map(lambda x : query in x)].copy()

        if without_split:
            results = results.query("row_type=='Elément'")
        
        # If no visualization
        if kind is None:
            return results
        else:
            fig = self.show_data(data = results.copy(),kind = kind,detailed_path = True,color_by_emissions = color_by_emissions,**kwargs)
            fig.update_layout(title=f"Base Carbone results for query='{query}'")
            return results,fig
            

    def search_word(self,query):
        return self.data.loc[self.data["text"].str.contains(query)]


    # def show_treemap(self,)
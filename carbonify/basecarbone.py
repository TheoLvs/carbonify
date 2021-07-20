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
            "custom_data":["element_id","emissions","unit"],
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
                    hovertemplate="<b>%{label}</b> - Count: %{value}<br>Emissions: %{color:.5f} %{customdata[2]}<br>Id: %{customdata[0]}"
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


    def search_by_id(self,element_id,return_value = False,print_unit = True):
        results = self.data.query(f"element_id=={element_id} and row_type=='Elément'")
        assert len(results) == 1
        results = results.iloc[0]

        name = results["full_name"]
        value = results["emissions"]
        unit = results["unit"]

        if return_value:
            if print_unit: print(results["unit"])
            return results["emissions"]
        else:
            return results[["full_name","emissions","unit"]].to_dict()

    def compare(self,element_id,with_id,raise_unit_error = True,metadata = True):

        element = self.search_by_id(element_id,return_value = False)
        with_element = self.search_by_id(with_id,return_value = False)

        if element["unit"] != with_element["unit"]:
            message = f"Warning - First element unit is {element['unit']} and second one is {with_element['unit']}"
            if raise_unit_error:
                raise Exception(message)
            else:
                print(message)

        comparison = element["emissions"] / with_element["emissions"]

        if metadata:
            return comparison,element,with_element
        else:
            return comparison



    def evaluate_transportation_by_plane(self,distance,condensation_trails = True,round_trip = False,cargo = False):
        """
        HYPOTHESIS 
        
        > Long and short courriers
        - Les courts courriers ont un rayon d’action d’environ 500 kilomètres (ex : avions à hélices) : il s'agit de liaisons entre villes françaises (métropole) par exemple.
        - Les moyens courriers ont un rayon d’action de 5000 kilomètres (Pour Air France, ils correspondent aux vols desservant l’Europe et l’Afrique du Nord). Exemple : A320.
        - Les longs courriers sont des avions de ligne pouvant voler sur 15 000 kilomètres de distance. Il s'agit de vols transocéaniques par exemple. Exemple : A340.
        Source https://www.bilans-ges.ademe.fr/forum/viewtopic.php?t=4192

        > Trails 
        https://www.carbone4.com/trainees-de-condensation-impact-climat

        > Cargo
        We assume big cargos above 100T
        We also suppose cargos are full with 100T load
        """

        # Ids in the Base Carbone for plane transportation
        if not cargo:
            SHORT_IDS = (28130,28129)
            MID_IDS = (28132,28131)
            LONG_IDS = (28134,28133)
        else:
            SHORT_IDS = (28065,28066)
            MID_IDS = (28063,28064)            
            LONG_IDS = (28055,28056)

        # Condensation trails filter
        condensation_idx = 0 if condensation_trails else 1

        # Find the right id for short, medium and long trips
        if distance < 500:
            element_id = SHORT_IDS[condensation_idx]
        elif distance < 5000:
            element_id = MID_IDS[condensation_idx]
        else:
            element_id = LONG_IDS[condensation_idx]

        # Prepare emissions ratio
        emissions_ratio = self.search_by_id(element_id)["emissions"]

        # Compute final emissions
        emissions = emissions_ratio * distance

        # Add round trip bonus
        if round_trip:
            emissions *= 2
        
        return emissions


    def evaluate_transportation_by_train(self,distance,tgv = True):
        pass

        

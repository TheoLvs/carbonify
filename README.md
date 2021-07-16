# Carbonify
## Open source library for carbon accounting and Lifecycle analysis
![](docs/assets/banner_carbonify.png)

Manipulating carbon data is complex and requires both climate expertise and the knowledge of the right data source to make valid hypothesis.

The **Carbonify** python library and tools are aimed to democratize data manipulation of carbon data to facilitate accounting and lifecycle analysis.  


!!! warning "Experimental"
    This library is extremely experimental, under active development and alpha-release
    Don't expect the documentation to be up-to-date or all features to be tested
    Please contact [us](mailto:theo.alvesdacosta@ekimetrics.com) if you have any question


## Features
### Current features
- Easy access to Base Carbone by ADEME with data indexing
- Data visualization and search functionalities to easily find carbon ratios


## Installation
### Install from PyPi
The library is available on [PyPi](https://pypi.org/project/carbonify/) via 
```
pip install carbonify
```

### For developers
- You can clone the github repo / fork and develop locally
- Poetry is used for environment management, dependencies and publishing, after clone you can run 

```
# To setup the environment
poetry install

# To run Jupyter notebook or a python console
poetry run jupyter notebook
poetry run python
```

## Contributors
- [Ekimetrics](https://ekimetrics.com/)



## Project Structure
```
- carbonify/ # Your python library
- data/
    - raw/
    - processed/
- docs/
- tests/                            # Where goes each unitary test in your folder
- scripts/                          # Where each automation script will go
- requirements.txt                  # Where you should put the libraries version used in your library
```


## References

### Base Carbone
- [Base Carbone](https://data.ademe.fr/datasets/base-carbone(r)) by ADEME - [Documentation](https://www.bilans-ges.ademe.fr/fr/accueil/contenu/index/page/presentation/siGras/0)
- [Agribalyse](https://data.ademe.fr/datasets/agribalyse-synthese) by ADEME - [Documentation](https://doc.agribalyse.fr/documentation/conditions-dusage-des-donnees)
- https://www.hellocarbo.com/blog/calculer/base-carbone/

### LCA 
- [CarbonFact.co](https://carbonfact.co/)
- https://www.carbonify.app/products/apple-iphone-12-us-64gb

### EDA components
- https://blog.streamlit.io/the-streamlit-agraph-component/
- https://github.com/ChrisChross/streamlit-agraph

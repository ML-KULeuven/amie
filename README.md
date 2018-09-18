# Automatic Monitoring of Indoor Exercises
Source code of our paper "AMIE: Automatic Monitoring of Indoor Exercises" at ECMLPKDD'18

The data can be dowloaded from https://dtai.cs.kuleuven.be/software/amie/amie-kinect-data.zip.
To use it, extract the hdf-file from the zip and place it in the data/ folder.


    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data               <- place 'amie-kinect-data.hdf' here
    │
    ├── notebooks          <- Jupyter notebooks.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make predictions
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations

# item-search

# Shopping Search Engine 

## Look for the ideal clothing items 😎

## Instructions

### Install libraries

`pip install -r requirements.txt`

### Run

`python app.py`

### Build and run container

Build container (uncomment launch call in app.py)

`docker build --tag item-search . `

Run container
`docker run -it -d --name item-search-engine -p 7000:7000  item-search:latest`

Structure
.

├── app.py
├── Dockerfile
├── LICENSE
├── README.md
├── search.py
└── requirements.txt
Author
Katana ML, Andrej Baranovskij

License
Licensed under the Apache License, Version 2.0. Copyright 2020-2021 Katana ML, Andrej Baranovskij. Copy of the license.
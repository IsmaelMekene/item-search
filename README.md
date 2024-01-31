# Shopping Search Engine 

## Description

Look for the ideal clothing items 😎

## Instructions

1. Install libraries

```
pip install -r requirements.txt
```

2. Run

```
python app.py
```

## Build and run container

1. Build container (uncomment launch call in app.py)

```
docker build --tag item-search .
```

2. Run container

```
docker run -it -d --name item-search-engine -p 7000:7000  item-search:latest
```

## Structure

```
.
├── app.py
├── Dockerfile
├── LICENSE
├── README.md
├── search.py
└── requirements.txt
```

## Author

[Ismael C.](https://ismaelmekene.com)
[GoogleColab](https://colab.research.google.com/drive/12oPiP2oKbww5LxLUeHup9YpwEh5ZtJOH?usp=sharing)

## License

Licensed under the MIT License, Version 2.0. 

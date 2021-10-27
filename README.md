# OpenCSMap

OpenCSMap is a system that reveals how Computer Science research is advancing all over the world. This system is intended to be a tool for researchers of CS to look for places to continue their careers (apply for jobs, PhD, MSc, etc.) or for linking with other researchers that may be near in the map and can collaborate. 

This system is divided in two parts. The first part was related to extracting and manipulating data from DBLP. We used XML snapshots available on their website and we linked authors-papers-affiliations. Then, we used OpenTapioca (Entity Linking) for obtaining structured data related to affiliations. OpenTapioca links to Wikidata entities so then we queried data from this knowledge base, taking as result coordinates of the affiliations, cities and countries. You can find example scripts in OpenTapioca and Wikidata folders.

The second part of this system is related to backend and frontend. Backend is mainly an Elasticsearch index, which we use for storing and querying papers' data that were indexed with the information retrieved in the part explained before. Frontend was developed using Django and Bootstrap. We used Leaflet library for showing results in a map layout.

A demo of the system is available at http://opencsmap.dcc.uchile.cl

## Setup

If you want to run the system locally, we suggest the following steps.

0.a) Download Docker

We use Docker to run Elasticsearch. For downloading please go to https://docs.docker.com/get-docker/. After that it's important to download Docker-compose (go to https://docs.docker.com/compose/install/)

0.b) Python, virtual enviorenment and requirements

Project is Python based. In order to work properly, we suggest installing >Python 3.6. Create a virtual enviorenment with something like:

`python3 -m venv OpenCSMap-env`

and then activate it with (Linux based OS):

`source OpenCSMap-env/bin/activate`

Then go to backend>requirements.txt file and run:

`pip3 install -r requirements.txt`

This will install all the packages needed.

1) Install Elasticsearch

In elasticsearch>install folder you will find a `docker-compose.yml` file. If this is the first time installing Elasticsearch via docker-compose, you have to run the following command:

`docker-compose up --build`

Sometimes it may fail because of virtual machine settings. If so, copy the command in the README.md of the same folder. Then try to run docker-compose command again. If lucky, Elasticsearch will be now installed in your machine. You can go to http://localhost:9200/ and a message of "You know, for search" must be displayed. 

Note: docker-compose file also installs 2 tools that are useful when using Elasticsearch. One is Kibana, a UI for managing indexes and querying them. The second one is Cerebro, a tool for managing all low-level configurations of the Elasticsearch instance. They are not important for our purpose so feel free to erase those lines on the compose file.

2) Creating index and indexing data

Now that Elasticsearch is installed we need to create our DBLP papers index. For this, go to elasticsearch>config, where you will find the papers-config.json. This is a json file that the structure of the index, how into search some fields and some Natural Language Processing rules to follow. To create the index run the next command:

`curl -H "Content-Type: application/json" -s -XPUT "http://localhost:9200/papers/?pretty" --data-binary @../config/papers-config.json; echo`

If response in shell is something like "acknowledged" : true, ..." everything should be okay. Go to http://localhost:9200/_cat/indices and check if papers index is available.

Now for indexing the data we need to go to elasticsearch>data. There is a Python file that run a script that indexes all the data we need. Data is available here. You can go with full data or a sample. When downloading the file you want, put it on the same folder as index_es.py file. Then from the shell just run:

`python index_es.py dblp.txt`

This process may take a while. Progress will be shown in the shell. When indexing is finished, you can go to http://localhost:9200/papers/_count and check that field 'count' is greater than 0. If you use full data it must be near 5M and if you use sample data it may be 500.

3) Django

Now that Elasticsearch is ready we can run our Django project. For doing this you need to go to backend>OpenCSMap. In the terminal, run:

`python manage.py migrate`

That will create our models. They are not important in general but they are useful for keeping track of the searches that are done. Then run:

`python manage.py runserver`

This will run the server on http://localhost:8000 . And that's all, now OpenCSMap is running in your machine.

## Acknowledgments

We thank Daniel Diomedi and Henry Rosales. They show us the technical use of Entity Linking tools as OpenTapioca, DBPedia Spotlight and TagMe.


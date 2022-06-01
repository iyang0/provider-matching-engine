This is a back-end python project for matching/filtering service providers

# We're building a matching engine and need your help!

You are tasked with creating a light-weight service for sorting, ranking, and displaying a list of skilled service providers. Providers have several attributes which are filterable.

The service should factor in these attributes as well as factors related to the use of the service when generating results.

## User Stories

- I would like to be able to exclude/include certain providers from results based on their active property

- I would like to be able to filter through providers on a combination of any of their user traits

- I would like the order of results to adjust based on how many times a provider has been returned; surfacing providers who have been returned fewer times towards the front of the list.

- I would like higher ranked providers to always be surfaced towards the front of the list.

-----

# Setting up

In your terminal go to the root directory of this project. Have python3 and pip installed and run the following commands. 

`python3 -m venv venv` - this will create a virtual environment directory(venv) for python installations to not interfere with other projects.

`source venv/bin/activate` - this will turn on your virtual environment.

`pip3 install -r requirements.txt` - install the required packages for this project for this environment.
This is a back-end python project for matching/filtering service providers

## We're building a matching engine and need your help!

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

## Server

I have set up a simple server rendering a table display of the providers in `providers.json`. You can filter down the providers based on whatever conditions apply to those traits through a form. All of the code for the server runs on `app.py`

`flask run` - runs the server

## Provider_list

The `Provider_list` class is the backbone of the project which uses the pandas library to filter down the rows of data. It has a `providers` attribute which is the source list, and a `df` attribute which is a pandas dataframe used as a running filtered dataset. This class can be used independent of the server if need be for other programs with a json of providers.

### Methods

- `list() -> List[Provider]` - Returns a list representation of the current filtered dataframe, useful for services over the web as dataframes can't be sent over easily.

- `sort_rating(ascending = False):` - Sort the current dataframe by rating, by default descending order.

- `reset_df()` - Resets the filtered dataframe to the data shape from the source list

- `filter_by_str(trait:str, value: str)` - Filters out rows of data from current dataframe by whether the row contains a substring of (value) in the column/trait of (trait).

- `filter_by_sex(sex: str)` - Filters out rows of data from current dataframe if the provider is the same sex as what is input

- `filter_by_date(operator: str, date: str)` - Filters out rows of data from current dataframe by whether the row has a birthday that is before, after, or at the provided (date).

  (date) should be in "YYYY-MM-DD" format
        
  Which operation is determined by the (operator) input which can be the following: 'at' for equal, 'after' for greater than, or 'before' for less than.

- `filter_by_num(trait: str, operator: str, value: Union[int,float])` - Filters out rows of data from current dataframe by whether the row contains a number with greater than, less than, or equal value than the number (value) in the column/trait of (trait) parameter.

  which operation is determined by the (operator) which can be the following:'eq' for equal, 'gt' for greater than, or 'lt' for less than.

- `filter_active(active = True)` - Filters out rows of data from current dataframe by whether that provider is either active or inactive, by default selects active.

- `filter_by_skills(skills: List[str], primary=True)` - Filters out rows of data from current dataframe bywhether that provider has the skills in the (skills) list. 
  By default checks skills in primary_skills, will check secondary_skills if (primary) is false

-`filter(traits: Filter_Options)` - A combination filter, takes in a dictionary (traits) with what traits to filter by as key and other needed options and values to filter through as the value to filter through.

Example:

```python
providers = Providers_list("providers.json")

options = {
    "rating" : ("gt", 5),
    "sex": "Male",
    "birth_date": ("before", "1990-01-01"),
    "primary_skills": ["Estimates"]
}
providers.filter(options).sort_rating().list()
```

and 

```python
providers = Providers_list("providers.json")

providers.filter_by_num("rating", "gt", 5)
        .filter_by_sex("Male")
        .filter_by_date("before", "1990-01-01")
        .filter_by_skills(["Estimates"], primary=True)
        .sort_rating()
        .list()
```

Both return the same sorted list by rating of provider dicts that are rated 5 or above that are male, that were born before 1990, and have Estimates as a primary skill.

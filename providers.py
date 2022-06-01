import json
from typing import List, Union
import pandas as pd
from helpers import intersection, unique_union
from providers_types import Filter_Options, Provider
from constants import STR_TRAITS

class Provider_list:
    def __init__(self, providers_json):
        """
        Create list and dataframe attribute from provided json file.
        Also creates primary_skills and secondary_skills attributes which are used
        for filtering providers by skill.
        """

        (self.providers, self.df) = Provider_list.get_providers(providers_json)
        (self.primary_skills, self.secondary_skills) = Provider_list.get_skills_dict(self.df)

    def __repr__(self):
        """
        Show Representation of how many rows and columns along with current dataframe.
        """

        return f"""<Provider_list object with {len(self.providers)} providers.>
        {len(self.df.index)} in current filtered dataFrame"""

    @staticmethod
    def get_providers(providers_json):
        """
        Takes the providers in providers.json and 
        returns a tuple of the list and dataframe representation
        """

        with open(providers_json) as json_file:
            providers_list: List[Provider] = json.load(json_file)
            providers_df = pd.DataFrame(providers_list)
            # Convert column to datetime64
            providers_df["birth_date"] = pd.to_datetime(providers_df["birth_date"],
                                                        format="%Y-%m-%d")

        return (providers_list, providers_df)

    @staticmethod
    def get_skills_dict(df: pd.DataFrame):
        """
        Takes in a dataframe with a primary_skills and secondary_skill column
        and returns a tuple with dicts of the skills as the keys and
        a list of the indexes for the rows of the df which has those skills as the value

        The returned list of index value used for df.iloc() method to return
        only providers with those skills
        """
        primary_skills: dict[str, list] = {}
        secondary_skills: dict[str, list] = {}

        for index, row in df[["primary_skills", "secondary_skill"]].iterrows():

            skill:str
            for skill in row["primary_skills"]:
                skill=skill.lower()
                if skill not in primary_skills:
                    primary_skills[skill] = []

                primary_skills[skill].append(index)

            for skill in row["secondary_skill"]:
                skill=skill.lower()
                if skill not in secondary_skills:
                    secondary_skills[skill] = []

                secondary_skills[skill].append(index)

        return (primary_skills, secondary_skills)

    def list(self) -> List[Provider]:
        """
        Return a list representation of the current filtered dataframe
        """

        # Convert datetime column into a string column
        converted_df = self.df.copy()
        converted_df["birth_date"] = converted_df["birth_date"].astype(str)
        df_list = []

        for index, row in converted_df.iterrows():
            df_list.append(row.to_dict())

        return df_list

    def sort_rating(self, ascending = False):
        """
        Sort the current dataframe by rating, by default descending order.
        """

        self.df = self.df.sort_values(by=['rating'], ascending=ascending)
        return self

    def reset_df(self):
        """
        Resets the filtered dataframe to the data shape from the source list
        """

        self.df = pd.DataFrame(self.providers)
        return self

    def filter_by_str(self, trait:str, value: str):
        """
        Filters out rows of data from current dataframe
        by whether the row contains a substring of <value>
        in the column/trait of <trait>.
        """

        self.df = self.df[self.df[trait].str.contains(value, case=False)]
        return self

    def filter_by_sex(self, sex: str):
        """
        Filters out rows of data from current dataframe
        by what sex the provider is
        """

        self.df = self.df[self.df["sex"] == sex]
        return self

    def filter_by_date(self, operator: str, date: str):
        """ 
        Filters out rows of data from current dataframe
        by whether the row has a birthday that is
        before, after, or at the provided <date>.

        <date> should be in "YYYY-MM-DD" format
        
        Which operation is determined by the <operator> which can be the following:
        'at' for equal, 'after' for greater than, or 'before' for less than.
        """

        if operator == "at":
            self.df = self.df.loc[self.df["birth_date"] == date]
        elif operator == "after":
            self.df = self.df.loc[self.df["birth_date"] > date]
        elif operator == "before":
            self.df = self.df.loc[self.df["birth_date"] < date]
        else:
            print("That operation is not used. use at, after, or before instead")

        return self

    def filter_by_num(self, trait: str, operator: str, value: Union[int,float]):
        """
        Filters out rows of data from current dataframe
        whether the row contains a number with
        greater than, less than, or equal value than the number <value>
        in the column/trait of <trait> parameter.
        
        which operation is determined by the <operator> which can be the following:
        'eq' for equal, 'gt' for greater than, or 'lt' for less than.
        """

        if operator == "eq":
            self.df = self.df[self.df[trait] == value]
        elif operator == "gt":
            self.df = self.df[self.df[trait] > value]
        elif operator == "lt":
            self.df = self.df[self.df[trait] < value]
        else:
            print("That operation is not used. use eq, gt, or lt instead")
        return self

    def filter_active(self, active = True):
        """
        Filters out rows of data from current dataframe
        by whether that provider is either active or inactive,
        by default selects active
        """

        self.df = self.df.loc[self.df['active'] == active]
        return self

    def filter_by_skills(self, skills: List[str], primary=True):
        """ 
        Filters out rows of data from current dataframe by
        whether that provider has the skills in the <skills> list. 
        By default checks skills in primary_skills,
        will check secondary_skills if <primary> is false
        """

        providers_index = []

        for skill in skills:

            skill = skill.lower()
            skills_intersection : list

            if primary:
                if skill in self.primary_skills:
                    # Get the intersection of providers with relevant skill
                    # and providers that are in current dataframe otherwise
                    # there will be an out of bounds access error for trying to
                    # access a provider with a skill that has been previously
                    # filtered out through a different method
                    skills_intersection = intersection( self.df.index,
                                                        self.primary_skills[skill])
                else:
                    print(f"{skill} is not in list of primary skills")

            else:
                if skill in self.secondary_skills:
                    skills_intersection = intersection( self.df.index,
                                                        self.secondary_skills[skill])
                else:
                    print(f"{skill} is not in list of secondary skills")
            
            # prevent duplicates by getting uniques instead of just adding to list
            providers_index = unique_union(providers_index, skills_intersection)

        # gets rows of providers based on list of indexes by which indexes have skills
        self.df = self.df.iloc[providers_index]
        return self

    def filter(self, traits: Filter_Options):
        """ takes in a dictionary <traits> with what traits to filter by as key
        and other needed options and values to filter through as the value
        to filter through multiple different traits.

        e.g. traits = {
            "rating" : ("gt", 5),
            "sex": "Male",
            "birth_date": ("before", "1990-01-01")
            "primary_skills": ["Estimates"]
        }

        the above examlple will filter all of the providers 
        that are male, has a rating greater than 5,
        has "Estimates" as a primary skill, and a birthday before 1990
        """

        for trait in traits:

            if trait == "id" or trait == "rating":
                id_op, id_val = traits[trait]
                self.filter_by_num(trait, id_op, id_val)

            if trait in STR_TRAITS:
                search_val = traits[trait]
                self.filter_by_str(trait, search_val)

            if trait == "sex":
                sex = traits[trait]
                self.filter_by_sex(sex)

            if trait == "primary_skills":
                skills = traits[trait]
                self.filter_by_skills(skills, primary=True)

            if trait == "secondary_skills":
                skills = traits[trait]
                self.filter_by_skills(skills, primary=False)

            if trait == "active":
                active = traits[trait]
                self.filter_active(active)

            if trait == "birth_date":
                id_op, id_val = traits[trait]
                self.filter_by_date(id_op, id_val)
            
        return self

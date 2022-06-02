from providers import ProviderList
from constants import TEST_JSON, TRAITS
from unittest import TestCase
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd

class GetProvidersStaticTest(TestCase):

    providers, df = ProviderList.get_providers(TEST_JSON)

    def test_columns_in_dataframe(self):
        columns = {*TRAITS, "returned"}
        df_columns = {*self.df.columns}
        assert df_columns == columns

    def test_initialize_with_empty_returned_column(self):
        assert (self.df["returned"]==0).all()

    def test_birth_date_col_is_datetime(self):
        assert is_datetime(self.df["birth_date"])

    def test_source_list_has_no_return_column(self):
        assert "returned" not in self.providers[0].keys()

class GetskillsStaticTest(TestCase):

    providers, df = ProviderList.get_providers(TEST_JSON)
    primary_skills, secondary_skills = ProviderList.get_skills_dict(df)

    def test_skills_in_dict_are_lowered(self):
        assert "testlowercase" in self.primary_skills

    def test_seeded_skill_in_primary_dict(self):
        assert "test primary skill" in self.primary_skills

    def test_seeded_skill_in_secondary_dict(self):
        assert "test secondary skill" in self.secondary_skills

    def test_user_has_seeded_skills(self):
        test_primary_users = self.primary_skills.get("test primary skill")
        test_secondary_users = self.secondary_skills.get("test secondary skill")

        assert 0 in test_primary_users
        assert 0 in test_secondary_users

class InitTest(TestCase):
    
    def test_init(self):
        providers = ProviderList(TEST_JSON)
        assert type(providers.providers) == list
        assert len(providers.providers) == 3
        assert providers.providers[0]["first_name"] == "test_first_name"
        assert providers.df["first_name"].values[0] == "test_first_name"
        assert "test primary skill" in providers.primary_skills

class InternalIncrementerTest(TestCase):
    
    providers = ProviderList(TEST_JSON)
    called = 0

    def increment(self):
        self.providers._increment_returned_counter()
        InternalIncrementerTest.called += 1

    def test_increment_returned(self):
        self.increment()
        assert all(self.providers.returned == InternalIncrementerTest.called)

    def test_dataframe_returned(self):
        self.increment()
        assert all(self.providers.df["returned"] == InternalIncrementerTest.called)

    def test_subset_increment_works(self):
        self.providers.df = self.providers.df.loc[self.providers.df['active']]
        test_list = [InternalIncrementerTest.called for n in range(3)]

        self.increment()

        test_list[0] += 1
        test_series = pd.Series(test_list)

        assert all(self.providers.returned == test_series)


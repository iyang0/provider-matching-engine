from providers import ProviderList
from constants import TEST_JSON, TRAITS, DEFAULT_COLUMNS, DEFAULT_ORDER
from unittest import TestCase
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd

class GetProvidersStaticTest(TestCase):

    def setUp(self):
        self.providers, self.df = ProviderList.get_providers(TEST_JSON)

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

    def setUp(self):
        self.providers, self.df = ProviderList.get_providers(TEST_JSON)
        self.primary_skills, self.secondary_skills = ProviderList.get_skills_dict(self.df)

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
    
    def setUp(self):
        self.providers = ProviderList(TEST_JSON)
        self.called = 0

    def increment(self):
        self.providers._increment_returned_counter()
        self.called += 1

    def test_increment_returned(self):
        self.increment()
        assert all(self.providers.returned == self.called)

    def test_dataframe_returned(self):
        self.increment()
        assert all(self.providers.df["returned"] == self.called)

    def test_subset_increment_works(self):
        self.providers.df = self.providers.df.loc[self.providers.df['active']]
        test_list = [self.called for n in range(3)]

        self.increment()

        test_list[0] += 1
        test_series = pd.Series(test_list)

        assert all(self.providers.returned == test_series)

class ListMethodTest(TestCase):

    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_list_same_as_source_without_change(self):
        assert self.providers.providers == self.providers.list()

    def test_list_has_returned_column_if_True(self):
        assert "returned" in self.providers.list(with_returned=True)[0]

    def test_only_lists_current_dataframe(self):
        self.providers.df = self.providers.df.loc[self.providers.df['active']]
        assert len(self.providers.list()) == 1

class sortRatingTest(TestCase):

    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_descending_sort(self):
        self.providers.sort_rating(ascending=False)
        head = self.providers.df["rating"].head(1).values[0]
        tail = self.providers.df["rating"].tail(1).values[0]
        assert head > tail
    
    def test_ascending_sort(self):
        self.providers.sort_rating(ascending=True)
        head = self.providers.df["rating"].head(1).values[0]
        tail = self.providers.df["rating"].tail(1).values[0]
        assert head < tail
    
class SortColTest(TestCase):

    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_with_default(self):
        self.providers.sort(DEFAULT_COLUMNS, DEFAULT_ORDER)
        test_id_list = [3,2,1]

        assert test_id_list == list(self.providers.df["id"])
    #todo: test with other columns

class Reset_test(TestCase):

    def setUp(self):
        self.providers = ProviderList(TEST_JSON)
    
    def tearDown(self):
        self.providers.returned = 0

    def test_resets_df(self):
        self.providers.df = self.providers.df.loc[self.providers.df['active']]
        assert len(self.providers.df) == 1
        self.providers.reset()
        assert len(self.providers.df) == 3
    
    def test_reset_does_not_update_returned(self):
        self.providers._increment_returned_counter()
        assert all(self.providers.returned == 1)
        self.providers.reset()
        assert all(self.providers.returned == 1)

    def test_reset_does_not_update_returned_df_column(self):
        self.providers._increment_returned_counter()
        assert all(self.providers.df["returned"] == 1)
        self.providers.reset()
        assert all(self.providers.df["returned"] == 1)

    def test_deep_reset(self):
        self.providers._increment_returned_counter()
        assert all(self.providers.returned == 1)
        self.providers.reset(counter_reset=True)
        assert all(self.providers.returned == 0)
        assert all(self.providers.df["returned"] == 0)


from providers import ProviderList
from constants import TEST_JSON, TRAITS, DEFAULT_COLUMNS, DEFAULT_ORDER
from unittest import TestCase
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd
from unittest.mock import MagicMock

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

    def test_sorting_one_column(self):
        self.providers.sort(["first_name"], [False])
        test_id_list = [1,3,2]

        assert test_id_list == list(self.providers.df["id"])

    def test_sort_two_columns(self):
        self.providers.sort(DEFAULT_COLUMNS, DEFAULT_ORDER)
        test_id_list = [3,2,1]

        assert test_id_list == list(self.providers.df["id"])



class ResetTest(TestCase):

    def setUp(self):
        self.providers = ProviderList(TEST_JSON)
    
    def tearDown(self):
        self.providers.returned[:] = 0

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

class FilterStrTest(TestCase):
    
    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_str_column_filter(self):
        self.providers.filter_by_str("first_name","test_first_name")

        assert len(self.providers.df) == 1
        assert self.providers.df["first_name"].values[0] == "test_first_name"

    def test_str_filter_gets_substrings(self):
        self.providers.filter_by_str("first_name","test")

        assert len(self.providers.df) == 1
        assert "test_first_name" in self.providers.df["first_name"].values

    def test_str_filter_gets_right_column(self):
        self.providers.filter_by_str("last_name","Solleme")

        assert len(self.providers.df) == 2
        assert "test_first_name" not in self.providers.df["first_name"].values

    def test_str_filter_increment_return(self):
        self.providers.filter_by_str("first_name","test_first_name")
        test_series = pd.Series([1, 0, 0])

        assert all(self.providers.returned == test_series)

class FilterSexTest(TestCase):
    
    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_sex_filter(self):
        self.providers.filter_by_sex("Female")

        assert len(self.providers.df) == 2

    def test_sex_filter_equality(self):
        self.providers.filter_by_sex("Male")

        assert "Female" not in self.providers.df["sex"]

    def test_sex_filter_increment_return(self):
        self.providers.filter_by_sex("Male")
        test_series = pd.Series([1, 0, 0])

        assert all(self.providers.returned == test_series)

class FilterDateTest(TestCase):
    
    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_date_filter_equal(self):
        self.providers.filter_by_date("at", "1951-03-16")

        assert len(self.providers.df) == 1
        assert "Alethea" in self.providers.df["first_name"].values
    
    def test_date_filter_before(self):
        self.providers.filter_by_date("before", "1951-03-16")

        assert len(self.providers.df) == 1
        assert "test_first_name" in self.providers.df["first_name"].values
    
    def test_date_filter_after(self):
        self.providers.filter_by_date("after", "1951-03-16")

        assert len(self.providers.df) == 1
        assert "Hettie" in self.providers.df["first_name"].values

    def test_date_filter_just_year(self):
        self.providers.filter_by_date("before", "1960")

        assert len(self.providers.df) == 2

    def test_date_filter_number_input_raises_err(self):
        self.assertRaises(TypeError, self.providers.filter_by_date, "before", 1960)

    def test_date_filter_increment_return(self):
        self.providers.filter_by_date("at", "1934-12-07")
        test_series = pd.Series([1, 0, 0])

        assert all(self.providers.returned == test_series)

class FilterNumTest(TestCase):

    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_num_filter_equal(self):
        self.providers.filter_by_num("rating","eq", 7.9)

        assert len(self.providers.df) == 1
        assert "Alethea" in self.providers.df["first_name"].values
    
    def test_num_filter_greater(self):
        self.providers.filter_by_num("rating", "gt", 8)

        assert len(self.providers.df) == 1
        assert "Hettie" in self.providers.df["first_name"].values
    
    def test_num_filter_less(self):
        self.providers.filter_by_num("rating","lt", 7)

        assert len(self.providers.df) == 1
        assert "test_first_name" in self.providers.df["first_name"].values

    def test_num_filter_increment_return(self):
        self.providers.filter_by_num("id", "eq", 1)
        test_series = pd.Series([1, 0, 0])

        assert all(self.providers.returned == test_series)

class FilterActiveTest(TestCase):

    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_active_filter(self):
        self.providers.filter_active()

        assert len(self.providers.df) == 1
        assert "test_first_name" in self.providers.df["first_name"].values

    def test_inactive_filter(self):
        self.providers.filter_active(False)

        assert len(self.providers.df) == 2

    def test_num_filter_increment_return(self):
        self.providers.filter_active()
        test_series = pd.Series([1, 0, 0])

        assert all(self.providers.returned == test_series)

class FilterSkillsTest(TestCase):
    
    def setUp(self):
        self.providers = ProviderList(TEST_JSON)

    def test_skill_filter_primary(self):
        self.providers.filter_by_skills(["test primary skill"], primary=True)

        assert len(self.providers.df) == 1
        assert "test_first_name" in self.providers.df["first_name"].values

    def test_skill_filter_secondary(self):
        self.providers.filter_by_skills(["test secondary skill"], primary=False)

        assert len(self.providers.df) == 2
        assert "test_first_name" in self.providers.df["first_name"].values
        assert "Hettie" in self.providers.df["first_name"].values
        

    def test_skill_filter_increment_return(self):
        self.providers.filter_by_skills(["test primary skill"], primary=True)
        test_series = pd.Series([1, 0, 0])

        assert all(self.providers.returned == test_series)

class FilterCombinationTest(TestCase):

    def setUp(self):
        self.providers = ProviderList(TEST_JSON)
        self.options = {
            "sex": "Female",
            "secondary_skills": ["test secondary skill"]
        }

    def test_multi_filter(self):
        self.providers.filter(self.options)

        assert "Hettie" in self.providers.df["first_name"].values

    def test_multi_filter_calls_other_methods(self):
        self.providers.filter_by_sex = MagicMock(return_value = self)
        self.providers.filter_by_skills = MagicMock(return_value = self)
        self.providers.filter_active = MagicMock(return_value = self)
        self.providers.filter(self.options)

        self.providers.filter_by_sex.assert_called()
        self.providers.filter_by_skills.assert_called()
        self.providers.filter_active.assert_not_called()

    def test_multi_filter_nonexistant_trait(self):
        nonexistant_trait = { "test": "value"}
        self.providers.filter(nonexistant_trait)
        test_series = pd.Series([0]*3)

        assert all(self.providers.returned == test_series)

    def test_multi_filter_increment_return(self):
        options = {
            "id": ("eq", 1),
            "first_name": "test_first_name",
            "primary_skills": ["test primary skill"]
        }
        self.providers.filter(options)
        test_series = pd.Series([3, 0, 0])

        assert all(self.providers.returned == test_series)
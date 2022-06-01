from providers_types import Filter_Options
from constants import STR_TRAITS

def intersection(lst1: list, lst2: list):
    """ returns list that is only unique shared values between the input lists"""
    return list(set(lst1) & set(lst2))

def unique_union(lst1: list, lst2: list):
    """ returns list that is all values of the two input lists with only unique values"""
    return list(set(lst1 + lst2))

def build_filter_option_from_form(form:dict):
    filters : Filter_Options = {}

    for trait in form.keys():

        if trait == "id_val" and form[trait] != "":
            id_option = form.get("id_option")
            id_val = int(form.get("id_val"))
            filters["id"] = (id_option, id_val)

        if trait in STR_TRAITS and form[trait] != "":
            filters[trait] = form.get(trait).capitalize()

        if trait == "sex" and form[trait] != "":
            filters[trait] = form.get("sex")

        if trait == "date_val" and form[trait] != "":
            date_option = form.get("date_option")
            date_val = form.get("date_val")
            filters["birth_date"] = (date_option, date_val)

        if trait == "rating_val" and form[trait] != "":
            rating_option = form.get("rating_option")
            rating_val = float(form.get("rating_val"))
            filters["rating"] = (rating_option, rating_val)

        if (trait == "primary_skills" or trait == "secondary_skills") and form[trait] != "":
            skills = form.get(trait).split(",")
            filters[trait] = skills

    return filters
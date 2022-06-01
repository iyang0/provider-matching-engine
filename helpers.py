def intersection(lst1: list, lst2: list):
    """ returns list that is only unique shared values between the input lists"""
    return list(set(lst1) & set(lst2))

def unique_union(lst1: list, lst2: list):
    """ returns list that is all values of the two input lists with only unique values"""
    return list(set(lst1 + lst2))

def build_filter_option_from_form(form:dict):
    return form
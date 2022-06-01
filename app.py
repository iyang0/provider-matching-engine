from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from providers import Provider_list
from constants import PROVIDER_JSON, FILTER_OPTIONS, STR_TRAITS, TRAITS, SEXES
from providers_types import Filter_Options

app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

providers = Provider_list(PROVIDER_JSON)

@app.route("/")
def root():
    """base case, show all the data."""

    providers.reset_df()
    providers_list = providers.sort_rating().list()

    return render_template("provider_list.html",
                            title = "List of Providers",
                            providers = providers_list)

@app.route("/filter", methods = ["POST", "GET"])
def filter():
    """provide a form to filter data by for get request
    otherwise, take form data and save it to filter options in session
    and redirect user to search with their filter options"""

    if request.method == "GET":
        return render_template("filter.html",
                                traits=TRAITS,
                                sexes=SEXES,
                                str_traits=STR_TRAITS)

    filters : Filter_Options = {}
    form = request.form

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

    session[FILTER_OPTIONS] = filters

    return redirect("/filtered")

@app.route("/filtered")
def filtered():
    """Show filtered list of providers based on filtered options,
    otherwise show all data"""

    filter_options = session.get(FILTER_OPTIONS)
    providers_list = []

    if filter_options is not None:
        providers_list = providers.filter(filter_options).sort_rating().list()
        providers.reset_df()
        session[FILTER_OPTIONS] = None
    else:
        providers_list = providers.sort_rating().list()

    return render_template("provider_list.html",
                            title = "List of Filtered Providers",
                            providers = providers_list)


@app.errorhandler(404)
def not_found(err):
    flash("You tried to access a page that does not exist")
    return redirect("/")

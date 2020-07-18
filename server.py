import json

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sqlalchemy import or_, and_, text

from covid19.models import Location, Case, init_db, session

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

""" 
    Database Setup Code
"""

init_db()
db_session = session()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



"""
    Flask App

    Several APIs here:
    - /locations - returns a list of all locations.
        - support query param filter by country/state/county
        - AND / OR semantics are fixed
    - /cases - returns a timeseries of case records.
        - support multiple location filters, OR them all
        - support ?location.state= ?location.country= ?location.county= filters
        - (no) support date range filters ?start=_&end=_
        - (no) support an ?agg filter. default to "sum"
        - include some of my tabulations
"""


@app.route('/')
def hello_world():
    return send_from_directory('templates', 'home.html')

@app.route("/location", methods=['GET'])
def locations():
    country = request.args.to_dict(flat=False).get('country', [])
    state = request.args.to_dict(flat=False).get('state', [])
    county = request.args.to_dict(flat=False).get('county', [])
    result = db_session.query(Location).filter(
        and_(
            or_(
                Location.country.in_(country),
                [] == country
            ),
            or_(
                Location.state.in_(state),
                [] == state
            ),
            or_(
                Location.county.in_(county),
                [] == county
            )
        )

    )
    r = [l.json() for l in result]
    return jsonify(r)

# determine validity of query param integers
def valid_int(i, default):
    out = default

    # must be a valid int
    try:
        out = int(i)
    except:
        pass

    # must be non-zero
    if out <= 0:
        out = default

    return out

@app.route("/cases", methods=["GET"])
def cases():
    country = request.args.to_dict(flat=False).get('country', [])
    state = request.args.to_dict(flat=False).get('state', [])
    county = request.args.to_dict(flat=False).get('county', [])


    case_duration = valid_int(request.args.get('case_duration'), 12)
    cgr_window = valid_int(request.args.get('cgr_window'), 5)



    s = text("""
           WITH cte AS (
            SELECT
                    date_trunc('day', date) as date,
                    cast(sum(pop) as float) as pop,
                    cast(sum(confirmed) as float) as cases,
                    cast(sum(deaths) as float) as deaths
            FROM cases c 
                JOIN locations l ON c.location_id = l.id
            WHERE 1=1
                AND NOT l.state = 'Recovered'
                AND c.active >=0
                AND (
                    (l.country IN :country OR :empty_country) 
                    AND
                    (l.state IN :state OR :empty_state)
                    AND
                    (l.county IN :county OR :empty_county)
                )
                --AND l.county IN ('Denver', 'Jefferson', 'Arapahoe', 'Adams', 'Douglas', 'Broomfield', 'Boulder')
                --AND l.county IN ('Summit', 'Eagle', 'Park', 'Grand', 'Lake', 'Clear Creek')
            GROUP BY date_trunc('day', date)
            ORDER BY date ASC
            )
            SELECT
                    date,
                    cases,
                    deaths,
                    pop,

                    (cases / pop) * 100000 as incidence,

                    (cases - lag(cases, 1) over (
                            ORDER BY date
                    )) as new_cases,

                    (deaths - lag(deaths, 1) over (
                            ORDER BY date
                    )) as new_deaths,


                    (cases - lag(cases, :active_case_duration) over (
                            ORDER BY date
                    )) as active_cases,

                    (
                        (cases - lag(cases, :active_case_duration) over (
                            ORDER BY date
                            ))
                        /
                        (lag(cases, :cgr_window)  over (ORDER BY date) - lag(cases, :cgr_window + :active_case_duration) over (
                            ORDER BY date
                        ))
                    ) ^  (1.0/5.0) * 100 as cgr


            FROM cte
        """
    )
    from sqlalchemy.dialects.postgresql import array, ARRAY
    from sqlalchemy import String, cast

    resp = db_session.execute(s, params={
        "country": tuple(country) or tuple("_"),
        "state": tuple(state) or tuple("_"),
        "county": tuple(county) or tuple("_"),
        "empty_country": len(country) == 0,
        "empty_state": len(state) == 0,
        "empty_county": len(county) == 0,
        "active_case_duration": case_duration,
        "cgr_window": cgr_window
        }
    ).fetchall()
    out = [case(r) for r in resp]
    # out = [c for c in out if c["cgr"]]
    return jsonify(out)

def case(case_row):
    # date,cases,deaths,prev_week,new_cases,new_deaths,active_cases,cgr
    return {
        "date": case_row[0],
        "cases": case_row[1],
        "deaths": case_row[2],
        "pop": case_row[3],
        "incidence": case_row[4],
        "new_cases": case_row[5],
        "new_deaths": case_row[6],
        "active_cases": case_row[7],
        "cgr": case_row[8]
    }

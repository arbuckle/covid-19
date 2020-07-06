import json

from flask import Flask, jsonify, request
from sqlalchemy import or_, and_, text

from models import Location, Case, init_db, session

app = Flask(__name__)

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
    result = db_session.query(Location).first()
    s = result.json()
    return jsonify(s)


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
                    sum(confirmed) as cases,
                    sum(deaths) as deaths
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

                    cast(lag(cases, 7) over (
                            ORDER BY date
                    ) as float) as prev_week,

                    (cases - cast(lag(cases, 1) over (
                            ORDER BY date
                    ) as float)) as new_cases,

                    (deaths - cast(lag(deaths, 1) over (
                            ORDER BY date
                    ) as float)) as new_deaths,


                    (cases - cast(lag(cases, :active_case_duration) over (
                            ORDER BY date
                    ) as float)) as active_cases,

                    (
                        (cases - cast(lag(cases, :active_case_duration) over (
                            ORDER BY date
                            ) as float))
                        /
                        (lag(cases, :cgr_window)  over (ORDER BY date) - cast(lag(cases, :cgr_window + :active_case_duration) over (
                            ORDER BY date
                        ) as float))
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
    return jsonify(out)

def case(case_row):
    # date,cases,deaths,prev_week,new_cases,new_deaths,active_cases,cgr
    return {
        "date": case_row[0],
        "cases": case_row[1],
        "deaths": case_row[2],
        "new_cases": case_row[4],
        "new_deaths": case_row[5],
        "active_cases": case_row[6],
        "cgr": case_row[7]
    }

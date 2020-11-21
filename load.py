import os
import csv
import datetime
import requests
import urllib.parse

from sqlalchemy import desc
from models import *

expectedHeader = ['FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'Combined_Key']

dbhost = os.getenv('POSTGRES_SERVICE_HOST', '127.0.0.1')
dbuser = os.getenv('POSTGRES_USER', 'covid')
dbpass = os.getenv('POSTGRES_PASSWORD', '')

def match_header(header):
    # Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,FIPS,Incident_Rate,People_Tested,People_Hospitalized,Mortality_Rate,UID,ISO3,Testing_Rate,Hospitalization_Rate
    for i in expectedHeader:
        match = False
        for j in header:
            if i == j:
                match = True
                break
        if not match:
            return False
    return True

def retrieve(date):
    d = date.strftime('%m-%d-%Y')
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv" % d
    print("getting url - %s" % url)

    resp = requests.get(url)
    decoded_content = resp.content.decode('utf-8')
    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    cases_raw = list(cr)

    if len(cases_raw) < 2:
        print("no cases returned")
        return [], []

    for i, lol in enumerate(cases_raw[0]):
        cases_raw[0][i] = lol.strip().replace("\ufeff", "")
    if not match_header(cases_raw[0]):
        print("invalid header row")
        print("gott - ", cases_raw[0])
        print("want - ", expectedHeader)
        return [], []

    # generate two sets of data. one is a set of Case objects with no location_id set. the other is a set of locations, not unique or anything.
    cases, locations = [], []
    for row in cases_raw[1:]:
        l = Location(
            fips=row[0],
            county=row[1],
            state=row[2],
            country=row[3],
            lat=float((row[5] if row[5] else 0)),
            lon=float((row[6] if row[6] else 0)),
            combined=row[11]
        )

        c = Case(
            date=date,
            confirmed=parseValue(row[7], 'confirmed'),
            deaths=parseValue(row[8], 'deaths'),
            recovered=parseValue(row[9], 'recovered'),
            active=parseValue(row[10], 'active')
        )
        locations.append(l)
        cases.append(c)

    return cases, locations

def parseValue(n, kind):
    out = 0
    try:
        out = int(n)
    except ValueError as e:
        print("error parsing %s for %s" % (kind, n))
    return out

def main():

    init_db(dbhost, dbuser, dbpass)
    db_session = session()

    current = get_start_date(db_session)

    while current < datetime.date.today():
        load_date(current, db_session)
        current = current + datetime.timedelta(days=1)

def get_start_date(db_session):
    result = db_session.query(Case).order_by(desc(Case.date)).first()
    if not result:
        return datetime.date(2020, 3, 1)
    return result.date.date()

def load_date(date, db_session):
    # you have a pair of lists that are aligned on case and location.  
    # iterate locations to insert and get the id, then update the matched case, then insert the case
    cases, locations = retrieve(date)
    for idx, loc in enumerate(locations):
        if idx % 100 == 0:
            print("processing %d/%d records for %s" % (idx, len(locations), date))

        # select existing location record, or else insert
        result = db_session.query(Location).filter(
            Location.country == loc.country,
            Location.state == loc.state,
            Location.county == loc.county
        ).first()
        if result is None:
            print("creating location record", loc)
            db_session.add(loc)
            db_session.flush()
            location_id = loc.id
        else:
            location_id = result.id

        cases[idx].location_id = location_id
        # select or update case data
        result = db_session.query(Case).filter(
            Case.date == date,
            Case.location_id == cases[idx].location_id
        ).first()
        if result is None:
            db_session.add(cases[idx])
        elif result.confirmed > cases[idx].confirmed or result.deaths > cases[idx].deaths or result.recovered > cases[idx].recovered or result.active > cases[idx].active:
            print("updating case record", cases[idx])
            db_session.query(Case).filter(
                Case.id == result.id
            ).update({
                Case.confirmed: cases[idx].confirmed,
                Case.deaths: cases[idx].deaths,
                Case.recovered: cases[idx].recovered,
                Case.active: cases[idx].active
            })

    db_session.flush()
    db_session.commit()

if __name__ == "__main__":
    main()

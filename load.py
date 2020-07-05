import csv
import datetime
import urllib.parse

import requests

from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    fips = Column(String)
    county = Column(String)
    state = Column(String)
    country = Column(String)
    combined = Column(String)
    lat = Column(Float)
    lon = Column(Float)

    cases = relationship("Case")

    __table_args__ = (
        UniqueConstraint("country", "state", "county", name="unique_location"),
    )


    def __repr__(self):
        return "<Loc(Country='%s' State='%s' County='%s' Id='%s')>" % (self.country, self.state, self.county, self.id)

    def json(self):
        out = {
            "id": self.id,
            "fips": self.fips,
            "county": self.county,
            "state": self.state,
            "country": self.country,
            "combined": self.combined,
            "lat": self.lat,
            "lon": self.lon
        }
        return out

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    location_id = Column(Integer, ForeignKey('locations.id'))
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)
    active = Column(Integer)

    __table_args__ = (
        UniqueConstraint("date", "location_id", name="unique_date_place"),
    )
    def __repr__(self):
        return "<Case(Date=%s %d/%d/%d/%d)" % (self.date, self.confirmed, self.deaths, self.recovered, self.active)

def match_header(header):
    # Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,FIPS,Incident_Rate,People_Tested,People_Hospitalized,Mortality_Rate,UID,ISO3,Testing_Rate,Hospitalization_Rate
    expectedHeader = ['FIPS', 'Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Lat', 'Long_', 'Confirmed', 'Deaths', 'Recovered', 'Active', 'Combined_Key']
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
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv" % date
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
        try:
            active=int(row[10])
        except ValueError as e:
            print("error parsing active cases for %s" % row[11])
        active = 0
        c = Case(
            date=row[4],
            confirmed=int(row[7]),
            deaths=int(row[8]),
            recovered=int(row[9]),
            active=active
        )
        locations.append(l)
        cases.append(c)

    return cases, locations

def main():

    pw = ""
    with open(".password") as f:
        pw = f.read()
        pw = urllib.parse.quote_plus(pw)
    conn = "postgresql://covid:%s@localhost:5432/covid" % pw

    printLogs = False
    engine = create_engine(conn, echo=printLogs)

    # create all of the tables
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    # create a new instance for queries, etc
    session = Session()

    current = get_start_date(session)

    while current < datetime.date.today():
        d = current.strftime("%m-%d-%Y")
        load_date(d, session)
        current = current + datetime.timedelta(days=1)

def get_start_date(session):
    result = session.query(Case).order_by(desc(Case.date)).first()
    if not result:
        return datetime.date(2020, 6, 25)
    return result.date.date()

def load_date(date, session):
    # you have a pair of lists that are aligned on case and location.  
    # iterate locations to insert and get the id, then update the matched case, then insert the case
    cases, locations = retrieve(date)
    for idx, loc in enumerate(locations):
        if idx % 100 == 0:
            print("processing %d/%d records for %s" % (idx, len(locations), date))

        # select existing location record, or else insert
        result = session.query(Location).filter(
            Location.country == loc.country,
            Location.state == loc.state,
            Location.county == loc.county
        ).first()
        if result is None:
            print("creating location record", loc)
            session.add(loc)
            session.flush()
            location_id = loc.id
        else:
            location_id = result.id

        

        cases[idx].location_id = location_id
        # select or update case data
        result = session.query(Case).filter(
            Case.date == cases[idx].date,
            Case.location_id == cases[idx].location_id
        ).first()
        if result is None:
            session.add(cases[idx])
        elif result.confirmed != cases[idx].confirmed and result.deaths != cases[idx].deaths and result.recovered != cases[idx].recovered and result.active != cases[idx].active:
            print("updating case record", cases[idx])
            session.query(Case).filter(
                Case.id == result.id
            ).update({
                Case.confirmed: cases[idx].confirmed,
                Case.deaths: cases[idx].deaths,
                Case.recovered: cases[idx].recovered,
                Case.active: cases[idx].active
            })
        session.flush()

    session.commit()

if __name__ == "__main__":
    main()

import os
import csv
from sqlalchemy import update
from models import Location, init_db, session

def load_states(db_session):
    states_seen = {}
    with open('statepop.csv', newline='', encoding='ISO-8859-1') as f:
        r = csv.reader(f, delimiter=',')
        for row in r:
            if row[0] == 'SUMLEV':
                continue

            state = row[5]
            county = row[6]
            pop = row[18]

            if states_seen.get(state) is None:
                states_seen[state] = True
                continue

            if state == 'New York' and county == 'New York County':
                county = 'New York City'
            if state != 'New York':
                county = county.replace(" city", "")
            county = county.replace(" County", "")
            county = county.replace(" City and Borough", "")
            county = county.replace(" Parish", "")
            county = county.replace(" Census Area", "")
            county = county.replace(" Borough", "")
            county = county.replace(" Municipality", "")


            result = db_session.query(Location).filter(
                Location.country == "US",
                Location.state == state,
                Location.county == county
            ).first()

            q = update(Location).where(Location.id == result.id).values(pop=pop)
            db_session.execute(q)
            db_session.flush()

            print("updating %s/%s - %s" % (state, county, pop))
    db_session.commit()

def load_countries(db_session):
    with open('international_pop.csv', newline='', encoding='ISO-8859-1') as f:
        r = csv.reader(f, delimiter=',')
        for row in r:
            if row[0] == 'Region':
                continue
            if row[0].startswith('Less'):
                continue

            country = row[1]
            pop = row[3]

            result = db_session.query(Location).filter(
                Location.country == country,
                Location.state == ''
            ).all()

            proceed = False
            if len(result) > 1:
                print("few found - %s" % country)
            elif len(result) == 1:
                proceed = True
                print("one found - %s" % country)
            else:
                print("not found - %s" % country)

            if not proceed:
                continue
            id = result[0].id
            q = update(Location).where(Location.id == id).values(pop=pop)
            db_session.execute(q)
    db_session.flush()
    db_session.commit()


def main(do_states, do_countries):
    dbhost = os.getenv('POSTGRES_SERVICE_HOST', '127.0.0.1')
    dbuser = os.getenv('POSTGRES_USER', 'covid')
    dbpass = os.getenv('POSTGRES_PASSWORD', '')

    init_db(dbhost, dbuser, dbpass)
    db_session = session()

    if do_states:
        load_states(db_session)

    if do_countries:
        load_countries(db_session)


if __name__ == "__main__":
    states = os.getenv('DO_STATES', None)
    countries = os.getenv('DO_COUNTRIES', None)
    main(states is not None, countries is not None)

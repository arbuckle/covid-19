# covid data tracker

https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/04-08-2020.csv

scrape data from here and put into a database

also scrape data from colorado's covid site because i want that sooner! 

JHU publishes this daily: 

    FIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,Combined_Key


two tables really.  location, and case_ts


    location
    FIPS,Admin2,Province_State,Country_Region,Combined_KeyLat,Long

    cases
    Date,Location_ID,Confirmed,Deaths,Recovered,Active


Ultimately the stat I care about is the compound daily growth rate over an N-day window. 7 is likely the most accurate since it would include weekends. 

```
    WITH cte AS (
            SELECT
                    date as date,
                    sum(confirmed) as cases,
                    sum(deaths) as deaths
            FROM cases c JOIN locations l ON c.location_id = l.id
            WHERE l.state ilike 'colorado'
            GROUP BY date
            ORDER BY date ASC
    )
    SELECT
            date,
            cases,
            deaths,

            cast(lag(cases, 7) over (
                    ORDER BY date
            ) as float) as prev_week,

            (((cast(cases as float)/cast(lag(cases, 7) over (
                    ORDER BY date
            ) as float)) ^ (1.0/7.0)) * 100) as cdgr

    FROM cte
```

JHU changed their data format on the 22nd of march and before. Going back in time, need to aggregate cases on a per-state basis (maybe pin all cases to the capital city?) and possible aggregate on a per-country basis.

The colorado dataset reports on hospitalizations which imo is a great metric. Hospital admissions is an indicator of the case rate that is independent of testing capacity. Unfortunately the JHU data doesn't have this.



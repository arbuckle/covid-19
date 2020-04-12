# covid data tracker


This is a small project to stick covid-19 data into a database and compute moving averages and smoothed compound growth rates for charting. Charts might get pushed to an e-ink screen for a zero-effort daily tally (stop reading the news!).  It primarily uses data sourced from JHU. 

One piece that is maybe different from other efforts is that I'll be attempting to generate a covid-19 forecast. This would be similar to the allergen or air quality forecasts that people can access today, only instead of figuring quality of life it would be estimating the probability of your contracting covid-19 on any given day.

Guessing the forecast would combine data from multiple sources. First, an estimate of social interactivity that is a function of the weather, day of the week, time of day, and maybe whether it's a holiday. This would be a broad estiamte of how many people are out of the house and moving around on any given day.

Second, an estiamte of the current covid-19 case load in an area. This would be a ratio like the cases-per-100k that epedimiologists use today. The estimate would be based on trajectory from prior days' data - is the compound growth rate growing or slowing, what was the last known case count, and how many cases do we estimate are resolved. Possibly also hospital capacity, as that is a significant factor in covid-19 outcomes.

These two pieces of information together would provide the ability to approximate the odds of contracting covid-19 on any given day. We could present this on a scale of 0 - 100. 100 would not mean 100% odds of catching covid-19 that day, but it might mean that if you were to go outside every day for a year, you would be guaranteed to catch covid-19 with 99.99% probability. 

This would enable governments to make recommendations about social distancing that are based on realtime case data and observations. Individuals would be able to make informed choices based on their individual risk tolerance. Recommendations can be made for individuals within certain age ranges or with certain health conditions that would enable them to manage their personal risk, while others can make choices that represent their needs.

If hospitals start to get crowded, the score goes up. If the disease spread acclerated, the score goes up. On weekends, when lots of people don't have work obligations, the score might be higher. Broadcast this to everyone and it's a powerful tool for incentivizing all of society to behave in ways that strike the right balance between economic productivity and health. 






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

what is next?

- get a more complete dataset for US states 
- make a little webpage to run queries and display data
- generate a bmp from the webpage
- compound daily growth rates for deaths and cases
- all-US testing capacity estimation
- index stats from various states to date-of-first case
- covid "forecast". based on case data, day of week, weather, and holiday compute a score indicating whether it's safe to go outside 









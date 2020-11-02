<template>
  <div class="about">
    <h1>About this project</h1>


    <h2>What is this project?</h2>

    <p>
      This project aggregates data from JHU's covid tracking project in order to estimate the probability of encountering a covid-19 in daily life. 
      The aim here is to provide an annualized 'risk score' that can be used to make sensible decisions about social interactions.
    </p>


    <h2>Where do you get the data?</h2>

    <p>
      Data is loaded from JHU's covid tracker into a database. 
      This data is joined with population data for counties, states, and countries to populate a pair of tables with case data and location data. 
    </p>

    <h2>How are you measuring safety?</h2>

    <p>
        The risk measurements here are compound. Individual risk is the chance that any individual in the uninfected population is infected with COVID-19, based on current active cases.
    </p>
    <p>
        Group risk is the compound value of all individual risks. Effectively this is (individual risk ^ group size).
    </p>
    <p>
        Annualized risk is the measure of multiple successive group risks.  Each group meeting is considered to be an 
        independent event, so the annual risk is the (group risk ^ number of encounters). 
    </p>
    <p>
        Adjusted risk gives the user the ability to estimate their chances of contracting COVID-19 in a single encounter.
        This reduces the group risk and presents an adjusted risk score. 
    </p>


    <h2>Where is the source code for this?</h2>

    <a href="https://github.com/arbuckle/covid19">https://github.com/arbuckle/covid19</a>



  </div>
</template>

<style scoped>

h1 {
  margin: 20px 0;
}
h2 {
  margin: 15px 0;
}

</style>
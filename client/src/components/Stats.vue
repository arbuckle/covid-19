<template>
    <div class="stats">
        <table>
          <thead>
            <tr>
              <td>Data</td>
              <td>Value</td>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Population</td>
              <td>{{ pop }}</td>
            </tr>
            <tr>
              <td>Uninfected Population</td>
              <td>{{ uninfected }}</td>
            </tr>
            <tr>
            <tr>
              <td>Incidence</td>
              <td>{{ incidence }} per 100k</td>
            </tr>

            <tr>
              <td></td>
              <td></td>
            </tr>

            <tr>
              <td>Total Cases</td>
              <td>{{ total }}</td>
            </tr>
            <tr>
              <td>Active Cases</td>
              <td>{{ active }}</td>
            </tr>
            <tr>
              <td>Total Deaths</td>
              <td>{{ totalDeaths }}</td>
            </tr>

            <tr>
              <td></td>
              <td></td>
            </tr>

            <tr>
              <td>New Cases</td>
              <td>{{ newCases }}</td>
            </tr>
            <tr>
              <td>New Deaths</td>
              <td>{{ newDeaths }}</td>
            </tr>

            <tr>
              <td></td>
              <td></td>
            </tr>

            <tr>
              <td>{{ cgr }}-day Growth Rate</td>
              <td>{{ growthRate }}%</td>
            </tr>


          </tbody>
        </table>

        <div class="gathering">

            <div>
                <h2>Gathering Risks</h2>

                <strong>{{ iRisk }}</strong> - probability that any individual in the population has covid <br>
                <strong>{{ iSafe }}%</strong> - odds that a random 1:1 encounter is safe <br>
                <strong>{{ gRisk }}</strong> - probability that someone in a gathering of {{ size }} has covid<br>
                <strong>{{ gSafe }}%</strong> - odds that a gathering of {{ size }} is safe <br>
                <strong>{{ gAnnualRisk }}</strong> - probability that '{{ freqSel }}' gatherings of {{ size }} result in a covid encounter<br>
                <strong>{{ gAnnualSafe }}%</strong> - odds that a {{ size }} people gathering '{{ freqSel }}' is safe, if done for a whole year<br>
            </div>


            <ui-textbox
                help="The number of people in your gathering / how many encounters will you have"
                label="Gathering Size"
                placeholder="Enter gathering size"
                type="number"
                v-model="size"
            ></ui-textbox>

            <ui-radio-group
                name="freq"
                :options="['Daily', 'Weekly', 'Biweekly', 'Monthly', 'Quarterly', 'Just Once']"
                v-model="freqSel"
            >Gathering Frequency</ui-radio-group>

        </div>

    </div>
</template>

<script>

export default {
  name: 'Stats',
  props: {
    cases: Array,
    cgr: Number
  },
  data: () => {
    return {
        size: 10,
        freqSel: 'Weekly'
    }
  },
  computed: {
      latest () {
        if (this.cases.length <= 0) { return {} }

        return this.cases[this.cases.length - 1]
      },
      pop () {
        let n = this.latest.pop || 0
        return this.commify(n)
      },
      uninfected () {
        let n = this.latest.pop || 0
        let t = this.latest.cases
        return this.commify(n-t)
      },
      incidence () {
        let n = this.latest.incidence || 0
        n = Math.round(n, 0)
        return this.commify(n)
      },
      total () {
        let n = this.latest.cases || 0
        return this.commify(n)
      },
      active () {
        let n = this.latest.active_cases || 0 
        return this.commify(n)
      },
      totalDeaths () {
        let n = this.latest.deaths || 0 
        return this.commify(n)
      },
      newCases () {
        let n = this.latest.new_cases || 0
        return this.commify(n)
      },
      newDeaths () {
        let n = this.latest.new_deaths || 0
        return this.commify(n)
      },
      growthRate () {
        let n = this.latest.cgr || 0.0
        return Math.round(n * 100) / 100
      },
      iRisk () {
        // returns the individual risk of someone having covid-19
        // active cases divided by population to the power of 1
        if (this.latest.active_cases <= 0) { return 0 }

        let a = this.latest.active_cases
        let t = this.latest.pop - this.latest.cases
        let p = Math.pow(a / t, 1) 
        return Math.round(p * 1000000) / 1000000
      },
      iSafe () {
          return Math.round( ((1 - this.iRisk) * 100) * 1000) / 1000
      }, 
      gRisk () {
        let i = 1 - this.iRisk
        let p = 1 - Math.pow(i, this.size)
        return Math.round(p * 1000000) / 1000000
      },
      gSafe () {
          return Math.round( ((1 - this.gRisk) * 100) * 1000) / 1000
      },
      freq () {
          let n = 0
          if (this.freqSel === 'Just Once') {
              n = 1
          } else if (this.freqSel === 'Quarterly') {
              n = 4
          } else if (this.freqSel === 'Monthly') {
              n = 12
          } else if (this.freqSel === 'Biweekly') {
              n = 26
          } else if (this.freqSel === 'Weekly') {
              n = 52
          } else if (this.freqSel === 'Daily') {
              n = 365
          }
          return n
      },
      gAnnualRisk () {
          let i = 1 - this.gRisk
          let p = 1 - Math.pow(i, this.freq)
          return Math.round(p * 1000000) / 1000000
      },
      gAnnualSafe () {
          return Math.round( ((1 - this.gAnnualRisk) * 100) * 1000) / 1000
      }


  },
  methods: {
      commify (val) {
        // add commas lol
        val = ("" + val).split("")
        let n = Math.floor(val.length / 3)
        // indexes are i * 3 + (i-1)
        for (let i = 1; i < n+1; i++) {
            let idx = val.length - (i*3) - (i-1)
            if (idx === 0) { continue }
            val.splice(idx , 0, ",")
        }

        return val.join("")
      }
  }
}

</script>
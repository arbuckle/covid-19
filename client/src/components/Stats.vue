<template>
    <div class="stats">
        <table class="stat-table">
          <thead>
            <tr>
              <td>Location Data</td>
              <td></td>
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

            <tr class="spacer"></tr>

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

            <tr class="spacer"></tr>

            <tr>
              <td>New Cases</td>
              <td>{{ newCases }}</td>
            </tr>
            <tr>
              <td>New Deaths</td>
              <td>{{ newDeaths }}</td>
            </tr>

            <tr class="spacer"></tr>

            <tr>
              <td>{{ cgr }}-day Growth Rate</td>
              <td>{{ growthRate }}%</td>
            </tr>
            <tr>
              <td>{{ cgr }}-day Incidence</td>
              <td>{{ windowIncidence }} per 100k</td>
            </tr>


          </tbody>
        </table>
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
      windowIncidence () {
        let n = this.latest.window_incidence || 0.0
        n = Math.round(n, 0)
        return this.commify(n)
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

<style scoped>
  .stat-table {
    width: 100%;
    margin: 0 0 40px 0;
  }
  .stat-table thead {
    font-weight: bold;
  }
  .stat-table thead td {
    border-bottom: 1px solid #333;
  }
  .stat-table tbody td {
    border-bottom: 1px solid #ababab;
  }

  .stat-table tr.spacer {
    height: 15px;
  }
</style>
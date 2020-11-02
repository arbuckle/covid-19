<template>

      <div class="hello">
        <h2>Case Data</h2>

          <div class="field">
            Date Range
            <label>({{ dur }} days)</label>
            <ui-slider
                show-marker
                snap-to-steps

                :step="1"
                :min="0"
                :max="aggLabels.length"

                v-on:change="updateCharts()"
                v-model="dur"
            ></ui-slider>
          </div>

        <div class="chart">
            <canvas id="actives"></canvas>
        </div>

        <hr>

        <div class="chart">
            <canvas id="cumulatives"></canvas>
        </div>
      </div>

</template>

<script>
import Chart from 'chart.js'

export default {
  name: 'Charts',
  props: {
    msg: String,
    data: Array
  },
  data: () => {
    return {
      cumulativeCtx: undefined,
      activeCtx: undefined,

      dur: 90, // days of chart to plot

      aggLabels: [],
      activeCases: [],
      newCases: [],
      cgr: [],

      loaded: false,
      chartCumulative: undefined,
      chartActive: undefined
    }
  },
  created: function() {

  },
  methods: {
    resetData: function() {
      this.aggLabels = []
      this.activeCases = []
      this.newCases = []
      this.cgr = []
      this.cgrLine = []

      this.cumLabels = []
      this.cases = []
      this.deaths = []
      this.inc = []
    },
    loadData: function() {
      for (var i = 0; i < this.data.length; i++) {
          let c = this.data[i]
          let d = new Date(c.date)

          this.cumLabels.push(d.toISOString().split('T')[0])
          this.deaths.push(c.deaths)
          this.cases.push(c.cases)
          this.inc.push(c.incidence)

          if (c.cgr && c.active_cases) {
            this.aggLabels.push(d.toISOString().split('T')[0])
            this.activeCases.push(c.active_cases - c.new_cases)
            this.newCases.push(c.new_cases)
            this.cgr.push(c.cgr)
            this.cgrLine.push(100)
          }
      }
    },
    updateCharts: function() {

      let updateOpts = {
        duration: 10,
        easing: 'easeInCubic'
      }

      // splice this mother... how? 
      // all the charts are equally sized...
      // get 'dur' value 
      // (this.aggLabels.length - dur > 0) ? this.aggLabels.length - dur : 0 

      let d = this.dur+1
      let n = this.aggLabels.length - d
      let ix = n > 0 ? n : 0

      this.chartActive.data.labels = this.aggLabels.slice(ix)
      this.chartActive.data.datasets[0].data = this.activeCases.slice(ix)
      this.chartActive.data.datasets[1].data = this.newCases.slice(ix)
      this.chartActive.data.datasets[2].data = this.cgr.slice(ix)
      this.chartActive.data.datasets[3].data = this.cgrLine.slice(ix)

      this.chartActive.update(updateOpts)

      this.chartCumulative.data.labels = this.cumLabels.slice(ix)
      this.chartCumulative.data.datasets[0].data = this.cases.slice(ix)
      this.chartCumulative.data.datasets[1].data = this.deaths.slice(ix)
      this.chartCumulative.data.datasets[2].data = this.inc.slice(ix)
      this.chartCumulative.update(updateOpts)

    },
    createCharts: function() {
      this.cumulativeCtx = document.getElementById('cumulatives')
      this.activeCtx = document.getElementById('actives')

      let d = this.dur+1
      let n = this.aggLabels.length - d
      let ix = n > 0 ? n : 0

      this.chartCumulative = new Chart(this.cumulativeCtx, {
          type: 'bar',
          data: {
              labels: this.cumLabels.slice(ix),
              datasets: [
              {
                  label: 'Total Cases',
                  data: this.cases.slice(ix),
                  backgroundColor: '#3333ff',
                  yAxisID: 'left'
              },
              {
                  label: 'Total Deaths',
                  data: this.deaths.slice(ix),
                  backgroundColor: '#993333',
                  yAxisID: 'left'
              },
              {
                  label: 'Incidence',
                  data: this.inc.slice(ix),
                  type: 'line',
                  yAxisID: 'right'

              }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                  yAxes: [{
                      id: 'left',
                      position: 'left',
                      ticks: {
                          beginAtZero: true
                      }
                  },
              {
                  id: 'right',
                  type: 'linear',
                  position: 'right',
                  ticks: {
                      beginAtZero: true
                  }
              }]
              }
          }
      })

      this.chartActive = new Chart(this.activeCtx, {
          type: 'bar',
          data: {
              labels: this.aggLabels.slice(ix),
              datasets: [
              {
                  label: 'Active Cases',
                  data: this.activeCases.slice(ix),
                  backgroundColor: '#3333ff',
                  yAxisID: 'left'
              },
              {
                  label: 'New Cases',
                  data: this.newCases.slice(ix),
                  backgroundColor: '#993333',
                  yAxisID: 'left'
              },
              {
                  label: 'Growth Rate',
                  data: this.cgr.slice(ix),
                  type: 'line',
                  yAxisID: 'right'
              },
              {
                  label: 'omit',
                  pointRadius: 0,
                  fill: false,
                  data: this.cgrLine.slice(ix),
                  type: 'line',
                  yAxisID: 'right'
              }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              legend:{
                labels: {
                  filter: (leg) => {
                    if (leg.text === 'omit') { return }
                    return leg
                  }
                }
              },
              scales: {
                xAxes: [{
                  stacked: true,
                  }],
                  yAxes: [{
                      id: 'left',
                      position: 'left',
                      stacked: true,
                      ticks: {
                          beginAtZero: true
                      }
                  },
              {
                  id: 'right',
                  type: 'linear',
                  position: 'right',
                  ticks: {
                      beginAtZero: false
                  }
              }]
              }
          }
      })
    }
  },
  watch: {
    data: function(){

      this.resetData()
      this.loadData()


      if (!this.loaded) {
        this.createCharts()
        this.loaded = true
        return
      }

      this.updateCharts()


    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .chart {
      width: 100%;
      height: 400px;
  }

  h2 {
    margin: 20px 0;
  }

</style>

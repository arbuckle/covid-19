<template>
  <div class="hello">
    <h1>{{ msg }}</h1>

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
  name: 'HelloWorld',
  props: {
    msg: String,
    data: Array
  },
  data: () => {
    return {
      cumulativeCtx: undefined,
      activeCtx: undefined,

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
          }
      }
    },
    updateCharts: function() {

      let updateOpts = {
        duration: 300,
        easing: 'easeInCubic'
      }

      this.chartActive.data.datasets[0].data = this.activeCases
      this.chartActive.data.datasets[1].data = this.newCases
      this.chartActive.data.datasets[2].data = this.cgr

      this.chartActive.update(updateOpts)

      this.chartCumulative.data.datasets[0].data = this.cases
      this.chartCumulative.data.datasets[1].data = this.deaths
      this.chartCumulative.data.datasets[2].data = this.inc
      this.chartCumulative.update(updateOpts)

    },
    createCharts: function() {
      this.cumulativeCtx = document.getElementById('cumulatives')
      this.activeCtx = document.getElementById('actives')

      this.chartCumulative = new Chart(this.cumulativeCtx, {
          type: 'bar',
          data: {
              labels: this.cumLabels,
              datasets: [
              {
                  label: 'Total Cases',
                  data: this.cases,
                  backgroundColor: '#3333ff',
                  yAxisID: 'left'
              },
              {
                  label: 'Total Deaths',
                  data: this.deaths,
                  backgroundColor: '#993333',
                  yAxisID: 'left'
              },
              {
                  label: 'Incidence',
                  data: this.inc,
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
              labels: this.aggLabels,
              datasets: [
              {
                  label: 'Active Cases',
                  data: this.activeCases,
                  backgroundColor: '#3333ff',
                  yAxisID: 'left'
              },
              {
                  label: 'New Cases',
                  data: this.newCases,
                  backgroundColor: '#993333',
                  yAxisID: 'left'
              },
              {
                  label: 'Growth Rate',
                  data: this.cgr,
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
                      beginAtZero: true
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
</style>

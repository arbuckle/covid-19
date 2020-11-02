<template>
    <div class="gathering">
      <div>
        <h2>Gathering Risks</h2>

        <div class="widget-wrap">

          <div class="widget">
            <div class="title">Individual</div>
            <div :class="iSafe > thresholdSafe ? 'stat safe' : iSafe > thresholdRisk ? 'stat risky' : 'stat danger'">
              {{ iSafe }}% safe
            </div>
            <div class="inverted">{{ Math.round(iRisk * 10000) / 100 }}% covid risk</div>
            <div class="help">{{ iSafe }}% probability that any 1:1 encounter is safe</div>
          </div>

          <div class="widget">
            <div class="title">Group</div>
            <div :class="gSafe > thresholdSafe ? 'stat safe' : gSafe > thresholdRisk ? 'stat risky' : 'stat danger'">
              {{ gSafe }}% safe
            </div>
            <div class="inverted">{{ Math.round(gRisk * 10000) / 100 }}% covid risk</div>
            <div class="help">{{ gSafe }}% probability that group of {{ size }} is safe</div>
          </div>

          <div class="widget">
            <div class="title">Annual</div>
            <div :class="gAnnualSafe > thresholdSafe ? 'stat safe' : gAnnualSafe > thresholdRisk ? 'stat risky' : 'stat danger'">
              {{ gAnnualSafe }}% safe
            </div>
            <div class="inverted">{{ Math.round(gAnnualRisk * 10000) / 100 }}% covid risk</div>
            <div class="help">{{ gAnnualSafe }}% probability that a group of {{ size }} gathering {{ freqSel }} is safe</div>
          </div>

          <div class="widget">
            <div class="title">Adjusted</div>
            <div :class="gAASafe > thresholdSafe ? 'stat safe' : gAASafe > thresholdRisk ? 'stat risky' : 'stat danger'">
              {{ gAASafe }}% safe
            </div>
            <div class="inverted">{{ Math.round(gAARisk * 10000) / 100 }}% covid risk</div>
            <div class="help">Annual safety adjusted for transmission probability</div>
          </div>
        </div>

      </div>

      <div class="info">
        Adjust the gathering size and frequency below to see how the size of a social event and the 
        frequency of social contact play into the chances of encountering COVID-19. 
      </div>


      <ui-textbox
        help="The number of people in your gathering / how many encounters will you have"
        label="Gathering Size"
        placeholder="Enter gathering size"
        type="number"
        v-model="size"
        class="control"
      ></ui-textbox>

      <ui-radio-group
        name="freq"
        :options="['Daily', 'Weekly', 'Biweekly', 'Monthly', 'Quarterly', 'Just Once']"
        v-model="freqSel"
        class="control"
      >Gathering Frequency</ui-radio-group>

      <ui-textbox
        help="The chances (%) that an encounter results in transmission. This is where interventions like masks, meeting outdoors, social distancing, or HEPA filters all have an impact"
        label="Transmission Probability %"
        placeholder="Enter transmission probability"
        type="number"
        :min=0
        :max=100
        v-model="tp"
        class="control"
      ></ui-textbox>



    </div>
</template>

<script>

export default {
  name: 'Gathering',
  props: {
    cases: Array,
    cgr: Number
  },
  data: () => {
    return {
        size: 5,
        tp: 85,
        freqSel: 'Weekly',
        thresholdSafe: 90,
        thresholdRisk: 50,
    }
  },
  computed: {
      latest () {
        if (this.cases.length <= 0) { return {} }

        return this.cases[this.cases.length - 1]
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
          return Math.round( ((1 - this.iRisk) * 100) * 100) / 100
      }, 
      gRisk () {
        let i = 1 - this.iRisk
        let p = 1 - Math.pow(i, this.size)
        return Math.round(p * 1000000) / 1000000
      },
      gSafe () {
          return Math.round( ((1 - this.gRisk) * 100) * 100) / 100
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
          return Math.round( ((1 - this.gAnnualRisk) * 100) * 100) / 100
      },
      gAARisk () {
        let tp = this.tp / 100

        let i = 1 - this.gRisk * tp
        let p = 1 - Math.pow(i, this.freq)
        return Math.round(p * 1000000) / 1000000
      },
      gAASafe () {
        return Math.round( ((1 - this.gAARisk) * 100) * 100) / 100
      }


  },
  methods: {
  }
}

</script>

<style scoped>
  h2 {
    margin: 20px 0;
  }

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

  .widget-wrap {
    display: flex;
    flex-wrap: wrap;
  }
  .widget {
    padding: 0 60px 20px;
    text-align: center;
    flex: 2 1 25%;
  }
  .widget .title {

  }
  .widget .stat {
    font-size: 1.5em;
    color: green;
  }
  .widget .stat.safe {color: green;}
  .widget .stat.risky {color: #fa7500;}
  .widget .stat.danger {color: red;}
  .widget .inverted {
    font-size: 0.8em;
  }
  .widget .help {
    font-style: italic;
    font-size: 0.65em;
    color: #ababab;
  }

  .info {
    margin: 20px 0;
  }

  .control {
    margin: 15px 0;
  }
</style>
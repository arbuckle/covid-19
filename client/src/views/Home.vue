<template>
  <div class="home">

    <div class="intro">
      This is a tool to help communicate the risks associated with social contact during the coronavirus pandemic. 
      Choose a location from the dropdowns below, and the risk of repeated gatherings will be displayed. 
    </div>


    <div class="top">
      <div class="selection">
        <div class="field">
          <ui-select
              label="Country"
              placeholder="Select one or more countries"
              :options="countries"
              v-model="selectedCountries"
              v-on:change="makeStates(); redraw()"
              has-search
              multiple
          ></ui-select>
        </div>
        <div class="field">
          <ui-select
              label="State"
              placeholder="Select one or more states"
              :options="states"
              v-model="selectedStates"
              v-on:change="makeCounties(); redraw()"
              :disabled="(selectedCountries.length === 0)"
              has-search
              multiple
          ></ui-select>
        </div>
        <div class="field">
        <ui-select
              label="County"
              placeholder="Select one or more counties"
              :options="counties"
              v-model="selectedCounties"
              :disabled="(selectedStates.length === 0)"
              v-on:change="redraw()"
              has-search
              multiple
          ></ui-select>
        </div>
        <div class="hidden">
          <div class="field">
            <label>{{ cgr }}-day Compound Growth Rate</label>
            <ui-slider
                show-marker
                snap-to-steps

                :step="1"
                :min="1"
                :max="10"

                v-model="cgr"
            ></ui-slider>
          </div>
          <div class="field">
            <label>Case Duration ({{ dur }} days)</label>
            <ui-slider
                show-marker
                snap-to-steps

                :step="1"
                :min="1"
                :max="21"

                v-model="dur"
            ></ui-slider>
          </div>
          <div class="field">
            <ui-button
              v-on:click="redraw()"
            >
              Get Results
            </ui-button>
          </div>
        </div>
      </div>


      <div class="stats">
        <Stats :loc="locData" :cases="chartData" :cgr="cgr" />
      </div>
    </div>

    <div class="gathering-wrap">
      <gathering :loc="locData" :cases="chartData" :cgr="cgr" ></gathering>
    </div>

    <div class="chart-wrap">
      <Charts :data="chartData" />
    </div>

  </div>
</template>

<script>
// @ is an alias to /src
import Stats from '@/components/Stats.vue'
import Charts from '@/components/Charts.vue'
import Gathering from '@/components/Gathering.vue'
import axios from 'axios'

let base = 'http://127.0.0.1:5000'

export default {
  name: 'Home',
  data: () => {
    return {
      chartData: [],
      locData: [],

      // carriers of raw data used to retrieve filtered lists
      selCountry: undefined,
      selState: undefined,
      selCounty: undefined,

      countries: [],
      states: [],
      counties: [],

      cgr: 7,
      dur: 14,
      selectedCountries: ["US"],
      selectedStates: ["Colorado"],
      selectedCounties: [],
    }
  },
  methods: {
    makeCountries () {
      // this is a bullshit method with a side effect of setting the value of this.countries
      // required because vue can't detect changes to an array or object type
      if (!this.selCountry) { return [] }
      let out = []
      for (const key in this.selCountry) {
        out.push(key)
      }
      this.countries = out
    },
    makeStates () {
      if (!this.selState) { return [] }
      let out = []
      for (const i in this.selectedCountries) {
        let c = this.selectedCountries[i]
        for (const key in this.selState) {
          if (this.selState[key] === c) {
            out.push(key)
          }
        }
      }
      out.sort()
      this.states = out
    },
    makeCounties () {
      if (!this.selCounty) { return [] }
      let out = []
      for (const i in this.selectedStates) {
        let state = this.selectedStates[i]
        for (const j in this.selCounty) {
          let el = this.selCounty[j]
          if (el.state === state) {
            out.push(el.county)
          }
        }
      }
      out.sort()
      this.counties = out
    },
    query: function () {
      let url = "?cgr_window=" + this.cgr
      url = url + "&case_duration=" + this.dur
      for (let i in this.selectedCountries) {
        url = url + '&country=' + this.selectedCountries[i]
      }
      for (let i in this.selectedStates) {
        url = url + '&state=' + this.selectedStates[i]
      }
      for (let i in this.selectedCounties) {
        url = url + '&county=' + this.selectedCounties[i]
      }
      return url
    },
    redraw: function(){

      let that = this

      let cases = base + "/cases" + this.query()
      let p = axios.get(cases)
      p.then((resp) => {
        that.chartData = resp.data
      })

    }
  },
  created: function() {
    let p = axios.get(base+"/location")
    let that = this
    p.then((resp) => {
      this.selCountry = {} 
      this.selState = {}
      this.selCounty = []

      resp.data.forEach((el) => {

        // populate counties
        that.selCounty.push(el)

        // populate states next
        // the key is the state name, and the value is the country
        if (!that.selState[el.state]) { 
          that.selState[el.state] = el.country
        }

        // populate the country
        if (!that.selCountry[el.country]) { 
          that.selCountry[el.country] = true
        }
      })

      that.makeCountries()
      that.makeStates()
      that.makeCounties()
      that.redraw()
    })
  },
  components: {
    Gathering,
    Charts,
    Stats
  }
}
</script>

<style>
  .top {
    display: flex
  }
  .home .selection {
    flex: 1 1 25%;
  }
  .home .stats {
    margin-left: 80px;
    flex: 1 1 60%;
  }

  .intro {
    margin: 20px 0 60px 0;
  }

  .gathering-wrap {
    border-top: 1px solid #757575;
    margin: 40px 0 0 0;
  }

  .chart-wrap {
    border-top: 1px solid #757575;
    margin: 40px 0 0 0;
  }

  .hidden {
    display: none;
  }

</style>
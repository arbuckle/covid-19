<template>
  <div class="home">
    <div class="field">
           <ui-select
                label="Country"
                placeholder="Select one or more countries"
                :options="countries"
                v-model="selectedCountries"
                v-on:change="makeStates()"
                has-search
                multiple
            ></ui-select>

           <ui-select
                label="State"
                placeholder="Select one or more states"
                :options="states"
                v-model="selectedStates"
                v-on:change="makeCounties()"
                :disabled="(selectedCountries.length === 0)"
                has-search
                multiple
            ></ui-select>

           <ui-select
                label="County"
                placeholder="Select one or more counties"
                :options="counties"
                v-model="selectedCounties"
                :disabled="(selectedStates.length === 0)"
                has-search
                multiple
            ></ui-select>

            <ui-slider
              label="N-day Compound Growth Rate"
                show-marker
                snap-to-steps

                :step="1"
                :min="1"
                :max="10"

                v-model="cgr"
            ></ui-slider>

            <ui-slider
              label="Case Duration"
                show-marker
                snap-to-steps

                :step="1"
                :min="1"
                :max="21"

                v-model="dur"
            ></ui-slider>

            <ui-button
              v-on:click="redraw()"
            >
              Get Results
            </ui-button>
    </div>

    <Charts :data="cumulative" />
  </div>
</template>

<script>
// @ is an alias to /src
import Charts from '@/components/Charts.vue'
import axios from 'axios'

let base = "http://127.0.0.1:5000"

export default {
  name: 'Home',
  data: () => {
    return {
      cumulative: [],

      // carriers of raw data used to retrieve filtered lists
      selCountry: undefined,
      selState: undefined,
      selCounty: undefined,

      countries: [],
      states: [],
      counties: [],

      cgr: 5,
      dur: 12,
      selectedCountries: [],
      selectedStates: [],
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
    redraw: function(){

      let url = base + "/cases?cgr_window=" + this.cgr
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

      let p = axios.get(url)
      let that = this
      p.then((resp) => {
        that.cumulative = resp.data
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
    })
    // build the list of countries.  
    // get all locations
    // extract a list of unique countries
    // extract a list of states for each country
    // extract a list of counties for each country+state

  },
  components: {
    Charts
  }
}
</script>

<style global>

</style>
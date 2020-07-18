<template>
  <div class="home">
    <div class="field">
      <label for="country">Country</label>
      <input v-model="country" />
    </div>
    <div class="field">
      <label for="state">State</label>
      <input v-model="state" />
    </div>
    <div class="field">
      <label for="county">County</label>
      <input v-model="county" />
    </div>
    <div class="field">
      <button v-on:click="redraw">go</button>
    </div>
    <HelloWorld :data="cumulative" />
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'
import axios from 'axios'

export default {
  name: 'Home',
  data: () => {
    return {
      cumulative: [],
      country: 'US',
      state: 'Colorado',
      county: 'Denver'
    }
  },
  methods: {
    redraw: function(){
      let country = this.country
      let state = this.state
      let county = this.county
      let cgr = 5
      let dur = 12

      let base = "http://127.0.0.1:5000/cases?"
      let url = base + "cgr_window=" + cgr
      url = url + "&case_duration=" + dur
      url = url + "&country=" + country
      url = url + "&state=" + state
      url = url + "&county=" + county

      let p = axios.get(url)
      let that = this
      p.then((resp) => {
        console.log(resp)
        that.cumulative = resp.data
      })


    }
  },
  created: function() {

  },
  components: {
    HelloWorld
  }
}
</script>

<style global>
  /* reset from https://dev.to/hankchizljaw/a-modern-css-reset-6p3 */
  /* Box sizing rules */
  *,
  *::before,
  *::after {
  box-sizing: border-box;
  }

  /* Remove default padding */
  ul[class],
  ol[class] {
  padding: 0;
  }

  /* Remove default margin */
  body,
  h1,
  h2,
  h3,
  h4,
  p,
  ul[class],
  ol[class],
  li,
  figure,
  figcaption,
  blockquote,
  dl,
  dd {
  margin: 0;
  }

  /* Set core body defaults */
  body {
  min-height: 100vh;
  scroll-behavior: smooth;
  text-rendering: optimizeSpeed;
  line-height: 1.5;
  background-color: #333;
  color: #e3e3e3;
  margin: 20px;
  }

  /* Remove list styles on ul, ol elements with a class attribute */
  ul[class],
  ol[class] {
  list-style: none;
  }

  /* A elements that don't have a class get default styles */
  a:not([class]) {
  text-decoration-skip-ink: auto;
  }

  /* Make images easier to work with */
  img {
  max-width: 100%;
  display: block;
  }

  /* Natural flow and rhythm in articles by default */
  article > * + * {
  margin-top: 1em;
  }

  /* Inherit fonts for inputs and buttons */
  input,
  button,
  textarea,
  select {
  font: inherit;
  }

  /* Remove all animations and transitions for people that prefer not to see them */
  @media (prefers-reduced-motion: reduce) {
  * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
  }
  }
</style>
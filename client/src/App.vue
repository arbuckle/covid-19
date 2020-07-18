<template>
  <div class="app">
    <div id="nav">
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>
    </div>

    <div class="main">
      <router-view/>
    </div>
  </div>
</template>

<script>

export default {
  name: 'App'
};
</script>

<style global>

  *,
  *::before,
  *::after {
      box-sizing: border-box;
  }

  html {
      font-size: 100%;
  }

</style>
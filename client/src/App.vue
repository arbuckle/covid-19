<template>
  <div class="app">
    <div class="nav">
      <div class="logo">
        <router-link to="/">
          <h1>
            Covid Weather Report
          </h1>
        </router-link>
      </div>
      <div class="links">
        <div class="link">
          <router-link to="/about">About</router-link>
        </div>
      </div>
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
      margin: 0;
      padding: 0;
  }

  html {
      font-size: 100%;
      background-color: #dedede;
  }

  .nav {
    height: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #333333;
    color: #000;
  }

  .nav .logo {
    margin: 0 20px;
  }
  .logo a {
    color: inherit;
    text-decoration: none;
  }

  .nav .links {
    display: flex;
    align-items: center;
  }
  .nav .link {
    margin: 0 20px;
  }

  .main {
    padding: 0 60px;
    border-top: 1px solid #a08d8d;
    color: #222222;
  }

</style>
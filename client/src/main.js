import Vue from 'vue'
import App from './App.vue'
import router from './router'
import KeenUI from 'keen-ui';
import 'keen-ui/dist/keen-ui.css';

Vue.config.productionTip = false

Vue.use(KeenUI);

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

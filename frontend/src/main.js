import './theme.scss'
import Vue from 'vue'
import App from './App.vue'
import store from './store'
import router from './router'
import ControlPointEventBus from './controlpoint-event-bus'

Vue.config.productionTip = false



new Vue({
  store: store,
  router: router,
  render: h => h(App)
}).$mount('#app')

let eventBus = new ControlPointEventBus(store)
eventBus.run()

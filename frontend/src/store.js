import Vue from 'vue'
import Vuex from 'vuex'
import upnpapi from './upnpapi.js'

Vue.use(Vuex)

const state = {
  available_renderers: [],
  available_servers: [],
  active_player: null,
  volume: 0
}

export const mutations = {
  set_available_renderers(state, renderers) {
    state.available_renderers = renderers
  },
  set_available_servers(state, servers) {
    state.available_servers = servers
  },
  set_active_player(state, player) {
    state.active_player = player
  },
  set_volume(state, volume) {
    state.volume = volume
  }
}

export const getters = {
  getMediaServerByUDN: (state) => (udn) => {
    return state.available_servers.find(server => server.udn === udn);
  }
}

export const actions = {
  async update_available_renderers(context) {
    let devices = await upnpapi.getMediaRenderers()
    context.commit('set_available_renderers', devices)
  },
  async update_available_servers(context) {
    let devices = await upnpapi.getLibraryDevices()
    context.commit('set_available_servers', devices)
  },
  async update_playback_info(context) {
    let playbackInfo = await upnpapi.getCurrentPlaybackInfo()
    context.commit('set_active_player', playbackInfo.player)
    context.commit('set_volume', playbackInfo.volume)
  }
}


const store = new Vuex.Store({
  state,
  mutations,
  getters,
  actions
})

export default store

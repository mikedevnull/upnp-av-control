import Vue from "vue";
import Vuex from "vuex";
import upnpapi from "./upnpapi.js";

Vue.use(Vuex);

const state = {
  availableRenderers: [],
  availableServers: [],
  activePlayer: null,
  volume: 0
};

export const mutations = {
  setAvailableRenderers(state, renderers) {
    state.availableRenderers = renderers;
  },
  setAvailableServers(state, servers) {
    state.availableServers = servers;
  },
  setActivePlayer(state, player) {
    state.activePlayer = player;
  },
  setVolume(state, volume) {
    state.volume = volume;
  }
};

export const getters = {
  getMediaServerByUDN: state => udn => {
    return state.availableServers.find(server => server.udn === udn);
  }
};

export const actions = {
  async updateAvailableRenderers(context) {
    const devices = await upnpapi.getMediaRenderers();
    context.commit("setAvailableRenderers", devices);
  },
  async updateAvailableServers(context) {
    const devices = await upnpapi.getLibraryDevices();
    context.commit("setAvailableServers", devices);
  },
  async updatePlaybackInfo(context) {
    const playbackInfo = await upnpapi.getCurrentPlaybackInfo();
    context.commit("setActivePlayer", playbackInfo.player);
    context.commit("setVolume", playbackInfo.volume);
  }
};

const store = new Vuex.Store({
  state,
  mutations,
  getters,
  actions
});

export default store;

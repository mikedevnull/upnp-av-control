export const state = () => ({
  devices: [],
  selectedPlayerId: undefined,
  selected_player: undefined,
})

export const mutations = {
  addDevice(state, device) {
    if (
      state.devices.find((d) => {
        return d.id === device.id
      }) === undefined
    ) {
      state.devices.push(device)
    }
  },

  removeDevice(state, id) {
    state.devices = state.devices.filter((d) => {
      return d.id !== id
    })
  },

  setSelectedPlayer(state, id) {
    state.selectedPlayerId = id
  },

  setPlayer(state, device) {
    state.selected_player = device
  },
}

export const actions = {
  addDevice(context, device) {
    context.commit('addDevice', device)
  },
  removeDevice(context, device) {
    context.commit('removeDevice', device)
  },
  selectPlayer(context, deviceid) {
    context.commit('setSelectedPlayer', deviceid)
    const player = context.state.devices.find((d) => d.id === deviceid)
    context.commit('setPlayer', player)
  },
}

export const getters = {
  current_title(state) {
    if (state.selected_player) {
      return state.selected_player.name
    }
    return 'No player selected'
  },
}

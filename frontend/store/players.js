export const state = () => ({
  devices: [],
  selectedPlayerId: undefined,
  selected_player: undefined,
})

export const mutations = {
  addDevice(state, device) {
    if (
      state.devices.find((d) => {
        return d.udn === device.udn
      }) === undefined
    ) {
      state.devices.push(device)
    }
  },

  removeDevice(state, udn) {
    state.devices = state.devices.filter((d) => {
      return d.udn !== udn
    })
  },

  setSelectedPlayer(state, udn) {
    state.selectedPlayerId = udn
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
  selectPlayer(context, deviceudn) {
    context.commit('setSelectedPlayer', deviceudn)
    const player = context.state.devices.find((d) => d.udn === deviceudn)
    context.commit('setPlayer', player)
  },
}

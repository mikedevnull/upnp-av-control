<template>
  <div>
    <top-bar>Select playback device</top-bar>
    <player-selection
      :players="devices"
      :selected-player-id="selectedPlayerId"
      @selected="selectPlayer"
    />
  </div>
</template>

<script>
import { mapState } from 'vuex'
export default {
  computed: { ...mapState('players', ['devices', 'selectedPlayerId']) },
  methods: {
    selectPlayer(udn) {
      this.$store.dispatch('players/selectPlayer', udn)
    },
  },
}
</script>

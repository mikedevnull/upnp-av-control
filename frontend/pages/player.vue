<template>
  <div class="h-screen flex flex-col">
    <TopBar
      ><template #nav-action
        ><nuxt-link to="/"><NavIconDown class="w-6 h-6" /></nuxt-link
      ></template>
      Now playing
      <template #extra-action
        ><nuxt-link to="select-player"
          ><DevicesIcon class="w-6 h-6" /></nuxt-link></template
    ></TopBar>
    <player class="pt-4" />
  </div>
</template>

<script>
import NavIconDown from '~/assets/nav-down.svg?inline'
import DevicesIcon from '~/assets/control-devices.svg?inline'
export default {
  components: { NavIconDown, DevicesIcon },
  transition: 'player',
  data() {
    return {}
  },

  methods: {},
}
</script>

<style scoped>
.player-enter-active,
.player-leave-active {
  transition: 0.4s;
}
.player-enter {
  transform: translate(0, 100%);
}
.player-leave-to {
  transform: translate(0, 90%);
}
</style>

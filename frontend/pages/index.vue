<template>
  <div class="h-screen flex flex-col">
    <TopBar
      ><template #nav-action><NavIconDown class="w-6 h-6" /></template> Now
      playing
      <template #extra-action
        ><nuxt-link to="select-player"
          ><DevicesIcon class="w-6 h-6" /></nuxt-link></template
    ></TopBar>
    <player class="pt-4" @openPlayerSelection="$router.push('select-player')" />
  </div>
</template>

<script>
import NavIconDown from '~/assets/nav-down.svg?inline'
import DevicesIcon from '~/assets/control-devices.svg?inline'
export default {
  components: { NavIconDown, DevicesIcon },
  data() {
    return {}
  },

  methods: {},
}
</script>

<style>
/* Sample `apply` at-rules with Tailwind CSS
.container {
@apply min-h-screen flex justify-center items-center text-center mx-auto;
}
*/
.container {
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.title {
  font-family: 'Quicksand', 'Source Sans Pro', -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  display: block;
  font-weight: 300;
  font-size: 100px;
  color: #35495e;
  letter-spacing: 1px;
}

.subtitle {
  font-weight: 300;
  font-size: 42px;
  color: #526488;
  word-spacing: 5px;
  padding-bottom: 15px;
}

.links {
  padding-top: 15px;
}
</style>

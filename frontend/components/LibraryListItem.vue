<template>
  <div
    class="flex items-center hover:bg-primary-lightest"
    @mouseover="hover = true"
    @mouseout="hover = false"
  >
    <div class="mr-2 w-8 h-8 border rounded">
      <PlayIcon v-if="hover" />
    </div>
    <a href="#" class="flex-grow" @click="onItemSelected">{{ item.title }}</a>
  </div>
</template>
<script>
import PlayIcon from '~/assets/control-play.svg?inline'
export default {
  components: { PlayIcon },
  props: {
    item: undefined,
  },
  data() {
    return {
      hover: false,
    }
  },
  computed: {
    isBrowsable() {
      return this.item.upnpclass === 'container'
    },
  },
  methods: {
    onItemSelected() {
      if (this.isBrowsable) {
        this.$emit('browse', this.item)
      } else {
        const player = this.$store.state.players.selected_player
        if (player) {
          this.$upnpapi.play(player, this.item.id)
        }
      }
    },
  },
}
</script>

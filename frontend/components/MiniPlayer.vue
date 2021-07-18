<template>
  <div class="p-4 h-16 border-t flex justify-between items-center">
    <nuxt-link to="/player"
      ><nav-up-icon class="h-6 w-6 text-primary"
    /></nuxt-link>
    {{ current_title }}
    <span class="w-6" />
  </div>
</template>
<script>
import { mapGetters } from 'vuex'
import NavUpIcon from '~/assets/nav-back.svg?inline'

export default {
  components: { NavUpIcon },
  computed: {
    ...mapGetters('players', ['current_title']),
  },
}
</script>

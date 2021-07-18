<template>
  <div>
    <div class="flex flex-col divide-solid divide-y-2 justify-start">
      <div v-for="player in players" :key="player.udn" class="">
        <a
          href="#"
          class="block flex items-center px-4 h-16 hover:bg-primary-lightest"
          :class="{
            [`bg-primary-lightest`]: selectedPlayerId === player.id,
          }"
          @click="$emit('selected', player.id)"
          ><div>
            <img
              v-if="player.icon"
              :src="player.icon"
              class="h-14 w-14 m-1 rounded-xl border border-primary-light"
            />
            {{ player.name }}
          </div>
        </a>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    players: { type: Array, default: Array },
    selectedPlayerId: undefined,
  },
}
</script>

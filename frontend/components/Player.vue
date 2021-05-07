<template>
  <div class="flex flex-col w-full h-full">
    <div class="flex-grow-2">
      <img
        v-if="picture"
        :src="picture"
        class="rounded-3xl mx-auto shadow-2xl border-primary-light border w-9/12"
      />
      <PlaceHolder
        v-else
        class="rounded-3xl mx-auto h-48 text-primary-light shadow-2xl border-primary-light border w-9/12"
      />
    </div>
    <div class="flex-grow p-8 max-h-44 text-center text-primary">
      <h3 class="text-4xl font-bold">Title</h3>
      <h4>Band</h4>
    </div>
    <div class="mb-4 flex justify-around items-center">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6 text-primary-light"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
        />
      </svg>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6 text-primary"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 6h16M4 12h16m-7 6h7"
        />
      </svg>
    </div>
    <div class="mb-8 flex justify-around items-center">
      <PrevIcon class="h-12 w-12 text-primary" />
      <PlayIcon class="w-24 h-24 text-primary" />
      <NextIcon class="h-12 w-12 text-primary" />
    </div>
  </div>
</template>
<script>
import PlayIcon from '~/assets/control-play.svg?inline'
import PrevIcon from '~/assets/control-prev.svg?inline'
import NextIcon from '~/assets/control-next.svg?inline'
import PlaceHolder from '~/assets/photo.svg?inline'
export default {
  components: { PlayIcon, PrevIcon, NextIcon, PlaceHolder },
  data() {
    return {
      picture: undefined,
    }
  },
}
</script>

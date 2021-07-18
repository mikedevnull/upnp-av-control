<template>
  <div class="h-screen flex flex-col">
    <TopBar
      ><template #nav-action
        ><a href="#" @click="browseBack"> <NavIconBack class="w-6 h-6" /></a
      ></template>
      Browse
    </TopBar>
    <div class="flex-grow m-4">
      <h1 class="text-4xl mb-4">{{ title }}</h1>
      <ul>
        <li v-for="child in children" :key="child.id">
          <library-list-item :item="child" @browse="browse" />
        </li>
      </ul>
    </div>
    <MiniPlayer />
  </div>
</template>

<script>
import NavIconBack from '~/assets/nav-back.svg?inline'

export default {
  components: { NavIconBack },
  data() {
    return {
      currentId: undefined,
      entry: undefined,
      children: [],
    }
  },

  async fetch() {
    this.entry = await this.$upnpapi.getLibraryItem(this.currentId)
    this.children = await this.$upnpapi.browseLibrary(this.currentId)
  },

  computed: {
    title() {
      if (this.entry && this.entry.title) {
        return this.entry.title
      }
      return ''
    },
  },
  methods: {
    browse(child) {
      this.currentId = child.id
      this.entry = undefined
      this.children = []
      this.$fetch()
    },
    browseBack() {
      this.currentId = this.entry.parentID
      if (this.currentId === '-1') {
        this.currentId = undefined
      }
      this.children = []
      this.entry = undefined
      this.$fetch()
    },
  },
}
</script>

<style></style>

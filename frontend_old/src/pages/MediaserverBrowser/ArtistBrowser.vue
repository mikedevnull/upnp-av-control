<template>
  <div class="browser-view">
    <LoadSpinner
      v-if="!ready"
      class="browser-view__load-indicator"
    ></LoadSpinner>
    <template v-else>
      <div class="browser-view__details">
        <img class="browser-view__artwork" :src="coverArt" />
        <span class="browser-view-typography--title">{{ item.title }}</span>
      </div>
      <div class="browser-view__children">
        <CoverImageGrid
          v-if="musicAlbums.length > 0"
          :udn="udn"
          :items="musicAlbums"
        ></CoverImageGrid>
        <TrackList
          v-if="musicTracks.length > 0"
          :udn="udn"
          :items="musicTracks"
        ></TrackList>
      </div>
    </template>
  </div>
</template>
<script>
import ContainerBrowserMixin from "./ContainerBrowserMixin";
import LoadSpinner from "@/components/LoadSpinner";
import CoverImageGrid from "./CoverImageGrid";
import TrackList from "./TrackList";
import utils from "./container-type-utils";

export default {
  components: { TrackList, LoadSpinner, CoverImageGrid },
  mixins: [ContainerBrowserMixin],
  data() {
    return {};
  },
  computed: {
    coverArt() {
      return utils.guessImageForParentItem(this.item, this.children);
    }
  }
};
</script>
<style lang="scss">
@use "./style.scss";
</style>

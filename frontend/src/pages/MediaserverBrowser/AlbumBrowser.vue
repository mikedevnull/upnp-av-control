<template>
  <div class="browser-view">
    <LoadSpinner
      v-if="!ready"
      class="browser-view__load-indicator"
    ></LoadSpinner>
    <template v-else>
      <div class="browser-view__details">
        <img class="browser-view__artwork" :src="coverArt" />
        <span class="mdc-typography--subtitle1">{{ item.title }}</span>
        <span class="mdc-typography--subtitle2">{{ item.artist }}</span>
      </div>
      <div class="browser-view__children">
        <TrackList
          v-if="musicTracks.length > 0"
          :udn="udn"
          :items="musicTracks"
        ></TrackList>
        <CoverImageGrid
          v-if="musicAlbums.length > 0"
          :udn="udn"
          :items="musicAlbums"
        ></CoverImageGrid>
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
  components: { LoadSpinner, CoverImageGrid, TrackList },
  mixins: [ContainerBrowserMixin],
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

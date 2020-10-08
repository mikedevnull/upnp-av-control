<template>
  <div class="browser-view">
    <LoadSpinner v-if="!ready" class="browser-view__load-indicator"></LoadSpinner>
    <template v-else>
      <div class="browser-view__details">
        <img class="browser-view__artwork" :src="coverArt" />
        <span class="mdc-typography--subtitle1">{{item.title}}</span>
        <span class="mdc-typography--subtitle2">{{item.artist}}</span>
      </div>
      <div class="browser-view__children">
        <TrackList :udn="udn" :items="musicTracks" v-if="musicTracks.length > 0"></TrackList>
        <CoverImageGrid :udn="udn" :items="musicAlbums" v-if="musicAlbums.length > 0"></CoverImageGrid>
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
  mixins: [ContainerBrowserMixin],
  components: { LoadSpinner, CoverImageGrid, TrackList },
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


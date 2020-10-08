<template>
  <div class="browser-view">
    <LoadSpinner v-if="!ready" class="browser-view__load-indicator"></LoadSpinner>
    <template v-else>
      <div class="browser-view__details">
        <img class="browser-view__artwork" :src="coverArt" />
        <span class="browser-view-typography--title">{{item.title}}</span>
      </div>
      <div class="browser-view__children">
        <CoverImageGrid :udn="udn" :items="musicAlbums" v-if="musicAlbums.length > 0"></CoverImageGrid>
        <TrackList :udn="udn" :items="musicTracks" v-if="musicTracks.length > 0"></TrackList>
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
  components: { TrackList, LoadSpinner, CoverImageGrid },
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


<template>
  <div>
    <LoadSpinner v-if="!ready"></LoadSpinner>
    <component v-else :is="browseComponent" :item="item" :udn="udn"></component>
  </div>
</template>
<script>
import ControlPoint from "@/upnpapi.js";
import GenericContainerBrowser from "./GenericContainerBrowser";
import ArtistBrowser from "./ArtistBrowser";
import AlbumBrowser from "./AlbumBrowser";
import LoadSpinner from "@/components/LoadSpinner";

export default {
  name: "MediaserverBrowser",
  components: {
    LoadSpinner,
    GenericContainerBrowser,
    ArtistBrowser,
    AlbumBrowser
  },
  props: {
    udn: { type: String },
    objectID: { type: String, default: undefined }
  },
  data: function() {
    return {
      item: undefined
    };
  },
  computed: {
    ready() {
      return this.item !== undefined;
    },
    title() {
      return this.item !== undefined ? this.item.title : "";
    },
    browseComponent() {
      if (!this.item) {
        return GenericContainerBrowser;
      }
      const upnpclass = this.item.upnpclass;
      if (upnpclass.startsWith("object.container.person.musicArtist")) {
        return ArtistBrowser;
      } else if (upnpclass.startsWith("object.container.album.musicAlbum")) {
        return AlbumBrowser;
      } else {
        return GenericContainerBrowser;
      }
    }
  },
  watch: {
    objectID: async function() {
      await this.loadData();
    }
  },
  methods: {
    loadData: function() {
      this.item = undefined;
      ControlPoint.getObjectMetadata(this.udn, this.objectID).then(data => {
        this.item = data[0];
      });
    }
  },
  mounted: function() {
    this.loadData();
  }
};
</script>
<style lang="scss">
</style>

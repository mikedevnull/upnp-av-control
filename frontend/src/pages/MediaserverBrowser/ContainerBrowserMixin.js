import ControlPoint from "@/upnpapi.js";
import utils from "./container-type-utils";

export default {
  props: ['item', 'udn'],
  data() {
    return {
      children: []
    };
  },
  computed: {
    ready() {
      return this.children !== undefined;
    },
    musicAlbums() {
      return utils.filterByUpnpClass(this.children, "object.container.album.musicAlbum");
    },
    musicTracks() {
      return utils.filterByUpnpClass(this.children, "object.item.audioItem.musicTrack");
    }
  },
  methods: {
    loadData() {
      this.children = undefined;
      ControlPoint.browseServer(this.udn, this.item.id).then(data => {
        this.children = data;
      });
    },
    itemBrowseChildrenRoute(udn, objectID) {
      return utils.itemBrowseChildrenRoute(udn, objectID);
    }
  },
  watch: {
    item: async function () {
      await this.loadData();
    }
  },
  mounted: function () {
    this.loadData();
  }
}

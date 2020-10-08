<template>
  <div class="browser-view">
    <LoadSpinner v-if="!ready" class="browser-view__load-indicator"></LoadSpinner>
    <template v-else>
      <div class="browser-view__details">
        <img class="browser-view__artwork" :src="folderIcon" />
        <span class="browser-view-typography--title">{{item.title}}</span>
        <span class="browser-view-typography--subtitle">{{title}}</span>
      </div>
      <div class="browser-view__children">
        <ul class="mdc-list">
          <li
            v-for="(child, index) in children"
            :key="child.id"
            :tabindex="index == 0 ? index : false"
          >
            <router-link class="mdc-list-item" :to="itemBrowseChildrenRoute(udn, child.id)">
              <span class="mdc-list-item__graphic">
                <img class="mdc-image-list__image" :src="iconForItem(child)" />
              </span>
              <span class="mdc-list-item__text">{{child.title}}</span>
            </router-link>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>
<script>
import ContainerBrowserMixin from "./ContainerBrowserMixin";
import utils from "./container-type-utils";
import { MDCList } from "@material/list";
import LoadSpinner from "@/components/LoadSpinner";

export default {
  mixins: [ContainerBrowserMixin],
  components: { LoadSpinner },
  data() {
    return {
      mdcList: undefined,
      folderIcon: utils.folderIcon,
      mediaserver: undefined
    };
  },
  methods: {
    iconForItem(item) {
      return utils.imageForItem(item);
    }
  },
  computed: {
    title() {
      if (this.mediaserver) {
        return this.mediaserver.friendly_name;
      }
      return "";
    }
  },
  watch: {
    item: async function() {
      await this.loadData();
    }
  },
  mounted: function() {
    this.mdcList = new MDCList(document.querySelector(".mdc-list", this.$el));
    this.mediaserver = this.$store.getters.getMediaServerByUDN(this.udn);
  },
  beforeDestroy: function() {
    if (this.mdcList !== undefined) {
      this.mdcList.destroy();
      this.mdcList = undefined;
    }
  }
};
</script>
<style lang="scss">
@use "@material/list/mdc-list";
@use "./style.scss";
</style>

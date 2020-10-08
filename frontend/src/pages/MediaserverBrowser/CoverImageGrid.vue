<template>
  <div>
    <span class="browser-view__section-heading">{{heading}}</span>
    <ul class="mdc-image-list cover-image-grid mdc-image-list--with-text-protection">
      <li
        v-for="item in items"
        :item="item"
        :key="item.id"
        class="mdc-image-list__item cover-image-grid__item"
      >
        <router-link :to="itemBrowseChildrenRoute(udn, item.id)">
          <div class="mdc-image-list__image-aspect-container">
            <img class="mdc-image-list__image" :src="imageForItem(item)" />
          </div>
          <div class="mdc-image-list__supporting">
            <span class="mdc-image-list__label">{{item.title}}</span>
          </div>
        </router-link>
      </li>
    </ul>
  </div>
</template>
<script>
import utils from "./container-type-utils";
export default {
  components: {},
  props: {
    items: {},
    udn: { type: String },
    heading: { type: String, default: "Albums" }
  },
  methods: {
    imageForItem(item) {
      return utils.imageForItem(item);
    },
    itemBrowseChildrenRoute(udn, objectID) {
      return utils.itemBrowseChildrenRoute(udn, objectID);
    }
  }
};
</script>
<style lang="scss" scoped>
@use "@material/image-list/mdc-image-list";
@use "@material/image-list";
@use "./style.scss";
.cover-image-grid {
  @include image-list.standard-columns(2);
}
@media (min-width: 768px) {
  .cover-image-grid {
    @include image-list.standard-columns(4);
  }
}
.cover-image-grid__item {
  background-color: #ccc;
}
</style>

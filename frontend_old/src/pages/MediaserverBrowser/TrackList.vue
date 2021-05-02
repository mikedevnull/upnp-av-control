<template>
  <div>
    <span class="browser-view__section-heading">{{ heading }}</span>
    <ul class="mdc-list">
      <li
        v-for="(item, index) in items"
        :key="item.id"
        class="mdc-list-item"
        :tabindex="index == 0 ? index : false"
      >
        <span class="mdc-list-item__graphic">
          <img class="mdc-image-list__image" :src="imageForItem(item)" />
        </span>
        <span class="mdc-list-item__text">{{ item.title }}</span>
      </li>
    </ul>
  </div>
</template>
<script>
import utils from "./container-type-utils";
export default {
  components: {},
  props: {
    items: { type: Array, default: () => [] },
    udn: { type: String, default: undefined },
    heading: { type: String, default: "Tracks" }
  },
  methods: {
    imageForItem(item) {
      return utils.imageForItem(item);
    }
  }
};
</script>
<style lang="scss" scoped></style>

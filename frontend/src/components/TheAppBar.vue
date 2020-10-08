<template>
  <header class="mdc-top-app-bar">
    <div class="mdc-top-app-bar__row">
      <section class="mdc-top-app-bar__section mdc-top-app-bar__section--align-start">
        <span class="mdc-top-app-bar__title">UPnP AV controller</span>
      </section>
      <section class="mdc-top-app-bar__section mdc-top-app-bar__section--align-end" role="toolbar">
        <router-link :to="{ name: 'media'}" class="mdc-button top-bar__nav-button">
          <div class="mdc-button__ripple"></div>
          <span class="mdc-button__label">Musik library</span>
          <i class="material-icons mdc-button__icon" aria-hidden="true">library_music</i>
        </router-link>
      </section>
    </div>
  </header>
</template>

<script>
import { MDCTopAppBar } from "@material/top-app-bar";

export default {
  components: {},
  computed: {},
  data() {
    return {
      mdcAppBar: undefined
    };
  },
  mounted() {
    this.mdcAppBar = MDCTopAppBar.attachTo(this.$el);
  },
  beforeDestroy() {
    if (typeof this.mdcAppBar !== "undefined") {
      this.mdcAppBar.destroy();
    }
  }
};
</script>
<style lang="scss">
@use '@material/top-app-bar/mdc-top-app-bar';
@use '@material/button/mdc-button';
@use '@material/button';
@use '@material/theme';

.top-bar__nav-button {
  @include button.ink-color(theme.prop-value(on-primary));
}
</style>

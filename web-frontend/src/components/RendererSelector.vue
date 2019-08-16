<template>
  <v-select
    label="Renderer"
    v-model="active_renderer"
    :items="available_renderers"
    item-text="name"
    item-value="udn"
    @change="selectRenderer"
  ></v-select>
</template>

<script>
import ControlPoint from "../upnpapi";

export default {
  data: () => ({
    available_renderers: null,
    active_renderer: null
  }),
  methods: {
    selectRenderer(value) {
      console.log(value);
      ControlPoint.setActiveRenderer(value);
    }
  },
  mounted: function() {
    ControlPoint.getMediaRenderers().then(
      devices => (this.available_renderers = devices)
    );
    ControlPoint.getCurrentPlaybackInfo().then(info => {
      console.log(info);
      this.active_renderer = info.player;
    });
  }
};
</script>

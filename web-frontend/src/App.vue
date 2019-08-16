<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title class="headline text-uppercase">
        <span>Upnp AV Control Point</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <RendererSelector></RendererSelector>
    </v-app-bar>

    <v-content>
    </v-content>
  </v-app>
</template>

<script>
import RendererSelector from "./components/RendererSelector";
export default {
  name: "App",
  components: {
    RendererSelector
  },
  data: () => ({
    //
  })
};
</script>

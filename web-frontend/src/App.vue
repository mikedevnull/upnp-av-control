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
      <v-container text-xs-center>
        <v-layout align-center>
          <v-flex xs12>
            <RendererControl></RendererControl>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import RendererControl from "./components/RendererControl";
import RendererSelector from "./components/RendererSelector";
export default {
  name: "App",
  components: {
    RendererControl,
    RendererSelector
  },
  data: () => ({
    //
  })
};
</script>

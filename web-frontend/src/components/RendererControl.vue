<template>
  <v-card>
    <v-card-text>
      <v-toolbar flat>
        <v-btn text icon>
          <v-icon large>mdi-volume-high</v-icon>
        </v-btn>

        <v-slider style="padding-top: 20px" v-model="volume" max="1" step="0.01"></v-slider>
        <p style="min-width: 3em; margin-left: 5px; padding-top: 10px">{{Math.round(volume * 100)}}%</p>
        <v-spacer></v-spacer>
        <v-btn outlined fab small class="ma-2" color="indigo">
          <v-icon large>mdi-skip-previous</v-icon>
        </v-btn>
        <v-btn outlined fab small class="ma-2" color="indigo">
          <v-icon large>mdi-stop</v-icon>
        </v-btn>
        <v-btn outlined fab class="ma-2" color="indigo">
          <v-icon large>mdi-play</v-icon>
        </v-btn>
        <v-btn outlined fab small class="ma-2" color="indigo">
          <v-icon large>mdi-skip-next</v-icon>
        </v-btn>
        <v-spacer></v-spacer>
      </v-toolbar>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  data: () => ({ volume: 100 }),
  mounted() {}
};
</script>

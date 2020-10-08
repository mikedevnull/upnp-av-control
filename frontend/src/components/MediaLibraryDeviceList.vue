<template>
  <div>
    <h3>Mediaservers</h3>
    <ol v-for="server in available_servers" :key="server.udn">
      <li>
        <router-link :to="{name: 'browse', params: {udn: server.udn}}">{{server.friendly_name}}</router-link>
      </li>
    </ol>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  data: () => ({}),
  methods: {},
  computed: { ...mapState(["available_servers"]) }
};
</script>

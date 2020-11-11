<template>
  <div>
    <h3>Mediaservers</h3>
    <ol>
      <li v-for="server in availableServers" :key="server.udn">
        <router-link :to="{ name: 'browse', params: { udn: server.udn } }">{{
          server.friendlyName
        }}</router-link>
      </li>
    </ol>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  data: () => ({}),
  computed: { ...mapState(["availableServers"]) },
  methods: {}
};
</script>

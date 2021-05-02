<template>
  <div class="mdc-typography">
    <TheAppBar></TheAppBar>
    <main class="mdc-top-app-bar--fixed-adjust">
      <div class="main-grid">
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<script>
import TheAppBar from "./components/TheAppBar";

export default {
  name: "App",
  components: { TheAppBar }
};
</script>
<style lang="scss">
@use "@material/typography/mdc-typography";
@use '@material/layout-grid';
@import url("https://fonts.googleapis.com/css?family=Roboto:300,400,500");
@import url("https://fonts.googleapis.com/icon?family=Material+Icons");
body {
  margin: 0;
}
.main-grid {
  @include layout-grid.layout-grid(
    phone,
    map-get(layout-grid.$default-margin, phone)
  );

  @media (min-width: layout-grid.breakpoint-min(tablet)) {
    @include layout-grid.layout-grid(
      tablet,
      map-get(layout-grid.$default-margin, tablet)
    );
  }
  @media (min-width: layout-grid.breakpoint-min(desktop)) {
    @include layout-grid.layout-grid(
      desktop,
      map-get(layout-grid.$default-margin, desktop),
      1024px
    );
  }
}
</style>

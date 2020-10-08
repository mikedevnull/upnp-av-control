<template>
  <div class="loader">
    <div class="spinner"></div>
  </div>
</template>
<script>
export default {};
</script>
<style lang="scss" scoped>
@use '@material/theme';

.loader {
  text-align: center;
  padding-top: 70px;
}

.spinner {
  display: inline-block;
  width: 70px;
  height: 70px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  @include theme.prop(border-top-color, secondary);
  animation: spin 1s ease-in-out infinite;
  -webkit-animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    -webkit-transform: rotate(360deg);
  }
}
@-webkit-keyframes spin {
  to {
    -webkit-transform: rotate(360deg);
  }
}
</style>

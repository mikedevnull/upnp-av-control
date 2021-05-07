<template>
  <div class="p-4 h-16 flex justify-between items-center border-b">
    <slot name="nav-action"
      ><nuxt-link to="/"
        ><nav-back-icon class="h-6 w-6 text-primary" /></nuxt-link
    ></slot>
    <span><slot></slot></span>
    <slot name="extra-action"> <span class="w-6" /></slot>
  </div>
</template>
<script>
import NavBackIcon from '~/assets/nav-back.svg?inline'
export default {
  components: { NavBackIcon },
}
</script>

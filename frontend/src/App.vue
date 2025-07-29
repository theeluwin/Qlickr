<template>
  <v-app>
    <NavComp v-if="!$route.meta.hideNav" />
    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>
    <FooterComp v-if="!$route.meta.hideFooter" />
  </v-app>
</template>

<script setup lang="ts">

  import { useRoute } from 'vue-router'

  import NavComp from '@/comps/NavComp.vue'
  import FooterComp from '@/comps/FooterComp.vue'


  const route = useRoute()

</script>

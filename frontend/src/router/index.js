
import Vue from 'vue'
import VueRouter from 'vue-router'
import MediaLibraryDeviceList from '@/components/MediaLibraryDeviceList'
import MediaserverBrowser from '@/pages/MediaserverBrowser';

Vue.use(VueRouter);

const routes = [
  { path: '/media', name: 'media', component: MediaLibraryDeviceList },
  {
    path: '/media/:udn', name: 'browse', component: MediaserverBrowser,
    props: route => ({ udn: route.params.udn, objectID: route.query.objectID })
  },
  { path: '/', redirect: { name: 'media' } }
]
const router = new VueRouter({ routes: routes })

export default router;

import upnpApiFactory from '~/upnpapi'

export default async function ({ $axios, store }, inject) {
  // Create a custom axios instance
  const api = $axios.create({
    headers: {
      common: {
        Accept: 'text/plain, */*',
      },
    },
  })

  // Set baseURL to something different
  api.setBaseURL('/')

  const upnpapi = upnpApiFactory(api)

  // Inject to context as $api
  inject('upnpapi', upnpapi)

  const renderers = await upnpapi.getMediaRenderers()
  for (const renderer of renderers) {
    store.dispatch('players/addDevice', renderer)
  }
}

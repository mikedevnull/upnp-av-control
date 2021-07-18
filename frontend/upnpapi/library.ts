import { NuxtAxiosInstance } from '@nuxtjs/axios'

type LibraryListItem = {
  title: string
  id: string
  parentID?: string
  upnpclass: string
}

export function browse(connector: NuxtAxiosInstance, id: string) {
  if (id) {
    const url = `/api/library/${id}`
    return connector
      .get(url)
      .then((response: any) => response.data as LibraryListItem[])
  } else {
    const url = `/api/library/`
    return connector
      .get(url)
      .then((response: any) => response.data as LibraryListItem[])
  }
}

export function getItem(connector: NuxtAxiosInstance, id: string) {
  if (id) {
    const url = `/api/library/${id}/metadata`
    return connector.get(url).then((response: any) => response.data)
  }
  return {}
}

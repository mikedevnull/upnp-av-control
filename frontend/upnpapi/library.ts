import { NuxtAxiosInstance } from '@nuxtjs/axios'
import { LibraryListItem } from './types'
import { adaptTo } from './utils'

export function browse(connector: NuxtAxiosInstance, id: string) {
  if (id) {
    const url = `/api/library/${id}`
    return connector
      .get(url)
      .then((response: any) => response.data)
      .then((data: any) => adaptTo<LibraryListItem[]>(data))
  } else {
    const url = `/api/library/`
    return connector
      .get(url)
      .then((response: any) => response.data)
      .then((data: any) => adaptTo<LibraryListItem[]>(data))
  }
}

export function getItem(connector: NuxtAxiosInstance, id: string) {
  if (id) {
    const url = `/api/library/${id}/metadata`
    return connector.get(url).then((response: any) => response.data)
  }
  return {}
}

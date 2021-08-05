import { LibraryListItem } from "./types";
import { adaptTo } from "./utils";

export function browse(id: string) {
  if (id) {
    const url = `/api/library/${id}`;
    return fetch(url)
      .then((response: any) => response.json())
      .then((data: any) => adaptTo<LibraryListItem[]>(data));
  } else {
    const url = `/api/library/`;
    return fetch(url)
      .then((response: any) => response.json())
      .then((data: any) => adaptTo<LibraryListItem[]>(data));
  }
}

export function getItem(id: string) {
  if (id) {
    const url = `/api/library/${id}/metadata`;
    return fetch(url).then((response: any) => response.json());
  }
  return {};
}

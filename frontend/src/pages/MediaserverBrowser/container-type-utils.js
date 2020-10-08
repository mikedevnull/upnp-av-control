import folderIcon from "@/assets/folder-24px.svg";
import albumIcon from "@/assets/album-24px.svg";
import personIcon from "@/assets/person-24px.svg";
import trackIcon from "@/assets/music_note-black-24dp.svg";

function iconForUpnpClass(upnpclass) {
  if (
    upnpclass.startsWith("object.container.person.musicArtist")
  ) {
    return personIcon;
  } else if (
    upnpclass.startsWith("object.container.album.musicAlbum")
  ) {
    return albumIcon;
  } else if (
    upnpclass.startsWith("object.item.audioItem.musicTrack")
  ) {
    return trackIcon;
  } else {
    return folderIcon;
  }
}

function filterByUpnpClass(items, upnpclass) {
  if (items) {
    return items.filter(x => x.upnpclass.startsWith(upnpclass));
  }
  return [];
}

function imageURIFromItem(item) {
  if (item) {
    if (item.albumArtURI) {
      return '/api' + item.albumArtURI;
    }
    else if (item.artistDiscographyURI) {
      return '/api' + item.artistDiscographyURI;
    }
  }
}

function imageForItem(item) {
  if (item) {
    let uri = imageURIFromItem(item);
    if (uri) {
      return uri;
    }
    else {
      return iconForUpnpClass(item.upnpclass);
    }
  }
}

function imageURIFromFirstItem(items) {
  if (items) {
    let item = items.find(x => imageURIFromItem(x) !== undefined)
    return imageURIFromItem(item);
  }
}

function guessImageForParentItem(item, children) {
  let itemImage = imageURIFromItem(item);
  if (itemImage) {
    return itemImage;
  }
  let childImage = imageURIFromFirstItem(children);
  if (childImage) {
    return childImage;
  }
  if (item) {
    return iconForUpnpClass(item.upnpclass);
  }
  return folderIcon;
}

function itemBrowseChildrenRoute(udn, objectID) {
  return {
    name: "browse",
    params: { udn },
    query: { objectID }
  };
}

export default {
  iconForUpnpClass,
  filterByUpnpClass,
  imageForItem,
  itemBrowseChildrenRoute,
  guessImageForParentItem,
  folderIcon,
  albumIcon,
  personIcon,
  trackIcon,
  fallbackIcon: folderIcon
}


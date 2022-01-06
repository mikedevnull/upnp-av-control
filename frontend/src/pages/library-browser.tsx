import { TopBar, Miniplayer, Browser } from "../components";
import { PlaybackControl, api } from "../upnpapi";
import { useState } from "react";
import { LibraryListItem } from "../upnpapi/types";
import { NavLink, useHistory, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { ReactComponent as NavBackIcon } from "../assets/nav-back.svg";
interface LibraryBrowserProps {
  playbackControl: PlaybackControl;
}

interface CurrentItemMetadata {
  parentID?: string;
  title: string;
}

interface LibraryNavProps {
  parentID?: string;
  title: string;
  isRoot: boolean;
}

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

function LibraryNav(props: LibraryNavProps) {
  let backlink;
  if (props.parentID) {
    const uri = "/?" + new URLSearchParams({ id: props.parentID }).toString();
    backlink = (
      <NavLink aria-label="Back" to={uri}>
        <NavBackIcon />
      </NavLink>
    );
  } else if (!props.isRoot) {
    backlink = (
      <NavLink to="/">
        <NavBackIcon />
      </NavLink>
    );
  }
  return <TopBar nav={backlink} title={props.title} />;
}

export default function LibraryBrowser(props: LibraryBrowserProps) {
  const query = useQuery();
  const history = useHistory();
  const queryId = query.get("id");
  let id: string | undefined;
  if (queryId !== null) {
    id = queryId;
  }

  const [currentItemMeta, setCurrentItemMeta] = useState<CurrentItemMetadata>({
    title: "",
  });
  const [items, setItems] = useState<LibraryListItem[]>([]);

  const onSelect = (item: LibraryListItem) => {
    if (item.upnpclass.startsWith("container")) {
      setCurrentItemMeta({
        ...currentItemMeta,
        title: item.title,
      });
      history.push({
        pathname: "/",
        search: "?" + new URLSearchParams({ id: item.id }).toString(),
      });
    } else if (item.upnpclass.startsWith("item")) {
      const idx = items.indexOf(item);
      const itemsToPlay = items.slice(idx);
      props.playbackControl.playItemsImmediatly(itemsToPlay.map((i) => i.id));
    }
  };

  useEffect(() => {
    setItems([]);
    api.browse(id).then(setItems);
    if (id) {
      api.getItem(id).then((item) => {
        setCurrentItemMeta((meta) => {
          return {
            ...meta,
            parentID: item.parentID,
            title: item.title,
          };
        });
      });
    } else {
      setCurrentItemMeta((meta) => {
        return {
          ...meta,
          parentID: undefined,
          title: "",
        };
      });
    }
  }, [id]);

  return (
    <div className="h-screen w-full flex flex-col">
      <LibraryNav isRoot={id === undefined} {...currentItemMeta}></LibraryNav>
      <Browser items={items} clickHandler={onSelect}></Browser>
      <Miniplayer playbackControl={props.playbackControl}></Miniplayer>
    </div>
  );
}

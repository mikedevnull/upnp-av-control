import { TopBar, Miniplayer, Browser } from "../components";
import { PlaybackControl } from "../upnpapi";
import { useState } from "react";
import { LibraryListItem } from "../upnpapi/types";
import { NavLink, useHistory, useLocation } from "react-router-dom";
import { useEffect } from "react";
import * as library from "../upnpapi/library";
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
      <NavLink to={uri}>
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
  const onSelect = (item: LibraryListItem) => {
    setCurrentItemMeta({
      ...currentItemMeta,
      title: item.title,
    });
    history.push({
      pathname: "/",
      search: "?" + new URLSearchParams({ id: item.id }).toString(),
    });
  };

  useEffect(() => {
    if (id) {
      library.getItem(id).then((item) => {
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
      <Browser id={id} clickHandler={onSelect}></Browser>
      <Miniplayer playbackControl={props.playbackControl}></Miniplayer>
    </div>
  );
}

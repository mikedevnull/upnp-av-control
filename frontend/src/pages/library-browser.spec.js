import React from "react";
import { cleanup, fireEvent, render, waitFor } from "@testing-library/react";
import LibraryBrowser from "./library-browser";
import { Router } from "react-router-dom";
import { createMemoryHistory } from "history";
import PlaybackControl from "../upnpapi/playback_control";
import * as api from "../upnpapi/api";

jest.mock("../upnpapi/playback_control");
jest.mock("../upnpapi/api");

afterEach(cleanup);

const fakeItems = [
  {
    title: "one",
    id: "1",
    upnpclass: "container",
  },
  {
    title: "two",
    id: "2",
    upnpclass: "item",
  },
  {
    title: "three",
    id: "3",
    upnpclass: "container",
  },
];

const fakeItemMetadata = {
  title: "foo",
  id: "1234",
  parentID: "42",
  upnpclass: "container",
};

describe("LibraryBrowser", () => {
  let history;
  let control;
  beforeEach(() => {
    api.browse.mockClear();
    api.getItem.mockClear();
    api.browse.mockResolvedValue(fakeItems);
    api.getItem.mockResolvedValue(fakeItemMetadata);
    control = new PlaybackControl();
    history = createMemoryHistory();
  });

  it("displays a list of library root item", async () => {
    const component = render(
      <Router history={history}>
        <LibraryBrowser playbackControl={control} />
      </Router>
    );
    expect(await component.findByText("one")).toBeTruthy();
    expect(await component.findByText("two")).toBeTruthy();
    expect(await component.findByText("three")).toBeTruthy();
    // root of library, no back link
    expect(component.queryByAltText("Back")).toBeFalsy();
  });

  it("displays a list of library items based on the id in the url", async () => {
    history.push({
      pathname: "/",
      search: "?" + new URLSearchParams({ id: "1234" }).toString(),
    });
    const component = render(
      <Router history={history}>
        <LibraryBrowser playbackControl={control} />
      </Router>
    );
    expect(await component.findByText("one")).toBeTruthy();
    expect(api.browse).toHaveBeenCalledWith("1234");
    expect(api.getItem).toHaveBeenCalledWith("1234");
    const nav = component.getByLabelText("Back");
    expect(nav.href).toEqual(expect.stringContaining("?id=42"));
  });

  it("triggers play on click on music item ", async () => {
    control.play = jest.fn();
    const component = render(
      <Router history={history}>
        <LibraryBrowser playbackControl={control} />
      </Router>
    );
    expect(await component.findByText("two")).toBeTruthy();
    const item = component.getByText("two");
    fireEvent.click(item);
    expect(control.playItemsImmediatly).toHaveBeenCalledTimes(1);
    expect(control.playItemsImmediatly).toHaveBeenCalledWith(["2", "3"]);
  });

  it("browses subitems on click on container ", async () => {
    control.play = jest.fn();
    const component = render(
      <Router history={history}>
        <LibraryBrowser playbackControl={control} />
      </Router>
    );
    expect(await component.findByText("one")).toBeTruthy();
    const item = component.getByText("one");
    const historyCb = jest.fn();
    history.listen(historyCb);
    fireEvent.click(item);
    expect(await component.findByText("one")).toBeTruthy();
    expect(historyCb).toHaveBeenCalledTimes(1);
    expect(control.play).toHaveBeenCalledTimes(0);
  });
});

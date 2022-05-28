import JsonRPCClient from "./jsonrpc";

describe("JsonRPCClient notifications", () => {
  it("invokes registered callback on notification", () => {
    const client = new JsonRPCClient();
    const callback = jest.fn();
    client.on("some_notification", callback);
    client.handleMessage('{"jsonrpc": "2.0", "method":"some_notification"}');
    expect(callback).toHaveBeenCalled();
  });

  it("passes list arguments to callbacks", () => {
    const client = new JsonRPCClient();
    const callback = jest.fn();
    client.on("some_notification", callback);
    client.handleMessage(
      '{"jsonrpc": "2.0", "method":"some_notification", "params":[1,2]}'
    );
    expect(callback).toHaveBeenCalledWith(1, 2);
  });

  it("passes object argument to callbacks", () => {
    const client = new JsonRPCClient();
    const callback = jest.fn();
    client.on("some_notification", callback);
    client.handleMessage(
      '{"jsonrpc": "2.0", "method":"some_notification", "params":{"foo": "bar", "baz": 42}}'
    );
    expect(callback).toHaveBeenCalledWith({ foo: "bar", baz: 42 });
  });

  it("ignores notifications without registered handler", () => {
    const client = new JsonRPCClient();
    const callback = jest.fn();
    client.on("some_notification", callback);
    client.handleMessage('{"jsonrpc": "2.0", "method":"another_notification"}');
    expect(callback).not.toHaveBeenCalled();
  });
});

describe("JsonRPCClient calls", () => {
  let lastCall: { method: string; id: string; params?: object };
  const streamer = (payload: string) => {
    lastCall = JSON.parse(payload);
  };
  it("invokes function and returns result", () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    const result1 = client.call("foo", { value: 12 });
    expect(lastCall.method).toBe("foo");
    expect(lastCall.params).toEqual({ value: 12 });
    const requestid1 = lastCall.id;
    const result2 = client.call("bar");
    expect(lastCall.method).toBe("bar");
    const requestid2 = lastCall.id;
    // simulate responses in different order
    client.handleMessage(
      JSON.stringify({ jsonrpc: "2.0", result: 12, id: requestid2 })
    );
    client.handleMessage(
      JSON.stringify({ jsonrpc: "2.0", result: 42, id: requestid1 })
    );
    expect(result1).resolves.toEqual(42);
    expect(result2).resolves.toEqual(12);
  });

  it("rejects promise on jsonrpc error", () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    const result1 = client.call("foo", { value: 12 });
    expect(lastCall.method).toBe("foo");
    expect(lastCall.params).toEqual({ value: 12 });
    const requestid1 = lastCall.id;
    client.handleMessage(
      JSON.stringify({
        jsonrpc: "2.0",
        error: { code: -321, message: "uhh, something went wrong" },
        id: requestid1,
      })
    );

    return expect(result1).rejects.toStrictEqual({
      code: -321,
      message: "uhh, something went wrong",
    });
  });

  it("rejects pending promises on abort", async () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    const result1 = client.call("foo", { value: 12 });
    client.abort();
    expect(result1).rejects.toEqual("aborted");
  });
});

describe("JsonRPCClient error handling", () => {
  const streamer = jest.fn();
  it("calls onerror for unexpected responses", () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    client.onerror = jest.fn();

    client.handleMessage(
      JSON.stringify({ jsonrpc: "2.0", result: 12, id: 1234 })
    );
    expect(client.onerror).toHaveBeenCalledWith("Unexpected jsonrpc response");
  });

  it("calls onerror for unexpected error responses", () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    client.onerror = jest.fn();

    client.handleMessage(
      JSON.stringify({
        jsonrpc: "2.0",
        error: { code: -321, message: "uhh, something went wrong" },
        id: 1234,
      })
    );
    expect(client.onerror).toHaveBeenCalledWith("Unexpected jsonrpc error");
  });

  it("calls onerror for invalid jsonrpc messages", () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    client.onerror = jest.fn();

    client.handleMessage(JSON.stringify({ jsonrpc: "2.0" }));
    expect(client.onerror).toHaveBeenCalledWith("malformed jsonrpc message");
  });

  it("calls onerror for unparsable messages", () => {
    const client = new JsonRPCClient();
    client.streamTo = streamer;
    client.onerror = jest.fn();

    client.handleMessage("{foo");
    expect(client.onerror).toHaveBeenCalled();
  });

  it("throws an error as default onerror handler", () => {
    const client = new JsonRPCClient();
    expect(client.onerror).toThrowError();
  });

  it("throws an error if no streamTo handler has been set", () => {
    const client = new JsonRPCClient();
    expect(() => {
      client.call("foo");
    }).toThrowError();
  });
});

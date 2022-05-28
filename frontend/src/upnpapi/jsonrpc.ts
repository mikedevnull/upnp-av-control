interface JsonRPCNotification {
  jsonrpc: "2.0";
  method: string;
  params?: Array<number | number | boolean | string> | object;
}

interface JsonRPCResponse {
  jsonrpc: "2.0";
  result: unknown;
  id: string | number;
}

interface JsonRPCError {
  jsonrpc: "2.0";
  error: {
    code: number;
    message: string;
    data?: never;
  };
  id: string | number;
}

type PromiseHandle = {
  resolve: CallableFunction;
  reject: CallableFunction;
};

function isNotification(o: unknown): o is JsonRPCNotification {
  if (typeof o === "object" && o != null) {
    if (!("id" in o) && "method" in o) {
      return true;
    }
  }
  return false;
}

function isRPCResponse(o: unknown): o is JsonRPCResponse {
  if (typeof o === "object" && o != null) {
    if ("id" in o && "result" in o) {
      return true;
    }
  }
  return false;
}

function isRPCError(o: unknown): o is JsonRPCError {
  if (typeof o === "object" && o != null) {
    if ("id" in o && "error" in o) {
      return true;
    }
  }
  return false;
}

export default class JsonRPCClient {
  _pending: Map<string | number, PromiseHandle>;
  _callbacks: Map<string, CallableFunction>;
  _callId: number;
  onerror: CallableFunction;
  streamTo: CallableFunction;
  onclose?: CallableFunction;
  constructor() {
    this._pending = new Map();
    this._callbacks = new Map();
    this._callId = 1;
    this.onerror = function (message: string) {
      throw new Error(message);
    };
    this.onclose = undefined;
    this.streamTo = () => {
      throw new Error("must provide a streamTo implementation");
    };
  }

  call(method: string, params?: object): Promise<unknown> {
    const id = this._callId++;
    const request = JSON.stringify({ jsonrpc: "2.0", method, id, params });
    const promise = new Promise<unknown>((resolve, reject) => {
      this._pending.set(id, { resolve, reject });
    });
    this.streamTo(request);
    return promise;
  }

  handleMessage(data: string) {
    try {
      const payload = JSON.parse(data);
      if (payload.jsonrpc !== "2.0") {
        this.onerror("received non jsonrpc message");
      } else if (isNotification(payload)) {
        this._handleNotification(payload);
      } else if (isRPCResponse(payload)) {
        this._handleResponse(payload);
      } else if (isRPCError(payload)) {
        this._handleError(payload);
      } else {
        this.onerror("malformed jsonrpc message");
      }
    } catch (e) {
      this.onerror(e);
    }
  }

  _handleNotification(payload: JsonRPCNotification) {
    // this is a notification
    const notifyCallback = this._callbacks.get(payload.method);
    if (notifyCallback === undefined) {
      return;
    }
    const params = payload.params;
    if (params === undefined) {
      notifyCallback();
    } else if (Array.isArray(params)) {
      notifyCallback(...params);
    } else {
      notifyCallback(params);
    }
  }

  _handleResponse(payload: JsonRPCResponse) {
    const handle = this._pending.get(payload.id);
    if (handle) {
      this._pending.delete(payload.id);
      handle.resolve(payload.result);
    } else {
      this.onerror("Unexpected jsonrpc response");
    }
  }

  _handleError(payload: JsonRPCError) {
    const handle = this._pending.get(payload.id);
    if (handle) {
      this._pending.delete(payload.id);
      handle.reject(payload.error);
    } else {
      this.onerror("Unexpected jsonrpc error");
    }
  }

  on(methodName: string, fn: CallableFunction) {
    this._callbacks.set(methodName, fn);
  }

  abort() {
    for (let value of this._pending.values()) {
      value.reject("aborted");
    }
    this._pending.clear();
  }
}

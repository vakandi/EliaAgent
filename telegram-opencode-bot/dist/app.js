var __require = /* @__PURE__ */ ((x) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(x, {
  get: (a, b) => (typeof require !== "undefined" ? require : a)[b]
}) : x)(function(x) {
  if (typeof require !== "undefined") return require.apply(this, arguments);
  throw Error('Dynamic require of "' + x + '" is not supported');
});

// src/app.ts
import { Bot as Bot2 } from "grammy";

// src/services/config.service.ts
var ConfigService = class {
  constructor() {
    this.telegramBotTokens = (process.env.TELEGRAM_BOT_TOKENS || "").split(",").map((token) => token.trim()).filter((token) => token.length > 0);
    const allowedIds = process.env.ALLOWED_USER_IDS || "";
    this.allowedUserIds = allowedIds.split(",").map((id) => id.trim()).filter((id) => id.length > 0).map((id) => parseInt(id, 10)).filter((id) => !isNaN(id));
    const adminId = process.env.ADMIN_USER_ID || "";
    this.adminUserId = adminId.trim().length > 0 ? parseInt(adminId.trim(), 10) : void 0;
    if (this.adminUserId && isNaN(this.adminUserId)) {
      this.adminUserId = void 0;
    }
    const autoKillValue = process.env.AUTO_KILL?.toLowerCase();
    this.autoKill = autoKillValue === "true" || autoKillValue === "1";
    this.mediaTmpLocation = process.env.MEDIA_TMP_LOCATION || "/tmp/telegramcoder_media";
    const cleanUpValue = process.env.CLEAN_UP_MEDIADIR?.toLowerCase();
    this.cleanUpMediaDir = cleanUpValue === "true" || cleanUpValue === "1";
    this.messageDeleteTimeout = parseInt(process.env.MESSAGE_DELETE_TIMEOUT || "10000", 10);
    this.homeDirectory = process.env.HOME || "/tmp";
    this.systemEnv = process.env;
  }
  // Telegram Configuration Getters
  getTelegramBotTokens() {
    return [...this.telegramBotTokens];
  }
  getAllowedUserIds() {
    return [...this.allowedUserIds];
  }
  getAdminUserId() {
    return this.adminUserId;
  }
  isAutoKillEnabled() {
    return this.autoKill;
  }
  // Media Configuration Getters
  getMediaTmpLocation() {
    return this.mediaTmpLocation;
  }
  shouldCleanUpMediaDir() {
    return this.cleanUpMediaDir;
  }
  // Message Configuration Getters
  getMessageDeleteTimeout() {
    return this.messageDeleteTimeout;
  }
  // System Environment Getters
  getHomeDirectory() {
    return this.homeDirectory;
  }
  getSystemEnv() {
    return { ...this.systemEnv };
  }
  // Validation
  validate() {
    if (this.telegramBotTokens.length === 0) {
      throw new Error("No bot tokens found in TELEGRAM_BOT_TOKENS environment variable");
    }
    if (this.allowedUserIds.length === 0) {
      console.warn("Warning: No allowed user IDs configured. Consider setting ALLOWED_USER_IDS.");
    }
  }
  // Debug information
  getDebugInfo() {
    return `ConfigService:
  - Bot Tokens: ${this.telegramBotTokens.length}
  - Allowed Users: ${this.allowedUserIds.length}
  - Admin User ID: ${this.adminUserId || "Not set"}
  - Auto Kill: ${this.autoKill}
  - Media Location: ${this.mediaTmpLocation}
  - Clean Up Media Dir: ${this.cleanUpMediaDir}
  - Message Delete Timeout: ${this.messageDeleteTimeout}ms`;
  }
};

// node_modules/@opencode-ai/sdk/dist/gen/core/serverSentEvents.gen.js
var createSseClient = ({ onSseError, onSseEvent, responseTransformer, responseValidator, sseDefaultRetryDelay, sseMaxRetryAttempts, sseMaxRetryDelay, sseSleepFn, url, ...options }) => {
  let lastEventId;
  const sleep = sseSleepFn ?? ((ms) => new Promise((resolve2) => setTimeout(resolve2, ms)));
  const createStream = async function* () {
    let retryDelay = sseDefaultRetryDelay ?? 3e3;
    let attempt = 0;
    const signal = options.signal ?? new AbortController().signal;
    while (true) {
      if (signal.aborted)
        break;
      attempt++;
      const headers = options.headers instanceof Headers ? options.headers : new Headers(options.headers);
      if (lastEventId !== void 0) {
        headers.set("Last-Event-ID", lastEventId);
      }
      try {
        const response = await fetch(url, { ...options, headers, signal });
        if (!response.ok)
          throw new Error(`SSE failed: ${response.status} ${response.statusText}`);
        if (!response.body)
          throw new Error("No body in SSE response");
        const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
        let buffer = "";
        const abortHandler = () => {
          try {
            reader.cancel();
          } catch {
          }
        };
        signal.addEventListener("abort", abortHandler);
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done)
              break;
            buffer += value;
            const chunks = buffer.split("\n\n");
            buffer = chunks.pop() ?? "";
            for (const chunk of chunks) {
              const lines = chunk.split("\n");
              const dataLines = [];
              let eventName;
              for (const line of lines) {
                if (line.startsWith("data:")) {
                  dataLines.push(line.replace(/^data:\s*/, ""));
                } else if (line.startsWith("event:")) {
                  eventName = line.replace(/^event:\s*/, "");
                } else if (line.startsWith("id:")) {
                  lastEventId = line.replace(/^id:\s*/, "");
                } else if (line.startsWith("retry:")) {
                  const parsed = Number.parseInt(line.replace(/^retry:\s*/, ""), 10);
                  if (!Number.isNaN(parsed)) {
                    retryDelay = parsed;
                  }
                }
              }
              let data;
              let parsedJson = false;
              if (dataLines.length) {
                const rawData = dataLines.join("\n");
                try {
                  data = JSON.parse(rawData);
                  parsedJson = true;
                } catch {
                  data = rawData;
                }
              }
              if (parsedJson) {
                if (responseValidator) {
                  await responseValidator(data);
                }
                if (responseTransformer) {
                  data = await responseTransformer(data);
                }
              }
              onSseEvent?.({
                data,
                event: eventName,
                id: lastEventId,
                retry: retryDelay
              });
              if (dataLines.length) {
                yield data;
              }
            }
          }
        } finally {
          signal.removeEventListener("abort", abortHandler);
          reader.releaseLock();
        }
        break;
      } catch (error) {
        onSseError?.(error);
        if (sseMaxRetryAttempts !== void 0 && attempt >= sseMaxRetryAttempts) {
          break;
        }
        const backoff = Math.min(retryDelay * 2 ** (attempt - 1), sseMaxRetryDelay ?? 3e4);
        await sleep(backoff);
      }
    }
  };
  const stream = createStream();
  return { stream };
};

// node_modules/@opencode-ai/sdk/dist/gen/core/auth.gen.js
var getAuthToken = async (auth, callback) => {
  const token = typeof callback === "function" ? await callback(auth) : callback;
  if (!token) {
    return;
  }
  if (auth.scheme === "bearer") {
    return `Bearer ${token}`;
  }
  if (auth.scheme === "basic") {
    return `Basic ${btoa(token)}`;
  }
  return token;
};

// node_modules/@opencode-ai/sdk/dist/gen/core/bodySerializer.gen.js
var jsonBodySerializer = {
  bodySerializer: (body) => JSON.stringify(body, (_key, value) => typeof value === "bigint" ? value.toString() : value)
};

// node_modules/@opencode-ai/sdk/dist/gen/core/pathSerializer.gen.js
var separatorArrayExplode = (style) => {
  switch (style) {
    case "label":
      return ".";
    case "matrix":
      return ";";
    case "simple":
      return ",";
    default:
      return "&";
  }
};
var separatorArrayNoExplode = (style) => {
  switch (style) {
    case "form":
      return ",";
    case "pipeDelimited":
      return "|";
    case "spaceDelimited":
      return "%20";
    default:
      return ",";
  }
};
var separatorObjectExplode = (style) => {
  switch (style) {
    case "label":
      return ".";
    case "matrix":
      return ";";
    case "simple":
      return ",";
    default:
      return "&";
  }
};
var serializeArrayParam = ({ allowReserved, explode, name, style, value }) => {
  if (!explode) {
    const joinedValues2 = (allowReserved ? value : value.map((v) => encodeURIComponent(v))).join(separatorArrayNoExplode(style));
    switch (style) {
      case "label":
        return `.${joinedValues2}`;
      case "matrix":
        return `;${name}=${joinedValues2}`;
      case "simple":
        return joinedValues2;
      default:
        return `${name}=${joinedValues2}`;
    }
  }
  const separator = separatorArrayExplode(style);
  const joinedValues = value.map((v) => {
    if (style === "label" || style === "simple") {
      return allowReserved ? v : encodeURIComponent(v);
    }
    return serializePrimitiveParam({
      allowReserved,
      name,
      value: v
    });
  }).join(separator);
  return style === "label" || style === "matrix" ? separator + joinedValues : joinedValues;
};
var serializePrimitiveParam = ({ allowReserved, name, value }) => {
  if (value === void 0 || value === null) {
    return "";
  }
  if (typeof value === "object") {
    throw new Error("Deeply-nested arrays/objects aren\u2019t supported. Provide your own `querySerializer()` to handle these.");
  }
  return `${name}=${allowReserved ? value : encodeURIComponent(value)}`;
};
var serializeObjectParam = ({ allowReserved, explode, name, style, value, valueOnly }) => {
  if (value instanceof Date) {
    return valueOnly ? value.toISOString() : `${name}=${value.toISOString()}`;
  }
  if (style !== "deepObject" && !explode) {
    let values = [];
    Object.entries(value).forEach(([key, v]) => {
      values = [...values, key, allowReserved ? v : encodeURIComponent(v)];
    });
    const joinedValues2 = values.join(",");
    switch (style) {
      case "form":
        return `${name}=${joinedValues2}`;
      case "label":
        return `.${joinedValues2}`;
      case "matrix":
        return `;${name}=${joinedValues2}`;
      default:
        return joinedValues2;
    }
  }
  const separator = separatorObjectExplode(style);
  const joinedValues = Object.entries(value).map(([key, v]) => serializePrimitiveParam({
    allowReserved,
    name: style === "deepObject" ? `${name}[${key}]` : key,
    value: v
  })).join(separator);
  return style === "label" || style === "matrix" ? separator + joinedValues : joinedValues;
};

// node_modules/@opencode-ai/sdk/dist/gen/core/utils.gen.js
var PATH_PARAM_RE = /\{[^{}]+\}/g;
var defaultPathSerializer = ({ path: path33, url: _url }) => {
  let url = _url;
  const matches = _url.match(PATH_PARAM_RE);
  if (matches) {
    for (const match of matches) {
      let explode = false;
      let name = match.substring(1, match.length - 1);
      let style = "simple";
      if (name.endsWith("*")) {
        explode = true;
        name = name.substring(0, name.length - 1);
      }
      if (name.startsWith(".")) {
        name = name.substring(1);
        style = "label";
      } else if (name.startsWith(";")) {
        name = name.substring(1);
        style = "matrix";
      }
      const value = path33[name];
      if (value === void 0 || value === null) {
        continue;
      }
      if (Array.isArray(value)) {
        url = url.replace(match, serializeArrayParam({ explode, name, style, value }));
        continue;
      }
      if (typeof value === "object") {
        url = url.replace(match, serializeObjectParam({
          explode,
          name,
          style,
          value,
          valueOnly: true
        }));
        continue;
      }
      if (style === "matrix") {
        url = url.replace(match, `;${serializePrimitiveParam({
          name,
          value
        })}`);
        continue;
      }
      const replaceValue = encodeURIComponent(style === "label" ? `.${value}` : value);
      url = url.replace(match, replaceValue);
    }
  }
  return url;
};
var getUrl = ({ baseUrl, path: path33, query, querySerializer, url: _url }) => {
  const pathUrl = _url.startsWith("/") ? _url : `/${_url}`;
  let url = (baseUrl ?? "") + pathUrl;
  if (path33) {
    url = defaultPathSerializer({ path: path33, url });
  }
  let search = query ? querySerializer(query) : "";
  if (search.startsWith("?")) {
    search = search.substring(1);
  }
  if (search) {
    url += `?${search}`;
  }
  return url;
};

// node_modules/@opencode-ai/sdk/dist/gen/client/utils.gen.js
var createQuerySerializer = ({ allowReserved, array, object } = {}) => {
  const querySerializer = (queryParams) => {
    const search = [];
    if (queryParams && typeof queryParams === "object") {
      for (const name in queryParams) {
        const value = queryParams[name];
        if (value === void 0 || value === null) {
          continue;
        }
        if (Array.isArray(value)) {
          const serializedArray = serializeArrayParam({
            allowReserved,
            explode: true,
            name,
            style: "form",
            value,
            ...array
          });
          if (serializedArray)
            search.push(serializedArray);
        } else if (typeof value === "object") {
          const serializedObject = serializeObjectParam({
            allowReserved,
            explode: true,
            name,
            style: "deepObject",
            value,
            ...object
          });
          if (serializedObject)
            search.push(serializedObject);
        } else {
          const serializedPrimitive = serializePrimitiveParam({
            allowReserved,
            name,
            value
          });
          if (serializedPrimitive)
            search.push(serializedPrimitive);
        }
      }
    }
    return search.join("&");
  };
  return querySerializer;
};
var getParseAs = (contentType) => {
  if (!contentType) {
    return "stream";
  }
  const cleanContent = contentType.split(";")[0]?.trim();
  if (!cleanContent) {
    return;
  }
  if (cleanContent.startsWith("application/json") || cleanContent.endsWith("+json")) {
    return "json";
  }
  if (cleanContent === "multipart/form-data") {
    return "formData";
  }
  if (["application/", "audio/", "image/", "video/"].some((type) => cleanContent.startsWith(type))) {
    return "blob";
  }
  if (cleanContent.startsWith("text/")) {
    return "text";
  }
  return;
};
var checkForExistence = (options, name) => {
  if (!name) {
    return false;
  }
  if (options.headers.has(name) || options.query?.[name] || options.headers.get("Cookie")?.includes(`${name}=`)) {
    return true;
  }
  return false;
};
var setAuthParams = async ({ security, ...options }) => {
  for (const auth of security) {
    if (checkForExistence(options, auth.name)) {
      continue;
    }
    const token = await getAuthToken(auth, options.auth);
    if (!token) {
      continue;
    }
    const name = auth.name ?? "Authorization";
    switch (auth.in) {
      case "query":
        if (!options.query) {
          options.query = {};
        }
        options.query[name] = token;
        break;
      case "cookie":
        options.headers.append("Cookie", `${name}=${token}`);
        break;
      case "header":
      default:
        options.headers.set(name, token);
        break;
    }
  }
};
var buildUrl = (options) => getUrl({
  baseUrl: options.baseUrl,
  path: options.path,
  query: options.query,
  querySerializer: typeof options.querySerializer === "function" ? options.querySerializer : createQuerySerializer(options.querySerializer),
  url: options.url
});
var mergeConfigs = (a, b) => {
  const config = { ...a, ...b };
  if (config.baseUrl?.endsWith("/")) {
    config.baseUrl = config.baseUrl.substring(0, config.baseUrl.length - 1);
  }
  config.headers = mergeHeaders(a.headers, b.headers);
  return config;
};
var mergeHeaders = (...headers) => {
  const mergedHeaders = new Headers();
  for (const header of headers) {
    if (!header || typeof header !== "object") {
      continue;
    }
    const iterator = header instanceof Headers ? header.entries() : Object.entries(header);
    for (const [key, value] of iterator) {
      if (value === null) {
        mergedHeaders.delete(key);
      } else if (Array.isArray(value)) {
        for (const v of value) {
          mergedHeaders.append(key, v);
        }
      } else if (value !== void 0) {
        mergedHeaders.set(key, typeof value === "object" ? JSON.stringify(value) : value);
      }
    }
  }
  return mergedHeaders;
};
var Interceptors = class {
  _fns;
  constructor() {
    this._fns = [];
  }
  clear() {
    this._fns = [];
  }
  getInterceptorIndex(id) {
    if (typeof id === "number") {
      return this._fns[id] ? id : -1;
    } else {
      return this._fns.indexOf(id);
    }
  }
  exists(id) {
    const index = this.getInterceptorIndex(id);
    return !!this._fns[index];
  }
  eject(id) {
    const index = this.getInterceptorIndex(id);
    if (this._fns[index]) {
      this._fns[index] = null;
    }
  }
  update(id, fn) {
    const index = this.getInterceptorIndex(id);
    if (this._fns[index]) {
      this._fns[index] = fn;
      return id;
    } else {
      return false;
    }
  }
  use(fn) {
    this._fns = [...this._fns, fn];
    return this._fns.length - 1;
  }
};
var createInterceptors = () => ({
  error: new Interceptors(),
  request: new Interceptors(),
  response: new Interceptors()
});
var defaultQuerySerializer = createQuerySerializer({
  allowReserved: false,
  array: {
    explode: true,
    style: "form"
  },
  object: {
    explode: true,
    style: "deepObject"
  }
});
var defaultHeaders = {
  "Content-Type": "application/json"
};
var createConfig = (override = {}) => ({
  ...jsonBodySerializer,
  headers: defaultHeaders,
  parseAs: "auto",
  querySerializer: defaultQuerySerializer,
  ...override
});

// node_modules/@opencode-ai/sdk/dist/gen/client/client.gen.js
var createClient = (config = {}) => {
  let _config = mergeConfigs(createConfig(), config);
  const getConfig = () => ({ ..._config });
  const setConfig = (config2) => {
    _config = mergeConfigs(_config, config2);
    return getConfig();
  };
  const interceptors = createInterceptors();
  const beforeRequest = async (options) => {
    const opts = {
      ..._config,
      ...options,
      fetch: options.fetch ?? _config.fetch ?? globalThis.fetch,
      headers: mergeHeaders(_config.headers, options.headers),
      serializedBody: void 0
    };
    if (opts.security) {
      await setAuthParams({
        ...opts,
        security: opts.security
      });
    }
    if (opts.requestValidator) {
      await opts.requestValidator(opts);
    }
    if (opts.body && opts.bodySerializer) {
      opts.serializedBody = opts.bodySerializer(opts.body);
    }
    if (opts.serializedBody === void 0 || opts.serializedBody === "") {
      opts.headers.delete("Content-Type");
    }
    const url = buildUrl(opts);
    return { opts, url };
  };
  const request = async (options) => {
    const { opts, url } = await beforeRequest(options);
    const requestInit = {
      redirect: "follow",
      ...opts,
      body: opts.serializedBody
    };
    let request2 = new Request(url, requestInit);
    for (const fn of interceptors.request._fns) {
      if (fn) {
        request2 = await fn(request2, opts);
      }
    }
    const _fetch = opts.fetch;
    let response = await _fetch(request2);
    for (const fn of interceptors.response._fns) {
      if (fn) {
        response = await fn(response, request2, opts);
      }
    }
    const result = {
      request: request2,
      response
    };
    if (response.ok) {
      if (response.status === 204 || response.headers.get("Content-Length") === "0") {
        return opts.responseStyle === "data" ? {} : {
          data: {},
          ...result
        };
      }
      const parseAs = (opts.parseAs === "auto" ? getParseAs(response.headers.get("Content-Type")) : opts.parseAs) ?? "json";
      let data;
      switch (parseAs) {
        case "arrayBuffer":
        case "blob":
        case "formData":
        case "json":
        case "text":
          data = await response[parseAs]();
          break;
        case "stream":
          return opts.responseStyle === "data" ? response.body : {
            data: response.body,
            ...result
          };
      }
      if (parseAs === "json") {
        if (opts.responseValidator) {
          await opts.responseValidator(data);
        }
        if (opts.responseTransformer) {
          data = await opts.responseTransformer(data);
        }
      }
      return opts.responseStyle === "data" ? data : {
        data,
        ...result
      };
    }
    const textError = await response.text();
    let jsonError;
    try {
      jsonError = JSON.parse(textError);
    } catch {
    }
    const error = jsonError ?? textError;
    let finalError = error;
    for (const fn of interceptors.error._fns) {
      if (fn) {
        finalError = await fn(error, response, request2, opts);
      }
    }
    finalError = finalError || {};
    if (opts.throwOnError) {
      throw finalError;
    }
    return opts.responseStyle === "data" ? void 0 : {
      error: finalError,
      ...result
    };
  };
  const makeMethod = (method) => {
    const fn = (options) => request({ ...options, method });
    fn.sse = async (options) => {
      const { opts, url } = await beforeRequest(options);
      return createSseClient({
        ...opts,
        body: opts.body,
        headers: opts.headers,
        method,
        url
      });
    };
    return fn;
  };
  return {
    buildUrl,
    connect: makeMethod("CONNECT"),
    delete: makeMethod("DELETE"),
    get: makeMethod("GET"),
    getConfig,
    head: makeMethod("HEAD"),
    interceptors,
    options: makeMethod("OPTIONS"),
    patch: makeMethod("PATCH"),
    post: makeMethod("POST"),
    put: makeMethod("PUT"),
    request,
    setConfig,
    trace: makeMethod("TRACE")
  };
};

// node_modules/@opencode-ai/sdk/dist/gen/core/params.gen.js
var extraPrefixesMap = {
  $body_: "body",
  $headers_: "headers",
  $path_: "path",
  $query_: "query"
};
var extraPrefixes = Object.entries(extraPrefixesMap);

// node_modules/@opencode-ai/sdk/dist/gen/client.gen.js
var client = createClient(createConfig({
  baseUrl: "http://localhost:4096"
}));

// node_modules/@opencode-ai/sdk/dist/gen/sdk.gen.js
var _HeyApiClient = class {
  _client = client;
  constructor(args) {
    if (args?.client) {
      this._client = args.client;
    }
  }
};
var Global = class extends _HeyApiClient {
  /**
   * Get events
   */
  event(options) {
    return (options?.client ?? this._client).get.sse({
      url: "/global/event",
      ...options
    });
  }
};
var Project = class extends _HeyApiClient {
  /**
   * List all projects
   */
  list(options) {
    return (options?.client ?? this._client).get({
      url: "/project",
      ...options
    });
  }
  /**
   * Get the current project
   */
  current(options) {
    return (options?.client ?? this._client).get({
      url: "/project/current",
      ...options
    });
  }
};
var Pty = class extends _HeyApiClient {
  /**
   * List all PTY sessions
   */
  list(options) {
    return (options?.client ?? this._client).get({
      url: "/pty",
      ...options
    });
  }
  /**
   * Create a new PTY session
   */
  create(options) {
    return (options?.client ?? this._client).post({
      url: "/pty",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  /**
   * Remove a PTY session
   */
  remove(options) {
    return (options.client ?? this._client).delete({
      url: "/pty/{id}",
      ...options
    });
  }
  /**
   * Get PTY session info
   */
  get(options) {
    return (options.client ?? this._client).get({
      url: "/pty/{id}",
      ...options
    });
  }
  /**
   * Update PTY session
   */
  update(options) {
    return (options.client ?? this._client).put({
      url: "/pty/{id}",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Connect to a PTY session
   */
  connect(options) {
    return (options.client ?? this._client).get({
      url: "/pty/{id}/connect",
      ...options
    });
  }
};
var Config = class extends _HeyApiClient {
  /**
   * Get config info
   */
  get(options) {
    return (options?.client ?? this._client).get({
      url: "/config",
      ...options
    });
  }
  /**
   * Update config
   */
  update(options) {
    return (options?.client ?? this._client).patch({
      url: "/config",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  /**
   * List all providers
   */
  providers(options) {
    return (options?.client ?? this._client).get({
      url: "/config/providers",
      ...options
    });
  }
};
var Tool = class extends _HeyApiClient {
  /**
   * List all tool IDs (including built-in and dynamically registered)
   */
  ids(options) {
    return (options?.client ?? this._client).get({
      url: "/experimental/tool/ids",
      ...options
    });
  }
  /**
   * List tools with JSON schema parameters for a provider/model
   */
  list(options) {
    return (options.client ?? this._client).get({
      url: "/experimental/tool",
      ...options
    });
  }
};
var Instance = class extends _HeyApiClient {
  /**
   * Dispose the current instance
   */
  dispose(options) {
    return (options?.client ?? this._client).post({
      url: "/instance/dispose",
      ...options
    });
  }
};
var Path = class extends _HeyApiClient {
  /**
   * Get the current path
   */
  get(options) {
    return (options?.client ?? this._client).get({
      url: "/path",
      ...options
    });
  }
};
var Vcs = class extends _HeyApiClient {
  /**
   * Get VCS info for the current instance
   */
  get(options) {
    return (options?.client ?? this._client).get({
      url: "/vcs",
      ...options
    });
  }
};
var Session = class extends _HeyApiClient {
  /**
   * List all sessions
   */
  list(options) {
    return (options?.client ?? this._client).get({
      url: "/session",
      ...options
    });
  }
  /**
   * Create a new session
   */
  create(options) {
    return (options?.client ?? this._client).post({
      url: "/session",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  /**
   * Get session status
   */
  status(options) {
    return (options?.client ?? this._client).get({
      url: "/session/status",
      ...options
    });
  }
  /**
   * Delete a session and all its data
   */
  delete(options) {
    return (options.client ?? this._client).delete({
      url: "/session/{id}",
      ...options
    });
  }
  /**
   * Get session
   */
  get(options) {
    return (options.client ?? this._client).get({
      url: "/session/{id}",
      ...options
    });
  }
  /**
   * Update session properties
   */
  update(options) {
    return (options.client ?? this._client).patch({
      url: "/session/{id}",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Get a session's children
   */
  children(options) {
    return (options.client ?? this._client).get({
      url: "/session/{id}/children",
      ...options
    });
  }
  /**
   * Get the todo list for a session
   */
  todo(options) {
    return (options.client ?? this._client).get({
      url: "/session/{id}/todo",
      ...options
    });
  }
  /**
   * Analyze the app and create an AGENTS.md file
   */
  init(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/init",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Fork an existing session at a specific message
   */
  fork(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/fork",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Abort a session
   */
  abort(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/abort",
      ...options
    });
  }
  /**
   * Unshare the session
   */
  unshare(options) {
    return (options.client ?? this._client).delete({
      url: "/session/{id}/share",
      ...options
    });
  }
  /**
   * Share a session
   */
  share(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/share",
      ...options
    });
  }
  /**
   * Get the diff for this session
   */
  diff(options) {
    return (options.client ?? this._client).get({
      url: "/session/{id}/diff",
      ...options
    });
  }
  /**
   * Summarize the session
   */
  summarize(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/summarize",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * List messages for a session
   */
  messages(options) {
    return (options.client ?? this._client).get({
      url: "/session/{id}/message",
      ...options
    });
  }
  /**
   * Create and send a new message to a session
   */
  prompt(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/message",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Get a message from a session
   */
  message(options) {
    return (options.client ?? this._client).get({
      url: "/session/{id}/message/{messageID}",
      ...options
    });
  }
  /**
   * Create and send a new message to a session, start if needed and return immediately
   */
  promptAsync(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/prompt_async",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Send a new command to a session
   */
  command(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/command",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Run a shell command
   */
  shell(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/shell",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Revert a message
   */
  revert(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/revert",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Restore all reverted messages
   */
  unrevert(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/unrevert",
      ...options
    });
  }
};
var Command = class extends _HeyApiClient {
  /**
   * List all commands
   */
  list(options) {
    return (options?.client ?? this._client).get({
      url: "/command",
      ...options
    });
  }
};
var Oauth = class extends _HeyApiClient {
  /**
   * Authorize a provider using OAuth
   */
  authorize(options) {
    return (options.client ?? this._client).post({
      url: "/provider/{id}/oauth/authorize",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Handle OAuth callback for a provider
   */
  callback(options) {
    return (options.client ?? this._client).post({
      url: "/provider/{id}/oauth/callback",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
};
var Provider = class extends _HeyApiClient {
  /**
   * List all providers
   */
  list(options) {
    return (options?.client ?? this._client).get({
      url: "/provider",
      ...options
    });
  }
  /**
   * Get provider authentication methods
   */
  auth(options) {
    return (options?.client ?? this._client).get({
      url: "/provider/auth",
      ...options
    });
  }
  oauth = new Oauth({ client: this._client });
};
var Find = class extends _HeyApiClient {
  /**
   * Find text in files
   */
  text(options) {
    return (options.client ?? this._client).get({
      url: "/find",
      ...options
    });
  }
  /**
   * Find files
   */
  files(options) {
    return (options.client ?? this._client).get({
      url: "/find/file",
      ...options
    });
  }
  /**
   * Find workspace symbols
   */
  symbols(options) {
    return (options.client ?? this._client).get({
      url: "/find/symbol",
      ...options
    });
  }
};
var File = class extends _HeyApiClient {
  /**
   * List files and directories
   */
  list(options) {
    return (options.client ?? this._client).get({
      url: "/file",
      ...options
    });
  }
  /**
   * Read a file
   */
  read(options) {
    return (options.client ?? this._client).get({
      url: "/file/content",
      ...options
    });
  }
  /**
   * Get file status
   */
  status(options) {
    return (options?.client ?? this._client).get({
      url: "/file/status",
      ...options
    });
  }
};
var App = class extends _HeyApiClient {
  /**
   * Write a log entry to the server logs
   */
  log(options) {
    return (options?.client ?? this._client).post({
      url: "/log",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  /**
   * List all agents
   */
  agents(options) {
    return (options?.client ?? this._client).get({
      url: "/agent",
      ...options
    });
  }
};
var Auth = class extends _HeyApiClient {
  /**
   * Remove OAuth credentials for an MCP server
   */
  remove(options) {
    return (options.client ?? this._client).delete({
      url: "/mcp/{name}/auth",
      ...options
    });
  }
  /**
   * Start OAuth authentication flow for an MCP server
   */
  start(options) {
    return (options.client ?? this._client).post({
      url: "/mcp/{name}/auth",
      ...options
    });
  }
  /**
   * Complete OAuth authentication with authorization code
   */
  callback(options) {
    return (options.client ?? this._client).post({
      url: "/mcp/{name}/auth/callback",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  /**
   * Start OAuth flow and wait for callback (opens browser)
   */
  authenticate(options) {
    return (options.client ?? this._client).post({
      url: "/mcp/{name}/auth/authenticate",
      ...options
    });
  }
  /**
   * Set authentication credentials
   */
  set(options) {
    return (options.client ?? this._client).put({
      url: "/auth/{id}",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
};
var Mcp = class extends _HeyApiClient {
  /**
   * Get MCP server status
   */
  status(options) {
    return (options?.client ?? this._client).get({
      url: "/mcp",
      ...options
    });
  }
  /**
   * Add MCP server dynamically
   */
  add(options) {
    return (options?.client ?? this._client).post({
      url: "/mcp",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  /**
   * Connect an MCP server
   */
  connect(options) {
    return (options.client ?? this._client).post({
      url: "/mcp/{name}/connect",
      ...options
    });
  }
  /**
   * Disconnect an MCP server
   */
  disconnect(options) {
    return (options.client ?? this._client).post({
      url: "/mcp/{name}/disconnect",
      ...options
    });
  }
  auth = new Auth({ client: this._client });
};
var Lsp = class extends _HeyApiClient {
  /**
   * Get LSP server status
   */
  status(options) {
    return (options?.client ?? this._client).get({
      url: "/lsp",
      ...options
    });
  }
};
var Formatter = class extends _HeyApiClient {
  /**
   * Get formatter status
   */
  status(options) {
    return (options?.client ?? this._client).get({
      url: "/formatter",
      ...options
    });
  }
};
var Control = class extends _HeyApiClient {
  /**
   * Get the next TUI request from the queue
   */
  next(options) {
    return (options?.client ?? this._client).get({
      url: "/tui/control/next",
      ...options
    });
  }
  /**
   * Submit a response to the TUI request queue
   */
  response(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/control/response",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
};
var Tui = class extends _HeyApiClient {
  /**
   * Append prompt to the TUI
   */
  appendPrompt(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/append-prompt",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  /**
   * Open the help dialog
   */
  openHelp(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/open-help",
      ...options
    });
  }
  /**
   * Open the session dialog
   */
  openSessions(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/open-sessions",
      ...options
    });
  }
  /**
   * Open the theme dialog
   */
  openThemes(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/open-themes",
      ...options
    });
  }
  /**
   * Open the model dialog
   */
  openModels(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/open-models",
      ...options
    });
  }
  /**
   * Submit the prompt
   */
  submitPrompt(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/submit-prompt",
      ...options
    });
  }
  /**
   * Clear the prompt
   */
  clearPrompt(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/clear-prompt",
      ...options
    });
  }
  /**
   * Execute a TUI command (e.g. agent_cycle)
   */
  executeCommand(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/execute-command",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  /**
   * Show a toast notification in the TUI
   */
  showToast(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/show-toast",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  /**
   * Publish a TUI event
   */
  publish(options) {
    return (options?.client ?? this._client).post({
      url: "/tui/publish",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      }
    });
  }
  control = new Control({ client: this._client });
};
var Event = class extends _HeyApiClient {
  /**
   * Get events
   */
  subscribe(options) {
    return (options?.client ?? this._client).get.sse({
      url: "/event",
      ...options
    });
  }
};
var OpencodeClient = class extends _HeyApiClient {
  /**
   * Respond to a permission request
   */
  postSessionIdPermissionsPermissionId(options) {
    return (options.client ?? this._client).post({
      url: "/session/{id}/permissions/{permissionID}",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });
  }
  global = new Global({ client: this._client });
  project = new Project({ client: this._client });
  pty = new Pty({ client: this._client });
  config = new Config({ client: this._client });
  tool = new Tool({ client: this._client });
  instance = new Instance({ client: this._client });
  path = new Path({ client: this._client });
  vcs = new Vcs({ client: this._client });
  session = new Session({ client: this._client });
  command = new Command({ client: this._client });
  provider = new Provider({ client: this._client });
  find = new Find({ client: this._client });
  file = new File({ client: this._client });
  app = new App({ client: this._client });
  mcp = new Mcp({ client: this._client });
  lsp = new Lsp({ client: this._client });
  formatter = new Formatter({ client: this._client });
  tui = new Tui({ client: this._client });
  auth = new Auth({ client: this._client });
  event = new Event({ client: this._client });
};

// node_modules/@opencode-ai/sdk/dist/client.js
function createOpencodeClient(config) {
  if (!config?.fetch) {
    const customFetch = (req) => {
      req.timeout = false;
      return fetch(req);
    };
    config = {
      ...config,
      fetch: customFetch
    };
  }
  if (config?.directory) {
    config.headers = {
      ...config.headers,
      "x-opencode-directory": encodeURIComponent(config.directory)
    };
  }
  const client2 = createClient(config);
  return new OpencodeClient({ client: client2 });
}

// node_modules/@opencode-ai/sdk/dist/server.js
import { spawn } from "node:child_process";

// src/features/opencode/event-handlers/utils.ts
function escapeHtml(text) {
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function formatAsHtml(text) {
  return escapeHtml(text).replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>").replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/\*([^*]+)\*/g, "<i>$1</i>").replace(/__([^_]+)__/g, "<u>$1</u>").replace(/~~([^~]+)~~/g, "<s>$1</s>").replace(/^###\s+(.*)$/gm, "<b>$1</b>").replace(/^##\s+(.*)$/gm, "<b>$1</b>").replace(/^#\s+(.*)$/gm, "<b>$1</b>");
}
async function sendAndAutoDelete(ctx, message, deleteAfterMs = 2500) {
  try {
    const sentMessage = await ctx.reply(message);
    setTimeout(async () => {
      try {
        await ctx.api.deleteMessage(ctx.chat.id, sentMessage.message_id);
      } catch (error) {
        console.log("Error deleting auto-delete message:", error);
      }
    }, deleteAfterMs);
  } catch (error) {
    console.log("Error sending auto-delete message:", error);
  }
}

// src/features/opencode/event-handlers/message.updated.handler.ts
async function messageUpdatedHandler(event, ctx, userSession) {
  try {
    const { info } = event.properties;
    if (info?.summary?.title) {
      const title = info.summary.title;
      const client2 = createOpencodeClient({
        baseUrl: process.env.OPENCODE_BASE_URL || "http://localhost:4000"
      });
      await client2.session.update({
        path: { id: userSession.sessionId },
        body: { title }
      });
      console.log(`\u2713 Updated session title: "${title}"`);
      await sendAndAutoDelete(ctx, `\u{1F4DD} New title: ${title}`, 2500);
    }
  } catch (error) {
    console.log("Error in message.updated handler:", error);
  }
  return null;
}

// src/features/opencode/event-handlers/message.removed.handler.ts
import * as fs from "fs";
import * as path from "path";
async function messageRemovedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path.join(process.cwd(), "events");
  if (!fs.existsSync(eventsDir)) {
    fs.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path.join(eventsDir, `${eventType}.last.json`);
  fs.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/session.status.handler.ts
import * as fs2 from "fs";
import * as path2 from "path";
async function sessionStatusHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path2.join(process.cwd(), "events");
  if (!fs2.existsSync(eventsDir)) {
    fs2.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path2.join(eventsDir, `${eventType}.last.json`);
  fs2.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/session.idle.handler.ts
import * as fs3 from "fs";
import * as path3 from "path";
async function sessionIdleHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path3.join(process.cwd(), "events");
  if (!fs3.existsSync(eventsDir)) {
    fs3.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path3.join(eventsDir, `${eventType}.last.json`);
  fs3.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/session.error.handler.ts
import * as fs4 from "fs";
import * as path4 from "path";
async function sessionErrorHandler(event, ctx, userSession) {
  console.log("[session.error handler] Processing error event");
  const eventsDir = path4.join(process.cwd(), "events");
  if (!fs4.existsSync(eventsDir)) {
    fs4.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path4.join(eventsDir, `${eventType}.last.json`);
  fs4.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  const errorLogPath = path4.join(eventsDir, "session-errors.json");
  let errorLog = [];
  if (fs4.existsSync(errorLogPath)) {
    try {
      errorLog = JSON.parse(fs4.readFileSync(errorLogPath, "utf8"));
    } catch (e) {
      errorLog = [];
    }
  }
  const errorEntry = {
    timestamp: Date.now(),
    sessionId: userSession.sessionId,
    error: event.properties?.error || "Unknown error",
    message: event.properties?.message || "No message",
    stack: event.properties?.stack || "No stack"
  };
  errorLog.push(errorEntry);
  fs4.writeFileSync(errorLogPath, JSON.stringify(errorLog, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/file.edited.handler.ts
import * as fs5 from "fs";
import * as path5 from "path";
async function fileEditedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path5.join(process.cwd(), "events");
  if (!fs5.existsSync(eventsDir)) {
    fs5.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path5.join(eventsDir, `${eventType}.last.json`);
  fs5.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/pty.created.handler.ts
import * as fs6 from "fs";
import * as path6 from "path";
async function ptyCreatedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path6.join(process.cwd(), "events");
  if (!fs6.existsSync(eventsDir)) {
    fs6.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path6.join(eventsDir, `${eventType}.last.json`);
  fs6.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/pty.exited.handler.ts
import * as fs7 from "fs";
import * as path7 from "path";
async function ptyExitedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path7.join(process.cwd(), "events");
  if (!fs7.existsSync(eventsDir)) {
    fs7.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path7.join(eventsDir, `${eventType}.last.json`);
  fs7.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/server.instance.disposed.handler.ts
import * as fs8 from "fs";
import * as path8 from "path";
async function serverInstanceDisposedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path8.join(process.cwd(), "events");
  if (!fs8.existsSync(eventsDir)) {
    fs8.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path8.join(eventsDir, `${eventType}.last.json`);
  fs8.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/installation.updated.handler.ts
import * as fs9 from "fs";
import * as path9 from "path";
async function installationUpdatedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path9.join(process.cwd(), "events");
  if (!fs9.existsSync(eventsDir)) {
    fs9.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path9.join(eventsDir, `${eventType}.last.json`);
  fs9.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/installation.update-available.handler.ts
import * as fs10 from "fs";
import * as path10 from "path";
async function installationUpdateAvailableHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path10.join(process.cwd(), "events");
  if (!fs10.existsSync(eventsDir)) {
    fs10.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path10.join(eventsDir, `${eventType}.last.json`);
  fs10.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/lsp.client.diagnostics.handler.ts
import * as fs11 from "fs";
import * as path11 from "path";
async function lspClientDiagnosticsHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path11.join(process.cwd(), "events");
  if (!fs11.existsSync(eventsDir)) {
    fs11.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path11.join(eventsDir, `${eventType}.last.json`);
  fs11.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/lsp.updated.handler.ts
import * as fs12 from "fs";
import * as path12 from "path";
async function lspUpdatedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path12.join(process.cwd(), "events");
  if (!fs12.existsSync(eventsDir)) {
    fs12.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path12.join(eventsDir, `${eventType}.last.json`);
  fs12.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/message-part-updated/text-part.handler.ts
var updateMessageId = null;
var lastUpdateTime = 0;
var deleteTimeout = null;
var latestText = "";
async function handleTextPart(ctx, text) {
  try {
    const now = Date.now();
    if (deleteTimeout) {
      clearTimeout(deleteTimeout);
      deleteTimeout = null;
    }
    const lines = text.split("\n");
    const limitedText = lines.length > 50 ? lines.slice(-50).join("\n") : text;
    latestText = formatAsHtml(limitedText);
    if (!updateMessageId) {
      const sentMessage = await ctx.reply(latestText, { parse_mode: "HTML" });
      updateMessageId = sentMessage.message_id;
      lastUpdateTime = now;
    } else {
      const timeSinceLastUpdate = now - lastUpdateTime;
      if (timeSinceLastUpdate < 2e3) {
        deleteTimeout = setTimeout(() => {
          deleteTextMessage(ctx);
        }, 5e3);
        return;
      }
      await ctx.api.editMessageText(
        ctx.chat.id,
        updateMessageId,
        latestText,
        { parse_mode: "HTML" }
      );
      lastUpdateTime = now;
    }
    deleteTimeout = setTimeout(() => {
      deleteTextMessage(ctx);
    }, 5e3);
  } catch (error) {
    console.log("Error in text part handler:", error);
  }
}
async function deleteTextMessage(ctx) {
  try {
    if (updateMessageId) {
      await ctx.api.deleteMessage(ctx.chat.id, updateMessageId);
      updateMessageId = null;
    }
  } catch (error) {
    console.log("Error deleting text message:", error);
  }
}

// src/features/opencode/event-handlers/message-part-updated/reasoning-part.handler.ts
var reasoningMessageId = null;
var reasoningDeleteTimeout = null;
async function handleReasoningPart(ctx) {
  try {
    if (reasoningDeleteTimeout) {
      clearTimeout(reasoningDeleteTimeout);
      reasoningDeleteTimeout = null;
    }
    if (!reasoningMessageId) {
      const sentMessage = await ctx.reply("Reasoning");
      reasoningMessageId = sentMessage.message_id;
    }
    reasoningDeleteTimeout = setTimeout(async () => {
      try {
        if (reasoningMessageId) {
          await ctx.api.deleteMessage(ctx.chat.id, reasoningMessageId);
          reasoningMessageId = null;
        }
      } catch (error) {
        console.log("Error deleting reasoning message:", error);
      }
    }, 2500);
  } catch (error) {
    console.log("Error in reasoning part handler:", error);
  }
}

// src/features/opencode/event-handlers/message-part-updated/tool-part.handler.ts
var toolMessageId = null;
var toolDeleteTimeout = null;
async function handleToolPart(ctx, part) {
  try {
    if (toolDeleteTimeout) {
      clearTimeout(toolDeleteTimeout);
      toolDeleteTimeout = null;
    }
    if (!toolMessageId && part.tool) {
      const sentMessage = await ctx.reply(`\u{1F527} ${part.tool}`);
      toolMessageId = sentMessage.message_id;
    }
    toolDeleteTimeout = setTimeout(async () => {
      try {
        if (toolMessageId) {
          await ctx.api.deleteMessage(ctx.chat.id, toolMessageId);
          toolMessageId = null;
        }
      } catch (error) {
        console.log("Error deleting tool message:", error);
      }
    }, 2500);
  } catch (error) {
    console.log("Error in tool part handler:", error);
  }
}

// src/features/opencode/event-handlers/message.part.updated.handler.ts
async function messagePartUpdatedHandler(event, ctx, userSession) {
  try {
    const { part } = event.properties;
    if (part.type === "reasoning") {
      await handleReasoningPart(ctx);
      return null;
    }
    if (part.type === "tool") {
      await handleToolPart(ctx, part);
      return null;
    }
    if (part.type !== "text") {
      return null;
    }
    await handleTextPart(ctx, part.text);
  } catch (error) {
    console.log("Error in message.part.updated handler:", error);
  }
  return null;
}

// src/features/opencode/event-handlers/message.part.removed.handler.ts
import * as fs13 from "fs";
import * as path13 from "path";
async function messagePartRemovedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path13.join(process.cwd(), "events");
  if (!fs13.existsSync(eventsDir)) {
    fs13.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path13.join(eventsDir, `${eventType}.last.json`);
  fs13.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/permission.updated.handler.ts
import * as fs14 from "fs";
import * as path14 from "path";
async function permissionUpdatedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path14.join(process.cwd(), "events");
  if (!fs14.existsSync(eventsDir)) {
    fs14.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path14.join(eventsDir, `${eventType}.last.json`);
  fs14.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/permission.replied.handler.ts
import * as fs15 from "fs";
import * as path15 from "path";
async function permissionRepliedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path15.join(process.cwd(), "events");
  if (!fs15.existsSync(eventsDir)) {
    fs15.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path15.join(eventsDir, `${eventType}.last.json`);
  fs15.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/session.compacted.handler.ts
import * as fs16 from "fs";
import * as path16 from "path";
async function sessionCompactedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path16.join(process.cwd(), "events");
  if (!fs16.existsSync(eventsDir)) {
    fs16.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path16.join(eventsDir, `${eventType}.last.json`);
  fs16.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/todo.updated.handler.ts
async function todoUpdatedHandler(event, ctx, userSession) {
  try {
    const { todos } = event.properties;
    if (todos && Array.isArray(todos)) {
      const todoCount = todos.length;
      await sendAndAutoDelete(ctx, `\u{1F4CB} ${todoCount} todo${todoCount !== 1 ? "s" : ""}`, 2500);
    }
  } catch (error) {
    console.log("Error in todo.updated handler:", error);
  }
  return null;
}

// src/features/opencode/event-handlers/command.executed.handler.ts
import * as fs17 from "fs";
import * as path17 from "path";
async function commandExecutedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path17.join(process.cwd(), "events");
  if (!fs17.existsSync(eventsDir)) {
    fs17.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path17.join(eventsDir, `${eventType}.last.json`);
  fs17.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/session.created.handler.ts
import * as fs18 from "fs";
import * as path18 from "path";
async function sessionCreatedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path18.join(process.cwd(), "events");
  if (!fs18.existsSync(eventsDir)) {
    fs18.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path18.join(eventsDir, `${eventType}.last.json`);
  fs18.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/session.updated.handler.ts
async function sessionUpdatedHandler(event, ctx, userSession) {
  console.log(event.type);
  return null;
}

// src/features/opencode/event-handlers/session.deleted.handler.ts
import * as fs19 from "fs";
import * as path19 from "path";
async function sessionDeletedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path19.join(process.cwd(), "events");
  if (!fs19.existsSync(eventsDir)) {
    fs19.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path19.join(eventsDir, `${eventType}.last.json`);
  fs19.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/session.diff.handler.ts
import * as fs20 from "fs";
import * as path20 from "path";
async function sessionDiffHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path20.join(process.cwd(), "events");
  if (!fs20.existsSync(eventsDir)) {
    fs20.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path20.join(eventsDir, `${eventType}.last.json`);
  fs20.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/file.watcher.updated.handler.ts
import * as fs21 from "fs";
import * as path21 from "path";
async function fileWatcherUpdatedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path21.join(process.cwd(), "events");
  if (!fs21.existsSync(eventsDir)) {
    fs21.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path21.join(eventsDir, `${eventType}.last.json`);
  fs21.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/vcs.branch.updated.handler.ts
import * as fs22 from "fs";
import * as path22 from "path";
async function vcsBranchUpdatedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path22.join(process.cwd(), "events");
  if (!fs22.existsSync(eventsDir)) {
    fs22.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path22.join(eventsDir, `${eventType}.last.json`);
  fs22.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/tui.prompt.append.handler.ts
import * as fs23 from "fs";
import * as path23 from "path";
async function tuiPromptAppendHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path23.join(process.cwd(), "events");
  if (!fs23.existsSync(eventsDir)) {
    fs23.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path23.join(eventsDir, `${eventType}.last.json`);
  fs23.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/tui.command.execute.handler.ts
import * as fs24 from "fs";
import * as path24 from "path";
async function tuiCommandExecuteHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path24.join(process.cwd(), "events");
  if (!fs24.existsSync(eventsDir)) {
    fs24.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path24.join(eventsDir, `${eventType}.last.json`);
  fs24.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/tui.toast.show.handler.ts
import * as fs25 from "fs";
import * as path25 from "path";
async function tuiToastShowHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path25.join(process.cwd(), "events");
  if (!fs25.existsSync(eventsDir)) {
    fs25.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path25.join(eventsDir, `${eventType}.last.json`);
  fs25.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/pty.updated.handler.ts
import * as fs26 from "fs";
import * as path26 from "path";
async function ptyUpdatedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path26.join(process.cwd(), "events");
  if (!fs26.existsSync(eventsDir)) {
    fs26.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path26.join(eventsDir, `${eventType}.last.json`);
  fs26.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/pty.deleted.handler.ts
import * as fs27 from "fs";
import * as path27 from "path";
async function ptyDeletedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path27.join(process.cwd(), "events");
  if (!fs27.existsSync(eventsDir)) {
    fs27.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path27.join(eventsDir, `${eventType}.last.json`);
  fs27.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/event-handlers/server.connected.handler.ts
import * as fs28 from "fs";
import * as path28 from "path";
async function serverConnectedHandler(event, ctx, userSession) {
  console.log(event.type);
  const eventsDir = path28.join(process.cwd(), "events");
  if (!fs28.existsSync(eventsDir)) {
    fs28.mkdirSync(eventsDir, { recursive: true });
  }
  const eventType = event.type.replace(/\./g, "-");
  const filePath = path28.join(eventsDir, `${eventType}.last.json`);
  fs28.writeFileSync(filePath, JSON.stringify(event, null, 2), "utf8");
  return null;
}

// src/features/opencode/opencode.event-handlers.ts
var eventHandlers = {
  "message.updated": messageUpdatedHandler,
  "message.removed": messageRemovedHandler,
  "message.part.updated": messagePartUpdatedHandler,
  "message.part.removed": messagePartRemovedHandler,
  "permission.updated": permissionUpdatedHandler,
  "permission.replied": permissionRepliedHandler,
  "session.status": sessionStatusHandler,
  "session.idle": sessionIdleHandler,
  "session.compacted": sessionCompactedHandler,
  "session.error": sessionErrorHandler,
  "session.created": sessionCreatedHandler,
  "session.updated": sessionUpdatedHandler,
  "session.deleted": sessionDeletedHandler,
  "session.diff": sessionDiffHandler,
  "file.edited": fileEditedHandler,
  "file.watcher.updated": fileWatcherUpdatedHandler,
  "todo.updated": todoUpdatedHandler,
  "command.executed": commandExecutedHandler,
  "vcs.branch.updated": vcsBranchUpdatedHandler,
  "installation.updated": installationUpdatedHandler,
  "installation.update-available": installationUpdateAvailableHandler,
  "lsp.client.diagnostics": lspClientDiagnosticsHandler,
  "lsp.updated": lspUpdatedHandler,
  "tui.prompt.append": tuiPromptAppendHandler,
  "tui.command.execute": tuiCommandExecuteHandler,
  "tui.toast.show": tuiToastShowHandler,
  "pty.created": ptyCreatedHandler,
  "pty.updated": ptyUpdatedHandler,
  "pty.exited": ptyExitedHandler,
  "pty.deleted": ptyDeletedHandler,
  "server.instance.disposed": serverInstanceDisposedHandler,
  "server.connected": serverConnectedHandler
};
async function processEvent(event, ctx, userSession) {
  try {
    const handler = eventHandlers[event.type];
    if (handler) {
      const result = await handler(event, ctx, userSession);
      if (result) {
        return result;
      }
    }
    if (!handler) {
      return null;
    }
  } catch (error) {
    console.error(`Error handling event ${event.type}:`, error);
    return null;
  }
}

// src/features/opencode/opencode.service.ts
var OpenCodeService = class {
  constructor(baseUrl) {
    this.userSessions = /* @__PURE__ */ new Map();
    this.eventAbortControllers = /* @__PURE__ */ new Map();
    this.baseUrl = baseUrl || process.env.OPENCODE_SERVER_URL || "http://localhost:4096";
  }
  async createSession(userId, title) {
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const result = await client2.session.create({
        body: { title: title || `Telegram Session ${(/* @__PURE__ */ new Date()).toISOString()}` }
      });
      if (!result.data) {
        throw new Error("Failed to create session");
      }
      const userSession = {
        userId,
        sessionId: result.data.id,
        session: result.data,
        createdAt: /* @__PURE__ */ new Date(),
        currentAgent: "build"
      };
      this.userSessions.set(userId, userSession);
      return userSession;
    } catch (error) {
      if (error instanceof Error && (error.message.includes("fetch failed") || error.message.includes("ECONNREFUSED"))) {
        throw new Error(`Cannot connect to OpenCode server at ${this.baseUrl}. Please ensure:
1. OpenCode server is running
2. OPENCODE_SERVER_URL is configured correctly in .env file`);
      }
      throw error;
    }
  }
  getUserSession(userId) {
    return this.userSessions.get(userId);
  }
  updateSessionContext(userId, chatId, messageId) {
    const session = this.userSessions.get(userId);
    if (session) {
      session.chatId = chatId;
      session.lastMessageId = messageId;
    }
  }
  async startEventStream(userId, ctx) {
    const userSession = this.getUserSession(userId);
    if (!userSession || !userSession.chatId) {
      return;
    }
    this.stopEventStream(userId);
    const abortController = new AbortController();
    this.eventAbortControllers.set(userId, abortController);
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const events = await client2.event.subscribe();
      for await (const event of events.stream) {
        if (abortController.signal.aborted) {
          break;
        }
        await processEvent(event, ctx, userSession);
      }
    } catch (error) {
      console.error("Event stream error:", error);
    } finally {
      this.eventAbortControllers.delete(userId);
    }
  }
  stopEventStream(userId) {
    const controller = this.eventAbortControllers.get(userId);
    if (controller) {
      controller.abort();
      this.eventAbortControllers.delete(userId);
    }
  }
  async sendPrompt(userId, text, fileContext) {
    const userSession = this.getUserSession(userId);
    if (!userSession) {
      throw new Error("No active session. Please use /opencode to start a session first.");
    }
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const fullPrompt = fileContext ? `${fileContext}

${text}` : text;
      const result = await client2.session.prompt({
        path: { id: userSession.sessionId },
        body: {
          parts: [{ type: "text", text: fullPrompt }],
          agent: userSession.currentAgent
        }
      });
      if (!result.data) {
        throw new Error("Failed to send prompt");
      }
      const textParts = result.data.parts?.filter((part) => part.type === "text").map((part) => part.text).join("\n");
      return textParts || "No response received";
    } catch (error) {
      if (error instanceof Error && (error.message.includes("fetch failed") || error.message.includes("ECONNREFUSED"))) {
        throw new Error(`Cannot connect to OpenCode server at ${this.baseUrl}. Please ensure the OpenCode server is running.`);
      }
      throw error;
    }
  }
  async deleteSession(userId) {
    const userSession = this.getUserSession(userId);
    if (!userSession) {
      return false;
    }
    this.stopEventStream(userId);
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      await client2.session.delete({
        path: { id: userSession.sessionId }
      });
      this.userSessions.delete(userId);
      return true;
    } catch (error) {
      console.error(`Failed to delete session for user ${userId}:`, error);
      return false;
    }
  }
  hasActiveSession(userId) {
    return this.userSessions.has(userId);
  }
  attachToSession(userId, sessionId, title) {
    const userSession = {
      userId,
      sessionId,
      session: { id: sessionId, title: title || "Resumed Session" },
      createdAt: /* @__PURE__ */ new Date(),
      currentAgent: "build",
      chatId: 0
    };
    this.userSessions.set(userId, userSession);
  }
  async abortSession(userId) {
    const userSession = this.getUserSession(userId);
    if (!userSession) {
      return false;
    }
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      await client2.session.abort({
        path: { id: userSession.sessionId }
      });
      return true;
    } catch (error) {
      console.error(`Failed to abort session for user ${userId}:`, error);
      return false;
    }
  }
  async getAvailableAgents() {
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const result = await client2.app.agents();
      if (!result.data) {
        return [];
      }
      const internalAgents = ["compaction", "title", "summary"];
      const filtered = result.data.filter((agent) => {
        if (agent.hidden === true) {
          console.log(`Filtering out hidden agent: ${agent.name}`);
          return false;
        }
        if (agent.mode === "subagent") {
          console.log(`Filtering out subagent: ${agent.name}`);
          return false;
        }
        if (internalAgents.includes(agent.name)) {
          console.log(`Filtering out internal agent: ${agent.name}`);
          return false;
        }
        return agent.mode === "primary" || agent.mode === "all";
      }).map((agent) => ({
        name: agent.name || "unknown",
        mode: agent.mode,
        description: agent.description
      }));
      console.log("Filtered agents:", filtered.map((a) => a.name));
      return filtered;
    } catch (error) {
      console.error("Failed to get available agents:", error);
      return [];
    }
  }
  async cycleToNextAgent(userId) {
    const userSession = this.getUserSession(userId);
    if (!userSession) {
      return { success: false };
    }
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const agents = await this.getAvailableAgents();
      if (agents.length === 0) {
        console.error("No available agents to cycle through");
        return { success: false };
      }
      const currentAgent = userSession.currentAgent || agents[0].name;
      const currentIndex = agents.findIndex((a) => a.name === currentAgent);
      const nextIndex = (currentIndex + 1) % agents.length;
      const nextAgent = agents[nextIndex].name;
      userSession.currentAgent = nextAgent;
      console.log(`\u2713 Cycled agent for user ${userId}: ${currentAgent} \u2192 ${nextAgent}`);
      console.log(`  Available agents: ${agents.map((a) => a.name).join(", ")}`);
      return { success: true, currentAgent: nextAgent };
    } catch (error) {
      console.error(`Failed to cycle agent for user ${userId}:`, error);
      return { success: false };
    }
  }
  async updateSessionTitle(userId, title) {
    const userSession = this.getUserSession(userId);
    if (!userSession) {
      return { success: false, message: "No active session found" };
    }
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      await client2.session.update({
        path: { id: userSession.sessionId },
        body: { title }
      });
      console.log(`\u2713 Updated session title for user ${userId}: "${title}"`);
      return { success: true };
    } catch (error) {
      console.error(`Failed to update session title for user ${userId}:`, error);
      return { success: false, message: "Failed to update session title" };
    }
  }
  async getProjects() {
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const result = await client2.project.list();
      if (!result.data) {
        return [];
      }
      return result.data.map((project) => ({
        id: project.id,
        worktree: project.worktree
      }));
    } catch (error) {
      console.error("Failed to get projects:", error);
      return [];
    }
  }
  async getSessions(limit = 5) {
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const result = await client2.session.list();
      if (!result.data) {
        return [];
      }
      return result.data.sort((a, b) => b.time.updated - a.time.updated).slice(0, limit).map((session) => ({
        id: session.id,
        title: session.title,
        created: session.time.created,
        updated: session.time.updated
      }));
    } catch (error) {
      console.error("Failed to get sessions:", error);
      return [];
    }
  }
  async undoLastMessage(userId) {
    const userSession = this.getUserSession(userId);
    if (!userSession) {
      return { success: false, message: "No active session found" };
    }
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      if (typeof client2.session.revert !== "function") {
        return { success: false, message: "Undo is not available in this SDK version" };
      }
      await client2.session.revert({
        path: { id: userSession.sessionId }
      });
      console.log(`\u2713 Undid last message for user ${userId}`);
      return { success: true };
    } catch (error) {
      console.error(`Failed to undo message for user ${userId}:`, error);
      return { success: false, message: "Failed to undo last message" };
    }
  }
  async redoLastMessage(userId) {
    const userSession = this.getUserSession(userId);
    if (!userSession) {
      return { success: false, message: "No active session found" };
    }
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      if (typeof client2.session.unrevert !== "function") {
        return { success: false, message: "Redo is not available in this SDK version" };
      }
      await client2.session.unrevert({
        path: { id: userSession.sessionId }
      });
      console.log(`\u2713 Redid last message for user ${userId}`);
      return { success: true };
    } catch (error) {
      console.error(`Failed to redo message for user ${userId}:`, error);
      return { success: false, message: "Failed to redo last message" };
    }
  }
};

// src/features/opencode/opencode.bot.ts
import { InputFile, Keyboard } from "grammy";

// src/services/opencode-server.service.ts
import { spawn as spawn2 } from "child_process";
var OpenCodeServerService = class {
  // 30 seconds
  constructor(serverUrl) {
    this.serverProcess = null;
    this.startupTimeout = 3e4;
    this.serverUrl = serverUrl || process.env.OPENCODE_SERVER_URL || "http://localhost:4096";
  }
  async isServerRunning() {
    try {
      const url = new URL(this.serverUrl);
      const response = await fetch(this.serverUrl, {
        method: "HEAD",
        signal: AbortSignal.timeout(5e3)
      });
      return response.ok || response.status < 500;
    } catch (error) {
      return false;
    }
  }
  async isOpenCodeInstalled() {
    try {
      const { execSync } = __require("child_process");
      execSync("opencode --version", { stdio: "ignore" });
      return true;
    } catch {
      return false;
    }
  }
  async startServer() {
    if (await this.isServerRunning()) {
      return { success: true, message: "OpenCode server is already running" };
    }
    if (!await this.isOpenCodeInstalled()) {
      return {
        success: false,
        message: "opencode command is not available. Please install OpenCode: npm install -g opencode-ai"
      };
    }
    try {
      const url = new URL(this.serverUrl);
      const port = url.port || "4096";
      const hostname = url.hostname || "localhost";
      const args = ["serve", "--port", port, "--hostname", hostname];
      this.serverProcess = spawn2("opencode", args, {
        detached: true,
        stdio: "ignore"
      });
      this.serverProcess.unref();
      const startTime = Date.now();
      while (Date.now() - startTime < this.startupTimeout) {
        if (await this.isServerRunning()) {
          return {
            success: true,
            message: `OpenCode server started successfully on ${this.serverUrl}`
          };
        }
        await new Promise((resolve2) => setTimeout(resolve2, 1e3));
      }
      return {
        success: false,
        message: "OpenCode server started but did not respond within 30 seconds"
      };
    } catch (error) {
      return {
        success: false,
        message: `Failed to start OpenCode server: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }
  stopServer() {
    if (this.serverProcess && !this.serverProcess.killed) {
      this.serverProcess.kill();
      this.serverProcess = null;
    }
  }
};

// src/middleware/access-control.middleware.ts
var AccessControlMiddleware = class _AccessControlMiddleware {
  static {
    this.allowedUserIds = null;
  }
  static {
    this.adminUserId = null;
  }
  static {
    this.notifiedUsers = /* @__PURE__ */ new Set();
  }
  static {
    this.configService = null;
  }
  static {
    this.bot = null;
  }
  static setConfigService(config) {
    _AccessControlMiddleware.configService = config;
  }
  static setBot(bot2) {
    _AccessControlMiddleware.bot = bot2;
  }
  static initializeAllowedUsers() {
    if (_AccessControlMiddleware.allowedUserIds === null) {
      if (!_AccessControlMiddleware.configService) {
        throw new Error("ConfigService not set in AccessControlMiddleware");
      }
      const allowedIds = _AccessControlMiddleware.configService.getAllowedUserIds();
      _AccessControlMiddleware.allowedUserIds = new Set(allowedIds);
      const configAdminId = _AccessControlMiddleware.configService.getAdminUserId();
      if (configAdminId) {
        _AccessControlMiddleware.adminUserId = configAdminId;
      } else {
        const firstUser = Array.from(_AccessControlMiddleware.allowedUserIds)[0];
        if (firstUser) {
          _AccessControlMiddleware.adminUserId = firstUser;
        }
      }
      console.log(`Access Control: ${_AccessControlMiddleware.allowedUserIds.size} user(s) allowed`);
      if (_AccessControlMiddleware.adminUserId) {
        console.log(`Access Control: Admin user ID: ${_AccessControlMiddleware.adminUserId}`);
      }
    }
    return _AccessControlMiddleware.allowedUserIds;
  }
  static async requireAccess(ctx, next) {
    if (!ctx.from) {
      await ctx.reply("Unable to identify user. Please try again.");
      return;
    }
    const userId = ctx.from.id;
    const allowedUsers = _AccessControlMiddleware.initializeAllowedUsers();
    if (!allowedUsers.has(userId)) {
      console.log(`Unauthorized access attempt from user ${userId}`);
      await _AccessControlMiddleware.notifyAdminOfUnauthorizedAccess(ctx);
      if (_AccessControlMiddleware.isAutoKillEnabled()) {
        await ctx.reply(
          `\u{1F6AB} Unauthorized access detected.

The Telegram User ID is: ${userId}

The bot worker is now shutting down for security reasons.`
        );
        console.log(`AUTO_KILL: Unauthorized access from ${userId}. Shutting down worker...`);
        setTimeout(() => {
          process.exit(1);
        }, 1e3);
        return;
      }
      await ctx.reply(
        `\u{1F6AB} You don't have access to this bot.

Your Telegram User ID is: ${userId}

Please contact the bot administrator to get access.`
      );
      return;
    }
    await next();
  }
  static isAllowed(userId) {
    const allowedUsers = _AccessControlMiddleware.initializeAllowedUsers();
    return allowedUsers.has(userId);
  }
  static getAllowedUserIds() {
    const allowedUsers = this.initializeAllowedUsers();
    return Array.from(allowedUsers);
  }
  static isAdmin(userId) {
    this.initializeAllowedUsers();
    return _AccessControlMiddleware.adminUserId === userId;
  }
  static async notifyAdminOfDownload(ctx, url) {
    if (!_AccessControlMiddleware.bot || !_AccessControlMiddleware.adminUserId || !ctx.from) {
      return;
    }
    const userId = ctx.from.id;
    if (_AccessControlMiddleware.isAdmin(userId)) {
      return;
    }
    try {
      const username = ctx.from.username ? `@${ctx.from.username}` : "No username";
      const firstName = ctx.from.first_name || "Unknown";
      const lastName = ctx.from.last_name || "";
      const fullName = `${firstName} ${lastName}`.trim();
      const notificationMessage = [
        "\u{1F4E5} <b>Download Request</b>",
        "",
        "<b>User Information:</b>",
        `\u2022 Name: ${fullName}`,
        `\u2022 Username: ${username}`,
        `\u2022 User ID: <code>${userId}</code>`,
        "",
        "<b>Requested Link:</b>",
        `<code>${url}</code>`,
        "",
        `<i>Time: ${(/* @__PURE__ */ new Date()).toLocaleString()}</i>`
      ].join("\n");
      const sentMessage = await _AccessControlMiddleware.bot.api.sendMessage(
        _AccessControlMiddleware.adminUserId,
        notificationMessage,
        { parse_mode: "HTML" }
      );
      if (_AccessControlMiddleware.configService && sentMessage) {
        const deleteTimeout2 = _AccessControlMiddleware.configService.getMessageDeleteTimeout();
        if (deleteTimeout2 > 0) {
          setTimeout(async () => {
            try {
              await _AccessControlMiddleware.bot.api.deleteMessage(
                _AccessControlMiddleware.adminUserId,
                sentMessage.message_id
              );
            } catch (error) {
              console.error("Failed to delete admin notification message:", error);
            }
          }, deleteTimeout2);
        }
      }
      console.log(`Notified admin ${_AccessControlMiddleware.adminUserId} about download request from ${userId}`);
    } catch (error) {
      console.error("Failed to notify admin of download request:", error);
    }
  }
  static isAutoKillEnabled() {
    if (!_AccessControlMiddleware.configService) {
      return false;
    }
    return _AccessControlMiddleware.configService.isAutoKillEnabled();
  }
  static async notifyAdminOfUnauthorizedAccess(ctx) {
    if (!_AccessControlMiddleware.bot || !_AccessControlMiddleware.adminUserId || !ctx.from) {
      return;
    }
    try {
      const userId = ctx.from.id;
      const username = ctx.from.username ? `@${ctx.from.username}` : "No username";
      const firstName = ctx.from.first_name || "Unknown";
      const lastName = ctx.from.last_name || "";
      const fullName = `${firstName} ${lastName}`.trim();
      const message = ctx.message?.text || ctx.callbackQuery?.data || "Unknown action";
      const notificationMessage = [
        "\u{1F6A8} <b>Unauthorized Access Attempt</b>",
        "",
        "<b>User Information:</b>",
        `\u2022 Name: ${fullName}`,
        `\u2022 Username: ${username}`,
        `\u2022 User ID: <code>${userId}</code>`,
        "",
        "<b>Attempted Action:</b>",
        `<code>${message}</code>`,
        "",
        `<i>Time: ${(/* @__PURE__ */ new Date()).toLocaleString()}</i>`
      ].join("\n");
      const sentMessage = await _AccessControlMiddleware.bot.api.sendMessage(
        _AccessControlMiddleware.adminUserId,
        notificationMessage,
        { parse_mode: "HTML" }
      );
      if (_AccessControlMiddleware.configService && sentMessage) {
        const deleteTimeout2 = _AccessControlMiddleware.configService.getMessageDeleteTimeout();
        if (deleteTimeout2 > 0) {
          setTimeout(async () => {
            try {
              await _AccessControlMiddleware.bot.api.deleteMessage(
                _AccessControlMiddleware.adminUserId,
                sentMessage.message_id
              );
            } catch (error) {
              console.error("Failed to delete admin notification message:", error);
            }
          }, deleteTimeout2);
        }
      }
      console.log(`Notified admin ${_AccessControlMiddleware.adminUserId} about unauthorized access from ${userId}`);
    } catch (error) {
      console.error("Failed to notify admin of unauthorized access:", error);
    }
  }
};

// src/utils/message.utils.ts
var MessageUtils = class {
  /**
   * Schedules a message for automatic deletion after a timeout
   * @param ctx - The context object containing bot API
   * @param messageId - The ID of the message to delete
   * @param timeoutMs - Timeout in milliseconds (default: 10000 = 10 seconds)
   */
  static async scheduleMessageDeletion(ctx, messageId, timeoutMs = 1e4) {
    if (timeoutMs <= 0) {
      return;
    }
    setTimeout(async () => {
      try {
        await ctx.api.deleteMessage(ctx.chat.id, messageId);
      } catch (error) {
        console.error("Failed to delete message:", error);
      }
    }, timeoutMs);
  }
  /**
   * Escapes special characters for Telegram's Markdown format
   * @param text - The text to escape
   * @returns The escaped text safe for use in Markdown messages
   */
  static escapeMarkdown(text) {
    return text.replace(/[_*[\]()~`>#+\-=|{}.!\\]/g, "\\$&");
  }
};

// src/utils/error.utils.ts
var ErrorUtils = class _ErrorUtils {
  /**
   * Extracts a readable error message from an unknown error type
   * @param error - The error to format
   * @returns A human-readable error message string
   */
  static formatError(error) {
    return error instanceof Error ? error.message : "Unknown error";
  }
  /**
   * Creates a standardized error message for failed actions
   * @param action - Description of the action that failed (e.g., "send to terminal")
   * @param error - The error that occurred
   * @returns A formatted error message string
   */
  static createErrorMessage(action, error) {
    return `\u274C Failed to ${action}.

Error: ${_ErrorUtils.formatError(error)}`;
  }
};

// src/features/file-mentions/file-mentions.parser.ts
var FileMentionParser = class {
  constructor() {
    // Pattern: @path/to/file.ext or @"path with spaces/file.ext"
    this.MENTION_PATTERN = /@(?:"([^"]+)"|([^\s]+))/g;
  }
  /**
   * Parse all @mentions from text
   */
  parse(text) {
    const mentions = [];
    let match;
    this.MENTION_PATTERN.lastIndex = 0;
    while ((match = this.MENTION_PATTERN.exec(text)) !== null) {
      const raw = match[0];
      const query = match[1] || match[2];
      const before = text[match.index - 1];
      const after = text[match.index + raw.length];
      if (before === "@" || after === "@") {
        continue;
      }
      mentions.push({
        raw,
        query,
        startIndex: match.index,
        endIndex: match.index + raw.length
      });
    }
    return mentions;
  }
  /**
   * Replace @mentions in text with resolved file references
   */
  replace(text, replacements) {
    let result = text;
    const sorted = Array.from(replacements.entries()).sort((a, b) => b[0].length - a[0].length);
    for (const [mention, replacement] of sorted) {
      result = result.replace(mention, replacement);
    }
    return result;
  }
  /**
   * Check if text contains any @mentions
   */
  hasMentions(text) {
    this.MENTION_PATTERN.lastIndex = 0;
    return this.MENTION_PATTERN.test(text);
  }
};

// src/features/file-mentions/file-mentions.service.ts
var FileMentionService = class {
  constructor(baseUrl, config) {
    this.baseUrl = baseUrl || process.env.OPENCODE_SERVER_URL || "http://localhost:4096";
    this.parser = new FileMentionParser();
    this.config = {
      enabled: config?.enabled ?? true,
      maxResults: config?.maxResults ?? 10,
      maxFileSize: config?.maxFileSize ?? 1e5,
      // 100KB
      includeContent: config?.includeContent ?? true,
      cacheEnabled: config?.cacheEnabled ?? false,
      cacheTTL: config?.cacheTTL ?? 3e5
      // 5 minutes
    };
  }
  /**
   * Parse @mentions from text
   */
  parseMentions(text) {
    return this.parser.parse(text);
  }
  /**
   * Find files matching a query using OpenCode find.files API
   */
  async findFiles(query, directory) {
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const result = await client2.find.files({
        query: {
          query,
          directory,
          dirs: "false"
          // Only files, not directories
        }
      });
      if (!result.data) {
        return [];
      }
      return result.data.slice(0, this.config.maxResults).map((path33, index) => ({
        path: path33,
        // Score based on position (first result = 1.0, decreasing)
        score: 1 - index * 0.1
      }));
    } catch (error) {
      console.error("Failed to find files:", error);
      return [];
    }
  }
  /**
   * Search for files matching all mentions
   */
  async searchMentions(mentions, directory) {
    const results = /* @__PURE__ */ new Map();
    for (const mention of mentions) {
      const matches = await this.findFiles(mention.query, directory);
      results.set(mention, matches);
    }
    return results;
  }
  /**
   * Read file content using OpenCode file.read API
   */
  async readFile(path33) {
    const client2 = createOpencodeClient({ baseUrl: this.baseUrl });
    try {
      const result = await client2.file.read({
        query: { path: path33 }
      });
      if (!result.data) {
        return null;
      }
      return result.data.content;
    } catch (error) {
      console.error(`Failed to read file ${path33}:`, error);
      return null;
    }
  }
  /**
   * Resolve mentions to files with optional content
   */
  async resolveMentions(mentions, selectedFiles, includeContent = this.config.includeContent) {
    const resolved = [];
    for (const mention of mentions) {
      const file = selectedFiles.get(mention);
      if (!file) continue;
      let content;
      if (includeContent) {
        const fileContent = await this.readFile(file.path);
        if (fileContent !== null) {
          if (fileContent.length <= this.config.maxFileSize) {
            content = fileContent;
          } else {
            console.warn(`File ${file.path} too large (${fileContent.length} bytes), skipping content`);
          }
        }
      }
      resolved.push({
        mention,
        file,
        content
      });
    }
    return resolved;
  }
  /**
   * Format resolved mentions for inclusion in prompt
   */
  formatForPrompt(resolved) {
    if (resolved.length === 0) return "";
    let context = "\u{1F4CE} Referenced Files:\n\n";
    for (const item of resolved) {
      context += `File: ${item.file.path}
`;
      if (item.content) {
        context += "```\n" + item.content + "\n```\n\n";
      } else {
        context += "(Content not included)\n\n";
      }
    }
    return context;
  }
  /**
   * Check if the service is enabled
   */
  isEnabled() {
    return this.config.enabled;
  }
};

// src/features/file-mentions/file-mentions.ui.ts
var FileMentionUI = class {
  /**
   * Show file picker for a single mention with multiple matches
   */
  async showFilePicker(ctx, mention, matches) {
    if (matches.length === 0) {
      await ctx.reply(`\u274C No files found matching: ${mention.raw}`);
      return null;
    }
    if (matches.length === 1) {
      return 0;
    }
    const keyboard = matches.slice(0, 10).map((match, index) => [
      {
        text: `${index + 1}. ${this.shortenPath(match.path)}`,
        callback_data: `file:select:${index}`
      }
    ]);
    keyboard.push([
      { text: "\u274C Cancel", callback_data: "file:cancel" }
    ]);
    const message = await ctx.reply(
      `\u{1F50D} Found ${matches.length} match${matches.length > 1 ? "es" : ""} for <code>${this.escapeHtml(mention.raw)}</code>:

Please select the correct file:`,
      {
        parse_mode: "HTML",
        reply_markup: { inline_keyboard: keyboard }
      }
    );
    return new Promise((resolve2) => {
      const listener = async (callbackCtx) => {
        const data = callbackCtx.callbackQuery?.data;
        if (!data) return;
        if (data === "file:cancel") {
          await callbackCtx.answerCallbackQuery("Cancelled");
          await ctx.api.editMessageText(
            message.chat.id,
            message.message_id,
            "\u274C File selection cancelled"
          );
          resolve2(null);
        } else if (data.startsWith("file:select:")) {
          const index = parseInt(data.split(":")[2]);
          await callbackCtx.answerCallbackQuery();
          await ctx.api.editMessageText(
            message.chat.id,
            message.message_id,
            `\u2705 Selected: <code>${this.escapeHtml(matches[index].path)}</code>`,
            { parse_mode: "HTML" }
          );
          resolve2(index);
        }
      };
      ctx.api.on("callback_query", listener);
    });
  }
  /**
   * Show summary of all file matches and get confirmations
   */
  async confirmAllMatches(ctx, matches) {
    const resolved = /* @__PURE__ */ new Map();
    for (const [mention, fileMatches] of matches.entries()) {
      if (fileMatches.length === 0) {
        await ctx.reply(`\u274C No files found matching: ${mention.raw}`);
        return null;
      }
      if (fileMatches.length === 1) {
        resolved.set(mention, fileMatches[0]);
        await ctx.reply(
          `\u2705 <code>${this.escapeHtml(mention.raw)}</code> \u2192 <code>${this.escapeHtml(fileMatches[0].path)}</code>`,
          { parse_mode: "HTML" }
        );
      } else {
        const selectedIndex = await this.showFilePicker(ctx, mention, fileMatches);
        if (selectedIndex === null) {
          return null;
        }
        resolved.set(mention, fileMatches[selectedIndex]);
      }
    }
    return resolved;
  }
  /**
   * Show error message for file mention
   */
  async showError(ctx, mention, error) {
    await ctx.reply(
      `\u274C Error with <code>${this.escapeHtml(mention.raw)}</code>:
${error}`,
      { parse_mode: "HTML" }
    );
  }
  /**
   * Show loading indicator
   */
  async showSearching(ctx, mentionCount) {
    return await ctx.reply(
      `\u{1F50D} Searching for ${mentionCount} file${mentionCount > 1 ? "s" : ""}...`
    );
  }
  /**
   * Shorten long file paths for display
   */
  shortenPath(path33, maxLength = 50) {
    if (path33.length <= maxLength) return path33;
    const parts = path33.split("/");
    if (parts.length <= 2) return path33;
    const filename = parts[parts.length - 1];
    const remaining = maxLength - filename.length - 3;
    if (remaining <= 0) return `.../${filename}`;
    let prefix = "";
    for (let i = 0; i < parts.length - 1; i++) {
      if ((prefix + parts[i]).length < remaining) {
        prefix += parts[i] + "/";
      } else {
        break;
      }
    }
    return `${prefix}.../${filename}`;
  }
  /**
   * Escape HTML special characters
   */
  escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
};

// src/features/elia-extraprompt/extraprompt.handler.ts
import * as fs29 from "fs";
import * as path29 from "path";
import { spawn as spawn3 } from "child_process";
import { fileURLToPath } from "url";
var TELEGRAM_MAX_MESSAGE = 4e3;
var runningSessions = /* @__PURE__ */ new Set();
function getAgentDir() {
  const fromEnv = process.env.ELIA_HELPER_DIR;
  if (fromEnv && fs29.existsSync(fromEnv)) return path29.resolve(fromEnv);
  try {
    const thisDir = path29.dirname(fileURLToPath(import.meta.url));
    for (const rel of ["../..", "../../../..", "../../../../.."]) {
      const candidate = path29.resolve(thisDir, rel);
      if (fs29.existsSync(path29.join(candidate, "logs"))) return candidate;
    }
  } catch {
  }
  return null;
}
function getOpenCodeModelEnv(agentDir) {
  const modelFile = path29.join(agentDir, ".opencode_model");
  if (!fs29.existsSync(modelFile)) return "opencode/big-pickle";
  const id = fs29.readFileSync(modelFile, "utf8").trim() || "big-pickle";
  switch (id) {
    case "nvidia":
      return "mistralai/mixtral-8x7b-instruct-v0.1";
    case "minimax":
      return "opencode/minimax-m2.5-free";
    case "big-pickle":
      return "opencode/big-pickle";
    case "nemotron":
      return "opencode/nemotron-3-super-free";
    case "mimo":
      return "opencode/mimo-v2-flash-free";
    default:
      return "opencode/big-pickle";
  }
}
var ANSI_RE = /\x1b\[[0-9;]*[a-zA-Z]?/g;
function stripAnsi(s) {
  return s.replace(ANSI_RE, "").trim();
}
function summarizeLine(line) {
  const t = stripAnsi(line);
  if (!t) return null;
  if (t.startsWith("\u2192 ")) return "\u{1F527} " + t.slice(2).replace(/\s+/g, " ").slice(0, 120);
  if (t.startsWith("\u2731 ")) return "\u{1F527} " + t.slice(2).replace(/\s+/g, " ").slice(0, 120);
  if (t.startsWith("\u2717 ")) return "\u274C " + t.slice(2).replace(/\s+/g, " ").slice(0, 200);
  if (t.startsWith("$ ")) return "\u2318 " + t.slice(2).replace(/\n/g, " ").slice(0, 100);
  if (t.includes("Wrote file successfully") || t.includes("Write ") || /←\s*Write\s+/.test(t)) {
    const m = t.match(/Write\s+([^\s]+)/) || t.match(/Wrote\s+([^\s]+)/);
    return "\u{1F4DD} Wrote: " + (m ? m[1] : "file");
  }
  return null;
}
function chunkSend(text) {
  const out = [];
  let rest = text;
  while (rest.length > TELEGRAM_MAX_MESSAGE) {
    let split = rest.slice(0, TELEGRAM_MAX_MESSAGE);
    const lastNewline = split.lastIndexOf("\n");
    if (lastNewline > TELEGRAM_MAX_MESSAGE / 2) split = rest.slice(0, lastNewline + 1);
    out.push(split);
    rest = rest.slice(split.length);
  }
  if (rest) out.push(rest);
  return out;
}
async function runExtrapromptWithStream(chatId, extraPrompt, send) {
  const agentDir = getAgentDir();
  if (!agentDir) {
    await send("EliaAI not configured (set ELIA_HELPER_DIR).");
    return;
  }
  const triggerScript = path29.join(agentDir, "trigger_opencode_interactive.sh");
  if (!fs29.existsSync(triggerScript)) {
    await send("Trigger script not found: trigger_opencode_interactive.sh");
    return;
  }
  const key = String(chatId);
  if (runningSessions.has(key)) {
    await send("A session is already running. Wait for it to finish.");
    return;
  }
  runningSessions.add(key);
  const sessionId = Date.now();
  await send(`\u{1F504} New session started (id: ${sessionId})

Streaming agent output\u2026`);
  const agentPayloadsDir = path29.join(agentDir, ".agent_payloads");
  if (!fs29.existsSync(agentPayloadsDir)) {
    fs29.mkdirSync(agentPayloadsDir, { recursive: true });
  }
  const timestamp = (/* @__PURE__ */ new Date()).toISOString().replace(/[:.]/g, "-");
  const promptFile = path29.join(agentPayloadsDir, `prompt_${timestamp}.txt`);
  const promptContent = `# \u{1F6A8} URGENT CONTEXT - ${(/* @__PURE__ */ new Date()).toLocaleString()}

${extraPrompt}
`;
  fs29.writeFileSync(promptFile, promptContent, "utf8");
  let buffer = "";
  let lastSend = 0;
  const SEND_INTERVAL_MS = 2e3;
  const BUF_MAX = 3500;
  const flush = async (force = false) => {
    const now = Date.now();
    if (buffer.length === 0) return;
    if (!force && buffer.length < BUF_MAX && now - lastSend < SEND_INTERVAL_MS) return;
    const chunks = chunkSend(buffer);
    buffer = "";
    lastSend = now;
    for (const c of chunks) {
      if (c.trim()) await send(c).catch(() => {
      });
    }
  };
  return new Promise((resolve2) => {
    const promptContent2 = fs29.readFileSync(promptFile, "utf8");
    const child = spawn3("/bin/zsh", [triggerScript, promptContent2], {
      cwd: agentDir,
      env: {
        ...process.env,
        ELIA_HELPER_DIR: agentDir,
        OPENCODE_MODEL: getOpenCodeModelEnv(agentDir)
      },
      stdio: ["ignore", "pipe", "pipe"]
    });
    const onData = async (raw) => {
      const s = raw.toString("utf8");
      const lines = s.split(/\r?\n/);
      for (const line of lines) {
        const summarized = summarizeLine(line);
        if (summarized !== null) {
          buffer += summarized + "\n";
        } else {
          const clean = stripAnsi(line);
          if (clean) buffer += (clean.length > 400 ? clean.slice(0, 400) + "\u2026" : clean) + "\n";
        }
      }
      await flush();
    };
    child.stdout?.on("data", onData);
    child.stderr?.on("data", onData);
    child.on("exit", async (code, signal) => {
      try {
        if (fs29.existsSync(promptFile)) fs29.unlinkSync(promptFile);
      } catch {
      }
      runningSessions.delete(key);
      await flush(true);
      const status = code === 0 ? "\u2705" : "\u26A0\uFE0F";
      await send(`${status} Session finished (exit: ${code ?? "\u2014"}${signal ? `, signal: ${signal}` : ""})`).catch(() => {
      });
      resolve2();
    });
    child.on("error", async (err) => {
      try {
        if (fs29.existsSync(promptFile)) fs29.unlinkSync(promptFile);
      } catch {
      }
      runningSessions.delete(key);
      await send("\u274C Failed to start agent: " + err.message).catch(() => {
      });
      resolve2();
    });
  });
}
function getEliaAIRuns(agentDir, limit = 20) {
  const logDir = path29.join(agentDir, "logs");
  if (!fs29.existsSync(logDir)) return [];
  const entries = [];
  const files = fs29.readdirSync(logDir);
  for (const name of files) {
    if (name.startsWith("opencode_interactive_") && name.endsWith(".log")) {
      const stat = fs29.statSync(path29.join(logDir, name));
      entries.push({ name, mtime: stat.mtimeMs, type: "interactive" });
    } else if (name.startsWith("opencode_run_") && name.endsWith(".log")) {
      const stat = fs29.statSync(path29.join(logDir, name));
      entries.push({ name, mtime: stat.mtimeMs, type: "cron" });
    }
  }
  entries.sort((a, b) => b.mtime - a.mtime);
  return entries.slice(0, limit);
}
var resumingRun = /* @__PURE__ */ new Map();
function getRunContext(agentDir, logFileName, headLines = 15, tailLines = 15) {
  const logPath = path29.join(agentDir, "logs", logFileName);
  if (!fs29.existsSync(logPath)) return "(log file not found)";
  const raw = fs29.readFileSync(logPath, "utf8");
  const lines = raw.split(/\r?\n/).filter((l) => stripAnsi(l).trim());
  if (lines.length === 0) return "(empty log)";
  const head = lines.slice(0, headLines).map(stripAnsi).join("\n");
  const tail = lines.length > headLines ? lines.slice(-tailLines).map(stripAnsi).join("\n") : "";
  if (!tail) return head.slice(0, 2500);
  return `--- First ${headLines} lines ---
${head.slice(0, 1200)}

--- Last ${tailLines} lines ---
${tail.slice(-1200)}`;
}
async function handleResumeIfSet(ctx) {
  const userId = ctx.from?.id;
  const text = ctx.message?.text?.trim();
  if (userId === void 0 || !text) return false;
  const logFileName = resumingRun.get(userId);
  if (!logFileName) return false;
  resumingRun.delete(userId);
  const agentDir = getAgentDir();
  if (!agentDir) {
    await ctx.reply("EliaAI not configured.");
    return true;
  }
  const prompt = `[Resuming run: ${logFileName}]

${text}`;
  const chatId = ctx.chat.id;
  const send = (t) => ctx.api.sendMessage(chatId, t, { parse_mode: void 0 });
  await runExtrapromptWithStream(chatId, prompt, send);
  return true;
}
function registerExtrapromptHandlers(bot2) {
  const agentDir = getAgentDir();
  if (!agentDir) {
    console.log("[Elia] ELIA_HELPER_DIR not set, /extraprompt and /extra-prompt disabled");
    return;
  }
  const handler = async (ctx) => {
    const msg = ctx.message?.text?.replace(/^\/extraprompt\s*/i, "").replace(/^\/extra-prompt\s*/i, "").trim();
    if (!msg) {
      await ctx.reply("Usage: /extraprompt <your message>");
      return;
    }
    const chatId = ctx.chat?.id;
    if (chatId === void 0) return;
    const send = (text) => bot2.api.sendMessage(chatId, text, { parse_mode: void 0 });
    await runExtrapromptWithStream(chatId, msg, send);
  };
  const runsHandler = async (ctx) => {
    const runs = getEliaAIRuns(agentDir, 20);
    if (runs.length === 0) {
      await ctx.reply("No EliaAI agent runs found in logs/ (opencode_interactive_*.log, opencode_run_*.log).");
      return;
    }
    const lines = ["\u{1F4CB} EliaAI runs (select to see context & resume):", ""];
    runs.forEach((r, i) => {
      const date = new Date(r.mtime);
      const label = r.type === "cron" ? "cron" : "interactive";
      lines.push(`${i + 1}. ${date.toLocaleString()} [${label}] ${r.name}`);
    });
    const keyboard = runs.map((r, i) => [
      { text: `Select #${i + 1}`, callback_data: `wh_run:${r.name}` }
    ]);
    await ctx.reply(lines.join("\n"), {
      reply_markup: { inline_keyboard: keyboard }
    });
  };
  bot2.command("extraprompt", AccessControlMiddleware.requireAccess, handler);
  bot2.command("extra-prompt", AccessControlMiddleware.requireAccess, handler);
  bot2.command("runs", AccessControlMiddleware.requireAccess, runsHandler);
  bot2.callbackQuery(/^wh_run:/, AccessControlMiddleware.requireAccess, async (ctx) => {
    await ctx.answerCallbackQuery();
    const data = ctx.callbackQuery.data;
    const logFileName = data?.replace(/^wh_run:/, "") ?? "";
    if (!logFileName) return;
    const context = getRunContext(agentDir, logFileName);
    const preview = context.length > 3500 ? context.slice(0, 3500) + "\n\u2026" : context;
    await ctx.reply(`\u{1F4C4} Run: ${logFileName}

${preview}`, {
      reply_markup: {
        inline_keyboard: [[{ text: "\u25B6 Resume this run", callback_data: `wh_resume:${logFileName}` }]]
      }
    });
  });
  bot2.callbackQuery(/^wh_resume:/, AccessControlMiddleware.requireAccess, async (ctx) => {
    await ctx.answerCallbackQuery();
    const data = ctx.callbackQuery.data;
    const logFileName = data?.replace(/^wh_resume:/, "") ?? "";
    if (!logFileName) return;
    const userId = ctx.from?.id;
    if (userId === void 0) return;
    resumingRun.set(userId, logFileName);
    await ctx.reply(`\u2705 Resuming run: ${logFileName}

Send your next message to continue this session.`);
  });
}

// src/features/opencode/opencode.bot.ts
import * as fs30 from "fs";
import * as path30 from "path";
import { spawn as spawn4 } from "child_process";
function timeAgo(timestamp) {
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1e3);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);
  if (seconds < 10) return "Few seconds ago";
  if (seconds < 60) return `${seconds} seconds ago`;
  if (minutes < 60) return minutes === 1 ? "1 minute ago" : `${minutes} minutes ago`;
  if (hours < 24) return hours === 1 ? "1 hour ago" : `${hours} hours ago`;
  if (days < 7) return days === 1 ? "1 day ago" : `${days} days ago`;
  return weeks === 1 ? "1 week ago" : `${weeks} weeks ago`;
}
async function transcribeWithWhisper(audioPath) {
  return new Promise((resolve2, reject) => {
    const whisperBin = "/opt/homebrew/bin/whisper";
    const args = [
      audioPath,
      "--model",
      "large-v3",
      "--language",
      "fr",
      "--task",
      "transcribe",
      "--output_format",
      "txt"
    ];
    console.log(`[Whisper] Starting transcription: ${audioPath}`);
    try {
      const stats = fs30.statSync(audioPath);
      console.log(`[Whisper] File size: ${stats.size} bytes`);
      if (stats.size === 0) {
        reject(new Error("Audio file is empty"));
        return;
      }
    } catch (e) {
      reject(new Error(`Cannot access audio file: ${e}`));
      return;
    }
    const whisper = spawn4(whisperBin, args);
    let output = "";
    let errorOutput = "";
    whisper.stdout.on("data", (data) => {
      output += data.toString();
    });
    whisper.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });
    whisper.on("close", (code) => {
      if (code === 0) {
        console.log(`[Whisper] Transcription complete`);
        resolve2(output.trim());
      } else {
        console.error(`[Whisper] Error: ${errorOutput}`);
        reject(new Error(`Whisper failed: ${errorOutput}`));
      }
    });
    whisper.on("error", (err) => {
      console.error(`[Whisper] Spawn error: ${err.message}`);
      reject(err);
    });
  });
}
var OpenCodeBot = class {
  constructor(opencodeService2, configService2) {
    this.opencodeService = opencodeService2;
    this.configService = configService2;
    this.serverService = new OpenCodeServerService();
    this.fileMentionService = new FileMentionService();
    this.fileMentionUI = new FileMentionUI();
  }
  createControlKeyboard() {
    return new Keyboard().text("\u23F9\uFE0F ESC").text("\u21E5 TAB").resized().persistent();
  }
  registerHandlers(bot2) {
    bot2.command("start", AccessControlMiddleware.requireAccess, this.handleStart.bind(this));
    bot2.command("help", AccessControlMiddleware.requireAccess, this.handleStart.bind(this));
    bot2.command("opencode", AccessControlMiddleware.requireAccess, this.handleOpenCode.bind(this));
    bot2.command("esc", AccessControlMiddleware.requireAccess, this.handleEsc.bind(this));
    bot2.command("endsession", AccessControlMiddleware.requireAccess, this.handleEndSession.bind(this));
    bot2.command("rename", AccessControlMiddleware.requireAccess, this.handleRename.bind(this));
    bot2.command("projects", AccessControlMiddleware.requireAccess, this.handleProjects.bind(this));
    bot2.command("sessions", AccessControlMiddleware.requireAccess, this.handleSessions.bind(this));
    bot2.command("undo", AccessControlMiddleware.requireAccess, this.handleUndo.bind(this));
    bot2.command("redo", AccessControlMiddleware.requireAccess, this.handleRedo.bind(this));
    bot2.hears("\u23F9\uFE0F ESC", AccessControlMiddleware.requireAccess, this.handleEsc.bind(this));
    bot2.hears("\u21E5 TAB", AccessControlMiddleware.requireAccess, this.handleTab.bind(this));
    bot2.callbackQuery("esc", AccessControlMiddleware.requireAccess, this.handleEscButton.bind(this));
    bot2.callbackQuery("tab", AccessControlMiddleware.requireAccess, this.handleTabButton.bind(this));
    bot2.callbackQuery(/^oc_session:/, AccessControlMiddleware.requireAccess, this.handleSessionSelect.bind(this));
    bot2.on("message:document", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
    bot2.on("message:photo", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
    bot2.on("message:video", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
    bot2.on("message:audio", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
    bot2.on("message:voice", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
    bot2.on("message:video_note", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
    bot2.on("message:text", AccessControlMiddleware.requireAccess, async (ctx, next) => {
      if (ctx.message?.text?.startsWith("/")) {
        return next();
      }
      if (ctx.message?.text === "\u23F9\uFE0F ESC" || ctx.message?.text === "\u21E5 TAB") {
        return next();
      }
      await this.handleMessageAsPrompt(ctx);
    });
  }
  async handleStart(ctx) {
    try {
      const helpMessage = [
        "\u{1F44B} <b>Welcome to TelegramCoder!</b>",
        "",
        "\u{1F3AF} <b>Session Commands:</b>",
        "/opencode [title] - Start a new OpenCode AI session",
        "   Example: /opencode Fix login bug",
        "/rename &lt;title&gt; - Rename your current session",
        "   Example: /rename Updated task name",
        "/endsession - End and close your current session",
        "/sessions - View your recent sessions (last 5)",
        "/projects - List available projects",
        "",
        "\u26A1\uFE0F <b>Control Commands:</b>",
        "/esc - Abort the current AI operation",
        "/undo - Revert the last message/change",
        "/redo - Restore a previously undone change",
        "\u21E5 TAB button - Cycle between agents (build \u2194 plan)",
        "\u23F9\uFE0F ESC button - Same as /esc command",
        "",
        "\u{1F4CB} <b>Information Commands:</b>",
        "/start - Show this help message",
        "/help - Show this help message",
        "/sessions - View recent sessions with IDs",
        "/projects - List available projects",
        "",
        "\u{1F4AC} <b>How to Use:</b>",
        "1. Start: /opencode My Project",
        "2. Chat: Just send messages directly (no /prompt needed)",
        "3. Upload: Send any file - it saves to /tmp/telegramCoder",
        "4. Control: Use ESC/TAB buttons on session message",
        "5. Rename: /rename New Name (anytime during session)",
        "6. Undo/Redo: /undo or /redo to manage changes",
        "7. End: /endsession when done",
        "",
        "\u{1F916} <b>Agents Available:</b>",
        "\u2022 <b>build</b> - Implements code and makes changes",
        "\u2022 <b>plan</b> - Plans and analyzes without editing",
        "\u2022 Use TAB button to switch between agents",
        "",
        "\u{1F4A1} <b>Tips:</b>",
        "\u2022 This help message stays - reference it anytime!",
        "\u2022 Send files - they're saved to /tmp/telegramCoder",
        "\u2022 Tap the file path to copy it to clipboard",
        "\u2022 Session messages auto-delete after 10 seconds",
        "\u2022 Tab between build/plan agents as needed",
        "\u2022 Use descriptive titles for better organization",
        "\u2022 All messages go directly to the AI",
        "\u2022 Use /undo if AI makes unwanted changes",
        "\u2022 Streaming responses limited to last 50 lines",
        "",
        "\u{1F527} <b>EliaAI (if configured):</b>",
        "/extraprompt &lt;message&gt; - Run EliaAI agent with extra context (streams output here)",
        "/runs - List agent runs (cron + /extraprompt) from EliaAI logs",
        "",
        "\u{1F680} <b>Get started:</b> /opencode"
      ].join("\n");
      await ctx.reply(helpMessage, { parse_mode: "HTML" });
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("show help message", error));
    }
  }
  async handleOpenCode(ctx) {
    try {
      const userId = ctx.from?.id;
      if (!userId) {
        await ctx.reply("\u274C Unable to identify user");
        return;
      }
      if (this.opencodeService.hasActiveSession(userId)) {
        const message = await ctx.reply("\u2705 Session already started", {
          reply_markup: {
            inline_keyboard: [
              [
                { text: "\u23F9\uFE0F ESC", callback_data: "esc" },
                { text: "\u21E5 TAB", callback_data: "tab" }
              ]
            ]
          }
        });
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          message.message_id,
          this.configService.getMessageDeleteTimeout()
        );
        return;
      }
      const text = ctx.message?.text || "";
      const title = text.replace("/opencode", "").trim() || void 0;
      const statusMessage = await ctx.reply("\u{1F504} Starting OpenCode session...");
      try {
        let userSession;
        try {
          userSession = await this.opencodeService.createSession(userId, title);
        } catch (error) {
          if (error instanceof Error && error.message.includes("Cannot connect to OpenCode server")) {
            await ctx.api.editMessageText(
              ctx.chat.id,
              statusMessage.message_id,
              "\u{1F504} OpenCode server not running. Starting server...\n\nThis may take up to 30 seconds."
            );
            const startResult = await this.serverService.startServer();
            if (!startResult.success) {
              await ctx.api.editMessageText(
                ctx.chat.id,
                statusMessage.message_id,
                `\u274C Failed to start OpenCode server.

${startResult.message}

Please start the server manually using:
<code>opencode serve</code>`,
                { parse_mode: "HTML" }
              );
              return;
            }
            await ctx.api.editMessageText(
              ctx.chat.id,
              statusMessage.message_id,
              "\u2705 OpenCode server started!\n\n\u{1F504} Creating session..."
            );
            userSession = await this.opencodeService.createSession(userId, title);
          } else {
            throw error;
          }
        }
        const successMessage = await ctx.api.editMessageText(
          ctx.chat.id,
          statusMessage.message_id,
          "\u2705 Session started",
          {
            reply_markup: {
              inline_keyboard: [
                [
                  { text: "\u23F9\uFE0F ESC", callback_data: "esc" },
                  { text: "\u21E5 TAB", callback_data: "tab" }
                ]
              ]
            }
          }
        );
        const messageId = typeof successMessage === "object" && successMessage && "message_id" in successMessage ? successMessage.message_id : statusMessage.message_id;
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          messageId,
          this.configService.getMessageDeleteTimeout()
        );
        this.opencodeService.updateSessionContext(userId, ctx.chat.id, messageId);
        this.opencodeService.startEventStream(userId, ctx).catch((error) => {
          console.error("Event stream error:", error);
        });
      } catch (error) {
        await ctx.api.editMessageText(
          ctx.chat.id,
          statusMessage.message_id,
          ErrorUtils.createErrorMessage("start OpenCode session", error)
        );
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("start OpenCode session", error));
    }
  }
  async handleMessageAsPrompt(ctx) {
    try {
      const userId = ctx.from?.id;
      if (!userId) {
        await ctx.reply("\u274C Unable to identify user");
        return;
      }
      const resumed = await handleResumeIfSet(ctx);
      if (resumed) return;
      if (!this.opencodeService.hasActiveSession(userId)) {
        await ctx.reply("\u274C No active OpenCode session. Use /opencode to start a session first.");
        return;
      }
      const promptText = ctx.message?.text?.trim() || "";
      if (!promptText) {
        return;
      }
      const mentions = this.fileMentionService.parseMentions(promptText);
      if (mentions.length > 0 && this.fileMentionService.isEnabled()) {
        await this.handlePromptWithMentions(ctx, userId, promptText, mentions);
      } else {
        await this.sendPromptToOpenCode(ctx, userId, promptText);
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("send prompt to OpenCode", error));
    }
  }
  async handlePromptWithMentions(ctx, userId, promptText, mentions) {
    try {
      const searchMessage = await this.fileMentionUI.showSearching(ctx, mentions.length);
      const matches = await this.fileMentionService.searchMentions(mentions);
      await ctx.api.deleteMessage(searchMessage.chat.id, searchMessage.message_id).catch(() => {
      });
      const selectedFiles = await this.fileMentionUI.confirmAllMatches(ctx, matches);
      if (!selectedFiles) {
        await ctx.reply("\u274C File selection cancelled");
        return;
      }
      const resolved = await this.fileMentionService.resolveMentions(
        mentions,
        selectedFiles,
        true
      );
      const fileContext = this.fileMentionService.formatForPrompt(resolved);
      await this.sendPromptToOpenCode(ctx, userId, promptText, fileContext);
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("process file mentions", error));
    }
  }
  async sendPromptToOpenCode(ctx, userId, promptText, fileContext) {
    try {
      const response = await this.opencodeService.sendPrompt(userId, promptText, fileContext);
      const isMarkdown = this.isMarkdownContent(response);
      const hasManyLines = response.split("\n").length > 20;
      if (isMarkdown || hasManyLines) {
        const buffer = Buffer.from(response, "utf-8");
        await ctx.replyWithDocument(new InputFile(buffer, "response.md"));
        return;
      }
      const maxLength = 4e3;
      if (response.length <= maxLength) {
        await ctx.reply(formatAsHtml(response), { parse_mode: "HTML" });
      } else {
        const chunks = this.splitIntoChunks(response, maxLength);
        for (const chunk of chunks) {
          await ctx.reply(formatAsHtml(chunk), { parse_mode: "HTML" });
        }
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("send prompt to OpenCode", error));
    }
  }
  isMarkdownContent(text) {
    return text.trimStart().startsWith("#");
  }
  splitIntoChunks(text, maxLength) {
    const chunks = [];
    let currentChunk = "";
    const lines = text.split("\n");
    for (const line of lines) {
      if (currentChunk.length + line.length + 1 > maxLength) {
        if (currentChunk) {
          chunks.push(currentChunk);
        }
        currentChunk = line;
      } else {
        if (currentChunk) {
          currentChunk += "\n" + line;
        } else {
          currentChunk = line;
        }
      }
    }
    if (currentChunk) {
      chunks.push(currentChunk);
    }
    return chunks;
  }
  async handleEndSession(ctx) {
    try {
      const userId = ctx.from?.id;
      if (!userId) {
        await ctx.reply("\u274C Unable to identify user");
        return;
      }
      if (!this.opencodeService.hasActiveSession(userId)) {
        await ctx.reply("\u2139\uFE0F You don't have an active OpenCode session. Use /opencode to start one.");
        return;
      }
      const success = await this.opencodeService.deleteSession(userId);
      if (success) {
        const sentMessage = await ctx.reply("\u2705 OpenCode session ended successfully.");
        const deleteTimeout2 = this.configService.getMessageDeleteTimeout();
        if (deleteTimeout2 > 0 && sentMessage) {
          await MessageUtils.scheduleMessageDeletion(
            ctx,
            sentMessage.message_id,
            deleteTimeout2
          );
        }
      } else {
        await ctx.reply("\u26A0\uFE0F Failed to end session. It may have already been closed.");
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("end OpenCode session", error));
    }
  }
  async handleEsc(ctx) {
    try {
      const userId = ctx.from?.id;
      if (!userId) {
        await ctx.reply("\u274C Unable to identify user");
        return;
      }
      if (!this.opencodeService.hasActiveSession(userId)) {
        await ctx.reply("\u2139\uFE0F You don't have an active OpenCode session. Use /opencode to start one.");
        return;
      }
      const success = await this.opencodeService.abortSession(userId);
      if (success) {
        await ctx.reply("\u23F9\uFE0F Current operation aborted successfully.");
      } else {
        await ctx.reply("\u26A0\uFE0F Failed to abort operation. Please try again.");
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("abort OpenCode operation", error));
    }
  }
  async handleTab(ctx) {
    try {
      const userId = ctx.from?.id;
      if (!userId) {
        await ctx.reply("\u274C Unable to identify user");
        return;
      }
      if (!this.opencodeService.hasActiveSession(userId)) {
        await ctx.reply("\u2139\uFE0F You don't have an active OpenCode session. Use /opencode to start one.");
        return;
      }
      try {
        const result = await this.opencodeService.cycleToNextAgent(userId);
        if (result.success && result.currentAgent) {
          const message = await ctx.reply(`\u21E5 <b>${result.currentAgent}</b>`, { parse_mode: "HTML" });
          await MessageUtils.scheduleMessageDeletion(
            ctx,
            message.message_id,
            this.configService.getMessageDeleteTimeout()
          );
        } else {
          const errorMsg = await ctx.reply("\u26A0\uFE0F Failed to cycle agent. Please try again.");
          await MessageUtils.scheduleMessageDeletion(
            ctx,
            errorMsg.message_id,
            this.configService.getMessageDeleteTimeout()
          );
        }
      } catch (error) {
        const errorMsg = await ctx.reply(ErrorUtils.createErrorMessage("cycle agent", error));
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          errorMsg.message_id,
          this.configService.getMessageDeleteTimeout()
        );
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("handle TAB", error));
    }
  }
  async handleEscButton(ctx) {
    try {
      await ctx.answerCallbackQuery();
      await this.handleEsc(ctx);
    } catch (error) {
      await ctx.answerCallbackQuery("Error handling ESC");
      console.error("Error in handleEscButton:", error);
    }
  }
  async handleTabButton(ctx) {
    try {
      await ctx.answerCallbackQuery();
      await this.handleTab(ctx);
    } catch (error) {
      await ctx.answerCallbackQuery("Error handling TAB");
      console.error("Error in handleTabButton:", error);
    }
  }
  async handleSessionSelect(ctx) {
    console.log("[handleSessionSelect] Called!");
    try {
      const data = ctx.callbackQuery.data;
      const sessionId = data?.replace(/^oc_session:/, "");
      console.log("[handleSessionSelect] Session ID:", sessionId);
      if (!sessionId) {
        await ctx.answerCallbackQuery("Invalid session");
        return;
      }
      const userId = ctx.from?.id;
      if (!userId) {
        await ctx.answerCallbackQuery("Cannot identify user");
        return;
      }
      const sessions = await this.opencodeService.getSessions(20);
      const session = sessions.find((s) => s.id === sessionId);
      if (!session) {
        await ctx.answerCallbackQuery("Session not found");
        return;
      }
      await ctx.answerCallbackQuery();
      const shortId = session.id.substring(0, 12);
      const title = session.title || "Untitled";
      const created = new Date(session.created * 1e3).toLocaleString();
      const updated = new Date(session.updated * 1e3).toLocaleString();
      this.opencodeService.attachToSession(userId, session.id, session.title);
      await ctx.reply(
        `\u{1F4CB} <b>Session Attached:</b>

<b>Title:</b> ${title}
<b>ID:</b> <code>${shortId}</code>...
<b>Created:</b> ${created}
<b>Updated:</b> ${updated}

\u2705 You are now attached to this session!
Send any message to continue the conversation.`,
        {
          parse_mode: "HTML",
          reply_markup: {
            inline_keyboard: [
              [
                { text: "\u23F9\uFE0F ESC", callback_data: "esc" },
                { text: "\u21E5 TAB", callback_data: "tab" }
              ]
            ]
          }
        }
      );
    } catch (error) {
      console.error("[handleSessionSelect] Error:", error);
      await ctx.answerCallbackQuery("Error: " + String(error));
    }
  }
  async handleRename(ctx) {
    try {
      const userId = ctx.from?.id;
      if (!userId) {
        await ctx.reply("\u274C Unable to identify user");
        return;
      }
      if (!this.opencodeService.hasActiveSession(userId)) {
        await ctx.reply("\u274C No active session. Use /opencode to start one first.");
        return;
      }
      const text = ctx.message?.text || "";
      const newTitle = text.replace("/rename", "").trim();
      if (!newTitle) {
        await ctx.reply("\u274C Please provide a new title.\n\nUsage: /rename <new title>");
        return;
      }
      const result = await this.opencodeService.updateSessionTitle(userId, newTitle);
      if (result.success) {
        const message = await ctx.reply(`\u2705 Session renamed to: <b>${newTitle}</b>`, { parse_mode: "HTML" });
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          message.message_id,
          this.configService.getMessageDeleteTimeout()
        );
      } else {
        await ctx.reply(`\u274C ${result.message || "Failed to rename session"}`);
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("rename session", error));
    }
  }
  async handleProjects(ctx) {
    try {
      const projects = await this.opencodeService.getProjects();
      if (projects.length === 0) {
        const message2 = await ctx.reply("\u{1F4C2} No projects found");
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          message2.message_id,
          this.configService.getMessageDeleteTimeout()
        );
        return;
      }
      const projectList = projects.map((project, index) => `${index + 1}. ${project.worktree}`).join("\n");
      const message = await ctx.reply(`\u{1F4C2} <b>Available Projects:</b>

${projectList}`, {
        parse_mode: "HTML"
      });
      await MessageUtils.scheduleMessageDeletion(
        ctx,
        message.message_id,
        this.configService.getMessageDeleteTimeout()
      );
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("list projects", error));
    }
  }
  async handleSessions(ctx) {
    try {
      console.log("[handleSessions] Called! userId:", ctx.from?.id);
      const sessions = await this.opencodeService.getSessions(10);
      console.log("[handleSessions] Got sessions:", sessions.length);
      if (sessions.length === 0) {
        await ctx.reply("\u{1F4AC} No OpenCode server sessions found. Use /opencode to start a new session.");
        return;
      }
      const lines = ["\u{1F4CB} <b>OpenCode Sessions</b> (tap to resume):", ""];
      sessions.forEach((s, i) => {
        const shortId = s.id.substring(0, 8);
        const title = s.title || "Untitled";
        const createdAgo = timeAgo(s.created);
        const updatedAgo = timeAgo(s.updated);
        lines.push(`${i + 1}. <b>${title}</b>
   \u{1F194} ${shortId}...
   \u{1F4C5} Created: ${createdAgo}
   \u{1F4AC} Last chat: ${updatedAgo}`);
      });
      const keyboard = sessions.map((s, i) => {
        const createdAgo = timeAgo(s.created);
        const updatedAgo = timeAgo(s.updated);
        const label = `${i + 1}. ${updatedAgo}`;
        return [{ text: label, callback_data: `oc_session:${s.id}` }];
      });
      await ctx.reply(lines.join("\n"), {
        parse_mode: "HTML",
        reply_markup: { inline_keyboard: keyboard }
      });
    } catch (error) {
      console.error("[handleSessions] Error:", error);
      await ctx.reply("Error: " + String(error));
    }
  }
  async handleUndo(ctx) {
    const userId = ctx.from?.id;
    if (!userId) return;
    try {
      const result = await this.opencodeService.undoLastMessage(userId);
      if (result.success) {
        const message = await ctx.reply("\u21A9\uFE0F <b>Undone</b> - Last message reverted", { parse_mode: "HTML" });
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          message.message_id,
          this.configService.getMessageDeleteTimeout()
        );
      } else {
        const errorMsg = result.message || "Failed to undo last message";
        const message = await ctx.reply(`\u274C ${errorMsg}`);
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          message.message_id,
          this.configService.getMessageDeleteTimeout()
        );
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("undo", error));
    }
  }
  async handleRedo(ctx) {
    const userId = ctx.from?.id;
    if (!userId) return;
    try {
      const result = await this.opencodeService.redoLastMessage(userId);
      if (result.success) {
        const message = await ctx.reply("\u21AA\uFE0F <b>Redone</b> - Change restored", { parse_mode: "HTML" });
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          message.message_id,
          this.configService.getMessageDeleteTimeout()
        );
      } else {
        const errorMsg = result.message || "Failed to redo last message";
        const message = await ctx.reply(`\u274C ${errorMsg}`);
        await MessageUtils.scheduleMessageDeletion(
          ctx,
          message.message_id,
          this.configService.getMessageDeleteTimeout()
        );
      }
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("redo", error));
    }
  }
  async handleFileUpload(ctx) {
    try {
      const message = ctx.message;
      if (!message) return;
      let fileId;
      let fileName;
      let fileType = "file";
      if (message.document) {
        fileId = message.document.file_id;
        fileName = message.document.file_name || `document_${Date.now()}`;
        fileType = "document";
      } else if (message.photo && message.photo.length > 0) {
        const photo = message.photo[message.photo.length - 1];
        fileId = photo.file_id;
        fileName = `photo_${Date.now()}.jpg`;
        fileType = "photo";
      } else if (message.video) {
        fileId = message.video.file_id;
        fileName = message.video.file_name || `video_${Date.now()}.mp4`;
        fileType = "video";
      } else if (message.audio) {
        fileId = message.audio.file_id;
        fileName = message.audio.file_name || `audio_${Date.now()}.mp3`;
        fileType = "audio";
      } else if (message.voice) {
        fileId = message.voice.file_id;
        fileName = `voice_${Date.now()}.ogg`;
        fileType = "voice";
      } else if (message.video_note) {
        fileId = message.video_note.file_id;
        fileName = `video_note_${Date.now()}.mp4`;
        fileType = "video_note";
      }
      if (!fileId || !fileName) {
        await ctx.reply("\u274C Unable to process this file type");
        return;
      }
      const file = await ctx.api.getFile(fileId);
      if (!file.file_path) {
        await ctx.reply("\u274C Unable to get file path from Telegram");
        return;
      }
      const fileUrl = `https://api.telegram.org/file/bot${ctx.api.token}/${file.file_path}`;
      const response = await fetch(fileUrl);
      if (!response.ok) {
        await ctx.reply("\u274C Failed to download file from Telegram");
        return;
      }
      const saveDir = "/tmp/telegramCoder";
      if (!fs30.existsSync(saveDir)) {
        console.log(`Creating directory: ${saveDir}`);
        fs30.mkdirSync(saveDir, { recursive: true });
        console.log(`\u2713 Directory created: ${saveDir}`);
      }
      const savePath = path30.join(saveDir, fileName);
      const buffer = Buffer.from(await response.arrayBuffer());
      fs30.writeFileSync(savePath, buffer);
      if (fileType === "voice" || fileType === "audio") {
        const userId = ctx.from?.id;
        await ctx.reply("\u{1F399}\uFE0F Transcription en cours avec Whisper... (large-v3, fran\xE7ais)");
        try {
          const transcription = await transcribeWithWhisper(savePath);
          if (!transcription || transcription.trim() === "") {
            await ctx.reply("\u26A0\uFE0F Aucun texte d\xE9tect\xE9 dans l'audio.");
            return;
          }
          console.log(`[Whisper] Transcription: ${transcription.substring(0, 100)}...`);
          if (userId && this.opencodeService.hasActiveSession(userId)) {
            await ctx.reply("\u{1F4E4} Envoi de la transcription \xE0 OpenCode...");
            const response2 = await this.opencodeService.sendPrompt(
              userId,
              `[Transcription vocale]: ${transcription}`
            );
            await ctx.reply(response2 || "\u2705 Transcription envoy\xE9e \xE0 OpenCode!");
          } else {
            await ctx.reply("\u{1F399}\uFE0F D\xE9marrage d'une session OpenCode...");
            try {
              const sessionTitle = `Voice: ${transcription.substring(0, 30)}...`;
              const newSession = await this.opencodeService.createSession(userId, sessionTitle);
              this.opencodeService.updateSessionContext(userId, ctx.chat?.id || 0, ctx.message?.message_id || 0);
              await ctx.reply("\u2705 Session d\xE9marr\xE9e! Envoi de la transcription...");
              const response2 = await this.opencodeService.sendPrompt(
                userId,
                `[Transcription vocale]: ${transcription}`
              );
              await ctx.reply(response2 || "\u2705 Transcription envoy\xE9e \xE0 la nouvelle session!");
            } catch (sessionError) {
              console.error("[Voice] Session error:", sessionError);
              await ctx.reply(
                `\u{1F399}\uFE0F <b>Transcription:</b>

${transcription}

\u274C Impossible de d\xE9marrer une session: ${sessionError instanceof Error ? sessionError.message : String(sessionError)}

Utilise /opencode pour d\xE9marrer une session manuellement.`,
                { parse_mode: "HTML" }
              );
            }
          }
          fs30.unlinkSync(savePath);
          return;
        } catch (whisperError) {
          console.error("[Whisper] Error:", whisperError);
          await ctx.reply(`\u274C Erreur de transcription: ${whisperError instanceof Error ? whisperError.message : String(whisperError)}`);
        }
      }
      const confirmMessage = await ctx.reply(
        `\u2705 <b>File saved!</b>

Path: <code>${savePath}</code>

Tap the path to copy it.`,
        { parse_mode: "HTML" }
      );
      await MessageUtils.scheduleMessageDeletion(
        ctx,
        confirmMessage.message_id,
        this.configService.getMessageDeleteTimeout()
      );
      console.log(`\u2713 File saved: ${savePath} (${fileType}, ${buffer.length} bytes)`);
    } catch (error) {
      console.error("Error handling file upload:", error);
      await ctx.reply(ErrorUtils.createErrorMessage("save file", error));
    }
  }
};

// src/features/opencode/analyze-bottleneck.bot.ts
import * as fs31 from "fs";
import * as path31 from "path";
var AnalyzeBottleneckBot = class {
  constructor(opencodeService2, configService2) {
    this.opencodeService = opencodeService2;
    this.configService = configService2;
  }
  registerHandlers(bot2) {
    bot2.command("analyse_your_bottleneck", AccessControlMiddleware.requireAccess, this.handleAnalyzeBottleneck.bind(this));
  }
  async handleAnalyzeBottleneck(ctx) {
    try {
      const eventsDir = path31.join(process.cwd(), "events");
      const analysis = [
        "\u{1F50D} <b>RAPPORT D'ANALYSE - Goulots d'\xE9tranglement AI</b>\n",
        "\u2550".repeat(40) + "\n"
      ];
      let totalIssues = 0;
      const errorLogPath = path31.join(eventsDir, "session-errors.json");
      if (fs31.existsSync(errorLogPath)) {
        try {
          const errorLog = JSON.parse(fs31.readFileSync(errorLogPath, "utf8"));
          if (errorLog.length > 0) {
            analysis.push(`\u{1F4CA} <b>Errors d\xE9tect\xE9s:</b> ${errorLog.length}
`);
            const errorTypes = {};
            errorLog.forEach((e) => {
              const errorKey = e.error || "Unknown";
              errorTypes[errorKey] = (errorTypes[errorKey] || 0) + 1;
            });
            Object.entries(errorTypes).forEach(([error, count]) => {
              analysis.push(`  \u2022 ${error}: ${count}x`);
            });
            analysis.push("");
            totalIssues += errorLog.length;
          }
        } catch (e) {
        }
      }
      const lastErrorPath = path31.join(eventsDir, "session-error.last.json");
      if (fs31.existsSync(lastErrorPath)) {
        try {
          const lastError = JSON.parse(fs31.readFileSync(lastErrorPath, "utf8"));
          analysis.push("\u{1F4CC} <b>Derni\xE8re erreur:</b>");
          analysis.push(`  Error: ${lastError.properties?.error || "N/A"}`);
          analysis.push(`  Message: ${lastError.properties?.message || "N/A"}`);
          if (lastError.properties?.stack) {
            analysis.push(`  Stack: ${lastError.properties.stack.substring(0, 200)}...`);
          }
          analysis.push("");
        } catch (e) {
        }
      }
      const sessions = await this.opencodeService.getSessions(10);
      if (sessions.length > 0) {
        analysis.push(`\u{1F4CB} <b>Sessions r\xE9centes:</b> ${sessions.length}
`);
        sessions.forEach((s, i) => {
          analysis.push(`  ${i + 1}. ${s.title.substring(0, 40)}`);
        });
        analysis.push("");
      }
      const messageUpdatedPath = path31.join(eventsDir, "message-updated.last.json");
      if (fs31.existsSync(messageUpdatedPath)) {
        try {
          const lastMsg = JSON.parse(fs31.readFileSync(messageUpdatedPath, "utf8"));
          if (lastMsg.properties?.parts) {
            const textParts = lastMsg.properties.parts.filter((p) => p.type === "text");
            const toolParts = lastMsg.properties.parts.filter((p) => p.type === "tool");
            const reasoningParts = lastMsg.properties.parts.filter((p) => p.type === "reasoning");
            analysis.push("\u{1F4AC} <b>Dernier message:</b>");
            analysis.push(`  Text parts: ${textParts.length}`);
            analysis.push(`  Tool calls: ${toolParts.length}`);
            analysis.push(`  Reasoning: ${reasoningParts.length}`);
            analysis.push("");
          }
        } catch (e) {
        }
      }
      const lspPath = path31.join(eventsDir, "lsp-client-diagnostics.last.json");
      if (fs31.existsSync(lspPath)) {
        try {
          const lspDiags = JSON.parse(fs31.readFileSync(lspPath, "utf8"));
          if (lspDiags.properties?.diagnostics) {
            const diags = lspDiags.properties.diagnostics;
            const errors = diags.filter((d) => d.severity === 1);
            const warnings = diags.filter((d) => d.severity === 2);
            analysis.push("\u{1F527} <b>LSP Diagnostics:</b>");
            analysis.push(`  Errors: ${errors.length}`);
            analysis.push(`  Warnings: ${warnings.length}`);
            if (errors.length > 0) {
              analysis.push("\n  \u{1F4D5} <b>Errors:</b>");
              errors.slice(0, 5).forEach((e) => {
                analysis.push(`    - ${e.message?.substring(0, 80)}`);
              });
            }
            analysis.push("");
          }
        } catch (e) {
        }
      }
      const sessionDiffPath = path31.join(eventsDir, "session-diff.last.json");
      if (fs31.existsSync(sessionDiffPath)) {
        try {
          const sessionDiff = JSON.parse(fs31.readFileSync(sessionDiffPath, "utf8"));
          analysis.push("\u{1F4CA} <b>Session Diff:</b>");
          if (sessionDiff.properties?.diffs) {
            const diffs = sessionDiff.properties.diffs;
            analysis.push(`  Total changes: ${diffs.length}`);
            const fileEdits = diffs.filter((d) => d.type === "file_edit");
            const fileCreations = diffs.filter((d) => d.type === "file_creation");
            const fileDeletions = diffs.filter((d) => d.type === "file_deletion");
            analysis.push(`  File edits: ${fileEdits.length}`);
            analysis.push(`  File creations: ${fileCreations.length}`);
            analysis.push(`  File deletions: ${fileDeletions.length}`);
          }
          analysis.push("");
        } catch (e) {
        }
      }
      const commandExecutedPath = path31.join(eventsDir, "command-executed.last.json");
      if (fs31.existsSync(commandExecutedPath)) {
        try {
          const cmdExec = JSON.parse(fs31.readFileSync(commandExecutedPath, "utf8"));
          analysis.push("\u{1F5A5}\uFE0F <b>Last Command:</b>");
          analysis.push(`  Command: ${cmdExec.properties?.command || "N/A"}`);
          analysis.push(`  Exit code: ${cmdExec.properties?.exitCode || "N/A"}`);
          analysis.push("");
        } catch (e) {
        }
      }
      analysis.push("\u2550".repeat(40));
      analysis.push("\n\u{1F3AF} <b>R\xC9SUM\xC9:</b>");
      analysis.push(`  Total issues: ${totalIssues}`);
      if (totalIssues === 0) {
        analysis.push("\n\u2705 <b>Pas de probl\xE8mes d\xE9tect\xE9s!</b>");
        analysis.push("Le syst\xE8me fonctionne correctement.");
      } else {
        analysis.push("\n\u26A0\uFE0F <b>Probl\xE8mes d\xE9tect\xE9s - Analyse recommand\xE9e:</b>");
        analysis.push("1. V\xE9rifier les logs d'erreur ci-dessus");
        analysis.push("2. Examiner les diagnostics LSP");
        analysis.push("3. Consid\xE9rer les outils utilis\xE9s");
      }
      const report = analysis.join("\n");
      await ctx.reply(report, { parse_mode: "HTML" });
    } catch (error) {
      await ctx.reply(ErrorUtils.createErrorMessage("analyze bottleneck", error));
    }
  }
};

// src/app.ts
import dotenv from "dotenv";
import * as fs32 from "fs";
import * as path32 from "path";
console.log("[TelegramCoder] Starting bot...");
dotenv.config();
var configService = new ConfigService();
try {
  configService.validate();
  console.log("[TelegramCoder] Configuration loaded successfully");
  console.log(configService.getDebugInfo());
} catch (error) {
  console.error("[TelegramCoder] Configuration error:", error);
  process.exit(1);
}
var tokens = configService.getTelegramBotTokens();
if (tokens.length === 0) {
  console.error("[TelegramCoder] No bot tokens found in configuration");
  process.exit(1);
}
var botToken = tokens[0];
console.log(`[TelegramCoder] Initializing with token: ${botToken.substring(0, 10)}...`);
var bot = new Bot2(botToken);
var opencodeService = new OpenCodeService();
bot.catch((err) => {
  const ctx = err.ctx;
  console.error(`[TelegramCoder] Error while handling update ${ctx.update.update_id}:`, err.error);
});
AccessControlMiddleware.setConfigService(configService);
AccessControlMiddleware.setBot(bot);
var opencodeBot = new OpenCodeBot(opencodeService, configService);
var analyzeBottleneckBot = new AnalyzeBottleneckBot(opencodeService, configService);
opencodeBot.registerHandlers(bot);
analyzeBottleneckBot.registerHandlers(bot);
registerExtrapromptHandlers(bot);
async function startBot() {
  try {
    console.log("[TelegramCoder] Starting initialization...");
    if (configService.shouldCleanUpMediaDir()) {
      const botMediaPath = path32.join(configService.getMediaTmpLocation(), "bot-1");
      if (fs32.existsSync(botMediaPath)) {
        console.log(`[TelegramCoder] Cleaning up media directory: ${botMediaPath}`);
        fs32.rmSync(botMediaPath, { recursive: true, force: true });
        console.log("[TelegramCoder] \u2705 Media directory cleaned");
      }
    }
    try {
      const me = await bot.api.getMe();
      const fullName = [me.first_name, me.last_name].filter(Boolean).join(" ");
      console.log(`[TelegramCoder] Bot info: ${fullName} (@${me.username})`);
    } catch (error) {
      console.error("[TelegramCoder] Failed to get bot info:", error);
    }
    try {
      await bot.api.setMyCommands([
        { command: "start", description: "Show help message" },
        { command: "help", description: "Show help message" },
        { command: "opencode", description: "Start an OpenCode session" },
        { command: "rename", description: "Rename current session" },
        { command: "endsession", description: "End your OpenCode session" },
        { command: "esc", description: "Abort current AI operation" },
        { command: "sessions", description: "List sessions" },
        { command: "extraprompt", description: "Run EliaAI agent with extra context" },
        { command: "runs", description: "List EliaAI agent runs (cron + extraprompt)" },
        { command: "analyse_your_bottleneck", description: "Analyze AI bottlenecks and issues" }
      ]);
      console.log("[TelegramCoder] \u2705 Bot commands registered");
    } catch (error) {
      console.error("[TelegramCoder] Failed to set bot commands:", error);
    }
    console.log("[TelegramCoder] About to start bot with webhook...");
    const webhookUrl = process.env.TELEGRAM_WEBHOOK_URL;
    if (webhookUrl) {
      console.log("[TelegramCoder] Using webhook mode:", webhookUrl);
      await bot.api.setWebhook(webhookUrl);
      console.log("[TelegramCoder] \u2705 Webhook set successfully");
    } else {
      console.log("[TelegramCoder] No webhook URL, using long polling...");
      await bot.start({
        polling: {
          timeout: 30
        }
      });
    }
    console.log("[TelegramCoder] \u2705 Bot started successfully");
  } catch (error) {
    console.error("[TelegramCoder] Failed to start:", error);
    process.exit(1);
  }
}
var shuttingDown = false;
async function gracefulShutdown(signal) {
  if (shuttingDown) {
    console.log("[TelegramCoder] Shutdown already in progress...");
    return;
  }
  shuttingDown = true;
  console.log(`[TelegramCoder] Received ${signal}, shutting down gracefully...`);
  try {
    await bot.stop();
    console.log("[TelegramCoder] \u2705 Shutdown complete");
    process.exit(0);
  } catch (error) {
    console.error("[TelegramCoder] Error during shutdown:", error);
    process.exit(1);
  }
}
process.on("SIGINT", () => gracefulShutdown("SIGINT"));
process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
process.on("unhandledRejection", (reason, promise) => {
  console.error("[TelegramCoder] Unhandled Rejection at:", promise, "reason:", reason);
});
process.on("uncaughtException", (error) => {
  console.error("[TelegramCoder] Uncaught Exception:", error);
  gracefulShutdown("UNCAUGHT_EXCEPTION");
});
startBot().catch((error) => {
  console.error("[TelegramCoder] Fatal error:", error);
  process.exit(1);
});
//# sourceMappingURL=app.js.map

var ur = Object.defineProperty;
var fr = (e, t, n) => t in e ? ur(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var J = (e, t, n) => fr(e, typeof t != "symbol" ? t + "" : t, n);
import * as dr from "vue";
import { toRaw as dn, toValue as be, normalizeClass as ut, normalizeStyle as hr, cloneVNode as re, vModelDynamic as pr, vShow as mr, withDirectives as hn, h as q, toDisplayString as pn, withModifiers as gr, resolveDynamicComponent as yr, normalizeProps as vr, TransitionGroup as wr, createTextVNode as _r, unref as z, toRef as me, readonly as Rt, customRef as ye, ref as W, onBeforeUnmount as Er, onMounted as mn, nextTick as Se, getCurrentScope as br, onScopeDispose as Sr, getCurrentInstance as He, watch as K, isRef as Ot, shallowRef as ie, watchEffect as Nt, computed as j, inject as ae, shallowReactive as kr, defineComponent as X, reactive as Rr, provide as U, onUnmounted as Or, onErrorCaptured as Nr, openBlock as fe, createElementBlock as Ee, createElementVNode as gn, createVNode as Pr, createCommentVNode as ft, mergeProps as de, createBlock as yn, Teleport as Vr, renderSlot as Cr, useAttrs as Ar, Fragment as $r, useSlots as Ke, KeepAlive as xr } from "vue";
let vn;
function Tr(e) {
  vn = e;
}
function dt() {
  return vn;
}
function We() {
  const { queryPath: e, pathParams: t, queryParams: n } = dt();
  return {
    path: e,
    ...t === void 0 ? {} : { params: t },
    ...n === void 0 ? {} : { queryParams: n }
  };
}
function jt(e, t) {
  Object.entries(e).forEach(([n, r]) => t(r, n));
}
function Ge(e, t) {
  return wn(e, {
    valueFn: t
  });
}
function wn(e, t) {
  const { valueFn: n, keyFn: r } = t;
  return Object.fromEntries(
    Object.entries(e).map(([s, o], i) => [
      r ? r(s, o) : s,
      n(o, s, i)
    ])
  );
}
function Ir(e, t, n) {
  if (Array.isArray(t)) {
    const [s, ...o] = t;
    switch (s) {
      case "!":
        return !e;
      case "+":
        return e + o[0];
      case "~+":
        return o[0] + e;
    }
  }
  const r = Dr(t);
  return e[r];
}
function Dr(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      throw new Error("No bindable function provided");
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function jr(e, t, n) {
  return t.reduce(
    (r, s) => Ir(r, s),
    e
  );
}
function Mr(e, t) {
  return t ? t.reduce((n, r) => n[r], e) : e;
}
const Br = window.structuredClone || ((e) => JSON.parse(JSON.stringify(e)));
function _n(e) {
  if (typeof e == "function")
    return e;
  try {
    return Br(dn(be(e)));
  } catch {
    return e;
  }
}
function Lr(e, t) {
  const n = e.classes;
  if (!n)
    return null;
  if (typeof n == "string")
    return ut(n);
  const { str: r, map: s, bind: o } = n, { bindingGetter: i } = t, a = [];
  return r && a.push(r), s && a.push(
    Ge(
      s,
      (c) => i.getValue(c)
    )
  ), o && a.push(...o.map((c) => i.getValue(c))), ut(a);
}
function Fr(e, t) {
  const n = [], { bindingGetter: r } = t, { dStyle: s = {}, sStyle: o = [] } = e;
  n.push(
    Ge(
      s || {},
      (c) => r.getValue(c)
    )
  ), n.push(
    ...o.map((c) => r.getValue(c))
  );
  const i = hr([e.style || {}, n]);
  return {
    hasStyle: i && Object.keys(i).length > 0,
    styles: i
  };
}
function Wr(e, t, n) {
  const r = [], { dir: s = [] } = t, { bindingGetter: o } = n;
  return s.forEach((i) => {
    const { sys: a, name: c, arg: h, value: u, mf: l } = i;
    if (c === "vmodel") {
      const f = o.getRef(u);
      if (e = re(e, {
        [`onUpdate:${h}`]: (d) => {
          f.value = d;
        }
      }), a === 1) {
        const d = l ? Object.fromEntries(l.map((p) => [p, !0])) : {};
        r.push([pr, f.value, void 0, d]);
      } else
        e = re(e, {
          [h]: f.value
        });
    } else if (c === "vshow") {
      const f = o.getValue(u);
      r.push([mr, f]);
    } else
      console.warn(`Directive ${c} is not supported yet`);
  }), r.length > 0 ? hn(e, r) : e;
}
function Te(e, t) {
  return q(or, {
    config: e,
    vforSetting: t == null ? void 0 : t.vforSetting,
    slotSetting: t == null ? void 0 : t.slotSetting
  });
}
function Ur(e, t, n) {
  if (!e.slots)
    return;
  const r = e.slots ?? {};
  if (t) {
    const a = r[":"];
    if (!a)
      return;
    const { scope: c, items: h } = a;
    return c ? Te(c, {
      buildOptions: n
    }) : h == null ? void 0 : h.map((u) => ve(u, n));
  }
  return wn(r, { keyFn: (a) => a === ":" ? "default" : a, valueFn: (a) => {
    const { usePropId: c, scope: h } = a;
    return h ? (u) => Te(h, {
      buildOptions: n,
      slotSetting: c ? {
        id: c,
        value: u
      } : void 0
    }) : () => {
      var u;
      return (u = a.items) == null ? void 0 : u.map((l) => ve(l, n));
    };
  } });
}
function G(e, t) {
  t = t || {};
  const n = [...Object.keys(t), "__Vue"], r = [...Object.values(t), dr];
  try {
    return new Function(...n, `return (${e})`)(...r);
  } catch (s) {
    throw new Error(s + " in function code: " + e);
  }
}
function Ue(e, t = !0) {
  if (!(typeof e != "object" || e === null)) {
    if (Array.isArray(e)) {
      t && e.forEach((n) => Ue(n, !0));
      return;
    }
    for (const [n, r] of Object.entries(e))
      if (n.startsWith(":"))
        try {
          e[n.slice(1)] = new Function(`return (${r})`)(), delete e[n];
        } catch (s) {
          console.error(
            `Error while converting ${n} attribute to function:`,
            s
          );
        }
      else
        t && Ue(r, !0);
  }
}
function zr(e, t) {
  const n = e.startsWith(":");
  return n && (e = e.slice(1), t = G(t)), { name: e, value: t, isFunc: n };
}
class Hr {
  toString() {
    return "";
  }
}
const Ie = new Hr();
function ke(e) {
  return dn(e) === Ie;
}
function Kr(e, t) {
  var o;
  const n = {}, r = e.props ?? {}, { bindingGetter: s } = t;
  return Ue(r), jt(e.bProps || {}, (i, a) => {
    const c = s.getValue(i);
    ke(c) || (Ue(c), n[a] = Gr(c, a));
  }), (o = e.proxyProps) == null || o.forEach((i) => {
    const a = s.getValue(i);
    typeof a == "object" && jt(a, (c, h) => {
      const { name: u, value: l } = zr(h, c);
      n[u] = l;
    });
  }), { ...r, ...n };
}
function Gr(e, t) {
  return t === "innerText" ? pn(e) : e;
}
function Pt(e) {
  return e !== null && typeof e == "object" && e.nodeType === 1 && typeof e.nodeName == "string";
}
class qr {
  async eventSend(t, n) {
    const { fType: r, hKey: s, key: o } = t, i = dt().webServerInfo, a = o !== void 0 ? { key: o } : {}, c = r === "sync" ? i.event_url : i.event_async_url;
    let h = {};
    const u = await fetch(c, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        bind: n,
        hKey: s,
        ...a,
        page: We(),
        ...h
      })
    });
    if (!u.ok)
      throw new Error(`HTTP error! status: ${u.status}`);
    return await u.json();
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, s = dt().webServerInfo, o = n === "sync" ? s.watch_url : s.watch_async_url, i = t.getServerInputs(), a = {
      key: r,
      input: i,
      page: We()
    };
    return await (await fetch(o, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(a)
    })).json();
  }
}
class Jr {
  async eventSend(t, n) {
    const { fType: r, hKey: s, key: o } = t, i = o !== void 0 ? { key: o } : {};
    let a = {};
    const c = {
      bind: n,
      fType: r,
      hKey: s,
      ...i,
      page: We(),
      ...a
    };
    return await window.pywebview.api.event_call(c);
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, s = t.getServerInputs(), o = {
      key: r,
      input: s,
      fType: n,
      page: We()
    };
    return await window.pywebview.api.watch_call(o);
  }
}
let ht;
function Qr(e) {
  switch (e) {
    case "web":
      ht = new qr();
      break;
    case "webview":
      ht = new Jr();
      break;
  }
}
function En() {
  return ht;
}
function bn(e) {
  const { config: t, bindingGetter: n } = e;
  if (!t)
    return {
      run: () => {
      },
      tryReset: () => {
      }
    };
  const r = t.map((i) => {
    const [a, c, h] = i, u = n.getRef(a);
    function l(f, d) {
      const { type: p, value: y } = d;
      if (p === "const") {
        f.value = y;
        return;
      }
      if (p === "action") {
        const v = Yr(y, n);
        f.value = v;
        return;
      }
    }
    return {
      run: () => l(u, c),
      reset: () => l(u, h)
    };
  });
  return {
    run: () => {
      r.forEach((i) => i.run());
    },
    tryReset: () => {
      r.forEach((i) => i.reset());
    }
  };
}
function Yr(e, t) {
  const { inputs: n = [], code: r } = e, s = G(r), o = n.map((i) => t.getValue(i));
  return s(...o);
}
function Mt(e) {
  return e == null;
}
const ue = {
  Ref: 0,
  EventContext: 1,
  Data: 2,
  JsFn: 3,
  ElementRef: 4
}, Bt = {
  const: "c",
  ref: "r",
  range: "n"
}, Ae = {
  Ref: 0,
  RouterAction: 1,
  ElementRefAction: 2,
  JsCode: 3
};
function qe(e, t, n) {
  if (Mt(t) || Mt(e.values))
    return;
  t = t;
  const r = e.values, s = e.types ?? Array.from({ length: t.length }).fill(0);
  t.forEach((o, i) => {
    const a = s[i];
    if (a === 1)
      return;
    if (o.type === Ae.Ref) {
      if (a === 2) {
        r[i].forEach(([u, l]) => {
          const f = o.ref, d = {
            ...f,
            path: [...f.path ?? [], ...u]
          };
          n.updateValue(d, l);
        });
        return;
      }
      n.updateValue(o.ref, r[i]);
      return;
    }
    if (o.type === Ae.RouterAction) {
      const h = r[i], u = n.getRouter(o.ref)[h.fn];
      u(...h.args);
      return;
    }
    if (o.type === Ae.ElementRefAction) {
      const h = o.ref, u = n.getRef(h).value, l = r[i], { method: f, args: d = [] } = l;
      u[f](...d);
      return;
    }
    if (o.type === Ae.JsCode) {
      const h = r[i];
      if (!h)
        return;
      const u = G(h);
      Promise.resolve(u());
      return;
    }
    const c = n.getRef(o.ref);
    c.value = r[i];
  });
}
class Xr extends Map {
  constructor(t) {
    super(), this.factory = t;
  }
  getOrDefault(t) {
    if (!this.has(t)) {
      const n = this.factory();
      return this.set(t, n), n;
    }
    return super.get(t);
  }
}
function Sn(e) {
  return new Xr(e);
}
const Zr = "on:mounted";
function es(e, t, n) {
  if (!t)
    return e;
  const r = Sn(() => []);
  t.map(([a, c]) => {
    const h = ts(c, n), { eventName: u, handleEvent: l } = is({
      eventName: a,
      info: c,
      handleEvent: h
    });
    r.getOrDefault(u).push(l);
  });
  const s = {};
  for (const [a, c] of r) {
    const h = c.length === 1 ? c[0] : (...u) => c.forEach((l) => Promise.resolve().then(() => l(...u)));
    s[a] = h;
  }
  const { [Zr]: o, ...i } = s;
  return e = re(e, i), o && (e = hn(e, [
    [
      {
        mounted(a) {
          o(a);
        }
      }
    ]
  ])), e;
}
function ts(e, t) {
  if (e.type === "web") {
    const n = ns(e, t);
    return rs(e, n, t);
  } else {
    if (e.type === "vue")
      return os(e, t);
    if (e.type === "js")
      return ss(e, t);
  }
  throw new Error(`unknown event type ${e}`);
}
function ns(e, t) {
  const { inputs: n = [] } = e, { bindingGetter: r } = t;
  return (...s) => n.map(({ value: o, type: i }) => {
    if (i === ue.EventContext) {
      const { path: a } = o;
      if (a.startsWith(":")) {
        const c = a.slice(1);
        return G(c)(...s);
      }
      return Mr(s[0], a.split("."));
    }
    return i === ue.Ref ? r.getValue(o) : o;
  });
}
function rs(e, t, n) {
  const { bindingGetter: r } = n;
  async function s(...o) {
    const i = t(...o), a = bn({
      config: e.preSetup,
      bindingGetter: r
    });
    try {
      a.run();
      const c = await En().eventSend(e, i);
      if (!c)
        return;
      qe(c, e.sets, r);
    } finally {
      a.tryReset();
    }
  }
  return s;
}
function ss(e, t) {
  const { sets: n, code: r, inputs: s = [] } = e, { bindingGetter: o } = t, i = G(r);
  function a(...c) {
    const h = s.map(({ value: l, type: f }) => {
      if (f === ue.EventContext) {
        if (l.path.startsWith(":")) {
          const d = l.path.slice(1);
          return G(d)(...c);
        }
        return jr(c[0], l.path.split("."));
      }
      if (f === ue.Ref)
        return o.getValue(l);
      if (f === ue.Data)
        return l;
      if (f === ue.ElementRef) {
        const d = o.getValue(l);
        return d && (Pt(d) ? d : d.$el);
      }
      if (f === ue.JsFn)
        return o.getValue(l);
      throw new Error(`unknown input type ${f}`);
    }), u = i(...h);
    if (n !== void 0) {
      const f = n.length === 1 ? [u] : u, d = f.map((p) => p === void 0 ? 1 : 0);
      qe(
        { values: f, types: d },
        n,
        o
      );
    }
  }
  return a;
}
function os(e, t) {
  const { code: n, inputs: r = {} } = e, { bindingGetter: s } = t, o = Ge(
    r,
    (c) => c.type !== ue.Data ? s.getRef(c.value) : c.value
  ), i = G(n, o);
  function a(...c) {
    i(...c);
  }
  return a;
}
function is(e) {
  const { eventName: t, info: n, handleEvent: r } = e;
  if (n.type === "vue")
    return {
      eventName: t,
      handleEvent: r
    };
  const { modifier: s = [] } = n;
  if (s.length === 0)
    return {
      eventName: t,
      handleEvent: r
    };
  const o = ["passive", "capture", "once"], i = [], a = [];
  for (const u of s)
    o.includes(u) ? i.push(u[0].toUpperCase() + u.slice(1)) : a.push(u);
  const c = i.length > 0 ? t + i.join("") : t, h = a.length > 0 ? gr(r, a) : r;
  return {
    eventName: c,
    handleEvent: h
  };
}
function as(e, t, n) {
  const { eRef: r } = t, { bindingGetter: s } = n;
  return r ? re(e, { ref: s.getRef(r) }) : e;
}
function cs(e, t) {
  const n = ls(e, t), r = yr(n), s = typeof r == "string", o = Lr(e, t), { styles: i, hasStyle: a } = Fr(e, t), c = Ur(e, s, t), h = Kr(e, t), u = vr(h) || {};
  a && (u.style = i), o && (u.class = o);
  let l = q(r, { ...u }, c);
  return l = es(l, e.events, t), l = as(l, e, t), Wr(l, e, t);
}
function ls(e, t) {
  const { tag: n } = e;
  return typeof n == "string" ? n : t.bindingGetter.getValue(n);
}
function us(e, t) {
  var l, f, d;
  const { fkey: n, tsGroup: r = {}, scope: s } = e, o = !!((l = e.used) != null && l.item), i = !!((f = e.used) != null && f.index), a = !!((d = e.used) != null && d.key), c = [], { sourceInfo: h, iterSource: u } = fs(e, t);
  for (const [p, y, v] of u) {
    const w = {};
    o && (w.item = {
      value: y,
      id: e.used.item
    }, h && (w.item.sourceInfo = {
      source: h.source,
      type: h.type,
      index: p,
      key: v
    })), i && (w.index = {
      value: p,
      id: e.used.index
    }), a && (w.key = {
      value: v,
      id: e.used.key
    });
    let g = Te(s, {
      buildOptions: t,
      vforSetting: w
    });
    const _ = ps(n, { value: y, index: p });
    g = re(g, { key: _ }), c.push(g);
  }
  return r && Object.keys(r).length > 0 ? q(wr, r, {
    default: () => c
  }) : c;
}
function fs(e, t) {
  const { type: n, value: r } = e.array, { bindingGetter: s } = t, o = n === Bt.range, i = n === Bt.const || o && typeof r == "number";
  if (o) {
    const { start: a = 0, end: c, step: h = 1 } = r, u = typeof a == "number" ? a : s.getValue(a), l = typeof c == "number" ? c : s.getValue(c), f = typeof h == "number" ? h : s.getValue(h);
    return {
      sourceInfo: void 0,
      iterSource: Lt(u, l, f)
    };
  }
  {
    const a = i ? r : s.getValue(e.array.value);
    if (typeof a == "number")
      return {
        sourceInfo: void 0,
        iterSource: Lt(0, a, 1)
      };
    if (Array.isArray(a)) {
      function* c() {
        for (let h = 0; h < a.length; h++)
          yield [h, a[h]];
      }
      return {
        sourceInfo: i ? void 0 : {
          source: s.getRef(e.array.value),
          type: "array"
        },
        iterSource: c()
      };
    }
    if (typeof a == "object" && a !== null) {
      function* c() {
        let h = 0;
        for (const [u, l] of Object.entries(a))
          yield [h++, l, u];
      }
      return {
        sourceInfo: i ? void 0 : {
          source: s.getRef(e.array.value),
          type: "object"
        },
        iterSource: c()
      };
    }
    if (ke(a))
      return a;
  }
  throw new Error("Not implemented yet");
}
function* Lt(e, t, n = 1) {
  if (n === 0)
    throw new Error("Step cannot be 0");
  let r = 0;
  if (n > 0)
    for (let s = e; s < t; s += n)
      yield [r++, s];
  else
    for (let s = e; s > t; s += n)
      yield [r++, s];
}
const ds = (e) => e, hs = (e, t) => t;
function ps(e, t) {
  const { value: n, index: r } = t, s = ms(e ?? "index");
  return typeof s == "function" ? s(n, r) : e === "item" ? ds(n) : hs(n, r);
}
function ms(e) {
  const t = e.trim();
  if (t === "item" || t === "index")
    return;
  if (e.startsWith(":")) {
    e = e.slice(1);
    try {
      return G(e);
    } catch (r) {
      throw new Error(r + " in function code: " + e);
    }
  }
  const n = `(item, index) => { return ${t}; }`;
  try {
    return G(n);
  } catch (r) {
    throw new Error(r + " in function code: " + n);
  }
}
function gs(e, t) {
  const { on: n, items: r } = e;
  return (typeof n == "boolean" ? n : t.bindingGetter.getValue(n)) ? r == null ? void 0 : r.map((o) => ve(o, t)) : void 0;
}
function ys(e, t) {
  const { cond: n, const: r = 0, cases: s, default: o } = e, a = r === 1 ? n : t.bindingGetter.getValue(n), c = [];
  let h = !1;
  for (const { value: u, items: l = [] } of s || [])
    if (u === a) {
      c.push(...l.map((f) => ve(f, t))), h = !0;
      break;
    }
  return !h && o && o.items && c.push(
    ...o.items.map((u) => ve(u, t))
  ), c;
}
function vs(e, t) {
  const { value: n, r = 0 } = e, s = r === 1 ? t.bindingGetter.getValue(n) : n;
  return _r(s);
}
const ws = /* @__PURE__ */ new Map(
  [
    ["vfor", us],
    ["vif", gs],
    ["match", ys],
    ["content", vs]
  ]
);
function _s(e, t) {
  const n = ws.get(e.tag);
  if (!n)
    throw new Error(`Unknown logic component ${e.tag}`);
  return n(e, t);
}
function ve(e, t) {
  const { type: n } = e;
  if (n === "cp")
    return cs(e, t);
  if (n === "logic")
    return _s(e, t);
  if (n === "scope")
    return Te(e, {
      buildOptions: t
    });
  throw new Error(`Unknown component type ${n}`);
}
function kn(e) {
  return "r" in e;
}
function Vt(e) {
  return br() ? (Sr(e), !0) : !1;
}
function te(e) {
  return typeof e == "function" ? e() : z(e);
}
const Rn = typeof window < "u" && typeof document < "u";
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const Es = (e) => e != null, bs = Object.prototype.toString, Ss = (e) => bs.call(e) === "[object Object]", De = () => {
};
function ks(e, t) {
  function n(...r) {
    return new Promise((s, o) => {
      Promise.resolve(e(() => t.apply(this, r), { fn: t, thisArg: this, args: r })).then(s).catch(o);
    });
  }
  return n;
}
const On = (e) => e();
function Rs(e = On) {
  const t = W(!0);
  function n() {
    t.value = !1;
  }
  function r() {
    t.value = !0;
  }
  const s = (...o) => {
    t.value && e(...o);
  };
  return { isActive: Rt(t), pause: n, resume: r, eventFilter: s };
}
function pt(e, t = !1, n = "Timeout") {
  return new Promise((r, s) => {
    setTimeout(t ? () => s(n) : r, e);
  });
}
function Nn(e) {
  return He();
}
function Pn(...e) {
  if (e.length !== 1)
    return me(...e);
  const t = e[0];
  return typeof t == "function" ? Rt(ye(() => ({ get: t, set: De }))) : W(t);
}
function Os(e, t, n = {}) {
  const {
    eventFilter: r = On,
    ...s
  } = n;
  return K(
    e,
    ks(
      r,
      t
    ),
    s
  );
}
function Ns(e, t, n = {}) {
  const {
    eventFilter: r,
    ...s
  } = n, { eventFilter: o, pause: i, resume: a, isActive: c } = Rs(r);
  return { stop: Os(
    e,
    t,
    {
      ...s,
      eventFilter: o
    }
  ), pause: i, resume: a, isActive: c };
}
function Ps(e, t) {
  Nn() && Er(e, t);
}
function Vn(e, t = !0, n) {
  Nn() ? mn(e, n) : t ? e() : Se(e);
}
function mt(e, t = !1) {
  function n(l, { flush: f = "sync", deep: d = !1, timeout: p, throwOnTimeout: y } = {}) {
    let v = null;
    const g = [new Promise((_) => {
      v = K(
        e,
        (S) => {
          l(S) !== t && (v ? v() : Se(() => v == null ? void 0 : v()), _(S));
        },
        {
          flush: f,
          deep: d,
          immediate: !0
        }
      );
    })];
    return p != null && g.push(
      pt(p, y).then(() => te(e)).finally(() => v == null ? void 0 : v())
    ), Promise.race(g);
  }
  function r(l, f) {
    if (!Ot(l))
      return n((S) => S === l, f);
    const { flush: d = "sync", deep: p = !1, timeout: y, throwOnTimeout: v } = f ?? {};
    let w = null;
    const _ = [new Promise((S) => {
      w = K(
        [e, l],
        ([C, x]) => {
          t !== (C === x) && (w ? w() : Se(() => w == null ? void 0 : w()), S(C));
        },
        {
          flush: d,
          deep: p,
          immediate: !0
        }
      );
    })];
    return y != null && _.push(
      pt(y, v).then(() => te(e)).finally(() => (w == null || w(), te(e)))
    ), Promise.race(_);
  }
  function s(l) {
    return n((f) => !!f, l);
  }
  function o(l) {
    return r(null, l);
  }
  function i(l) {
    return r(void 0, l);
  }
  function a(l) {
    return n(Number.isNaN, l);
  }
  function c(l, f) {
    return n((d) => {
      const p = Array.from(d);
      return p.includes(l) || p.includes(te(l));
    }, f);
  }
  function h(l) {
    return u(1, l);
  }
  function u(l = 1, f) {
    let d = -1;
    return n(() => (d += 1, d >= l), f);
  }
  return Array.isArray(te(e)) ? {
    toMatch: n,
    toContains: c,
    changed: h,
    changedTimes: u,
    get not() {
      return mt(e, !t);
    }
  } : {
    toMatch: n,
    toBe: r,
    toBeTruthy: s,
    toBeNull: o,
    toBeNaN: a,
    toBeUndefined: i,
    changed: h,
    changedTimes: u,
    get not() {
      return mt(e, !t);
    }
  };
}
function Vs(e) {
  return mt(e);
}
function Cs(e, t, n) {
  let r;
  Ot(n) ? r = {
    evaluating: n
  } : r = n || {};
  const {
    lazy: s = !1,
    evaluating: o = void 0,
    shallow: i = !0,
    onError: a = De
  } = r, c = W(!s), h = i ? ie(t) : W(t);
  let u = 0;
  return Nt(async (l) => {
    if (!c.value)
      return;
    u++;
    const f = u;
    let d = !1;
    o && Promise.resolve().then(() => {
      o.value = !0;
    });
    try {
      const p = await e((y) => {
        l(() => {
          o && (o.value = !1), d || y();
        });
      });
      f === u && (h.value = p);
    } catch (p) {
      a(p);
    } finally {
      o && f === u && (o.value = !1), d = !0;
    }
  }), s ? j(() => (c.value = !0, h.value)) : h;
}
const Re = Rn ? window : void 0, As = Rn ? window.document : void 0;
function Ct(e) {
  var t;
  const n = te(e);
  return (t = n == null ? void 0 : n.$el) != null ? t : n;
}
function Ft(...e) {
  let t, n, r, s;
  if (typeof e[0] == "string" || Array.isArray(e[0]) ? ([n, r, s] = e, t = Re) : [t, n, r, s] = e, !t)
    return De;
  Array.isArray(n) || (n = [n]), Array.isArray(r) || (r = [r]);
  const o = [], i = () => {
    o.forEach((u) => u()), o.length = 0;
  }, a = (u, l, f, d) => (u.addEventListener(l, f, d), () => u.removeEventListener(l, f, d)), c = K(
    () => [Ct(t), te(s)],
    ([u, l]) => {
      if (i(), !u)
        return;
      const f = Ss(l) ? { ...l } : l;
      o.push(
        ...n.flatMap((d) => r.map((p) => a(u, d, p, f)))
      );
    },
    { immediate: !0, flush: "post" }
  ), h = () => {
    c(), i();
  };
  return Vt(h), h;
}
function $s() {
  const e = W(!1), t = He();
  return t && mn(() => {
    e.value = !0;
  }, t), e;
}
function Cn(e) {
  const t = $s();
  return j(() => (t.value, !!e()));
}
function xs(e, t, n = {}) {
  const { window: r = Re, ...s } = n;
  let o;
  const i = Cn(() => r && "MutationObserver" in r), a = () => {
    o && (o.disconnect(), o = void 0);
  }, c = j(() => {
    const f = te(e), d = (Array.isArray(f) ? f : [f]).map(Ct).filter(Es);
    return new Set(d);
  }), h = K(
    () => c.value,
    (f) => {
      a(), i.value && f.size && (o = new MutationObserver(t), f.forEach((d) => o.observe(d, s)));
    },
    { immediate: !0, flush: "post" }
  ), u = () => o == null ? void 0 : o.takeRecords(), l = () => {
    h(), a();
  };
  return Vt(l), {
    isSupported: i,
    stop: l,
    takeRecords: u
  };
}
function Ts(e, t, n) {
  const {
    immediate: r = !0,
    delay: s = 0,
    onError: o = De,
    onSuccess: i = De,
    resetOnExecute: a = !0,
    shallow: c = !0,
    throwError: h
  } = {}, u = c ? ie(t) : W(t), l = W(!1), f = W(!1), d = ie(void 0);
  async function p(w = 0, ...g) {
    a && (u.value = t), d.value = void 0, l.value = !1, f.value = !0, w > 0 && await pt(w);
    const _ = typeof e == "function" ? e(...g) : e;
    try {
      const S = await _;
      u.value = S, l.value = !0, i(S);
    } catch (S) {
      if (d.value = S, o(S), h)
        throw S;
    } finally {
      f.value = !1;
    }
    return u.value;
  }
  r && p(s);
  const y = {
    state: u,
    isReady: l,
    isLoading: f,
    error: d,
    execute: p
  };
  function v() {
    return new Promise((w, g) => {
      Vs(f).toBe(!1).then(() => w(y)).catch(g);
    });
  }
  return {
    ...y,
    then(w, g) {
      return v().then(w, g);
    }
  };
}
function Is(e, t = {}) {
  const { window: n = Re } = t, r = Cn(() => n && "matchMedia" in n && typeof n.matchMedia == "function");
  let s;
  const o = W(!1), i = (h) => {
    o.value = h.matches;
  }, a = () => {
    s && ("removeEventListener" in s ? s.removeEventListener("change", i) : s.removeListener(i));
  }, c = Nt(() => {
    r.value && (a(), s = n.matchMedia(te(e)), "addEventListener" in s ? s.addEventListener("change", i) : s.addListener(i), o.value = s.matches);
  });
  return Vt(() => {
    c(), a(), s = void 0;
  }), o;
}
const Be = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, Le = "__vueuse_ssr_handlers__", Ds = /* @__PURE__ */ js();
function js() {
  return Le in Be || (Be[Le] = Be[Le] || {}), Be[Le];
}
function An(e, t) {
  return Ds[e] || t;
}
function Ms(e) {
  return Is("(prefers-color-scheme: dark)", e);
}
function Bs(e) {
  return e == null ? "any" : e instanceof Set ? "set" : e instanceof Map ? "map" : e instanceof Date ? "date" : typeof e == "boolean" ? "boolean" : typeof e == "string" ? "string" : typeof e == "object" ? "object" : Number.isNaN(e) ? "any" : "number";
}
const Ls = {
  boolean: {
    read: (e) => e === "true",
    write: (e) => String(e)
  },
  object: {
    read: (e) => JSON.parse(e),
    write: (e) => JSON.stringify(e)
  },
  number: {
    read: (e) => Number.parseFloat(e),
    write: (e) => String(e)
  },
  any: {
    read: (e) => e,
    write: (e) => String(e)
  },
  string: {
    read: (e) => e,
    write: (e) => String(e)
  },
  map: {
    read: (e) => new Map(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e.entries()))
  },
  set: {
    read: (e) => new Set(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e))
  },
  date: {
    read: (e) => new Date(e),
    write: (e) => e.toISOString()
  }
}, Wt = "vueuse-storage";
function gt(e, t, n, r = {}) {
  var s;
  const {
    flush: o = "pre",
    deep: i = !0,
    listenToStorageChanges: a = !0,
    writeDefaults: c = !0,
    mergeDefaults: h = !1,
    shallow: u,
    window: l = Re,
    eventFilter: f,
    onError: d = (P) => {
      console.error(P);
    },
    initOnMounted: p
  } = r, y = (u ? ie : W)(typeof t == "function" ? t() : t);
  if (!n)
    try {
      n = An("getDefaultStorage", () => {
        var P;
        return (P = Re) == null ? void 0 : P.localStorage;
      })();
    } catch (P) {
      d(P);
    }
  if (!n)
    return y;
  const v = te(t), w = Bs(v), g = (s = r.serializer) != null ? s : Ls[w], { pause: _, resume: S } = Ns(
    y,
    () => x(y.value),
    { flush: o, deep: i, eventFilter: f }
  );
  l && a && Vn(() => {
    n instanceof Storage ? Ft(l, "storage", Y) : Ft(l, Wt, Z), p && Y();
  }), p || Y();
  function C(P, T) {
    if (l) {
      const B = {
        key: e,
        oldValue: P,
        newValue: T,
        storageArea: n
      };
      l.dispatchEvent(n instanceof Storage ? new StorageEvent("storage", B) : new CustomEvent(Wt, {
        detail: B
      }));
    }
  }
  function x(P) {
    try {
      const T = n.getItem(e);
      if (P == null)
        C(T, null), n.removeItem(e);
      else {
        const B = g.write(P);
        T !== B && (n.setItem(e, B), C(T, B));
      }
    } catch (T) {
      d(T);
    }
  }
  function I(P) {
    const T = P ? P.newValue : n.getItem(e);
    if (T == null)
      return c && v != null && n.setItem(e, g.write(v)), v;
    if (!P && h) {
      const B = g.read(T);
      return typeof h == "function" ? h(B, v) : w === "object" && !Array.isArray(B) ? { ...v, ...B } : B;
    } else return typeof T != "string" ? T : g.read(T);
  }
  function Y(P) {
    if (!(P && P.storageArea !== n)) {
      if (P && P.key == null) {
        y.value = v;
        return;
      }
      if (!(P && P.key !== e)) {
        _();
        try {
          (P == null ? void 0 : P.newValue) !== g.write(y.value) && (y.value = I(P));
        } catch (T) {
          d(T);
        } finally {
          P ? Se(S) : S();
        }
      }
    }
  }
  function Z(P) {
    Y(P.detail);
  }
  return y;
}
const Fs = "*,*::before,*::after{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}";
function Ws(e = {}) {
  const {
    selector: t = "html",
    attribute: n = "class",
    initialValue: r = "auto",
    window: s = Re,
    storage: o,
    storageKey: i = "vueuse-color-scheme",
    listenToStorageChanges: a = !0,
    storageRef: c,
    emitAuto: h,
    disableTransition: u = !0
  } = e, l = {
    auto: "",
    light: "light",
    dark: "dark",
    ...e.modes || {}
  }, f = Ms({ window: s }), d = j(() => f.value ? "dark" : "light"), p = c || (i == null ? Pn(r) : gt(i, r, o, { window: s, listenToStorageChanges: a })), y = j(() => p.value === "auto" ? d.value : p.value), v = An(
    "updateHTMLAttrs",
    (S, C, x) => {
      const I = typeof S == "string" ? s == null ? void 0 : s.document.querySelector(S) : Ct(S);
      if (!I)
        return;
      const Y = /* @__PURE__ */ new Set(), Z = /* @__PURE__ */ new Set();
      let P = null;
      if (C === "class") {
        const B = x.split(/\s/g);
        Object.values(l).flatMap((ee) => (ee || "").split(/\s/g)).filter(Boolean).forEach((ee) => {
          B.includes(ee) ? Y.add(ee) : Z.add(ee);
        });
      } else
        P = { key: C, value: x };
      if (Y.size === 0 && Z.size === 0 && P === null)
        return;
      let T;
      u && (T = s.document.createElement("style"), T.appendChild(document.createTextNode(Fs)), s.document.head.appendChild(T));
      for (const B of Y)
        I.classList.add(B);
      for (const B of Z)
        I.classList.remove(B);
      P && I.setAttribute(P.key, P.value), u && (s.getComputedStyle(T).opacity, document.head.removeChild(T));
    }
  );
  function w(S) {
    var C;
    v(t, n, (C = l[S]) != null ? C : S);
  }
  function g(S) {
    e.onChanged ? e.onChanged(S, w) : w(S);
  }
  K(y, g, { flush: "post", immediate: !0 }), Vn(() => g(y.value));
  const _ = j({
    get() {
      return h ? p.value : y.value;
    },
    set(S) {
      p.value = S;
    }
  });
  return Object.assign(_, { store: p, system: d, state: y });
}
function Us(e = {}) {
  const {
    valueDark: t = "dark",
    valueLight: n = ""
  } = e, r = Ws({
    ...e,
    onChanged: (i, a) => {
      var c;
      e.onChanged ? (c = e.onChanged) == null || c.call(e, i === "dark", a, i) : a(i);
    },
    modes: {
      dark: t,
      light: n
    }
  }), s = j(() => r.system.value);
  return j({
    get() {
      return r.value === "dark";
    },
    set(i) {
      const a = i ? "dark" : "light";
      s.value === a ? r.value = "auto" : r.value = a;
    }
  });
}
function zs(e = null, t = {}) {
  var n, r, s;
  const {
    document: o = As,
    restoreOnUnmount: i = (l) => l
  } = t, a = (n = o == null ? void 0 : o.title) != null ? n : "", c = Pn((r = e ?? (o == null ? void 0 : o.title)) != null ? r : null), h = e && typeof e == "function";
  function u(l) {
    if (!("titleTemplate" in t))
      return l;
    const f = t.titleTemplate || "%s";
    return typeof f == "function" ? f(l) : te(f).replace(/%s/g, l);
  }
  return K(
    c,
    (l, f) => {
      l !== f && o && (o.title = u(typeof l == "string" ? l : ""));
    },
    { immediate: !0 }
  ), t.observe && !t.titleTemplate && o && !h && xs(
    (s = o.head) == null ? void 0 : s.querySelector("title"),
    () => {
      o && o.title !== c.value && (c.value = u(o.title));
    },
    { childList: !0 }
  ), Ps(() => {
    if (i) {
      const l = i(a, c.value || "");
      l != null && o && (o.title = l);
    }
  }), c;
}
function $n(e) {
  return e.constructor.name === "AsyncFunction";
}
function xn(e, t, n) {
  const [r] = t;
  switch (r) {
    case "bind":
      return e[ne(t, n)];
    case "!":
      return !e;
    case "+":
      return e + ne(t, n);
    case "~+":
      return ne(t, n) + e;
    case "<":
      return e < ne(t, n);
    case "<=":
      return e <= ne(t, n);
    case ">":
      return e > ne(t, n);
    case ">=":
      return e >= ne(t, n);
    case "==":
      return e == ne(t, n);
    case "!=":
      return e != ne(t, n);
    case "len":
      return e.length;
    default:
      throw new Error(`Invalid flag ${r} in array at ${t}`);
  }
}
function ne(e, t) {
  const [n, r, s] = e, o = () => s && s[0] ? t(r[0]) : r[0];
  switch (n) {
    case "bind":
      return o();
    case "+":
      return o();
    case "~+":
      return o();
    case "<":
      return o();
    case "<=":
      return o();
    case ">":
      return o();
    case ">=":
      return o();
    case "==":
      return o();
    case "!=":
      return o();
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function Hs(e, t, n) {
  return In(t).reduce(
    (r, s) => xn(r, s, n),
    e
  );
}
function Tn(e, t, n, r) {
  In(t).reduce((s, o, i) => {
    if (i === t.length - 1)
      s[ne(o, r)] = n;
    else
      return xn(s, o, r);
  }, e);
}
function In(e) {
  return Ks(e) ? e.map((t) => ["bind", [t]]) : e;
}
function Ks(e) {
  return !Array.isArray(e[0]);
}
function Gs(e, t, n) {
  const { paths: r, getBindableValueFn: s } = t, { paths: o, getBindableValueFn: i } = t;
  return r === void 0 || r.length === 0 ? e : ye(() => ({
    get() {
      try {
        return Hs(
          be(e),
          r,
          s
        );
      } catch {
        return;
      }
    },
    set(a) {
      Tn(
        be(e),
        o || r,
        a,
        i
      );
    }
  }));
}
function Ut(e, t) {
  return !ke(e) && JSON.stringify(t) === JSON.stringify(e);
}
function At(e) {
  if (Ot(e)) {
    const t = e;
    return ye(() => ({
      get() {
        return be(t);
      },
      set(n) {
        const r = be(t);
        Ut(r, n) || (t.value = n);
      }
    }));
  }
  return ye((t, n) => ({
    get() {
      return t(), e;
    },
    set(r) {
      Ut(e, r) || (e = r, n());
    }
  }));
}
function qs(e) {
  const { type: t, key: n, value: r } = e.args;
  return t === "local" ? gt(n, r) : gt(n, r, sessionStorage);
}
const Js = "insta-color-scheme";
function Qs(e) {
  return Us({
    storageKey: Js,
    onChanged(n) {
      n ? (document.documentElement.setAttribute("theme-mode", "dark"), document.documentElement.classList.add("insta-dark")) : (document.documentElement.setAttribute("theme-mode", "light"), document.documentElement.classList.remove("insta-dark"));
    }
  });
}
function Ys(e) {
  return zs();
}
const Xs = /* @__PURE__ */ new Map([
  ["storage", qs],
  ["useDark", Qs],
  ["usePageTitle", Ys]
]);
function Zs(e) {
  const { type: t } = e;
  if (!t)
    throw new Error("Invalid ref type");
  const n = Xs.get(t);
  if (!n)
    throw new Error(`Invalid ref type ${t}`);
  return n(e);
}
function eo(e, t) {
  const { deepCompare: n = !1, type: r } = e;
  if (!r) {
    const { value: s } = e;
    return n ? At(s) : W(s);
  }
  return Zs(e);
}
function to(e, t, n) {
  const { bind: r = {}, code: s, const: o = [] } = e, i = Object.values(r).map((u, l) => o[l] === 1 ? u : t.getRef(u));
  if ($n(new Function(s)))
    return Cs(
      async () => {
        const u = Object.fromEntries(
          Object.keys(r).map((l, f) => [l, i[f]])
        );
        return await G(s, u)();
      },
      null,
      { lazy: !0 }
    );
  const a = Object.fromEntries(
    Object.keys(r).map((u, l) => [u, i[l]])
  ), c = G(s, a);
  return j(c);
}
function no(e) {
  const { init: t, deepEqOnInput: n } = e;
  return n === void 0 ? ie(t ?? Ie) : At(t ?? Ie);
}
function ro(e, t, n) {
  const {
    inputs: r = [],
    code: s,
    slient: o,
    data: i,
    asyncInit: a = null,
    deepEqOnInput: c = 0
  } = e, h = o || Array(r.length).fill(0), u = i || Array(r.length).fill(0), l = r.filter((v, w) => h[w] === 0 && u[w] === 0).map((v) => t.getRef(v));
  function f() {
    return r.map((v, w) => {
      if (u[w] === 1)
        return v;
      const g = t.getValue(v);
      return Pt(g) ? g : _n(g);
    });
  }
  const d = G(s), p = c === 0 ? ie(Ie) : At(Ie), y = { immediate: !0, deep: !0 };
  return $n(d) ? (p.value = a, K(
    l,
    async () => {
      f().some(ke) || (p.value = await d(...f()));
    },
    y
  )) : K(
    l,
    () => {
      const v = f();
      v.some(ke) || (p.value = d(...v));
    },
    y
  ), Rt(p);
}
function so(e, t, n) {
  const s = {
    ref: {
      r: n.getBindIndex(F(e, t.id))
    },
    type: Ae.Ref
  };
  return {
    ...t,
    immediate: !0,
    outputs: [s, ...t.outputs || []]
  };
}
function oo(e) {
  const { watchConfigs: t, computedConfigs: n, bindingGetter: r, sid: s } = e;
  return new io(t, n, r, s);
}
class io {
  constructor(t, n, r, s) {
    J(this, "taskQueue", []);
    J(this, "id2TaskMap", /* @__PURE__ */ new Map());
    J(this, "input2TaskIdMap", Sn(() => []));
    this.bindingGetter = r;
    const o = [], i = (a) => {
      var h;
      const c = new ao(a, r);
      return this.id2TaskMap.set(c.id, c), (h = a.inputs) == null || h.forEach((u, l) => {
        var d, p;
        if (((d = a.data) == null ? void 0 : d[l]) === 0 && ((p = a.slient) == null ? void 0 : p[l]) === 0) {
          const y = u.r;
          this.input2TaskIdMap.getOrDefault(y).push(c.id);
        }
      }), c;
    };
    t == null || t.forEach((a) => {
      const c = i(a);
      o.push(c);
    }), n == null || n.forEach((a) => {
      const c = i(
        so(s, a, r)
      );
      o.push(c);
    }), o.forEach((a) => {
      const {
        deep: c = !0,
        once: h,
        flush: u,
        immediate: l = !0
      } = a.watchConfig, f = {
        immediate: l,
        deep: c,
        once: h,
        flush: u
      }, d = this._getWatchTargets(a);
      K(
        d,
        (p) => {
          p.some(ke) || (a.modify = !0, this.taskQueue.push(new co(a)), this._scheduleNextTick());
        },
        f
      );
    });
  }
  _getWatchTargets(t) {
    if (!t.watchConfig.inputs)
      return [];
    const n = t.slientInputs, r = t.constDataInputs;
    return t.watchConfig.inputs.filter(
      (o, i) => !r[i] && !n[i]
    ).map((o) => this.bindingGetter.getRef(o));
  }
  _scheduleNextTick() {
    Se(() => this._runAllTasks());
  }
  _runAllTasks() {
    const t = this.taskQueue.slice();
    this.taskQueue.length = 0, this._setTaskNodeRelations(t), t.forEach((n) => {
      n.run();
    });
  }
  _setTaskNodeRelations(t) {
    t.forEach((n) => {
      const r = this._findNextNodes(n, t);
      n.appendNextNodes(...r), r.forEach((s) => {
        s.appendPrevNodes(n);
      });
    });
  }
  _findNextNodes(t, n) {
    const r = t.watchTask.watchConfig.outputs;
    if (r && r.length <= 0)
      return [];
    const s = this._getCalculatorTasksByOutput(
      t.watchTask.watchConfig.outputs
    );
    return n.filter(
      (o) => s.has(o.watchTask.id) && o.watchTask.id !== t.watchTask.id
    );
  }
  _getCalculatorTasksByOutput(t) {
    const n = /* @__PURE__ */ new Set();
    return t == null || t.forEach((r) => {
      if (!kn(r.ref))
        throw new Error("Non-var output bindings are not supported.");
      const s = r.ref.r;
      (this.input2TaskIdMap.get(s) || []).forEach((i) => n.add(i));
    }), n;
  }
}
class ao {
  constructor(t, n) {
    J(this, "modify", !0);
    J(this, "_running", !1);
    J(this, "id");
    J(this, "_runningPromise", null);
    J(this, "_runningPromiseResolve", null);
    J(this, "_inputInfos");
    this.watchConfig = t, this.bindingGetter = n, this.id = Symbol(t.debug), this._inputInfos = this.createInputInfos();
  }
  createInputInfos() {
    const { inputs: t = [] } = this.watchConfig, n = this.watchConfig.data || Array.from({ length: t.length }).fill(0), r = this.watchConfig.slient || Array.from({ length: t.length }).fill(0);
    return {
      const_data: n,
      slients: r
    };
  }
  get slientInputs() {
    return this._inputInfos.slients;
  }
  get constDataInputs() {
    return this._inputInfos.const_data;
  }
  getServerInputs() {
    const { const_data: t } = this._inputInfos;
    return this.watchConfig.inputs ? this.watchConfig.inputs.map((n, r) => t[r] === 0 ? this.bindingGetter.getValue(n) : n) : [];
  }
  get running() {
    return this._running;
  }
  get runningPromise() {
    return this._runningPromise;
  }
  /**
   * setRunning
   */
  setRunning() {
    this._running = !0, this._runningPromise = new Promise((t) => {
      this._runningPromiseResolve = t;
    });
  }
  /**
   * taskDone
   */
  taskDone() {
    this._running = !1, this._runningPromiseResolve && (this._runningPromiseResolve(), this._runningPromiseResolve = null);
  }
}
class co {
  /**
   *
   */
  constructor(t) {
    J(this, "prevNodes", []);
    J(this, "nextNodes", []);
    J(this, "_runningPrev", !1);
    this.watchTask = t;
  }
  /**
   * appendPrevNodes
   */
  appendPrevNodes(...t) {
    this.prevNodes.push(...t);
  }
  /**
   *
   */
  appendNextNodes(...t) {
    this.nextNodes.push(...t);
  }
  /**
   * hasNextNodes
   */
  hasNextNodes() {
    return this.nextNodes.length > 0;
  }
  /**
   * run
   */
  async run() {
    if (this.prevNodes.length > 0 && !this._runningPrev)
      try {
        this._runningPrev = !0, await Promise.all(this.prevNodes.map((t) => t.run()));
      } finally {
        this._runningPrev = !1;
      }
    if (this.watchTask.running) {
      await this.watchTask.runningPromise;
      return;
    }
    if (this.watchTask.modify) {
      this.watchTask.modify = !1, this.watchTask.setRunning();
      try {
        await lo(this.watchTask);
      } finally {
        this.watchTask.taskDone();
      }
    }
  }
}
async function lo(e) {
  const { bindingGetter: t } = e, { outputs: n, preSetup: r } = e.watchConfig, s = bn({
    config: r,
    bindingGetter: t
  });
  try {
    s.run(), e.taskDone();
    const o = await En().watchSend(e);
    if (!o)
      return;
    qe(o, n, t);
  } finally {
    s.tryReset();
  }
}
function uo(e, t) {
  const {
    on: n,
    code: r,
    immediate: s,
    deep: o,
    once: i,
    flush: a,
    bind: c = {},
    onData: h,
    bindData: u
  } = e, l = h || Array.from({ length: n.length }).fill(0), f = u || Array.from({ length: Object.keys(c).length }).fill(0), d = Ge(
    c,
    (v, w, g) => f[g] === 0 ? t.getRef(v) : v
  ), p = G(r, d), y = n.length === 1 ? zt(l[0] === 1, n[0], t) : n.map(
    (v, w) => zt(l[w] === 1, v, t)
  );
  return K(y, p, { immediate: s, deep: o, once: i, flush: a });
}
function zt(e, t, n) {
  return e ? () => t : n.getRef(t);
}
function fo(e, t) {
  const {
    inputs: n = [],
    outputs: r,
    slient: s,
    data: o,
    code: i,
    immediate: a = !0,
    deep: c,
    once: h,
    flush: u
  } = e, l = s || Array.from({ length: n.length }).fill(0), f = o || Array.from({ length: n.length }).fill(0), d = G(i), p = n.filter((v, w) => l[w] === 0 && f[w] === 0).map((v) => t.getRef(v));
  function y() {
    return n.map((v, w) => {
      if (f[w] === 0) {
        const g = t.getValue(v);
        return Pt(g) ? g : _n(g);
      }
      return v;
    });
  }
  K(
    p,
    () => {
      let v = d(...y());
      if (!r)
        return;
      const g = r.length === 1 ? [v] : v, _ = g.map((S) => S === void 0 ? 1 : 0);
      qe(
        {
          values: g,
          types: _
        },
        r,
        t
      );
    },
    { immediate: a, deep: c, once: h, flush: u }
  );
}
function ho() {
  return Dn().__VUE_DEVTOOLS_GLOBAL_HOOK__;
}
function Dn() {
  return typeof navigator < "u" && typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : {};
}
const po = typeof Proxy == "function", mo = "devtools-plugin:setup", go = "plugin:settings:set";
let _e, yt;
function yo() {
  var e;
  return _e !== void 0 || (typeof window < "u" && window.performance ? (_e = !0, yt = window.performance) : typeof globalThis < "u" && (!((e = globalThis.perf_hooks) === null || e === void 0) && e.performance) ? (_e = !0, yt = globalThis.perf_hooks.performance) : _e = !1), _e;
}
function vo() {
  return yo() ? yt.now() : Date.now();
}
class wo {
  constructor(t, n) {
    this.target = null, this.targetQueue = [], this.onQueue = [], this.plugin = t, this.hook = n;
    const r = {};
    if (t.settings)
      for (const i in t.settings) {
        const a = t.settings[i];
        r[i] = a.defaultValue;
      }
    const s = `__vue-devtools-plugin-settings__${t.id}`;
    let o = Object.assign({}, r);
    try {
      const i = localStorage.getItem(s), a = JSON.parse(i);
      Object.assign(o, a);
    } catch {
    }
    this.fallbacks = {
      getSettings() {
        return o;
      },
      setSettings(i) {
        try {
          localStorage.setItem(s, JSON.stringify(i));
        } catch {
        }
        o = i;
      },
      now() {
        return vo();
      }
    }, n && n.on(go, (i, a) => {
      i === this.plugin.id && this.fallbacks.setSettings(a);
    }), this.proxiedOn = new Proxy({}, {
      get: (i, a) => this.target ? this.target.on[a] : (...c) => {
        this.onQueue.push({
          method: a,
          args: c
        });
      }
    }), this.proxiedTarget = new Proxy({}, {
      get: (i, a) => this.target ? this.target[a] : a === "on" ? this.proxiedOn : Object.keys(this.fallbacks).includes(a) ? (...c) => (this.targetQueue.push({
        method: a,
        args: c,
        resolve: () => {
        }
      }), this.fallbacks[a](...c)) : (...c) => new Promise((h) => {
        this.targetQueue.push({
          method: a,
          args: c,
          resolve: h
        });
      })
    });
  }
  async setRealTarget(t) {
    this.target = t;
    for (const n of this.onQueue)
      this.target.on[n.method](...n.args);
    for (const n of this.targetQueue)
      n.resolve(await this.target[n.method](...n.args));
  }
}
function _o(e, t) {
  const n = e, r = Dn(), s = ho(), o = po && n.enableEarlyProxy;
  if (s && (r.__VUE_DEVTOOLS_PLUGIN_API_AVAILABLE__ || !o))
    s.emit(mo, e, t);
  else {
    const i = o ? new wo(n, s) : null;
    (r.__VUE_DEVTOOLS_PLUGINS__ = r.__VUE_DEVTOOLS_PLUGINS__ || []).push({
      pluginDescriptor: n,
      setupFn: t,
      proxy: i
    }), i && t(i.proxiedTarget);
  }
}
var R = {};
const oe = typeof document < "u";
function jn(e) {
  return typeof e == "object" || "displayName" in e || "props" in e || "__vccOpts" in e;
}
function Eo(e) {
  return e.__esModule || e[Symbol.toStringTag] === "Module" || // support CF with dynamic imports that do not
  // add the Module string tag
  e.default && jn(e.default);
}
const A = Object.assign;
function it(e, t) {
  const n = {};
  for (const r in t) {
    const s = t[r];
    n[r] = Q(s) ? s.map(e) : e(s);
  }
  return n;
}
const $e = () => {
}, Q = Array.isArray;
function O(e) {
  const t = Array.from(arguments).slice(1);
  console.warn.apply(console, ["[Vue Router warn]: " + e].concat(t));
}
const Mn = /#/g, bo = /&/g, So = /\//g, ko = /=/g, Ro = /\?/g, Bn = /\+/g, Oo = /%5B/g, No = /%5D/g, Ln = /%5E/g, Po = /%60/g, Fn = /%7B/g, Vo = /%7C/g, Wn = /%7D/g, Co = /%20/g;
function $t(e) {
  return encodeURI("" + e).replace(Vo, "|").replace(Oo, "[").replace(No, "]");
}
function Ao(e) {
  return $t(e).replace(Fn, "{").replace(Wn, "}").replace(Ln, "^");
}
function vt(e) {
  return $t(e).replace(Bn, "%2B").replace(Co, "+").replace(Mn, "%23").replace(bo, "%26").replace(Po, "`").replace(Fn, "{").replace(Wn, "}").replace(Ln, "^");
}
function $o(e) {
  return vt(e).replace(ko, "%3D");
}
function xo(e) {
  return $t(e).replace(Mn, "%23").replace(Ro, "%3F");
}
function To(e) {
  return e == null ? "" : xo(e).replace(So, "%2F");
}
function Oe(e) {
  try {
    return decodeURIComponent("" + e);
  } catch {
    R.NODE_ENV !== "production" && O(`Error decoding "${e}". Using original value`);
  }
  return "" + e;
}
const Io = /\/$/, Do = (e) => e.replace(Io, "");
function at(e, t, n = "/") {
  let r, s = {}, o = "", i = "";
  const a = t.indexOf("#");
  let c = t.indexOf("?");
  return a < c && a >= 0 && (c = -1), c > -1 && (r = t.slice(0, c), o = t.slice(c + 1, a > -1 ? a : t.length), s = e(o)), a > -1 && (r = r || t.slice(0, a), i = t.slice(a, t.length)), r = Bo(r ?? t, n), {
    fullPath: r + (o && "?") + o + i,
    path: r,
    query: s,
    hash: Oe(i)
  };
}
function jo(e, t) {
  const n = t.query ? e(t.query) : "";
  return t.path + (n && "?") + n + (t.hash || "");
}
function Ht(e, t) {
  return !t || !e.toLowerCase().startsWith(t.toLowerCase()) ? e : e.slice(t.length) || "/";
}
function Kt(e, t, n) {
  const r = t.matched.length - 1, s = n.matched.length - 1;
  return r > -1 && r === s && he(t.matched[r], n.matched[s]) && Un(t.params, n.params) && e(t.query) === e(n.query) && t.hash === n.hash;
}
function he(e, t) {
  return (e.aliasOf || e) === (t.aliasOf || t);
}
function Un(e, t) {
  if (Object.keys(e).length !== Object.keys(t).length)
    return !1;
  for (const n in e)
    if (!Mo(e[n], t[n]))
      return !1;
  return !0;
}
function Mo(e, t) {
  return Q(e) ? Gt(e, t) : Q(t) ? Gt(t, e) : e === t;
}
function Gt(e, t) {
  return Q(t) ? e.length === t.length && e.every((n, r) => n === t[r]) : e.length === 1 && e[0] === t;
}
function Bo(e, t) {
  if (e.startsWith("/"))
    return e;
  if (R.NODE_ENV !== "production" && !t.startsWith("/"))
    return O(`Cannot resolve a relative location without an absolute path. Trying to resolve "${e}" from "${t}". It should look like "/${t}".`), e;
  if (!e)
    return t;
  const n = t.split("/"), r = e.split("/"), s = r[r.length - 1];
  (s === ".." || s === ".") && r.push("");
  let o = n.length - 1, i, a;
  for (i = 0; i < r.length; i++)
    if (a = r[i], a !== ".")
      if (a === "..")
        o > 1 && o--;
      else
        break;
  return n.slice(0, o).join("/") + "/" + r.slice(i).join("/");
}
const ce = {
  path: "/",
  // TODO: could we use a symbol in the future?
  name: void 0,
  params: {},
  query: {},
  hash: "",
  fullPath: "/",
  matched: [],
  meta: {},
  redirectedFrom: void 0
};
var Ne;
(function(e) {
  e.pop = "pop", e.push = "push";
})(Ne || (Ne = {}));
var ge;
(function(e) {
  e.back = "back", e.forward = "forward", e.unknown = "";
})(ge || (ge = {}));
const ct = "";
function zn(e) {
  if (!e)
    if (oe) {
      const t = document.querySelector("base");
      e = t && t.getAttribute("href") || "/", e = e.replace(/^\w+:\/\/[^\/]+/, "");
    } else
      e = "/";
  return e[0] !== "/" && e[0] !== "#" && (e = "/" + e), Do(e);
}
const Lo = /^[^#]+#/;
function Hn(e, t) {
  return e.replace(Lo, "#") + t;
}
function Fo(e, t) {
  const n = document.documentElement.getBoundingClientRect(), r = e.getBoundingClientRect();
  return {
    behavior: t.behavior,
    left: r.left - n.left - (t.left || 0),
    top: r.top - n.top - (t.top || 0)
  };
}
const Je = () => ({
  left: window.scrollX,
  top: window.scrollY
});
function Wo(e) {
  let t;
  if ("el" in e) {
    const n = e.el, r = typeof n == "string" && n.startsWith("#");
    if (R.NODE_ENV !== "production" && typeof e.el == "string" && (!r || !document.getElementById(e.el.slice(1))))
      try {
        const o = document.querySelector(e.el);
        if (r && o) {
          O(`The selector "${e.el}" should be passed as "el: document.querySelector('${e.el}')" because it starts with "#".`);
          return;
        }
      } catch {
        O(`The selector "${e.el}" is invalid. If you are using an id selector, make sure to escape it. You can find more information about escaping characters in selectors at https://mathiasbynens.be/notes/css-escapes or use CSS.escape (https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape).`);
        return;
      }
    const s = typeof n == "string" ? r ? document.getElementById(n.slice(1)) : document.querySelector(n) : n;
    if (!s) {
      R.NODE_ENV !== "production" && O(`Couldn't find element using selector "${e.el}" returned by scrollBehavior.`);
      return;
    }
    t = Fo(s, e);
  } else
    t = e;
  "scrollBehavior" in document.documentElement.style ? window.scrollTo(t) : window.scrollTo(t.left != null ? t.left : window.scrollX, t.top != null ? t.top : window.scrollY);
}
function qt(e, t) {
  return (history.state ? history.state.position - t : -1) + e;
}
const wt = /* @__PURE__ */ new Map();
function Uo(e, t) {
  wt.set(e, t);
}
function zo(e) {
  const t = wt.get(e);
  return wt.delete(e), t;
}
let Ho = () => location.protocol + "//" + location.host;
function Kn(e, t) {
  const { pathname: n, search: r, hash: s } = t, o = e.indexOf("#");
  if (o > -1) {
    let a = s.includes(e.slice(o)) ? e.slice(o).length : 1, c = s.slice(a);
    return c[0] !== "/" && (c = "/" + c), Ht(c, "");
  }
  return Ht(n, e) + r + s;
}
function Ko(e, t, n, r) {
  let s = [], o = [], i = null;
  const a = ({ state: f }) => {
    const d = Kn(e, location), p = n.value, y = t.value;
    let v = 0;
    if (f) {
      if (n.value = d, t.value = f, i && i === p) {
        i = null;
        return;
      }
      v = y ? f.position - y.position : 0;
    } else
      r(d);
    s.forEach((w) => {
      w(n.value, p, {
        delta: v,
        type: Ne.pop,
        direction: v ? v > 0 ? ge.forward : ge.back : ge.unknown
      });
    });
  };
  function c() {
    i = n.value;
  }
  function h(f) {
    s.push(f);
    const d = () => {
      const p = s.indexOf(f);
      p > -1 && s.splice(p, 1);
    };
    return o.push(d), d;
  }
  function u() {
    const { history: f } = window;
    f.state && f.replaceState(A({}, f.state, { scroll: Je() }), "");
  }
  function l() {
    for (const f of o)
      f();
    o = [], window.removeEventListener("popstate", a), window.removeEventListener("beforeunload", u);
  }
  return window.addEventListener("popstate", a), window.addEventListener("beforeunload", u, {
    passive: !0
  }), {
    pauseListeners: c,
    listen: h,
    destroy: l
  };
}
function Jt(e, t, n, r = !1, s = !1) {
  return {
    back: e,
    current: t,
    forward: n,
    replaced: r,
    position: window.history.length,
    scroll: s ? Je() : null
  };
}
function Go(e) {
  const { history: t, location: n } = window, r = {
    value: Kn(e, n)
  }, s = { value: t.state };
  s.value || o(r.value, {
    back: null,
    current: r.value,
    forward: null,
    // the length is off by one, we need to decrease it
    position: t.length - 1,
    replaced: !0,
    // don't add a scroll as the user may have an anchor, and we want
    // scrollBehavior to be triggered without a saved position
    scroll: null
  }, !0);
  function o(c, h, u) {
    const l = e.indexOf("#"), f = l > -1 ? (n.host && document.querySelector("base") ? e : e.slice(l)) + c : Ho() + e + c;
    try {
      t[u ? "replaceState" : "pushState"](h, "", f), s.value = h;
    } catch (d) {
      R.NODE_ENV !== "production" ? O("Error with push/replace State", d) : console.error(d), n[u ? "replace" : "assign"](f);
    }
  }
  function i(c, h) {
    const u = A({}, t.state, Jt(
      s.value.back,
      // keep back and forward entries but override current position
      c,
      s.value.forward,
      !0
    ), h, { position: s.value.position });
    o(c, u, !0), r.value = c;
  }
  function a(c, h) {
    const u = A(
      {},
      // use current history state to gracefully handle a wrong call to
      // history.replaceState
      // https://github.com/vuejs/router/issues/366
      s.value,
      t.state,
      {
        forward: c,
        scroll: Je()
      }
    );
    R.NODE_ENV !== "production" && !t.state && O(`history.state seems to have been manually replaced without preserving the necessary values. Make sure to preserve existing history state if you are manually calling history.replaceState:

history.replaceState(history.state, '', url)

You can find more information at https://router.vuejs.org/guide/migration/#Usage-of-history-state`), o(u.current, u, !0);
    const l = A({}, Jt(r.value, c, null), { position: u.position + 1 }, h);
    o(c, l, !1), r.value = c;
  }
  return {
    location: r,
    state: s,
    push: a,
    replace: i
  };
}
function Gn(e) {
  e = zn(e);
  const t = Go(e), n = Ko(e, t.state, t.location, t.replace);
  function r(o, i = !0) {
    i || n.pauseListeners(), history.go(o);
  }
  const s = A({
    // it's overridden right after
    location: "",
    base: e,
    go: r,
    createHref: Hn.bind(null, e)
  }, t, n);
  return Object.defineProperty(s, "location", {
    enumerable: !0,
    get: () => t.location.value
  }), Object.defineProperty(s, "state", {
    enumerable: !0,
    get: () => t.state.value
  }), s;
}
function qo(e = "") {
  let t = [], n = [ct], r = 0;
  e = zn(e);
  function s(a) {
    r++, r !== n.length && n.splice(r), n.push(a);
  }
  function o(a, c, { direction: h, delta: u }) {
    const l = {
      direction: h,
      delta: u,
      type: Ne.pop
    };
    for (const f of t)
      f(a, c, l);
  }
  const i = {
    // rewritten by Object.defineProperty
    location: ct,
    // TODO: should be kept in queue
    state: {},
    base: e,
    createHref: Hn.bind(null, e),
    replace(a) {
      n.splice(r--, 1), s(a);
    },
    push(a, c) {
      s(a);
    },
    listen(a) {
      return t.push(a), () => {
        const c = t.indexOf(a);
        c > -1 && t.splice(c, 1);
      };
    },
    destroy() {
      t = [], n = [ct], r = 0;
    },
    go(a, c = !0) {
      const h = this.location, u = (
        // we are considering delta === 0 going forward, but in abstract mode
        // using 0 for the delta doesn't make sense like it does in html5 where
        // it reloads the page
        a < 0 ? ge.back : ge.forward
      );
      r = Math.max(0, Math.min(r + a, n.length - 1)), c && o(this.location, h, {
        direction: u,
        delta: a
      });
    }
  };
  return Object.defineProperty(i, "location", {
    enumerable: !0,
    get: () => n[r]
  }), i;
}
function Jo(e) {
  return e = location.host ? e || location.pathname + location.search : "", e.includes("#") || (e += "#"), R.NODE_ENV !== "production" && !e.endsWith("#/") && !e.endsWith("#") && O(`A hash base must end with a "#":
"${e}" should be "${e.replace(/#.*$/, "#")}".`), Gn(e);
}
function ze(e) {
  return typeof e == "string" || e && typeof e == "object";
}
function qn(e) {
  return typeof e == "string" || typeof e == "symbol";
}
const _t = Symbol(R.NODE_ENV !== "production" ? "navigation failure" : "");
var Qt;
(function(e) {
  e[e.aborted = 4] = "aborted", e[e.cancelled = 8] = "cancelled", e[e.duplicated = 16] = "duplicated";
})(Qt || (Qt = {}));
const Qo = {
  1({ location: e, currentLocation: t }) {
    return `No match for
 ${JSON.stringify(e)}${t ? `
while being at
` + JSON.stringify(t) : ""}`;
  },
  2({ from: e, to: t }) {
    return `Redirected from "${e.fullPath}" to "${Xo(t)}" via a navigation guard.`;
  },
  4({ from: e, to: t }) {
    return `Navigation aborted from "${e.fullPath}" to "${t.fullPath}" via a navigation guard.`;
  },
  8({ from: e, to: t }) {
    return `Navigation cancelled from "${e.fullPath}" to "${t.fullPath}" with a new navigation.`;
  },
  16({ from: e, to: t }) {
    return `Avoided redundant navigation to current location: "${e.fullPath}".`;
  }
};
function Pe(e, t) {
  return R.NODE_ENV !== "production" ? A(new Error(Qo[e](t)), {
    type: e,
    [_t]: !0
  }, t) : A(new Error(), {
    type: e,
    [_t]: !0
  }, t);
}
function se(e, t) {
  return e instanceof Error && _t in e && (t == null || !!(e.type & t));
}
const Yo = ["params", "query", "hash"];
function Xo(e) {
  if (typeof e == "string")
    return e;
  if (e.path != null)
    return e.path;
  const t = {};
  for (const n of Yo)
    n in e && (t[n] = e[n]);
  return JSON.stringify(t, null, 2);
}
const Yt = "[^/]+?", Zo = {
  sensitive: !1,
  strict: !1,
  start: !0,
  end: !0
}, ei = /[.+*?^${}()[\]/\\]/g;
function ti(e, t) {
  const n = A({}, Zo, t), r = [];
  let s = n.start ? "^" : "";
  const o = [];
  for (const h of e) {
    const u = h.length ? [] : [
      90
      /* PathScore.Root */
    ];
    n.strict && !h.length && (s += "/");
    for (let l = 0; l < h.length; l++) {
      const f = h[l];
      let d = 40 + (n.sensitive ? 0.25 : 0);
      if (f.type === 0)
        l || (s += "/"), s += f.value.replace(ei, "\\$&"), d += 40;
      else if (f.type === 1) {
        const { value: p, repeatable: y, optional: v, regexp: w } = f;
        o.push({
          name: p,
          repeatable: y,
          optional: v
        });
        const g = w || Yt;
        if (g !== Yt) {
          d += 10;
          try {
            new RegExp(`(${g})`);
          } catch (S) {
            throw new Error(`Invalid custom RegExp for param "${p}" (${g}): ` + S.message);
          }
        }
        let _ = y ? `((?:${g})(?:/(?:${g}))*)` : `(${g})`;
        l || (_ = // avoid an optional / if there are more segments e.g. /:p?-static
        // or /:p?-:p2
        v && h.length < 2 ? `(?:/${_})` : "/" + _), v && (_ += "?"), s += _, d += 20, v && (d += -8), y && (d += -20), g === ".*" && (d += -50);
      }
      u.push(d);
    }
    r.push(u);
  }
  if (n.strict && n.end) {
    const h = r.length - 1;
    r[h][r[h].length - 1] += 0.7000000000000001;
  }
  n.strict || (s += "/?"), n.end ? s += "$" : n.strict && !s.endsWith("/") && (s += "(?:/|$)");
  const i = new RegExp(s, n.sensitive ? "" : "i");
  function a(h) {
    const u = h.match(i), l = {};
    if (!u)
      return null;
    for (let f = 1; f < u.length; f++) {
      const d = u[f] || "", p = o[f - 1];
      l[p.name] = d && p.repeatable ? d.split("/") : d;
    }
    return l;
  }
  function c(h) {
    let u = "", l = !1;
    for (const f of e) {
      (!l || !u.endsWith("/")) && (u += "/"), l = !1;
      for (const d of f)
        if (d.type === 0)
          u += d.value;
        else if (d.type === 1) {
          const { value: p, repeatable: y, optional: v } = d, w = p in h ? h[p] : "";
          if (Q(w) && !y)
            throw new Error(`Provided param "${p}" is an array but it is not repeatable (* or + modifiers)`);
          const g = Q(w) ? w.join("/") : w;
          if (!g)
            if (v)
              f.length < 2 && (u.endsWith("/") ? u = u.slice(0, -1) : l = !0);
            else
              throw new Error(`Missing required param "${p}"`);
          u += g;
        }
    }
    return u || "/";
  }
  return {
    re: i,
    score: r,
    keys: o,
    parse: a,
    stringify: c
  };
}
function ni(e, t) {
  let n = 0;
  for (; n < e.length && n < t.length; ) {
    const r = t[n] - e[n];
    if (r)
      return r;
    n++;
  }
  return e.length < t.length ? e.length === 1 && e[0] === 80 ? -1 : 1 : e.length > t.length ? t.length === 1 && t[0] === 80 ? 1 : -1 : 0;
}
function Jn(e, t) {
  let n = 0;
  const r = e.score, s = t.score;
  for (; n < r.length && n < s.length; ) {
    const o = ni(r[n], s[n]);
    if (o)
      return o;
    n++;
  }
  if (Math.abs(s.length - r.length) === 1) {
    if (Xt(r))
      return 1;
    if (Xt(s))
      return -1;
  }
  return s.length - r.length;
}
function Xt(e) {
  const t = e[e.length - 1];
  return e.length > 0 && t[t.length - 1] < 0;
}
const ri = {
  type: 0,
  value: ""
}, si = /[a-zA-Z0-9_]/;
function oi(e) {
  if (!e)
    return [[]];
  if (e === "/")
    return [[ri]];
  if (!e.startsWith("/"))
    throw new Error(R.NODE_ENV !== "production" ? `Route paths should start with a "/": "${e}" should be "/${e}".` : `Invalid path "${e}"`);
  function t(d) {
    throw new Error(`ERR (${n})/"${h}": ${d}`);
  }
  let n = 0, r = n;
  const s = [];
  let o;
  function i() {
    o && s.push(o), o = [];
  }
  let a = 0, c, h = "", u = "";
  function l() {
    h && (n === 0 ? o.push({
      type: 0,
      value: h
    }) : n === 1 || n === 2 || n === 3 ? (o.length > 1 && (c === "*" || c === "+") && t(`A repeatable param (${h}) must be alone in its segment. eg: '/:ids+.`), o.push({
      type: 1,
      value: h,
      regexp: u,
      repeatable: c === "*" || c === "+",
      optional: c === "*" || c === "?"
    })) : t("Invalid state to consume buffer"), h = "");
  }
  function f() {
    h += c;
  }
  for (; a < e.length; ) {
    if (c = e[a++], c === "\\" && n !== 2) {
      r = n, n = 4;
      continue;
    }
    switch (n) {
      case 0:
        c === "/" ? (h && l(), i()) : c === ":" ? (l(), n = 1) : f();
        break;
      case 4:
        f(), n = r;
        break;
      case 1:
        c === "(" ? n = 2 : si.test(c) ? f() : (l(), n = 0, c !== "*" && c !== "?" && c !== "+" && a--);
        break;
      case 2:
        c === ")" ? u[u.length - 1] == "\\" ? u = u.slice(0, -1) + c : n = 3 : u += c;
        break;
      case 3:
        l(), n = 0, c !== "*" && c !== "?" && c !== "+" && a--, u = "";
        break;
      default:
        t("Unknown state");
        break;
    }
  }
  return n === 2 && t(`Unfinished custom RegExp for param "${h}"`), l(), i(), s;
}
function ii(e, t, n) {
  const r = ti(oi(e.path), n);
  if (R.NODE_ENV !== "production") {
    const o = /* @__PURE__ */ new Set();
    for (const i of r.keys)
      o.has(i.name) && O(`Found duplicated params with name "${i.name}" for path "${e.path}". Only the last one will be available on "$route.params".`), o.add(i.name);
  }
  const s = A(r, {
    record: e,
    parent: t,
    // these needs to be populated by the parent
    children: [],
    alias: []
  });
  return t && !s.record.aliasOf == !t.record.aliasOf && t.children.push(s), s;
}
function ai(e, t) {
  const n = [], r = /* @__PURE__ */ new Map();
  t = nn({ strict: !1, end: !0, sensitive: !1 }, t);
  function s(l) {
    return r.get(l);
  }
  function o(l, f, d) {
    const p = !d, y = en(l);
    R.NODE_ENV !== "production" && fi(y, f), y.aliasOf = d && d.record;
    const v = nn(t, l), w = [y];
    if ("alias" in l) {
      const S = typeof l.alias == "string" ? [l.alias] : l.alias;
      for (const C of S)
        w.push(
          // we need to normalize again to ensure the `mods` property
          // being non enumerable
          en(A({}, y, {
            // this allows us to hold a copy of the `components` option
            // so that async components cache is hold on the original record
            components: d ? d.record.components : y.components,
            path: C,
            // we might be the child of an alias
            aliasOf: d ? d.record : y
            // the aliases are always of the same kind as the original since they
            // are defined on the same record
          }))
        );
    }
    let g, _;
    for (const S of w) {
      const { path: C } = S;
      if (f && C[0] !== "/") {
        const x = f.record.path, I = x[x.length - 1] === "/" ? "" : "/";
        S.path = f.record.path + (C && I + C);
      }
      if (R.NODE_ENV !== "production" && S.path === "*")
        throw new Error(`Catch all routes ("*") must now be defined using a param with a custom regexp.
See more at https://router.vuejs.org/guide/migration/#Removed-star-or-catch-all-routes.`);
      if (g = ii(S, f, v), R.NODE_ENV !== "production" && f && C[0] === "/" && hi(g, f), d ? (d.alias.push(g), R.NODE_ENV !== "production" && ui(d, g)) : (_ = _ || g, _ !== g && _.alias.push(g), p && l.name && !tn(g) && (R.NODE_ENV !== "production" && di(l, f), i(l.name))), Qn(g) && c(g), y.children) {
        const x = y.children;
        for (let I = 0; I < x.length; I++)
          o(x[I], g, d && d.children[I]);
      }
      d = d || g;
    }
    return _ ? () => {
      i(_);
    } : $e;
  }
  function i(l) {
    if (qn(l)) {
      const f = r.get(l);
      f && (r.delete(l), n.splice(n.indexOf(f), 1), f.children.forEach(i), f.alias.forEach(i));
    } else {
      const f = n.indexOf(l);
      f > -1 && (n.splice(f, 1), l.record.name && r.delete(l.record.name), l.children.forEach(i), l.alias.forEach(i));
    }
  }
  function a() {
    return n;
  }
  function c(l) {
    const f = pi(l, n);
    n.splice(f, 0, l), l.record.name && !tn(l) && r.set(l.record.name, l);
  }
  function h(l, f) {
    let d, p = {}, y, v;
    if ("name" in l && l.name) {
      if (d = r.get(l.name), !d)
        throw Pe(1, {
          location: l
        });
      if (R.NODE_ENV !== "production") {
        const _ = Object.keys(l.params || {}).filter((S) => !d.keys.find((C) => C.name === S));
        _.length && O(`Discarded invalid param(s) "${_.join('", "')}" when navigating. See https://github.com/vuejs/router/blob/main/packages/router/CHANGELOG.md#414-2022-08-22 for more details.`);
      }
      v = d.record.name, p = A(
        // paramsFromLocation is a new object
        Zt(
          f.params,
          // only keep params that exist in the resolved location
          // only keep optional params coming from a parent record
          d.keys.filter((_) => !_.optional).concat(d.parent ? d.parent.keys.filter((_) => _.optional) : []).map((_) => _.name)
        ),
        // discard any existing params in the current location that do not exist here
        // #1497 this ensures better active/exact matching
        l.params && Zt(l.params, d.keys.map((_) => _.name))
      ), y = d.stringify(p);
    } else if (l.path != null)
      y = l.path, R.NODE_ENV !== "production" && !y.startsWith("/") && O(`The Matcher cannot resolve relative paths but received "${y}". Unless you directly called \`matcher.resolve("${y}")\`, this is probably a bug in vue-router. Please open an issue at https://github.com/vuejs/router/issues/new/choose.`), d = n.find((_) => _.re.test(y)), d && (p = d.parse(y), v = d.record.name);
    else {
      if (d = f.name ? r.get(f.name) : n.find((_) => _.re.test(f.path)), !d)
        throw Pe(1, {
          location: l,
          currentLocation: f
        });
      v = d.record.name, p = A({}, f.params, l.params), y = d.stringify(p);
    }
    const w = [];
    let g = d;
    for (; g; )
      w.unshift(g.record), g = g.parent;
    return {
      name: v,
      path: y,
      params: p,
      matched: w,
      meta: li(w)
    };
  }
  e.forEach((l) => o(l));
  function u() {
    n.length = 0, r.clear();
  }
  return {
    addRoute: o,
    resolve: h,
    removeRoute: i,
    clearRoutes: u,
    getRoutes: a,
    getRecordMatcher: s
  };
}
function Zt(e, t) {
  const n = {};
  for (const r of t)
    r in e && (n[r] = e[r]);
  return n;
}
function en(e) {
  const t = {
    path: e.path,
    redirect: e.redirect,
    name: e.name,
    meta: e.meta || {},
    aliasOf: e.aliasOf,
    beforeEnter: e.beforeEnter,
    props: ci(e),
    children: e.children || [],
    instances: {},
    leaveGuards: /* @__PURE__ */ new Set(),
    updateGuards: /* @__PURE__ */ new Set(),
    enterCallbacks: {},
    // must be declared afterwards
    // mods: {},
    components: "components" in e ? e.components || null : e.component && { default: e.component }
  };
  return Object.defineProperty(t, "mods", {
    value: {}
  }), t;
}
function ci(e) {
  const t = {}, n = e.props || !1;
  if ("component" in e)
    t.default = n;
  else
    for (const r in e.components)
      t[r] = typeof n == "object" ? n[r] : n;
  return t;
}
function tn(e) {
  for (; e; ) {
    if (e.record.aliasOf)
      return !0;
    e = e.parent;
  }
  return !1;
}
function li(e) {
  return e.reduce((t, n) => A(t, n.meta), {});
}
function nn(e, t) {
  const n = {};
  for (const r in e)
    n[r] = r in t ? t[r] : e[r];
  return n;
}
function Et(e, t) {
  return e.name === t.name && e.optional === t.optional && e.repeatable === t.repeatable;
}
function ui(e, t) {
  for (const n of e.keys)
    if (!n.optional && !t.keys.find(Et.bind(null, n)))
      return O(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
  for (const n of t.keys)
    if (!n.optional && !e.keys.find(Et.bind(null, n)))
      return O(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
}
function fi(e, t) {
  t && t.record.name && !e.name && !e.path && O(`The route named "${String(t.record.name)}" has a child without a name and an empty path. Using that name won't render the empty path child so you probably want to move the name to the child instead. If this is intentional, add a name to the child route to remove the warning.`);
}
function di(e, t) {
  for (let n = t; n; n = n.parent)
    if (n.record.name === e.name)
      throw new Error(`A route named "${String(e.name)}" has been added as a ${t === n ? "child" : "descendant"} of a route with the same name. Route names must be unique and a nested route cannot use the same name as an ancestor.`);
}
function hi(e, t) {
  for (const n of t.keys)
    if (!e.keys.find(Et.bind(null, n)))
      return O(`Absolute path "${e.record.path}" must have the exact same param named "${n.name}" as its parent "${t.record.path}".`);
}
function pi(e, t) {
  let n = 0, r = t.length;
  for (; n !== r; ) {
    const o = n + r >> 1;
    Jn(e, t[o]) < 0 ? r = o : n = o + 1;
  }
  const s = mi(e);
  return s && (r = t.lastIndexOf(s, r - 1), R.NODE_ENV !== "production" && r < 0 && O(`Finding ancestor route "${s.record.path}" failed for "${e.record.path}"`)), r;
}
function mi(e) {
  let t = e;
  for (; t = t.parent; )
    if (Qn(t) && Jn(e, t) === 0)
      return t;
}
function Qn({ record: e }) {
  return !!(e.name || e.components && Object.keys(e.components).length || e.redirect);
}
function gi(e) {
  const t = {};
  if (e === "" || e === "?")
    return t;
  const r = (e[0] === "?" ? e.slice(1) : e).split("&");
  for (let s = 0; s < r.length; ++s) {
    const o = r[s].replace(Bn, " "), i = o.indexOf("="), a = Oe(i < 0 ? o : o.slice(0, i)), c = i < 0 ? null : Oe(o.slice(i + 1));
    if (a in t) {
      let h = t[a];
      Q(h) || (h = t[a] = [h]), h.push(c);
    } else
      t[a] = c;
  }
  return t;
}
function rn(e) {
  let t = "";
  for (let n in e) {
    const r = e[n];
    if (n = $o(n), r == null) {
      r !== void 0 && (t += (t.length ? "&" : "") + n);
      continue;
    }
    (Q(r) ? r.map((o) => o && vt(o)) : [r && vt(r)]).forEach((o) => {
      o !== void 0 && (t += (t.length ? "&" : "") + n, o != null && (t += "=" + o));
    });
  }
  return t;
}
function yi(e) {
  const t = {};
  for (const n in e) {
    const r = e[n];
    r !== void 0 && (t[n] = Q(r) ? r.map((s) => s == null ? null : "" + s) : r == null ? r : "" + r);
  }
  return t;
}
const vi = Symbol(R.NODE_ENV !== "production" ? "router view location matched" : ""), sn = Symbol(R.NODE_ENV !== "production" ? "router view depth" : ""), Qe = Symbol(R.NODE_ENV !== "production" ? "router" : ""), xt = Symbol(R.NODE_ENV !== "production" ? "route location" : ""), bt = Symbol(R.NODE_ENV !== "production" ? "router view location" : "");
function Ve() {
  let e = [];
  function t(r) {
    return e.push(r), () => {
      const s = e.indexOf(r);
      s > -1 && e.splice(s, 1);
    };
  }
  function n() {
    e = [];
  }
  return {
    add: t,
    list: () => e.slice(),
    reset: n
  };
}
function le(e, t, n, r, s, o = (i) => i()) {
  const i = r && // name is defined if record is because of the function overload
  (r.enterCallbacks[s] = r.enterCallbacks[s] || []);
  return () => new Promise((a, c) => {
    const h = (f) => {
      f === !1 ? c(Pe(4, {
        from: n,
        to: t
      })) : f instanceof Error ? c(f) : ze(f) ? c(Pe(2, {
        from: t,
        to: f
      })) : (i && // since enterCallbackArray is truthy, both record and name also are
      r.enterCallbacks[s] === i && typeof f == "function" && i.push(f), a());
    }, u = o(() => e.call(r && r.instances[s], t, n, R.NODE_ENV !== "production" ? wi(h, t, n) : h));
    let l = Promise.resolve(u);
    if (e.length < 3 && (l = l.then(h)), R.NODE_ENV !== "production" && e.length > 2) {
      const f = `The "next" callback was never called inside of ${e.name ? '"' + e.name + '"' : ""}:
${e.toString()}
. If you are returning a value instead of calling "next", make sure to remove the "next" parameter from your function.`;
      if (typeof u == "object" && "then" in u)
        l = l.then((d) => h._called ? d : (O(f), Promise.reject(new Error("Invalid navigation guard"))));
      else if (u !== void 0 && !h._called) {
        O(f), c(new Error("Invalid navigation guard"));
        return;
      }
    }
    l.catch((f) => c(f));
  });
}
function wi(e, t, n) {
  let r = 0;
  return function() {
    r++ === 1 && O(`The "next" callback was called more than once in one navigation guard when going from "${n.fullPath}" to "${t.fullPath}". It should be called exactly one time in each navigation guard. This will fail in production.`), e._called = !0, r === 1 && e.apply(null, arguments);
  };
}
function lt(e, t, n, r, s = (o) => o()) {
  const o = [];
  for (const i of e) {
    R.NODE_ENV !== "production" && !i.components && !i.children.length && O(`Record with path "${i.path}" is either missing a "component(s)" or "children" property.`);
    for (const a in i.components) {
      let c = i.components[a];
      if (R.NODE_ENV !== "production") {
        if (!c || typeof c != "object" && typeof c != "function")
          throw O(`Component "${a}" in record with path "${i.path}" is not a valid component. Received "${String(c)}".`), new Error("Invalid route component");
        if ("then" in c) {
          O(`Component "${a}" in record with path "${i.path}" is a Promise instead of a function that returns a Promise. Did you write "import('./MyPage.vue')" instead of "() => import('./MyPage.vue')" ? This will break in production if not fixed.`);
          const h = c;
          c = () => h;
        } else c.__asyncLoader && // warn only once per component
        !c.__warnedDefineAsync && (c.__warnedDefineAsync = !0, O(`Component "${a}" in record with path "${i.path}" is defined using "defineAsyncComponent()". Write "() => import('./MyPage.vue')" instead of "defineAsyncComponent(() => import('./MyPage.vue'))".`));
      }
      if (!(t !== "beforeRouteEnter" && !i.instances[a]))
        if (jn(c)) {
          const u = (c.__vccOpts || c)[t];
          u && o.push(le(u, n, r, i, a, s));
        } else {
          let h = c();
          R.NODE_ENV !== "production" && !("catch" in h) && (O(`Component "${a}" in record with path "${i.path}" is a function that does not return a Promise. If you were passing a functional component, make sure to add a "displayName" to the component. This will break in production if not fixed.`), h = Promise.resolve(h)), o.push(() => h.then((u) => {
            if (!u)
              throw new Error(`Couldn't resolve component "${a}" at "${i.path}"`);
            const l = Eo(u) ? u.default : u;
            i.mods[a] = u, i.components[a] = l;
            const d = (l.__vccOpts || l)[t];
            return d && le(d, n, r, i, a, s)();
          }));
        }
    }
  }
  return o;
}
function on(e) {
  const t = ae(Qe), n = ae(xt);
  let r = !1, s = null;
  const o = j(() => {
    const u = z(e.to);
    return R.NODE_ENV !== "production" && (!r || u !== s) && (ze(u) || (r ? O(`Invalid value for prop "to" in useLink()
- to:`, u, `
- previous to:`, s, `
- props:`, e) : O(`Invalid value for prop "to" in useLink()
- to:`, u, `
- props:`, e)), s = u, r = !0), t.resolve(u);
  }), i = j(() => {
    const { matched: u } = o.value, { length: l } = u, f = u[l - 1], d = n.matched;
    if (!f || !d.length)
      return -1;
    const p = d.findIndex(he.bind(null, f));
    if (p > -1)
      return p;
    const y = an(u[l - 2]);
    return (
      // we are dealing with nested routes
      l > 1 && // if the parent and matched route have the same path, this link is
      // referring to the empty child. Or we currently are on a different
      // child of the same parent
      an(f) === y && // avoid comparing the child with its parent
      d[d.length - 1].path !== y ? d.findIndex(he.bind(null, u[l - 2])) : p
    );
  }), a = j(() => i.value > -1 && ki(n.params, o.value.params)), c = j(() => i.value > -1 && i.value === n.matched.length - 1 && Un(n.params, o.value.params));
  function h(u = {}) {
    if (Si(u)) {
      const l = t[z(e.replace) ? "replace" : "push"](
        z(e.to)
        // avoid uncaught errors are they are logged anyway
      ).catch($e);
      return e.viewTransition && typeof document < "u" && "startViewTransition" in document && document.startViewTransition(() => l), l;
    }
    return Promise.resolve();
  }
  if (R.NODE_ENV !== "production" && oe) {
    const u = He();
    if (u) {
      const l = {
        route: o.value,
        isActive: a.value,
        isExactActive: c.value,
        error: null
      };
      u.__vrl_devtools = u.__vrl_devtools || [], u.__vrl_devtools.push(l), Nt(() => {
        l.route = o.value, l.isActive = a.value, l.isExactActive = c.value, l.error = ze(z(e.to)) ? null : 'Invalid "to" value';
      }, { flush: "post" });
    }
  }
  return {
    route: o,
    href: j(() => o.value.href),
    isActive: a,
    isExactActive: c,
    navigate: h
  };
}
function _i(e) {
  return e.length === 1 ? e[0] : e;
}
const Ei = /* @__PURE__ */ X({
  name: "RouterLink",
  compatConfig: { MODE: 3 },
  props: {
    to: {
      type: [String, Object],
      required: !0
    },
    replace: Boolean,
    activeClass: String,
    // inactiveClass: String,
    exactActiveClass: String,
    custom: Boolean,
    ariaCurrentValue: {
      type: String,
      default: "page"
    }
  },
  useLink: on,
  setup(e, { slots: t }) {
    const n = Rr(on(e)), { options: r } = ae(Qe), s = j(() => ({
      [cn(e.activeClass, r.linkActiveClass, "router-link-active")]: n.isActive,
      // [getLinkClass(
      //   props.inactiveClass,
      //   options.linkInactiveClass,
      //   'router-link-inactive'
      // )]: !link.isExactActive,
      [cn(e.exactActiveClass, r.linkExactActiveClass, "router-link-exact-active")]: n.isExactActive
    }));
    return () => {
      const o = t.default && _i(t.default(n));
      return e.custom ? o : q("a", {
        "aria-current": n.isExactActive ? e.ariaCurrentValue : null,
        href: n.href,
        // this would override user added attrs but Vue will still add
        // the listener, so we end up triggering both
        onClick: n.navigate,
        class: s.value
      }, o);
    };
  }
}), bi = Ei;
function Si(e) {
  if (!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey) && !e.defaultPrevented && !(e.button !== void 0 && e.button !== 0)) {
    if (e.currentTarget && e.currentTarget.getAttribute) {
      const t = e.currentTarget.getAttribute("target");
      if (/\b_blank\b/i.test(t))
        return;
    }
    return e.preventDefault && e.preventDefault(), !0;
  }
}
function ki(e, t) {
  for (const n in t) {
    const r = t[n], s = e[n];
    if (typeof r == "string") {
      if (r !== s)
        return !1;
    } else if (!Q(s) || s.length !== r.length || r.some((o, i) => o !== s[i]))
      return !1;
  }
  return !0;
}
function an(e) {
  return e ? e.aliasOf ? e.aliasOf.path : e.path : "";
}
const cn = (e, t, n) => e ?? t ?? n, Ri = /* @__PURE__ */ X({
  name: "RouterView",
  // #674 we manually inherit them
  inheritAttrs: !1,
  props: {
    name: {
      type: String,
      default: "default"
    },
    route: Object
  },
  // Better compat for @vue/compat users
  // https://github.com/vuejs/router/issues/1315
  compatConfig: { MODE: 3 },
  setup(e, { attrs: t, slots: n }) {
    R.NODE_ENV !== "production" && Ni();
    const r = ae(bt), s = j(() => e.route || r.value), o = ae(sn, 0), i = j(() => {
      let h = z(o);
      const { matched: u } = s.value;
      let l;
      for (; (l = u[h]) && !l.components; )
        h++;
      return h;
    }), a = j(() => s.value.matched[i.value]);
    U(sn, j(() => i.value + 1)), U(vi, a), U(bt, s);
    const c = W();
    return K(() => [c.value, a.value, e.name], ([h, u, l], [f, d, p]) => {
      u && (u.instances[l] = h, d && d !== u && h && h === f && (u.leaveGuards.size || (u.leaveGuards = d.leaveGuards), u.updateGuards.size || (u.updateGuards = d.updateGuards))), h && u && // if there is no instance but to and from are the same this might be
      // the first visit
      (!d || !he(u, d) || !f) && (u.enterCallbacks[l] || []).forEach((y) => y(h));
    }, { flush: "post" }), () => {
      const h = s.value, u = e.name, l = a.value, f = l && l.components[u];
      if (!f)
        return ln(n.default, { Component: f, route: h });
      const d = l.props[u], p = d ? d === !0 ? h.params : typeof d == "function" ? d(h) : d : null, v = q(f, A({}, p, t, {
        onVnodeUnmounted: (w) => {
          w.component.isUnmounted && (l.instances[u] = null);
        },
        ref: c
      }));
      if (R.NODE_ENV !== "production" && oe && v.ref) {
        const w = {
          depth: i.value,
          name: l.name,
          path: l.path,
          meta: l.meta
        };
        (Q(v.ref) ? v.ref.map((_) => _.i) : [v.ref.i]).forEach((_) => {
          _.__vrv_devtools = w;
        });
      }
      return (
        // pass the vnode to the slot as a prop.
        // h and <component :is="..."> both accept vnodes
        ln(n.default, { Component: v, route: h }) || v
      );
    };
  }
});
function ln(e, t) {
  if (!e)
    return null;
  const n = e(t);
  return n.length === 1 ? n[0] : n;
}
const Oi = Ri;
function Ni() {
  const e = He(), t = e.parent && e.parent.type.name, n = e.parent && e.parent.subTree && e.parent.subTree.type;
  if (t && (t === "KeepAlive" || t.includes("Transition")) && typeof n == "object" && n.name === "RouterView") {
    const r = t === "KeepAlive" ? "keep-alive" : "transition";
    O(`<router-view> can no longer be used directly inside <transition> or <keep-alive>.
Use slot props instead:

<router-view v-slot="{ Component }">
  <${r}>
    <component :is="Component" />
  </${r}>
</router-view>`);
  }
}
function Ce(e, t) {
  const n = A({}, e, {
    // remove variables that can contain vue instances
    matched: e.matched.map((r) => Mi(r, ["instances", "children", "aliasOf"]))
  });
  return {
    _custom: {
      type: null,
      readOnly: !0,
      display: e.fullPath,
      tooltip: t,
      value: n
    }
  };
}
function Fe(e) {
  return {
    _custom: {
      display: e
    }
  };
}
let Pi = 0;
function Vi(e, t, n) {
  if (t.__hasDevtools)
    return;
  t.__hasDevtools = !0;
  const r = Pi++;
  _o({
    id: "org.vuejs.router" + (r ? "." + r : ""),
    label: "Vue Router",
    packageName: "vue-router",
    homepage: "https://router.vuejs.org",
    logo: "https://router.vuejs.org/logo.png",
    componentStateTypes: ["Routing"],
    app: e
  }, (s) => {
    typeof s.now != "function" && console.warn("[Vue Router]: You seem to be using an outdated version of Vue Devtools. Are you still using the Beta release instead of the stable one? You can find the links at https://devtools.vuejs.org/guide/installation.html."), s.on.inspectComponent((u, l) => {
      u.instanceData && u.instanceData.state.push({
        type: "Routing",
        key: "$route",
        editable: !1,
        value: Ce(t.currentRoute.value, "Current Route")
      });
    }), s.on.visitComponentTree(({ treeNode: u, componentInstance: l }) => {
      if (l.__vrv_devtools) {
        const f = l.__vrv_devtools;
        u.tags.push({
          label: (f.name ? `${f.name.toString()}: ` : "") + f.path,
          textColor: 0,
          tooltip: "This component is rendered by &lt;router-view&gt;",
          backgroundColor: Yn
        });
      }
      Q(l.__vrl_devtools) && (l.__devtoolsApi = s, l.__vrl_devtools.forEach((f) => {
        let d = f.route.path, p = er, y = "", v = 0;
        f.error ? (d = f.error, p = Ti, v = Ii) : f.isExactActive ? (p = Zn, y = "This is exactly active") : f.isActive && (p = Xn, y = "This link is active"), u.tags.push({
          label: d,
          textColor: v,
          tooltip: y,
          backgroundColor: p
        });
      }));
    }), K(t.currentRoute, () => {
      c(), s.notifyComponentUpdate(), s.sendInspectorTree(a), s.sendInspectorState(a);
    });
    const o = "router:navigations:" + r;
    s.addTimelineLayer({
      id: o,
      label: `Router${r ? " " + r : ""} Navigations`,
      color: 4237508
    }), t.onError((u, l) => {
      s.addTimelineEvent({
        layerId: o,
        event: {
          title: "Error during Navigation",
          subtitle: l.fullPath,
          logType: "error",
          time: s.now(),
          data: { error: u },
          groupId: l.meta.__navigationId
        }
      });
    });
    let i = 0;
    t.beforeEach((u, l) => {
      const f = {
        guard: Fe("beforeEach"),
        from: Ce(l, "Current Location during this navigation"),
        to: Ce(u, "Target location")
      };
      Object.defineProperty(u.meta, "__navigationId", {
        value: i++
      }), s.addTimelineEvent({
        layerId: o,
        event: {
          time: s.now(),
          title: "Start of navigation",
          subtitle: u.fullPath,
          data: f,
          groupId: u.meta.__navigationId
        }
      });
    }), t.afterEach((u, l, f) => {
      const d = {
        guard: Fe("afterEach")
      };
      f ? (d.failure = {
        _custom: {
          type: Error,
          readOnly: !0,
          display: f ? f.message : "",
          tooltip: "Navigation Failure",
          value: f
        }
      }, d.status = Fe("❌")) : d.status = Fe("✅"), d.from = Ce(l, "Current Location during this navigation"), d.to = Ce(u, "Target location"), s.addTimelineEvent({
        layerId: o,
        event: {
          title: "End of navigation",
          subtitle: u.fullPath,
          time: s.now(),
          data: d,
          logType: f ? "warning" : "default",
          groupId: u.meta.__navigationId
        }
      });
    });
    const a = "router-inspector:" + r;
    s.addInspector({
      id: a,
      label: "Routes" + (r ? " " + r : ""),
      icon: "book",
      treeFilterPlaceholder: "Search routes"
    });
    function c() {
      if (!h)
        return;
      const u = h;
      let l = n.getRoutes().filter((f) => !f.parent || // these routes have a parent with no component which will not appear in the view
      // therefore we still need to include them
      !f.parent.record.components);
      l.forEach(rr), u.filter && (l = l.filter((f) => (
        // save matches state based on the payload
        St(f, u.filter.toLowerCase())
      ))), l.forEach((f) => nr(f, t.currentRoute.value)), u.rootNodes = l.map(tr);
    }
    let h;
    s.on.getInspectorTree((u) => {
      h = u, u.app === e && u.inspectorId === a && c();
    }), s.on.getInspectorState((u) => {
      if (u.app === e && u.inspectorId === a) {
        const f = n.getRoutes().find((d) => d.record.__vd_id === u.nodeId);
        f && (u.state = {
          options: Ai(f)
        });
      }
    }), s.sendInspectorTree(a), s.sendInspectorState(a);
  });
}
function Ci(e) {
  return e.optional ? e.repeatable ? "*" : "?" : e.repeatable ? "+" : "";
}
function Ai(e) {
  const { record: t } = e, n = [
    { editable: !1, key: "path", value: t.path }
  ];
  return t.name != null && n.push({
    editable: !1,
    key: "name",
    value: t.name
  }), n.push({ editable: !1, key: "regexp", value: e.re }), e.keys.length && n.push({
    editable: !1,
    key: "keys",
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.keys.map((r) => `${r.name}${Ci(r)}`).join(" "),
        tooltip: "Param keys",
        value: e.keys
      }
    }
  }), t.redirect != null && n.push({
    editable: !1,
    key: "redirect",
    value: t.redirect
  }), e.alias.length && n.push({
    editable: !1,
    key: "aliases",
    value: e.alias.map((r) => r.record.path)
  }), Object.keys(e.record.meta).length && n.push({
    editable: !1,
    key: "meta",
    value: e.record.meta
  }), n.push({
    key: "score",
    editable: !1,
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.score.map((r) => r.join(", ")).join(" | "),
        tooltip: "Score used to sort routes",
        value: e.score
      }
    }
  }), n;
}
const Yn = 15485081, Xn = 2450411, Zn = 8702998, $i = 2282478, er = 16486972, xi = 6710886, Ti = 16704226, Ii = 12131356;
function tr(e) {
  const t = [], { record: n } = e;
  n.name != null && t.push({
    label: String(n.name),
    textColor: 0,
    backgroundColor: $i
  }), n.aliasOf && t.push({
    label: "alias",
    textColor: 0,
    backgroundColor: er
  }), e.__vd_match && t.push({
    label: "matches",
    textColor: 0,
    backgroundColor: Yn
  }), e.__vd_exactActive && t.push({
    label: "exact",
    textColor: 0,
    backgroundColor: Zn
  }), e.__vd_active && t.push({
    label: "active",
    textColor: 0,
    backgroundColor: Xn
  }), n.redirect && t.push({
    label: typeof n.redirect == "string" ? `redirect: ${n.redirect}` : "redirects",
    textColor: 16777215,
    backgroundColor: xi
  });
  let r = n.__vd_id;
  return r == null && (r = String(Di++), n.__vd_id = r), {
    id: r,
    label: n.path,
    tags: t,
    children: e.children.map(tr)
  };
}
let Di = 0;
const ji = /^\/(.*)\/([a-z]*)$/;
function nr(e, t) {
  const n = t.matched.length && he(t.matched[t.matched.length - 1], e.record);
  e.__vd_exactActive = e.__vd_active = n, n || (e.__vd_active = t.matched.some((r) => he(r, e.record))), e.children.forEach((r) => nr(r, t));
}
function rr(e) {
  e.__vd_match = !1, e.children.forEach(rr);
}
function St(e, t) {
  const n = String(e.re).match(ji);
  if (e.__vd_match = !1, !n || n.length < 3)
    return !1;
  if (new RegExp(n[1].replace(/\$$/, ""), n[2]).test(t))
    return e.children.forEach((i) => St(i, t)), e.record.path !== "/" || t === "/" ? (e.__vd_match = e.re.test(t), !0) : !1;
  const s = e.record.path.toLowerCase(), o = Oe(s);
  return !t.startsWith("/") && (o.includes(t) || s.includes(t)) || o.startsWith(t) || s.startsWith(t) || e.record.name && String(e.record.name).includes(t) ? !0 : e.children.some((i) => St(i, t));
}
function Mi(e, t) {
  const n = {};
  for (const r in e)
    t.includes(r) || (n[r] = e[r]);
  return n;
}
function Bi(e) {
  const t = ai(e.routes, e), n = e.parseQuery || gi, r = e.stringifyQuery || rn, s = e.history;
  if (R.NODE_ENV !== "production" && !s)
    throw new Error('Provide the "history" option when calling "createRouter()": https://router.vuejs.org/api/interfaces/RouterOptions.html#history');
  const o = Ve(), i = Ve(), a = Ve(), c = ie(ce);
  let h = ce;
  oe && e.scrollBehavior && "scrollRestoration" in history && (history.scrollRestoration = "manual");
  const u = it.bind(null, (m) => "" + m), l = it.bind(null, To), f = (
    // @ts-expect-error: intentionally avoid the type check
    it.bind(null, Oe)
  );
  function d(m, b) {
    let E, k;
    return qn(m) ? (E = t.getRecordMatcher(m), R.NODE_ENV !== "production" && !E && O(`Parent route "${String(m)}" not found when adding child route`, b), k = b) : k = m, t.addRoute(k, E);
  }
  function p(m) {
    const b = t.getRecordMatcher(m);
    b ? t.removeRoute(b) : R.NODE_ENV !== "production" && O(`Cannot remove non-existent route "${String(m)}"`);
  }
  function y() {
    return t.getRoutes().map((m) => m.record);
  }
  function v(m) {
    return !!t.getRecordMatcher(m);
  }
  function w(m, b) {
    if (b = A({}, b || c.value), typeof m == "string") {
      const N = at(n, m, b.path), M = t.resolve({ path: N.path }, b), pe = s.createHref(N.fullPath);
      return R.NODE_ENV !== "production" && (pe.startsWith("//") ? O(`Location "${m}" resolved to "${pe}". A resolved location cannot start with multiple slashes.`) : M.matched.length || O(`No match found for location with path "${m}"`)), A(N, M, {
        params: f(M.params),
        hash: Oe(N.hash),
        redirectedFrom: void 0,
        href: pe
      });
    }
    if (R.NODE_ENV !== "production" && !ze(m))
      return O(`router.resolve() was passed an invalid location. This will fail in production.
- Location:`, m), w({});
    let E;
    if (m.path != null)
      R.NODE_ENV !== "production" && "params" in m && !("name" in m) && // @ts-expect-error: the type is never
      Object.keys(m.params).length && O(`Path "${m.path}" was passed with params but they will be ignored. Use a named route alongside params instead.`), E = A({}, m, {
        path: at(n, m.path, b.path).path
      });
    else {
      const N = A({}, m.params);
      for (const M in N)
        N[M] == null && delete N[M];
      E = A({}, m, {
        params: l(N)
      }), b.params = l(b.params);
    }
    const k = t.resolve(E, b), $ = m.hash || "";
    R.NODE_ENV !== "production" && $ && !$.startsWith("#") && O(`A \`hash\` should always start with the character "#". Replace "${$}" with "#${$}".`), k.params = u(f(k.params));
    const L = jo(r, A({}, m, {
      hash: Ao($),
      path: k.path
    })), V = s.createHref(L);
    return R.NODE_ENV !== "production" && (V.startsWith("//") ? O(`Location "${m}" resolved to "${V}". A resolved location cannot start with multiple slashes.`) : k.matched.length || O(`No match found for location with path "${m.path != null ? m.path : m}"`)), A({
      fullPath: L,
      // keep the hash encoded so fullPath is effectively path + encodedQuery +
      // hash
      hash: $,
      query: (
        // if the user is using a custom query lib like qs, we might have
        // nested objects, so we keep the query as is, meaning it can contain
        // numbers at `$route.query`, but at the point, the user will have to
        // use their own type anyway.
        // https://github.com/vuejs/router/issues/328#issuecomment-649481567
        r === rn ? yi(m.query) : m.query || {}
      )
    }, k, {
      redirectedFrom: void 0,
      href: V
    });
  }
  function g(m) {
    return typeof m == "string" ? at(n, m, c.value.path) : A({}, m);
  }
  function _(m, b) {
    if (h !== m)
      return Pe(8, {
        from: b,
        to: m
      });
  }
  function S(m) {
    return I(m);
  }
  function C(m) {
    return S(A(g(m), { replace: !0 }));
  }
  function x(m) {
    const b = m.matched[m.matched.length - 1];
    if (b && b.redirect) {
      const { redirect: E } = b;
      let k = typeof E == "function" ? E(m) : E;
      if (typeof k == "string" && (k = k.includes("?") || k.includes("#") ? k = g(k) : (
        // force empty params
        { path: k }
      ), k.params = {}), R.NODE_ENV !== "production" && k.path == null && !("name" in k))
        throw O(`Invalid redirect found:
${JSON.stringify(k, null, 2)}
 when navigating to "${m.fullPath}". A redirect must contain a name or path. This will break in production.`), new Error("Invalid redirect");
      return A({
        query: m.query,
        hash: m.hash,
        // avoid transferring params if the redirect has a path
        params: k.path != null ? {} : m.params
      }, k);
    }
  }
  function I(m, b) {
    const E = h = w(m), k = c.value, $ = m.state, L = m.force, V = m.replace === !0, N = x(E);
    if (N)
      return I(
        A(g(N), {
          state: typeof N == "object" ? A({}, $, N.state) : $,
          force: L,
          replace: V
        }),
        // keep original redirectedFrom if it exists
        b || E
      );
    const M = E;
    M.redirectedFrom = b;
    let pe;
    return !L && Kt(r, k, E) && (pe = Pe(16, { to: M, from: k }), It(
      k,
      k,
      // this is a push, the only way for it to be triggered from a
      // history.listen is with a redirect, which makes it become a push
      !0,
      // This cannot be the first navigation because the initial location
      // cannot be manually navigated to
      !1
    )), (pe ? Promise.resolve(pe) : P(M, k)).catch((H) => se(H) ? (
      // navigation redirects still mark the router as ready
      se(
        H,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? H : rt(H)
    ) : (
      // reject any unknown error
      nt(H, M, k)
    )).then((H) => {
      if (H) {
        if (se(
          H,
          2
          /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
        ))
          return R.NODE_ENV !== "production" && // we are redirecting to the same location we were already at
          Kt(r, w(H.to), M) && // and we have done it a couple of times
          b && // @ts-expect-error: added only in dev
          (b._count = b._count ? (
            // @ts-expect-error
            b._count + 1
          ) : 1) > 30 ? (O(`Detected a possibly infinite redirection in a navigation guard when going from "${k.fullPath}" to "${M.fullPath}". Aborting to avoid a Stack Overflow.
 Are you always returning a new location within a navigation guard? That would lead to this error. Only return when redirecting or aborting, that should fix this. This might break in production if not fixed.`), Promise.reject(new Error("Infinite redirect in navigation guard"))) : I(
            // keep options
            A({
              // preserve an existing replacement but allow the redirect to override it
              replace: V
            }, g(H.to), {
              state: typeof H.to == "object" ? A({}, $, H.to.state) : $,
              force: L
            }),
            // preserve the original redirectedFrom if any
            b || M
          );
      } else
        H = B(M, k, !0, V, $);
      return T(M, k, H), H;
    });
  }
  function Y(m, b) {
    const E = _(m, b);
    return E ? Promise.reject(E) : Promise.resolve();
  }
  function Z(m) {
    const b = Me.values().next().value;
    return b && typeof b.runWithContext == "function" ? b.runWithContext(m) : m();
  }
  function P(m, b) {
    let E;
    const [k, $, L] = Li(m, b);
    E = lt(k.reverse(), "beforeRouteLeave", m, b);
    for (const N of k)
      N.leaveGuards.forEach((M) => {
        E.push(le(M, m, b));
      });
    const V = Y.bind(null, m, b);
    return E.push(V), we(E).then(() => {
      E = [];
      for (const N of o.list())
        E.push(le(N, m, b));
      return E.push(V), we(E);
    }).then(() => {
      E = lt($, "beforeRouteUpdate", m, b);
      for (const N of $)
        N.updateGuards.forEach((M) => {
          E.push(le(M, m, b));
        });
      return E.push(V), we(E);
    }).then(() => {
      E = [];
      for (const N of L)
        if (N.beforeEnter)
          if (Q(N.beforeEnter))
            for (const M of N.beforeEnter)
              E.push(le(M, m, b));
          else
            E.push(le(N.beforeEnter, m, b));
      return E.push(V), we(E);
    }).then(() => (m.matched.forEach((N) => N.enterCallbacks = {}), E = lt(L, "beforeRouteEnter", m, b, Z), E.push(V), we(E))).then(() => {
      E = [];
      for (const N of i.list())
        E.push(le(N, m, b));
      return E.push(V), we(E);
    }).catch((N) => se(
      N,
      8
      /* ErrorTypes.NAVIGATION_CANCELLED */
    ) ? N : Promise.reject(N));
  }
  function T(m, b, E) {
    a.list().forEach((k) => Z(() => k(m, b, E)));
  }
  function B(m, b, E, k, $) {
    const L = _(m, b);
    if (L)
      return L;
    const V = b === ce, N = oe ? history.state : {};
    E && (k || V ? s.replace(m.fullPath, A({
      scroll: V && N && N.scroll
    }, $)) : s.push(m.fullPath, $)), c.value = m, It(m, b, E, V), rt();
  }
  let ee;
  function cr() {
    ee || (ee = s.listen((m, b, E) => {
      if (!Dt.listening)
        return;
      const k = w(m), $ = x(k);
      if ($) {
        I(A($, { replace: !0, force: !0 }), k).catch($e);
        return;
      }
      h = k;
      const L = c.value;
      oe && Uo(qt(L.fullPath, E.delta), Je()), P(k, L).catch((V) => se(
        V,
        12
        /* ErrorTypes.NAVIGATION_CANCELLED */
      ) ? V : se(
        V,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? (I(
        A(g(V.to), {
          force: !0
        }),
        k
        // avoid an uncaught rejection, let push call triggerError
      ).then((N) => {
        se(
          N,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && !E.delta && E.type === Ne.pop && s.go(-1, !1);
      }).catch($e), Promise.reject()) : (E.delta && s.go(-E.delta, !1), nt(V, k, L))).then((V) => {
        V = V || B(
          // after navigation, all matched components are resolved
          k,
          L,
          !1
        ), V && (E.delta && // a new navigation has been triggered, so we do not want to revert, that will change the current history
        // entry while a different route is displayed
        !se(
          V,
          8
          /* ErrorTypes.NAVIGATION_CANCELLED */
        ) ? s.go(-E.delta, !1) : E.type === Ne.pop && se(
          V,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && s.go(-1, !1)), T(k, L, V);
      }).catch($e);
    }));
  }
  let tt = Ve(), Tt = Ve(), je;
  function nt(m, b, E) {
    rt(m);
    const k = Tt.list();
    return k.length ? k.forEach(($) => $(m, b, E)) : (R.NODE_ENV !== "production" && O("uncaught error during route navigation:"), console.error(m)), Promise.reject(m);
  }
  function lr() {
    return je && c.value !== ce ? Promise.resolve() : new Promise((m, b) => {
      tt.add([m, b]);
    });
  }
  function rt(m) {
    return je || (je = !m, cr(), tt.list().forEach(([b, E]) => m ? E(m) : b()), tt.reset()), m;
  }
  function It(m, b, E, k) {
    const { scrollBehavior: $ } = e;
    if (!oe || !$)
      return Promise.resolve();
    const L = !E && zo(qt(m.fullPath, 0)) || (k || !E) && history.state && history.state.scroll || null;
    return Se().then(() => $(m, b, L)).then((V) => V && Wo(V)).catch((V) => nt(V, m, b));
  }
  const st = (m) => s.go(m);
  let ot;
  const Me = /* @__PURE__ */ new Set(), Dt = {
    currentRoute: c,
    listening: !0,
    addRoute: d,
    removeRoute: p,
    clearRoutes: t.clearRoutes,
    hasRoute: v,
    getRoutes: y,
    resolve: w,
    options: e,
    push: S,
    replace: C,
    go: st,
    back: () => st(-1),
    forward: () => st(1),
    beforeEach: o.add,
    beforeResolve: i.add,
    afterEach: a.add,
    onError: Tt.add,
    isReady: lr,
    install(m) {
      const b = this;
      m.component("RouterLink", bi), m.component("RouterView", Oi), m.config.globalProperties.$router = b, Object.defineProperty(m.config.globalProperties, "$route", {
        enumerable: !0,
        get: () => z(c)
      }), oe && // used for the initial navigation client side to avoid pushing
      // multiple times when the router is used in multiple apps
      !ot && c.value === ce && (ot = !0, S(s.location).catch(($) => {
        R.NODE_ENV !== "production" && O("Unexpected error when starting the router:", $);
      }));
      const E = {};
      for (const $ in ce)
        Object.defineProperty(E, $, {
          get: () => c.value[$],
          enumerable: !0
        });
      m.provide(Qe, b), m.provide(xt, kr(E)), m.provide(bt, c);
      const k = m.unmount;
      Me.add(m), m.unmount = function() {
        Me.delete(m), Me.size < 1 && (h = ce, ee && ee(), ee = null, c.value = ce, ot = !1, je = !1), k();
      }, R.NODE_ENV !== "production" && oe && Vi(m, b, t);
    }
  };
  function we(m) {
    return m.reduce((b, E) => b.then(() => Z(E)), Promise.resolve());
  }
  return Dt;
}
function Li(e, t) {
  const n = [], r = [], s = [], o = Math.max(t.matched.length, e.matched.length);
  for (let i = 0; i < o; i++) {
    const a = t.matched[i];
    a && (e.matched.find((h) => he(h, a)) ? r.push(a) : n.push(a));
    const c = e.matched[i];
    c && (t.matched.find((h) => he(h, c)) || s.push(c));
  }
  return [n, r, s];
}
function Fi() {
  return ae(Qe);
}
function Wi(e) {
  return ae(xt);
}
const sr = Symbol("BINDING_GETTER_KEY");
function Ui(e, t) {
  const n = Gi(e);
  return zi(e, n, t), Or(() => {
    n._release();
  }), U(sr, n), {
    bindingGetter: n
  };
}
function zi(e, t, n) {
  var s, o, i, a, c, h, u, l, f;
  const { id: r } = e;
  if (Hi(n.vforSetting, r, t), Ki(n.slotSetting, r, t), e.routerParam) {
    const d = F(r, e.routerParam), p = Wi(), y = j(() => p.params);
    t._registerBinding(d, y), U(d, y);
  }
  if (e.routerAct) {
    const d = F(r, e.routerAct), p = Fi();
    t._registerBinding(d, p), U(d, p);
  }
  (s = e.data) == null || s.forEach((d) => {
    const p = F(r, d.id);
    t._registerBinding(p, d.value), U(p, d.value);
  }), (o = e.jsFn) == null || o.forEach((d) => {
    const p = F(r, d.id), y = qi(d);
    t._registerBinding(p, y), U(p, y);
  }), (i = e.eRefs) == null || i.forEach((d) => {
    const p = F(r, d.id), y = ie(null);
    t._registerBinding(p, y), U(p, y);
  }), (a = e.refs) == null || a.forEach((d) => {
    const { id: p } = d, y = F(r, p), v = eo(d);
    t._registerBinding(y, v), U(y, v);
  }), (c = e.web_computed) == null || c.forEach((d) => {
    const p = F(r, d.id), y = no(d);
    t._registerBinding(p, y), U(p, y);
  }), (h = e.js_computed) == null || h.forEach((d) => {
    const p = F(r, d.id), y = ro(
      d,
      t
    );
    t._registerBinding(p, y), U(p, y);
  }), (u = e.vue_computed) == null || u.forEach((d) => {
    const p = F(r, d.id), y = to(
      d,
      t
    );
    t._registerBinding(p, y), U(p, y);
  }), oo({
    watchConfigs: e.py_watch || [],
    computedConfigs: e.web_computed || [],
    bindingGetter: t,
    sid: r
  }), (l = e.js_watch) == null || l.forEach((d) => {
    fo(d, t);
  }), (f = e.vue_watch) == null || f.forEach((d) => {
    uo(d, t);
  });
}
function Hi(e, t, n) {
  if (e != null && e.item) {
    const { id: r } = e.item, s = F(t, r), o = Ji(e.item, n);
    n._registerBinding(s, o), U(s, o);
  }
  if (e != null && e.index) {
    const { id: r, value: s } = e.index, o = F(t, r), i = W(s);
    n._registerBinding(o, i), U(o, i);
  }
  if (e != null && e.key) {
    const { id: r, value: s } = e.key, o = F(t, r), i = W(s);
    n._registerBinding(o, i), U(o, i);
  }
}
function Ki(e, t, n) {
  if (!e)
    return;
  const { id: r, value: s } = e, o = F(t, r), i = ie(s);
  n._registerBinding(o, i), U(o, i);
}
function Gi(e) {
  const { binds: t } = e, n = /* @__PURE__ */ new Map(), r = /* @__PURE__ */ new Map();
  let s = null, o = null;
  t == null || t.forEach((g, _) => {
    const { sid: S, id: C } = g, x = F(S, C);
    if (S !== e.id) {
      const I = ae(x);
      n.set(_, I);
    } else
      r.set(x, _);
  });
  function i(g) {
    const _ = a(g);
    return Gs(_, {
      paths: g.path,
      getBindableValueFn: c
    });
  }
  function a(g) {
    const _ = n.get(g.r);
    if (!_)
      throw new Error(`Binding not found: ${JSON.stringify(g)}`);
    return _;
  }
  function c(g) {
    return be(i(g));
  }
  function h(g) {
    const _ = n.get(g.r);
    if (!_)
      throw new Error(`Router binding not found: ${JSON.stringify(g)}`);
    return _;
  }
  function u(g, _) {
    if (kn(g)) {
      const S = a(g);
      if (g.path) {
        Tn(S.value, g.path, _, c);
        return;
      }
      S.value = _;
      return;
    }
    throw new Error(`Unsupported output binding: ${g}`);
  }
  function l(g) {
    if (g != null && g.item) {
      const { id: _, value: S, sourceInfo: C } = g.item;
      if (C) {
        const { index: Y, key: Z } = C;
        s && (s.value = Y), o && (o.value = Z);
      }
      const x = F(e.id, _), I = i({ r: d(x) });
      I.value = S;
    }
    if (g != null && g.index) {
      const { id: _, value: S } = g.index, C = F(e.id, _), x = i({ r: d(C) });
      x.value = S;
    }
    if (g != null && g.key) {
      const { id: _, value: S } = g.key, C = F(e.id, _), x = i({ r: d(C) });
      x.value = S;
    }
  }
  function f(g) {
    if (!g)
      return;
    const { id: _, value: S } = g, C = F(e.id, _), x = i({ r: d(C) });
    x.value = S;
  }
  function d(g) {
    return r.get(g);
  }
  function p(g, _) {
    const S = r.get(g);
    n.set(S, _);
  }
  function y() {
    n.clear(), r.clear();
  }
  function v(g) {
    return s = W(g), s;
  }
  function w(g) {
    return o = W(g), o;
  }
  return {
    getValue: c,
    getRef: i,
    updateValue: u,
    getBindIndex: d,
    updateVForInfo: l,
    updateSlotInfo: f,
    getRouter: h,
    initVForIndexRef: v,
    initVForKeyRef: w,
    _registerBinding: p,
    _release: y
  };
}
function F(e, t) {
  return `${e}-${t}`;
}
function qi(e) {
  const { immediately: t = !1, code: n } = e;
  let r = G(n);
  return t && (r = r()), ye(() => ({
    get() {
      return r;
    },
    set() {
      throw new Error("Cannot set value to js function");
    }
  }));
}
function Ka() {
  const { getRef: e, getRouter: t, getValue: n } = ae(sr);
  return {
    getRef: e,
    getRouter: t,
    getValue: n
  };
}
function Ji(e, t) {
  const { value: n, sourceInfo: r } = e;
  if (r) {
    const { source: s, type: o, index: i, key: a } = r, c = t.initVForIndexRef(i);
    return o === "array" ? ye(() => ({
      get() {
        return s.value[c.value];
      },
      set(h) {
        s.value[c.value] = h;
      }
    })) : ye(() => {
      const h = t.initVForKeyRef(a);
      return {
        get() {
          return s.value[h.value];
        },
        set(u) {
          s.value[h.value] = u;
        }
      };
    });
  }
  return W(n);
}
const or = X(Qi, {
  props: ["config", "vforSetting", "slotSetting"]
});
function Qi(e) {
  const { config: t, vforSetting: n, slotSetting: r } = e, { items: s } = t, { bindingGetter: o } = Ui(t, { vforSetting: n, slotSetting: r });
  return () => {
    if (o.updateVForInfo(e.vforSetting), o.updateSlotInfo(e.slotSetting), !s)
      return null;
    if (s.length === 1) {
      const i = s[0];
      return ve(i, { sid: t.id, bindingGetter: o });
    }
    return s == null ? void 0 : s.map(
      (i) => ve(i, { sid: t.id, bindingGetter: o })
    );
  };
}
function Yi(e, t) {
  const { state: n, isReady: r, isLoading: s } = Ts(async () => {
    let o = e;
    const i = t;
    if (!o && !i)
      throw new Error("Either config or configUrl must be provided");
    if (!o && i && (o = await (await fetch(i)).json()), !o)
      throw new Error("Failed to load config");
    return o;
  }, {});
  return { config: n, isReady: r, isLoading: s };
}
function Xi(e) {
  const t = W(!1), n = W("");
  function r(s, o) {
    let i;
    return o.component ? i = `Error captured from component:tag: ${o.component.tag} ; id: ${o.component.id} ` : i = "Error captured from app init", console.group(i), console.error("Component:", o.component), console.error("Error:", s), console.groupEnd(), e && (t.value = !0, n.value = `${i} ${s.message}`), !1;
  }
  return Nr(r), { hasError: t, errorMessage: n };
}
let kt;
function Zi(e) {
  if (e === "web" || e === "webview") {
    kt = ea;
    return;
  }
  if (e === "zero") {
    kt = ta;
    return;
  }
  throw new Error(`Unsupported mode: ${e}`);
}
function ea(e) {
  const { assetPath: t = "/assets/icons", icon: n = "" } = e, [r, s] = n.split(":");
  return {
    assetPath: t,
    svgName: `${r}.svg`
  };
}
function ta(e) {
  const { icon: t = "" } = e, [n] = t.split(":"), [r] = n.split(".");
  return {
    assetPath: "",
    svgName: r
  };
}
function na(e, t) {
  const n = j(() => {
    const r = e.value;
    if (!r)
      return null;
    const i = new DOMParser().parseFromString(r, "image/svg+xml").querySelector("svg");
    if (!i)
      throw new Error("Invalid svg string");
    const a = {};
    for (const f of i.attributes)
      a[f.name] = f.value;
    const { size: c, color: h, attrs: u } = t;
    h.value !== null && h.value !== void 0 && (i.removeAttribute("fill"), i.querySelectorAll("*").forEach((d) => {
      d.hasAttribute("fill") && d.setAttribute("fill", "currentColor");
    }), a.color = h.value), c.value !== null && c.value !== void 0 && (a.width = c.value.toString(), a.height = c.value.toString());
    const l = i.innerHTML;
    return {
      ...a,
      ...u,
      innerHTML: l
    };
  });
  return () => {
    if (!n.value)
      return null;
    const r = n.value;
    return q("svg", r);
  };
}
const ra = {
  class: "app-box insta-theme",
  "data-scaling": "100%"
}, sa = {
  key: 0,
  style: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
}, oa = {
  key: 0,
  style: { color: "red", "font-size": "1.2em", margin: "1rem", border: "1px dashed red", padding: "1rem" }
}, ia = /* @__PURE__ */ X({
  __name: "App",
  props: {
    config: {},
    meta: {},
    configUrl: {}
  },
  setup(e) {
    const t = e, { debug: n = !1 } = t.meta, { config: r, isLoading: s } = Yi(
      t.config,
      t.configUrl
    );
    K(r, (a) => {
      a.url && (Tr({
        mode: t.meta.mode,
        version: t.meta.version,
        queryPath: a.url.path,
        pathParams: a.url.params,
        webServerInfo: a.webInfo
      }), Qr(t.meta.mode)), Zi(t.meta.mode);
    });
    const { hasError: o, errorMessage: i } = Xi(n);
    return (a, c) => (fe(), Ee("div", ra, [
      z(s) ? (fe(), Ee("div", sa, c[0] || (c[0] = [
        gn("p", { style: { margin: "auto" } }, "Loading ...", -1)
      ]))) : (fe(), Ee("div", {
        key: 1,
        class: ut(["insta-main", z(r).class])
      }, [
        Pr(z(or), {
          config: z(r).scope
        }, null, 8, ["config"]),
        z(o) ? (fe(), Ee("div", oa, pn(z(i)), 1)) : ft("", !0)
      ], 2))
    ]));
  }
}), un = /* @__PURE__ */ new Map([
  [
    "size",
    {
      classes: "ist-r-size",
      handler: (e) => aa(e)
    }
  ],
  [
    "weight",
    {
      classes: "ist-r-weight",
      styleVar: "--weight",
      handler: (e) => e
    }
  ],
  [
    "text_align",
    {
      classes: "ist-r-ta",
      styleVar: "--ta",
      handler: (e) => e
    }
  ],
  [
    "trim",
    {
      classes: (e) => ca("ist-r", e)
    }
  ],
  [
    "truncate",
    {
      classes: "ist-r-truncate"
    }
  ],
  [
    "text_wrap",
    {
      classes: "ist-r-tw",
      handler: (e) => la(e)
    }
  ]
]);
function ir(e) {
  const t = {}, n = [], r = {};
  for (const [o, i] of Object.entries(e)) {
    if (i === void 0 || !un.has(o))
      continue;
    const a = typeof i == "object" ? i : { initial: i };
    for (const [c, h] of Object.entries(a)) {
      const { classes: u, styleVar: l, handler: f, propHandler: d } = un.get(o), p = c === "initial";
      if (u) {
        const y = typeof u == "function" ? u(h) : u, v = p ? y : `${c}:${y}`;
        n.push(v);
      }
      if (f) {
        const y = f(h);
        if (l) {
          const v = p ? l : `${l}-${c}`;
          t[v] = y;
        } else {
          if (!Array.isArray(y))
            throw new Error(`Invalid style value: ${y}`);
          y.forEach((v) => {
            for (const [w, g] of Object.entries(v))
              t[w] = g;
          });
        }
      }
      if (d) {
        const y = d(h);
        for (const [v, w] of Object.entries(y))
          r[v] = w;
      }
    }
  }
  return {
    classes: n.join(" "),
    style: t,
    props: r
  };
}
function aa(e) {
  const t = Number(e);
  if (isNaN(t))
    throw new Error(`Invalid font size value: ${e}`);
  return [
    { "--fs": `var(--font-size-${t})` },
    { "--lh": `var(--line-height-${t})` },
    { "--ls": `var(--letter-spacing-${t})` }
  ];
}
function ca(e, t) {
  return `${e}-lt-${t}`;
}
function la(e) {
  if (e === "wrap")
    return {
      "--ws": "normal"
    };
  if (e === "nowrap")
    return {
      "--ws": "nowrap"
    };
  if (e === "pretty")
    return [{ "--ws": "normal" }, { "--tw": "pretty" }];
  if (e === "balance")
    return [{ "--ws": "normal" }, { "--tw": "balance" }];
  throw new Error(`Invalid text wrap value: ${e}`);
}
const ua = "insta-Heading", fa = X(da, {
  props: [
    "as",
    "as_child",
    "size",
    "weight",
    "align",
    "trim",
    "truncate",
    "text_wrap",
    "innerText"
  ]
});
function da(e) {
  return () => {
    const { classes: t, style: n, props: r } = ir(e), s = de(
      { class: t, style: n, ...r },
      { class: ua }
    );
    return q(e.as || "h1", s, e.innerText);
  };
}
const ha = /* @__PURE__ */ X({
  __name: "_Teleport",
  props: {
    to: {},
    defer: { type: Boolean, default: !0 },
    disabled: { type: Boolean, default: !1 }
  },
  setup(e) {
    return (t, n) => (fe(), yn(Vr, {
      to: t.to,
      defer: t.defer,
      disabled: t.disabled
    }, [
      Cr(t.$slots, "default")
    ], 8, ["to", "defer", "disabled"]));
  }
}), pa = ["width", "height", "color"], ma = ["xlink:href"], ga = /* @__PURE__ */ X({
  __name: "Icon",
  props: {
    size: {},
    icon: {},
    color: {},
    assetPath: {},
    svgName: {},
    rawSvg: {},
    appMode: {}
  },
  setup(e) {
    const t = e, { assetPath: n, svgName: r } = kt(t), { appMode: s } = t, o = me(() => t.icon ? t.icon.split(":")[1] : ""), i = me(() => t.size || "1em"), a = me(() => t.color || "currentColor"), c = me(() => t.rawSvg || null), h = s === "zero" ? j(() => `#${r}-${o.value}`) : j(() => `${n}/${r}#${o.value}`), u = Ar(), l = na(c, {
      size: me(() => t.size),
      color: me(() => t.color),
      attrs: u
    });
    return (f, d) => (fe(), Ee($r, null, [
      o.value ? (fe(), Ee("svg", de({
        key: 0,
        width: i.value,
        height: i.value,
        color: a.value
      }, z(u)), [
        gn("use", { "xlink:href": z(h) }, null, 8, ma)
      ], 16, pa)) : ft("", !0),
      c.value ? (fe(), yn(z(l), { key: 1 })) : ft("", !0)
    ], 64));
  }
}), xe = /* @__PURE__ */ new Map([
  [
    "p",
    {
      classes: "ist-r-p",
      styleVar: "--p",
      handler: (e) => D("space", e)
    }
  ],
  [
    "px",
    {
      classes: "ist-r-px",
      styleVar: "--px",
      handler: (e) => D("space", e)
    }
  ],
  [
    "py",
    {
      classes: "ist-r-py",
      styleVar: "--py",
      handler: (e) => D("space", e)
    }
  ],
  [
    "pt",
    {
      classes: "ist-r-pt",
      styleVar: "--pt",
      handler: (e) => D("space", e)
    }
  ],
  [
    "pb",
    {
      classes: "ist-r-pb",
      styleVar: "--pb",
      handler: (e) => D("space", e)
    }
  ],
  [
    "pl",
    {
      classes: "ist-r-pl",
      styleVar: "--pl",
      handler: (e) => D("space", e)
    }
  ],
  [
    "pr",
    {
      classes: "ist-r-pr",
      styleVar: "--pr",
      handler: (e) => D("space", e)
    }
  ],
  [
    "width",
    {
      classes: "ist-r-w",
      styleVar: "--width",
      handler: (e) => e
    }
  ],
  [
    "height",
    {
      classes: "ist-r-h",
      styleVar: "--height",
      handler: (e) => e
    }
  ],
  [
    "min_width",
    {
      classes: "ist-r-min-w",
      styleVar: "--min_width",
      handler: (e) => e
    }
  ],
  [
    "min_height",
    {
      classes: "ist-r-min-h",
      styleVar: "--min_height",
      handler: (e) => e
    }
  ],
  [
    "max_width",
    {
      classes: "ist-r-max-w",
      styleVar: "--max_width",
      handler: (e) => e
    }
  ],
  [
    "max_height",
    {
      classes: "ist-r-max-h",
      styleVar: "--max_height",
      handler: (e) => e
    }
  ],
  [
    "position",
    {
      classes: "ist-r-position",
      styleVar: "--position",
      handler: (e) => e
    }
  ],
  [
    "inset",
    {
      classes: "ist-r-inset",
      styleVar: "--inset",
      handler: (e) => D("space", e)
    }
  ],
  [
    "top",
    {
      classes: "ist-r-top",
      styleVar: "--top",
      handler: (e) => D("space", e)
    }
  ],
  [
    "right",
    {
      classes: "ist-r-right",
      styleVar: "--right",
      handler: (e) => D("space", e)
    }
  ],
  [
    "bottom",
    {
      classes: "ist-r-bottom",
      styleVar: "--bottom",
      handler: (e) => D("space", e)
    }
  ],
  [
    "left",
    {
      classes: "ist-r-left",
      styleVar: "--left",
      handler: (e) => D("space", e)
    }
  ],
  [
    "overflow",
    {
      classes: "ist-r-overflow",
      styleVar: "--overflow",
      handler: (e) => e
    }
  ],
  [
    "overflow_x",
    {
      classes: "ist-r-ox",
      styleVar: "--overflow_x",
      handler: (e) => e
    }
  ],
  [
    "overflow_y",
    {
      classes: "ist-r-oy",
      styleVar: "--overflow_y",
      handler: (e) => e
    }
  ],
  [
    "flex_basis",
    {
      classes: "ist-r-fb",
      styleVar: "--flex_basis",
      handler: (e) => e
    }
  ],
  [
    "flex_shrink",
    {
      classes: "ist-r-fs",
      styleVar: "--flex_shrink",
      handler: (e) => e
    }
  ],
  [
    "flex_grow",
    {
      classes: "ist-r-fg",
      styleVar: "--flex_grow",
      handler: (e) => e
    }
  ],
  [
    "grid_area",
    {
      classes: "ist-r-ga",
      styleVar: "--grid_area",
      handler: (e) => e
    }
  ],
  [
    "grid_column",
    {
      classes: "ist-r-gc",
      styleVar: "--grid_column",
      handler: (e) => e
    }
  ],
  [
    "grid_column_start",
    {
      classes: "ist-r-gcs",
      styleVar: "--grid_column_start",
      handler: (e) => e
    }
  ],
  [
    "grid_column_end",
    {
      classes: "ist-r-gce",
      styleVar: "--grid_column_end",
      handler: (e) => e
    }
  ],
  [
    "grid_row",
    {
      classes: "ist-r-gr",
      styleVar: "--grid_row",
      handler: (e) => e
    }
  ],
  [
    "grid_row_start",
    {
      classes: "ist-r-grs",
      styleVar: "--grid_row_start",
      handler: (e) => e
    }
  ],
  [
    "grid_row_end",
    {
      classes: "ist-r-gre",
      styleVar: "--grid_row_end",
      handler: (e) => e
    }
  ],
  [
    "m",
    {
      classes: "ist-r-m",
      styleVar: "--m",
      handler: (e) => D("space", e)
    }
  ],
  [
    "mx",
    {
      classes: "ist-r-mx",
      styleVar: "--mx",
      handler: (e) => D("space", e)
    }
  ],
  [
    "my",
    {
      classes: "ist-r-my",
      styleVar: "--my",
      handler: (e) => D("space", e)
    }
  ],
  [
    "mt",
    {
      classes: "ist-r-mt",
      styleVar: "--mt",
      handler: (e) => D("space", e)
    }
  ],
  [
    "mr",
    {
      classes: "ist-r-mr",
      styleVar: "--mr",
      handler: (e) => D("space", e)
    }
  ],
  [
    "mb",
    {
      classes: "ist-r-mb",
      styleVar: "--mb",
      handler: (e) => D("space", e)
    }
  ],
  [
    "ml",
    {
      classes: "ist-r-ml",
      styleVar: "--ml",
      handler: (e) => D("space", e)
    }
  ],
  [
    "display",
    {
      classes: "ist-r-display",
      styleVar: "--display",
      handler: (e) => e
    }
  ],
  [
    "direction",
    {
      classes: "ist-r-fd",
      styleVar: "--direction",
      handler: (e) => e
    }
  ],
  [
    "align",
    {
      classes: "ist-r-ai",
      styleVar: "--align",
      handler: (e) => e
    }
  ],
  [
    "justify",
    {
      classes: "ist-r-jc",
      styleVar: "--justify",
      handler: (e) => e
    }
  ],
  [
    "wrap",
    {
      classes: "ist-r-wrap",
      styleVar: "--wrap",
      handler: (e) => e
    }
  ],
  [
    "gap",
    {
      classes: "ist-r-gap",
      styleVar: "--gap",
      handler: (e) => D("space", e)
    }
  ],
  [
    "gap_x",
    {
      classes: "ist-r-cg",
      styleVar: "--gap_x",
      handler: (e) => D("space", e)
    }
  ],
  [
    "gap_y",
    {
      classes: "ist-r-rg",
      styleVar: "--gap_y",
      handler: (e) => D("space", e)
    }
  ],
  [
    "areas",
    {
      classes: "ist-r-gta",
      styleVar: "--areas",
      handler: (e) => e
    }
  ],
  [
    "columns",
    {
      classes: "ist-r-gtc",
      styleVar: "--columns",
      handler: (e) => fn(e)
    }
  ],
  [
    "rows",
    {
      classes: "ist-r-gtr",
      styleVar: "--rows",
      handler: (e) => fn(e)
    }
  ],
  [
    "flow",
    {
      classes: "ist-r-gaf",
      styleVar: "--flow",
      handler: (e) => e
    }
  ],
  [
    "ctn_size",
    {
      classes: "ist-r-ctn_size",
      styleVar: "--ctn_size",
      handler: (e) => D("container", e)
    }
  ]
]);
function Ye(e) {
  e.length > 1 && console.warn("Only accept one child element when as_child is true");
}
function Xe(e) {
  return Object.fromEntries(
    Object.entries(e).filter(([t, n]) => n !== void 0)
  );
}
function Ze(e, t) {
  const n = {}, r = [], s = new Set(t || []), o = {
    style: {},
    class: []
  };
  for (const [a, c] of Object.entries(e)) {
    if (!xe.has(a))
      continue;
    const h = typeof c == "object" ? c : { initial: c };
    for (const [u, l] of Object.entries(h)) {
      const { classes: f, styleVar: d, handler: p } = xe.get(a), y = u === "initial", v = y ? f : `${u}:${f}`, w = y ? d : `${d}-${u}`, g = p(l);
      if (s.has(a)) {
        o.class.push(v), o.style[w] = g;
        continue;
      }
      r.push(v), n[w] = g;
    }
  }
  return {
    classes: r.join(" "),
    style: n,
    excludeReslut: o
  };
}
function D(e, t) {
  const n = Number(t);
  if (isNaN(n))
    return t;
  {
    const r = n < 0 ? -1 : 1;
    return `calc(var(--${e}-${n}) * ${r})`;
  }
}
function fn(e) {
  const t = Number(e);
  return isNaN(t) ? e : `repeat(${t}, 1fr)`;
}
const et = [
  "p",
  "px",
  "py",
  "pt",
  "pb",
  "pl",
  "pr",
  "width",
  "height",
  "min_width",
  "min_height",
  "max_width",
  "max_height",
  "position",
  "inset",
  "top",
  "right",
  "bottom",
  "left",
  "overflow",
  "overflow_x",
  "overflow_y",
  "flex_basis",
  "flex_shrink",
  "flex_grow",
  "grid_area",
  "grid_column",
  "grid_column_start",
  "grid_column_end",
  "grid_row",
  "grid_row_start",
  "grid_row_end",
  "m",
  "mx",
  "my",
  "mt",
  "mr",
  "mb",
  "ml"
], ya = [
  "as",
  "as_child",
  "display",
  "align",
  "justify",
  "wrap",
  "gap",
  "gap_x",
  "gap_y"
].concat(et), va = ["direction"].concat(ya), wa = [
  "as_child",
  "size",
  "display",
  "align",
  "ctn_size"
].concat(et), _a = ["as", "as_child", "display"].concat(et), Ea = [
  "as",
  "as_child",
  "display",
  "areas",
  "columns",
  "rows",
  "flow",
  "align",
  "justify",
  "gap",
  "gap_x",
  "gap_y"
].concat(et), ba = "insta-Box", Sa = X(ka, {
  props: _a
});
function ka(e) {
  const t = Ke();
  return () => {
    var a;
    const n = Xe(e), { classes: r, style: s } = Ze(n), o = de(
      { class: r, style: s },
      { class: ba }
    ), i = (a = t.default) == null ? void 0 : a.call(t);
    return e.as_child && i && i.length > 0 ? (Ye(i), re(i[0], o)) : q(e.as || "div", o, i);
  };
}
const Ra = "insta-Flex", Oa = {
  gap: "2"
}, Na = X(Pa, {
  props: va
});
function Pa(e) {
  const t = Ke();
  return () => {
    var a;
    const n = { ...Oa, ...Xe(e) }, { classes: r, style: s } = Ze(n), o = de(
      { class: r, style: s },
      { class: Ra }
    ), i = (a = t.default) == null ? void 0 : a.call(t);
    return e.as_child && i && i.length > 0 ? (Ye(i), re(i[0], o)) : q(e.as || "div", o, i);
  };
}
const Va = "insta-Grid", Ca = {
  gap: "2"
}, Aa = X($a, {
  props: Ea
});
function $a(e) {
  const t = Ke();
  return () => {
    var c;
    const n = { ...Ca, ...Xe(e) }, r = Ze(n), [s, o] = xa(r.classes, r.style), i = de(
      { class: s, style: o },
      { class: Va }
    ), a = (c = t.default) == null ? void 0 : c.call(t);
    return e.as_child && a && a.length > 0 ? (Ye(a), re(a[0], i)) : q(e.as || "div", i, a);
  };
}
function xa(e, t) {
  const n = xe.get("areas").styleVar, r = xe.get("columns").styleVar, s = n in t, o = r in t;
  if (!s || o)
    return [e, t];
  const i = Ta(t[n]);
  if (i) {
    const { classes: a, styleVar: c } = xe.get("columns");
    e = `${e} ${a}`, t[c] = i;
  }
  return [e, t];
}
function Ta(e) {
  if (typeof e != "string") return null;
  const t = [...e.matchAll(/"([^"]+)"/g)].map((i) => i[1]);
  if (t.length === 0) return null;
  const s = t[0].trim().split(/\s+/).length;
  return t.every(
    (i) => i.trim().split(/\s+/).length === s
  ) ? `repeat(${s}, 1fr)` : null;
}
const Ia = "insta-Container", Da = X(ja, {
  props: wa
});
function ja(e) {
  const t = Ke();
  return () => {
    var h;
    const n = Xe(e), { classes: r, style: s, excludeReslut: o } = Ze(n, [
      "ctn_size"
    ]), i = de(
      { class: r, style: s },
      { class: Ia }
    ), a = (h = t.default) == null ? void 0 : h.call(t);
    if (e.as_child && a && a.length > 0)
      return Ye(a), re(a[0], i);
    const c = q(
      "div",
      de({ class: "insta-ContainerInner" }, o),
      a
    );
    return q("div", i, c);
  };
}
const Ma = "insta-Text", Ba = X(La, {
  props: [
    "as",
    "as_child",
    "size",
    "weight",
    "align",
    "trim",
    "truncate",
    "text_wrap",
    "innerText"
  ]
});
function La(e) {
  return () => {
    const { classes: t, style: n, props: r } = ir(e), s = de(
      { class: t, style: n, ...r },
      { class: Ma }
    );
    return q(e.as || "span", s, e.innerText);
  };
}
function Fa(e, t) {
  const { mode: n = "hash" } = t.router, r = n === "hash" ? Jo() : n === "memory" ? qo() : Gn();
  e.use(
    Bi({
      history: r,
      routes: Wa(t)
    })
  );
}
function Wa(e) {
  if (!e.router)
    throw new Error("Router config is not provided.");
  const { routes: t = [], kAlive: n = !1 } = e.router;
  return t.map(
    (s) => ar(s, n)
  );
}
function ar(e, t) {
  const {
    server: n = !1,
    vueItem: r,
    scope: s,
    children: o
  } = e, i = () => {
    if (n)
      throw new Error("Server-side rendering is not supported yet.");
    return Promise.resolve(Ua(e, t));
  }, a = o == null ? void 0 : o.map(
    (h) => ar(h, t)
  ), c = {
    ...r,
    children: a,
    component: i
  };
  return s || delete c.component, a || delete c.children, c;
}
function Ua(e, t) {
  const { scope: n } = e;
  if (!n)
    throw new Error("Scope is not provided.");
  const r = re(Te(n), { key: n.id });
  return t ? q(xr, null, () => r) : r;
}
function Ga(e, t) {
  e.component("insta-ui", ia), e.component("teleport", ha), e.component("icon", ga), e.component("heading", fa), e.component("box", Sa), e.component("flex", Na), e.component("grid", Aa), e.component("container", Da), e.component("ui-text", Ba), t.router && Fa(e, t);
}
export {
  Ue as convertDynamicProperties,
  Ga as install,
  Ka as useBindingGetter
};
//# sourceMappingURL=insta-ui.js.map

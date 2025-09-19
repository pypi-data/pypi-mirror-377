const {
  SvelteComponent: Ae,
  append_hydration: ze,
  attr: Me,
  children: Oe,
  claim_svg_element: Ue,
  detach: Ve,
  init: Fe,
  insert_hydration: Ge,
  noop: He,
  safe_not_equal: Je,
  svg_element: Ke
} = window.__gradio__svelte__internal;
function I() {
}
function R(t, e) {
  return t != t ? e == e : t !== e || t && typeof t == "object" || typeof t == "function";
}
const w = [];
function A(t, e = I) {
  let i;
  const n = /* @__PURE__ */ new Set();
  function l(o) {
    if (R(t, o) && (t = o, i)) {
      const d = !w.length;
      for (const m of n)
        m[1](), w.push(m, t);
      if (d) {
        for (let m = 0; m < w.length; m += 2)
          w[m][0](w[m + 1]);
        w.length = 0;
      }
    }
  }
  function s(o) {
    l(o(t));
  }
  function _(o, d = I) {
    const m = [o, d];
    return n.add(m), n.size === 1 && (i = e(l, s) || I), o(t), () => {
      n.delete(m), n.size === 0 && i && (i(), i = null);
    };
  }
  return { set: l, update: s, subscribe: _ };
}
const {
  SvelteComponent: Le,
  append_hydration: Pe,
  attr: Qe,
  binding_callbacks: Re,
  check_outros: We,
  children: Xe,
  claim_component: Ye,
  claim_element: Ze,
  claim_space: xe,
  claim_text: et,
  component_subscribe: tt,
  create_component: nt,
  create_slot: lt,
  destroy_component: it,
  destroy_each: st,
  detach: _t,
  element: ot,
  empty: at,
  ensure_array_like: ct,
  get_all_dirty_from_scope: rt,
  get_slot_changes: dt,
  group_outros: ut,
  init: ft,
  insert_hydration: mt,
  listen: bt,
  mount_component: ht,
  run_all: pt,
  safe_not_equal: gt,
  set_data: vt,
  set_store_value: kt,
  set_style: yt,
  space: wt,
  stop_propagation: $t,
  text: qt,
  toggle_class: Ct,
  transition_in: St,
  transition_out: Et,
  update_slot_base: Tt
} = window.__gradio__svelte__internal, { setContext: Dt, createEventDispatcher: It, tick: Bt, onMount: Nt } = window.__gradio__svelte__internal, W = {}, {
  SvelteComponent: jt,
  add_flush_callback: At,
  bind: zt,
  binding_callbacks: Mt,
  claim_component: Ot,
  create_component: Ut,
  create_slot: Vt,
  destroy_component: Ft,
  get_all_dirty_from_scope: Gt,
  get_slot_changes: Ht,
  init: Jt,
  mount_component: Kt,
  safe_not_equal: Lt,
  transition_in: Pt,
  transition_out: Qt,
  update_slot_base: Rt
} = window.__gradio__svelte__internal, { createEventDispatcher: Wt } = window.__gradio__svelte__internal, {
  SvelteComponent: X,
  append_hydration: q,
  attr: b,
  children: E,
  claim_element: T,
  claim_space: B,
  claim_text: H,
  component_subscribe: z,
  create_slot: Y,
  destroy_block: Z,
  detach: g,
  element: D,
  empty: $,
  ensure_array_like: M,
  get_all_dirty_from_scope: x,
  get_slot_changes: ee,
  init: te,
  insert_hydration: C,
  listen: ne,
  safe_not_equal: le,
  set_data: J,
  set_store_value: O,
  space: N,
  text: K,
  toggle_class: U,
  transition_in: ie,
  transition_out: se,
  update_keyed_each: _e,
  update_slot_base: oe
} = window.__gradio__svelte__internal, { setContext: ae, createEventDispatcher: ce } = window.__gradio__svelte__internal;
function V(t, e, i) {
  const n = t.slice();
  return n[14] = e[i], n[16] = i, n;
}
function F(t) {
  let e;
  function i(s, _) {
    return (
      /*t*/
      s[14].id === /*$selected_tab*/
      s[4] ? de : re
    );
  }
  let n = i(t), l = n(t);
  return {
    c() {
      l.c(), e = $();
    },
    l(s) {
      l.l(s), e = $();
    },
    m(s, _) {
      l.m(s, _), C(s, e, _);
    },
    p(s, _) {
      n === (n = i(s)) && l ? l.p(s, _) : (l.d(1), l = n(s), l && (l.c(), l.m(e.parentNode, e)));
    },
    d(s) {
      s && g(e), l.d(s);
    }
  };
}
function re(t) {
  let e, i = (
    /*t*/
    t[14].name + ""
  ), n, l, s, _, o, d, m, h;
  function u() {
    return (
      /*click_handler*/
      t[12](
        /*t*/
        t[14],
        /*i*/
        t[16]
      )
    );
  }
  return {
    c() {
      e = D("button"), n = K(i), l = N(), this.h();
    },
    l(a) {
      e = T(a, "BUTTON", {
        role: !0,
        "aria-selected": !0,
        "aria-controls": !0,
        "aria-disabled": !0,
        id: !0,
        class: !0
      });
      var c = E(e);
      n = H(c, i), l = B(c), c.forEach(g), this.h();
    },
    h() {
      b(e, "role", "tab"), b(e, "aria-selected", !1), b(e, "aria-controls", s = /*t*/
      t[14].elem_id), e.disabled = _ = !/*t*/
      t[14].interactive, b(e, "aria-disabled", o = !/*t*/
      t[14].interactive), b(e, "id", d = /*t*/
      t[14].elem_id ? (
        /*t*/
        t[14].elem_id + "-button"
      ) : null), b(e, "class", "svelte-1t1824p");
    },
    m(a, c) {
      C(a, e, c), q(e, n), q(e, l), m || (h = ne(e, "click", u), m = !0);
    },
    p(a, c) {
      t = a, c & /*tabs*/
      8 && i !== (i = /*t*/
      t[14].name + "") && J(n, i), c & /*tabs*/
      8 && s !== (s = /*t*/
      t[14].elem_id) && b(e, "aria-controls", s), c & /*tabs*/
      8 && _ !== (_ = !/*t*/
      t[14].interactive) && (e.disabled = _), c & /*tabs*/
      8 && o !== (o = !/*t*/
      t[14].interactive) && b(e, "aria-disabled", o), c & /*tabs*/
      8 && d !== (d = /*t*/
      t[14].elem_id ? (
        /*t*/
        t[14].elem_id + "-button"
      ) : null) && b(e, "id", d);
    },
    d(a) {
      a && g(e), m = !1, h();
    }
  };
}
function de(t) {
  let e, i = (
    /*t*/
    t[14].name + ""
  ), n, l, s, _;
  return {
    c() {
      e = D("button"), n = K(i), l = N(), this.h();
    },
    l(o) {
      e = T(o, "BUTTON", {
        role: !0,
        class: !0,
        "aria-selected": !0,
        "aria-controls": !0,
        id: !0
      });
      var d = E(e);
      n = H(d, i), l = B(d), d.forEach(g), this.h();
    },
    h() {
      b(e, "role", "tab"), b(e, "class", "selected svelte-1t1824p"), b(e, "aria-selected", !0), b(e, "aria-controls", s = /*t*/
      t[14].elem_id), b(e, "id", _ = /*t*/
      t[14].elem_id ? (
        /*t*/
        t[14].elem_id + "-button"
      ) : null);
    },
    m(o, d) {
      C(o, e, d), q(e, n), q(e, l);
    },
    p(o, d) {
      d & /*tabs*/
      8 && i !== (i = /*t*/
      o[14].name + "") && J(n, i), d & /*tabs*/
      8 && s !== (s = /*t*/
      o[14].elem_id) && b(e, "aria-controls", s), d & /*tabs*/
      8 && _ !== (_ = /*t*/
      o[14].elem_id ? (
        /*t*/
        o[14].elem_id + "-button"
      ) : null) && b(e, "id", _);
    },
    d(o) {
      o && g(e);
    }
  };
}
function G(t, e) {
  let i, n, l = (
    /*t*/
    e[14].visible && F(e)
  );
  return {
    key: t,
    first: null,
    c() {
      i = $(), l && l.c(), n = $(), this.h();
    },
    l(s) {
      i = $(), l && l.l(s), n = $(), this.h();
    },
    h() {
      this.first = i;
    },
    m(s, _) {
      C(s, i, _), l && l.m(s, _), C(s, n, _);
    },
    p(s, _) {
      e = s, /*t*/
      e[14].visible ? l ? l.p(e, _) : (l = F(e), l.c(), l.m(n.parentNode, n)) : l && (l.d(1), l = null);
    },
    d(s) {
      s && (g(i), g(n)), l && l.d(s);
    }
  };
}
function ue(t) {
  let e, i, n = [], l = /* @__PURE__ */ new Map(), s, _, o, d = M(
    /*tabs*/
    t[3]
  );
  const m = (a) => (
    /*t*/
    a[14].id
  );
  for (let a = 0; a < d.length; a += 1) {
    let c = V(t, d, a), f = m(c);
    l.set(f, n[a] = G(f, c));
  }
  const h = (
    /*#slots*/
    t[11].default
  ), u = Y(
    h,
    t,
    /*$$scope*/
    t[10],
    null
  );
  return {
    c() {
      e = D("div"), i = D("div");
      for (let a = 0; a < n.length; a += 1)
        n[a].c();
      s = N(), u && u.c(), this.h();
    },
    l(a) {
      e = T(a, "DIV", { class: !0, id: !0 });
      var c = E(e);
      i = T(c, "DIV", { class: !0, role: !0 });
      var f = E(i);
      for (let y = 0; y < n.length; y += 1)
        n[y].l(f);
      f.forEach(g), s = B(c), u && u.l(c), c.forEach(g), this.h();
    },
    h() {
      b(i, "class", "tab-nav scroll-hide svelte-1t1824p"), b(i, "role", "tablist"), b(e, "class", _ = "tabs " + /*elem_classes*/
      t[2].join(" ") + " svelte-1t1824p"), b(
        e,
        "id",
        /*elem_id*/
        t[1]
      ), U(e, "hide", !/*visible*/
      t[0]);
    },
    m(a, c) {
      C(a, e, c), q(e, i);
      for (let f = 0; f < n.length; f += 1)
        n[f] && n[f].m(i, null);
      q(e, s), u && u.m(e, null), o = !0;
    },
    p(a, [c]) {
      c & /*tabs, $selected_tab, change_tab, dispatch*/
      408 && (d = M(
        /*tabs*/
        a[3]
      ), n = _e(n, c, m, 1, a, d, l, i, Z, G, null, V)), u && u.p && (!o || c & /*$$scope*/
      1024) && oe(
        u,
        h,
        a,
        /*$$scope*/
        a[10],
        o ? ee(
          h,
          /*$$scope*/
          a[10],
          c,
          null
        ) : x(
          /*$$scope*/
          a[10]
        ),
        null
      ), (!o || c & /*elem_classes*/
      4 && _ !== (_ = "tabs " + /*elem_classes*/
      a[2].join(" ") + " svelte-1t1824p")) && b(e, "class", _), (!o || c & /*elem_id*/
      2) && b(
        e,
        "id",
        /*elem_id*/
        a[1]
      ), (!o || c & /*elem_classes, visible*/
      5) && U(e, "hide", !/*visible*/
      a[0]);
    },
    i(a) {
      o || (ie(u, a), o = !0);
    },
    o(a) {
      se(u, a), o = !1;
    },
    d(a) {
      a && g(e);
      for (let c = 0; c < n.length; c += 1)
        n[c].d();
      u && u.d(a);
    }
  };
}
const fe = W;
function me(t, e, i) {
  let n, l, { $$slots: s = {}, $$scope: _ } = e, { visible: o = !0 } = e, { elem_id: d = "id" } = e, { elem_classes: m = [] } = e, { selected: h } = e, u = [];
  const a = A(!1);
  z(t, a, (r) => i(4, l = r));
  const c = A(0);
  z(t, c, (r) => i(13, n = r));
  const f = ce();
  ae(fe, {
    register_tab: (r) => {
      let p;
      return u.find((k) => k.id === r.id) ? (p = u.findIndex((k) => k.id === r.id), i(3, u[p] = { ...u[p], ...r }, u)) : (u.push({
        name: r.name,
        id: r.id,
        elem_id: r.elem_id,
        visible: r.visible,
        interactive: r.interactive
      }), p = u.length - 1), a.update((k) => {
        if (k === !1 && r.visible && r.interactive)
          return r.id;
        let S = u.find((j) => j.visible && j.interactive);
        return S ? S.id : k;
      }), i(3, u), p;
    },
    unregister_tab: (r) => {
      const p = u.findIndex((v) => v.id === r.id);
      u.splice(p, 1), a.update((v) => {
        var k, S;
        return v === r.id ? ((k = u[p]) == null ? void 0 : k.id) || ((S = u[u.length - 1]) == null ? void 0 : S.id) : v;
      });
    },
    selected_tab: a,
    selected_tab_index: c
  });
  function y(r) {
    const p = u.find((v) => v.id === r);
    p && p.interactive && p.visible ? (i(9, h = r), O(a, l = r, l), O(c, n = u.findIndex((v) => v.id === r), n), f("change")) : console.warn("Attempted to select a non-interactive or hidden tab.");
  }
  const Q = (r, p) => {
    y(r.id), f("select", { value: r.name, index: p });
  };
  return t.$$set = (r) => {
    "visible" in r && i(0, o = r.visible), "elem_id" in r && i(1, d = r.elem_id), "elem_classes" in r && i(2, m = r.elem_classes), "selected" in r && i(9, h = r.selected), "$$scope" in r && i(10, _ = r.$$scope);
  }, t.$$.update = () => {
    t.$$.dirty & /*tabs, selected*/
    520 && h !== null && y(h);
  }, [
    o,
    d,
    m,
    u,
    l,
    a,
    c,
    f,
    y,
    h,
    _,
    s,
    Q
  ];
}
class be extends X {
  constructor(e) {
    super(), te(this, e, me, ue, le, {
      visible: 0,
      elem_id: 1,
      elem_classes: 2,
      selected: 9
    });
  }
}
const {
  SvelteComponent: he,
  add_flush_callback: pe,
  bind: ge,
  binding_callbacks: ve,
  claim_component: ke,
  create_component: ye,
  create_slot: we,
  destroy_component: $e,
  get_all_dirty_from_scope: qe,
  get_slot_changes: Ce,
  init: Se,
  mount_component: Ee,
  safe_not_equal: Te,
  transition_in: L,
  transition_out: P,
  update_slot_base: De
} = window.__gradio__svelte__internal, { createEventDispatcher: Ie } = window.__gradio__svelte__internal;
function Be(t) {
  let e;
  const i = (
    /*#slots*/
    t[5].default
  ), n = we(
    i,
    t,
    /*$$scope*/
    t[9],
    null
  );
  return {
    c() {
      n && n.c();
    },
    l(l) {
      n && n.l(l);
    },
    m(l, s) {
      n && n.m(l, s), e = !0;
    },
    p(l, s) {
      n && n.p && (!e || s & /*$$scope*/
      512) && De(
        n,
        i,
        l,
        /*$$scope*/
        l[9],
        e ? Ce(
          i,
          /*$$scope*/
          l[9],
          s,
          null
        ) : qe(
          /*$$scope*/
          l[9]
        ),
        null
      );
    },
    i(l) {
      e || (L(n, l), e = !0);
    },
    o(l) {
      P(n, l), e = !1;
    },
    d(l) {
      n && n.d(l);
    }
  };
}
function Ne(t) {
  let e, i, n;
  function l(_) {
    t[6](_);
  }
  let s = {
    visible: (
      /*visible*/
      t[1]
    ),
    elem_id: (
      /*elem_id*/
      t[2]
    ),
    elem_classes: (
      /*elem_classes*/
      t[3]
    ),
    $$slots: { default: [Be] },
    $$scope: { ctx: t }
  };
  return (
    /*selected*/
    t[0] !== void 0 && (s.selected = /*selected*/
    t[0]), e = new be({ props: s }), ve.push(() => ge(e, "selected", l)), e.$on(
      "change",
      /*change_handler*/
      t[7]
    ), e.$on(
      "select",
      /*select_handler*/
      t[8]
    ), {
      c() {
        ye(e.$$.fragment);
      },
      l(_) {
        ke(e.$$.fragment, _);
      },
      m(_, o) {
        Ee(e, _, o), n = !0;
      },
      p(_, [o]) {
        const d = {};
        o & /*visible*/
        2 && (d.visible = /*visible*/
        _[1]), o & /*elem_id*/
        4 && (d.elem_id = /*elem_id*/
        _[2]), o & /*elem_classes*/
        8 && (d.elem_classes = /*elem_classes*/
        _[3]), o & /*$$scope*/
        512 && (d.$$scope = { dirty: o, ctx: _ }), !i && o & /*selected*/
        1 && (i = !0, d.selected = /*selected*/
        _[0], pe(() => i = !1)), e.$set(d);
      },
      i(_) {
        n || (L(e.$$.fragment, _), n = !0);
      },
      o(_) {
        P(e.$$.fragment, _), n = !1;
      },
      d(_) {
        $e(e, _);
      }
    }
  );
}
function je(t, e, i) {
  let { $$slots: n = {}, $$scope: l } = e;
  const s = Ie();
  let { visible: _ = !0 } = e, { elem_id: o = "" } = e, { elem_classes: d = [] } = e, { selected: m } = e, { gradio: h } = e;
  function u(f) {
    m = f, i(0, m);
  }
  const a = () => h.dispatch("change"), c = (f) => h.dispatch("select", f.detail);
  return t.$$set = (f) => {
    "visible" in f && i(1, _ = f.visible), "elem_id" in f && i(2, o = f.elem_id), "elem_classes" in f && i(3, d = f.elem_classes), "selected" in f && i(0, m = f.selected), "gradio" in f && i(4, h = f.gradio), "$$scope" in f && i(9, l = f.$$scope);
  }, t.$$.update = () => {
    t.$$.dirty & /*selected*/
    1 && s("prop_change", { selected: m });
  }, [
    m,
    _,
    o,
    d,
    h,
    n,
    u,
    a,
    c,
    l
  ];
}
class Xt extends he {
  constructor(e) {
    super(), Se(this, e, je, Ne, Te, {
      visible: 1,
      elem_id: 2,
      elem_classes: 3,
      selected: 0,
      gradio: 4
    });
  }
}
export {
  fe as TABS,
  Xt as default
};

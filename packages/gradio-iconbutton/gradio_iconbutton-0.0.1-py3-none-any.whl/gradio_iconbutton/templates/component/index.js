var O = (l) => {
  throw TypeError(l);
};
var R = (l, e, n) => e.has(l) || O("Cannot " + n);
var w = (l, e, n) => (R(l, e, "read from private field"), n ? n.call(l) : e.get(l)), E = (l, e, n) => e.has(l) ? O("Cannot add the same private member more than once") : e instanceof WeakSet ? e.add(l) : e.set(l, n), G = (l, e, n, i) => (R(l, e, "write to private field"), i ? i.call(l, n) : e.set(l, n), n);
new Intl.Collator(0, { numeric: 1 }).compare;
typeof process < "u" && process.versions && process.versions.node;
var b;
class je extends TransformStream {
  /** Constructs a new instance. */
  constructor(n = { allowCR: !1 }) {
    super({
      transform: (i, t) => {
        for (i = w(this, b) + i; ; ) {
          const s = i.indexOf(`
`), o = n.allowCR ? i.indexOf("\r") : -1;
          if (o !== -1 && o !== i.length - 1 && (s === -1 || s - 1 > o)) {
            t.enqueue(i.slice(0, o)), i = i.slice(o + 1);
            continue;
          }
          if (s === -1)
            break;
          const a = i[s - 1] === "\r" ? s - 1 : s;
          t.enqueue(i.slice(0, a)), i = i.slice(s + 1);
        }
        G(this, b, i);
      },
      flush: (i) => {
        if (w(this, b) === "")
          return;
        const t = n.allowCR && w(this, b).endsWith("\r") ? w(this, b).slice(0, -1) : w(this, b);
        i.enqueue(t);
      }
    });
    E(this, b, "");
  }
}
b = new WeakMap();
const {
  SvelteComponent: Q,
  append_hydration: U,
  attr: d,
  bubble: V,
  check_outros: X,
  children: W,
  claim_element: B,
  claim_space: D,
  create_slot: F,
  detach: g,
  element: T,
  empty: M,
  get_all_dirty_from_scope: H,
  get_slot_changes: J,
  group_outros: Y,
  init: Z,
  insert_hydration: q,
  listen: y,
  safe_not_equal: p,
  set_style: h,
  space: K,
  src_url_equal: C,
  toggle_class: v,
  transition_in: I,
  transition_out: S,
  update_slot_base: P
} = window.__gradio__svelte__internal;
function x(l) {
  let e, n, i, t, s, o, a = (
    /*icon*/
    l[7] && N(l)
  );
  const f = (
    /*#slots*/
    l[12].default
  ), u = F(
    f,
    l,
    /*$$scope*/
    l[11],
    null
  );
  return {
    c() {
      e = T("button"), a && a.c(), n = K(), u && u.c(), this.h();
    },
    l(_) {
      e = B(_, "BUTTON", { class: !0, id: !0 });
      var m = W(e);
      a && a.l(m), n = D(m), u && u.l(m), m.forEach(g), this.h();
    },
    h() {
      d(e, "class", i = /*size*/
      l[4] + " " + /*variant*/
      l[3] + " " + /*elem_classes*/
      l[1].join(" ") + " svelte-1j6e1i7"), d(
        e,
        "id",
        /*elem_id*/
        l[0]
      ), e.disabled = /*disabled*/
      l[8], v(e, "hidden", !/*visible*/
      l[2]), h(
        e,
        "flex-grow",
        /*scale*/
        l[9]
      ), h(
        e,
        "width",
        /*scale*/
        l[9] === 0 ? "fit-content" : null
      );
    },
    m(_, m) {
      q(_, e, m), a && a.m(e, null), U(e, n), u && u.m(e, null), t = !0, s || (o = y(
        e,
        "click",
        /*click_handler*/
        l[13]
      ), s = !0);
    },
    p(_, m) {
      /*icon*/
      _[7] ? a ? a.p(_, m) : (a = N(_), a.c(), a.m(e, n)) : a && (a.d(1), a = null), u && u.p && (!t || m & /*$$scope*/
      2048) && P(
        u,
        f,
        _,
        /*$$scope*/
        _[11],
        t ? J(
          f,
          /*$$scope*/
          _[11],
          m,
          null
        ) : H(
          /*$$scope*/
          _[11]
        ),
        null
      ), (!t || m & /*size, variant, elem_classes*/
      26 && i !== (i = /*size*/
      _[4] + " " + /*variant*/
      _[3] + " " + /*elem_classes*/
      _[1].join(" ") + " svelte-1j6e1i7")) && d(e, "class", i), (!t || m & /*elem_id*/
      1) && d(
        e,
        "id",
        /*elem_id*/
        _[0]
      ), (!t || m & /*disabled*/
      256) && (e.disabled = /*disabled*/
      _[8]), (!t || m & /*size, variant, elem_classes, visible*/
      30) && v(e, "hidden", !/*visible*/
      _[2]), m & /*scale*/
      512 && h(
        e,
        "flex-grow",
        /*scale*/
        _[9]
      ), m & /*scale*/
      512 && h(
        e,
        "width",
        /*scale*/
        _[9] === 0 ? "fit-content" : null
      );
    },
    i(_) {
      t || (I(u, _), t = !0);
    },
    o(_) {
      S(u, _), t = !1;
    },
    d(_) {
      _ && g(e), a && a.d(), u && u.d(_), s = !1, o();
    }
  };
}
function $(l) {
  let e, n, i, t, s = (
    /*icon*/
    l[7] && A(l)
  );
  const o = (
    /*#slots*/
    l[12].default
  ), a = F(
    o,
    l,
    /*$$scope*/
    l[11],
    null
  );
  return {
    c() {
      e = T("a"), s && s.c(), n = K(), a && a.c(), this.h();
    },
    l(f) {
      e = B(f, "A", {
        href: !0,
        rel: !0,
        "aria-disabled": !0,
        class: !0,
        id: !0
      });
      var u = W(e);
      s && s.l(u), n = D(u), a && a.l(u), u.forEach(g), this.h();
    },
    h() {
      d(
        e,
        "href",
        /*link*/
        l[6]
      ), d(e, "rel", "noopener noreferrer"), d(
        e,
        "aria-disabled",
        /*disabled*/
        l[8]
      ), d(e, "class", i = /*size*/
      l[4] + " " + /*variant*/
      l[3] + " " + /*elem_classes*/
      l[1].join(" ") + " svelte-1j6e1i7"), d(
        e,
        "id",
        /*elem_id*/
        l[0]
      ), v(e, "hidden", !/*visible*/
      l[2]), v(
        e,
        "disabled",
        /*disabled*/
        l[8]
      ), h(
        e,
        "flex-grow",
        /*scale*/
        l[9]
      ), h(
        e,
        "pointer-events",
        /*disabled*/
        l[8] ? "none" : null
      ), h(
        e,
        "width",
        /*scale*/
        l[9] === 0 ? "fit-content" : null
      );
    },
    m(f, u) {
      q(f, e, u), s && s.m(e, null), U(e, n), a && a.m(e, null), t = !0;
    },
    p(f, u) {
      /*icon*/
      f[7] ? s ? s.p(f, u) : (s = A(f), s.c(), s.m(e, n)) : s && (s.d(1), s = null), a && a.p && (!t || u & /*$$scope*/
      2048) && P(
        a,
        o,
        f,
        /*$$scope*/
        f[11],
        t ? J(
          o,
          /*$$scope*/
          f[11],
          u,
          null
        ) : H(
          /*$$scope*/
          f[11]
        ),
        null
      ), (!t || u & /*link*/
      64) && d(
        e,
        "href",
        /*link*/
        f[6]
      ), (!t || u & /*disabled*/
      256) && d(
        e,
        "aria-disabled",
        /*disabled*/
        f[8]
      ), (!t || u & /*size, variant, elem_classes*/
      26 && i !== (i = /*size*/
      f[4] + " " + /*variant*/
      f[3] + " " + /*elem_classes*/
      f[1].join(" ") + " svelte-1j6e1i7")) && d(e, "class", i), (!t || u & /*elem_id*/
      1) && d(
        e,
        "id",
        /*elem_id*/
        f[0]
      ), (!t || u & /*size, variant, elem_classes, visible*/
      30) && v(e, "hidden", !/*visible*/
      f[2]), (!t || u & /*size, variant, elem_classes, disabled*/
      282) && v(
        e,
        "disabled",
        /*disabled*/
        f[8]
      ), u & /*scale*/
      512 && h(
        e,
        "flex-grow",
        /*scale*/
        f[9]
      ), u & /*disabled*/
      256 && h(
        e,
        "pointer-events",
        /*disabled*/
        f[8] ? "none" : null
      ), u & /*scale*/
      512 && h(
        e,
        "width",
        /*scale*/
        f[9] === 0 ? "fit-content" : null
      );
    },
    i(f) {
      t || (I(a, f), t = !0);
    },
    o(f) {
      S(a, f), t = !1;
    },
    d(f) {
      f && g(e), s && s.d(), a && a.d(f);
    }
  };
}
function N(l) {
  let e, n, i;
  return {
    c() {
      e = T("img"), this.h();
    },
    l(t) {
      e = B(t, "IMG", { class: !0, src: !0, alt: !0 }), this.h();
    },
    h() {
      d(e, "class", "button-icon svelte-1j6e1i7"), C(e.src, n = /*icon*/
      l[7].url) || d(e, "src", n), d(e, "alt", i = `${/*value*/
      l[5]} icon`), v(
        e,
        "right-padded",
        /*value*/
        l[5]
      );
    },
    m(t, s) {
      q(t, e, s);
    },
    p(t, s) {
      s & /*icon*/
      128 && !C(e.src, n = /*icon*/
      t[7].url) && d(e, "src", n), s & /*value*/
      32 && i !== (i = `${/*value*/
      t[5]} icon`) && d(e, "alt", i), s & /*value*/
      32 && v(
        e,
        "right-padded",
        /*value*/
        t[5]
      );
    },
    d(t) {
      t && g(e);
    }
  };
}
function A(l) {
  let e, n, i;
  return {
    c() {
      e = T("img"), this.h();
    },
    l(t) {
      e = B(t, "IMG", { class: !0, src: !0, alt: !0 }), this.h();
    },
    h() {
      d(e, "class", "button-icon svelte-1j6e1i7"), C(e.src, n = /*icon*/
      l[7].url) || d(e, "src", n), d(e, "alt", i = `${/*value*/
      l[5]} icon`);
    },
    m(t, s) {
      q(t, e, s);
    },
    p(t, s) {
      s & /*icon*/
      128 && !C(e.src, n = /*icon*/
      t[7].url) && d(e, "src", n), s & /*value*/
      32 && i !== (i = `${/*value*/
      t[5]} icon`) && d(e, "alt", i);
    },
    d(t) {
      t && g(e);
    }
  };
}
function ee(l) {
  let e, n, i, t;
  const s = [$, x], o = [];
  function a(f, u) {
    return (
      /*link*/
      f[6] && /*link*/
      f[6].length > 0 ? 0 : 1
    );
  }
  return e = a(l), n = o[e] = s[e](l), {
    c() {
      n.c(), i = M();
    },
    l(f) {
      n.l(f), i = M();
    },
    m(f, u) {
      o[e].m(f, u), q(f, i, u), t = !0;
    },
    p(f, [u]) {
      let _ = e;
      e = a(f), e === _ ? o[e].p(f, u) : (Y(), S(o[_], 1, 1, () => {
        o[_] = null;
      }), X(), n = o[e], n ? n.p(f, u) : (n = o[e] = s[e](f), n.c()), I(n, 1), n.m(i.parentNode, i));
    },
    i(f) {
      t || (I(n), t = !0);
    },
    o(f) {
      S(n), t = !1;
    },
    d(f) {
      f && g(i), o[e].d(f);
    }
  };
}
function le(l, e, n) {
  let { $$slots: i = {}, $$scope: t } = e, { elem_id: s = "" } = e, { elem_classes: o = [] } = e, { visible: a = !0 } = e, { variant: f = "secondary" } = e, { size: u = "lg" } = e, { value: _ = null } = e, { link: m = null } = e, { icon: j = null } = e, { disabled: z = !1 } = e, { scale: k = 0 } = e;
  const L = void 0;
  function r(c) {
    V.call(this, l, c);
  }
  return l.$$set = (c) => {
    "elem_id" in c && n(0, s = c.elem_id), "elem_classes" in c && n(1, o = c.elem_classes), "visible" in c && n(2, a = c.visible), "variant" in c && n(3, f = c.variant), "size" in c && n(4, u = c.size), "value" in c && n(5, _ = c.value), "link" in c && n(6, m = c.link), "icon" in c && n(7, j = c.icon), "disabled" in c && n(8, z = c.disabled), "scale" in c && n(9, k = c.scale), "$$scope" in c && n(11, t = c.$$scope);
  }, [
    s,
    o,
    a,
    f,
    u,
    _,
    m,
    j,
    z,
    k,
    L,
    t,
    i,
    r
  ];
}
class ie extends Q {
  constructor(e) {
    super(), Z(this, e, le, ee, p, {
      elem_id: 0,
      elem_classes: 1,
      visible: 2,
      variant: 3,
      size: 4,
      value: 5,
      link: 6,
      icon: 7,
      disabled: 8,
      scale: 9,
      min_width: 10
    });
  }
  get min_width() {
    return this.$$.ctx[10];
  }
}
const {
  SvelteComponent: ne,
  claim_component: te,
  claim_text: se,
  create_component: fe,
  destroy_component: ue,
  detach: ae,
  init: _e,
  insert_hydration: oe,
  mount_component: re,
  safe_not_equal: ce,
  set_data: de,
  text: me,
  transition_in: he,
  transition_out: be
} = window.__gradio__svelte__internal;
function ve(l) {
  let e = (
    /*value*/
    (l[3] ? (
      /*gradio*/
      l[11].i18n(
        /*value*/
        l[3]
      )
    ) : "") + ""
  ), n;
  return {
    c() {
      n = me(e);
    },
    l(i) {
      n = se(i, e);
    },
    m(i, t) {
      oe(i, n, t);
    },
    p(i, t) {
      t & /*value, gradio*/
      2056 && e !== (e = /*value*/
      (i[3] ? (
        /*gradio*/
        i[11].i18n(
          /*value*/
          i[3]
        )
      ) : "") + "") && de(n, e);
    },
    d(i) {
      i && ae(n);
    }
  };
}
function ge(l) {
  let e, n;
  return e = new ie({
    props: {
      value: (
        /*value*/
        l[3]
      ),
      variant: (
        /*variant*/
        l[4]
      ),
      elem_id: (
        /*elem_id*/
        l[0]
      ),
      elem_classes: (
        /*elem_classes*/
        l[1]
      ),
      size: (
        /*size*/
        l[6]
      ),
      scale: (
        /*scale*/
        l[7]
      ),
      link: (
        /*link*/
        l[9]
      ),
      icon: (
        /*icon*/
        l[8]
      ),
      min_width: (
        /*min_width*/
        l[10]
      ),
      visible: (
        /*visible*/
        l[2]
      ),
      disabled: !/*interactive*/
      l[5],
      $$slots: { default: [ve] },
      $$scope: { ctx: l }
    }
  }), e.$on(
    "click",
    /*click_handler*/
    l[12]
  ), {
    c() {
      fe(e.$$.fragment);
    },
    l(i) {
      te(e.$$.fragment, i);
    },
    m(i, t) {
      re(e, i, t), n = !0;
    },
    p(i, [t]) {
      const s = {};
      t & /*value*/
      8 && (s.value = /*value*/
      i[3]), t & /*variant*/
      16 && (s.variant = /*variant*/
      i[4]), t & /*elem_id*/
      1 && (s.elem_id = /*elem_id*/
      i[0]), t & /*elem_classes*/
      2 && (s.elem_classes = /*elem_classes*/
      i[1]), t & /*size*/
      64 && (s.size = /*size*/
      i[6]), t & /*scale*/
      128 && (s.scale = /*scale*/
      i[7]), t & /*link*/
      512 && (s.link = /*link*/
      i[9]), t & /*icon*/
      256 && (s.icon = /*icon*/
      i[8]), t & /*min_width*/
      1024 && (s.min_width = /*min_width*/
      i[10]), t & /*visible*/
      4 && (s.visible = /*visible*/
      i[2]), t & /*interactive*/
      32 && (s.disabled = !/*interactive*/
      i[5]), t & /*$$scope, value, gradio*/
      10248 && (s.$$scope = { dirty: t, ctx: i }), e.$set(s);
    },
    i(i) {
      n || (he(e.$$.fragment, i), n = !0);
    },
    o(i) {
      be(e.$$.fragment, i), n = !1;
    },
    d(i) {
      ue(e, i);
    }
  };
}
function ke(l, e, n) {
  let { elem_id: i = "" } = e, { elem_classes: t = [] } = e, { visible: s = !0 } = e, { value: o } = e, { variant: a = "secondary" } = e, { interactive: f } = e, { size: u = "lg" } = e, { scale: _ = 0 } = e, { icon: m = null } = e, { link: j = null } = e, { min_width: z = void 0 } = e, { gradio: k } = e;
  const L = () => k.dispatch("click");
  return l.$$set = (r) => {
    "elem_id" in r && n(0, i = r.elem_id), "elem_classes" in r && n(1, t = r.elem_classes), "visible" in r && n(2, s = r.visible), "value" in r && n(3, o = r.value), "variant" in r && n(4, a = r.variant), "interactive" in r && n(5, f = r.interactive), "size" in r && n(6, u = r.size), "scale" in r && n(7, _ = r.scale), "icon" in r && n(8, m = r.icon), "link" in r && n(9, j = r.link), "min_width" in r && n(10, z = r.min_width), "gradio" in r && n(11, k = r.gradio);
  }, [
    i,
    t,
    s,
    o,
    a,
    f,
    u,
    _,
    m,
    j,
    z,
    k,
    L
  ];
}
class ze extends ne {
  constructor(e) {
    super(), _e(this, e, ke, ge, ce, {
      elem_id: 0,
      elem_classes: 1,
      visible: 2,
      value: 3,
      variant: 4,
      interactive: 5,
      size: 6,
      scale: 7,
      icon: 8,
      link: 9,
      min_width: 10,
      gradio: 11
    });
  }
}
export {
  ie as BaseButton,
  ze as default
};

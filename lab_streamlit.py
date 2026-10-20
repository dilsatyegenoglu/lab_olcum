# -*- coding: utf-8 -*-
"""
Laboratuvar Malzemeleri ve Ölçüm Cihazları - Öğretici Streamlit Uygulaması
==========================================================================
© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır.

Ön lisans "Laboratuvar Malzemeleri ve Ölçüm Cihazları" dersi için etkileşimli öğretim
aracı: laboratuvar güvenliği, cam malzemeler, ölçümün temelleri, terazi ve nem tayini,
pH / EC metre, optik cihazlar, ileri analiz cihazları, laboratuvar türleri ve örnek alma.
Her konunun sonunda 10 / 20 / 30 seçmeli alıştırma ve adım adım çözüm.

Kurulum   : pip install -r requirements.txt
Çalıştırma: streamlit run lab_streamlit.py
"""

import math
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Laboratuvar Malzemeleri ve Ölçüm Cihazları", page_icon="🔬", layout="wide")

TELIF = "© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır."

# Renkler
MAVI, PEMBE, YESIL, TURUNCU = "#3B6FB6", "#D9577A", "#3C9A5F", "#E8A33B"
MOR, GRI_K, SARI = "#8E5BB5", "#5F6B7A", "#F2C94C"
SIVI, CAM, CAM_K = "#9CC3E6", "#EAF3FB", "#4A5A6A"   # sıvı, cam dolgu, cam çizgi
YAZI = 'font-family="Source Sans Pro, Segoe UI, Arial, sans-serif"'

st.markdown("""
<style>
.kutucuk {border-left:5px solid #3B6FB6; background:rgba(59,111,182,0.08);
          padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.uyari {border-left:5px solid #D9534F; background:rgba(217,83,79,0.08);
        padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.ipucu {border-left:5px solid #3C9A5F; background:rgba(60,154,95,0.08);
        padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.kartlar {display:flex; flex-wrap:wrap; gap:12px; margin:8px 0 14px 0;}
.kart {flex:1 1 220px; border:1px solid rgba(128,128,128,0.35); border-radius:10px;
       padding:12px 14px; background:rgba(128,128,128,0.05);}
.kart h4 {margin:0 0 6px 0; font-size:1.02rem;}
.kart p {margin:0; font-size:0.93rem;}
.dizi {font-family:monospace; font-size:18px; letter-spacing:1px; line-height:2.0;
       overflow-x:auto; white-space:nowrap; padding:6px 10px; border-radius:8px;
       background:rgba(128,128,128,0.07);}
.baz {display:inline-block; min-width:20px; text-align:center; border-radius:4px;
      margin:1px; padding:0 2px; color:#111; font-weight:700;}
.kodon {display:inline-block; border:1.5px solid rgba(128,128,128,0.6); border-radius:6px;
        padding:2px 6px; margin:3px; text-align:center; font-family:monospace;}
.kodon small {display:block; font-family:sans-serif; font-size:11px;}
.zaman {border-left:4px solid #3B6FB6; padding:4px 0 4px 12px; margin:6px 0;}
.zaman b.yil {color:#3B6FB6; font-size:1.05rem;}
.flash {border:2px solid #3B6FB6; border-radius:14px; padding:26px; text-align:center;
        font-size:1.4rem; font-weight:700; margin:10px 0;}
.flash-cevap {font-size:1.05rem; font-weight:400; margin-top:12px;}
.adim-baslik {font-size:1.15rem; font-weight:700; color:#3B6FB6; margin-top:18px;
              border-bottom:2px solid rgba(59,111,182,0.3);}
.etiket {border:2px dashed #5F6B7A; border-radius:10px; padding:12px 16px; max-width:420px;
          background:rgba(242,201,76,0.12); font-family:monospace; line-height:1.6;}
.ekran {font-family:monospace; font-size:1.6rem; background:#1d2b1f; color:#8CF59A;
        padding:8px 14px; border-radius:8px; display:inline-block; letter-spacing:2px;}
.renk-kutu {width:100%; height:110px; border-radius:12px; border:1px solid #999;}
</style>
""", unsafe_allow_html=True)


def ipucu(metin):
    st.markdown(f'<div class="ipucu">{metin}</div>', unsafe_allow_html=True)


def kartlar(liste):
    """liste: [(başlık, metin), ...]"""
    icerik = "".join(f'<div class="kart"><h4>{b}</h4><p>{m}</p></div>' for b, m in liste)
    st.markdown(f'<div class="kartlar">{icerik}</div>', unsafe_allow_html=True)


def kutu(metin):
    st.markdown(f'<div class="kutucuk">{metin}</div>', unsafe_allow_html=True)


def uyari(metin):
    st.markdown(f'<div class="uyari">{metin}</div>', unsafe_allow_html=True)


def ciz(fig, yukseklik=380):
    fig.update_layout(height=yukseklik, margin=dict(l=40, r=20, t=50, b=40),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def tablo(df):
    try:
        st.dataframe(df, hide_index=True, width="stretch")
    except TypeError:
        st.dataframe(df, hide_index=True, use_container_width=True)


def rng():
    if "rng" not in st.session_state:
        st.session_state.rng = np.random.default_rng()
    return st.session_state.rng


SORU_SAYISI = 10


def _md(t):
    return ("md", t)


def _tx(t):
    return ("tex", t)


def _fmt(x, ondalik=4):
    if abs(x - round(x)) < 1e-9 and abs(x) >= 1:
        return f"{int(round(x))}"
    return f"{x:.{ondalik}f}"


def soru_sayi(metin, dogru, cozum, yanlis=(), ondalik=4, tol=None):
    """Sayısal soru; sık yapılan hatalardan türetilen yanlış seçeneklerle seçmeliye çevrilir."""
    return {"tip": "sayi", "metin": metin, "dogru": float(dogru), "yanlis": list(yanlis),
            "ondalik": ondalik, "cozum": cozum}


def soru_secim(r, metin, dogru, yanlislar, cozum):
    return {"tip": "secim", "metin": metin, "dogru": dogru, "yanlis": list(yanlislar),
            "cozum": cozum}


def _secmeliye_cevir(r, s):
    if s["tip"] == "secim":
        secenekler = [s["dogru"]] + s["yanlis"]
    else:
        x, od = s["dogru"], s["ondalik"]
        dogru = _fmt(x, od)
        olasilik = 0 < x < 1
        secenekler = [dogru]
        for v in s["yanlis"]:
            if v is None or not math.isfinite(v) or (v < 0 <= x) or (olasilik and v > 1):
                continue
            t = _fmt(v, od)
            if t not in secenekler:
                secenekler.append(t)
            if len(secenekler) == 4:
                break
        deneme = 0
        while len(secenekler) < 4 and deneme < 200:
            deneme += 1
            if abs(x - round(x)) < 1e-9 and abs(x) >= 1:
                adim_ = max(3, int(round(abs(x) * 0.25)))
                v = x + int(r.choice([-1, 1])) * int(r.integers(1, adim_ + 1))
            elif deneme > 40 or abs(x) < 10 ** (-od + 1):
                v = abs(x) + float(r.integers(5, 400)) * 10 ** (-od)
            else:
                v = x * (1 + float(r.choice([-1, 1])) * float(r.uniform(0.12, 0.6)))
            if (v < 0 <= x) or (olasilik and v >= 1):
                continue
            t = _fmt(v, od)
            if t not in secenekler:
                secenekler.append(t)
        s = dict(s, dogru=dogru)
    sira = r.permutation(len(secenekler))
    s["secenekler"] = [secenekler[i] for i in sira]
    return s


def _sec(r, liste):
    return liste[int(r.integers(0, len(liste)))]


def _kavram_sec(r, havuz, adet):
    idx = r.permutation(len(havuz))[:adet]
    return [havuz[i] for i in idx]


def _al_cevapla(k, i):
    v = st.session_state.get(f"{k}_c{i}")
    if v is not None and f"{k}_cevap{i}" not in st.session_state:
        st.session_state[f"{k}_cevap{i}"] = v


ADET_SECENEK = [10, 20, 30]


def _temizle(k):
    for i in range(1, max(ADET_SECENEK) + 1):
        for ek in ("c", "cevap", "kilit"):
            st.session_state.pop(f"{k}_{ek}{i}", None)


def _al_yenile(k, uretici):
    _temizle(k)
    st.session_state[k] = _uret(uretici, st.session_state.get(f"{k}_adet", SORU_SAYISI))


def _uret(uretici, adet=SORU_SAYISI):
    """Üreticiyi gerektiği kadar çağırıp metni tekrarlanmayan 'adet' soru toplar."""
    r = rng()
    sorular, gorulen = [], set()
    for _ in range(40):
        for s in uretici(r):
            if s["metin"] not in gorulen:
                gorulen.add(s["metin"])
                sorular.append(_secmeliye_cevir(r, s))
            if len(sorular) >= adet:
                return sorular
    return sorular


def alistirma_blogu(anahtar, baslik, uretici):
    st.divider()
    st.subheader(f"✍️ Alıştırmalar: {baslik}")
    st.caption("Her soruda bir seçenek işaretleyin. Yanıtınız kilitlenir; doğru ya da yanlış "
               "olduğu ve **adım adım çözüm** o zaman açılır. Önce kâğıt-kalemle hesaplayın!")
    k = f"al_{anahtar}"
    st.radio("Kaç soru?", ADET_SECENEK, horizontal=True, key=f"{k}_adet",
             on_change=_al_yenile, args=(k, uretici))
    if k not in st.session_state:
        st.session_state[k] = _uret(uretici, st.session_state.get(f"{k}_adet", SORU_SAYISI))
    sorular = st.session_state[k]
    dogru_say = cevap_say = 0
    for i, s in enumerate(sorular, 1):
        with st.container(border=True):
            st.markdown(f"**Soru {i} / {len(sorular)}.** {s['metin']}")
            secili = st.session_state.get(f"{k}_cevap{i}")
            if secili is None:
                st.radio("Seçiniz", s["secenekler"], index=None, key=f"{k}_c{i}",
                         label_visibility="collapsed", on_change=_al_cevapla, args=(k, i))
            else:
                cevap_say += 1
                st.radio("Yanıtınız", s["secenekler"], index=s["secenekler"].index(secili),
                         key=f"{k}_kilit{i}", disabled=True, label_visibility="collapsed")
                if secili == s["dogru"]:
                    dogru_say += 1
                    st.success("✅ Doğru!")
                else:
                    st.error(f"❌ Yanlış. Doğru yanıt: **{s['dogru']}**")
                with st.expander("📖 Nasıl hesaplanır?", expanded=True):
                    for tur, icerik in s["cozum"]:
                        if tur == "tex":
                            for parca in icerik.split(r"\qquad"):
                                st.latex(parca)
                        else:
                            st.markdown(icerik)
    st.progress(cevap_say / len(sorular),
                text=f"Yanıtlanan: {cevap_say} / {len(sorular)}  ·  Doğru: {dogru_say}")
    if cevap_say == len(sorular):
        oran = dogru_say / len(sorular)
        mesaj = (f"🎉 Tebrikler! {dogru_say}/{len(sorular)}" if oran >= 0.8 else
                 f"👍 {dogru_say}/{len(sorular)}: yanlışların çözümlerini tekrar inceleyin"
                 if oran >= 0.5 else
                 f"📚 {dogru_say}/{len(sorular)}: konuyu yukarıdan bir kez daha okuyup yeni "
                 "sorularla deneyin")
        (st.success if oran >= 0.8 else st.info if oran >= 0.5 else st.warning)(mesaj)
    st.button("🎲 Yeni sorular", key=f"{k}_yeni", on_click=_al_yenile, args=(k, uretici))


def svg_goster(svg):
    import base64
    veri = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    st.markdown(f'<div style="width:100%;margin:6px 0 14px 0;text-align:center">'
                f'<img src="data:image/svg+xml;base64,{veri}" style="width:100%;'
                f'max-width:1000px;background:white;border-radius:12px"/></div>',
                unsafe_allow_html=True)


def _krom(x, y, h, w, renk, sent=0.33):
    yc = y + h * sent
    return (f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{yc - y - 3}" rx="{w / 2}" '
            f'fill="{renk}" stroke="#444" stroke-width="1.4"/>'
            f'<rect x="{x - w / 2}" y="{yc + 3}" width="{w}" height="{y + h - yc - 3}" '
            f'rx="{w / 2}" fill="{renk}" stroke="#444" stroke-width="1.4"/>'
            f'<ellipse cx="{x}" cy="{yc}" rx="{w * 0.3}" ry="5" fill="{renk}" stroke="#444" '
            f'stroke-width="1.2"/>')


def _bant(x, y, w, renk, h=12):
    return (f'<rect x="{x - w / 2 + 1.5}" y="{y - h / 2}" width="{w - 3}" height="{h}" '
            f'fill="{renk}" stroke="#222" stroke-width="0.8"/>')


def _yazi(x, y, t, boy=14, renk="#222", hiza="middle", kalin=False):
    k = ' font-weight="700"' if kalin else ""
    return (f'<text x="{x}" y="{y}" {YAZI} font-size="{boy}" fill="{renk}" '
            f'text-anchor="{hiza}"{k}>{t}</text>')


def _ok(x1, y1, x2, y2, renk="#555"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{renk}" stroke-width="2.2" '
            f'marker-end="url(#okucu)"/>')


_OK_TANIM = ('<defs><marker id="okucu" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
             'fill="#555"/></marker></defs>')


def _yarim_daire(cx, cy, r, sol, sag):
    return (f'<path d="M{cx},{cy - r} A{r},{r} 0 0 0 {cx},{cy + r} Z" fill="{sol}"/>'
            f'<path d="M{cx},{cy - r} A{r},{r} 0 0 1 {cx},{cy + r} Z" fill="{sag}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#333" stroke-width="1.4"/>')


# ===========================================================================
# ŞEMALAR (SVG) — tamamı bu uygulama için çizilmiştir
# ===========================================================================
def svg_ac(w, h, maks=None):
    m = f"max-width:{maks}px;" if maks else ""
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" style="{m}" '
            f'xmlns="http://www.w3.org/2000/svg">' + _OK_TANIM +
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="white"/>')


def _kutu_svg(x, y, w, h, renk, yazi, boy=14, dolgu=None, kalin=True, renk_yazi="#222"):
    d = dolgu or "white"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{d}" stroke="{renk}" '
            f'stroke-width="2"/>' +
            "".join(_yazi(x + w / 2, y + h / 2 + 5 + (i - (len(yazi) - 1) / 2) * (boy + 3), t, boy,
                          renk_yazi, kalin=(kalin and i == 0))
                    for i, t in enumerate(yazi if isinstance(yazi, (list, tuple)) else [yazi])))


# ---------------------------------------------------------------------------
# Cam malzemeler: her çizim (cx, by) = (orta x, alt y) noktasına göre
# ---------------------------------------------------------------------------
_CIZGI = f'stroke="{CAM_K}" stroke-width="2.2" stroke-linejoin="round"'


def _cizgiler(x, y1, y2, adim, uzun=5, kisa=3, sag=True):
    s = ""
    i = 0
    y = y2
    while y >= y1:
        L = uzun if i % 5 == 0 else kisa
        x2 = x - L if sag else x + L
        s += f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y}" stroke="{CAM_K}" stroke-width="1"/>'
        y -= adim
        i += 1
    return s


def _beher(cx, by):
    return (f'<rect x="{cx - 34}" y="{by - 40}" width="68" height="38" fill="{SIVI}"/>'
            f'<path d="M{cx - 42},{by - 86} L{cx - 35},{by - 80} L{cx - 35},{by - 5} '
            f'Q{cx - 35},{by} {cx - 30},{by} L{cx + 30},{by} Q{cx + 35},{by} {cx + 35},{by - 5} '
            f'L{cx + 35},{by - 82}" fill="none" {_CIZGI}/>' + _cizgiler(cx + 33, by - 70, by - 10, 6))


def _erlen(cx, by):
    return (f'<path d="M{cx - 27},{by - 30} L{cx - 38},{by - 6} Q{cx - 40},{by} {cx - 33},{by} '
            f'L{cx + 33},{by} Q{cx + 40},{by} {cx + 38},{by - 6} L{cx + 27},{by - 30} Z" fill="{SIVI}"/>'
            f'<path d="M{cx - 10},{by - 118} L{cx - 10},{by - 82} L{cx - 38},{by - 6} '
            f'Q{cx - 40},{by} {cx - 33},{by} L{cx + 33},{by} Q{cx + 40},{by} {cx + 38},{by - 6} '
            f'L{cx + 10},{by - 82} L{cx + 10},{by - 118}" fill="none" {_CIZGI}/>'
            f'<line x1="{cx - 13}" y1="{by - 118}" x2="{cx + 13}" y2="{by - 118}" {_CIZGI}/>')


def _balon(cx, by):
    return (f'<path d="M{cx - 30},{by - 36} A31,31 0 0 0 {cx - 24},{by} L{cx + 24},{by} '
            f'A31,31 0 0 0 {cx + 30},{by - 36} Z" fill="{SIVI}"/>'
            f'<rect x="{cx - 5}" y="{by - 104}" width="10" height="44" fill="{SIVI}"/>'
            f'<path d="M{cx - 6},{by - 140} L{cx - 6},{by - 62} A33,33 0 0 0 {cx - 24},{by} '
            f'L{cx + 24},{by} A33,33 0 0 0 {cx + 6},{by - 62} L{cx + 6},{by - 140}" fill="none" {_CIZGI}/>'
            f'<line x1="{cx - 9}" y1="{by - 104}" x2="{cx + 9}" y2="{by - 104}" stroke="#D9534F" '
            f'stroke-width="2"/>'
            f'<rect x="{cx - 8}" y="{by - 154}" width="16" height="14" rx="3" fill="#C9D3DD" '
            f'stroke="{CAM_K}" stroke-width="1.5"/>')


def _mezur(cx, by):
    return (f'<rect x="{cx - 13}" y="{by - 70}" width="26" height="58" fill="{SIVI}"/>'
            f'<path d="M{cx - 18},{by - 150} L{cx - 13},{by - 146} L{cx - 13},{by - 12} '
            f'L{cx + 13},{by - 12} L{cx + 13},{by - 148}" fill="none" {_CIZGI}/>'
            f'<path d="M{cx - 30},{by} L{cx - 22},{by - 12} L{cx + 22},{by - 12} L{cx + 30},{by} Z" '
            f'fill="{CAM}" {_CIZGI}/>' + _cizgiler(cx + 12, by - 140, by - 16, 6, 8, 4))


def _tam_pipet(cx, by):
    return (f'<path d="M{cx - 3},{by - 160} L{cx - 3},{by - 98} Q{cx - 13},{by - 90} {cx - 12},{by - 76} '
            f'Q{cx - 13},{by - 62} {cx - 3},{by - 54} L{cx - 3},{by - 14} L{cx},{by} '
            f'L{cx + 3},{by - 14} L{cx + 3},{by - 54} Q{cx + 13},{by - 62} {cx + 12},{by - 76} '
            f'Q{cx + 13},{by - 90} {cx + 3},{by - 98} L{cx + 3},{by - 160}" fill="{CAM}" {_CIZGI}/>'
            f'<line x1="{cx - 6}" y1="{by - 140}" x2="{cx + 6}" y2="{by - 140}" stroke="#D9534F" '
            f'stroke-width="2"/>')


def _dereceli_pipet(cx, by):
    return (f'<path d="M{cx - 4},{by - 160} L{cx - 4},{by - 20} L{cx},{by} L{cx + 4},{by - 20} '
            f'L{cx + 4},{by - 160}" fill="{CAM}" {_CIZGI}/>' +
            _cizgiler(cx + 4, by - 150, by - 26, 5, 8, 4))


def _buret(cx, by):
    return (f'<rect x="{cx - 5}" y="{by - 110}" width="10" height="70" fill="{SIVI}"/>'
            f'<path d="M{cx - 6},{by - 160} L{cx - 6},{by - 40} L{cx - 2},{by - 30} L{cx - 2},{by - 4} '
            f'L{cx},{by} L{cx + 2},{by - 4} L{cx + 2},{by - 30} L{cx + 6},{by - 40} L{cx + 6},{by - 160}" '
            f'fill="none" {_CIZGI}/>' + _cizgiler(cx + 6, by - 155, by - 45, 5, 8, 4) +
            f'<rect x="{cx - 18}" y="{by - 31}" width="36" height="7" rx="3" fill="#5F6B7A"/>'
            f'<circle cx="{cx}" cy="{by - 27}" r="5" fill="#C9D3DD" stroke="{CAM_K}"/>')


def _huni(cx, by):
    return (f'<path d="M{cx - 40},{by - 120} L{cx + 40},{by - 120} L{cx + 5},{by - 70} L{cx + 5},{by} '
            f'L{cx - 5},{by} L{cx - 5},{by - 70} Z" fill="{CAM}" {_CIZGI}/>'
            f'<path d="M{cx - 30},{by - 116} L{cx + 30},{by - 116} L{cx},{by - 78} Z" fill="white" '
            f'stroke="#B7B7B7" stroke-width="1.2"/>')


def _tup(cx, by):
    return (f'<path d="M{cx - 11},{by - 50} L{cx - 11},{by - 11} A11,11 0 0 0 {cx + 11},{by - 11} '
            f'L{cx + 11},{by - 50} Z" fill="{SIVI}"/>'
            f'<path d="M{cx - 14},{by - 140} L{cx - 11},{by - 137} L{cx - 11},{by - 11} '
            f'A11,11 0 0 0 {cx + 11},{by - 11} L{cx + 11},{by - 137} L{cx + 14},{by - 140}" '
            f'fill="none" {_CIZGI}/>')


def _desikator(cx, by):
    noktalar = "".join(f'<circle cx="{cx - 30 + 8 * i}" cy="{by - 12 - (i % 2) * 5}" r="3" fill="#3B6FB6"/>'
                       for i in range(9))
    return (f'<path d="M{cx - 48},{by - 70} L{cx - 44},{by - 6} Q{cx - 43},{by} {cx - 36},{by} '
            f'L{cx + 36},{by} Q{cx + 43},{by} {cx + 44},{by - 6} L{cx + 48},{by - 70} Z" '
            f'fill="{CAM}" {_CIZGI}/>' + noktalar +
            f'<line x1="{cx - 46}" y1="{by - 30}" x2="{cx + 46}" y2="{by - 30}" stroke="#888" '
            f'stroke-width="3" stroke-dasharray="6 4"/>'
            f'<path d="M{cx - 18},{by - 30} L{cx - 15},{by - 46} L{cx + 15},{by - 46} L{cx + 18},{by - 30}" '
            f'fill="#F4F1EA" stroke="#777" stroke-width="1.5"/>'
            f'<path d="M{cx - 54},{by - 72} Q{cx},{by - 112} {cx + 54},{by - 72} Z" fill="{CAM}" {_CIZGI}/>'
            f'<rect x="{cx - 8}" y="{by - 102}" width="16" height="12" rx="4" fill="#C9D3DD" '
            f'stroke="{CAM_K}" stroke-width="1.5"/>')


def _kroze(cx, by):
    return (f'<path d="M{cx - 30},{by - 54} L{cx - 20},{by} L{cx + 20},{by} L{cx + 30},{by - 54} Z" '
            f'fill="#F4F1EA" stroke="#777" stroke-width="2"/>'
            f'<path d="M{cx - 34},{by - 58} Q{cx},{by - 72} {cx + 34},{by - 58} Z" fill="#F4F1EA" '
            f'stroke="#777" stroke-width="2"/>'
            f'<rect x="{cx - 5}" y="{by - 74}" width="10" height="8" rx="3" fill="#F4F1EA" stroke="#777"/>')


def _puar(cx, by):
    return (f'<circle cx="{cx}" cy="{by - 70}" r="34" fill="#D9534F" stroke="#8B2E2B" stroke-width="2"/>'
            f'<rect x="{cx - 6}" y="{by - 136}" width="12" height="32" rx="4" fill="#C94A46" '
            f'stroke="#8B2E2B" stroke-width="1.5"/>'
            f'<rect x="{cx - 6}" y="{by - 38}" width="12" height="38" rx="4" fill="#C94A46" '
            f'stroke="#8B2E2B" stroke-width="1.5"/>'
            f'<rect x="{cx + 30}" y="{by - 76}" width="22" height="12" rx="4" fill="#C94A46" '
            f'stroke="#8B2E2B" stroke-width="1.5"/>' +
            _yazi(cx, by - 116, "A", 13, "white", kalin=True) + _yazi(cx, by - 14, "S", 13, "white", kalin=True)
            + _yazi(cx + 41, by - 66, "E", 11, "white", kalin=True))


def _mikropipet(cx, by):
    return (f'<rect x="{cx - 4}" y="{by - 160}" width="8" height="14" rx="2" fill="#5F6B7A"/>'
            f'<rect x="{cx - 9}" y="{by - 164}" width="18" height="6" rx="3" fill="#3B6FB6"/>'
            f'<path d="M{cx - 13},{by - 146} L{cx + 13},{by - 146} L{cx + 11},{by - 60} L{cx + 5},{by - 46} '
            f'L{cx - 5},{by - 46} L{cx - 11},{by - 60} Z" fill="#DDE3EA" stroke="{CAM_K}" stroke-width="2"/>'
            f'<rect x="{cx - 8}" y="{by - 120}" width="16" height="22" rx="2" fill="#1d2b1f"/>' +
            _yazi(cx, by - 104, "100", 9, "#8CF59A", kalin=True) +
            f'<path d="M{cx - 5},{by - 46} L{cx + 5},{by - 46} L{cx + 1},{by} L{cx - 1},{by} Z" '
            f'fill="#F2E8B5" stroke="#B8A44A" stroke-width="1.5"/>'
            f'<path d="M{cx + 13},{by - 140} L{cx + 22},{by - 132} L{cx + 13},{by - 124}" fill="#5F6B7A"/>')


def _saat_cami(cx, by):
    return (f'<path d="M{cx - 50},{by - 30} Q{cx},{by + 4} {cx + 50},{by - 30}" fill="{CAM}" {_CIZGI}/>'
            f'<ellipse cx="{cx}" cy="{by - 18}" rx="14" ry="5" fill="#E8A33B"/>')


CAM_MALZEME = {
    "beher": ("Beher", _beher,
              "Sıvıları ve çözeltileri karıştırmak, ısıtmak, geçici olarak koymak için silindirik kap "
              "(5–1000 mL ve üstü). Üzerindeki çizgiler <b>yaklaşık</b> hacim gösterir.",
              "Hassas hacim ölçmek ya da çözelti hazırlamak için kullanılmaz."),
    "erlen": ("Erlen", _erlen,
              "Konik gövdeli, dar ağızlı kap (10–500 mL). Çalkalarken sıçratmaz; en çok "
              "<b>titrasyonda</b> titre edilen çözelti erlene konur.",
              "Çizgileri yaklaşıktır, ölçüm için değildir."),
    "balon": ("Balon joje (ölçü balonu)", _balon,
              "Uzun boyunlu, kapaklı balon. Boynundaki <b>tek çizgi</b> tam hacmi gösterir (2–2000 mL). "
              "Derişimi bilinen <b>standart çözelti hazırlamak</b> için kullanılır.",
              "Tek bir hacmi ölçer; çizgiye menisküsün alt kenarı göz hizasında getirilir. Isıtılmaz."),
    "mezur": ("Mezür", _mezur,
              "Taksimatlı (dereceli) silindir. Bir sıvıyı ölçerek başka bir kaba <b>aktarmak</b> için "
              "kullanılır.",
              "Pipet, büret ve balon jojeden daha az hassastır; hassas ölçümde kullanılmaz."),
    "tam_pipet": ("Tam pipet (bölmesiz)", _tam_pipet,
                  "Ortası şişkin pipet; tek bir hacmi (ör. 10,00 mL) çok hassas aktarır. Puarla çekilir.",
                  "Ağızla asla çekilmez. Çizgiye göz hizasında gelinir."),
    "dereceli_pipet": ("Dereceli pipet", _dereceli_pipet,
                       "Üzerinde taksimat olan ince cam boru (0,1–25 mL). İstenen hacim aktarılabilir.",
                       "Puarla çekilir. Başka bir çözeltiye daldırılmaz, orijinal şişeye sokulmaz."),
    "buret": ("Büret", _buret,
              "Ucu musluklu, taksimatlı uzun cam boru. <b>Titrasyonda</b> harcanan çözelti hacmini ölçer.",
              "Okuma göz hizasında, menisküsün alt kenarından yapılır; başlangıç ve bitiş okunur, farkı alınır."),
    "huni": ("Huni", _huni,
             "Sıvıyı dar ağızlı kaba aktarmak ya da filtre kâğıdıyla <b>süzmek</b> için.",
             "Süzme sırasında filtre kâğıdı huninin kenarını aşmamalıdır."),
    "tup": ("Deney tüpü", _tup,
            "Küçük hacimli tepkimeler ve ısıtma için (yaygın boyut: 15 × 160 mm).",
            "Isıtırken ağzı kendine ve başkasına çevrilmez."),
    "desikator": ("Desikatör", _desikator,
                  "İçinde nem çekici madde (silika jel, susuz CaCl₂ gibi) bulunan kapaklı kap. Kurutulmuş "
                  "numune ve kapları <b>nem çekmeden soğutmak</b> için.",
                  "Kapağı yana kaydırılarak açılır. Sıcak kap konunca kapak hemen sıkıca kapatılmaz; "
                  "hava genleşip kapağı itebilir."),
    "kroze": ("Kroze (porselen)", _kroze,
              "Yüksek sıcaklığa dayanıklı porselen kap. <b>Kül tayininde</b> kül fırınında kullanılır.",
              "Önce kızdırılır, desikatörde soğutulur, darası alınır."),
    "saat": ("Saat camı", _saat_cami,
             "Az miktarda katı tartmak, beherin ağzını örtmek için kavisli cam.",
             "Tartımdan önce temiz ve kuru olmalıdır."),
    "puar": ("Puar", _puar,
             "Pipete takılan lastik pompa: <b>A</b> havayı boşaltır, <b>S</b> sıvıyı çeker, <b>E</b> "
             "sıvıyı boşaltır.",
             "Laboratuvarda hiçbir sıvı ağızla çekilmez; daima puar ya da pipet pompası kullanılır."),
    "mikropipet": ("Mikropipet", _mikropipet,
                   "Mikrolitre (µL) düzeyinde ayarlanabilir hacim aktarır (ör. 10–100 µL).",
                   "Her numunede uç değiştirilir; ayar aralığının dışına çevrilmez; yatay bırakılmaz."),
}


def svg_cam(secili=None):
    anahtar = list(CAM_MALZEME)
    sut = 4
    w, h = 170, 215
    satir = (len(anahtar) + sut - 1) // sut
    s = [svg_ac(w * sut + 20, h * satir + 20, 900)]
    for i, k in enumerate(anahtar):
        ad, f, _, _ = CAM_MALZEME[k]
        x = 10 + (i % sut) * w
        y = 10 + (i // sut) * h
        sec = (k == secili)
        s.append(f'<rect x="{x + 4}" y="{y + 4}" width="{w - 8}" height="{h - 8}" rx="12" '
                 f'fill="{"#FFF5E0" if sec else "#FAFBFD"}" stroke="{TURUNCU if sec else "#D5DCE4"}" '
                 f'stroke-width="{4 if sec else 1.2}"/>')
        s.append(f'<g opacity="{1 if (secili is None or sec) else 0.45}">{f(x + w / 2, y + 172)}</g>')
        kelimeler = ad.split(" (")[0]
        s.append(_yazi(x + w / 2, y + 198, kelimeler, 15, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Menisküs okuma ve paralaks hatası
# ---------------------------------------------------------------------------
def svg_meniskus(goz):
    """goz: -1 alttan, 0 göz hizası, +1 üstten. Döndürür (svg, okunan_deger)."""
    W, H = 640, 340
    xs, xm, xa = 300, 400, 500          # ön çeper (skala), menisküs dibi, arka çeper
    deger, ym = 46.0, 175               # gerçek değer ve menisküs dibinin y'si
    px = 60                             # 1 mL = 60 px
    s = [svg_ac(W, H, 760)]
    s.append(f'<rect x="{xs}" y="30" width="{xa - xs}" height="280" fill="{CAM}"/>')
    s.append(f'<path d="M{xs},{ym - 14} Q{xm},{ym + 14} {xa},{ym - 14} L{xa},310 L{xs},310 Z" fill="{SIVI}"/>')
    s.append(f'<line x1="{xs}" y1="30" x2="{xs}" y2="310" {_CIZGI}/>'
             f'<line x1="{xa}" y1="30" x2="{xa}" y2="310" {_CIZGI}/>')
    for i in range(-2, 3):
        y = ym - i * px
        s.append(f'<line x1="{xs}" y1="{y}" x2="{xs + 26}" y2="{y}" stroke="#222" stroke-width="2"/>')
        s.append(_yazi(xs - 8, y + 5, f"{deger + i:.0f}", 14, "#222", "end", True))
        for j in range(1, 10):
            yy = y - j * px / 10
            if yy > 30:
                s.append(f'<line x1="{xs}" y1="{yy}" x2="{xs + (14 if j == 5 else 8)}" y2="{yy}" '
                         f'stroke="#444" stroke-width="1"/>')
    ye = {-1: 280, 0: ym, 1: 70}[goz]
    xe = 70
    yk = ye + (ym - ye) * (xs - xe) / (xm - xe)
    okunan = deger + (ym - yk) / px
    renk = YESIL if goz == 0 else "#D9534F"
    s.append(f'<ellipse cx="{xe}" cy="{ye}" rx="24" ry="13" fill="white" stroke="#333" stroke-width="2"/>'
             f'<circle cx="{xe + 6}" cy="{ye}" r="7" fill="#3B6FB6"/>')
    s.append(f'<line x1="{xe + 24}" y1="{ye + (ym - ye) * 24 / (xm - xe)}" x2="{xm}" y2="{ym}" '
             f'stroke="{renk}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    s.append(f'<circle cx="{xs}" cy="{yk}" r="6" fill="{renk}"/>')
    s.append(f'<circle cx="{xm}" cy="{ym}" r="5" fill="#222"/>')
    s.append(_yazi(xm, ym + 32, "menisküsün alt kenarı", 13, "#222"))
    s.append(_yazi(xa + 10, 50, "yandan kesit", 12, "#666", "start"))
    s.append(_yazi(xs + 13, 24, "skala (ön yüz)", 12, "#666"))
    s.append(_yazi(W / 2, H - 8, f"Okunan: {okunan:.2f} mL   ·   Gerçek: {deger:.2f} mL", 16, renk, kalin=True))
    s.append("</svg>")
    return "".join(s), okunan


# ---------------------------------------------------------------------------
# Doğruluk ve kesinlik: dört hedef
# ---------------------------------------------------------------------------
def svg_hedefler():
    rr = np.random.default_rng(7)
    durum = [("Doğru ve kesin", 0, 0, 7, YESIL), ("Kesin ama doğru değil", 52, -30, 7, TURUNCU),
             ("Doğru ama kesin değil", 0, 0, 34, TURUNCU), ("Ne doğru ne kesin", 40, 35, 34, "#D9534F")]
    W, H = 880, 270
    s = [svg_ac(W, H, 900)]
    for i, (ad, dx, dy, sd, renk) in enumerate(durum):
        cx, cy = 110 + i * 220, 120
        for r, c in [(95, "#F3F5F8"), (72, "#E3E8EF"), (48, "#CFD7E2"), (24, "#B7C3D3")]:
            s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" stroke="#8A97A8"/>')
        s.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="#222"/>')
        for _ in range(7):
            x = cx + dx + rr.normal(0, sd)
            y = cy + dy + rr.normal(0, sd)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{renk}" stroke="white" stroke-width="1.5"/>')
        s.append(_yazi(cx, 248, ad, 15, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Dört laboratuvar ve ortak cihazlar
# ---------------------------------------------------------------------------
def svg_dort_lab():
    W, H = 860, 430
    s = [svg_ac(W, H, 900)]
    lab = [("Gıda", "Nem, kül, protein, yağ,", "Brix, aw, renk, pH", 165, 105, TURUNCU),
           ("Toprak", "pH, EC, kireç, organik", "madde, tekstür, P, K", 695, 105, "#8C5A3C"),
           ("Yaprak", "N, P, K, mikro", "elementler, SPAD", 165, 325, YESIL),
           ("Su", "pH, EC, çözünmüş O₂,", "bulanıklık, nitrat", 695, 325, MAVI)]
    for ad, a, b, x, y, renk in lab:
        s.append(f'<line x1="{x}" y1="{y}" x2="430" y2="215" stroke="{renk}" stroke-width="3" '
                 f'stroke-dasharray="8 6"/>')
    for ad, a, b, x, y, renk in lab:
        s.append(f'<rect x="{x - 150}" y="{y - 70}" width="300" height="140" rx="16" fill="white" '
                 f'stroke="{renk}" stroke-width="3"/>')
        s.append(_yazi(x, y - 28, ad, 22, renk, kalin=True))
        s.append(_yazi(x, y + 10, a, 16))
        s.append(_yazi(x, y + 34, b, 16))
    s.append(f'<circle cx="430" cy="215" r="98" fill="#F6F8FB" stroke="{GRI_K}" stroke-width="3"/>')
    s.append(_yazi(430, 176, "ORTAK CİHAZLAR", 15, GRI_K, kalin=True))
    for i, t in enumerate(["Terazi", "pH metre", "Spektrofotometre", "Etüv"]):
        s.append(_yazi(430, 206 + i * 23, t, 16, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Laboratuvar planı: güvenlik olanakları
# ---------------------------------------------------------------------------
LAB_OLANAK = {
    "ceker": ("Çeker ocak", "Zehirli, uçucu ve derişik asit/baz buharlarını dışarı atar. Yılda en az bir kez "
              "uzman kontrolü; çalışırken ön camı mümkün olduğunca aşağıda tutulur."),
    "goz": ("Göz duşu", "Göze kimyasal sıçrarsa göz kapakları açık tutularak en az 15–20 dakika yıkanır. "
            "Haftalık olarak çalıştırılıp kontrol edilmelidir."),
    "vucut": ("Vücut (acil) duşu", "Vücuda büyük miktarda kimyasal döküldüğünde ya da giysi alev aldığında "
              "kullanılır. Kirlenen giysiler çıkarılarak uzun süre yıkanılır."),
    "yangin": ("Yangın söndürücü", "Uygun tipte olmalı (ör. CO₂, kuru kimyevi toz). Basıncı ve dolum tarihi "
               "düzenli olarak (notlarda: 6 ayda bir) kontrol edilir."),
    "battaniye": ("Yangın battaniyesi", "Alev alan kişinin üzerine sarılarak hava teması kesilir; küçük "
                  "kap yangınlarının üzeri örtülür."),
    "ilkyardim": ("İlk yardım dolabı", "Her laboratuvarda bulunmalı; içeriği eksiksiz, son kullanma "
                  "tarihleri güncel olmalı. Kaza anında yapılacaklar yazılı olarak asılı durmalıdır."),
    "kimyasal": ("Kimyasal dolabı", "Kimyasallar türüne göre ayrı (asitler, bazlar, yanıcılar, "
                 "oksitleyiciler) ve havalandırmalı dolaplarda, en az miktarda tutulur."),
    "atik": ("Atık toplama", "Kimyasal atıklar türüne göre ayrı, etiketli kaplarda toplanır; lavaboya "
             "gelişigüzel dökülmez."),
    "kirik": ("Kırık cam kutusu", "Kırık cam çöp kutusuna değil, ayrı ve sağlam kırık cam kutusuna atılır."),
    "lavabo": ("Lavabo ve musluklar", "El yıkama ve malzeme durulama; su, gaz, elektrik kullanılmadığında "
               "kapalı tutulur."),
    "cikis": ("Acil çıkış", "Her zaman açık ve önü boş tutulur; acil durum planı kapının yanına asılır."),
}


def svg_lab_plan(secili=None):
    W, H = 880, 470
    s = [svg_ac(W, H, 900)]
    s.append(f'<rect x="30" y="30" width="820" height="400" fill="#FAFBFD" stroke="#5F6B7A" stroke-width="6"/>')
    # tezgahlar
    s.append(f'<rect x="250" y="190" width="380" height="70" rx="6" fill="#E3E8EF" stroke="#8A97A8"/>')
    s.append(_yazi(440, 231, "Çalışma tezgâhı", 15, "#5F6B7A", kalin=True))
    yer = {"ceker": (40, 40, 200, 80), "lavabo": (400, 40, 150, 60), "goz": (555, 40, 90, 60),
           "kimyasal": (750, 40, 90, 150), "atik": (750, 220, 90, 80), "kirik": (750, 320, 90, 60),
           "vucut": (40, 340, 110, 80), "yangin": (180, 360, 90, 60), "battaniye": (290, 360, 100, 60),
           "ilkyardim": (40, 180, 120, 110), "cikis": (520, 398, 140, 32)}
    renk = {"ceker": MOR, "lavabo": MAVI, "goz": "#17A2B8", "kimyasal": TURUNCU, "atik": GRI_K,
            "kirik": "#8C5A3C", "vucut": "#17A2B8", "yangin": "#D9534F", "battaniye": "#D9534F",
            "ilkyardim": YESIL, "cikis": YESIL}
    for k, (x, y, w, h) in yer.items():
        sec = (k == secili)
        op = 1 if (secili is None or sec) else 0.35
        s.append(f'<g opacity="{op}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" '
                 f'fill="{renk[k]}" fill-opacity="0.18" stroke="{renk[k]}" stroke-width="{5 if sec else 2.5}"/>')
        ad = LAB_OLANAK[k][0]
        parca = ad.split(" ") if len(ad) > 12 and w < 160 else [ad]
        for j, p in enumerate(parca):
            s.append(_yazi(x + w / 2, y + h / 2 + 5 + (j - (len(parca) - 1) / 2) * 17, p, 14,
                           "#222", kalin=True))
        s.append("</g>")
    s.append(f'<rect x="520" y="424" width="140" height="12" fill="white"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# GHS tehlike işaretleri (piktogramlar)
# ---------------------------------------------------------------------------
def _alev(cx, cy, k=1.0):
    return (f'<path d="M{cx},{cy - 30 * k} C{cx + 20 * k},{cy - 10 * k} {cx + 22 * k},{cy + 10 * k} '
            f'{cx + 10 * k},{cy + 22 * k} C{cx + 12 * k},{cy + 8 * k} {cx + 4 * k},{cy + 2 * k} {cx},{cy - 4 * k} '
            f'C{cx - 2 * k},{cy + 8 * k} {cx - 8 * k},{cy + 12 * k} {cx - 8 * k},{cy + 22 * k} '
            f'C{cx - 22 * k},{cy + 10 * k} {cx - 18 * k},{cy - 10 * k} {cx},{cy - 30 * k} Z" fill="#111"/>')


def _ghs_sembol(tur, cx, cy):
    if tur == "alev":
        return _alev(cx, cy - 4) + f'<rect x="{cx - 26}" y="{cy + 22}" width="52" height="5" fill="#111"/>'
    if tur == "oksit":
        return (f'<circle cx="{cx}" cy="{cy + 12}" r="14" fill="none" stroke="#111" stroke-width="6"/>'
                + _alev(cx, cy - 14, 0.7) + f'<rect x="{cx - 26}" y="{cy + 30}" width="52" height="5" fill="#111"/>')
    if tur == "patlayici":
        cizgi = "".join(f'<line x1="{cx}" y1="{cy + 6}" x2="{cx + 30 * math.cos(a)}" '
                        f'y2="{cy + 6 + 30 * math.sin(a)}" stroke="#111" stroke-width="4"/>'
                        for a in np.linspace(0, 2 * math.pi, 13)[:-1])
        return cizgi + f'<circle cx="{cx}" cy="{cy + 6}" r="13" fill="#111"/>'
    if tur == "asindirici":
        return (f'<rect x="{cx - 26}" y="{cy - 28}" width="10" height="22" fill="#111" transform="rotate(-20 {cx - 21} {cy - 17})"/>'
                f'<rect x="{cx + 14}" y="{cy - 28}" width="10" height="22" fill="#111" transform="rotate(20 {cx + 19} {cy - 17})"/>'
                f'<circle cx="{cx - 16}" cy="{cy}" r="3" fill="#111"/><circle cx="{cx + 14}" cy="{cy}" r="3" fill="#111"/>'
                f'<path d="M{cx - 30},{cy + 26} L{cx - 4},{cy + 26} L{cx - 4},{cy + 14} Q{cx - 10},{cy + 8} {cx - 16},{cy + 14} '
                f'Q{cx - 24},{cy + 8} {cx - 30},{cy + 14} Z" fill="#111"/>'
                f'<path d="M{cx + 4},{cy + 26} L{cx + 30},{cy + 26} L{cx + 30},{cy + 14} L{cx + 18},{cy + 8} '
                f'L{cx + 10},{cy + 16} L{cx + 4},{cy + 12} Z" fill="#111"/>')
    if tur == "gaz":
        return (f'<rect x="{cx - 28}" y="{cy}" width="52" height="20" rx="10" fill="#111"/>'
                f'<rect x="{cx + 22}" y="{cy + 5}" width="9" height="10" fill="#111"/>')
    if tur == "zehir":
        return (f'<line x1="{cx - 24}" y1="{cy + 8}" x2="{cx + 24}" y2="{cy + 30}" stroke="#111" stroke-width="6" stroke-linecap="round"/>'
                f'<line x1="{cx + 24}" y1="{cy + 8}" x2="{cx - 24}" y2="{cy + 30}" stroke="#111" stroke-width="6" stroke-linecap="round"/>'
                f'<circle cx="{cx}" cy="{cy - 12}" r="17" fill="#111"/>'
                f'<rect x="{cx - 9}" y="{cy}" width="18" height="10" fill="#111"/>'
                f'<circle cx="{cx - 6}" cy="{cy - 13}" r="4.5" fill="white"/><circle cx="{cx + 6}" cy="{cy - 13}" r="4.5" fill="white"/>')
    if tur == "unlem":
        return (f'<path d="M{cx - 6},{cy - 30} L{cx + 6},{cy - 30} L{cx + 3},{cy + 10} L{cx - 3},{cy + 10} Z" fill="#111"/>'
                f'<circle cx="{cx}" cy="{cy + 21}" r="6" fill="#111"/>')
    if tur == "saglik":
        yildiz = " ".join(f"{cx + (14 if i % 2 == 0 else 6) * math.cos(-math.pi / 2 + i * math.pi / 6):.1f},"
                          f"{cy + 12 + (14 if i % 2 == 0 else 6) * math.sin(-math.pi / 2 + i * math.pi / 6):.1f}"
                          for i in range(12))
        return (f'<circle cx="{cx}" cy="{cy - 22}" r="9" fill="#111"/>'
                f'<path d="M{cx - 22},{cy + 32} L{cx - 20},{cy - 6} Q{cx},{cy - 14} {cx + 20},{cy - 6} '
                f'L{cx + 22},{cy + 32} Z" fill="#111"/><polygon points="{yildiz}" fill="white"/>')
    if tur == "cevre":
        return (f'<line x1="{cx - 16}" y1="{cy + 8}" x2="{cx - 16}" y2="{cy - 26}" stroke="#111" stroke-width="4"/>'
                f'<line x1="{cx - 16}" y1="{cy - 14}" x2="{cx - 28}" y2="{cy - 24}" stroke="#111" stroke-width="3"/>'
                f'<line x1="{cx - 16}" y1="{cy - 6}" x2="{cx - 4}" y2="{cy - 18}" stroke="#111" stroke-width="3"/>'
                f'<line x1="{cx - 32}" y1="{cy + 10}" x2="{cx + 30}" y2="{cy + 10}" stroke="#111" stroke-width="3"/>'
                f'<path d="M{cx + 2},{cy + 22} Q{cx + 14},{cy + 12} {cx + 24},{cy + 22} Q{cx + 14},{cy + 32} {cx + 2},{cy + 22} Z '
                f'M{cx + 24},{cy + 22} L{cx + 32},{cy + 15} L{cx + 32},{cy + 29} Z" fill="#111"/>')
    return ""


GHS = [("alev", "Yanıcı", "Eter, etanol, hekzan"), ("oksit", "Oksitleyici", "Nitratlar, peroksitler"),
       ("patlayici", "Patlayıcı", "Kuru pikrik asit"), ("asindirici", "Aşındırıcı (korozif)", "Derişik H₂SO₄, NaOH"),
       ("gaz", "Basınçlı gaz", "Argon, azot tüpü"), ("zehir", "Akut zehirli", "Siyanürler, HF"),
       ("unlem", "Tahriş edici / zararlı", "Seyreltik asitler"), ("saglik", "Ciddi sağlık tehlikesi",
                                                                  "Kanserojen: Cr(VI), benzen"),
       ("cevre", "Çevreye zararlı", "Cıva, ağır metaller")]


def svg_ghs():
    sut = 3
    W, H = 690, 3 * 210 + 10
    s = [svg_ac(W, H, 760)]
    for i, (tur, ad, ornek) in enumerate(GHS):
        cx = 115 + (i % sut) * 230
        cy = 85 + (i // sut) * 210
        s.append(f'<rect x="{cx - 50}" y="{cy - 50}" width="100" height="100" fill="white" stroke="#D9241B" '
                 f'stroke-width="9" transform="rotate(45 {cx} {cy})"/>')
        s.append(_ghs_sembol(tur, cx, cy))
        s.append(_yazi(cx, cy + 96, ad, 15, "#222", kalin=True))
        s.append(_yazi(cx, cy + 115, ornek, 13, "#555"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Asit seyreltme: doğru ve yanlış sıra
# ---------------------------------------------------------------------------
def svg_asit_su():
    W, H = 760, 300
    s = [svg_ac(W, H, 820)]
    for i, (baslik, ust, alt, renk, isaret) in enumerate([
            ("DOĞRU: suya asit", "asit", "su", YESIL, "+"), ("YANLIŞ: asite su", "su", "asit", "#D9534F", "!")]):
        ox = 40 + i * 380
        s.append(_yazi(ox + 150, 32, baslik, 19, renk, kalin=True))
        s.append(f'<path d="M{ox + 90},{110} L{ox + 90},{262} Q{ox + 90},{270} {ox + 98},{270} L{ox + 202},{270} '
                 f'Q{ox + 210},{270} {ox + 210},{262} L{ox + 210},{110}" fill="none" {_CIZGI}/>')
        alt_r = SIVI if alt == "su" else "#F2D27A"
        ust_r = "#F2D27A" if ust == "asit" else SIVI
        s.append(f'<rect x="{ox + 92}" y="{190}" width="116" height="78" fill="{alt_r}"/>')
        s.append(_yazi(ox + 150, 240, "SU (bol)" if alt == "su" else "DERİŞİK ASİT", 14, "#222", kalin=True))
        s.append(f'<path d="M{ox + 230},{60} L{ox + 270},{60} L{ox + 262},{110} L{ox + 238},{110} Z" '
                 f'fill="{ust_r}" stroke="{CAM_K}" stroke-width="2" transform="rotate(-35 {ox + 250} {85})"/>')
        s.append(_yazi(ox + 300, 70, "asit" if ust == "asit" else "su", 15, "#222", "start", True))
        s.append(f'<path d="M{ox + 222},{108} Q{ox + 190},{130} {ox + 172},{186}" fill="none" stroke="{ust_r}" '
                 f'stroke-width="5"/>')
        if i == 0:
            s.append(_yazi(ox + 150, 292, "Isı bol suya dağılır, yavaş yavaş ve karıştırarak", 13, "#333"))
        else:
            for dx, dy in [(-30, -40), (-10, -60), (15, -50), (35, -35), (-45, -20)]:
                s.append(f'<circle cx="{ox + 160 + dx}" cy="{180 + dy}" r="5" fill="#F2D27A" stroke="#C99A1E"/>')
            s.append(_yazi(ox + 150, 292, "Su kaynar, asitle birlikte sıçrar!", 13, "#D9534F", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Analitik terazi ve dara
# ---------------------------------------------------------------------------
TERAZI_ADIM = [("0.0000", "Terazi açık, kapılar kapalı, boş. Su terazisi (kabarcık) ortada mı?"),
               ("24.3871", "Temiz, kuru ve oda sıcaklığındaki tartım kabı (saat camı) kefeye kondu."),
               ("0.0000", "DARA (TARE) tuşuna basıldı: kabın kütlesi sıfırlandı."),
               ("1.0052", "Numune eklendi, kapılar kapatıldı, değer sabitlenince okundu: 1,0052 g."),
               ("1.0047…", "HATA: Sıcak numune tartıldı. Isınan hava yükselip kefeyi kaldırır, değer sürekli "
                           "kayar ve gerçeğinden düşük okunur. Önce desikatörde soğutulmalı.")]


def svg_terazi(adim):
    W, H = 640, 330
    s = [svg_ac(W, H, 700)]
    s.append(f'<rect x="120" y="230" width="400" height="70" rx="10" fill="#DDE3EA" stroke="#5F6B7A" stroke-width="2"/>')
    s.append(f'<rect x="150" y="60" width="340" height="170" fill="#EAF3FB" fill-opacity="0.7" stroke="#8A97A8" '
             f'stroke-width="2"/>')
    s.append(_yazi(320, 52, "rüzgârlık (cam kapılar)", 13, "#666"))
    s.append(f'<rect x="270" y="200" width="100" height="8" rx="3" fill="#9AA6B2"/>'
             f'<rect x="314" y="208" width="12" height="22" fill="#9AA6B2"/>')
    ekran, _ = TERAZI_ADIM[adim]
    s.append(f'<rect x="230" y="248" width="180" height="36" rx="5" fill="#1d2b1f"/>')
    s.append(f'<text x="400" y="274" font-family="monospace" font-size="24" fill="#8CF59A" '
             f'text-anchor="end">{ekran} g</text>')
    s.append(f'<rect x="430" y="254" width="60" height="26" rx="6" fill="{TURUNCU if adim == 2 else "#B5BEC8"}"/>')
    s.append(_yazi(460, 272, "DARA", 13, "white", kalin=True))
    s.append(f'<circle cx="170" cy="266" r="14" fill="white" stroke="#555"/>'
             f'<circle cx="170" cy="266" r="5" fill="none" stroke="#555"/>'
             f'<circle cx="170" cy="266" r="4" fill="{SIVI}"/>')
    s.append(_yazi(170, 316, "su terazisi", 12, "#666"))
    if adim >= 1:
        s.append(f'<path d="M265,198 Q320,182 375,198 Z" fill="{CAM}" {_CIZGI}/>')
    if adim >= 3:
        s.append(f'<ellipse cx="320" cy="190" rx="18" ry="6" fill="#E8A33B"/>')
    if adim == 4:
        for dx in (-20, 0, 20):
            s.append(f'<path d="M{320 + dx},180 q8,-14 0,-28 q-8,-14 0,-28" fill="none" stroke="#D9534F" '
                     f'stroke-width="2.5"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Kurut – soğut – tart döngüsü ve kül
# ---------------------------------------------------------------------------
def svg_kurut_tart():
    W, H = 880, 270
    s = [svg_ac(W, H, 900)]
    adim = [("Etüv", ["Etüv", "105 °C", "kurut"], "#D9534F"), ("Desikatör", ["Desikatör", "nem çekmeden", "soğut"], MAVI),
            ("Terazi", ["Analitik terazi", "tart"], GRI_K), ("Karar", ["Önceki tartımla", "aynı mı?"], MOR)]
    for i, (_, yazi, renk) in enumerate(adim):
        x = 30 + i * 215
        s.append(_kutu_svg(x, 50, 170, 100, renk, yazi, 16))
        if i < 3:
            s.append(_ok(x + 172, 100, x + 213, 100))
    s.append(f'<path d="M760,152 L760,210 L115,210 L115,154" fill="none" stroke="{MOR}" stroke-width="2.5" '
             f'stroke-dasharray="8 5" marker-end="url(#okucu)"/>')
    s.append(_yazi(437, 230, "Hayır → tekrar kurut (sabit ağırlığa kadar)", 15, MOR, kalin=True))
    s.append(_yazi(820, 40, "Evet → bitti", 15, YESIL, "end", True))
    s.append(_yazi(440, 262, "Kül tayininde aynı döngü kül fırınında (gıdada genellikle 525–550 °C) yapılır.",
                   14, "#444"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# UV-Vis spektrofotometre
# ---------------------------------------------------------------------------
def _renk_karis(r1, r2, t):
    a = [int(r1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(r2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(round(x + (y - x) * t)):02X}" for x, y in zip(a, b))


def svg_spektro(A, numune_renk="#C2185B", isik_renk="#2E9E44"):
    """A: absorbans. Geçen ışık oranı T = 10^-A."""
    T = 10 ** (-A)
    W, H = 900, 300
    s = [svg_ac(W, H, 920)]
    # lamba
    s.append(f'<circle cx="70" cy="140" r="30" fill="#FFF3B0" stroke="#C9A227" stroke-width="2"/>')
    s.append(f'<path d="M58,150 q6,-22 12,0 q6,-22 12,0" fill="none" stroke="#C9A227" stroke-width="2"/>')
    s.append(_yazi(70, 200, "Işık kaynağı", 15, "#222", kalin=True))
    s.append(f'<rect x="100" y="132" width="90" height="16" fill="#FFF3B0" opacity="0.9"/>')
    # prizma ve renk tayfı
    s.append(f'<polygon points="190,185 240,95 290,185" fill="#EAF3FB" stroke="{CAM_K}" stroke-width="2"/>')
    tayf = ["#8E24AA", "#3949AB", "#1E88E5", "#2E9E44", "#FDD835", "#FB8C00", "#E53935"]
    for i, c in enumerate(tayf):
        s.append(f'<line x1="265" y1="140" x2="330" y2="{100 + i * 13}" stroke="{c}" stroke-width="4"/>')
    s.append(f'<rect x="330" y="92" width="10" height="38" fill="#333"/><rect x="330" y="151" width="10" height="45" fill="#333"/>')
    s.append(_yazi(270, 225, "Monokromatör", 15, "#222", kalin=True))
    s.append(_yazi(270, 244, "(tek dalga boyu seçer)", 12, "#555"))
    s.append(f'<rect x="340" y="134" width="120" height="12" fill="{isik_renk}"/>')
    s.append(_yazi(400, 125, "I₀", 18, "#222", kalin=True))
    # küvet
    dolgu = _renk_karis("#FFFFFF", numune_renk, min(1.0, A / 1.6))
    s.append(f'<rect x="460" y="80" width="80" height="120" fill="{dolgu}" stroke="{CAM_K}" stroke-width="3"/>')
    s.append(_yazi(500, 225, "Küvet (numune)", 15, "#222", kalin=True))
    s.append(f'<line x1="460" y1="250" x2="540" y2="250" stroke="#555" stroke-width="1.5" marker-end="url(#okucu)" '
             f'marker-start="url(#okucu)"/>')
    s.append(_yazi(500, 270, "b = 1 cm", 13, "#555"))
    # geçen ışık
    kal = max(1.0, 12 * T)
    s.append(f'<rect x="540" y="{140 - kal / 2}" width="130" height="{kal}" fill="{isik_renk}" '
             f'opacity="{0.25 + 0.75 * T:.2f}"/>')
    s.append(_yazi(605, 125, "I", 18, "#222", kalin=True))
    # dedektör ve ekran
    s.append(f'<rect x="670" y="105" width="50" height="70" rx="6" fill="#5F6B7A"/>')
    s.append(_yazi(695, 200, "Dedektör", 15, "#222", kalin=True))
    s.append(_ok(722, 140, 752, 140))
    s.append(f'<rect x="755" y="88" width="130" height="104" rx="8" fill="#1d2b1f"/>')
    s.append(f'<text x="820" y="125" font-family="monospace" font-size="20" fill="#8CF59A" text-anchor="middle">A={A:.3f}</text>')
    s.append(f'<text x="820" y="160" font-family="monospace" font-size="20" fill="#8CF59A" text-anchor="middle">%T={100 * T:.1f}</text>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# El refraktometresi: görüş alanı
# ---------------------------------------------------------------------------
def svg_refrakto(brix):
    W, H = 640, 330
    cx, cy, r = 220, 165, 140
    ust, alt = 32, 0                         # skala 0 (altta) – 32 (üstte)
    y0, y1 = cy + 115, cy - 115
    yb = y0 + (y1 - y0) * (brix - alt) / (ust - alt)
    s = [svg_ac(W, H, 680)]
    s.append(f'<defs><clipPath id="goris"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>')
    s.append(f'<g clip-path="url(#goris)"><rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{yb - cy + r}" '
             f'fill="#2F6DB5"/><rect x="{cx - r}" y="{yb}" width="{2 * r}" height="{cy + r - yb}" fill="#F7FAFD"/>')
    for v in range(0, 33):
        y = y0 + (y1 - y0) * v / (ust - alt)
        L = 34 if v % 5 == 0 else 18
        renk = "white" if y < yb else "#222"
        s.append(f'<line x1="{cx + 10}" y1="{y:.1f}" x2="{cx + 10 + L}" y2="{y:.1f}" stroke="{renk}" stroke-width="1.6"/>')
        if v % 5 == 0:
            s.append(_yazi(cx + 52, y + 5, str(v), 15, renk, "start", True))
    s.append("</g>")
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#333" stroke-width="8"/>')
    s.append(f'<line x1="{cx - r + 10}" y1="{yb:.1f}" x2="{cx + 4}" y2="{yb:.1f}" stroke="{TURUNCU}" stroke-width="3"/>')
    s.append(_yazi(470, 120, "Mavi ile beyazın", 16, "#222", kalin=True))
    s.append(_yazi(470, 142, "sınır çizgisi skalada", 16, "#222", kalin=True))
    s.append(_yazi(470, 164, "nereyi kesiyorsa", 16, "#222", kalin=True))
    s.append(_yazi(470, 200, f"okunan: {brix:.1f} °Brix", 22, TURUNCU, kalin=True))
    s.append(_yazi(470, 236, "(göz merceğinden", 13, "#666"))
    s.append(_yazi(470, 254, "bakınca görülen alan)", 13, "#666"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Kjeldahl: yakma – damıtma – titrasyon
# ---------------------------------------------------------------------------
def svg_kjeldahl(aktif):
    bas = ["1 · Yakma", "2 · Damıtma", "3 · Titrasyon"]
    paneller = range(3) if aktif is None else [aktif]
    W, H = (900, 340) if aktif is None else (300, 340)
    s = [svg_ac(W, H, 920 if aktif is None else 420)]
    for j, i in enumerate(paneller):
        ox = 10 + j * 300 - (0 if aktif is None else 0)
        ox = 10 + j * 300
        op = 1
        s.append(f'<g opacity="{op}"><rect x="{ox}" y="10" width="280" height="320" rx="14" fill="#FAFBFD" '
                 f'stroke="{TURUNCU if aktif == i else "#D5DCE4"}" stroke-width="{4 if aktif == i else 1.5}"/>')
        s.append(_yazi(ox + 140, 42, bas[i], 19, "#222", kalin=True))
        if i == 0:
            s.append(f'<rect x="{ox + 50}" y="230" width="180" height="76" rx="6" fill="#8A97A8"/>')
            for k in range(3):
                tx = ox + 85 + k * 55
                s.append(f'<path d="M{tx - 9},{90} L{tx - 9},{262} A9,9 0 0 0 {tx + 9},{262} L{tx + 9},{90}" '
                         f'fill="{CAM}" {_CIZGI}/><rect x="{tx - 8}" y="200" width="16" height="64" fill="#5D4037"/>')
                s.append(f'<path d="M{tx},{84} q8,-10 0,-20 q-8,-10 0,-20" fill="none" stroke="#9E9E9E" stroke-width="2"/>')
            s.append(f'<g>{_yazi(ox + 140, 298, "ısıtma bloğu", 13, "white", kalin=True)}</g>')
            s.append(_yazi(ox + 140, 322, "H₂SO₄ + katalizör → NH₄⁺", 14, "#333"))
        elif i == 1:
            s.append(f'<circle cx="{ox + 70}" cy="230" r="38" fill="#FFF3E0" stroke="{CAM_K}" stroke-width="2"/>')
            s.append(_yazi(ox + 70, 236, "+ NaOH", 13, "#222", kalin=True))
            s.append(f'<path d="M{ox + 70},{192} L{ox + 70},{110} L{ox + 200},{150}" fill="none" stroke="{CAM_K}" stroke-width="5"/>')
            s.append(f'<rect x="{ox + 110}" y="{108}" width="70" height="26" rx="10" fill="#B3E5FC" stroke="{CAM_K}" '
                     f'transform="rotate(17 {ox + 145} {121})"/>')
            s.append(_yazi(ox + 150, 95, "soğutucu", 12, "#555"))
            s.append(f'<path d="M{ox + 200},150 L{ox + 200},235" stroke="{CAM_K}" stroke-width="4"/>')
            s.append(f'<path d="M{ox + 185},220 L{ox + 175},290 L{ox + 235},290 L{ox + 225},220 Z" fill="#E1F5FE" '
                     f'stroke="{CAM_K}" stroke-width="2"/>')
            s.append(_yazi(ox + 205, 312, "borik asit", 13, "#333"))
            s.append(_yazi(ox + 110, 175, "NH₃ ↑", 15, MOR, kalin=True))
        else:
            s.append(_buret(ox + 140, 225))
            s.append(_erlen(ox + 140, 300))
            s.append(_yazi(ox + 225, 110, "standart", 13, "#333")); s.append(_yazi(ox + 225, 126, "HCl", 13, "#333"))
            s.append(_yazi(ox + 230, 280, "renk", 13, "#333"))
            s.append(_yazi(ox + 230, 296, "dönüşü", 13, "#333"))
        s.append("</g>")
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# AAS ve ICP-OES
# ---------------------------------------------------------------------------
def svg_aas_icp():
    W, H = 900, 380
    s = [svg_ac(W, H, 920)]
    s.append(_yazi(20, 34, "AAS: atomlar ışığı SOĞURUR", 18, MAVI, "start", True))
    s.append(_kutu_svg(20, 60, 150, 80, MAVI, ["Oyuk katot", "lambası (Fe)"], 14))
    s.append(f'<rect x="170" y="94" width="430" height="12" fill="#FDD835" opacity="0.8"/>')
    s.append(_alev(300, 85, 1.4).replace("#111", "#FB8C00"))
    s.append(f'<rect x="250" y="112" width="100" height="12" rx="3" fill="#5F6B7A"/>')
    s.append(_yazi(300, 150, "alev: numune atomlaşır", 13, "#333"))
    s.append(_kutu_svg(440, 60, 140, 80, GRI_K, ["Monokromatör"], 14))
    s.append(_ok(582, 100, 625, 100))
    s.append(_kutu_svg(630, 60, 110, 80, GRI_K, ["Dedektör"], 14))
    s.append(_yazi(820, 95, "ışık azaldı", 14, "#D9534F", kalin=True))
    s.append(_yazi(820, 115, "→ derişim", 14, "#D9534F", kalin=True))
    s.append(f'<line x1="20" y1="185" x2="880" y2="185" stroke="#D5DCE4" stroke-width="2"/>')
    s.append(_yazi(20, 222, "ICP-OES: plazmadaki atomlar ışık YAYAR", 18, MOR, "start", True))
    s.append(f'<path d="M130,350 L130,290 Q130,240 160,230 Q190,240 190,290 L190,350 Z" fill="#E1BEE7" stroke="{MOR}" stroke-width="2"/>')
    s.append(f'<ellipse cx="160" cy="262" rx="20" ry="32" fill="white" opacity="0.8"/>')
    s.append(_yazi(160, 372, "argon plazması ~6000–10 000 K", 13, "#333"))
    tayf = ["#3949AB", "#1E88E5", "#2E9E44", "#FDD835", "#E53935"]
    for i, c in enumerate(tayf):
        s.append(f'<line x1="195" y1="270" x2="440" y2="{238 + i * 18}" stroke="{c}" stroke-width="3"/>')
    s.append(_kutu_svg(440, 230, 160, 100, GRI_K, ["Spektrometre", "çok dalga boyu", "aynı anda"], 14))
    s.append(_ok(602, 280, 640, 280))
    s.append(_kutu_svg(645, 240, 230, 80, MOR, ["K, Ca, Mg, Fe, Zn…", "hepsi birlikte"], 14))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Soxhlet
# ---------------------------------------------------------------------------
def svg_soxhlet():
    W, H = 720, 470
    s = [svg_ac(W, H, 720)]
    cx = 200
    s.append(f'<rect x="{cx - 28}" y="20" width="56" height="110" rx="8" fill="#B3E5FC" stroke="{CAM_K}" stroke-width="2"/>')
    s.append(f'<rect x="{cx - 10}" y="30" width="20" height="90" fill="white" stroke="{CAM_K}"/>')
    s.append(_yazi(cx + 45, 60, "soğutucu (su girişi / çıkışı)", 14, "#222", "start"))
    s.append(f'<rect x="{cx - 38}" y="130" width="76" height="140" fill="{CAM}" stroke="{CAM_K}" stroke-width="2.5"/>')
    s.append(f'<rect x="{cx - 36}" y="200" width="72" height="68" fill="#FFF3B0" opacity="0.8"/>')
    s.append(f'<rect x="{cx - 20}" y="160" width="40" height="100" rx="6" fill="#F4F1EA" stroke="#8D6E63" stroke-width="2"/>')
    s.append(_yazi(cx + 85, 150, "kartuş: kurutulmuş, öğütülmüş numune", 14, "#222", "start"))
    s.append(f'<path d="M{cx + 38},255 L{cx + 58},255 L{cx + 58},185 L{cx + 70},185 L{cx + 70},300 L{cx + 20},300" '
             f'fill="none" stroke="{CAM_K}" stroke-width="3"/>')
    s.append(_yazi(cx + 85, 235, "sifon: dolunca boşaltır", 14, "#222", "start"))
    s.append(f'<path d="M{cx - 52},{20 + 290} L{cx - 52},{150} " stroke="{CAM_K}" stroke-width="3" fill="none"/>')
    s.append(_yazi(cx - 60, 230, "buhar", 13, "#555", "end"))
    s.append(f'<circle cx="{cx}" cy="350" r="52" fill="{CAM}" stroke="{CAM_K}" stroke-width="2.5"/>')
    s.append(f'<path d="M{cx - 48},365 A52,52 0 0 0 {cx + 48},365 Z" fill="#FFE082"/>')
    s.append(_yazi(cx, 385, "çözücü + yağ", 12, "#222", kalin=True))
    s.append(f'<rect x="{cx - 70}" y="400" width="140" height="40" rx="6" fill="#D9534F"/>')
    s.append(_yazi(cx, 426, "ısıtıcı (alev YOK)", 14, "white", kalin=True))
    s.append(_yazi(cx + 80, 345, "Çözücü buharlaşır → soğutucuda yoğunlaşır →", 13, "#333", "start"))
    s.append(_yazi(cx + 80, 363, "numuneyi yıkar → yağı alıp geri akar.", 13, "#333", "start"))
    s.append(_yazi(cx + 80, 381, "Döngü saatlerce tekrarlanır.", 13, "#333", "start"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Kromatografi kolonu
# ---------------------------------------------------------------------------
KROM_BILESEN = [("Bileşen 1", "#E53935", 2.0), ("Bileşen 2", "#FDD835", 1.4), ("Bileşen 3", "#1E88E5", 1.0)]


def svg_kolon(t):
    """t: 0..1 zaman. Her bileşen kendi hızıyla ilerler."""
    W, H = 360, 470
    ust, alt = 60, 400
    s = [svg_ac(W, H, 380)]
    s.append(_yazi(120, 36, "karışım ↓  hareketli faz", 13, "#333"))
    s.append(f'<rect x="90" y="{ust}" width="60" height="{alt - ust}" fill="#F4F1EA" stroke="{CAM_K}" stroke-width="2.5"/>')
    for (ad, renk, hiz) in KROM_BILESEN:
        y = ust + 10 + (alt - ust + 40) * t * hiz
        if y < alt:
            s.append(f'<rect x="92" y="{y:.1f}" width="56" height="{14 + 20 * t:.1f}" fill="{renk}" opacity="0.8"/>')
    s.append(f'<rect x="80" y="{alt + 8}" width="80" height="34" rx="6" fill="#5F6B7A"/>')
    s.append(_yazi(120, alt + 30, "dedektör", 13, "white", kalin=True))
    s.append(_yazi(200, 140, "durağan faz", 14, "#333", "start", True))
    s.append(_yazi(200, 160, "(kolon dolgusu)", 13, "#555", "start"))
    s.append(_yazi(200, 220, "Durağan faza az", 13, "#333", "start"))
    s.append(_yazi(200, 238, "tutunan önce çıkar", 13, "#333", "start"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Numune alma akışı
# ---------------------------------------------------------------------------
def svg_numune():
    W, H = 590, 500
    s = [svg_ac(W, H, 640)]
    s.append(f'<rect x="30" y="70" width="150" height="130" rx="20" fill="#E3E8EF" stroke="#5F6B7A" stroke-width="2.5"/>')
    s.append(f'<rect x="34" y="100" width="142" height="96" rx="16" fill="#FFFDF5"/>')
    s.append(f'<line x1="105" y1="40" x2="105" y2="170" stroke="#5F6B7A" stroke-width="4"/>'
             f'<path d="M80,170 L130,170" stroke="#5F6B7A" stroke-width="6"/>')
    s.append(_yazi(105, 228, "1 · Karıştır", 16, "#222", kalin=True))
    s.append(_yazi(105, 248, "≤400 L: ≥5 dk · >400 L: ≥10 dk", 12, "#555"))
    s.append(_ok(190, 135, 240, 135))
    s.append(f'<path d="M270,70 L270,60 L300,60 L300,70 L312,90 L312,200 L258,200 L258,90 Z" fill="#FFFDF5" '
             f'stroke="{CAM_K}" stroke-width="2.5"/>')
    s.append(f'<rect x="250" y="44" width="58" height="18" rx="4" fill="#D9534F"/>')
    s.append(_yazi(285, 228, "2 · Al ve kapat", 16, "#222", kalin=True))
    s.append(_yazi(285, 248, "~200 mL, çift örnek", 12, "#555"))
    s.append(_ok(330, 135, 380, 135))
    s.append(f'<rect x="390" y="80" width="150" height="100" rx="6" fill="#FFF8DC" stroke="#8A6D1E" stroke-width="2" '
             f'stroke-dasharray="6 4"/>')
    for i, t in enumerate(["Sahibi: …", "Tür: çiğ süt", "Yer: …", "Tarih: …", "Sıcaklık: 4 °C"]):
        s.append(_yazi(400, 100 + i * 17, t, 12, "#333", "start"))
    s.append(_yazi(465, 228, "3 · Etiketle", 16, "#222", kalin=True))
    s.append(f'<path d="M465,240 L465,262 L120,262 L120,300" fill="none" stroke="#555" stroke-width="2.2" marker-end="url(#okucu)"/>')
    s.append('<g transform="translate(-550,250)">')
    s.append(f'<rect x="610" y="85" width="120" height="100" rx="10" fill="#E1F5FE" stroke="{MAVI}" stroke-width="2.5"/>')
    s.append(_yazi(670, 130, "0–5 °C", 18, MAVI, kalin=True))
    s.append(_yazi(670, 228, "4 · Soğuk taşı", 16, "#222", kalin=True))
    s.append(_ok(735, 135, 780, 135))
    s.append(_kutu_svg(785, 85, 100, 100, YESIL, ["LAB", "≤ 24 saat"], 16))
    s.append(_yazi(835, 228, "5 · Ulaştır", 16, "#222", kalin=True))
    s.append("</g></svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Yaprak analizi adımları
# ---------------------------------------------------------------------------
def svg_yaprak():
    W, H = 900, 200
    s = [svg_ac(W, H, 920)]
    adim = [("1 · Örnekleme", "doğru dönem,", "doğru yaprak"), ("2 · Yıkama", "hızlıca", "saf su"),
            ("3 · Kurutma", "etüvde", "65–70 °C"), ("4 · Öğütme", "değirmen,", "ince toz"),
            ("5 · Analiz", "Kjeldahl, spektro,", "AAS / ICP")]
    for i, (a, b, c) in enumerate(adim):
        x = 15 + i * 178
        s.append(_kutu_svg(x, 40, 150, 120, YESIL, [a, b, c], 15))
        if i < 4:
            s.append(_ok(x + 152, 100, x + 175, 100))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Ek malzemeler: cam, plastik, porselen / metal
# ---------------------------------------------------------------------------
PLASTIK = "#F3EBD3"          # yarı saydam plastik (PP) dolgu
PLASTIK_K = "#9A8A5C"


def _petri(cx, by):
    return (f'<ellipse cx="{cx}" cy="{by - 18}" rx="56" ry="14" fill="{CAM}" stroke="{CAM_K}" stroke-width="2"/>'
            f'<path d="M{cx - 56},{by - 18} L{cx - 56},{by - 6} A56,14 0 0 0 {cx + 56},{by - 6} L{cx + 56},{by - 18}" '
            f'fill="{CAM}" stroke="{CAM_K}" stroke-width="2"/>'
            f'<ellipse cx="{cx}" cy="{by - 13}" rx="46" ry="9" fill="#F7E9A8"/>'
            f'<circle cx="{cx - 14}" cy="{by - 14}" r="3" fill="#E8A33B"/><circle cx="{cx + 12}" cy="{by - 11}" r="2.5" fill="#E8A33B"/>'
            f'<ellipse cx="{cx}" cy="{by - 40}" rx="60" ry="15" fill="none" stroke="{CAM_K}" stroke-width="2" '
            f'stroke-dasharray="5 3"/>' + _yazi(cx, by - 60, "kapak", 12, "#777"))


def _baget(cx, by):
    return (f'<rect x="{cx - 4}" y="{by - 150}" width="8" height="150" rx="4" fill="{CAM}" stroke="{CAM_K}" stroke-width="2" '
            f'transform="rotate(12 {cx} {by - 75})"/>')


def _pastor(cx, by):
    return (f'<rect x="{cx - 8}" y="{by - 160}" width="16" height="34" rx="7" fill="#D9534F" stroke="#8B2E2B" stroke-width="1.5"/>'
            f'<path d="M{cx - 6},{by - 128} L{cx - 6},{by - 70} L{cx - 1.5},{by - 60} L{cx - 1.5},{by} L{cx + 1.5},{by} '
            f'L{cx + 1.5},{by - 60} L{cx + 6},{by - 70} L{cx + 6},{by - 128} Z" fill="{CAM}" {_CIZGI}/>')


def _amber_sise(cx, by):
    return (f'<rect x="{cx - 32}" y="{by - 100}" width="64" height="100" rx="10" fill="#B5651D" fill-opacity="0.75" '
            f'stroke="#6D3A0E" stroke-width="2"/>'
            f'<rect x="{cx - 14}" y="{by - 124}" width="28" height="26" fill="#B5651D" fill-opacity="0.75" stroke="#6D3A0E" stroke-width="2"/>'
            f'<rect x="{cx - 18}" y="{by - 140}" width="36" height="18" rx="3" fill="#2B5DA8"/>'
            f'<rect x="{cx - 24}" y="{by - 72}" width="48" height="34" rx="3" fill="white"/>' +
            _yazi(cx, by - 51, "ışıktan", 10, "#333") + _yazi(cx, by - 40, "korur", 10, "#333"))


def _damlalik(cx, by):
    return (f'<rect x="{cx - 26}" y="{by - 80}" width="52" height="80" rx="10" fill="{CAM}" stroke="{CAM_K}" stroke-width="2"/>'
            f'<rect x="{cx - 24}" y="{by - 42}" width="48" height="40" rx="8" fill="{SIVI}"/>'
            f'<rect x="{cx - 11}" y="{by - 96}" width="22" height="18" fill="#333"/>'
            f'<path d="M{cx - 9},{by - 96} Q{cx},{by - 136} {cx + 9},{by - 96} Z" fill="#D9534F"/>'
            f'<line x1="{cx}" y1="{by - 80}" x2="{cx}" y2="{by - 20}" stroke="{CAM_K}" stroke-width="3"/>')


def _cam_kuvet(cx, by, renk=CAM, ad="kuvars"):
    return (f'<rect x="{cx - 18}" y="{by - 110}" width="36" height="110" rx="3" fill="{renk}" stroke="{CAM_K}" stroke-width="2"/>'
            f'<rect x="{cx - 15}" y="{by - 70}" width="30" height="66" fill="{SIVI}"/>'
            f'<rect x="{cx - 18}" y="{by - 110}" width="8" height="110" fill="#888" opacity="0.35"/>'
            f'<rect x="{cx + 10}" y="{by - 110}" width="8" height="110" fill="#888" opacity="0.35"/>' +
            _yazi(cx + 34, by - 90, "mat", 11, "#777", "start") + _yazi(cx + 34, by - 77, "yüz", 11, "#777", "start"))


def _falkon(cx, by):
    return (f'<rect x="{cx - 17}" y="{by - 160}" width="34" height="20" rx="3" fill="#2B5DA8"/>'
            f'<path d="M{cx - 15},{by - 140} L{cx - 15},{by - 40} L{cx - 3},{by} L{cx + 3},{by} L{cx + 15},{by - 40} '
            f'L{cx + 15},{by - 140} Z" fill="{PLASTIK}" stroke="{PLASTIK_K}" stroke-width="2"/>'
            f'<path d="M{cx - 14},{by - 80} L{cx - 14},{by - 40} L{cx - 3},{by - 2} L{cx + 3},{by - 2} L{cx + 14},{by - 40} '
            f'L{cx + 14},{by - 80} Z" fill="{SIVI}"/>' + _cizgiler(cx + 14, by - 130, by - 45, 8, 7, 4) +
            f'<rect x="{cx - 13}" y="{by - 128}" width="12" height="30" fill="white" opacity="0.8"/>')


def _ependorf(cx, by):
    return (f'<path d="M{cx - 13},{by - 90} L{cx - 13},{by - 45} L{cx - 3},{by} L{cx + 3},{by} L{cx + 13},{by - 45} '
            f'L{cx + 13},{by - 90} Z" fill="{PLASTIK}" stroke="{PLASTIK_K}" stroke-width="2"/>'
            f'<path d="M{cx - 12},{by - 45} L{cx - 3},{by - 2} L{cx + 3},{by - 2} L{cx + 12},{by - 45} Z" fill="{SIVI}"/>'
            f'<rect x="{cx - 16}" y="{by - 98}" width="32" height="9" rx="2" fill="{PLASTIK}" stroke="{PLASTIK_K}" stroke-width="2"/>'
            f'<path d="M{cx + 16},{by - 94} Q{cx + 30},{by - 104} {cx + 26},{by - 122}" fill="none" stroke="{PLASTIK_K}" stroke-width="2"/>'
            f'<rect x="{cx + 12}" y="{by - 140}" width="30" height="9" rx="2" fill="{PLASTIK}" stroke="{PLASTIK_K}" '
            f'stroke-width="2" transform="rotate(-60 {cx + 27} {by - 135})"/>' + _yazi(cx, by - 120, "1,5 mL", 12, "#555"))


def _uclar(cx, by):
    s = f'<rect x="{cx - 52}" y="{by - 40}" width="104" height="40" rx="4" fill="#3B6FB6" fill-opacity="0.85"/>'
    s += f'<rect x="{cx - 56}" y="{by - 48}" width="112" height="10" rx="2" fill="#2B5DA8"/>'
    for i in range(6):
        x = cx - 42 + i * 17
        s += (f'<path d="M{x - 5},{by - 100} L{x + 5},{by - 100} L{x + 1},{by - 46} L{x - 1},{by - 46} Z" '
              f'fill="#F2E8B5" stroke="#B8A44A" stroke-width="1.2"/>')
    return s


def _piset(cx, by):
    return (f'<rect x="{cx - 30}" y="{by - 100}" width="60" height="100" rx="14" fill="#F4F7FA" stroke="{PLASTIK_K}" stroke-width="2"/>'
            f'<rect x="{cx - 28}" y="{by - 48}" width="56" height="46" rx="12" fill="{SIVI}"/>'
            f'<rect x="{cx - 14}" y="{by - 116}" width="28" height="18" rx="3" fill="#E8A33B"/>'
            f'<path d="M{cx},{by - 116} L{cx},{by - 140} L{cx + 40},{by - 130}" fill="none" stroke="#9AA6B2" stroke-width="4"/>'
            f'<rect x="{cx - 20}" y="{by - 84}" width="40" height="22" rx="3" fill="white" stroke="#ccc"/>' +
            _yazi(cx, by - 68, "saf su", 11, "#2B5DA8", kalin=True))


def _plastik_pastor(cx, by):
    return (f'<ellipse cx="{cx}" cy="{by - 135}" rx="13" ry="22" fill="{PLASTIK}" stroke="{PLASTIK_K}" stroke-width="2"/>'
            f'<path d="M{cx - 5},{by - 114} L{cx - 5},{by - 20} L{cx - 1.5},{by} L{cx + 1.5},{by} L{cx + 5},{by - 20} '
            f'L{cx + 5},{by - 114} Z" fill="{PLASTIK}" stroke="{PLASTIK_K}" stroke-width="2"/>' +
            _cizgiler(cx + 5, by - 100, by - 40, 6, 6, 3))


def _numune_kabi(cx, by):
    return (f'<rect x="{cx - 34}" y="{by - 24 - 70}" width="68" height="16" rx="4" fill="#D9534F"/>'
            f'<path d="M{cx - 32},{by - 78} L{cx - 28},{by} L{cx + 28},{by} L{cx + 32},{by - 78} Z" fill="{PLASTIK}" '
            f'stroke="{PLASTIK_K}" stroke-width="2"/>'
            f'<rect x="{cx - 22}" y="{by - 58}" width="44" height="26" fill="white" stroke="#ccc"/>' +
            _yazi(cx, by - 41, "etiket", 11, "#555") + _yazi(cx, by - 108, "steril", 12, "#2B5DA8", kalin=True))


def _plastik_beher(cx, by):
    return (_beher(cx, by).replace(CAM_K, PLASTIK_K).replace('fill="none"', f'fill="{PLASTIK}" fill-opacity="0.5"') +
            f'<path d="M{cx + 35},{by - 70} Q{cx + 56},{by - 70} {cx + 56},{by - 45} Q{cx + 56},{by - 25} {cx + 35},{by - 25}" '
            f'fill="none" stroke="{PLASTIK_K}" stroke-width="5"/>' + _yazi(cx - 6, by - 52, "PP", 13, "#6B5B2E", kalin=True))


def _havan(cx, by):
    return (f'<path d="M{cx - 50},{by - 60} Q{cx - 48},{by} {cx},{by} Q{cx + 48},{by} {cx + 50},{by - 60} Z" '
            f'fill="#F4F1EA" stroke="#777" stroke-width="2.5"/>'
            f'<ellipse cx="{cx}" cy="{by - 60}" rx="50" ry="9" fill="#E8E2D6" stroke="#777" stroke-width="2"/>'
            f'<rect x="{cx - 2}" y="{by - 140}" width="16" height="90" rx="8" fill="#F4F1EA" stroke="#777" stroke-width="2" '
            f'transform="rotate(25 {cx + 6} {by - 95})"/>')


def _spatul(cx, by):
    return (f'<rect x="{cx - 3}" y="{by - 150}" width="6" height="130" fill="#B0B8C1" stroke="#6B7580" stroke-width="1.2"/>'
            f'<path d="M{cx - 10},{by - 20} L{cx + 10},{by - 20} L{cx + 6},{by} L{cx - 6},{by} Z" fill="#B0B8C1" stroke="#6B7580"/>'
            f'<ellipse cx="{cx}" cy="{by - 154}" rx="11" ry="7" fill="#B0B8C1" stroke="#6B7580"/>')


def _masa(cx, by):
    return (f'<path d="M{cx - 4},{by - 150} Q{cx - 30},{by - 80} {cx - 10},{by}" fill="none" stroke="#6B7580" stroke-width="6"/>'
            f'<path d="M{cx + 4},{by - 150} Q{cx + 30},{by - 80} {cx + 10},{by}" fill="none" stroke="#6B7580" stroke-width="6"/>'
            f'<circle cx="{cx}" cy="{by - 150}" r="7" fill="#6B7580"/>'
            f'<path d="M{cx - 14},{by - 2} Q{cx},{by + 6} {cx + 14},{by - 2}" fill="none" stroke="#6B7580" stroke-width="4"/>')


def _termometre(cx, by):
    return (f'<rect x="{cx - 6}" y="{by - 160}" width="12" height="140" rx="6" fill="{CAM}" stroke="{CAM_K}" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{by - 14}" r="12" fill="#D9534F" stroke="{CAM_K}" stroke-width="2"/>'
            f'<rect x="{cx - 2}" y="{by - 90}" width="4" height="70" fill="#D9534F"/>' +
            _cizgiler(cx + 6, by - 150, by - 30, 8, 7, 4))


def _tup_sporu(cx, by):
    s = (f'<rect x="{cx - 60}" y="{by - 80}" width="120" height="10" fill="#C9D3DD" stroke="#5F6B7A"/>'
         f'<rect x="{cx - 60}" y="{by - 10}" width="120" height="10" fill="#C9D3DD" stroke="#5F6B7A"/>'
         f'<rect x="{cx - 60}" y="{by - 80}" width="6" height="80" fill="#5F6B7A"/><rect x="{cx + 54}" y="{by - 80}" width="6" height="80" fill="#5F6B7A"/>')
    for i, c in enumerate([SIVI, "#F7C6C7", "#C8E6C9", None]):
        x = cx - 36 + i * 24
        s += (f'<path d="M{x - 8},{by - 120} L{x - 8},{by - 18} A8,8 0 0 0 {x + 8},{by - 18} L{x + 8},{by - 120}" '
              f'fill="{c or CAM}" {_CIZGI}/>')
    return s


def _bek(cx, by):
    return (f'<rect x="{cx - 34}" y="{by - 12}" width="68" height="12" rx="4" fill="#5F6B7A"/>'
            f'<rect x="{cx - 7}" y="{by - 110}" width="14" height="100" fill="#9AA6B2" stroke="#5F6B7A"/>'
            f'<rect x="{cx - 10}" y="{by - 40}" width="20" height="10" fill="#5F6B7A"/>'
            f'<path d="M{cx},{by - 160} Q{cx + 16},{by - 130} {cx + 6},{by - 112} L{cx - 6},{by - 112} Q{cx - 16},{by - 130} {cx},{by - 160} Z" fill="#5C8DF6"/>'
            f'<path d="M{cx},{by - 145} Q{cx + 8},{by - 126} {cx + 3},{by - 114} L{cx - 3},{by - 114} Q{cx - 8},{by - 126} {cx},{by - 145} Z" fill="#B3D4FF"/>')


EK_CAM = {
    "petri": ("Petri kabı", _petri, "Kapaklı, yayvan kap. Mikroorganizma <b>besiyerinde üretmek</b> için; cam ya da tek "
              "kullanımlık plastik olabilir.", "Mikrobiyolojide steril olmalı; ters çevrilerek inkübe edilir."),
    "baget": ("Cam baget", _baget, "Cam karıştırma çubuğu. Çözeltiyi karıştırmak, sıvıyı akıtırken yönlendirmek için.",
              "Ölçü balonunda ya da ince cam kapta sert vurulmaz; camı kırabilir."),
    "pastor": ("Pastör pipeti (cam)", _pastor, "Ucuna lastik takılan ince cam damlalık; az miktarda sıvıyı damla damla aktarır.",
               "Ölçüm aracı değildir; hacim ölçmez."),
    "amber": ("Amber şişe (kahverengi)", _amber_sise, "Işığa duyarlı kimyasal ve çözeltileri (ör. gümüş nitrat, bazı "
              "standartlar) <b>ışıktan korumak</b> için.", "Etiketine ad, derişim ve tarih yazılır."),
    "damlalik": ("Damlalıklı şişe", _damlalik, "İndikatör ve ayıraçları damla damla kullanmak için.",
                 "Damlalık başka şişeye konmaz; karışma olur."),
    "kuvet": ("Kuvars küvet", lambda cx, by: _cam_kuvet(cx, by), "Spektrofotometrede numunenin konduğu kap. "
              "<b>Kuvars</b> küvet UV bölgesinde de ışığı geçirir.", "Mat yüzünden tutulur; şeffaf yüze dokunulmaz."),
}
PLASTIK_MALZEME = {
    "falkon": ("Falkon tüpü", _falkon, "15 ya da 50 mL'lik, vidalı kapaklı, konik dipli plastik tüp. <b>Santrifüj</b>, "
               "numune saklama ve karıştırma için.", "Taksimatı yaklaşıktır; santrifüjde karşılıklı tüpler eşit doldurulur."),
    "ependorf": ("Eppendorf tüpü (mikrosantrifüj)", _ependorf, "0,5–2 mL'lik kapaklı küçük tüp; mikrolitre düzeyinde "
                 "numune, DNA ve ayıraçlar için.", "Kapak iyice kapatılmadan santrifüje konmaz."),
    "uclar": ("Pipet uçları", _uclar, "Mikropipetin tek kullanımlık uçları; hacme göre renk ve boyları farklıdır "
              "(ör. 10, 200, 1000 µL).", "Her numunede yeni uç kullanılır; uca elle dokunulmaz."),
    "piset": ("Piset (yıkama şişesi)", _piset, "Sıkınca ince bir akıntı veren plastik şişe; saf su ile <b>durulama</b> ve "
              "son hacme tamamlama için.", "İçindekinin adı (saf su, etanol) mutlaka yazılır."),
    "plastik_pastor": ("Plastik pastör pipeti", _plastik_pastor, "Tek parça, sıkma hazneli tek kullanımlık damlalık.",
                       "Taksimatı kabadır; hassas hacim için kullanılmaz."),
    "numune_kabi": ("Numune kabı", _numune_kabi, "Vidalı kapaklı, steril ya da temiz plastik kap; süt, su, toprak "
                    "örneği almak için.", "Etiketlenir; bakteriyolojik örnekte steril kap kullanılır."),
    "plastik_beher": ("Plastik (PP) beher", _plastik_beher, "Kırılmaz, hafif polipropilen beher. Hidroflorik asit ve "
                      "iz element çalışmalarında camın yerine kullanılır.", "Isıtılmaz; organik çözücülerin çoğuna "
                      "dayanıksız olabilir."),
    "puar": CAM_MALZEME["puar"],
    "mikropipet": CAM_MALZEME["mikropipet"],
}
DIGER_MALZEME = {
    "kroze": CAM_MALZEME["kroze"],
    "havan": ("Havan ve tokmak (porselen)", _havan, "Katı numuneyi <b>ezmek ve toz hâline getirmek</b> için.",
              "Kuru ve temiz olmalı; numuneler arasında iyice temizlenir."),
    "spatul": ("Spatül (metal)", _spatul, "Katı kimyasalı şişeden almak ve tartım kabına aktarmak için.",
               "Temiz ve kuru olmalı; iki farklı kimyasala aynı spatül temizlenmeden sokulmaz."),
    "masa": ("Maşa", _masa, "Sıcak kroze, beher ve tüpleri tutmak için.", "Kül fırınından kroze maşayla, ısıya dayanıklı "
             "eldivenle alınır."),
    "termometre": ("Termometre", _termometre, "Sıvıların ve ortamın sıcaklığını ölçer.", "Yuvarlanmayacak şekilde konur; "
                   "cıvalı termometre kırılırsa cıva dökülmesi gibi davranılır."),
    "tup_sporu": ("Tüp sporu (tüplük)", _tup_sporu, "Deney tüplerini dik tutmak için.", "Tüpler etiketli ve sırayla dizilir."),
    "bek": ("Bek (Bunsen) alevi", _bek, "Gazla çalışan ısıtıcı; mavi alev en sıcak bölgedir.",
            "Yanıcı çözücülerin (eter, alkol, hekzan) yakınında yakılmaz; kullanılmadığında gaz vanası kapatılır."),
}
CAM_MALZEME_TUM = {k: v for k, v in CAM_MALZEME.items() if k not in ("kroze", "puar", "mikropipet")}
CAM_MALZEME_TUM.update(EK_CAM)
MALZEME_GRUP = {"Cam": CAM_MALZEME_TUM, "Plastik ve lastik": PLASTIK_MALZEME, "Porselen, metal ve diğer": DIGER_MALZEME}
TUM_MALZEME = {}
for _g in MALZEME_GRUP.values():
    TUM_MALZEME.update(_g)


def svg_malzeme(sozluk, secili=None):
    anahtar = list(sozluk)
    sut = 4
    w, h = 170, 215
    satir = (len(anahtar) + sut - 1) // sut
    s = [svg_ac(w * sut + 20, h * satir + 20, 900)]
    for i, k in enumerate(anahtar):
        ad, f, _, _ = sozluk[k]
        x = 10 + (i % sut) * w
        y = 10 + (i // sut) * h
        sec = (k == secili)
        s.append(f'<rect x="{x + 4}" y="{y + 4}" width="{w - 8}" height="{h - 8}" rx="12" '
                 f'fill="{"#FFF5E0" if sec else "#FAFBFD"}" stroke="{TURUNCU if sec else "#D5DCE4"}" '
                 f'stroke-width="{4 if sec else 1.2}"/>')
        s.append(f'<g opacity="{1 if (secili is None or sec) else 0.45}">{f(x + w / 2, y + 172)}</g>')
        kisa = ad if len(ad) <= 22 else ad.split(" (")[0]
        boy = 15 if len(kisa) <= 17 else 13
        s.append(_yazi(x + w / 2, y + 198, kisa, boy, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# İş güvenliği işaretleri (ISO 7010 benzeri, sadeleştirilmiş)
# ---------------------------------------------------------------------------
def _sym_simsek(cx, cy, r="#111"):
    return f'<path d="M{cx + 6},{cy - 30} L{cx - 14},{cy + 4} L{cx},{cy + 4} L{cx - 8},{cy + 30} L{cx + 16},{cy - 6} L{cx + 2},{cy - 6} Z" fill="{r}"/>'


def _sym_sicak(cx, cy, r="#111"):
    s = f'<rect x="{cx - 24}" y="{cy + 18}" width="48" height="6" fill="{r}"/>'
    for dx in (-14, 0, 14):
        s += f'<path d="M{cx + dx},{cy + 12} q7,-9 0,-18 q-7,-9 0,-18" fill="none" stroke="{r}" stroke-width="3.5"/>'
    return s


def _sym_bio(cx, cy, r="#111"):
    s = ""
    for a in (90, 210, 330):
        x = cx + 11 * math.cos(math.radians(a))
        y = cy - 11 * math.sin(math.radians(a))
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="none" stroke="{r}" stroke-width="5"/>'
    return s + f'<circle cx="{cx}" cy="{cy}" r="5" fill="{r}"/>'


def _sym_radyo(cx, cy, r="#111"):
    s = f'<circle cx="{cx}" cy="{cy}" r="5" fill="{r}"/>'
    for a in (90, 210, 330):
        a1, a2 = math.radians(a - 30), math.radians(a + 30)
        p = [(cx + R * math.cos(t), cy - R * math.sin(t)) for R, t in ((9, a1), (26, a1), (26, a2), (9, a2))]
        s += (f'<path d="M{p[0][0]:.1f},{p[0][1]:.1f} L{p[1][0]:.1f},{p[1][1]:.1f} A26,26 0 0 0 {p[2][0]:.1f},{p[2][1]:.1f} '
              f'L{p[3][0]:.1f},{p[3][1]:.1f} A9,9 0 0 1 {p[0][0]:.1f},{p[0][1]:.1f} Z" fill="{r}"/>')
    return s


def _sym_lazer(cx, cy, r="#111"):
    s = f'<line x1="{cx - 28}" y1="{cy}" x2="{cx}" y2="{cy}" stroke="{r}" stroke-width="4"/>'
    for a in range(0, 360, 30):
        s += (f'<line x1="{cx + 6 * math.cos(math.radians(a)) + 4}" y1="{cy + 6 * math.sin(math.radians(a))}" '
              f'x2="{cx + 18 * math.cos(math.radians(a)) + 4}" y2="{cy + 18 * math.sin(math.radians(a))}" stroke="{r}" stroke-width="3"/>')
    return s


def _sym_gozluk(cx, cy, r="white"):
    return (f'<circle cx="{cx}" cy="{cy - 6}" r="17" fill="{r}"/>'
            f'<rect x="{cx - 26}" y="{cy - 10}" width="52" height="16" rx="8" fill="#1F5AA6" stroke="{r}" stroke-width="3"/>'
            f'<circle cx="{cx - 11}" cy="{cy - 2}" r="6" fill="{r}"/><circle cx="{cx + 11}" cy="{cy - 2}" r="6" fill="{r}"/>'
            f'<path d="M{cx - 18},{cy + 12} Q{cx},{cy + 32} {cx + 18},{cy + 12}" fill="{r}"/>')


def _sym_eldiven(cx, cy, r="white"):
    return (f'<path d="M{cx - 16},{cy + 28} L{cx - 16},{cy - 6} L{cx - 22},{cy - 16} L{cx - 18},{cy - 20} L{cx - 10},{cy - 10} '
            f'L{cx - 10},{cy - 30} L{cx - 4},{cy - 30} L{cx - 4},{cy - 10} L{cx - 2},{cy - 34} L{cx + 4},{cy - 34} L{cx + 4},{cy - 10} '
            f'L{cx + 8},{cy - 30} L{cx + 14},{cy - 30} L{cx + 12},{cy - 8} L{cx + 18},{cy - 22} L{cx + 23},{cy - 20} L{cx + 16},{cy + 4} '
            f'L{cx + 16},{cy + 28} Z" fill="{r}"/>')


def _sym_onluk(cx, cy, r="white"):
    return (f'<path d="M{cx - 10},{cy - 32} L{cx - 26},{cy - 22} L{cx - 30},{cy + 30} L{cx + 30},{cy + 30} L{cx + 26},{cy - 22} '
            f'L{cx + 10},{cy - 32} L{cx},{cy - 10} Z" fill="{r}"/>'
            f'<line x1="{cx}" y1="{cy - 10}" x2="{cx}" y2="{cy + 30}" stroke="#1F5AA6" stroke-width="2"/>')


def _sym_maske(cx, cy, r="white"):
    return (f'<circle cx="{cx}" cy="{cy - 8}" r="22" fill="{r}"/>'
            f'<path d="M{cx - 16},{cy - 2} Q{cx},{cy + 24} {cx + 16},{cy - 2} Z" fill="#1F5AA6" stroke="#1F5AA6"/>'
            f'<line x1="{cx - 16}" y1="{cy - 2}" x2="{cx - 24}" y2="{cy - 10}" stroke="#1F5AA6" stroke-width="2"/>'
            f'<line x1="{cx + 16}" y1="{cy - 2}" x2="{cx + 24}" y2="{cy - 10}" stroke="#1F5AA6" stroke-width="2"/>')


def _sym_kitap(cx, cy, r="white"):
    return (f'<path d="M{cx},{cy - 18} Q{cx - 16},{cy - 26} {cx - 30},{cy - 20} L{cx - 30},{cy + 20} Q{cx - 16},{cy + 14} {cx},{cy + 22} '
            f'Q{cx + 16},{cy + 14} {cx + 30},{cy + 20} L{cx + 30},{cy - 20} Q{cx + 16},{cy - 26} {cx},{cy - 18} Z" fill="{r}"/>'
            f'<line x1="{cx}" y1="{cy - 18}" x2="{cx}" y2="{cy + 22}" stroke="#1F5AA6" stroke-width="2.5"/>' +
            _yazi(cx, cy - 32, "i", 18, r, kalin=True))


def _sym_sigara(cx, cy):
    return (f'<rect x="{cx - 28}" y="{cy - 4}" width="44" height="10" fill="#111"/><rect x="{cx + 18}" y="{cy - 4}" width="8" height="10" fill="#111"/>'
            f'<path d="M{cx + 20},{cy - 10} q6,-8 0,-16" fill="none" stroke="#111" stroke-width="3"/>')


def _sym_kibrit(cx, cy):
    return (_alev(cx, cy - 6, 0.8) + f'<rect x="{cx - 3}" y="{cy + 12}" width="6" height="20" fill="#111"/>')


def _sym_yemek(cx, cy):
    return (f'<path d="M{cx - 26},{cy - 14} L{cx - 4},{cy - 14} L{cx - 7},{cy + 22} L{cx - 23},{cy + 22} Z" fill="#111"/>'
            f'<line x1="{cx + 12}" y1="{cy - 24}" x2="{cx + 12}" y2="{cy + 26}" stroke="#111" stroke-width="4"/>'
            f'<path d="M{cx + 5},{cy - 24} L{cx + 5},{cy - 8} Q{cx + 12},{cy - 2} {cx + 19},{cy - 8} L{cx + 19},{cy - 24}" '
            f'fill="none" stroke="#111" stroke-width="3"/>')


def _sym_su_yangin(cx, cy):
    return (_alev(cx + 8, cy + 6, 0.7) +
            f'<path d="M{cx - 30},{cy - 24} Q{cx - 8},{cy - 30} {cx + 2},{cy - 10}" fill="none" stroke="#111" stroke-width="4"/>'
            f'<circle cx="{cx - 2}" cy="{cy - 4}" r="2.5" fill="#111"/><circle cx="{cx + 6}" cy="{cy - 6}" r="2.5" fill="#111"/>')


def _sym_arti(cx, cy, r="white"):
    return f'<rect x="{cx - 8}" y="{cy - 24}" width="16" height="48" fill="{r}"/><rect x="{cx - 24}" y="{cy - 8}" width="48" height="16" fill="{r}"/>'


def _sym_gozdusu(cx, cy, r="white"):
    return (f'<path d="M{cx - 28},{cy + 8} Q{cx - 6},{cy - 14} {cx + 16},{cy + 8} Q{cx - 6},{cy + 26} {cx - 28},{cy + 8} Z" fill="{r}"/>'
            f'<circle cx="{cx - 6}" cy="{cy + 8}" r="6" fill="#2E8B57"/>'
            f'<path d="M{cx + 22},{cy - 28} Q{cx + 30},{cy - 10} {cx + 14},{cy - 2}" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<path d="M{cx + 10},{cy - 30} Q{cx + 20},{cy - 14} {cx + 4},{cy - 6}" fill="none" stroke="{r}" stroke-width="3"/>')


def _sym_dus(cx, cy, r="white"):
    s = (f'<path d="M{cx - 24},{cy - 30} L{cx + 10},{cy - 30} L{cx + 10},{cy - 22}" fill="none" stroke="{r}" stroke-width="4"/>'
         f'<path d="M{cx},{cy - 22} L{cx + 20},{cy - 22} L{cx + 16},{cy - 16} L{cx + 4},{cy - 16} Z" fill="{r}"/>'
         f'<circle cx="{cx - 6}" cy="{cy - 4}" r="6" fill="{r}"/>'
         f'<path d="M{cx - 14},{cy + 30} L{cx - 12},{cy + 4} L{cx},{cy + 4} L{cx + 2},{cy + 30} Z" fill="{r}"/>')
    for dx in (6, 10, 14, 18):
        s += f'<line x1="{cx + dx}" y1="{cy - 12}" x2="{cx + dx - 4}" y2="{cy + 6}" stroke="{r}" stroke-width="1.5"/>'
    return s


def _sym_cikis(cx, cy, r="white"):
    return (f'<rect x="{cx + 6}" y="{cy - 28}" width="22" height="56" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<circle cx="{cx - 12}" cy="{cy - 20}" r="6" fill="{r}"/>'
            f'<path d="M{cx - 14},{cy - 12} L{cx - 4},{cy + 4} L{cx - 18},{cy + 26} M{cx - 4},{cy + 4} L{cx + 6},{cy + 22} '
            f'M{cx - 12},{cy - 6} L{cx - 26},{cy + 2} M{cx - 10},{cy - 6} L{cx + 2},{cy - 10}" stroke="{r}" stroke-width="5" '
            f'fill="none" stroke-linecap="round"/>' + _ok(cx - 30, cy + 34, cx + 26, cy + 34).replace("#555", r))


def _sym_sondurucu(cx, cy, r="white"):
    return (f'<rect x="{cx - 10}" y="{cy - 18}" width="20" height="46" rx="6" fill="{r}"/>'
            f'<rect x="{cx - 4}" y="{cy - 28}" width="8" height="10" fill="{r}"/>'
            f'<path d="M{cx + 4},{cy - 26} L{cx + 20},{cy - 30} L{cx + 24},{cy - 20}" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<path d="M{cx - 10},{cy - 26} Q{cx - 26},{cy - 22} {cx - 24},{cy + 4}" fill="none" stroke="{r}" stroke-width="3"/>')


def _sym_alarm(cx, cy, r="white"):
    return (f'<rect x="{cx - 20}" y="{cy - 20}" width="40" height="40" rx="4" fill="none" stroke="{r}" stroke-width="3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="9" fill="{r}"/>'
            f'<path d="M{cx - 26},{cy - 26} q-6,6 0,12 M{cx + 26},{cy - 26} q6,6 0,12" stroke="{r}" stroke-width="3" fill="none"/>')


ISARETLER = {
    "Uyarı (tehlike)": ("sarı üçgen, siyah çerçeve", [
        ("Genel uyarı", lambda cx, cy: _ghs_sembol("unlem", cx, cy + 6)),
        ("Elektrik tehlikesi", _sym_simsek), ("Sıcak yüzey", _sym_sicak), ("Biyolojik tehlike", _sym_bio),
        ("Radyasyon", _sym_radyo), ("Lazer ışını", _sym_lazer),
        ("Yanıcı madde", lambda cx, cy: _ghs_sembol("alev", cx, cy + 2)),
        ("Aşındırıcı madde", lambda cx, cy: _ghs_sembol("asindirici", cx, cy + 4)),
        ("Zehirli madde", lambda cx, cy: _ghs_sembol("zehir", cx, cy + 2))]),
    "Zorunluluk (emir)": ("mavi daire, beyaz sembol", [
        ("Koruyucu gözlük tak", _sym_gozluk), ("Eldiven giy", _sym_eldiven), ("Önlük giy", _sym_onluk),
        ("Maske tak", _sym_maske), ("Talimatı oku", _sym_kitap)]),
    "Yasak": ("kırmızı çerçeveli beyaz daire, çapraz çizgi", [
        ("Sigara içilmez", _sym_sigara), ("Açık alev yasak", _sym_kibrit), ("Yemek ve içmek yasak", _sym_yemek),
        ("Su ile söndürme yasak", _sym_su_yangin)]),
    "Acil durum / ilk yardım": ("yeşil kare, beyaz sembol", [
        ("İlk yardım", _sym_arti), ("Göz duşu", _sym_gozdusu), ("Acil (güvenlik) duşu", _sym_dus), ("Acil çıkış", _sym_cikis)]),
    "Yangın ekipmanı": ("kırmızı kare, beyaz sembol", [
        ("Yangın söndürücü", _sym_sondurucu), ("Yangın alarm butonu", _sym_alarm)]),
}


def _isaret_ciz(grup, cx, cy, fn):
    if grup == "Uyarı (tehlike)":
        return (f'<path d="M{cx},{cy - 52} L{cx + 58},{cy + 46} L{cx - 58},{cy + 46} Z" fill="#F7C600" stroke="#111" '
                f'stroke-width="7" stroke-linejoin="round"/>' + fn(cx, cy + 14))
    if grup == "Zorunluluk (emir)":
        return f'<circle cx="{cx}" cy="{cy}" r="50" fill="#1F5AA6"/>' + fn(cx, cy)
    if grup == "Yasak":
        return (f'<circle cx="{cx}" cy="{cy}" r="46" fill="white"/>' + fn(cx, cy) +
                f'<circle cx="{cx}" cy="{cy}" r="46" fill="none" stroke="#D9241B" stroke-width="9"/>'
                f'<line x1="{cx - 32}" y1="{cy - 32}" x2="{cx + 32}" y2="{cy + 32}" stroke="#D9241B" stroke-width="9"/>')
    renk = "#2E8B57" if grup.startswith("Acil") else "#D9241B"
    return f'<rect x="{cx - 48}" y="{cy - 48}" width="96" height="96" rx="6" fill="{renk}"/>' + fn(cx, cy)


def svg_isaretler(grup):
    _, liste = ISARETLER[grup]
    sut = 3
    satir = (len(liste) + sut - 1) // sut
    W, H = 690, satir * 175 + 10
    s = [svg_ac(W, H, 720)]
    for i, (ad, fn) in enumerate(liste):
        cx = 115 + (i % sut) * 230
        cy = 72 + (i // sut) * 175
        s.append(_isaret_ciz(grup, cx, cy, fn))
        s.append(_yazi(cx, cy + 82, ad, 15, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


def svg_isaret_turleri():
    W, H = 900, 230
    s = [svg_ac(W, H, 920)]
    gruplar = list(ISARETLER)
    for i, g in enumerate(gruplar):
        cx = 90 + i * 180
        fn = ISARETLER[g][1][0][1]
        s.append(_isaret_ciz(g, cx, 85, fn))
        s.append(_yazi(cx, 168, g.split(" (")[0].split(" /")[0], 16, "#222", kalin=True))
        s.append(_yazi(cx, 188, ISARETLER[g][0].split(",")[0], 13, "#555"))
        if "," in ISARETLER[g][0]:
            s.append(_yazi(cx, 205, ISARETLER[g][0].split(",", 1)[1].strip(), 13, "#555"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# NFPA 704 elması
# ---------------------------------------------------------------------------
def svg_nfpa(saglik, yanici, reaktif, ozel):
    W, H = 420, 340
    cx, cy, a = 210, 170, 62
    s = [svg_ac(W, H, 420)]
    parca = [(cx, cy - a, "#2F6DB5", "", ""), (cx - a, cy, "#2F6DB5", str(saglik), "Sağlık"),
             (cx, cy - a, "#D9241B", str(yanici), "Yanıcılık"), (cx + a, cy, "#F7C600", str(reaktif), "Reaktiflik"),
             (cx, cy + a, "white", ozel, "Özel")]
    for x, y, renk, deger, ad in parca[1:]:
        s.append(f'<rect x="{x - a * 0.7071:.1f}" y="{y - a * 0.7071:.1f}" width="{a * 1.4142:.1f}" height="{a * 1.4142:.1f}" '
                 f'fill="{renk}" stroke="#111" stroke-width="3" transform="rotate(45 {x} {y})"/>')
        s.append(_yazi(x, y + 15, deger, 40 if len(deger) < 3 else 26, "#111" if renk != "#2F6DB5" else "white", kalin=True))
        if ad == "Özel" and deger == "W":
            s.append(f'<line x1="{x - 24}" y1="{y + 1}" x2="{x + 24}" y2="{y + 1}" stroke="#111" stroke-width="4"/>')
    s.append(_yazi(cx - a - 66, cy + 6, "Sağlık", 14, "#2F6DB5", "end", True))
    s.append(_yazi(cx, cy - 2 * a - 12, "Yanıcılık", 14, "#D9241B", kalin=True))
    s.append(_yazi(cx + a + 66, cy + 6, "Reaktiflik", 14, "#B58900", "start", True))
    s.append(_yazi(cx, cy + 2 * a + 26, "Özel uyarı", 14, "#333", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Metrik sistem merdiveni
# ---------------------------------------------------------------------------
ONEKLER = [("kilo", "k", 3), ("hekto", "h", 2), ("deka", "da", 1), ("", "", 0), ("desi", "d", -1), ("santi", "c", -2),
           ("mili", "m", -3), ("mikro", "µ", -6), ("nano", "n", -9), ("piko", "p", -12)]


def svg_merdiven(temel="g", bas=None, son=None):
    W, H = 900, 470
    s = [svg_ac(W, H, 920)]
    n = len(ONEKLER)
    sw = 84
    us = {o[2]: o for o in ONEKLER}
    ib = next((i for i, o in enumerate(ONEKLER) if o[2] == bas), None)
    ison = next((i for i, o in enumerate(ONEKLER) if o[2] == son), None)
    for i, (ad, sem, us_) in enumerate(ONEKLER):
        x = 20 + i * sw
        y = 40 + i * 30
        aralik = ib is not None and ison is not None and min(ib, ison) <= i <= max(ib, ison)
        renk = TURUNCU if i in (ib, ison) else ("#FFE8C2" if aralik else ("#DDE7F5" if us_ != 0 else "#C8E6C9"))
        s.append(f'<rect x="{x}" y="{y}" width="{sw - 6}" height="{H - y - 60}" rx="6" fill="{renk}" stroke="#7A8AA0"/>')
        etiket = f"{sem}{temel}"
        s.append(_yazi(x + (sw - 6) / 2, y + 30, etiket, 24, "#111", kalin=True))
        s.append(_yazi(x + (sw - 6) / 2, y + 52, ad if ad else "temel birim", 13, "#333"))
        s.append(_yazi(x + (sw - 6) / 2, y + 72, f"10{_ust(us_)}", 15, "#555"))
    for i in range(n - 1):
        x = 20 + (i + 1) * sw + (sw - 6) / 2
        y = 40 + (i + 1) * 30 - 8
        fark = ONEKLER[i][2] - ONEKLER[i + 1][2]
        s.append(_yazi(x, y, f"×{10 ** fark:g}", 13 if fark == 1 else 14, "#2B5DA8" if fark == 1 else "#D9534F", kalin=True))
    s.append(_yazi(450, H - 22, "Merdivenden aşağı inerken (küçük birime) ÇARP · yukarı çıkarken (büyük birime) BÖL",
                   16, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


def _ust(k):
    tablo_ = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(k).translate(tablo_)


# ---------------------------------------------------------------------------
# Hacim okuma şemaları
# ---------------------------------------------------------------------------
def svg_meniskus_turleri():
    W, H = 790, 368
    s = [svg_ac(W, H, 820)]
    paneller = [("Su ve sulu çözeltiler", "İç bükey (çukur)", "ALT kenardan oku", SIVI, 1),
                ("Cıva", "Dış bükey (tümsek)", "ÜST kenardan oku", "#9EA7B3", -1),
                ("Koyu / opak sıvı", "Alt kenar görünmez", "ÜST kenardan oku", "#5D2B4A", 1)]
    for i, (ad, sekil, kural, renk, yon) in enumerate(paneller):
        ox = 30 + i * 290
        cx, ym = ox + 120, 170
        s.append(_yazi(cx, 34, ad, 21, "#222", kalin=True))
        if i == 0:
            s.append(f'<rect x="{cx - 70}" y="{ym + 6}" width="140" height="44" fill="#222"/>')
            s.append(_yazi(cx + 92, ym + 34, "okuma kartı", 12, "#555", "start"))
        s.append(f'<rect x="{cx - 50}" y="60" width="100" height="250" fill="{CAM}" opacity="0.6"/>')
        if yon == 1:
            s.append(f'<path d="M{cx - 50},{ym - 16} Q{cx},{ym + 16} {cx + 50},{ym - 16} L{cx + 50},310 L{cx - 50},310 Z" '
                     f'fill="{renk}" opacity="{0.85 if i == 0 else 1}"/>')
        else:
            s.append(f'<path d="M{cx - 50},{ym + 14} Q{cx},{ym - 18} {cx + 50},{ym + 14} L{cx + 50},310 L{cx - 50},310 Z" '
                     f'fill="{renk}"/>')
        s.append(f'<line x1="{cx - 50}" y1="60" x2="{cx - 50}" y2="310" {_CIZGI}/>'
                 f'<line x1="{cx + 50}" y1="60" x2="{cx + 50}" y2="310" {_CIZGI}/>')
        yo = (ym if i == 0 else (ym - 2 if i == 1 else ym - 16))
        s.append(f'<line x1="{cx - 80}" y1="{yo}" x2="{cx + 80}" y2="{yo}" stroke="{TURUNCU}" stroke-width="3" '
                 f'stroke-dasharray="7 4"/>')
        s.append(_yazi(cx, 334, sekil, 17, "#555"))
        s.append(_yazi(cx, 356, kural, 18, "#D9534F" if i else YESIL, kalin=True))
    s.append("</svg>")
    return "".join(s)


def svg_olcek(tur, deger, goster=True):
    """tur: 'mezur' (100 mL, bölme 1 mL, değer yukarı artar) ya da 'buret' (50 mL, bölme 0,1 mL, aşağı artar)."""
    if tur == "mezur":
        bolme, etiket, orta, ppu, yon = 1.0, 10, 5, 13.0, 1
    else:
        bolme, etiket, orta, ppu, yon = 0.1, 1, 0.5, 150.0, -1
    W, H = 520, 420
    cx, cy = 230, 210
    s = [svg_ac(W, H, 520)]

    def y(v):
        return cy - (v - deger) * ppu * yon

    s.append(f'<rect x="{cx - 110}" y="20" width="220" height="{H - 40}" fill="{CAM}" opacity="0.7"/>')
    alt_y = H - 20 if yon == 1 else H - 20
    s.append(f'<path d="M{cx - 110},{cy - 12} Q{cx},{cy + 12} {cx + 110},{cy - 12} L{cx + 110},{alt_y} L{cx - 110},{alt_y} Z" '
             f'fill="{SIVI}"/>')
    v0 = deger - (cy - 20) / ppu
    v1 = deger + (H - 20 - cy) / ppu
    vmin, vmax = min(v0, v1) - bolme, max(v0, v1) + bolme
    n0 = int(math.floor(vmin / bolme))
    n1 = int(math.ceil(vmax / bolme))
    for n in range(n0, n1 + 1):
        v = round(n * bolme, 4)
        if v < 0:
            continue
        yy = y(v)
        if not 20 <= yy <= H - 20:
            continue
        uzun = abs(v / etiket - round(v / etiket)) < 1e-6
        orta_ = abs(v / orta - round(v / orta)) < 1e-6
        L = 70 if uzun else (46 if orta_ else 28)
        s.append(f'<line x1="{cx - 110}" y1="{yy:.1f}" x2="{cx - 110 + L}" y2="{yy:.1f}" stroke="#222" '
                 f'stroke-width="{2.2 if uzun else 1.3}"/>')
        if uzun:
            s.append(_yazi(cx - 122, yy + 6, f"{v:g}".replace(".", ","), 18, "#222", "end", True))
    s.append(f'<line x1="{cx - 110}" y1="20" x2="{cx - 110}" y2="{H - 20}" {_CIZGI}/>'
             f'<line x1="{cx + 110}" y1="20" x2="{cx + 110}" y2="{H - 20}" {_CIZGI}/>')
    s.append(_yazi(cx + 122, 44, "mezür (100 mL)" if tur == "mezur" else "büret (50 mL)", 16, "#222", "start", True))
    s.append(_yazi(cx + 122, 68, "değer yukarı artar ↑" if yon == 1 else "değer aşağı artar ↓", 15, "#2B5DA8", "start", True))
    s.append(_yazi(cx + 122, 92, "en küçük bölme:", 14, "#555", "start"))
    s.append(_yazi(cx + 122, 112, f"{str(bolme).replace('.', ',')} mL", 14, "#555", "start", True))
    if goster:
        s.append(f'<line x1="{cx - 120}" y1="{cy}" x2="{cx + 130}" y2="{cy}" stroke="{TURUNCU}" stroke-width="2.5" '
                 f'stroke-dasharray="7 4"/>')
    s.append("</svg>")
    return "".join(s)


def svg_etiket_kodlari():
    W, H = 900, 340
    s = [svg_ac(W, H, 920)]
    kod = [("A", ["Sınıf", "(A hassas, B)"], 90), ("10 mL", ["Nominal", "hacim"], 220), ("± 0,02 mL", ["Hata payı", "(tolerans)"], 365),
           ("Ex", ["Akıtılan", "hacim (TD)"], 510), ("20 °C", ["Kalibrasyon", "sıcaklığı"], 645), ("5 s", ["Bekleme", "süresi"], 780)]
    s.append(f'<rect x="30" y="100" width="840" height="70" rx="35" fill="{CAM}" stroke="{CAM_K}" stroke-width="2.5"/>')
    for k, acik, x in kod:
        s.append(_yazi(x, 145, k, 26, "#1F3F73", kalin=True))
        s.append(f'<line x1="{x}" y1="176" x2="{x}" y2="206" stroke="#888" stroke-width="1.5"/>')
        for j, parca in enumerate(acik):
            s.append(_yazi(x, 228 + j * 20, parca, 16, "#333", kalin=(j == 0)))
    s.append(_yazi(450, 56, "Tam pipetin üzerindeki yazılar ne anlatır?", 22, "#222", kalin=True))
    s.append(_yazi(450, 300, "Balon joje: “In” (TC) → İÇERDİĞİ hacme göre ayarlı.", 16, "#D9534F", kalin=True))
    s.append(_yazi(450, 324, "Pipet ve büret: “Ex” (TD) → AKITTIĞI hacme göre ayarlı.", 16, "#D9534F", kalin=True))
    s.append("</svg>")
    return "".join(s)


MP_ADIM = [("1 · Ayarla", "Hacmi ayar düğmesiyle ayarla; cihazın aralığının dışına çevirme.", 0, False, 0),
           ("2 · 1. durağa bas", "Uç havadayken pistonu BİRİNCİ DURAĞA kadar bastır.", 1, False, 0),
           ("3 · Daldır ve çek", "Ucu sıvıya 2–3 mm daldır, pistonu YAVAŞÇA bırak; sıvı uca dolar.", 0, True, 1),
           ("4 · Boşalt", "Ucu kabın çeperine değdir, pistonu 1. durağa bastır.", 1, False, 0.15),
           ("5 · 2. durak", "İKİNCİ DURAĞA kadar bastır: kalan son damla da üflenir.", 2, False, 0),
           ("6 · Ucu at", "Ucu atma düğmesiyle atık kabına at; sonraki numuneye yeni uç.", 0, False, 0)]


def svg_mikropipet_adim(i):
    ad, _, durak, sivi_icinde, dolu = MP_ADIM[i]
    W, H = 520, 380
    s = [svg_ac(W, H, 520)]
    cx, by = 200, 330
    piston = {0: 0, 1: 22, 2: 38}[durak]
    s.append(f'<rect x="{cx - 5}" y="{40 + piston}" width="10" height="34" rx="2" fill="#5F6B7A"/>')
    s.append(f'<rect x="{cx - 13}" y="{34 + piston}" width="26" height="8" rx="4" fill="#3B6FB6"/>')
    s.append(f'<path d="M{cx - 22},{74} L{cx + 22},{74} L{cx + 18},{230} L{cx + 8},{250} L{cx - 8},{250} L{cx - 18},{230} Z" '
             f'fill="#DDE3EA" stroke="{CAM_K}" stroke-width="2"/>')
    s.append(f'<rect x="{cx - 13}" y="110" width="26" height="30" rx="3" fill="#1d2b1f"/>')
    s.append(f'<text x="{cx}" y="131" font-family="monospace" font-size="14" fill="#8CF59A" text-anchor="middle">100</text>')
    s.append(f'<path d="M{cx + 22},96 L{cx + 38},104 L{cx + 22},112" fill="#5F6B7A"/>')
    if i < 5:
        s.append(f'<path d="M{cx - 8},250 L{cx + 8},250 L{cx + 2},{by} L{cx - 2},{by} Z" fill="#F2E8B5" stroke="#B8A44A" stroke-width="1.5"/>')
        if dolu:
            yd = by - 70 * dolu
            s.append(f'<path d="M{cx - 2 - 6 * dolu},{yd} L{cx + 2 + 6 * dolu},{yd} L{cx + 2},{by - 2} L{cx - 2},{by - 2} Z" fill="{SIVI}"/>')
    else:
        s.append(f'<path d="M{cx + 40},300 L{cx + 56},300 L{cx + 50},370 L{cx + 46},370 Z" fill="#F2E8B5" stroke="#B8A44A" '
                 f'stroke-width="1.5" transform="rotate(30 {cx + 48} 330)"/>')
        s.append(_ok(cx + 10, 260, cx + 40, 296))
    if sivi_icinde:
        s.append(f'<rect x="{cx - 50}" y="{by - 8}" width="100" height="40" fill="{SIVI}" opacity="0.8"/>')
    if i == 3:
        s.append(f'<path d="M{cx - 1},{by + 4} q-3,8 0,12 q3,-4 0,-12" fill="{SIVI}"/>')
    if i == 4:
        s.append(f'<circle cx="{cx}" cy="{by + 10}" r="4" fill="{SIVI}"/>')
    # durak göstergesi
    gx = 380
    for k, (et, yy) in enumerate([("dinlenme", 60), ("1. durak", 150), ("2. durak", 230)]):
        aktif = (k == durak)
        s.append(f'<line x1="{gx - 30}" y1="{yy}" x2="{gx + 30}" y2="{yy}" stroke="{TURUNCU if aktif else "#AAB4BF"}" stroke-width="{5 if aktif else 2}"/>')
        s.append(_yazi(gx + 40, yy + 5, et, 15, "#222" if aktif else "#888", "start", aktif))
    s.append(f'<line x1="{gx}" y1="60" x2="{gx}" y2="230" stroke="#AAB4BF" stroke-width="2"/>')
    s.append(_yazi(gx, 30, "Piston nerede?", 15, "#222", kalin=True))
    s.append(_yazi(W / 2, H - 6, ad, 18, "#222", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ===========================================================================
# VERİ: sözlük
# ===========================================================================
TERIMLER = [
    ("Doğruluk", "Ölçülen değerin gerçek değere yakınlığı."),
    ("Kesinlik", "Tekrarlanan ölçümlerin birbirine yakınlığı (tekrarlanabilirlik)."),
    ("Sistematik hata", "Hep aynı yöne sapan hata; tekrarla yok olmaz, kalibrasyonla düzeltilir."),
    ("Rastgele hata", "Ölçümden ölçüme değişen hata; tekrar ve ortalamayla azaltılır."),
    ("Kaba hata", "Dikkatsizlikten doğan hata: numune karışması, virgül hatası."),
    ("Kalibrasyon", "Cihazın gösterdiği değeri bilinen bir standartla karşılaştırıp gerekirse ayarlamak."),
    ("İzlenebilirlik", "Ölçüm sonucunun sertifikalı referans malzemeler aracılığıyla ulusal standarda bağlanması."),
    ("Sertifikalı referans malzeme", "Değeri belgelenmiş, kontrol ve kalibrasyonda kullanılan malzeme."),
    ("Kör (blank)", "Numune dışında her şeyi içeren çözelti; cihazı sıfırlamak ve arka planı düzeltmek için."),
    ("Dara", "Kabın kütlesini teraziden düşmek (sıfırlamak)."),
    ("Sabit ağırlık", "Art arda iki kurutma–tartım arasında kütlenin artık değişmemesi."),
    ("Menisküs", "Dar kaptaki sıvının kavisli yüzeyi; sulu çözeltilerde alt kenarından okunur."),
    ("Paralaks hatası", "Göz hizasında bakılmadığı için yanlış okuma."),
    ("A sınıfı cam malzeme", "Hata payı (toleransı) daha küçük, analizde tercih edilen cam malzeme."),
    ("Balon joje", "Tek bir hacmi hassas ölçen, standart çözelti hazırlamada kullanılan ölçü balonu."),
    ("Büret", "Titrasyonda harcanan çözelti hacmini ölçen musluklu, taksimatlı cam boru."),
    ("Puar", "Pipete sıvı çekmeye yarayan lastik pompa; ağızla pipet çekilmez."),
    ("Desikatör", "Nem çekici madde içeren, kurutulmuş numuneyi nem çekmeden soğutan kap."),
    ("Etüv", "Kurutma ve sabit sıcaklıkta bekletme için ısıtıcı dolap (genellikle 250 °C'ye kadar)."),
    ("Kül fırını", "1100 °C'ye kadar ısınan, kül tayininde kullanılan fırın (muffle)."),
    ("Kroze", "Kül tayininde kullanılan, yüksek sıcaklığa dayanıklı porselen kap."),
    ("Çeker ocak", "Zehirli ve uçucu buharları ortamdan uzaklaştıran havalandırmalı çalışma kabini."),
    ("GBF (SDS)", "Güvenlik Bilgi Formu: kimyasalın tehlikelerini ve kaza anında yapılacakları anlatan belge."),
    ("Korozif", "Aşındırıcı-yakıcı; deriyi ve metali tahrip eden."),
    ("pH", "Çözeltinin asitlik-bazlık ölçüsü; pH metrede cam elektrotla ölçülür."),
    ("Tampon çözelti", "pH'ı belli ve kararlı çözelti; pH metre kalibrasyonunda kullanılır (pH 4,01; 7,00; 10,01)."),
    ("Elektrot eğimi", "pH başına gerilim değişiminin ideale oranı; %95–105 kabul edilir."),
    ("EC", "Elektriksel iletkenlik; çözünmüş tuz miktarının göstergesi. 1 dS/m = 1000 µS/cm."),
    ("Çözünmüş oksijen", "Suda çözünmüş O₂ (mg/L ya da % doygunluk)."),
    ("NTU", "Bulanıklık birimi; türbidimetreyle ölçülür."),
    ("°Brix", "Çözünür kuru madde; 100 g çözeltide 1 g sakaroz eşdeğeri."),
    ("ATC", "Otomatik sıcaklık düzeltmesi (refraktometrede)."),
    ("Absorbans", "Çözeltinin soğurduğu ışığın ölçüsü; A = −log T."),
    ("Beer–Lambert yasası", "A = ε·b·c: absorbans derişimle doğru orantılıdır."),
    ("Kalibrasyon eğrisi", "Bilinen standartların cihaz yanıtına karşı grafiği; numunenin derişimi bundan bulunur."),
    ("R²", "Kalibrasyon doğrusunun uyumu; çoğu laboratuvar 0,99 ve üstünü ister."),
    ("Seyreltme katsayısı", "Numunenin kaç kat seyreltildiği; sonuç bu sayıyla çarpılır."),
    ("AAS", "Atomik absorpsiyon spektrometresi: atomların ışığı soğurmasıyla element tayini."),
    ("ICP-OES", "Plazmada uyarılan atomların yaydığı ışıkla çok elementi birlikte ölçen cihaz."),
    ("Kuru yakma", "Organik maddeyi kül fırınında yakarak mineral kısmı ayırma."),
    ("Yaş yakma", "Organik maddeyi asitle (ısıtarak ya da mikrodalgada) parçalama."),
    ("Kjeldahl", "Yakma–damıtma–titrasyonla azot (ve protein) tayini."),
    ("Protein faktörü", "Azot yüzdesini proteine çeviren katsayı: genel 6,25, süt 6,38, buğday 5,7."),
    ("Soxhlet", "Çözücüyle tekrarlı yıkayarak yağ tayini yapan düzenek."),
    ("HPLC", "Yüksek performanslı sıvı kromatografisi: uçucu olmayan bileşikleri ayırır."),
    ("GC", "Gaz kromatografisi: uçucu bileşikleri ayırır; GC-MS ile tanımlar."),
    ("Alıkonma süresi", "Bir bileşenin kolondan çıkıp dedektöre ulaştığı süre."),
    ("Su aktivitesi (aw)", "Mikroorganizmaların kullanabileceği serbest su (0–1)."),
    ("CIE L*a*b*", "Rengi sayıya çeviren sistem: L* açıklık, a* yeşil–kırmızı, b* mavi–sarı."),
    ("SPAD", "Yaprağı koparmadan göreceli klorofil ölçen cihaz değeri."),
    ("Parti", "Aynı tür hayvandan sağılan ve bir defada satışa sunulan süt."),
    ("Aseptik", "Mikrobiyal bulaşmayı önleyen, steril çalışma koşulu."),
    ("Polidispers", "Farklı büyüklükteki taneciklerin dağıldığı sistem (süt gibi)."),
    ("ISO/IEC 17025", "Deney ve kalibrasyon laboratuvarlarının yeterlilik standardı."),
    ("TÜRKAK", "Türk Akreditasyon Kurumu."),
    ("TÜBİTAK UME", "Türkiye'nin ulusal metroloji (ölçüm bilimi) enstitüsü."),
    ("ppm", "Milyonda bir kısım; sulu çözeltide 1 ppm = 1 mg/L, katıda 1 mg/kg."),
    ("ppb", "Milyarda bir kısım; sulu çözeltide 1 ppb = 1 µg/L. 1 ppm = 1000 ppb."),
    ("Mikro (µ)", "10⁻⁶ çarpanı; 1 µL = 0,001 mL, 1 µg = 0,001 mg."),
    ("Nano (n)", "10⁻⁹ çarpanı; dalga boyları nm ile verilir."),
    ("Mili (m)", "10⁻³ çarpanı; 1 mL = 0,001 L, 1 mg = 0,001 g."),
    ("Stok çözelti", "Derişik hazırlanıp seyreltilerek kullanılan çözelti; C₁V₁ = C₂V₂."),
    ("GHS", "Kimyasal tehlikeleri kırmızı çerçeveli elmas işaretlerle gösteren uluslararası sistem."),
    ("NFPA 704", "Sağlık (mavi), yanıcılık (kırmızı), reaktiflik (sarı) ve özel uyarıyı 0–4 ile gösteren elmas."),
    ("Zorunluluk işareti", "Mavi daire içinde beyaz sembol: gözlük tak, eldiven giy."),
    ("Falkon tüpü", "15 ya da 50 mL'lik vidalı kapaklı, konik dipli plastik santrifüj tüpü."),
    ("Eppendorf tüpü", "0,5–2 mL'lik kapaklı mikrosantrifüj tüpü."),
    ("Piset", "Saf suyla durulama için sıkmalı plastik yıkama şişesi."),
    ("Polipropilen (PP)", "Otoklavlanabilen, kimyasallara dayanıklı yaygın laboratuvar plastiği."),
]


# ===========================================================================
# SAYFALAR
# ===========================================================================
def sayfa_giris():
    st.title("🔬 Laboratuvar Malzemeleri ve Ölçüm Cihazları")
    st.markdown("""
Gıda, toprak, yaprak ve su laboratuvarlarında **güvenli çalışmayı**, **doğru malzemeyi seçmeyi**
ve **güvenilir ölçüm yapmayı** şemalar, etkileşimli hesaplayıcılar ve bol alıştırmayla öğrenmek
için hazırlanmış bir ders uygulaması. Her bölümün sonunda **10, 20 ya da 30 soruluk alıştırma**
ve **adım adım çözümler** var.""")
    svg_goster(svg_dort_lab())
    kartlar([
        ("1 · Laboratuvar güvenliği", "Olanaklar, laboratuvar planı, çalışma kuralları, asit seyreltme"),
        ("2 · Güvenlik ve tehlike işaretleri", "Uyarı, yasak, zorunluluk, acil durum ve yangın işaretleri; GHS; NFPA elması"),
        ("3 · Kimyasallar ve kazalar", "Tehlikeli kimyasallar, kaza anında ilk müdahale"),
        ("4 · Metrik sistem ve birimler", "kilo, mili, mikro, nano; birim çevirme merdiveni; %, ppm, ppb; seyreltme"),
        ("5 · Cam, plastik ve diğer malzemeler", "Beher, balon joje, büret, falkon, Eppendorf, piset…; menisküs, temizlik"),
        ("6 · Okuma ve kullanım", "Menisküs, paralaks, ölçek okuma alıştırması; büret, pipet, balon joje, mikropipet adım adım"),
        ("7 · Ölçümün temelleri", "Doğruluk–kesinlik, hata türleri, kalibrasyon"),
        ("8 · Terazi ve nem", "Terazi türleri, dara, etüv–desikatör–kül fırını, nem ve kül hesabı"),
        ("9 · pH, EC ve su", "pH metre kalibrasyonu, EC sıcaklık düzeltmesi, DO metre, türbidimetre"),
        ("10 · Optik cihazlar", "Refraktometre (Brix), spektrofotometre, Beer–Lambert, kalibrasyon eğrisi"),
        ("11 · İleri cihazlar", "AAS, ICP-OES, Kjeldahl, kül fırını, Soxhlet, HPLC ve GC"),
        ("12 · Laboratuvar türleri", "Toprak, yaprak ve gıda laboratuvarları; su aktivitesi, renk ölçümü"),
        ("13 · Örnek alma", "Mevzuat, parti, karıştırma süreleri, etiket, taşıma ve koruyucu"),
        ("14 · Kalite ve terimler", "Kayıt, ISO/IEC 17025, akreditasyon, sözlük ve hafıza kartları"),
        ("15 · Genel tekrar", "Tüm konulardan karışık sorular"),
    ])
    st.markdown("**Hazırlayanlar:** Emine Dilşat Yeğenoğlu & Tevfik Hasan Can")
    ipucu("Telefonda bölümleri sayfanın en üstündeki <b>Bölüm</b> kutusundan ya da sayfa "
          "sonundaki <b>Önceki / Sonraki</b> bağlantılarından seçebilirsiniz.")


# ---------------------------------------------------------------------------
KURALLAR = [
    ("Laboratuvara girerken kaban ve mont çıkarılır, laboratuvar önlüğü giyilir.", True),
    ("Çalışmaya göre koruyucu gözlük, yüz siperi ve eldiven kullanılır.", True),
    ("Laboratuvarda yemek, içmek ve sigara içmek yasaktır.", True),
    ("Tüpte sıvı ısıtılırken tüpün ağzı kendine ya da başkasına çevrilmez.", True),
    ("Katı kimyasallar temiz bir spatül ya da kaşıkla alınır.", True),
    ("Şişe kapağı ters çevrilerek (iç yüzü tezgâha değmeyecek şekilde) bırakılır.", True),
    ("Şişeden sıvı dökülürken etiket avuç içine gelecek şekilde (yukarıda) tutulur; böylece akan "
     "damla etiketi bozmaz.", True),
    ("Tartım ve analiz sonuçları laboratuvar defterine yazılır.", True),
    ("Su, gaz ve elektrik kullanılmadığında kapatılır; laboratuvardan en son çıkan sorumludur.", True),
    ("Hazırlanan çözeltinin şişesine adı, derişimi ve tarihi yazılır.", True),
    ("Asitli çözelti hazırlarken su yavaş yavaş asidin üzerine dökülür.", False),
    ("Kullanılmayan kimyasal, israf olmasın diye orijinal şişesine geri konur.", False),
    ("Bir çözeltiden çekilen pipet, temizlenmeden başka çözeltiye daldırılabilir.", False),
    ("Kırık cam normal çöp kutusuna atılır.", False),
    ("Dökülen kimyasalı silmek için kâğıt havlu her zaman uygundur.", False),
    ("Deney sürerken kısa bir süre için laboratuvardan ayrılmakta sakınca yoktur.", False),
    ("Termometre gibi yuvarlanabilecek cam eşyalar tezgâhın kenarına bırakılır.", False),
    ("Sıvılar pipete ağızla çekilebilir, yeter ki dikkat edilsin.", False),
]


def sayfa_guvenlik():
    st.title("1 · Laboratuvar güvenliği")
    st.markdown("""
Laboratuvar, **ciddi çalışma yapılan bir ortamdır**. Kazaların çoğu dikkatsizlik ve acele
yüzünden olur. Bu yüzden laboratuvar **güvenli tasarlanmalı**, çalışanlar da **kurallara
uymalıdır**.""")
    st.header("Laboratuvarın sahip olması gereken olanaklar")
    st.markdown("Bir yapı seçin, plandaki yeri vurgulansın:")
    adlar = ["— Tümünü göster —"] + [v[0] for v in LAB_OLANAK.values()]
    sec = st.selectbox("Güvenlik olanağı", adlar, label_visibility="collapsed")
    anahtar = None if sec.startswith("—") else list(LAB_OLANAK)[adlar.index(sec) - 1]
    svg_goster(svg_lab_plan(anahtar))
    if anahtar:
        kutu(f"<b>{LAB_OLANAK[anahtar][0]}:</b> {LAB_OLANAK[anahtar][1]}")
    kartlar([("Havalandırma ve çeker ocak", "Genel havalandırma rahat çalışma sağlar; çeker ocaklar "
                                             "yılda bir kez uzman kontrolünden geçer."),
             ("Atık toplama odası", "Kimyasal atıklar türüne göre toplanır, prosedüre göre bertaraf edilir."),
             ("Kimyasal deposu", "Çalışmanın gerektirdiği en az miktar tutulur; düzen kurallarına uyulur."),
             ("Bakım ve onarım", "Mekanik ve elektrik donanım spesifikasyonlara uygun olmalı; yangın "
                                 "söndürücülerin basıncı düzenli (notlarda 6 ayda bir) kontrol edilir.")])

    st.header("Asit seyreltme: altın kural")
    svg_goster(svg_asit_su())
    uyari("<b>Daima suya asit, asla asite su!</b> Derişik asit (özellikle sülfürik asit) suyla "
          "karışınca çok ısı açığa çıkar. Az miktardaki su asidin üzerine dökülürse anında kaynar ve "
          "asitle birlikte sıçrar. Bol suyun içine asit yavaş yavaş ve karıştırılarak eklenirse ısı "
          "suya dağılır. Bu iş çeker ocakta, gözlük ve eldivenle yapılır.")

    st.header("Laboratuvarda uyulacak kurallar")
    c1, c2 = st.columns(2)
    with c1:
        kutu("<b>✅ Yap</b><br>• Önlük, gözlük, eldiven<br>• İşi önceden planla<br>"
             "• Aletleri temiz tut, yerine koy<br>• Sonuçları deftere yaz<br>"
             "• Çözelti şişesini etiketle (ad, derişim, tarih)<br>• Kırık camı kırık cam kutusuna at<br>"
             "• Uçucu ve derişik asit/bazla çeker ocakta çalış")
    with c2:
        uyari("<b>⛔ Yapma</b><br>• Yeme, içme, sigara<br>• Ağızla pipet çekme<br>"
              "• Kimyasalın tadına, kokusuna doğrudan bakma<br>• Fazlayı orijinal şişeye geri koyma<br>"
              "• Orijinal şişeye pipet daldırma<br>• Deneyin başından ayrılma<br>"
              "• Kapağı kapalı şişeyi ısıtma; uçucu maddeyi açık alev yakınında kullanma")

    st.subheader("🎯 Mini oyun: kural mı, hata mı?")
    if "kural_i" not in st.session_state:
        st.session_state.kural_i = int(rng().integers(0, len(KURALLAR)))
    metin, dogru_mu = KURALLAR[st.session_state.kural_i]
    st.markdown(f'<div class="flash" style="font-size:1.1rem">{metin}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    yanit = None
    if c1.button("✅ Doğru kural"):
        yanit = True
    if c2.button("⛔ Hatalı davranış"):
        yanit = False
    if c3.button("➡️ Başka cümle"):
        st.session_state.kural_i = int(rng().integers(0, len(KURALLAR)))
        st.rerun()
    if yanit is not None:
        if yanit == dogru_mu:
            st.success("Doğru bildiniz!")
        else:
            st.error("Tekrar düşünün: " + ("Bu doğru bir kuraldır." if dogru_mu else "Bu hatalı bir davranıştır."))
    alistirma_blogu("guvenlik", "Laboratuvar güvenliği", gen_guvenlik)


# ---------------------------------------------------------------------------
KAZALAR = {
    "Göze kimyasal sıçradı": [
        "Hemen **göz duşuna** git; göz kapaklarını parmaklarınla açık tutarak **en az 15–20 dakika** bol, "
        "ılık suyla yıka.", "Kontakt lens varsa çıkar (yıkamayı geciktirmeden).",
        "Nötrleştirmeye çalışma (asit için baz, baz için asit **damlatma**).",
        "Kimyasalın etiketini / Güvenlik Bilgi Formunu (GBF) alarak hemen göz doktoruna git; 112'yi ara."],
    "Cilde asit ya da baz döküldü": [
        "Kirlenen giysi, saat ve takıları hemen çıkar.",
        "Bölgeyi **bol akan suyla en az 15–20 dakika** yıka; büyük temas varsa **acil duşu** kullan.",
        "Nötrleştirici (bikarbonat, sirke vb.) sürme: tepkime ısısı yanığı derinleştirebilir.",
        "Yanık büyükse ya da ağrı geçmiyorsa sağlık kuruluşuna başvur."],
    "Hidroflorik asit (HF) teması": [
        "Hemen bol suyla yıka, kirlenmiş giysileri çıkar.",
        "Varsa **kalsiyum glukonat jeli** sür (HF ile çalışılan laboratuvarda bulunmalıdır).",
        "Ağrı olmasa bile **hemen** sağlık kuruluşuna git: HF yanığı derindir ve gecikerek ortaya çıkar."],
    "Kimyasal yutuldu": [
        "**Kusturmaya çalışma** ve kusturucu bir şey içirme: yakıcı madde yemek borusunu ikinci kez yakar.",
        "Ağzı suyla çalkalat; bilinci yerindeyse doktor önermedikçe başka bir şey içirme.",
        "**112**'yi ve **Ulusal Zehir Danışma Merkezi (114)**'i ara; kimyasalın şişesini ya da GBF'yi göster."],
    "Bir kişinin giysisi alev aldı": [
        "Kişiyi **koşturma**: koşmak alevi büyütür.", "**Dur – yat – yuvarlan**; yangın battaniyesine sar "
        "ya da acil duşun altına al.", "Alev sönünce yanığı soğuk suyla soğut, 112'yi ara."],
    "Laboratuvarda yangın çıktı": [
        "**Önce haber ver**: yangın alarmı ve 112.", "Küçük ve kontrol edilebilir bir yangınsa uygun söndürücüyle "
        "müdahale et; değilse alanı boşalt.", "Elektrikli cihaz, çözücü (eter, alkol) yangınlarında **CO₂** ya da "
        "kuru kimyevi toz kullanılır; **su kullanılmaz**.", "Alkali metal (Na, K) yangınında asla su: kuru kum, "
        "toz grafit ya da D sınıfı söndürücü."],
    "Cıva döküldü (kırık termometre)": [
        "Alanı boşalt, havalandır; ısıtıcıları kapat.", "**Ev tipi elektrikli süpürge kullanma**: cıvayı "
        "buharlaştırıp yayar.", "Damlacıkları cıva toplama kitiyle (şırınga, karton) topla; küçük kalıntıların "
        "üzerine **kükürt tozu** serp.", "Toplananı kapalı kapta tehlikeli atık olarak teslim et."],
    "Cam kırıldı": [
        "Elle toplama; faraş–fırça ya da maşa kullan.", "Kırık camı **kırık cam kutusuna** at, normal çöpe atma.",
        "İçinde kimyasal varsa önce kimyasal dökülmesi gibi davran."],
}


def sayfa_kimyasal():
    st.title("3 · Tehlikeli kimyasallar ve kazalar")
    st.markdown("""
Laboratuvarda sağlığa zararlı kimyasallarla çalışılır. Kazaları önlemenin yolu kimyasalı
**tanımak**tır: her kimyasalın şişesindeki **tehlike işaretlerine** ve **Güvenlik Bilgi Formuna
(GBF, İng. SDS)** bakılır. Kaza anında yapılacaklar laboratuvarda **yazılı** olarak asılı durmalıdır.""")
    ipucu("Kimyasal şişelerindeki tehlike işaretlerini (GHS) ve laboratuvar duvarındaki güvenlik işaretlerini "
          "<b>2 · Güvenlik ve tehlike işaretleri</b> bölümünde ayrıntılı bulabilirsiniz.")

    st.header("Kimyasal madde grupları ve özel uyarılar")
    tablo(pd.DataFrame([
        ("Sülfürik asit (H₂SO₄)", "Her derişimde göz ve deriye zararlı; derişiği korozif, şiddetli yanık yapar. "
                                  "Seyreltirken daima suya asit eklenir."),
        ("Nitrik asit (HNO₃)", "Derişim arttıkça zararı artar; ısınınca zehirli azot oksit buharları verir. "
                               "Çeker ocakta çalışılır."),
        ("Hidroklorik asit (HCl)", "Dumanı solunmamalı; çeker ocakta açılır."),
        ("Glasiyal asetik asit", "Oldukça korozif; yanıkları geç iyileşir, sağlık kuruluşuna başvurulur."),
        ("Hidroflorik asit (HF)", "Son derece tehlikeli: deriden geçip derin yanık ve zehirlenme yapar. "
                                  "Yalnızca çeker ocakta; kalsiyum glukonat jeli hazır bulunur."),
        ("Pikrik asit", "Kuruyunca patlayıcı olur; daima ıslak tutulur (notlarda en az %10 su; ticari "
                        "ürünler genellikle çok daha fazla su içerir)."),
        ("Perklorik asit ve perkloratlar", "Güçlü oksitleyici; organik maddelerle patlayıcı karışım yapabilir. "
                                           "Dökülen yere kum ya da sodyum bikarbonat serpilir, kazınarak toplanır."),
        ("Alkaliler (NaOH, KOH)", "Deri, göz ve solunum yolları için çok tehlikeli; göze kaçması körlük yapabilir."),
        ("Alkali metaller (Na, K)", "Su ve nemli deriyle şiddetle tepkimeye girer; kerosen ya da inert gaz "
                                    "altında saklanır. Yangınında su kullanılmaz."),
        ("Eterler (dietil eter)", "Çok uçucu ve kolay tutuşur (parlama noktası yaklaşık −45 °C). Açık alev "
                                  "yakınında kullanılmaz; çeker ocakta çalışılır; yangını CO₂ ile söndürülür."),
        ("Oksalatlar", "Vücutta kalsiyumu çöktürür (kalsiyum oksalat); solunması ve deriyle uzun teması zararlıdır."),
        ("Cıva", "Buharı zehirlidir; dökülünce toplama kiti ve kükürt tozu kullanılır, süpürge kullanılmaz."),
    ], columns=["Madde / grup", "Tehlike ve önlem"]))

    st.header("🚑 Kaza anında ne yapmalı?")
    olay = st.selectbox("Bir kaza durumu seçin", list(KAZALAR))
    for i, adim in enumerate(KAZALAR[olay], 1):
        st.markdown(f"**{i}.** {adim}")
    uyari("<b>Güncel ilk yardım bilgisi:</b> Eski ders kitaplarında geçen <b>bakır sülfatla kusturma</b>, "
          "zehirlenmede <b>ağızdan sodyum tiyosülfat / sodyum nitrit içirme</b> ve yanığa <b>asetik asit ya da "
          "bikarbonat damlatarak nötrleştirme</b> artık önerilmez ve zararlı olabilir. Siyanür panzehirleri "
          "yalnızca sağlık personeli tarafından damar yoluyla verilir. Doğru yaklaşım: <b>bol suyla yıka, "
          "kusturma, 112 ve Ulusal Zehir Danışma Merkezi (114)</b>.")
    alistirma_blogu("kimyasal", "Kimyasallar ve kazalar", gen_kimyasal)


# ---------------------------------------------------------------------------
def sayfa_cam():
    st.title("5 · Cam, plastik ve diğer malzemeler")
    st.markdown("Önce malzeme grubunu, sonra bir malzeme seçin; şemada vurgulansın ve ne işe yaradığı açıklansın.")
    grup = st.radio("Malzeme grubu", list(MALZEME_GRUP), horizontal=True)
    sozluk = MALZEME_GRUP[grup]
    adlar = ["— Tümünü göster —"] + [v[0] for v in sozluk.values()]
    sec = st.selectbox("Malzeme", adlar, label_visibility="collapsed", key=f"malz_{grup}")
    anahtar = None if sec.startswith("—") else list(sozluk)[adlar.index(sec) - 1]
    svg_goster(svg_malzeme(sozluk, anahtar))
    if anahtar:
        ad, _, ne, dikkat = sozluk[anahtar]
        kutu(f"<b>{ad}</b><br>{ne}")
        ipucu(f"<b>Dikkat:</b> {dikkat}")
    st.caption("Şemalar öğretim amaçlı ve ölçeksizdir.")

    st.header("Cam mı, plastik mi?")
    tablo(pd.DataFrame({
        "Özellik": ["Isıya dayanıklılık", "Organik çözücüler (aseton, hekzan, eter)", "Hidroflorik asit (HF)",
                    "Derişik sıcak baz", "İz element (metal) analizi", "Kırılma", "Şeffaflık / temizlik"],
        "Cam (borosilikat)": ["Çok iyi (ısıtılabilir)", "Dayanıklı", "Camı eritir, KULLANILMAZ", "Yavaşça aşındırır",
                              "Yüzeyden iz metal bırakabilir", "Kırılır, kesebilir", "Çok iyi, tekrar tekrar kullanılır"],
        "Plastik": ["Sınırlı (PP otoklavlanabilir ~121 °C)", "Çoğu plastik dayanıksız (PTFE dayanıklı)",
                    "Plastik (PE, PP, PTFE) kap kullanılır", "Genellikle dayanıklı", "Tercih edilir",
                    "Kırılmaz, hafif", "Çoğu tek kullanımlık"]}))
    kartlar([("PP (polipropilen)", "Falkon ve Eppendorf tüpleri, pipet uçları, beher; otoklavlanabilir"),
             ("PE (polietilen)", "Piset, şişeler, bidonlar; esnek"),
             ("PS (polistiren)", "Tek kullanımlık petri ve küvet; çözücülere ve ısıya dayanıksız"),
             ("PTFE (teflon)", "Kimyasallara çok dayanıklı; manyetik balık, kapak contaları")])

    st.header("Hangi iş için hangi malzeme?")
    tablo(pd.DataFrame({
        "İş": ["Tam 250,0 mL standart çözelti hazırlamak", "10,00 mL numuneyi aktarmak",
               "Titrasyonda harcanan hacmi ölçmek", "Yaklaşık 50 mL su ölçüp aktarmak",
               "Çözeltiyi karıştırmak, ısıtmak", "Titre edilen çözeltiyi koymak",
               "50 µL örnek aktarmak", "Kurutulmuş kabı soğutmak", "Kül tayini"],
        "Malzeme": ["Balon joje", "Tam pipet (puarla)", "Büret", "Mezür", "Beher", "Erlen", "Mikropipet + uç",
                    "Desikatör", "Porselen kroze + kül fırını"],
        "Hassasiyet": ["Çok yüksek", "Çok yüksek", "Yüksek", "Orta", "Düşük (yaklaşık)", "Düşük",
                       "Yüksek (µL)", "—", "—"]}))
    kutu("<b>A sınıfı ve B sınıfı:</b> Hacim ölçen cam malzemelerin üzerinde sınıf yazar. <b>A sınıfının "
         "hata payı (toleransı) daha küçüktür</b>, analizlerde A sınıfı tercih edilir. Örneğin 100 mL A sınıfı "
         "balon jojenin toleransı yaklaşık ±0,1 mL, B sınıfının yaklaşık iki katıdır.")

    ipucu("Menisküs, paralaks hatası, büret–pipet–balon joje–mikropipet kullanımı ve okuma alıştırması için "
          "<b>6 · Hacim ölçen malzemeler: okuma ve kullanım</b> bölümüne geçin.")

    st.header("Cam malzemelerin temizliği")
    st.markdown("""
Analiz sonucunun doğruluğu, kullanılan cam malzemenin **temizliğine** bağlıdır. Temizlikte
malzemenin cinsine ve kirin türüne uygun çözelti seçilir.""")
    for i, a in enumerate(["Ön durulama (musluk suyu)", "Sabunlu / deterjanlı suyla fırçalayarak yıkama",
                           "Gerekirse özel temizleme çözeltisi (seyreltik HCl, alkali çözelti vb.)",
                           "Bol musluk suyuyla durulama", "Saf suyla 2–3 kez çalkalama",
                           "Ters çevirip kurutma (hacim ölçen cam etüvde yüksek sıcaklıkta kurutulmaz)"], 1):
        st.markdown(f"**{i}.** {a}")
    ipucu("<b>Temiz cam nasıl anlaşılır?</b> Su, iç yüzeyde damlacıklar bırakmadan <b>düzgün bir film</b> "
          "hâlinde akıyorsa cam temizdir.")
    uyari("<b>Güncel not:</b> Eski kaynaklarda geçen <b>bikromatlı (kromik) asit</b> karışımı, içerdiği "
          "altı değerlikli krom kanserojen ve çevre için çok zararlı olduğu için günümüzde kullanılmamaktadır. "
          "Yerine laboratuvar deterjanları ve seyreltik asit banyoları tercih edilir.")
    alistirma_blogu("cam", "Cam, plastik ve diğer malzemeler", gen_cam)


# ---------------------------------------------------------------------------
BIRIM_EC = {"µS/cm": 1.0, "mS/cm": 1000.0, "dS/m": 1000.0, "S/m": 10000.0}


def sayfa_olcum():
    st.title("7 · Ölçümün temelleri")
    st.header("Doğruluk ve kesinlik aynı şey değildir")
    svg_goster(svg_hedefler())
    c1, c2 = st.columns(2)
    with c1:
        kutu("<b>Doğruluk</b><br>Ölçülen değerin <b>gerçek değere</b> ne kadar yakın olduğu. Ortalama "
             "hedefin merkezine yakınsa ölçüm doğrudur.")
    with c2:
        kutu("<b>Kesinlik (tekrarlanabilirlik)</b><br>Tekrarlanan ölçümlerin <b>birbirine</b> ne kadar yakın "
             "olduğu. Noktalar sıkı kümeleniyorsa ölçüm kesindir.")
    st.subheader("🔬 Deney: üç pH metre, gerçek değer pH 7,00")
    c1, c2 = st.columns(2)
    sapma = c1.slider("Cihazın kalibrasyon kayması (sistematik hata)", -0.50, 0.50, 0.00, 0.05)
    dag = c2.slider("Ölçümlerin dağılması (rastgele hata)", 0.00, 0.40, 0.02, 0.01)
    rr = np.random.default_rng(3)
    olc = 7.00 + sapma + rr.normal(0, 1, 5) * dag
    fig = go.Figure()
    fig.add_scatter(x=list(range(1, 6)), y=olc, mode="markers+lines", name="Ölçümler",
                    marker=dict(size=13, color=MAVI))
    fig.add_hline(y=7.0, line_dash="dash", line_color=YESIL, annotation_text="gerçek değer 7,00")
    fig.add_hline(y=float(olc.mean()), line_dash="dot", line_color=TURUNCU,
                  annotation_text=f"ortalama {olc.mean():.2f}", annotation_position="bottom right")
    fig.update_layout(xaxis_title="Tekrar", yaxis_title="pH", yaxis_range=[6.0, 8.0])
    ciz(fig, 320)
    dogru = abs(olc.mean() - 7) < 0.05
    kesin = olc.std(ddof=1) < 0.05
    sonuc = {(True, True): ("Hem doğru hem kesin.", st.success),
             (False, True): ("Kesin ama doğru değil: sistematik hata var, kalibrasyon gerekir.", st.warning),
             (True, False): ("Ortalama doğru ama kesin değil: rastgele hata büyük, tekrar sayısını artır, "
                             "ortamı ve tekniği kontrol et.", st.warning),
             (False, False): ("Ne doğru ne kesin: cihaz ya da kullanım sorunu.", st.error)}[(dogru, kesin)]
    _ = sonuc[1](f"Ortalama {olc.mean():.2f}, standart sapma {olc.std(ddof=1):.3f} → {sonuc[0]}")

    st.header("Ölçüm hataları üç türlüdür")
    tablo(pd.DataFrame({
        "Hata türü": ["Sistematik", "Rastgele", "Kaba hata"],
        "Nedeni": ["Kalibre edilmemiş cihaz, yanlış yöntem", "Ortam dalgalanması, okuma farkları", "Dikkatsizlik"],
        "Örnek": ["Terazi her tartımda 0,05 g fazla gösteriyor", "Aynı numuneden üç farklı sonuç",
                  "Numunelerin karışması, virgül hatası"],
        "Nasıl azaltılır?": ["Kalibrasyon, referans malzemeyle kontrol", "Tekrarlı ölçüm, ortalama alma",
                             "Etiketleme, kayıt, ikinci kişi kontrolü"]}))
    uyari("<b>Sistematik hata tekrar ederek yok olmaz.</b> Yüz kez ölçseniz de aynı yöne sapar. Onu yalnızca "
          "kalibrasyon düzeltir.")

    st.header("Laboratuvarda sık kullanılan birimler")
    tablo(pd.DataFrame({
        "Birim": ["mg/L ≈ ppm", "µg/L ≈ ppb", "mg/kg", "µS/cm, dS/m", "% (g/100 g)", "°Brix", "NTU"],
        "Ne ifade eder?": ["Çözeltide derişim", "İz element derişimi", "Katı numunede element",
                           "Elektriksel iletkenlik", "Nem, kül, protein, yağ", "Çözünür kuru madde", "Bulanıklık"],
        "Not": ["Seyreltik sulu çözeltilerde geçerli", "Suda ağır metaller", "Toprak, yaprak; kuru madde esasıyla",
                "1 dS/m = 1 mS/cm = 1000 µS/cm", "Yaş mı kuru mu, mutlaka belirtilir", "20 °C referans",
                "Su analizleri"]}))
    st.subheader("🔁 İletkenlik birim çevirici")
    c1, c2, c3 = st.columns([1.2, 1, 1])
    deger = c1.number_input("Değer", 0.0, 1e6, 1.2, 0.1)
    b1 = c2.selectbox("Birimden", list(BIRIM_EC), index=2)
    b2 = c3.selectbox("Birime", list(BIRIM_EC), index=0)
    st.markdown(f"### {deger:g} {b1} = **{deger * BIRIM_EC[b1] / BIRIM_EC[b2]:g} {b2}**")

    st.header("Kalibrasyon, günlük kontrol ve izlenebilirlik")
    kartlar([("Kalibrasyon", "Cihazın gösterdiği değeri, değeri bilinen bir standartla karşılaştırmak ve "
                             "gerekirse ayarlamak."),
             ("Günlük kontrol", "Ölçüme başlamadan bir kontrol standardı okunur. Sonuç kabul sınırının dışındaysa "
                                "ölçüme geçilmez."),
             ("İzlenebilirlik", "Sertifikalı referans malzeme ulusal ölçüm standardına bağlanır. Türkiye'de bu "
                                "kurum TÜBİTAK UME'dir.")])
    ipucu("<b>Kural:</b> Kalibrasyon tarihi geçmiş cihazla ölçüm yapılmaz. Cihazın üzerindeki kalibrasyon "
          "etiketine her gün bakılır.")
    alistirma_blogu("olcum", "Ölçümün temelleri", gen_olcum)


# ---------------------------------------------------------------------------
def sayfa_terazi():
    st.title("8 · Terazi, sıcaklık ve nem tayini")
    st.markdown("**Tartım, her analizin ilk adımıdır.** Tartımdaki bir hata, sonraki bütün hesaplara taşınır.")
    tablo(pd.DataFrame({"Tür": ["Teknik terazi", "Hassas terazi", "Analitik terazi"],
                        "Okunabilirlik": ["0,1–0,01 g", "0,001 g", "0,0001 g (0,1 mg)"],
                        "Kullanım": ["Toprak, büyük numune", "Çözelti hazırlama", "Standart, kül, nem tayini"]}))
    st.subheader("🔬 Analitik terazide adım adım tartım")
    adim = st.select_slider("Adım", options=list(range(len(TERAZI_ADIM))),
                            format_func=lambda i: ["Boş", "Kap kondu", "Dara", "Numune", "Sıcak numune!"][i])
    svg_goster(svg_terazi(adim))
    _ = (st.error if adim == 4 else st.info)(TERAZI_ADIM[adim][1])
    kutu("<b>Kullanım kuralları:</b> su terazisi (kabarcık) ortada · açıldıktan sonra ısınma süresi beklenir · "
         "titreşimsiz masa, cereyansız ortam · kapılar kapalı tartılır · sıcak numune tartılmaz, desikatörde "
         "soğutulur · önce kap konur, dara alınır, sonra numune eklenir.")

    st.header("Etüv, desikatör ve kül fırını birlikte çalışır")
    svg_goster(svg_kurut_tart())
    tablo(pd.DataFrame({
        "Cihaz": ["Etüv", "Kül fırını (muffle)", "Desikatör"],
        "Sıcaklık": ["Genellikle 250 °C'ye kadar (±1 °C sabit)", "1100 °C'ye kadar", "Oda sıcaklığı"],
        "Kullanım": ["Kurutma, nem / kuru madde tayini, mikrobiyolojide inkübasyon",
                     "Kül tayini; element analizi için kuru yakma",
                     "Kurutulmuş numune ve kapları nem çekmeden soğutma"]}))
    st.caption("Kurumadde analizinde nikel ya da alüminyum kaplar, kül tayininde porselen krozeler kullanılır. "
               "Kaplar etüvde sabit ağırlığa getirilir, desikatörde soğutulur, sonra darası alınır.")

    st.subheader("🧮 Nem, kuru madde ve kül hesaplayıcı")
    c1, c2, c3 = st.columns(3)
    kap = c1.number_input("Boş kap (g)", 0.0, 500.0, 25.4312, 0.0001, format="%.4f")
    yas = c2.number_input("Kap + yaş numune (g)", 0.0, 500.0, 30.4290, 0.0001, format="%.4f")
    kuru = c3.number_input("Kap + kuru numune (g)", 0.0, 500.0, 29.6801, 0.0001, format="%.4f")
    m_yas, m_kuru = yas - kap, kuru - kap
    if m_yas <= 0 or m_kuru < 0 or m_kuru > m_yas:
        st.warning("Değerleri kontrol edin: kuru ağırlık yaş ağırlıktan büyük olamaz.")
    else:
        nem = (m_yas - m_kuru) / m_yas * 100
        st.latex(rf"\text{{Nem}}\,(\%) = \frac{{{m_yas:.4f} - {m_kuru:.4f}}}{{{m_yas:.4f}}}\times 100 = {nem:.2f}")
        st.markdown(f"**Kuru madde = 100 − nem = {100 - nem:.2f} %**")
        kul = st.number_input("Kül fırınından sonra kap + kül (g)", 0.0, 500.0, kap + 0.0412, 0.0001, format="%.4f")
        if kul >= kap:
            st.latex(rf"\text{{Kül}}\,(\%) = \frac{{{kul - kap:.4f}}}{{{m_yas:.4f}}}\times 100 = "
                     rf"{(kul - kap) / m_yas * 100:.2f}\ \text{{(yaş ağırlık)}}")

    st.header("Sıcaklık ölçümü ve nem tayini")
    c1, c2 = st.columns(2)
    with c1:
        kutu("<b>Sıcaklık</b><br>• Cam termometre, dijital prob<br>• <b>Veri kaydedici (datalogger)</b>: "
             "buzdolabı, etüv ve numune deposu sürekli izlenir<br>• pH, EC, Brix ve oksijen ölçümleri "
             "sıcaklığa bağlıdır")
    with c2:
        kutu("<b>Nem tayini</b><br>• Etüv: 105 °C'de sabit ağırlığa kadar kurutma (referans yöntem)<br>"
             "• Halojen nem analizörü: hızlı rutin kontrol, referans yöntemle doğrulanır<br>"
             "• Şekerli gıdalarda karamelleşme riski: vakum etüv, düşük sıcaklık")
    alistirma_blogu("terazi", "Terazi ve nem", gen_terazi)


# ---------------------------------------------------------------------------
def sayfa_elektro():
    st.title("9 · pH metre, EC metre ve su cihazları")
    st.header("pH metre nasıl çalışır?")
    st.markdown("""
**Cam elektrot**, çözeltideki hidrojen iyonu etkinliğine göre küçük bir **gerilim (mV)** üretir;
cihaz bunu pH'a çevirir. İdeal bir elektrotta 25 °C'de **pH 7'de gerilim 0 mV**'tur ve her pH
birimi için gerilim yaklaşık **59,16 mV** değişir (Nernst eğimi).""")
    st.subheader("🔬 Kalibrasyon simülatörü")
    c1, c2, c3 = st.columns(3)
    egim_y = c1.slider("Elektrodun gerçek eğimi (% ideal)", 80, 105, 98)
    sapma = c2.slider("Sıfır noktası kayması (mV)", -40, 40, 6)
    T = c3.slider("Sıcaklık (°C)", 5, 45, 25)
    nernst = 0.19842 * (T + 273.15)
    tamponlar = [4.01, 7.00, 10.01]
    mv = [sapma - egim_y / 100 * nernst * (p - 7) for p in tamponlar]
    a, b = np.polyfit(tamponlar, mv, 1)
    egim_olc = -a / nernst * 100
    xs = np.linspace(2, 12, 50)
    fig = go.Figure()
    fig.add_scatter(x=xs, y=-nernst * (xs - 7), name="İdeal elektrot", line=dict(dash="dash", color=GRI_K))
    fig.add_scatter(x=tamponlar, y=mv, mode="markers+text", name="Tampon okumaları",
                    text=[f"{v:.0f} mV" for v in mv], textposition="top right", marker=dict(size=13, color=MAVI))
    fig.add_scatter(x=xs, y=a * xs + b, name="Kalibrasyon doğrusu", line=dict(color=MAVI))
    fig.update_layout(xaxis_title="pH", yaxis_title="Gerilim (mV)")
    ciz(fig, 340)
    st.markdown(f"Bu sıcaklıkta ideal eğim **{nernst:.2f} mV/pH**. Ölçülen eğim **%{egim_olc:.1f}**, "
                f"pH 7'deki gerilim (sıfır noktası) **{b + 7 * a:.1f} mV**.")
    if 95 <= egim_olc <= 105 and abs(b + 7 * a) <= 30:
        st.success("Kalibrasyon kabul edilir (eğim %95–105 arasında).")
    else:
        st.error("Kalibrasyon kabul edilmez: elektrodu temizleyin, tamponları tazeleyin; düzelmezse elektrot "
                 "eskimiştir, değiştirilmelidir.")
    st.caption("Sıfır noktası için kabul sınırı üreticiye göre değişir; burada ±30 mV örnek olarak alınmıştır.")
    c1, c2 = st.columns(2)
    with c1:
        kutu("<b>Kalibrasyon adımları</b><br>1. Elektrodu saf suyla çalkala, kâğıtla hafifçe kurula<br>"
             "2. <b>Önce pH 7,00</b> tamponu (sıfır noktası)<br>3. Ölçüm aralığına göre pH 4,01 ve/veya 10,01<br>"
             "4. Eğimi kontrol et (%95–105)<br>5. Sıcaklık düzeltmesi açık olsun<br>6. Deftere kaydet")
    with c2:
        uyari("<b>Elektrot bakımı</b><br>✅ Saklama çözeltisinde tut (genellikle 3 M KCl)<br>"
              "✅ Ölçümler arasında saf suyla çalkala<br>✅ Tamponu taze kullan, şişeye geri dökme<br>"
              "⛔ Saf suda uzun süre saklama · ⛔ Cam ucu ovma<br>⛔ Kuru bırakma · ⛔ Yağlı numuneden sonra "
              "temizlemeden devam etme")
    st.caption("Toprak pH'ı genellikle 1:2,5 toprak:su süspansiyonunda ölçülür.")

    st.header("EC metre: tuzluluğun göstergesi")
    st.markdown("""
EC metre çözeltinin **elektrik iletme yeteneğini** ölçer. Çözünmüş tuz arttıkça EC artar.
Sıcaklık 1 °C arttığında EC yaklaşık **%2** artar; bu yüzden sonuç **25 °C'ye göre düzeltilir**.
Hücre, KCl standardıyla kalibre edilir (ör. 1413 µS/cm).""")
    st.latex(r"EC_{25} = \frac{EC_t}{1 + 0{,}02\,(t - 25)}")
    c1, c2 = st.columns(2)
    ect = c1.number_input("Ölçülen EC (µS/cm)", 0.0, 200000.0, 1450.0, 10.0)
    t = c2.slider("Numune sıcaklığı (°C)", 5, 40, 30)
    ec25 = ect / (1 + 0.02 * (t - 25))
    st.markdown(f"### EC₂₅ = {ec25:,.0f} µS/cm = **{ec25 / 1000:.2f} dS/m**".replace(",", "."))
    kartlar([("Su", "Sulama suyu tuzluluğu"), ("Toprak", "Saturasyon çamuru ekstraktında tuzluluk (dS/m)"),
             ("Gıda, şıra", "İyon içeriği, kalite kontrol")])

    st.header("Su analizinde kullanılan cihazlar")
    kartlar([("Çözünmüş oksijen (DO) ölçer", "mg/L ya da % doygunluk. Membranlı ya da optik sensör. Sıcaklık, "
                                             "tuzluluk ve basınç sonucu etkiler."),
             ("Türbidimetre", "Bulanıklık (NTU). Partiküllerin 90° açıyla saçtığı ışığı ölçer. Küvet temiz ve "
                              "çiziksiz olmalı."),
             ("Çok parametreli ölçer", "pH, EC, oksijen ve sıcaklık tek cihazda; arazide pratik, ama her sensör "
                                       "ayrı kalibre edilir.")])
    ipucu("<b>Su numunesi:</b> temiz şişe, etiket, soğuk taşıma (yaklaşık 4 °C). Oksijen, pH ve sıcaklık "
          "mümkünse <b>yerinde</b> ölçülür, çünkü bekledikçe değişir.")
    alistirma_blogu("elektro", "pH, EC ve su cihazları", gen_elektro)


# ---------------------------------------------------------------------------
def sayfa_optik():
    st.title("10 · Optik cihazlar")
    st.header("Refraktometre: şeker ve olgunluk")
    st.markdown("""
Işık bir sıvıdan geçerken **kırılır**; sıvıda çözünmüş madde arttıkça kırılma artar.
Refraktometre bu kırılmayı **°Brix** olarak gösterir: **1 °Brix ≈ 100 g çözeltide 1 g sakaroz
eşdeğeri çözünür kuru madde**.""")
    brix = st.slider("Örnek şıranın Brix değeri", 0.0, 32.0, 22.0, 0.2)
    svg_goster(svg_refrakto(brix))
    c1, c2 = st.columns(2)
    with c1:
        kutu("<b>Kullanım</b><br>• Sıfır ayarı <b>saf suyla</b> yapılır<br>• Prizmaya 2–3 damla konur, kapak "
             "kapatılır<br>• 20 °C referans; otomatik sıcaklık düzeltmeli (ATC) model tercih edilir<br>"
             "• Prizma her ölçümden sonra temizlenir")
    with c2:
        kutu("<b>Nerede?</b><br>• Üzümde hasat zamanı<br>• Meyve suyu, pekmez, bal, reçel")
    uyari("<b>Dikkat:</b> Brix yalnızca şeker değildir; asitler ve diğer çözünmüş maddeler de okumaya katılır. "
          "Gerçek şeker değerine yakın bir <b>tahmindir</b>.")

    st.header("UV-Vis spektrofotometre")
    st.markdown("""
Belirli dalga boyundaki ışık, renkli çözeltiden geçerken bir kısmı **soğurulur**. Soğurulan ışık
miktarı (**absorbans, A**) çözeltinin **derişimiyle doğru orantılıdır** (**Beer–Lambert yasası**).""")
    st.latex(r"A = \varepsilon \cdot b \cdot c \qquad A = -\log_{10} T = \log_{10}\frac{I_0}{I}")
    c = st.slider("Numunedeki derişim (mg/L)", 0.0, 10.0, 4.0, 0.5)
    A = 0.15 * c
    svg_goster(svg_spektro(A))
    st.markdown(f"Derişim **{c:g} mg/L** → absorbans **{A:.3f}** → ışığın yalnızca **%{100 * 10 ** -A:.1f}**'i "
                "geçiyor. Derişim iki katına çıkınca absorbans da iki katına çıkar; ama geçen ışık yarıya değil, "
                "**logaritmik** azalır.")
    kutu("<b>Kurallar:</b> Önce <b>kör (blank)</b> ile sıfırla · UV bölgesinde (&lt; 340 nm) <b>kuvars küvet</b> · "
         "küvetin <b>şeffaf yüzüne dokunma</b>, mat yüzünden tut · küvet çiziksiz ve temiz olmalı.<br>"
         "<b>Uygulamalar:</b> nitrat, fosfor, klorofil, antosiyanin, toplam fenol.")

    st.subheader("🔬 Kalibrasyon eğrisi hazırlayın")
    st.markdown("Derişimi bilinen standartlar okunur, doğru denklemi bulunur ve numunenin derişimi hesaplanır.")
    if "kal_tohum" not in st.session_state:
        st.session_state.kal_tohum = 11
    rr = np.random.default_rng(st.session_state.kal_tohum)
    egim = float(rr.uniform(0.08, 0.14))
    std = np.array([0, 2, 4, 6, 8, 10], dtype=float)
    absb = np.round(egim * std + rr.normal(0, 0.006, 6) + 0.004, 3)
    a, b = np.polyfit(std, absb, 1)
    r2 = 1 - ((absb - (a * std + b)) ** 2).sum() / ((absb - absb.mean()) ** 2).sum()
    c1, c2 = st.columns([1, 1.4])
    with c1:
        tablo(pd.DataFrame({"Standart (mg/L)": std, "Absorbans": absb}))
        if st.button("🎲 Yeni standart serisi"):
            st.session_state.kal_tohum = int(rng().integers(1, 10 ** 6))
            st.rerun()
    with c2:
        fig = go.Figure()
        fig.add_scatter(x=std, y=absb, mode="markers", name="Standartlar", marker=dict(size=12, color=MAVI))
        fig.add_scatter(x=std, y=a * std + b, name=f"y = {a:.4f}x + {b:.4f}", line=dict(color=TURUNCU))
        fig.update_layout(title=f"R² = {r2:.4f}", xaxis_title="Derişim (mg/L)", yaxis_title="Absorbans")
        ciz(fig, 320)
    c1, c2 = st.columns(2)
    a_num = c1.number_input("Numunenin absorbansı", 0.0, 3.0, 0.520, 0.005, format="%.3f")
    sf = c2.number_input("Seyreltme katsayısı", 1.0, 1000.0, 1.0, 1.0)
    c_hes = (a_num - b) / a
    st.latex(rf"c = \frac{{A - b}}{{a}} = \frac{{{a_num:.3f} - ({b:.4f})}}{{{a:.4f}}} = {c_hes:.2f}\ \text{{mg/L}}")
    if a_num > absb.max():
        st.error("Numunenin absorbansı en yüksek standarttan büyük: eğrinin **dışında**. Tahmin etme, numuneyi "
                 "**seyrelt** ve yeniden oku; sonucu seyreltme katsayısıyla çarp.")
    else:
        st.success(f"Orijinal numunedeki derişim = {c_hes:.2f} × {sf:g} = **{c_hes * sf:.2f} mg/L**")
    ipucu("Çoğu laboratuvar <b>R² ≥ 0,99</b> ister. Her seride bir <b>kontrol standardı</b> da okunur.")
    alistirma_blogu("optik", "Optik cihazlar", gen_optik)


# ---------------------------------------------------------------------------
def sayfa_ileri():
    st.title("11 · İleri analiz cihazları")
    st.header("Element analizi: AAS ve ICP-OES")
    svg_goster(svg_aas_icp())
    tablo(pd.DataFrame({
        "Cihaz": ["AAS", "ICP-OES"],
        "Prensip": ["Atomlaşan element kendine özgü dalga boyunda ışığı soğurur",
                    "Plazmada uyarılan atomlar ışık yayar"],
        "Güçlü yanı": ["Yaygın, ucuz, güvenilir", "Aynı anda çok element, hızlı"],
        "Sınırlılığı": ["Çoğunlukla tek tek element; her element için ayrı lamba", "Pahalı, argon gazı tüketir"]}))
    kutu("<b>Numune hazırlama:</b> Katı numune önce çözeltiye alınır: <b>kuru yakma</b> (kül fırını) ya da "
         "<b>yaş yakma</b> (asitle, mikrodalga). <b>Uygulama:</b> yaprakta K, Ca, Mg, Fe, Zn; toprakta mikro "
         "elementler; suda ağır metaller.")

    st.header("Kjeldahl: azot ve protein tayini")
    ad = st.radio("Aşama", ["1 · Yakma", "2 · Damıtma", "3 · Titrasyon"], horizontal=True)
    i = int(ad[0]) - 1
    svg_goster(svg_kjeldahl(i))
    st.markdown(["**Yakma:** Numune derişik sülfürik asit ve katalizörle ısıtılır. Organik azot **amonyuma** "
                 "dönüşür.",
                 "**Damıtma:** NaOH eklenir; açığa çıkan **amonyak** buharla damıtılıp **borik asitte** tutulur.",
                 "**Titrasyon:** Borik asitte tutulan amonyak **standart asitle** titre edilir; harcanan asitten "
                 "azot yüzdesi hesaplanır."][i])
    st.subheader("🧮 Protein hesaplayıcı")
    c1, c2, c3 = st.columns(3)
    v = c1.number_input("Harcanan HCl (mL)", 0.0, 100.0, 9.40, 0.05)
    vb = c2.number_input("Kör (mL)", 0.0, 10.0, 0.10, 0.05)
    M = c3.number_input("HCl molaritesi (M)", 0.001, 1.0, 0.1, 0.001, format="%.3f")
    c1, c2 = st.columns(2)
    m = c1.number_input("Numune (g)", 0.01, 10.0, 0.5000, 0.0001, format="%.4f")
    fak = c2.selectbox("Protein faktörü", ["6,25 (genel)", "6,38 (süt)", "5,70 (buğday)"])
    F = float(fak.split(" ")[0].replace(",", "."))
    N = (v - vb) * M * 1.4007 / m
    st.latex(rf"N\,(\%) = \frac{{(V - V_{{kör}})\times M \times 1{{,}}4007}}{{m}} = "
             rf"\frac{{({v:g} - {vb:g})\times {M:g}\times 1{{,}}4007}}{{{m:g}}} = {N:.3f}")
    st.latex(rf"\text{{Protein}}\,(\%) = N \times F = {N:.3f}\times {F:g} = {N * F:.2f}")
    st.caption("1,4007 = azotun mol kütlesi (14,007 g/mol) × 100 / 1000. Faktör 6,25, proteinlerin ortalama "
               "%16 azot içermesinden gelir (100 / 16 = 6,25).")
    uyari("<b>Güvenlik:</b> Derişik asit ve sıcak blok. Çeker ocak, gözlük ve eldiven zorunludur.")

    st.header("Kül fırını ve Soxhlet (yağ tayini)")
    c1, c2 = st.columns([1, 1.1])
    with c1:
        kutu("<b>Kül fırını (muffle)</b><br>• Gıdada genellikle 525–550 °C<br>• Organik kısım yanar, kalan "
             "<b>kül = mineral kısım</b><br>• Krozeler önce kızdırılır, desikatörde soğutulup darası alınır<br>"
             "• Element analizi (AAS, ICP) için numune de hazırlar")
        kutu("<b>Soxhlet</b><br>• Yağ, çözücüyle (petrol eteri, hekzan) defalarca yıkanarak ayrılır<br>"
             "• Numune önceden kurutulmuş ve öğütülmüş olmalı<br>• Çözücü uçurulur, kalan yağ tartılır")
        uyari("Çözücüler çok yanıcıdır: <b>açık alev yok, çeker ocak şart</b>.")
    with c2:
        svg_goster(svg_soxhlet())

    st.header("Kromatografi: karışımı bileşenlerine ayırmak")
    t = st.slider("Zaman (kolonda ilerleme)", 0.0, 1.0, 0.45, 0.05)
    c1, c2 = st.columns([0.7, 1.3])
    with c1:
        svg_goster(svg_kolon(t))
    with c2:
        zx = np.linspace(0, 1, 400)
        fig = go.Figure()
        for ad_, renk, hiz in KROM_BILESEN:
            tep = 330 / 380 / hiz
            y = np.exp(-((zx - tep) ** 2) / (2 * 0.018 ** 2)) * (zx <= t)
            fig.add_scatter(x=zx * 20, y=y, name=ad_, line=dict(color=renk, width=3), fill="tozeroy")
        fig.update_layout(xaxis_title="Alıkonma süresi (dk)",
                          yaxis_title="Sinyal", xaxis_range=[0, 20])
        ciz(fig, 360)
    st.caption("Sağdaki grafik: kromatogram (dedektör sinyali). Kromatogramda her tepe bir bileşendir; tepenin çıktığı süre (alıkonma süresi) bileşeni tanıtır, "
               "tepenin alanı miktarını gösterir. Durağan faza en az tutunan bileşen (1) önce çıkar.")
    tablo(pd.DataFrame({
        "": ["Ne için?", "Örnekler", "Dedektör"],
        "HPLC (sıvı kromatografi)": ["Uçucu olmayan bileşikler",
                                     "Şekerler, organik asitler, fenolikler, antosiyaninler, vitaminler",
                                     "UV / DAD, kırılma indisi (RI)"],
        "GC (gaz kromatografi)": ["Uçucu bileşikler", "Aroma, uçucu yağ, pestisit kalıntısı, yağ asitleri",
                                  "FID; GC-MS bileşiği kütle spektrumundan tanımlar"]}))
    ipucu("Bu cihazların yöntemini uzman kurar. <b>Teknisyenin işi</b> çoğunlukla numune hazırlama, süzme, "
          "seyreltme ve standart hazırlamadır. Sonucun kalitesi büyük ölçüde bu adımlara bağlıdır.")
    alistirma_blogu("ileri", "İleri analiz cihazları", gen_ileri)


# ---------------------------------------------------------------------------
def _lab_rgb(L, a, b):
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200

    def f(t):
        return t ** 3 if t ** 3 > 0.008856 else (t - 16 / 116) / 7.787
    X, Y, Z = 0.95047 * f(fx), 1.0 * f(fy), 1.08883 * f(fz)
    r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    bb = 0.0557 * X - 0.2040 * Y + 1.0570 * Z

    def gam(u):
        u = 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055
        return int(round(min(1, max(0, u)) * 255))
    return gam(r), gam(g), gam(bb)


def sayfa_lablar():
    st.title("12 · Laboratuvar türüne göre cihazlar")
    tur = st.radio("Laboratuvar", ["Toprak", "Yaprak", "Gıda", "Özet tablo"], horizontal=True)
    if tur == "Toprak":
        tablo(pd.DataFrame({
            "Analiz": ["pH", "Tuzluluk", "Kireç", "Organik madde", "Tekstür", "Yarayışlı fosfor", "K, Ca, Mg, mikro"],
            "Cihaz / yöntem": ["pH metre", "EC metre", "Scheibler kalsimetresi", "Walkley-Black (titrasyon)",
                               "Bouyoucos hidrometresi", "Spektrofotometre (Olsen)", "AAS, ICP-OES, alev fotometresi"],
            "Not": ["1:2,5 toprak:su süspansiyonu", "Saturasyon çamuru ekstraktı, dS/m",
                    "Asitle açığa çıkan CO₂ hacmi ölçülür", "Dikromatla yaş yakma", "Kum, silt, kil oranı",
                    "Kireçli ve nötr topraklar", "Ekstraksiyon çözeltisine göre"]}))
        ipucu("<b>Hazırlık:</b> Toprak havada kurutulur, ezilir, <b>2 mm elekten</b> geçirilir.")
    elif tur == "Yaprak":
        svg_goster(svg_yaprak())
        kutu("<b>Neden 105 °C değil de 65–70 °C?</b> Yaprak analizinde amaç element tayinidir; yüksek sıcaklıkta "
             "bazı azotlu bileşikler kaybolabilir ve doku karamelleşip öğütmeyi zorlaştırır. Bu yüzden yaprak "
             "örnekleri daha düşük sıcaklıkta kurutulur.")
        st.subheader("SPAD klorofil metre: tahribatsız ölçüm")
        st.markdown("""
Yaprağı koparmadan, **kırmızı (650 nm)** ve **yakın kızılötesi (940 nm)** ışığın yapraktan geçişini
karşılaştırarak **göreceli** bir klorofil değeri verir. Birimsizdir; aynı yaprakta birkaç okumanın
ortalaması alınır. Çeşide göre kalibre edilmeden mg klorofile çevrilmez.""")
    elif tur == "Gıda":
        st.subheader("Su aktivitesi (aw)")
        st.markdown("Mikroorganizmaların kullanabileceği **serbest suyu** gösterir (0–1). **Nem ≠ su aktivitesi:** "
                    "nem toplam suyu, aw ise bağlı olmayan suyu gösterir.")
        aw = st.slider("Gıdanın su aktivitesi", 0.50, 1.00, 0.85, 0.01)
        sinir = [("Çoğu bakteri", 0.91), ("Çoğu maya", 0.88), ("Çoğu küf", 0.80), ("Kurakçıl (kserofilik) küfler", 0.61)]
        fig = go.Figure()
        fig.add_bar(y=[s[0] for s in sinir], x=[s[1] for s in sinir], orientation="h",
                    marker_color=[YESIL if aw >= s[1] else "#C9D3DD" for s in sinir],
                    text=[("ÜREYEBİLİR" if aw >= s[1] else "üreyemez") + f" (alt sınır ≈ {s[1]})" for s in sinir],
                    textposition="inside")
        fig.add_vline(x=aw, line_color="#D9534F", line_width=3, annotation_text=f"aw = {aw:.2f}")
        fig.update_layout(xaxis_range=[0.5, 1.0], xaxis_title="Su aktivitesi")
        ciz(fig, 300)
        st.caption("Değerler ders kitaplarında verilen yaklaşık alt sınırlardır; türe ve ortama göre değişir. "
                   "Örnekler: taze meyve ~0,97 · reçel ~0,80 · pekmez, bal ~0,60 · kuru üzüm ~0,55–0,60.")
        st.subheader("Renk ölçer (kolorimetre): CIE L*a*b*")
        c1, c2, c3 = st.columns(3)
        L = c1.slider("L* (0 siyah – 100 beyaz)", 0, 100, 35)
        a = c2.slider("a* (− yeşil … + kırmızı)", -60, 60, 30)
        b = c3.slider("b* (− mavi … + sarı)", -60, 60, 12)
        r, g, bb = _lab_rgb(L, a, b)
        st.markdown(f'<div class="renk-kutu" style="background:rgb({r},{g},{bb})"></div>', unsafe_allow_html=True)
        st.caption("Ekrandaki renk yaklaşık bir gösterimdir. Kuru üzümde kahverengileşme L* değerinin düşmesiyle "
                   "izlenir.")
        kutu("<b>Viskozimetre:</b> Sıvının akmaya karşı direncini (kıvamını) ölçer: pekmez, şurup, bal. Sonuç "
             "sıcaklığa çok bağlıdır; ölçüm sabit sıcaklıkta yapılır.")
    else:
        tablo(pd.DataFrame({
            "Ölçülen": ["Kütle", "pH", "Tuzluluk, iletkenlik", "Nem", "Çözünür kuru madde", "Renkli bileşik derişimi",
                        "Mineral elementler", "Azot, protein", "Oksijen, bulanıklık", "Klorofil (tahribatsız)"],
            "Cihaz": ["Terazi", "pH metre", "EC metre", "Etüv, nem analizörü", "Refraktometre", "Spektrofotometre",
                      "AAS, ICP-OES", "Kjeldahl", "DO metre, türbidimetre", "SPAD metre"],
            "Laboratuvar": ["Hepsi", "Gıda, toprak, su", "Toprak, su", "Gıda, toprak, yaprak", "Gıda (üzüm, şıra)",
                            "Hepsi", "Toprak, yaprak, su, gıda", "Gıda, yaprak, toprak", "Su", "Yaprak"]}))
    alistirma_blogu("lablar", "Laboratuvar türleri", gen_lablar)


# ---------------------------------------------------------------------------
def sayfa_numune():
    st.title("13 · Örnek (numune) alma")
    st.markdown("""
Analiz ne kadar hassas olursa olsun, **örnek kitleyi temsil etmiyorsa sonuç yanlıştır**. Bu
yüzden örnek, mevzuattaki kurallara göre alınır, korunur ve laboratuvara ulaştırılır.""")
    svg_goster(svg_numune())
    kutu("<b>Yasal dayanak (ders notundaki):</b> 16.11.1997 tarihli Resmî Gazete'de yayımlanan Türk Gıda "
         "Kodeksi Yönetmeliği, 11. bölüm “Numune Alma ve Analiz Metodları”.")
    uyari("<b>Güncel durum:</b> 1997 tarihli yönetmelik yürürlükte değildir. Türk Gıda Kodeksi Yönetmeliği "
          "2011'de, ardından <b>19.02.2020 tarih ve 31044 sayılı Resmî Gazete</b>'de yeniden yayımlanmıştır; "
          "numune alma kuralları için güncel mevzuat ve ilgili standartlar izlenmelidir.")
    st.header("Örnek alırken nelere dikkat edilir?")
    kartlar([("Kitle ve ambalaj", "Kitlenin büyüklüğü, ambalaj şekli, örneğin fazı (katı, sıvı, toz)"),
             ("Analizin amacı", "Günlük rutin kontrol · mahkemeye intikal etmiş (bilirkişi) kontrol · sınıf "
                                "özelliklerinin belirlenmesi"),
             ("Miktar", "Kimyasal analiz için genellikle 200 mL; kap ne tam dolu ne çok az"),
             ("Kap", "Cam, paslanmaz çelik ya da kokusuz plastik; koku vermeyen, numuneyi etkilemeyen; buzlu "
                     "cam üzerine yazılabilir; en uygun kapak lastik kapak")])
    st.header("Bakteriyolojik örnek ve parti")
    st.markdown("""
- **Parti:** Aynı tür hayvandan sağılan ve bir defada satışa sunulan süt. Bir partiden **çift örnek** alınır.
- Bakteriyolojik analiz için örnek **steril** şişelere **aseptik** koşullarda alınır.
- Her örnekten 200 mL alınır, ağzı sıkıca kapatılır, gerekirse mühürlenir ve etiketlenir.
- Süt **polidispers** bir sistemdir (yağ, protein ve şeker farklı büyüklükte dağılmıştır); bu yüzden
  örnek almadan önce **iyice karıştırılır**.""")
    st.subheader("🧮 Karıştırma süresi rehberi")
    durum = st.selectbox("Süt nerede?", ["Tek bir kapta", "Birkaç kapta", "Soğutulmuş tankta",
                                         "Kaymak tabakası kuvvetli ya da donmuş"])
    if durum == "Tek bir kapta":
        st.info("5–6 kez başka kaba aktarılır ya da karıştırıcıyla 30 saniye karıştırılır.")
    elif durum == "Birkaç kapta":
        st.info("Her kaptan **aynı miktarda** örnek alınır, bir kapta toplanır, karıştırılarak örnek kabına konur.")
    elif durum == "Soğutulmuş tankta":
        hacim = st.number_input("Tank kapasitesi (L)", 50, 30000, 600, 50)
        st.info(f"{hacim} L {'≤' if hacim <= 400 else '>'} 400 L → örneklemeden önce **en az "
                f"{5 if hacim <= 400 else 10} dakika** karıştırılır.")
        st.caption("Büyük tank ve tankerlerde mekanik karıştırıcı, basınçlı hava ya da ~180 cm delikli karıştırıcı.")
    else:
        st.info("En çok 55 °C'lik su banyosunda buz ve kaymak çözülene kadar bekletilir; sonra en az 1 dakika "
                "karıştırılır ya da 10 kez kaptan kaba aktarılır.")
    ipucu("Karıştırırken <b>köpük</b> oluşmamalı. Köpük oluşursa sönene kadar beklenir, hafifçe karıştırılarak örnek alınır.")

    st.header("Örneğin laboratuvara iletilmesi")
    st.subheader("🏷️ Etiket hazırlayın")
    c1, c2 = st.columns(2)
    sahip = c1.text_input("Örnek sahibinin adı-soyadı", "")
    tur = c2.text_input("Örneğin türü", "Çiğ inek sütü")
    yer = c1.text_input("Alındığı yer", "")
    tarih = c2.text_input("Alınış tarihi (ve saati)", "")
    sic = c1.text_input("Sıcaklık (°C)", "4")
    alanlar = {"Sahibi": sahip, "Tür": tur, "Yer": yer, "Tarih": tarih, "Sıcaklık": sic}
    st.markdown('<div class="etiket">' + "<br>".join(f"<b>{k}:</b> {v or '……'}" for k, v in alanlar.items())
                + "</div>", unsafe_allow_html=True)
    eksik = [k for k, v in alanlar.items() if not v.strip()]
    if eksik:
        st.warning(f"Eksik bilgi: {', '.join(eksik)}. Etiketsiz ya da eksik etiketli örnek kabul edilmez.")
    else:
        st.success("Etiket tamam.")
    kutu("<b>Süre ve sıcaklık:</b> Örnek en kısa sürede (<b>24 saati geçmeden</b>) ve <b>0–5 °C</b>'de "
         "laboratuvara ulaştırılır.<br><b>Koruyucu:</b> Bu koşul sağlanamıyorsa notlara göre 200 mL süte 0,1 g "
         "potasyum dikromat eklenebilir. Bu örnekte <b>duyusal ve mikrobiyolojik analiz</b> ile <b>özgül ağırlık, "
         "kuru madde ve kül</b> analizleri yapılamaz.")
    uyari("Potasyum dikromat altı değerlikli krom içerir: <b>kanserojen ve zehirlidir</b>. Eldivenle çalışılır, "
          "atığı tehlikeli atık olarak toplanır.")
    st.header("Analize hazırlık")
    st.markdown("""
Süt kuru ve temiz bir behere boşaltılır. Şişede ve kapakta kaymak kalmamalıdır; bunun için süt
şişe ile beher arasında birkaç kez aktarılır. Kalıntı yine kalıyorsa süt su banyosunda **38 °C**'ye
kadar ısıtılıp çalkalanır, yağ homojen dağıtılır.""")
    alistirma_blogu("numune", "Örnek alma", gen_numune)


# ---------------------------------------------------------------------------
def _kart_yeni():
    st.session_state.kart_i = int(rng().integers(0, len(TERIMLER)))
    st.session_state.kart_acik = False


def sayfa_kalite():
    st.title("14 · Kalite, kayıt ve terimler")
    kartlar([("📒 Kayıt", "Cihaz kartı (marka, seri no, kalibrasyon tarihi) · kullanım ve bakım defteri · "
                         "ham veri sonuçla birlikte saklanır"),
             ("🏅 Kalite", "ISO/IEC 17025: deney ve kalibrasyon laboratuvarlarının yeterlilik standardı. "
                          "Türkiye'de akreditasyonu TÜRKAK verir."),
             ("🦺 Güvenlik", "Önlük, gözlük, eldiven · suya asit · asit ve çözücüyle çeker ocakta · ıslak zemin ve "
                            "kabloya dikkat · atıklar türüne göre ayrılır")])
    st.markdown('<div class="flash">Bir sonuç, onu üreten cihaz, yöntem ve kayıt kadar güvenilirdir.'
                '<div class="flash-cevap">Kalibre et, kontrol et, kaydet. Sonra ölç.</div></div>',
                unsafe_allow_html=True)
    st.header("🃏 Hafıza kartları")
    if "kart_i" not in st.session_state:
        _kart_yeni()
    terim, tanim = TERIMLER[st.session_state.kart_i]
    st.markdown(f'<div class="flash">{terim}' +
                (f'<div class="flash-cevap">{tanim}</div>' if st.session_state.kart_acik else "") +
                '</div>', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 2])
    if c1.button("👀 Tanımı göster"):
        st.session_state.kart_acik = True
        st.rerun()
    c2.button("➡️ Sonraki kart", on_click=_kart_yeni)
    st.header("📖 Sözlük")
    ara = st.text_input("Terim ara", "")
    for t, d in TERIMLER:
        if ara.lower() in (t + d).lower():
            st.markdown(f"**{t}:** {d}")
    alistirma_blogu("kalite", "Kalite ve terimler", gen_kalite)


def sayfa_tekrar():
    st.title("15 · Genel tekrar")
    st.markdown("Bütün konulardan karışık sorular (10, 20 ya da 30). **🎲 Yeni sorular** ile istediğiniz kadar "
                "tekrar edebilirsiniz.")
    alistirma_blogu("tekrar", "Karışık sorular", gen_tekrar)


# ---------------------------------------------------------------------------
# Sayı biçimlendirme (Türkçe: ondalık virgül, binlik nokta)
# ---------------------------------------------------------------------------
def _sayi_tr(x, bilimsel_sinir=(1e-4, 1e9)):
    if x == 0:
        return "0"
    v = float(f"{x:.10g}")
    ax = abs(v)
    if bilimsel_sinir[0] <= ax < bilimsel_sinir[1]:
        if abs(v - round(v)) < 1e-12:
            t = f"{int(round(v)):,}".replace(",", ".") if ax >= 10000 else str(int(round(v)))
            return t
        t = f"{v:.10f}".rstrip("0").rstrip(".")
        tam, ond = t.split(".")
        if abs(int(tam)) >= 10000:
            tam = f"{int(tam):,}".replace(",", ".")
        return f"{tam},{ond}"
    e = int(math.floor(math.log10(ax)))
    m = float(f"{v / 10 ** e:.6g}")
    mt = (f"{m:g}").replace(".", ",")
    return f"{mt} × 10{_ust(e)}"


BIRIM_TEMEL = {"Kütle": "g", "Hacim": "L", "Uzunluk": "m"}
ONEK_US = {o[1]: o[2] for o in ONEKLER}


def _cevir_birim(deger, b1, b2):
    """b1, b2: önek sembolleri ('' temel)."""
    return deger * 10 ** (ONEK_US[b1] - ONEK_US[b2])


# ---------------------------------------------------------------------------
def sayfa_isaretler():
    st.title("2 · Güvenlik ve tehlike işaretleri")
    st.markdown("""
Laboratuvarda iki tür işaretle karşılaşırız: **duvarlardaki güvenlik işaretleri** (iş güvenliği
işaretleri) ve **kimyasal şişelerindeki tehlike işaretleri**. İşaretin **şekli ve rengi**, ne
anlama geldiğini daha okumadan söyler.""")
    svg_goster(svg_isaret_turleri())
    tablo(pd.DataFrame({
        "Şekil ve renk": ["Sarı üçgen, siyah çerçeve", "Mavi daire", "Kırmızı çerçeveli daire, çapraz çizgi",
                          "Yeşil kare / dikdörtgen", "Kırmızı kare / dikdörtgen", "Kırmızı çerçeveli eşkenar dörtgen (elmas)"],
        "Anlamı": ["UYARI: dikkat, tehlike var", "ZORUNLULUK: bunu yapmak zorundasın", "YASAK: bunu yapma",
                   "ACİL DURUM: ilk yardım, kaçış, güvenlik donanımı", "YANGIN: yangınla mücadele donanımı",
                   "KİMYASAL TEHLİKE (GHS): şişenin içindeki maddenin tehlikesi"],
        "Örnek": ["Elektrik, sıcak yüzey, biyolojik tehlike", "Gözlük tak, eldiven giy", "Sigara içilmez, yemek yasak",
                  "Göz duşu, acil çıkış", "Yangın söndürücü, alarm butonu", "Yanıcı, aşındırıcı, zehirli"]}))
    st.header("Güvenlik işaretleri")
    grup = st.radio("İşaret grubu", list(ISARETLER), horizontal=True)
    svg_goster(svg_isaretler(grup))
    st.caption(f"{grup}: {ISARETLER[grup][0]}. Çizimler ISO 7010 işaretlerine benzetilerek sadeleştirilmiştir.")
    st.header("Kimyasal tehlike işaretleri (GHS)")
    svg_goster(svg_ghs())
    kutu("Kimyasal şişelerindeki kırmızı çerçeveli eşkenar dörtgenler dünya genelinde ortak kullanılan "
         "<b>GHS</b> (Avrupa ve Türkiye'de <b>CLP</b>) işaretleridir. Etikette işaretin yanında bir "
         "<b>uyarı kelimesi</b> bulunur: <b>“Tehlike”</b> (daha ciddi) ya da <b>“Dikkat”</b> (daha hafif). Ayrıntılı "
         "bilgi kimyasalın <b>Güvenlik Bilgi Formunda (GBF)</b> yer alır.")
    st.header("🔬 NFPA 704 elması")
    st.markdown("""
Bazı kimyasal dolaplarında, kaplarda ve kapılarda görülen dört renkli elmas, **acil durumda
müdahale edecek kişiye** tehlikeyi hızlıca anlatır. Her kutuda **0 (tehlike yok)** ile **4 (çok
yüksek tehlike)** arasında bir sayı vardır.""")
    c1, c2 = st.columns([1, 1.1])
    with c1:
        sg = st.slider("🔵 Sağlık", 0, 4, 3)
        yn = st.slider("🔴 Yanıcılık", 0, 4, 0)
        rk = st.slider("🟡 Reaktiflik (kararsızlık)", 0, 4, 1)
        oz = st.selectbox("⚪ Özel uyarı", ["", "W", "OX", "SA"],
                          format_func=lambda x: {"": "(boş)", "W": "W üstü çizili: suyla tepkimeye girer",
                                                 "OX": "OX: oksitleyici", "SA": "SA: boğucu gaz"}[x])
    with c2:
        svg_goster(svg_nfpa(sg, yn, rk, oz))
    anlam = {0: "tehlike yok", 1: "hafif", 2: "orta", 3: "ciddi", 4: "çok ciddi / ölümcül"}
    st.markdown(f"**Okuma:** sağlık tehlikesi {anlam[sg]} · yanıcılık {anlam[yn]} · reaktiflik {anlam[rk]}"
                + (f" · özel: {oz}" if oz else ""))
    uyari("<b>Dikkat:</b> NFPA'da <b>4 en tehlikeli</b> derecedir. GHS'nin sınıflandırma sisteminde ise kategori 1 en "
          "tehlikelidir. İki sistem karıştırılmamalıdır.")
    alistirma_blogu("isaret", "Güvenlik ve tehlike işaretleri", gen_isaret)


# ---------------------------------------------------------------------------
def sayfa_metrik():
    st.title("4 · Metrik sistem ve birimler")
    st.markdown("""
Laboratuvarda her gün **gram, miligram, mikrolitre, ppm** gibi birimlerle çalışırız. Bir analizde
en sık yapılan hata **birim çevirme hatasıdır**: virgülün bir basamak kayması sonucu 10 kat, üç
basamak kayması 1000 kat yanlış yapar. Metrik sistemde bütün birimler **10'un katlarıyla**
birbirine bağlıdır, bu yüzden kuralı bir kez öğrenmek yeter.""")
    st.header("Temel birimler")
    tablo(pd.DataFrame({
        "Büyüklük": ["Kütle", "Hacim", "Uzunluk", "Sıcaklık", "Zaman", "Madde miktarı"],
        "Temel birim": ["gram (g) · SI'da kilogram (kg)", "litre (L)", "metre (m)", "kelvin (K) · günlük: °C",
                        "saniye (s)", "mol"],
        "Laboratuvarda": ["Tartım: g, mg", "Çözelti: L, mL, µL", "Küvet: 1 cm, dalga boyu: nm", "Etüv 105 °C",
                          "Karıştırma 5 dk", "Çözelti derişimi (mol/L)"]}))
    st.header("Ön ekler (önek tablosu)")
    tablo(pd.DataFrame({
        "Önek": ["kilo", "hekto", "deka", "—", "desi", "santi", "mili", "mikro", "nano", "piko"],
        "Sembol": ["k", "h", "da", "—", "d", "c", "m", "µ", "n", "p"],
        "Çarpan": ["1000", "100", "10", "1", "0,1", "0,01", "0,001", "0,000 001", "0,000 000 001",
                   "0,000 000 000 001"],
        "10'un kuvveti": ["10³", "10²", "10¹", "10⁰", "10⁻¹", "10⁻²", "10⁻³", "10⁻⁶", "10⁻⁹", "10⁻¹²"],
        "Örnek": ["1 kg = 1000 g", "1 hL = 100 L", "1 dag = 10 g", "1 g", "1 dL = 0,1 L", "1 cm = 0,01 m",
                  "1 mg = 0,001 g", "1 µL = 0,000 001 L", "dalga boyu 540 nm", "1 pg = 10⁻¹² g"]}))
    ipucu("<b>Laboratuvarda en çok kullanılan dört basamak:</b> kilo → (temel) → mili → mikro → nano. "
          "Bunların arası hep <b>1000 kat</b>tır: 1 g = 1000 mg, 1 mg = 1000 µg, 1 µg = 1000 ng.")

    st.header("🔬 Birim çevirme merdiveni")
    c1, c2, c3, c4 = st.columns([1, 1.2, 1, 1])
    tur = c1.selectbox("Büyüklük", list(BIRIM_TEMEL))
    temel = BIRIM_TEMEL[tur]
    birimler = [o[1] + temel for o in ONEKLER]
    deger = c2.number_input("Değer", value=2.5, step=0.5, format="%g")
    b1 = c3.selectbox("Birimden", birimler, index=6, key=f"b1_{tur}")[:-len(temel)]
    b2 = c4.selectbox("Birime", birimler, index=7, key=f"b2_{tur}")[:-len(temel)]
    svg_goster(svg_merdiven(temel, ONEK_US[b1], ONEK_US[b2]))
    fark = ONEK_US[b1] - ONEK_US[b2]
    sonuc = _cevir_birim(deger, b1, b2)
    if fark > 0:
        acik = f"Küçük birime iniyoruz → **{10 ** fark:,}".replace(",", ".") + " ile ÇARP**"
    elif fark < 0:
        acik = f"Büyük birime çıkıyoruz → **{10 ** -fark:,}".replace(",", ".") + " ile BÖL**"
    else:
        acik = "Aynı birim."
    st.markdown(f"{acik}  \n### {_sayi_tr(deger)} {b1}{temel} = **{_sayi_tr(sonuc)} {b2}{temel}**")
    st.caption("Virgül kaydırma kuralı: 10 katında 1 basamak, 1000 katında 3 basamak kaydırılır. "
               "Çarparken virgül sağa, bölerken sola kayar.")

    st.subheader("Hacim eşitlikleri")
    kartlar([("1 mL = 1 cm³", "Bir mililitre, kenarı 1 cm olan küpün hacmidir (eski adı: cc)."),
             ("1 L = 1 dm³ = 1000 mL", "Bir litre, kenarı 10 cm olan küp."),
             ("1 µL = 1 mm³", "Mikropipetle çalışılan hacim; 1 mL = 1000 µL."),
             ("1 m³ = 1000 L", "Bir ton su yaklaşık 1 m³'tür.")])
    st.subheader("Sıcaklık")
    st.latex(r"T\,(\mathrm{K}) = t\,(^{\circ}\mathrm{C}) + 273{,}15")
    st.caption("Örnek: 25 °C = 298,15 K; 0 °C = 273,15 K. Kelvinde derece (°) işareti kullanılmaz.")
    st.subheader("Bilimsel gösterim")
    tablo(pd.DataFrame({"Uzun yazım": ["0,000 005 g", "0,003 L", "2 500 000 µL", "0,000 000 450 m"],
                        "Bilimsel gösterim": ["5 × 10⁻⁶ g", "3 × 10⁻³ L", "2,5 × 10⁶ µL", "4,5 × 10⁻⁷ m"],
                        "Önekle": ["5 µg", "3 mL", "2,5 L", "450 nm"]}))

    st.header("Derişim birimleri: %, ppm, ppb")
    st.markdown("""
Derişim, **bir karışımın içinde ne kadar madde olduğunu** gösterir. Çok az miktarlar için
yüzde (%) yetmez; **ppm** ve **ppb** kullanılır:
- **% (yüzde, parts per hundred):** 100 birimde 1 birim
- **ppm (parts per million, milyonda bir):** 1 000 000 birimde 1 birim
- **ppb (parts per billion, milyarda bir):** 1 000 000 000 birimde 1 birim""")
    tablo(pd.DataFrame({
        "Birim": ["%", "ppm", "ppb", "ppt"],
        "Oran": ["1 / 100", "1 / 1 000 000", "1 / 1 000 000 000", "1 / 1 000 000 000 000"],
        "Suda (çözelti)": ["1 g / 100 mL (w/v)", "1 mg/L", "1 µg/L", "1 ng/L"],
        "Katıda": ["1 g / 100 g", "1 mg/kg = 1 µg/g", "1 µg/kg = 1 ng/g", "1 ng/kg"],
        "Nerede?": ["Nem, kül, protein, yağ", "Nitrat, Fe, Zn, toprakta P", "Suda kurşun, kadmiyum, arsenik",
                    "Çok eser kirleticiler"]}))
    kutu("<b>Ezberlenecek üç eşitlik:</b><br>• <b>1 % = 10 000 ppm</b><br>• <b>1 ppm = 1000 ppb</b><br>"
         "• Seyreltik sulu çözeltide <b>1 ppm = 1 mg/L</b>, <b>1 ppb = 1 µg/L</b> (1 L su ≈ 1 kg kabul edilir)")
    kartlar([("1 ppm ne kadar az?", "1 ton (1000 L) suda 1 gram madde · zamanda: yaklaşık 12 günde 1 saniye"),
             ("1 ppb ne kadar az?", "1000 ton suda 1 gram · zamanda: yaklaşık 32 yılda 1 saniye")])
    oran = pd.DataFrame({"Birim": ["% (yüzde)", "‰ (binde)", "ppm", "ppb", "ppt"], "Kesir": [1e-2, 1e-3, 1e-6, 1e-9, 1e-12]})
    fig = go.Figure(go.Bar(x=oran["Birim"], y=oran["Kesir"], marker_color=[MAVI, MOR, YESIL, TURUNCU, PEMBE],
                           text=["10⁻²", "10⁻³", "10⁻⁶", "10⁻⁹", "10⁻¹²"], textposition="outside"))
    fig.update_layout(yaxis_type="log", yaxis_title="1 birimin karşılığı (kesir, log ölçek)",
                      title="Her adımda 1000 kat küçülür (ölçek logaritmik)")
    ciz(fig, 330)

    st.subheader("🧮 ppm hesaplayıcı")
    c1, c2 = st.columns(2)
    mg = c1.number_input("Çözünen madde (mg)", 0.0, 1e6, 25.0, 1.0)
    L = c2.number_input("Çözelti hacmi (L)", 0.001, 1e5, 0.5, 0.1)
    ppm = mg / L
    st.latex(rf"\text{{ppm}} = \frac{{\text{{mg}}}}{{\text{{L}}}} = \frac{{{_sayi_tr(mg)}}}{{{_sayi_tr(L)}}} = {_sayi_tr(ppm)}")
    st.markdown(f"= **{_sayi_tr(ppm)} ppm** = **{_sayi_tr(ppm * 1000)} ppb** = **%{_sayi_tr(ppm / 10000)}**")

    st.subheader("🧮 Seyreltme: C₁ · V₁ = C₂ · V₂")
    st.markdown("Derişik **stok** çözeltiden istenen derişimde çözelti hazırlarken stoktan ne kadar alınacağını bulur.")
    c1, c2, c3 = st.columns(3)
    C1 = c1.number_input("Stok derişimi C₁ (ppm)", 0.001, 1e6, 1000.0, 10.0)
    C2 = c2.number_input("İstenen derişim C₂ (ppm)", 0.001, 1e6, 10.0, 1.0)
    V2 = c3.number_input("İstenen hacim V₂ (mL)", 1.0, 1e5, 100.0, 10.0)
    if C2 > C1:
        st.error("İstenen derişim stoktan büyük olamaz: seyreltmeyle derişim yalnızca azalır.")
    else:
        V1 = C2 * V2 / C1
        st.latex(rf"V_1 = \frac{{C_2 \times V_2}}{{C_1}} = \frac{{{_sayi_tr(C2)} \times {_sayi_tr(V2)}}}{{{_sayi_tr(C1)}}} = "
                 rf"{_sayi_tr(V1)}\ \text{{mL}}")
        st.success(f"Stoktan **{_sayi_tr(V1)} mL** ( = {_sayi_tr(V1 * 1000)} µL) alınır, {_sayi_tr(V2)} mL'lik balon "
                   "jojeye konur ve saf suyla çizgiye tamamlanır.")
    st.subheader("🧮 Yüzde (w/v) çözelti hazırlama")
    c1, c2 = st.columns(2)
    yuzde = c1.number_input("İstenen derişim (% w/v)", 0.01, 50.0, 2.0, 0.5)
    hacim = c2.number_input("Hacim (mL)", 1.0, 5000.0, 250.0, 10.0)
    st.latex(rf"\text{{Tartılacak madde}} = \frac{{{_sayi_tr(yuzde)}\ \text{{g}}}}{{100\ \text{{mL}}}}\times "
             rf"{_sayi_tr(hacim)}\ \text{{mL}} = {_sayi_tr(yuzde * hacim / 100)}\ \text{{g}}")
    st.caption("% (w/v): 100 mL çözeltideki gram · % (w/w): 100 g karışımdaki gram · % (v/v): 100 mL çözeltideki mL "
               "(ör. alkol). Hangisi olduğu mutlaka yazılır.")
    alistirma_blogu("metrik", "Metrik sistem ve birimler", gen_metrik)


# ---------------------------------------------------------------------------
KULLANIM = {
    "Mezür": [
        "Ölçülecek hacme **en yakın** boyda mezür seç (8 mL için 10 mL'lik, 90 mL için 100 mL'lik).",
        "Mezürü **düz bir zemine** koy; elde tutarak okuma yapma.",
        "Sıvıyı çizgiye yaklaşınca damla damla tamamla (piset ya da pastör pipetiyle).",
        "**Göz hizasında**, menisküsün **alt kenarından** oku; en küçük bölmenin onda biri kadar tahmin et.",
        "Mezür **yaklaşık** ölçüm içindir; standart çözelti hazırlamada kullanılmaz."],
    "Büret": [
        "Saf suyla yıka, sonra kullanacağın çözeltiyle **2–3 kez çalkala** (iç yüzeydeki su çözeltiyi seyreltmesin).",
        "Musluk kapalıyken huniyle sıfırın biraz üstüne kadar doldur; **huniyi çıkar** (damlayıp okumayı bozar).",
        "Musluğu açıp ucu doldur; **uçtaki hava kabarcığını** mutlaka gider.",
        "**Başlangıç okumasını** yaz. Sıfırda olmak zorunda değildir: harcanan hacim = son okuma − ilk okuma.",
        "Bürette ölçek **yukarıdan aşağı** artar (0 üstte). 0,1 mL bölmeli bürette **iki ondalıkla** oku (ör. 23,47 mL).",
        "Titrasyon sonunda damlanın ucunda asılı kalanını erlenin çeperine değdirerek al, **son okumayı** yaz."],
    "Tam pipet": [
        "Puar ya da pipet pompası tak; **ağızla asla çekme**.",
        "Pipeti alacağın çözeltiyle 2–3 kez çalkala.",
        "Çözeltiyi **çizginin biraz üstüne** çek, ucun dışını kâğıtla sil.",
        "Göz hizasında menisküsün alt kenarını **çizgiye indir**.",
        "Ucu alıcı kabın **çeperine değdirerek** akıt; etikette yazan **bekleme süresini** (ör. 5 s) bekle.",
        "**Ucunda kalan son damla üflenmez** (“Ex” pipet bu damla hesaba katılarak ayarlanmıştır). Yalnızca üst "
        "kısmında “üflemeli” (blow-out) işareti, ince bir halka olan pipetlerde son damla üflenir."],
    "Dereceli pipet": [
        "Tam pipet gibi doldurulur; mümkünse **sıfır çizgisinden** başlatılır.",
        "İstenen hacim iki okuma arasındaki farktır: başlangıç − bitiş.",
        "Ucuna kadar dereceli ve dereceli olmayan modeller vardır; etiketine bak.",
        "Tam pipetten **daha az hassastır**; tek hacim için tam pipet tercih edilir."],
    "Balon joje": [
        "Tartılan katıyı ya da alınan stok çözeltiyi huniyle balona aktar; tartım kabını piset ile birkaç kez çalkalayıp onu da ekle.",
        "Balonu yarıya kadar saf suyla doldur, çözünene kadar çalkala.",
        "Çözelti **oda sıcaklığına (20 °C)** gelsin; sıcak çözeltiyle çizgiye tamamlanmaz.",
        "Çizgiye yaklaşınca **damla damla** tamamla; göz hizasında **menisküsün alt kenarı çizgiye teğet** olmalı.",
        "Kapağı kapat, **ters çevirip 10–15 kez** karıştır.",
        "Balon joje **“In”** (içerdiği hacme göre) ayarlıdır; çözelti saklama kabı olarak kullanılmaz, şişeye aktarılır."],
    "Beher ve erlen": [
        "Üzerindeki çizgiler **yalnızca yaklaşık** hacmi gösterir (hata ±%5 ya da daha fazla olabilir).",
        "Karıştırma, ısıtma, geçici koyma ve titrasyon kabı olarak kullanılır; hassas ölçüm yapılmaz."],
    "Mikropipet": [
        "Hacmi ayarla; **ayar aralığının dışına çevirme** (ör. 10–100 µL'lik pipet 150'ye çevrilmez).",
        "Uygun **ucu** sıkıca tak; uca elle dokunma.",
        "Pipeti **dik** tut, pistonu **1. durağa** bastır, ucu sıvıya **2–3 mm** daldır.",
        "Pistonu **yavaşça** bırak, 1–2 saniye bekle, ucu sıvıdan çıkar.",
        "Ucu alıcı kabın çeperine değdir; pistonu **1. durağa**, sonra **2. durağa** bastırarak tamamen boşalt.",
        "Pistonu 2. durakta tutarak ucu çıkar, sonra bırak; **ucu at**, yeni numuneye yeni uç tak.",
        "Pipeti **yatay bırakma**, içinde sıvı varken ters çevirme; sıvı gövdeye kaçar."],
}

TOLERANS = pd.DataFrame({
    "Malzeme (A sınıfı)": ["Beher 100 mL (çizgi)", "Mezür 100 mL", "Büret 50 mL", "Balon joje 100 mL", "Tam pipet 10 mL"],
    "Hata payı": ["≈ ±5 mL", "±0,5 mL", "±0,05 mL", "±0,10 mL", "±0,02 mL"],
    "Bağıl hata (%)": [5.0, 0.5, 0.1, 0.1, 0.2]})


def _okuma_yeni():
    rr = rng()
    tur = str(rr.choice(["mezur", "buret"]))
    if tur == "mezur":
        deger = round(float(rr.integers(150, 950)) / 10, 1)
    else:
        deger = round(float(rr.integers(150, 4850)) / 100, 2)
    st.session_state.ok_tur, st.session_state.ok_deger = tur, deger
    st.session_state.ok_cevap = None


def sayfa_okuma():
    st.title("6 · Hacim ölçen malzemeler: okuma ve kullanım")
    st.markdown("""
Hacim ölçen bir malzemenin ne kadar hassas olduğu, **doğru okunduğu ve doğru kullanıldığı** kadar
geçerlidir. En pahalı büret bile yukarıdan bakılarak okunursa yanlış sonuç verir.""")

    st.header("1. Menisküs nedir, nereden okunur?")
    st.markdown("""
Dar bir kaptaki sıvının yüzeyi düz değil, **kavislidir**; buna **menisküs** denir.
- **Su ve sulu çözeltiler** camı ıslatır, kenarlardan yukarı tırmanır: yüzey **çukur (iç bükey)**
  olur, okuma **alt kenardan** yapılır.
- **Cıva** camı ıslatmaz: yüzey **tümsek (dış bükey)** olur, okuma **üst kenardan** yapılır.
- **Koyu renkli ya da opak** çözeltilerde (ör. permanganat) alt kenar görünmez; **üst kenardan** okunur.""")
    svg_goster(svg_meniskus_turleri())
    ipucu("<b>Okuma kartı:</b> Menisküsün hemen arkasına, biraz altına siyah bir kart (ya da siyah bantlı beyaz kart) "
          "tutulursa alt kenar koyu ve keskin bir çizgi olarak görünür; okuma kolaylaşır.")

    st.header("2. Göz hizası ve paralaks hatası")
    goz = st.radio("Gözünüz nerede?", ["Üstten bakıyorum", "Göz hizasında", "Alttan bakıyorum"], index=1, horizontal=True)
    svg, okunan = svg_meniskus({"Üstten bakıyorum": 1, "Göz hizasında": 0, "Alttan bakıyorum": -1}[goz])
    svg_goster(svg)
    if goz == "Göz hizasında":
        st.success("Doğru okuma: 46,00 mL.")
    else:
        st.error(f"Paralaks hatası: {okunan:.2f} mL okundu.")
    tablo(pd.DataFrame({"Bakış": ["Üstten", "Göz hizasında", "Alttan"],
                        "Mezür, pipet, balon (değer yukarı artar)": ["Büyük okunur", "Doğru", "Küçük okunur"],
                        "Büret (değer aşağı artar)": ["Küçük okunur", "Doğru", "Büyük okunur"]}))
    uyari("Göz hizasına gelmek için <b>malzemeyi göze kaldırma, sen eğil</b> ya da malzemeyi düz zeminde bırakıp "
          "gözünü hizaya getir. Bürette okurken büret dik olmalı.")

    st.header("3. Ölçek nasıl okunur?")
    st.markdown("""
**Adım 1: Bölme değerini bul.** İki rakamlı çizgi arasındaki farkı aradaki bölme sayısına böl.
Örnek: 40 ile 50 arasında 10 bölme varsa her bölme 1 mL'dir.

**Adım 2: Tam bölmeyi oku.** Menisküsün altında kalan son çizgiyi bul.

**Adım 3: Bir basamak tahmin et.** Analog ölçeklerde en küçük bölmenin **onda biri** kadar
tahmin edilir ve yazılır. Bu yüzden 1 mL bölmeli mezürde **bir**, 0,1 mL bölmeli bürette **iki
ondalık** yazılır.""")
    c1, c2 = st.columns(2)
    with c1:
        svg_goster(svg_olcek("mezur", 46.4))
        st.markdown("Mezür: 46 ile 47 arasında, yaklaşık 4/10'unda → **46,4 mL**")
    with c2:
        svg_goster(svg_olcek("buret", 23.47))
        st.markdown("Büret: 23,4 ile 23,5 arasında, yaklaşık 7/10'unda → **23,47 mL**")

    st.subheader("🎯 Okuma alıştırması")
    if "ok_tur" not in st.session_state:
        _okuma_yeni()
    tur, deger = st.session_state.ok_tur, st.session_state.ok_deger
    svg_goster(svg_olcek(tur, deger, goster=False))
    c1, c2 = st.columns([1.2, 1])
    adim = 0.1 if tur == "mezur" else 0.01
    tahmin = c1.number_input(f"Okumanız (mL, {'bir' if tur == 'mezur' else 'iki'} ondalık)", 0.0, 100.0, 0.0, adim,
                             format="%.1f" if tur == "mezur" else "%.2f", key=f"ok_giris_{tur}_{deger}")
    if c1.button("✔ Kontrol et"):
        st.session_state.ok_cevap = tahmin
    c2.button("🎲 Yeni ölçek", on_click=_okuma_yeni)
    dy = f"{deger:.{1 if tur == 'mezur' else 2}f}".replace(".", ",")
    if st.session_state.get("ok_cevap") is not None:
        fark = abs(st.session_state.ok_cevap - deger)
        tol = 0.2 if tur == "mezur" else 0.02
        if fark <= tol / 2 + 1e-9:
            st.success(f"Harika! Doğru değer {dy} mL.")
        elif fark <= tol + 1e-9:
            st.info(f"Çok yakın (tahmin basamağında küçük fark normaldir). Doğru değer {dy} mL.")
        else:
            st.error(f"Doğru değer {dy} mL. Bölme değerini ve ölçeğin yönünü "
                     f"({'yukarı' if tur == 'mezur' else 'aşağı'} doğru artıyor) kontrol edin.")

    st.header("4. Malzemeye göre doğru kullanım")
    sec = st.selectbox("Malzeme seçin", list(KULLANIM))
    for i, a in enumerate(KULLANIM[sec], 1):
        st.markdown(f"**{i}.** {a}")
    if sec == "Mikropipet":
        st.subheader("Mikropipet adım adım")
        k = st.select_slider("Adım", options=list(range(len(MP_ADIM))), format_func=lambda i: MP_ADIM[i][0])
        svg_goster(svg_mikropipet_adim(k))
        kutu(MP_ADIM[k][1])
        ipucu("<b>Ters pipetleme:</b> Gliserol, protein çözeltisi gibi <b>yapışkan ya da köpüren</b> sıvılarda "
              "çekerken <b>2. durağa</b> kadar basılır, boşaltırken yalnızca <b>1. durağa</b> kadar basılır; uçta "
              "kalan fazlalık atılır. Böylece hava kabarcığı ve eksik hacim önlenir.")

    st.header("5. Malzemenin üzerindeki yazılar")
    svg_goster(svg_etiket_kodlari())
    kartlar([("A / B", "A sınıfı daha hassastır (hata payı yaklaşık yarısı kadardır)."),
             ("Ex (TD)", "“Akıtmak için”: boşaltılan hacim doğrudur. Pipet, büret."),
             ("In (TC)", "“İçermek için”: içindeki hacim doğrudur. Balon joje."),
             ("20 °C", "Ayarın yapıldığı sıcaklık; sıcak çözelti ölçülmez."),
             ("Bekleme süresi", "Akıtma bittikten sonra beklenecek süre (ör. “Ex + 5 s”).")])
    st.subheader("Hangi malzeme ne kadar hassas?")
    c1, c2 = st.columns([1, 1.1])
    with c1:
        tablo(TOLERANS)
    with c2:
        fig = go.Figure(go.Bar(x=TOLERANS["Bağıl hata (%)"], y=TOLERANS["Malzeme (A sınıfı)"], orientation="h",
                               marker_color=["#D9534F", TURUNCU, YESIL, YESIL, YESIL],
                               text=[f"%{v:g}".replace(".", ",") for v in TOLERANS["Bağıl hata (%)"]], textposition="outside"))
        fig.update_layout(xaxis_type="log", xaxis_title="Bağıl hata (%, log ölçek)", yaxis=dict(autorange="reversed"))
        ciz(fig, 300)
    st.caption("Değerler A sınıfı malzeme için tipik hata paylarıdır (ISO standartlarına yakın); beherdeki değer "
               "yaklaşıktır, beherler ölçüm aracı olarak sınıflandırılmaz.")
    alistirma_blogu("okuma", "Okuma ve kullanım", gen_okuma)


# ===========================================================================
# SORU ÜRETİCİLERİ
# ===========================================================================
def _secim(r, metin, dogru, yanlis, cozum):
    temiz = [y for y in dict.fromkeys(yanlis) if y != dogru][:3]
    return soru_secim(r, metin, dogru, temiz, [_md(c) if isinstance(c, str) else c for c in cozum])


def _tamamla(r, sabit, havuz):
    gerek = SORU_SAYISI - len(sabit)
    secilen = _kavram_sec(r, havuz, min(gerek, len(havuz)))
    hepsi = sabit + secilen
    sira = r.permutation(len(hepsi))
    return [hepsi[i] for i in sira]


def _ek(r, liste):
    return [_secim(r, m, d, y, c) for m, d, y, c in liste]


def _virgul(x, od=2):
    return f"{x:.{od}f}".replace(".", ",")


# ---------------------------------------------------------------------------
def gen_guvenlik(r):
    sabit = []
    kural, dogru_mu = KURALLAR[int(r.integers(0, len(KURALLAR)))]
    sabit.append(_secim(r, f"“{kural}” Bu ifade için hangisi doğrudur?",
                        "Doğru bir laboratuvar kuralıdır" if dogru_mu else "Hatalı bir davranıştır",
                        ["Hatalı bir davranıştır" if dogru_mu else "Doğru bir laboratuvar kuralıdır",
                         "Yalnızca mikrobiyoloji laboratuvarında geçerlidir", "Yalnızca öğretmen izin verirse geçerlidir"],
                        ["Bkz. 1. bölüm, kurallar listesi."]))
    olanak = list(LAB_OLANAK)[int(r.integers(0, len(LAB_OLANAK)))]
    ad, tanim = LAB_OLANAK[olanak]
    diger = [LAB_OLANAK[k][0] for k in LAB_OLANAK if k != olanak]
    sabit.append(_secim(r, f"“{tanim.split('.')[0]}.” Bu açıklama hangi güvenlik olanağına aittir?", ad,
                        [diger[int(i)] for i in r.permutation(len(diger))[:3]], [f"{ad}: {tanim}"]))
    havuz = _ek(r, [
        ("Derişik asit seyreltilirken doğru yol hangisidir?", "Bol suyun içine asit yavaş yavaş eklenir",
         ["Asidin üzerine hızla su dökülür", "Asit ve su aynı anda dökülür", "Asit önce ısıtılır, sonra su eklenir"],
         ["Asit–su karışması çok ısı açığa çıkarır; az su asidin üzerine gelirse kaynayıp sıçrar."]),
        ("Asidin üzerine su dökülürse ne olabilir?", "Su anında kaynar ve asitle birlikte sıçrar",
         ["Hiçbir şey olmaz", "Asit donar", "Çözelti renk değiştirir"], ["Isı az miktardaki suda toplanır."]),
        ("Laboratuvara girerken ilk yapılması gereken hangisidir?", "Kaban çıkarılıp laboratuvar önlüğü giyilir",
         ["Eldivenle telefon kullanılır", "Pencereler kapatılır", "Kimyasallar koklanarak tanınır"],
         ["Önlük; gerekiyorsa gözlük ve eldiven."]),
        ("Tüpte sıvı ısıtılırken tüpün ağzı nereye çevrilir?", "Kimsenin bulunmadığı tarafa",
         ["Kendine", "Yanındaki arkadaşına", "Tavana dik olarak yüze yakın"], ["Kaynayan sıvı fışkırabilir."]),
        ("Tartım sonuçları nereye yazılır?", "Laboratuvar defterine", ["Küçük kâğıtlara", "Ele", "Hiçbir yere; akılda tutulur"],
         ["Kayıt, sonucun güvenilirliğinin parçasıdır."]),
        ("Hazırlanan çözeltinin şişesine hangi bilgiler yazılır?", "Adı, derişimi ve hazırlanma tarihi",
         ["Yalnızca rengi", "Hazırlayanın telefon numarası", "Hiçbir şey; şişe görülünce anlaşılır"],
         ["Etiketsiz çözelti en büyük kaza nedenlerinden biridir."]),
        ("Kullanılmayan kimyasal ne yapılır?", "Orijinal şişesine geri konmaz; uygun atık kabına ya da ayrı kaba alınır",
         ["Orijinal şişesine geri dökülür", "Lavaboya dökülür", "Kâğıda dökülüp bırakılır"],
         ["Orijinal şişedeki kimyasal kirlenebilir."]),
        ("Kırık cam nereye atılır?", "Kırık cam kutusuna", ["Normal çöp kutusuna", "Lavaboya", "Kâğıt atık kutusuna"],
         ["Temizlik personelini korumak için."]),
        ("Çeker ocaklar ne sıklıkla uzman kontrolünden geçmelidir?", "Yılda en az bir kez",
         ["Hiçbir zaman", "On yılda bir", "Yalnızca arıza olunca"], ["Ders notu: yılda bir kez."]),
        ("Laboratuvardan en son çıkan kişinin sorumluluğu nedir?", "Su, gaz ve elektriğin kapalı olduğunu kontrol etmek",
         ["Pencereleri açık bırakmak", "Kimyasalları masada bırakmak", "Çeker ocağı açık bırakmak"],
         ["Kurallar listesi."]),
        ("Sıvı pipete nasıl çekilir?", "Puar ya da pipet pompasıyla", ["Ağızla", "Pipeti salladıktan sonra ağızla",
                                                                     "Eldivenle ağızla"], ["Ağızla pipet çekilmez."]),
        ("Dökülen kimyasalı temizlerken neden kâğıt kullanılmamalıdır?", "Kolayca parlayabilir ya da kimyasalla tepkimeye girebilir",
         ["Kâğıt pahalıdır", "Kâğıt kimyasalı seyreltir", "Kâğıt suyu emmez"], ["Ders notu, kural listesi."]),
        ("Şişeden sıvı dökerken etiket nasıl tutulur?", "Avuç içine (yukarı) gelecek şekilde",
         ["Aşağıya, akan damlaya gelecek şekilde", "Etiket koparılarak", "Fark etmez"],
         ["Damla etiketin ters yüzünden akar, etiket okunur kalır."]),
        ("Hangisi laboratuvarda bulunması gereken temel olanaklardan biri DEĞİLDİR?", "Televizyon",
         ["Göz duşu", "Yangın söndürücü", "Çeker ocak"], ["Temel olanaklar: havalandırma ve çeker ocak, depolar, musluklar, "
                                                           "vücut ve göz duşları, yangın söndürücüler."]),
        ("Termometre gibi yuvarlanabilen cam eşyalar nasıl bırakılır?", "Yuvarlanıp düşmeyecek şekilde",
         ["Tezgâhın kenarına", "Lavabonun içine", "Önlüğün cebine"], ["Kırılma ve cıva dökülmesi riski."]),
        ("Laboratuvarda hangisi yasaktır?", "Yemek, içmek ve sigara içmek", ["Önlük giymek", "Deftere yazmak", "Gözlük takmak"],
         ["Kimyasalların ağız yoluyla alınma riski."]),
        ("Deney sürerken laboratuvardan ayrılmak için hangisi doğrudur?", "Deneyin başından hiçbir nedenle ayrılınmaz",
         ["Kısa süre için ayrılınabilir", "Isıtıcı açıkken ayrılınabilir", "Arkadaşa haber vermek yeterlidir"],
         ["Kural listesi."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_kimyasal(r):
    sabit = []
    olay = list(KAZALAR)[int(r.integers(0, len(KAZALAR)))]
    adim = KAZALAR[olay][0].replace("**", "")
    yanlis = {"Göze kimyasal sıçradı": ["Gözü ovarak temizlemek", "Göze bikarbonat damlatmak", "Gözü kapatıp beklemek"],
              "Cilde asit ya da baz döküldü": ["Hemen bikarbonat sürmek", "Krem sürüp beklemek", "Giysileri üzerinde bırakmak"],
              "Hidroflorik asit (HF) teması": ["Ağrı yoksa bir şey yapmamak", "Sirkeyle silmek", "Yağ sürmek"],
              "Kimyasal yutuldu": ["%5 bakır sülfat içirip kusturmak", "Parmakla kusturmak", "Süt içirip beklemek"],
              "Bir kişinin giysisi alev aldı": ["Kişiyi koşturmak", "Üzerine eter dökmek", "Pencereyi açmak"],
              "Laboratuvarda yangın çıktı": ["Önce kendi başına söndürmeye çalışıp kimseye söylememek",
                                             "Çözücü yangınına su sıkmak", "Kapıları kilitlemek"],
              "Cıva döküldü (kırık termometre)": ["Ev tipi elektrikli süpürgeyle çekmek", "Lavaboya akıtmak", "Elle toplamak"],
              "Cam kırıldı": ["Elle toplamak", "Normal çöpe atmak", "Ayakla kenara itmek"]}[olay]
    sabit.append(_secim(r, f"“{olay}” durumunda ilk yapılması gereken hangisidir?", adim, yanlis,
                        ["Doğru sıra: " + " → ".join(a.replace("**", "") for a in KAZALAR[olay])]))
    g = GHS[int(r.integers(0, len(GHS)))]
    diger = [x[1] for x in GHS if x != g]
    sabit.append(_secim(r, f"“{g[2]}” gibi maddelerin şişesinde hangi tehlike işareti beklenir?", g[1],
                        [diger[int(i)] for i in r.permutation(len(diger))[:3]], [f"{g[1]}: ör. {g[2]}."]))
    havuz = _ek(r, [
        ("Kimyasal yutulduğunda doğru yaklaşım hangisidir?", "Kusturmadan 112 ve Zehir Danışma (114) aranır",
         ["%5 bakır sülfatla kusturulur", "Parmakla kusturulur", "Bol tuzlu su içirilir"],
         ["Bakır sülfatla kusturma eski ve tehlikeli bir uygulamadır; artık önerilmez."]),
        ("Ulusal Zehir Danışma Merkezi'nin telefon numarası hangisidir?", "114", ["112", "155", "110"],
         ["UZEM 114, 24 saat hizmet verir."]),
        ("Göze kimyasal kaçınca en az ne kadar süre yıkanır?", "15–20 dakika", ["10 saniye", "1 dakika", "Hiç yıkanmaz"],
         ["Göz kapakları açık tutularak göz duşunda."]),
        ("Kuruyunca patlayıcı olduğu için ıslak saklanan asit hangisidir?", "Pikrik asit",
         ["Asetik asit", "Hidroklorik asit", "Sitrik asit"], ["Ders notu: en az %10 sulu."]),
        ("Deriden geçip derin yanık ve zehirlenme yapan, kalsiyum glukonat jeli gerektiren asit hangisidir?",
         "Hidroflorik asit (HF)", ["Asetik asit", "Fosforik asit", "Borik asit"], ["HF son derece tehlikelidir."]),
        ("Isınınca zehirli azot oksit buharları veren asit hangisidir?", "Nitrik asit",
         ["Sülfürik asit", "Asetik asit", "Hidroklorik asit"], ["Çeker ocakta çalışılır."]),
        ("Sodyum, potasyum gibi alkali metaller nasıl saklanır?", "Kerosen ya da inert gaz altında",
         ["Su içinde", "Açık havada", "Alkol içinde"], ["Su ve nemle şiddetli tepkime verir."]),
        ("Alkali metal yangınında ne kullanılmaz?", "Su", ["Kuru kum", "Toz grafit", "D sınıfı söndürücü"],
         ["Su ile patlayıcı tepkime."]),
        ("Eter yangını ne ile söndürülür?", "CO₂", ["Su", "Islak bez", "Eter"], ["Ders notu."]),
        ("Dietil eterin en büyük tehlikesi nedir?", "Çok uçucu olup kolay tutuşması",
         ["Radyoaktif olması", "Katı olması", "Kokusuz olması"], ["Parlama noktası yaklaşık −45 °C."]),
        ("Cıva döküldüğünde hangisi YAPILMAZ?", "Ev tipi elektrikli süpürgeyle çekmek",
         ["Alanı havalandırmak", "Toplama kitiyle toplamak", "Kalıntıya kükürt tozu serpmek"],
         ["Süpürge cıvayı buharlaştırıp yayar."]),
        ("Kalsiyumu çöktürerek zarar veren madde grubu hangisidir?", "Oksalatlar",
         ["Eterler", "Alkali metaller", "Nitratlar"], ["Kalsiyum oksalat oluşur."]),
        ("Bir kişinin giysisi alev aldığında ne yapılır?", "Dur – yat – yuvarlan; yangın battaniyesi",
         ["Koşturulur", "Su yerine alkol dökülür", "Pencere açılır"], ["Koşmak alevi büyütür."]),
        ("Yangın çıkınca yapılacak ilk iş nedir?", "Yangını haber vermek", ["Pencereyi açmak", "Eşyaları toplamak",
                                                                          "Kimyasalları taşımak"], ["Ders notu."]),
        ("Cilde asit dökülünce bikarbonat sürmek neden önerilmez?", "Nötrleşme ısısı yanığı derinleştirebilir",
         ["Bikarbonat pahalıdır", "Bikarbonat asidi artırır", "Bikarbonat suda çözünmez"],
         ["Doğrusu: bol akan suyla 15–20 dk yıkamak."]),
        ("Kimyasalın tehlikelerini ve kaza anında yapılacakları anlatan belge hangisidir?", "Güvenlik Bilgi Formu (GBF / SDS)",
         ["Fatura", "Kalibrasyon sertifikası", "Garanti belgesi"], ["Her kimyasal için bulunur."]),
        ("Kırmızı çerçeveli eşkenar dörtgen içinde kuru kafa işareti neyi gösterir?", "Akut zehirli madde",
         ["Yanıcı madde", "Basınçlı gaz", "Çevreye zararlı madde"], ["GHS06."]),
        ("Siyanür zehirlenmesinde panzehir nasıl verilir?", "Sağlık personeli tarafından damar yoluyla",
         ["Laboratuvarda ağızdan içirilerek", "Deriye sürülerek", "Koklatılarak"],
         ["Ağızdan sodyum tiyosülfat / nitrit içirmek güncel bir uygulama değildir."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_cam(r):
    sabit = []
    k = list(TUM_MALZEME)[int(r.integers(0, len(TUM_MALZEME)))]
    ad, _, ne, _ = TUM_MALZEME[k]
    diger = [TUM_MALZEME[x][0] for x in TUM_MALZEME if x != k]
    temiz = re.sub("<[^>]+>", "", ne).split(".")[0]
    sabit.append(_secim(r, f"“{temiz}.” Bu tanım hangi malzemeye aittir?", ad,
                        [diger[int(i)] for i in r.permutation(len(diger))[:3]], [f"{ad}: {re.sub('<[^>]+>', '', ne)}"]))
    bas = round(float(r.uniform(0.5, 15)), 2)
    son = round(bas + float(r.uniform(5, 30)), 2)
    sabit.append(soru_sayi(f"Titrasyonda büretin başlangıç okuması {_virgul(bas)} mL, bitiş okuması {_virgul(son)} mL. "
                           "Harcanan hacim kaç mL'dir?", round(son - bas, 2),
                           [_tx(rf"V = {son} - {bas} = {son - bas:.2f}\ \text{{mL}}")],
                           yanlis=[son + bas, son, bas], ondalik=2))
    havuz = _ek(r, [
        ("Tam 250 mL ve derişimi bilinen bir çözelti hazırlamak için hangisi kullanılır?", "Balon joje",
         ["Beher", "Mezür", "Erlen"], ["Beher yalnızca yaklaşık hacim gösterir."]),
        ("Titrasyonda harcanan çözelti hacmini ölçen malzeme hangisidir?", "Büret", ["Mezür", "Huni", "Beher"],
         ["Büret musluklu, taksimatlıdır."]),
        ("Titrasyonda titre edilen çözelti hangi kaba konur?", "Erlen", ["Balon joje", "Büret", "Desikatör"],
         ["Konik yapısı çalkalarken sıçratmaz."]),
        ("Mezür hangi amaçla kullanılır?", "Bir sıvıyı ölçüp başka kaba aktarmak",
         ["Standart çözelti hazırlamak", "Kül tayini", "Numuneyi soğutmak"], ["Hassas ölçüm için kullanılmaz."]),
        ("Hangisi en hassas hacim ölçer?", "Tam pipet", ["Beher", "Erlen", "Mezür"], ["Tek hacim, çok hassas."]),
        ("Sulu çözeltilerde menisküs nereden okunur?", "Alt kenarından, göz hizasında",
         ["Üst kenarından", "Ortasından, yukarıdan bakarak", "Herhangi bir yerinden"], ["Paralaks hatası önlenir."]),
        ("Mezüre yukarıdan bakılarak okuma yapılırsa ne olur?", "Değer olduğundan büyük okunur",
         ["Değer olduğundan küçük okunur", "Hata olmaz", "Değer sıfır okunur"], ["Paralaks hatası."]),
        ("A sınıfı cam malzemenin B sınıfından farkı nedir?", "Hata payı (toleransı) daha küçüktür",
         ["Daha ucuzdur", "Plastiktir", "Isıya dayanıksızdır"], ["Analizde A sınıfı tercih edilir."]),
        ("Kurutulmuş kabı nem çekmeden soğutmak için ne kullanılır?", "Desikatör", ["Etüv", "Beher", "Huni"],
         ["İçinde silika jel, susuz CaCl₂ gibi nem çekici madde vardır."]),
        ("Kül tayininde numune hangi kaba konur?", "Porselen kroze", ["Plastik beher", "Balon joje", "Mezür"],
         ["Yüksek sıcaklığa dayanıklıdır."]),
        ("Puarda 'S' harfi neyi gösterir?", "Sıvıyı çekmeyi", ["Havayı boşaltmayı", "Sıvıyı boşaltmayı", "Sterilizasyonu"],
         ["A: hava boşalt, S: sıvı çek (suction), E: boşalt."]),
        ("Mikropipet kullanırken hangisi doğrudur?", "Her numunede uç değiştirilir",
         ["Aynı uç bütün numunelerde kullanılır", "Ayar aralığı dışına çevrilir", "Ağızla çekilir"],
         ["Çapraz bulaşmayı önler."]),
        ("Cam malzemenin temiz olduğu nasıl anlaşılır?", "Su, yüzeyde düzgün bir film hâlinde akar",
         ["Su damlacıklar hâlinde kalır", "Cam parlak görünür", "Cam kokusuzdur"], ["Yağlı yüzeyde su damlacık yapar."]),
        ("Eski kaynaklardaki bikromatlı (kromik) asit temizleme çözeltisi neden artık kullanılmıyor?",
         "Altı değerlikli krom kanserojen ve çevreye zararlıdır", ["Çok pahalıdır", "Camı temizlemez", "Kokusu yoktur"],
         ["Yerine laboratuvar deterjanları ve seyreltik asitler kullanılır."]),
        ("Cam temizliğinde son durulama ne ile yapılır?", "Saf su", ["Musluk suyu", "Deterjan", "Alkol ve yağ"],
         ["Musluk suyundaki iyonlar kalmasın diye."]),
        ("Hangi malzemenin boynunda tek bir ölçü çizgisi vardır?", "Balon joje", ["Mezür", "Büret", "Dereceli pipet"],
         ["Tek hacim ölçer."]),
        ("Filtre kâğıdıyla süzme için hangisi kullanılır?", "Huni", ["Büret", "Desikatör", "Kroze"], ["Süzme ve aktarma."]),
        ("Mikrolitre düzeyinde hacim aktarmak için hangisi kullanılır?", "Mikropipet", ["Mezür", "Beher", "Erlen"],
         ["µL düzeyi, ayarlanabilir."]),
        ("Hidroflorik asit hangi kapta saklanır?", "Plastik (PE, PP ya da PTFE) kapta", ["Cam şişede", "Porselen krozede",
                                                                                        "Metal kutuda"], ["HF camı eritir."]),
        ("Aseton, hekzan gibi organik çözücüler için hangi kap daha uygundur?", "Cam", ["Polistiren (PS) plastik",
                                                                                        "Kâğıt bardak", "Lastik torba"],
         ["Çoğu plastik organik çözücülerde çözünür ya da yumuşar."]),
        ("İz element (metal) analizinde neden plastik kap tercih edilir?", "Cam yüzeyden iz metal bırakabilir",
         ["Plastik daha ağırdır", "Plastik ısıya dayanıklıdır", "Camdan pahalıdır"], ["Kontaminasyonu önlemek için."]),
        ("15 ya da 50 mL'lik, vidalı kapaklı, konik dipli plastik santrifüj tüpüne ne denir?", "Falkon tüpü",
         ["Eppendorf tüpü", "Deney tüpü", "Petri kabı"], ["Santrifüj ve numune saklama."]),
        ("0,5–2 mL'lik kapaklı küçük plastik tüpe ne denir?", "Eppendorf (mikrosantrifüj) tüpü", ["Falkon tüpü", "Büret",
                                                                                                  "Balon joje"], ["µL düzeyi."]),
        ("Saf suyla durulama ve hacim tamamlamada kullanılan sıkmalı plastik şişeye ne denir?", "Piset",
         ["Puar", "Desikatör", "Kroze"], ["Yıkama şişesi."]),
        ("Mikroorganizmaları besiyerinde üretmek için hangi kap kullanılır?", "Petri kabı", ["Balon joje", "Büret", "Kroze"],
         ["Kapaklı yayvan kap."]),
        ("Işığa duyarlı çözeltiler hangi şişede saklanır?", "Amber (kahverengi) şişe", ["Şeffaf cam şişe", "Petri kabı",
                                                                                        "Piset"], ["Işıktan korur."]),
        ("Katı numuneyi toz hâline getirmek için hangisi kullanılır?", "Havan ve tokmak", ["Büret", "Desikatör", "Piset"],
         ["Porselen havan."]),
        ("Kül fırınından sıcak kroze ne ile alınır?", "Maşa (ve ısıya dayanıklı eldiven)", ["Elle", "Spatülle", "Kâğıtla"],
         ["Yanık riski."]),
        ("Hangi plastik otoklavlanabilir (yaklaşık 121 °C)?", "Polipropilen (PP)", ["Polistiren (PS)", "Kâğıt", "Parafin"],
         ["PS ısıya dayanıksızdır."]),
        ("Polistiren (PS) küvet hangi bölgede kullanılamaz?", "UV bölgesi", ["Görünür bölge", "Hiçbiri", "Her bölgede kullanılır"],
         ["UV için kuvars küvet gerekir."]),
        ("Bek alevinin en sıcak bölgesi hangisidir?", "Mavi alev bölgesi", ["Sarı alev", "Alevin dışı", "Gaz borusu"],
         ["Tam yanma."]),
        ("Pipet uçları için hangisi doğrudur?", "Her numunede yeni uç kullanılır", ["Aynı uç yıkanmadan kullanılır",
                                                                                   "Uca elle dokunulur", "Uç gerekmez"],
         ["Çapraz bulaşma."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_olcum(r):
    sabit = []
    ds = round(float(r.choice([0.4, 0.8, 1.2, 1.5, 2.3, 3.6, 4.2, 0.25])), 2)
    sabit.append(soru_sayi(f"{_virgul(ds)} dS/m kaç µS/cm eder?", ds * 1000,
                           [_tx(rf"1\ \text{{dS/m}} = 1000\ \mu\text{{S/cm}} \Rightarrow {ds}\times 1000 = {ds * 1000:g}")],
                           yanlis=[ds * 100, ds * 10, ds * 10000]))
    us = int(r.choice([350, 780, 1413, 2500, 5200, 640]))
    sabit.append(soru_sayi(f"{us} µS/cm kaç dS/m eder?", us / 1000,
                           [_tx(rf"{us} \div 1000 = {us / 1000:g}\ \text{{dS/m}}")], yanlis=[us / 100, us / 10, us / 10000],
                           ondalik=3))
    gercek = 7.00
    kayma = round(float(r.choice([0.3, 0.4, -0.3, 0.25])), 2)
    olc = [round(gercek + kayma + d, 2) for d in (0.01, -0.01, 0.0)]
    sabit.append(_secim(r, f"Gerçek değeri pH 7,00 olan tampon üç kez ölçülüyor: {', '.join(_virgul(x) for x in olc)}. "
                           "Bu ölçüm için hangisi doğrudur?", "Kesin ama doğru değil; kalibrasyon gerekir",
                        ["Hem doğru hem kesin", "Doğru ama kesin değil", "Ne doğru ne kesin"],
                        ["Değerler birbirine çok yakın (kesin) ama gerçek değerden aynı yöne sapıyor (sistematik hata)."]))
    havuz = _ek(r, [
        ("Doğruluk neyi ifade eder?", "Ölçülen değerin gerçek değere yakınlığını",
         ["Tekrarların birbirine yakınlığını", "Cihazın fiyatını", "Ölçümün hızını"], ["Kesinlik ise tekrarların yakınlığıdır."]),
        ("Kesinlik neyi ifade eder?", "Tekrarlanan ölçümlerin birbirine yakınlığını",
         ["Gerçek değere yakınlığı", "Ölçüm birimini", "Kalibrasyon tarihini"], ["Tekrarlanabilirlik."]),
        ("Her tartımda 0,05 g fazla gösteren terazinin hatası hangi türdendir?", "Sistematik", ["Rastgele", "Kaba", "Hata yoktur"],
         ["Hep aynı yönde ve aynı büyüklükte."]),
        ("Sistematik hata nasıl düzeltilir?", "Kalibrasyonla", ["Ölçümü çok tekrarlayarak", "Ortalama alarak", "Hızlı ölçerek"],
         ["Tekrar etmek sistematik hatayı yok etmez."]),
        ("Rastgele hata nasıl azaltılır?", "Tekrarlı ölçüm yapıp ortalama alarak", ["Kalibrasyonla tamamen",
                                                                                   "Tek ölçüm yaparak", "Virgülü silerek"],
         ["Rastgele hatalar ortalamada birbirini götürür."]),
        ("Numunelerin karışması hangi hata türüdür?", "Kaba hata", ["Sistematik hata", "Rastgele hata", "Paralaks"],
         ["Dikkatsizlik."]),
        ("Seyreltik sulu çözeltilerde mg/L hangi birime yaklaşık eşittir?", "ppm", ["ppb", "%", "NTU"], ["mg/L ≈ ppm."]),
        ("Suda ağır metal derişimi genellikle hangi birimle verilir?", "µg/L (≈ ppb)", ["°Brix", "NTU", "dS/m"],
         ["İz düzeyde."]),
        ("Toprak ve yaprakta element miktarı hangi birimle verilir?", "mg/kg", ["mg/L", "NTU", "°Brix"],
         ["Katı numune, kuru madde esasıyla."]),
        ("Bulanıklık birimi hangisidir?", "NTU", ["°Brix", "µS/cm", "ppm"], ["Türbidimetre."]),
        ("Türkiye'nin ulusal ölçüm standartlarından sorumlu kurumu hangisidir?", "TÜBİTAK UME",
         ["TÜRKAK", "TSE", "Sağlık Bakanlığı"], ["Ulusal Metroloji Enstitüsü."]),
        ("Ölçüme başlamadan bir kontrol standardı okumaya ne denir?", "Günlük kontrol", ["Akreditasyon", "Dara", "Kör"],
         ["Kabul sınırı dışındaysa ölçüme geçilmez."]),
        ("Kalibrasyon tarihi geçmiş cihaz için doğru davranış hangisidir?", "Kalibre edilmeden ölçüm yapılmaz",
         ["Ölçüm yapılır, sonra düzeltilir", "Ölçüm iki kez yapılır", "Fark etmez"], ["Kural."]),
        ("İzlenebilirlik ne demektir?", "Sonucun referans malzemelerle ulusal standarda bağlanması",
         ["Cihazın taşınabilir olması", "Numunenin izinin sürülmesi", "Sonucun internette yayınlanması"],
         ["Sertifikalı referans malzeme → ulusal standart."]),
        ("Nem, kül ve protein yüzdesi verilirken neyin belirtilmesi zorunludur?", "Yaş mı kuru ağırlık mı esas alındığı",
         ["Cihazın rengi", "Analizi yapanın yaşı", "Laboratuvarın kat numarası"], ["Sonuçlar çok farklı çıkar."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_terazi(r):
    sabit = []
    kap = round(float(r.uniform(20, 40)), 4)
    yas = round(float(r.uniform(3, 6)), 4)
    nem = float(r.uniform(5, 85))
    kuru = round(yas * (1 - nem / 100), 4)
    nem_g = (yas - kuru) / yas * 100
    sabit.append(soru_sayi(f"Boş kap {_virgul(kap, 4)} g; kap + yaş numune {_virgul(kap + yas, 4)} g; kurutmadan sonra "
                           f"kap + kuru numune {_virgul(kap + kuru, 4)} g. Numunenin nemi yüzde kaçtır?", round(nem_g, 2),
                           [_md(f"Yaş numune = {yas:.4f} g, kuru numune = {kuru:.4f} g"),
                            _tx(rf"\text{{Nem}} = \frac{{{yas:.4f} - {kuru:.4f}}}{{{yas:.4f}}}\times 100 = {nem_g:.2f}\,\%")],
                           yanlis=[round(100 - nem_g, 2), round((yas - kuru) / kuru * 100, 2), round(nem_g / 10, 2)],
                           ondalik=2))
    nem2 = int(r.integers(5, 90))
    sabit.append(soru_sayi(f"Nemi %{nem2} olan bir gıdanın kuru madde oranı yüzde kaçtır?", 100 - nem2,
                           [_tx(rf"\text{{Kuru madde}} = 100 - {nem2} = {100 - nem2}\,\%")], yanlis=[nem2, nem2 / 2, 100 + nem2]))
    m = round(float(r.uniform(2, 5)), 4)
    kul = round(float(r.uniform(0.02, 0.25)), 4)
    sabit.append(soru_sayi(f"{_virgul(m, 4)} g numune yakıldıktan sonra {_virgul(kul, 4)} g kül kalıyor. Kül yüzde kaçtır?",
                           round(kul / m * 100, 2), [_tx(rf"\frac{{{kul}}}{{{m}}}\times 100 = {kul / m * 100:.2f}\,\%")],
                           yanlis=[round(kul * 100, 2), round(m / kul, 2), round(100 - kul / m * 100, 2)], ondalik=2))
    havuz = _ek(r, [
        ("Okunabilirliği 0,0001 g olan terazi hangisidir?", "Analitik terazi", ["Teknik terazi", "Hassas terazi", "Baskül"],
         ["0,1 mg."]),
        ("Toprak gibi büyük numuneler için hangi terazi yeterlidir?", "Teknik terazi", ["Analitik terazi", "Mikroterazi",
                                                                                       "Hiçbiri"], ["0,1–0,01 g."]),
        ("Sıcak numune neden tartılmaz?", "Isınan hava kefeyi kaldırır, değer kayar ve düşük okunur",
         ["Terazi erir", "Numune ağırlaşır", "Ekran kapanır"], ["Önce desikatörde soğutulur."]),
        ("Dara (tare) tuşu ne işe yarar?", "Kabın kütlesini sıfırlar", ["Teraziyi kapatır", "Kalibrasyon yapar",
                                                                       "Numuneyi kurutur"], ["Sonra numune eklenir."]),
        ("Analitik terazide tartım yapılırken kapılar nasıl olmalıdır?", "Kapalı", ["Açık", "Yarı açık", "Fark etmez"],
         ["Hava akımı sonucu etkiler."]),
        ("Terazinin düz durduğu neyle kontrol edilir?", "Su terazisi (kabarcık)", ["Termometre", "pH metre", "Dara tuşu"],
         ["Kabarcık ortada olmalı."]),
        ("Nem tayininde referans yöntem hangisidir?", "Etüvde 105 °C'de sabit ağırlığa kadar kurutma",
         ["Kül fırınında 550 °C", "Halojen analizörde 1 dakika", "Güneşte kurutma"], ["Halojen analizör referansla doğrulanır."]),
        ("Kül tayini hangi cihazda yapılır?", "Kül fırını", ["Etüv", "Desikatör", "Santrifüj"], ["Gıdada 525–550 °C."]),
        ("Kül fırını en çok kaç dereceye kadar çıkabilir?", "1100 °C", ["105 °C", "250 °C", "37 °C"], ["Ders notu."]),
        ("Etüv genellikle en çok kaç dereceye kadar çıkar?", "250 °C", ["1100 °C", "50 °C", "2000 °C"], ["±1 °C sabit tutar."]),
        ("“Sabit ağırlık” ne demektir?", "Art arda iki kurutma–tartımda kütlenin değişmemesi",
         ["Numunenin hiç kurutulmaması", "Terazinin sabitlenmesi", "Kabın değişmemesi"], ["Kurutma tamamlanmıştır."]),
        ("Şekerli gıdalarda nem tayininde hangi risk vardır?", "Karamelleşme", ["Donma", "Patlama", "Radyasyon"],
         ["Vakum etüv ve düşük sıcaklık kullanılır."]),
        ("Buzdolabı ve etüvün sıcaklığını sürekli izleyen cihaz hangisidir?", "Veri kaydedici (datalogger)",
         ["Refraktometre", "Puar", "Türbidimetre"], ["Kayıt tutar."]),
        ("Sütte yağ tayininde hangi santrifüj kullanılır?", "Gerber santrifüjü", ["Soxhlet", "Kjeldahl", "Muffle"],
         ["Ders notu."]),
        ("Kurutma ve kül analizinden önce kap neden etüvde kurutulup desikatörde soğutulur?", "Kabın darası doğru alınsın diye",
         ["Kap süslensin diye", "Kap sterilize olsun diye", "Kap ağırlaşsın diye"], ["Nem ve sıcaklık tartımı bozar."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_elektro(r):
    sabit = []
    ect = int(r.integers(4, 40)) * 100
    t = int(r.choice([15, 18, 20, 22, 28, 30, 32, 35]))
    ec25 = ect / (1 + 0.02 * (t - 25))
    sabit.append(soru_sayi(f"{t} °C'de ölçülen EC {ect} µS/cm. 25 °C'ye düzeltilmiş EC yaklaşık kaç µS/cm'dir? "
                           "(1 °C başına %2)", round(ec25), [_tx(rf"EC_{{25}} = \frac{{{ect}}}{{1 + 0{{,}}02({t} - 25)}} = {ec25:.0f}")],
                           yanlis=[ect, round(ect * (1 + 0.02 * (t - 25))), round(ect - 0.02 * (t - 25))]))
    sabit.append(_secim(r, f"Sıcaklık 25 °C'nin {'üstünde' if t > 25 else 'altında'} ({t} °C) ölçülen EC, 25 °C'ye "
                           "düzeltilince nasıl değişir?", "Azalır" if t > 25 else "Artar",
                        ["Artar" if t > 25 else "Azalır", "Değişmez", "Sıfır olur"],
                        ["Sıcaklık arttıkça EC artar; düzeltme bu etkiyi geri alır."]))
    havuz = _ek(r, [
        ("pH metre kalibrasyonuna hangi tamponla başlanır?", "pH 7,00", ["pH 4,01", "pH 10,01", "Saf su"],
         ["pH 7 sıfır noktasını (0 mV) ayarlar; sonra eğim için 4 ve/veya 10."]),
        ("pH elektrodu eğiminin kabul aralığı genellikle nedir?", "%95–105", ["%50–60", "%10–20", "%150–200"], ["Ders notu."]),
        ("pH elektrodu nerede saklanır?", "Saklama çözeltisinde (genellikle 3 M KCl)", ["Saf suda uzun süre", "Kuru olarak",
                                                                                         "Asitte"], ["Kuru ve saf su zarar verir."]),
        ("pH elektrodunun cam ucu nasıl kurulanır?", "Kâğıtla hafifçe, ovmadan", ["Kâğıtla sertçe ovarak", "Bezle fırçalayarak",
                                                                                   "Hiç kurulanmaz, sallanır"], ["Cam zar hassastır."]),
        ("Kullanılmış tampon çözelti ne yapılır?", "Şişeye geri dökülmez", ["Şişeye geri dökülür", "Saf suyla karıştırılıp saklanır",
                                                                           "Ertesi gün tekrar kullanılır"], ["Kirlenmiş olabilir."]),
        ("25 °C'de ideal pH elektrodunun eğimi yaklaşık kaç mV/pH'dır?", "59,16", ["1,00", "100", "7,00"], ["Nernst eğimi."]),
        ("Toprak pH'ı genellikle hangi oranda ölçülür?", "1:2,5 toprak:su", ["1:100", "Kuru toprakta", "10:1"], ["Ders notu."]),
        ("EC metre neyi ölçer?", "Çözeltinin elektrik iletme yeteneğini", ["Oksijeni", "Bulanıklığı", "Şekeri"],
         ["Çözünmüş tuz arttıkça EC artar."]),
        ("EC sonuçları hangi sıcaklığa göre düzeltilir?", "25 °C", ["0 °C", "100 °C", "37 °C"], ["Standart referans."]),
        ("EC hücresi hangi standartla kalibre edilir?", "KCl standardı (ör. 1413 µS/cm)", ["pH 7 tamponu", "Sakaroz",
                                                                                         "Saf su"], ["Ders notu."]),
        ("Türbidimetre neyi ölçer?", "Bulanıklığı (NTU)", ["Tuzluluğu", "Şekeri", "Oksijeni"], ["90° saçılan ışık."]),
        ("Türbidimetre partiküllerin hangi açıyla saçtığı ışığı ölçer?", "90°", ["0°", "180°", "45°"], ["Ders notu."]),
        ("Çözünmüş oksijen sonucunu hangisi ETKİLEMEZ?", "Numune şişesinin rengi", ["Sıcaklık", "Tuzluluk", "Basınç"],
         ["Sıcaklık, tuzluluk ve basınç etkiler."]),
        ("Su numunesinde oksijen ve pH neden yerinde ölçülür?", "Bekledikçe değiştikleri için",
         ["Laboratuvarda ölçülemedikleri için", "Ucuz olduğu için", "Kural olmadığı için"], ["Ders notu."]),
        ("Su numunesi laboratuvara nasıl taşınır?", "Soğukta, yaklaşık 4 °C'de", ["Güneşte", "Sıcak suda", "Dondurarak"],
         ["Temiz şişe, etiket, soğuk taşıma."]),
        ("Çok parametreli ölçer için hangisi doğrudur?", "Her sensör ayrı kalibre edilir", ["Hiç kalibrasyon istemez",
                                                                                          "Bir kalibrasyon hepsine yeter",
                                                                                          "Yalnızca laboratuvarda çalışır"],
         ["pH, EC, O₂ sensörleri farklıdır."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_optik(r):
    sabit = []
    a = round(float(r.uniform(0.08, 0.15)), 4)
    b = round(float(r.uniform(0.001, 0.012)), 4)
    A = round(float(r.uniform(0.2, 1.0)), 3)
    c = (A - b) / a
    sabit.append(soru_sayi(f"Kalibrasyon doğrusu A = {_virgul(a, 4)}·c + {_virgul(b, 4)} (c: mg/L). Numunenin absorbansı "
                           f"{_virgul(A, 3)} ise derişim kaç mg/L'dir?", round(c, 2),
                           [_tx(rf"c = \frac{{{A} - {b}}}{{{a}}} = {c:.2f}\ \text{{mg/L}}")],
                           yanlis=[round(A / a, 2) if abs(A / a - c) > 0.02 else round(c * 1.3, 2), round(A * a, 3),
                                   round((A + b) / a, 2)], ondalik=2))
    sf = int(r.choice([2, 5, 10, 20, 25]))
    cs = round(float(r.uniform(1, 9)), 2)
    sabit.append(soru_sayi(f"Numune {sf} kat seyreltilip ölçülüyor; kalibrasyon eğrisinden {_virgul(cs)} mg/L bulunuyor. "
                           "Orijinal numunedeki derişim kaç mg/L'dir?", round(cs * sf, 2),
                           [_tx(rf"{cs}\times {sf} = {cs * sf:.2f}\ \text{{mg/L}}")], yanlis=[cs / sf, cs, cs + sf], ondalik=2))
    c1 = int(r.integers(2, 6))
    A1 = round(float(r.uniform(0.1, 0.3)), 2)
    k = int(r.choice([2, 3]))
    sabit.append(soru_sayi(f"Beer–Lambert yasasına uyan bir çözeltide {c1} mg/L için absorbans {_virgul(A1)}. Derişim {k} katına "
                           "çıkarsa absorbans kaç olur?", round(A1 * k, 2),
                           [_md("Absorbans derişimle doğru orantılıdır."), _tx(rf"{A1}\times {k} = {A1 * k:.2f}")],
                           yanlis=[A1, round(A1 / k, 3), round(A1 + k, 2)], ondalik=2))
    havuz = _ek(r, [
        ("Refraktometre hangi fiziksel olaya dayanır?", "Işığın kırılmasına", ["Işığın soğurulmasına", "Elektrik iletimine",
                                                                              "Radyoaktiviteye"], ["Çözünmüş madde arttıkça kırılma artar."]),
        ("1 °Brix ne anlama gelir?", "100 g çözeltide yaklaşık 1 g sakaroz eşdeğeri çözünür kuru madde",
         ["1 L suda 1 g tuz", "1 g şekerde 100 g su", "%1 alkol"], ["Ders notu."]),
        ("Refraktometrenin sıfır ayarı neyle yapılır?", "Saf su", ["Şıra", "Bal", "Tuzlu su"], ["Saf su 0 °Brix."]),
        ("Brix değeri için hangisi doğrudur?", "Şekerle birlikte asit ve diğer çözünmüş maddeleri de içerir",
         ["Yalnızca saf şekeri gösterir", "Yalnızca asitliği gösterir", "Yalnızca suyu gösterir"], ["Tahmindir."]),
        ("Refraktometrede ATC ne demektir?", "Otomatik sıcaklık düzeltmesi", ["Otomatik tartım", "Absorbans tamponu",
                                                                              "Asit titrasyonu"], ["20 °C referans."]),
        ("Beer–Lambert yasasında 'b' neyi gösterir?", "Işık yolunu (küvet kalınlığı)", ["Derişimi", "Absorbansı",
                                                                                         "Dalga boyunu"], ["Çoğunlukla 1 cm."]),
        ("Spektrofotometrede ölçümden önce cihaz neyle sıfırlanır?", "Kör (blank) çözelti", ["Numune", "En derişik standart",
                                                                                            "Musluk suyu"], ["Arka plan düzeltilir."]),
        ("UV bölgesinde ölçüm için hangi küvet kullanılır?", "Kuvars küvet", ["Cam küvet", "Plastik bardak", "Porselen kroze"],
         ["Cam ve çoğu plastik UV ışığı soğurur."]),
        ("Küvet nereden tutulur?", "Mat yüzünden", ["Şeffaf yüzünden", "İçinden", "Fark etmez"], ["Parmak izi ışığı engeller."]),
        ("Monokromatörün görevi nedir?", "Tek bir dalga boyunu seçmek", ["Numuneyi ısıtmak", "Işığı söndürmek", "Tartım yapmak"],
         ["Prizma ya da ızgara."]),
        ("Numunenin absorbansı en yüksek standarttan büyükse ne yapılır?", "Numune seyreltilip yeniden okunur",
         ["Doğru uzatılarak tahmin edilir", "Sonuç en yüksek standart yazılır", "Numune atılır"], ["Eğrinin dışında tahmin edilmez."]),
        ("Kalibrasyon eğrisinde çoğu laboratuvarın istediği R² değeri nedir?", "0,99 ve üstü", ["0,5", "0,8", "0,1"], ["Ders notu."]),
        ("Kalibrasyon eğrisi için kaç standart önerilir?", "5–6", ["1", "2", "50"], ["Kör + 5–6 standart."]),
        ("Hangisi spektrofotometreyle ölçülen analizlerden DEĞİLDİR?", "Brix", ["Nitrat", "Fosfor", "Toplam fenol"],
         ["Brix refraktometreyle ölçülür."]),
        ("Absorbans 1 ise numuneden geçen ışık yüzde kaçtır?", "%10", ["%1", "%50", "%90"], ["A = −log T → T = 10⁻¹."]),
        ("Absorbans 2 ise numuneden geçen ışık yüzde kaçtır?", "%1", ["%10", "%50", "%20"], ["T = 10⁻² = 0,01."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_ileri(r):
    sabit = []
    v = round(float(r.uniform(3, 20)), 2)
    vb = round(float(r.choice([0.05, 0.10, 0.15, 0.20])), 2)
    M = float(r.choice([0.05, 0.1, 0.2]))
    m = round(float(r.uniform(0.3, 1.2)), 4)
    N = (v - vb) * M * 1.4007 / m
    sabit.append(soru_sayi(f"Kjeldahl analizinde {_virgul(m, 4)} g numune için {_virgul(v)} mL, kör için {_virgul(vb)} mL "
                           f"{_virgul(M, 2)} M HCl harcanıyor. Azot yüzdesi kaçtır?", round(N, 2),
                           [_tx(rf"N = \frac{{({v} - {vb})\times {M}\times 1{{,}}4007}}{{{m}}} = {N:.2f}\,\%")],
                           yanlis=[round(v * M * 1.4007 / m, 2) if abs(vb) > 0 else round(N * 1.2, 2),
                                   round((v - vb) * M * 14.007 / m, 2), round(N * 6.25, 2)], ondalik=2))
    n2 = round(float(r.uniform(0.4, 3.5)), 2)
    urun, F = [("süt", 6.38), ("buğday", 5.7), ("genel bir gıda", 6.25)][int(r.integers(0, 3))]
    sabit.append(soru_sayi(f"Azot içeriği %{_virgul(n2)} olan {urun} örneğinin protein içeriği yüzde kaçtır? "
                           f"(Faktör {_virgul(F, 2)})", round(n2 * F, 2), [_tx(rf"{n2}\times {F} = {n2 * F:.2f}\,\%")],
                           yanlis=[round(n2 / F, 2), round(n2 * 6.25, 2) if F != 6.25 else round(n2 * 6.38, 2), round(n2 + F, 2)],
                           ondalik=2))
    havuz = _ek(r, [
        ("AAS hangi prensibe dayanır?", "Atomların kendine özgü dalga boyunda ışığı soğurmasına",
         ["Atomların ışık yaymasına", "Işığın kırılmasına", "Elektrik iletimine"], ["Atomik absorpsiyon."]),
        ("ICP-OES hangi prensibe dayanır?", "Plazmada uyarılan atomların ışık yaymasına",
         ["Atomların ışığı soğurmasına", "Kütle ölçümüne", "Kırılma indisine"], ["Optik emisyon."]),
        ("Aynı anda çok sayıda elementi hızla ölçen cihaz hangisidir?", "ICP-OES", ["AAS", "pH metre", "Refraktometre"],
         ["AAS çoğunlukla tek tek ölçer."]),
        ("AAS'de her element için ne gerekir?", "Ayrı bir oyuk katot lambası", ["Ayrı bir terazi", "Ayrı bir etüv", "Hiçbir şey"],
         ["Elemente özgü ışık kaynağı."]),
        ("ICP-OES'in işletme giderini artıran gaz hangisidir?", "Argon", ["Oksijen", "Azot", "Karbondioksit"], ["Plazma gazı."]),
        ("Katı numunenin kül fırınında yakılarak çözeltiye hazırlanmasına ne denir?", "Kuru yakma",
         ["Yaş yakma", "Titrasyon", "Kromatografi"], ["Yaş yakma asitle yapılır."]),
        ("Kjeldahl yönteminin doğru sırası hangisidir?", "Yakma → damıtma → titrasyon",
         ["Titrasyon → yakma → damıtma", "Damıtma → yakma → titrasyon", "Kurutma → kül → tartım"], ["Ders notu."]),
        ("Kjeldahl yakma aşamasında organik azot neye dönüşür?", "Amonyuma", ["Nitrata", "Azot gazına", "Üreye"],
         ["Derişik H₂SO₄ + katalizör."]),
        ("Kjeldahl damıtmasında açığa çıkan amonyak nerede tutulur?", "Borik asitte", ["Sülfürik asitte", "Saf suda",
                                                                                        "Havada"], ["Sonra titre edilir."]),
        ("Genel protein faktörü kaçtır?", "6,25", ["6,38", "5,70", "1,00"], ["Proteinler ortalama %16 azot içerir: 100/16."]),
        ("Sütte kullanılan protein faktörü kaçtır?", "6,38", ["6,25", "5,70", "4,00"], ["Ders notu."]),
        ("Soxhlet düzeneği hangi analiz için kullanılır?", "Yağ tayini", ["Protein tayini", "Kül tayini", "pH ölçümü"],
         ["Çözücüyle ekstraksiyon."]),
        ("Soxhlet'te çalışırken neden açık alev kullanılmaz?", "Çözücüler (eter, hekzan) çok yanıcıdır",
         ["Yağ donar", "Su kaynar", "Cam erir"], ["Çeker ocak şart."]),
        ("Gıdada kül tayini genellikle kaç derecede yapılır?", "525–550 °C", ["105 °C", "65–70 °C", "37 °C"], ["Ders notu."]),
        ("Uçucu olmayan şeker, organik asit ve antosiyaninler hangi cihazla ayrılır?", "HPLC", ["GC", "AAS", "Refraktometre"],
         ["Sıvı kromatografi."]),
        ("Aroma, uçucu yağ ve pestisit kalıntısı hangi cihazla analiz edilir?", "GC (gaz kromatografi)",
         ["HPLC", "pH metre", "SPAD"], ["Uçucu bileşikler."]),
        ("GC-MS'de bileşik neye göre tanımlanır?", "Kütle spektrumuna", ["Rengine", "Kokusuna", "pH'ına"], ["MS: kütle spektrometresi."]),
        ("Kromatogramda tepenin çıktığı süreye ne denir?", "Alıkonma süresi", ["Absorbans", "Kırılma indisi", "Dara"],
         ["Bileşeni tanıtır; tepe alanı miktarı gösterir."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_lablar(r):
    sabit = []
    ozet = [("Kütle", "Terazi"), ("Tuzluluk", "EC metre"), ("Çözünür kuru madde", "Refraktometre"),
            ("Mineral elementler", "AAS / ICP-OES"), ("Azot ve protein", "Kjeldahl"), ("Bulanıklık", "Türbidimetre"),
            ("Tahribatsız klorofil", "SPAD metre"), ("Toprakta kireç", "Scheibler kalsimetresi"),
            ("Toprak tekstürü", "Bouyoucos hidrometresi"), ("Toprakta organik madde", "Walkley-Black yöntemi"),
            ("Su aktivitesi", "aw ölçer"), ("Renk", "Kolorimetre (L*a*b*)"), ("Kıvam", "Viskozimetre")]
    i = int(r.integers(0, len(ozet)))
    diger = [o[1] for j, o in enumerate(ozet) if j != i]
    sabit.append(_secim(r, f"“{ozet[i][0]}” hangi cihaz ya da yöntemle ölçülür?", ozet[i][1],
                        [diger[int(k)] for k in r.permutation(len(diger))[:3]], [f"{ozet[i][0]} → {ozet[i][1]}"]))
    aw = round(float(r.uniform(0.55, 0.99)), 2)
    if aw >= 0.91:
        d = "Çoğu bakteri, maya ve küf üreyebilir"
    elif aw >= 0.80:
        d = "Çoğu bakteri üreyemez; maya ve küfler üreyebilir"
    elif aw >= 0.61:
        d = "Yalnızca kurakçıl (kserofilik) küfler gibi dayanıklı türler üreyebilir"
    else:
        d = "Mikroorganizmaların hemen hiçbiri üreyemez"
    secenek = ["Çoğu bakteri, maya ve küf üreyebilir", "Çoğu bakteri üreyemez; maya ve küfler üreyebilir",
               "Yalnızca kurakçıl (kserofilik) küfler gibi dayanıklı türler üreyebilir",
               "Mikroorganizmaların hemen hiçbiri üreyemez"]
    sabit.append(_secim(r, f"Su aktivitesi {_virgul(aw)} olan bir gıda için hangisi doğrudur?", d,
                        [s for s in secenek if s != d],
                        ["Yaklaşık alt sınırlar: bakteri 0,91 · maya 0,88 · küf 0,80 · kserofilik küf 0,61."]))
    havuz = _ek(r, [
        ("Toprak analizden önce nasıl hazırlanır?", "Havada kurutulur, ezilir, 2 mm elekten geçirilir",
         ["105 °C'de yakılır", "Suyla yıkanır", "Dondurulur"], ["Ders notu."]),
        ("Toprakta kireç tayini hangi cihazla yapılır?", "Scheibler kalsimetresi", ["Refraktometre", "Türbidimetre", "SPAD"],
         ["Asitle açığa çıkan CO₂ hacmi ölçülür."]),
        ("Toprak tekstürü (kum, silt, kil) nasıl belirlenir?", "Bouyoucos hidrometresiyle", ["pH metreyle", "Kjeldahl ile",
                                                                                            "Soxhlet ile"], ["Ders notu."]),
        ("Kireçli topraklarda yarayışlı fosfor hangi yöntemle belirlenir?", "Olsen (spektrofotometre)",
         ["Walkley-Black", "Scheibler", "Bouyoucos"], ["Ders notu."]),
        ("Toprakta organik madde hangi yöntemle belirlenir?", "Walkley-Black (dikromatla yaş yakma)",
         ["Olsen", "Bouyoucos", "Kjeldahl"], ["Titrasyonla."]),
        ("Toprak tuzluluğu genellikle hangi ekstraktta ölçülür?", "Saturasyon çamuru ekstraktı", ["Kuru toprakta", "Alkolde",
                                                                                                  "Yağda"], ["dS/m."]),
        ("Yaprak örnekleri hangi sıcaklıkta kurutulur?", "65–70 °C", ["105 °C", "550 °C", "20 °C"], ["Ders notu."]),
        ("Yaprak analizinde adımların doğru sırası hangisidir?", "Örnekleme → yıkama → kurutma → öğütme → analiz",
         ["Öğütme → yıkama → örnekleme → analiz", "Kurutma → örnekleme → yıkama → analiz", "Analiz → kurutma → yıkama"],
         ["Ders notu."]),
        ("SPAD metre hangi ışıkları kullanır?", "Kırmızı (650 nm) ve yakın kızılötesi (940 nm)",
         ["Mavi ve yeşil", "UV ve X ışını", "Yalnızca beyaz ışık"], ["Geçen ışıklar karşılaştırılır."]),
        ("SPAD değeri için hangisi doğrudur?", "Birimsizdir, göreceli bir değerdir", ["mg/L'dir", "°Brix'tir", "Kesin klorofil miktarıdır"],
         ["Kalibre edilmeden mg klorofile çevrilmez."]),
        ("Nem ile su aktivitesi arasındaki fark nedir?", "Nem toplam suyu, aw serbest (kullanılabilir) suyu gösterir",
         ["İkisi aynıdır", "aw toplam suyu gösterir", "Nem yalnızca buharı gösterir"], ["Raf ömrünü aw belirler."]),
        ("Nemi aynı iki gıdanın raf ömrü neden farklı olabilir?", "Su aktiviteleri farklı olabilir",
         ["Renkleri farklıdır", "Ambalaj rengi farklıdır", "Raf ömrü nemle belirlenmez, rastgeledir"],
         ["Bağlı su mikroorganizmaya kullanılamaz."]),
        ("CIE L*a*b* sisteminde L* neyi gösterir?", "Açıklığı (0 siyah – 100 beyaz)", ["Kırmızılığı", "Sarılığı", "Kıvamı"],
         ["a*: yeşil–kırmızı, b*: mavi–sarı."]),
        ("a* değeri pozitif (+) ise renk hangi yöne kayar?", "Kırmızıya", ["Yeşile", "Maviye", "Siyaha"], ["a*: − yeşil, + kırmızı."]),
        ("b* değeri pozitif (+) ise renk hangi yöne kayar?", "Sarıya", ["Maviye", "Yeşile", "Beyaza"], ["b*: − mavi, + sarı."]),
        ("Viskozimetre ölçümünde en önemli koşul nedir?", "Sabit sıcaklık", ["Karanlık oda", "Yüksek basınç", "Mıknatıs"],
         ["Kıvam sıcaklığa çok bağlıdır."]),
        ("Terazi, pH metre ve spektrofotometre hangi laboratuvarlarda kullanılır?", "Gıda, toprak, yaprak ve su laboratuvarlarının hepsinde",
         ["Yalnızca gıda", "Yalnızca toprak", "Hiçbirinde"], ["Ortak cihazlar."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_numune(r):
    sabit = []
    V = int(r.choice([150, 250, 300, 380, 400, 450, 600, 1000, 2500, 5000]))
    dk = 5 if V <= 400 else 10
    sabit.append(soru_sayi(f"Kapasitesi {V} L olan soğutulmuş süt tankından örnek alınmadan önce en az kaç dakika "
                           "karıştırılmalıdır?", dk, [_md(f"{V} L {'≤' if V <= 400 else '>'} 400 L → en az {dk} dk.")],
                           yanlis=[10 if dk == 5 else 5, 1, 30]))
    ml = int(r.choice([200, 400, 600, 1000]))
    sabit.append(soru_sayi(f"{ml} mL süte koruyucu olarak (notlardaki orana göre) kaç g potasyum dikromat eklenir?",
                           ml / 200 * 0.1, [_tx(rf"\frac{{0{{,}}1\ \text{{g}}}}{{200\ \text{{mL}}}}\times {ml} = {ml / 2000:g}\ \text{{g}}")],
                           yanlis=[0.1, ml / 200, ml / 100 * 0.1 * 4], ondalik=2))
    havuz = _ek(r, [
        ("Ders notunda numune almanın yasal dayanağı olarak hangi mevzuat gösterilmiştir?", "Türk Gıda Kodeksi Yönetmeliği",
         ["Trafik Kanunu", "Tapu Yönetmeliği", "Belediye Kanunu"], ["“Numune Alma ve Analiz Metodları” bölümü."]),
        ("Süt için 'parti' nedir?", "Aynı tür hayvandan sağılan ve bir defada satışa sunulan süt",
         ["Bir günde sağılan bütün sütler", "Bir şişe süt", "Farklı türlerden karışık süt"], ["Ders notu."]),
        ("Bir partiden kaç örnek alınır?", "Çift (2)", ["1", "10", "Hiç"], ["Biri yedek / şahit örnektir."]),
        ("Kimyasal analiz için genellikle ne kadar örnek alınır?", "200 mL", ["2 mL", "20 L", "5 mL"], ["Ders notu."]),
        ("Örnek laboratuvara en geç ne zaman ulaştırılmalıdır?", "24 saat içinde", ["1 hafta içinde", "1 ay içinde",
                                                                                   "Fark etmez"], ["0–5 °C'de."]),
        ("Örnek hangi sıcaklıkta taşınır?", "0–5 °C", ["20–25 °C", "37 °C", "55 °C"], ["Soğuk zincir."]),
        ("Etikette hangisi bulunmak ZORUNDA DEĞİLDİR?", "Analizi yapacak kişinin adı",
         ["Örnek sahibinin adı-soyadı", "Alınış tarihi", "Sıcaklık derecesi"], ["Etiket: sahip, tür, yer, tarih, sıcaklık."]),
        ("Potasyum dikromat eklenmiş sütte hangi analiz YAPILAMAZ?", "Mikrobiyolojik analiz",
         ["Hiçbiri; hepsi yapılabilir", "Yalnızca renk ölçümü yapılamaz", "Yalnızca ambalaj kontrolü yapılamaz"],
         ["Duyusal, mikrobiyolojik, özgül ağırlık, kuru madde ve kül yapılamaz."]),
        ("Potasyum dikromat neden dikkatle kullanılmalıdır?", "Altı değerlikli krom içerir; kanserojen ve zehirlidir",
         ["Çok pahalıdır", "Sütü tatlandırır", "Rengi yoktur"], ["Eldiven, tehlikeli atık."]),
        ("Bakteriyolojik analiz için örnek nasıl alınır?", "Steril şişeye, aseptik koşullarda",
         ["Herhangi bir şişeye", "Açık kovaya", "Kullanılmış kaba"], ["Bulaşma önlenir."]),
        ("Süt neden örnek alınmadan önce iyice karıştırılır?", "Polidispers olduğu için; yağ ayrılır, homojen değildir",
         ["Soğusun diye", "Köpürsün diye", "Rengi açılsın diye"], ["Temsil eden örnek için."]),
        ("Tek kaptaki süt nasıl homojen hâle getirilir?", "5–6 kez başka kaba aktarılarak ya da 30 sn karıştırılarak",
         ["Hiç karıştırılmadan", "Kaynatılarak", "Dondurularak"], ["Ders notu."]),
        ("Süt birkaç kaptaysa ne yapılır?", "Her kaptan aynı miktarda alınıp birleştirilir",
         ["Yalnızca ilk kaptan alınır", "En dolu kaptan alınır", "Rastgele bir kaptan alınır"], ["Temsil eden örnek."]),
        ("Kaymak tabakası kuvvetli ya da donmuş süt nasıl hazırlanır?", "En çok 55 °C'lik su banyosunda çözülür, sonra karıştırılır",
         ["Kaynatılır", "Mikrodalgada ısıtılır", "Kaymak atılır"], ["Ardından en az 1 dk karıştırma ya da 10 kez aktarma."]),
        ("Karıştırma sırasında köpük oluşursa ne yapılır?", "Köpük sönene kadar beklenip hafifçe karıştırılarak alınır",
         ["Köpük örneğe katılır", "Su eklenir", "Örnek atılır"], ["Ders notu."]),
        ("Analiz öncesi şişede kaymak kalıntısı varsa süt kaç dereceye ısıtılır?", "38 °C", ["55 °C", "100 °C", "4 °C"],
         ["Su banyosunda, sonra çalkalanır."]),
        ("Örnek kabı için hangisi doğrudur?", "Koku vermeyen, numuneyi etkilemeyen, kolay temizlenen malzeme",
         ["Kokulu plastik", "Paslı metal", "Kâğıt bardak"], ["Cam, paslanmaz çelik, kokusuz plastik."]),
        ("Örnek alma kabı nasıl doldurulur?", "Ne tam dolu ne çok az", ["Ağzına kadar", "Yarıdan az", "Taşırarak"], ["Ders notu."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_kalite(r):
    sabit = []
    for _ in range(3):
        i = int(r.integers(0, len(TERIMLER)))
        t, d = TERIMLER[i]
        diger = [x[0] for j, x in enumerate(TERIMLER) if j != i]
        sabit.append(_secim(r, f"“{d}” Bu tanım hangi terime aittir?", t,
                            [diger[int(k)] for k in r.permutation(len(diger))[:3]], [f"**{t}:** {d}"]))
    havuz = _ek(r, [
        ("Deney ve kalibrasyon laboratuvarlarının yeterlilik standardı hangisidir?", "ISO/IEC 17025",
         ["ISO 9001", "ISO 14001", "ISO 22000"], ["Laboratuvar yeterliliği."]),
        ("Türkiye'de laboratuvarlara akreditasyon veren kurum hangisidir?", "TÜRKAK", ["TÜBİTAK UME", "TSE", "YÖK"],
         ["Türk Akreditasyon Kurumu."]),
        ("Cihaz kartında hangisi bulunur?", "Marka, seri no, kalibrasyon tarihi", ["Kullanıcının adresi", "Fiyat etiketi",
                                                                                   "Cihazın rengi"], ["Kayıt."]),
        ("Ham veri ne yapılır?", "Sonuçla birlikte saklanır", ["Hemen silinir", "Yalnızca sonuç saklanır",
                                                               "Çöpe atılır"], ["İzlenebilirlik için."]),
        ("Laboratuvarın 'altın kuralı' hangisidir?", "Kalibre et, kontrol et, kaydet; sonra ölç",
         ["Hızlı ölç, sonra düşün", "Kayıt tutma", "Kalibrasyonu yılda bir düşün"], ["Sonuç, cihaz–yöntem–kayıt kadar güvenilirdir."]),
        ("Atıklar nasıl toplanır?", "Türüne göre ayrı ve etiketli kaplarda", ["Hepsi lavaboya", "Hepsi tek kovada",
                                                                              "Normal çöpe"], ["Atık toplama odası."]),
        ("Islak zemin ve elektrik kablosu için hangisi doğrudur?", "Birlikte ciddi elektrik çarpma riski oluşturur",
         ["Tehlikesizdir", "Cihazları korur", "Kalibrasyonu iyileştirir"], ["Güvenlik."]),
        ("Kullanım ve bakım defteri neden tutulur?", "Cihazın geçmişi ve güvenilirliği izlensin diye",
         ["Süs olsun diye", "Cihaz ağırlaşsın diye", "Zorunlu değildir"], ["Kayıt."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_tekrar(r):
    ureticiler = [gen_guvenlik, gen_isaret, gen_kimyasal, gen_metrik, gen_metrik, gen_cam, gen_okuma, gen_olcum, gen_terazi, gen_elektro, gen_optik,
                  gen_ileri, gen_lablar, gen_numune, gen_kalite]
    secilen = [ureticiler[int(i)] for i in r.permutation(len(ureticiler))[:SORU_SAYISI]]
    return [u(r)[0] for u in secilen]


# ---------------------------------------------------------------------------
# Metrik sistem soruları (sayılar her seferinde değişir)
# ---------------------------------------------------------------------------
_SIK_ONEK = {"g": ["k", "", "m", "µ", "n"], "L": ["", "d", "m", "µ"], "m": ["k", "", "c", "m", "µ", "n"]}


def _deger_sec(r):
    return float(r.choice([0.002, 0.025, 0.05, 0.2, 0.25, 0.5, 1.5, 2, 2.5, 3.2, 4, 7.5, 12, 25, 40, 75, 125, 250, 500, 750,
                           1200, 2500, 4000]))


_CIFTLER = {"g": [("k", ""), ("", "m"), ("m", "µ"), ("µ", "n"), ("k", "m"), ("", "µ")],
            "L": [("", "m"), ("m", "µ"), ("", "µ"), ("d", "m"), ("", "d")],
            "m": [("k", ""), ("", "c"), ("c", "m"), ("", "m"), ("m", "µ"), ("µ", "n"), ("", "n")]}


def _birim_sorusu(r):
    temel = str(r.choice(list(_CIFTLER)))
    b1, b2 = _CIFTLER[temel][int(r.integers(0, len(_CIFTLER[temel])))]
    if r.random() < 0.5:
        b1, b2 = b2, b1
    v = _deger_sec(r)
    f = ONEK_US[b1] - ONEK_US[b2]
    dogru = v * 10 ** f
    yanlis = [v * 10 ** -f, v * 10 ** (f + 3), v * 10 ** (f - 3), v * 10 ** (f + 1), v * 10 ** (f - 1)]
    d = f"{_sayi_tr(dogru)} {b2}{temel}"
    ys = []
    for y in yanlis:
        t = f"{_sayi_tr(y)} {b2}{temel}"
        if t != d and t not in ys:
            ys.append(t)
    yon = ("küçük birime iniliyor, " + f"{10 ** f:,}".replace(",", ".") + " ile çarpılır") if f > 0 else \
          ("büyük birime çıkılıyor, " + f"{10 ** -f:,}".replace(",", ".") + " ile bölünür")
    return _secim(r, f"{_sayi_tr(v)} {b1}{temel} kaç {b2}{temel} eder?", d, [ys[int(i)] for i in r.permutation(len(ys))[:3]],
                  [f"{b1 or '(temel)'}{temel} → {b2 or '(temel)'}{temel}: {yon}.",
                   f"{_sayi_tr(v)} {b1}{temel} {'×' if f > 0 else '÷'} {10 ** abs(f):,} = **{d}**".replace(",", ".")])


def _onek_sorusu(r):
    secenek = [o for o in ONEKLER if o[0]]
    i = int(r.integers(0, len(secenek)))
    ad, sem, us = secenek[i]
    tur = int(r.integers(0, 3))
    if tur == 0:
        diger = [f"10{_ust(o[2])}" for o in secenek if o[2] != us]
        return _secim(r, f"“{ad}” ön eki hangi çarpanı gösterir?", f"10{_ust(us)}",
                      [diger[int(k)] for k in r.permutation(len(diger))[:3]],
                      [f"{ad} ({sem}) = 10{_ust(us)}"])
    if tur == 1:
        diger = [o[1] for o in secenek if o[1] != sem]
        return _secim(r, f"“{ad}” ön ekinin sembolü hangisidir?", sem, [diger[int(k)] for k in r.permutation(len(diger))[:3]],
                      [f"{ad} → {sem}. Büyük-küçük harf önemlidir: m (mili) ile M (mega) farklıdır."])
    diger = [o[0] for o in secenek if o[0] != ad]
    return _secim(r, f"10{_ust(us)} çarpanını gösteren ön ek hangisidir?", ad, [diger[int(k)] for k in r.permutation(len(diger))[:3]],
                  [f"10{_ust(us)} = {ad} ({sem})"])


def _ppm_sorusu(r):
    tur = int(r.integers(0, 8))
    if tur == 0:
        p = float(r.choice([0.1, 0.5, 1, 2, 5, 12, 0.02]))
        return _secim(r, f"%{_sayi_tr(p)} kaç ppm eder?", f"{_sayi_tr(p * 10000)} ppm",
                      [f"{_sayi_tr(p * 100)} ppm", f"{_sayi_tr(p * 1000)} ppm", f"{_sayi_tr(p * 1e6)} ppm"],
                      ["1 % = 10 000 ppm", _tx(rf"{_sayi_tr(p)} \times 10\,000 = {_sayi_tr(p * 10000)}")])
    if tur == 1:
        p = float(r.choice([50, 200, 500, 2500, 10000, 25000]))
        return _secim(r, f"{_sayi_tr(p)} ppm yüzde kaçtır?", f"%{_sayi_tr(p / 10000)}",
                      [f"%{_sayi_tr(p / 100)}", f"%{_sayi_tr(p / 1000)}", f"%{_sayi_tr(p / 1e6)}"],
                      ["1 % = 10 000 ppm → ppm ÷ 10 000", _tx(rf"{_sayi_tr(p)} \div 10\,000 = {_sayi_tr(p / 10000)}")])
    if tur == 2:
        p = float(r.choice([0.005, 0.01, 0.05, 0.2, 1.5, 3]))
        return _secim(r, f"{_sayi_tr(p)} ppm kaç ppb eder?", f"{_sayi_tr(p * 1000)} ppb",
                      [f"{_sayi_tr(p / 1000)} ppb", f"{_sayi_tr(p * 100)} ppb", f"{_sayi_tr(p * 1e6)} ppb"],
                      ["1 ppm = 1000 ppb → çarpılır."])
    if tur == 3:
        p = float(r.choice([5, 10, 50, 120, 750, 2500]))
        return _secim(r, f"{_sayi_tr(p)} ppb kaç ppm eder?", f"{_sayi_tr(p / 1000)} ppm",
                      [f"{_sayi_tr(p * 1000)} ppm", f"{_sayi_tr(p / 100)} ppm", f"{_sayi_tr(p / 1e6)} ppm"],
                      ["1 ppm = 1000 ppb → ppb ÷ 1000."])
    if tur == 4:
        mg = float(r.choice([2, 5, 8, 12.5, 25, 40, 150]))
        L = float(r.choice([0.25, 0.5, 2, 4, 5]))
        return _secim(r, f"{_sayi_tr(mg)} mg madde suda çözülüp hacim {_sayi_tr(L)} L'ye tamamlanıyor. Derişim kaç ppm'dir?",
                      f"{_sayi_tr(mg / L)} ppm", [f"{_sayi_tr(mg * L)} ppm", f"{_sayi_tr(mg / L * 1000)} ppm",
                                                  f"{_sayi_tr(L / mg)} ppm"],
                      ["ppm = mg/L", _tx(rf"\frac{{{_sayi_tr(mg)}}}{{{_sayi_tr(L)}}} = {_sayi_tr(mg / L)}")])
    if tur == 5:
        ug = float(r.choice([3, 8, 15, 40, 120]))
        return _secim(r, f"Bir su örneğinde kurşun {_sayi_tr(ug)} µg/L bulunmuştur. Bu kaç ppb'dir?", f"{_sayi_tr(ug)} ppb",
                      [f"{_sayi_tr(ug * 1000)} ppb", f"{_sayi_tr(ug / 1000)} ppb", f"{_sayi_tr(ug / 1e6)} ppb"],
                      ["Seyreltik sulu çözeltide 1 ppb = 1 µg/L."])
    if tur == 6:
        mgkg = float(r.choice([2, 15, 45, 120, 380]))
        return _secim(r, f"Bir yaprak örneğinde çinko {_sayi_tr(mgkg)} mg/kg bulunmuştur. Bu kaç ppm'dir?", f"{_sayi_tr(mgkg)} ppm",
                      [f"{_sayi_tr(mgkg * 1000)} ppm", f"{_sayi_tr(mgkg / 1000)} ppm", f"{_sayi_tr(mgkg / 10)} ppm"],
                      ["1 ppm = 1 mg/kg (katı numunede)."])
    p = float(r.choice([2, 5, 10, 20, 50]))
    return _secim(r, f"{_sayi_tr(p)} ppm'lik 1 L çözeltide kaç mg madde vardır?", f"{_sayi_tr(p)} mg",
                  [f"{_sayi_tr(p * 1000)} mg", f"{_sayi_tr(p / 1000)} mg", f"{_sayi_tr(p * 10)} mg"],
                  ["1 ppm = 1 mg/L → 1 L'de p mg."])


def _seyreltme_sorusu(r):
    C1 = float(r.choice([100, 500, 1000, 2000]))
    C2 = float(r.choice([1, 2, 5, 10, 20, 25, 50]))
    V2 = float(r.choice([50, 100, 250, 500, 1000]))
    V1 = C2 * V2 / C1
    return _secim(r, f"{_sayi_tr(C1)} ppm'lik stoktan {_sayi_tr(C2)} ppm'lik {_sayi_tr(V2)} mL çözelti hazırlamak için "
                     "stoktan kaç mL alınır?", f"{_sayi_tr(V1)} mL",
                  [f"{_sayi_tr(C1 * V2 / C2)} mL", f"{_sayi_tr(V1 * 10)} mL", f"{_sayi_tr(V1 / 10)} mL"],
                  ["C₁·V₁ = C₂·V₂", _tx(rf"V_1 = \frac{{{_sayi_tr(C2)} \times {_sayi_tr(V2)}}}{{{_sayi_tr(C1)}}} = {_sayi_tr(V1)}\ \mathrm{{mL}}")])


def _cesitli_sorusu(r):
    tur = int(r.integers(0, 7))
    if tur == 0:
        c = int(r.choice([-20, 0, 4, 20, 25, 37, 105, 550]))
        return _secim(r, f"{c} °C kaç kelvindir?", f"{_sayi_tr(c + 273.15)} K",
                      [f"{_sayi_tr(c - 273.15)} K", f"{_sayi_tr(c + 100)} K", f"{_sayi_tr(c * 273.15)} K"],
                      ["K = °C + 273,15"])
    if tur == 1:
        ul = int(r.choice([5, 10, 50, 100, 200, 250, 500, 750]))
        return _secim(r, f"Mikropipet {ul} µL'ye ayarlanmıştır. Bu kaç mL'dir?", f"{_sayi_tr(ul / 1000)} mL",
                      [f"{_sayi_tr(ul * 1000)} mL", f"{_sayi_tr(ul / 100)} mL", f"{_sayi_tr(ul / 10)} mL"],
                      ["1 mL = 1000 µL → µL ÷ 1000"])
    if tur == 2:
        ml = float(r.choice([0.02, 0.05, 0.1, 0.25, 0.5, 1.5]))
        return _secim(r, f"{_sayi_tr(ml)} mL'yi mikropipete kaç µL olarak ayarlarsınız?", f"{_sayi_tr(ml * 1000)} µL",
                      [f"{_sayi_tr(ml * 100)} µL", f"{_sayi_tr(ml / 1000)} µL", f"{_sayi_tr(ml * 1e6)} µL"],
                      ["mL × 1000 = µL"])
    if tur == 3:
        cm3 = float(r.choice([1, 5, 25, 250, 1000]))
        return _secim(r, f"{_sayi_tr(cm3)} cm³ kaç mL'dir?", f"{_sayi_tr(cm3)} mL",
                      [f"{_sayi_tr(cm3 * 1000)} mL", f"{_sayi_tr(cm3 / 1000)} mL", f"{_sayi_tr(cm3 * 10)} mL"],
                      ["1 cm³ = 1 mL"])
    if tur == 4:
        yuzde = float(r.choice([0.5, 1, 2, 5, 10]))
        V = float(r.choice([100, 250, 500, 1000]))
        return _secim(r, f"%{_sayi_tr(yuzde)} (w/v) NaCl çözeltisinden {_sayi_tr(V)} mL hazırlamak için kaç g NaCl tartılır?",
                      f"{_sayi_tr(yuzde * V / 100)} g", [f"{_sayi_tr(yuzde * V)} g", f"{_sayi_tr(yuzde * V / 1000)} g",
                                                          f"{_sayi_tr(yuzde)} g"],
                      ["% (w/v) = 100 mL'deki gram", _tx(rf"\frac{{{_sayi_tr(yuzde)}}}{{100}}\times {_sayi_tr(V)} = {_sayi_tr(yuzde * V / 100)}\ \mathrm{{g}}")])
    if tur == 5:
        nm = int(r.choice([420, 540, 650, 880]))
        return _secim(r, f"Spektrofotometrede dalga boyu {nm} nm. Bu kaç metredir?", f"{_sayi_tr(nm * 1e-9)} m",
                      [f"{_sayi_tr(nm * 1e-6)} m", f"{_sayi_tr(nm * 1e-3)} m", f"{_sayi_tr(nm * 1e-12)} m"],
                      ["1 nm = 10⁻⁹ m"])
    # en büyük / en küçük
    temel = "g"
    adaylar = [(0.5, "g"), (450, "mg"), (2000, "µg"), (0.0004, "kg")]
    idx = r.permutation(4)
    degerler = [adaylar[int(i)] for i in idx]
    gram = [v * 10 ** ONEK_US[b[:-1]] for v, b in degerler]
    en = degerler[int(np.argmax(gram))]
    return _secim(r, "Aşağıdakilerden hangisi EN BÜYÜK kütledir?", f"{_sayi_tr(en[0])} {en[1]}",
                  [f"{_sayi_tr(v)} {b}" for v, b in degerler if (v, b) != en],
                  ["Hepsini grama çevir: " + ", ".join(f"{_sayi_tr(v)} {b} = {_sayi_tr(g_)} g" for (v, b), g_ in zip(degerler, gram))])


def gen_metrik(r):
    sabit = [_birim_sorusu(r) for _ in range(4)] + [_onek_sorusu(r), _onek_sorusu(r), _ppm_sorusu(r), _ppm_sorusu(r),
                                                     _seyreltme_sorusu(r), _cesitli_sorusu(r)]
    gorulen, sonuc = set(), []
    for s in sabit:
        if s["metin"] not in gorulen:
            gorulen.add(s["metin"])
            sonuc.append(s)
    return [sonuc[int(i)] for i in r.permutation(len(sonuc))]


# ---------------------------------------------------------------------------
def gen_isaret(r):
    sabit = []
    grup = list(ISARETLER)[int(r.integers(0, len(ISARETLER)))]
    anlam = {"Uyarı (tehlike)": "Uyarı: tehlike var", "Zorunluluk (emir)": "Zorunluluk: bunu yapmak zorundasın",
             "Yasak": "Yasak: bunu yapma", "Acil durum / ilk yardım": "Acil durum / ilk yardım donanımı",
             "Yangın ekipmanı": "Yangınla mücadele donanımı"}
    sabit.append(_secim(r, f"{ISARETLER[grup][0].capitalize()} biçimindeki işaret ne anlama gelir?", anlam[grup],
                        [v for k, v in anlam.items() if k != grup], [f"{ISARETLER[grup][0]} → {anlam[grup]}"]))
    ad, _ = ISARETLER[grup][1][int(r.integers(0, len(ISARETLER[grup][1])))]
    sekil = {"Uyarı (tehlike)": "Sarı üçgen", "Zorunluluk (emir)": "Mavi daire", "Yasak": "Kırmızı çerçeveli, çapraz çizgili daire",
             "Acil durum / ilk yardım": "Yeşil kare", "Yangın ekipmanı": "Kırmızı kare"}
    sabit.append(_secim(r, f"“{ad}” işareti hangi şekil ve renktedir?", sekil[grup],
                        [v for k, v in sekil.items() if k != grup], [f"{ad}: {grup.lower()} işaretidir."]))
    n = int(r.integers(0, 5))
    renk, ad2 = [("mavi", "sağlık"), ("kırmızı", "yanıcılık"), ("sarı", "reaktiflik (kararsızlık)")][int(r.integers(0, 3))]
    anl = {0: "Tehlike yok", 1: "Hafif tehlike", 2: "Orta tehlike", 3: "Ciddi tehlike", 4: "Çok ciddi / ölümcül tehlike"}
    sabit.append(_secim(r, f"NFPA elmasının {renk} bölümünde {n} yazıyor. Bu ne anlama gelir?", f"{ad2.capitalize()}: {anl[n].lower()}",
                        [f"{ad2.capitalize()}: {anl[int(k)].lower()}" for k in r.permutation(5) if int(k) != n],
                        ["NFPA'da 0 tehlike yok, 4 en yüksek tehlikedir.", f"Mavi: sağlık · kırmızı: yanıcılık · sarı: reaktiflik"]))
    g = GHS[int(r.integers(0, len(GHS)))]
    sabit.append(_secim(r, f"Kimyasal şişesinde kırmızı çerçeveli elmas içinde “{g[1].lower()}” işareti var. Hangi madde buna örnektir?",
                        g[2].split(",")[0], [x[2].split(",")[0] for x in GHS if x != g][:3], [f"{g[1]}: ör. {g[2]}."]))
    havuz = _ek(r, [
        ("Laboratuvar kapısında mavi daire içinde gözlük işareti ne anlama gelir?", "Koruyucu gözlük takmak zorunludur",
         ["Gözlük yasaktır", "Göz duşu buradadır", "Lazer tehlikesi vardır"], ["Mavi daire = zorunluluk."]),
        ("Yeşil kare içinde göz ve su işareti neyi gösterir?", "Göz duşunun yerini", ["Su içmenin yasak olduğunu",
                                                                                     "Gözlük takma zorunluluğunu", "Lazer tehlikesini"],
         ["Yeşil = acil durum / ilk yardım donanımı."]),
        ("Yangın söndürücünün yerini gösteren işaret hangi renktedir?", "Kırmızı kare", ["Yeşil kare", "Mavi daire", "Sarı üçgen"],
         ["Kırmızı kare = yangın ekipmanı."]),
        ("Sarı üçgen içinde şimşek işareti neyi gösterir?", "Elektrik tehlikesi", ["Lazer", "Sıcak yüzey", "Patlayıcı"],
         ["Uyarı işareti."]),
        ("Sarı üçgen içinde dalgalı çizgiler ve altında bir yüzey hangi tehlikeyi gösterir?", "Sıcak yüzey",
         ["Elektrik", "Su baskını", "Biyolojik tehlike"], ["Etüv, kül fırını, ısıtıcı blok yanında görülür."]),
        ("Üç iç içe halkadan oluşan sembol hangi tehlikeyi gösterir?", "Biyolojik tehlike", ["Radyasyon", "Lazer",
                                                                                            "Elektrik"],
         ["Mikrobiyoloji laboratuvarlarında görülür."]),
        ("Kırmızı çerçeveli çizgili daire içinde fincan ve çatal ne anlama gelir?", "Yemek ve içmek yasaktır",
         ["Mutfak buradadır", "Yemek molası zorunludur", "Kimyasal tadılabilir"], ["Yasak işareti."]),
        ("Su ile söndürme yasak işareti en çok hangi maddelerin bulunduğu yerde kullanılır?", "Alkali metaller (Na, K)",
         ["Kâğıt ve tahta", "Saf su", "Kum"], ["Bu maddeler suyla şiddetli tepkime verir."]),
        ("GHS işaretlerinde etiketteki uyarı kelimelerinden hangisi daha ciddi tehlikeyi gösterir?", "Tehlike",
         ["Dikkat", "Bilgi", "Not"], ["“Tehlike” > “Dikkat”."]),
        ("NFPA elmasında beyaz bölümde üstü çizili W ne anlama gelir?", "Suyla tepkimeye girer; su kullanılmaz",
         ["Su ile yıkanabilir", "Suda çözünür", "Su gibi zararsızdır"], ["Özel uyarı bölümü."]),
        ("NFPA elmasında en yüksek tehlike hangi sayıyla gösterilir?", "4", ["0", "1", "10"], ["0–4 arası; 4 en tehlikeli."]),
        ("NFPA elmasında mavi bölüm hangi tehlikeyi gösterir?", "Sağlık", ["Yanıcılık", "Reaktiflik", "Özel uyarı"], ["Mavi = sağlık."]),
        ("NFPA elmasında kırmızı bölüm hangi tehlikeyi gösterir?", "Yanıcılık", ["Sağlık", "Reaktiflik", "Özel uyarı"], ["Kırmızı = yanıcılık."]),
        ("NFPA elmasında sarı bölüm hangi tehlikeyi gösterir?", "Reaktiflik (kararsızlık)", ["Sağlık", "Yanıcılık", "Radyasyon"],
         ["Sarı = reaktiflik."]),
        ("Acil çıkış işareti hangi renktedir?", "Yeşil", ["Kırmızı", "Mavi", "Sarı"], ["Yeşil = güvenli yol, kaçış."]),
        ("Kimyasalın şişesindeki işaretlerin ayrıntılı açıklaması nerede bulunur?", "Güvenlik Bilgi Formunda (GBF)",
         ["Faturada", "Kalibrasyon sertifikasında", "Laboratuvar defterinde"], ["Her kimyasalın GBF'si vardır."]),
    ])
    return _tamamla(r, sabit, havuz)


# ---------------------------------------------------------------------------
def gen_okuma(r):
    sabit = []
    a = int(r.choice([10, 20, 40, 50, 60]))
    adim_ = float(r.choice([1, 2, 5, 10]))
    n = int(r.choice([5, 10, 20]))
    b = a + adim_ * 10
    bolme = (b - a) / n
    sabit.append(_secim(r, f"Bir mezürde {a:g} ile {b:g} mL çizgileri arasında {n} küçük bölme var. Bir bölme kaç mL'dir?",
                        f"{_sayi_tr(bolme)} mL", [f"{_sayi_tr(bolme * 10)} mL", f"{_sayi_tr(bolme / 10)} mL",
                                                  f"{_sayi_tr((b - a) / (n - 1))} mL", f"{_sayi_tr(b / n)} mL"],
                        ["Bölme değeri = (iki rakam arası fark) ÷ bölme sayısı",
                         f"({b:g} − {a:g}) ÷ {n} = {_sayi_tr(bolme)} mL"]))
    ilk = round(float(r.uniform(0.2, 5)), 2)
    son = round(ilk + float(r.uniform(8, 35)), 2)
    sabit.append(_secim(r, f"Titrasyonda büretin ilk okuması {_sayi_tr(ilk)} mL, son okuması {_sayi_tr(son)} mL. "
                           "Harcanan çözelti kaç mL'dir?", f"{_sayi_tr(round(son - ilk, 2))} mL",
                        [f"{_sayi_tr(son)} mL", f"{_sayi_tr(round(son + ilk, 2))} mL", f"{_sayi_tr(round(50 - son, 2))} mL"],
                        ["Harcanan = son − ilk okuma (büret sıfırdan başlamak zorunda değildir)."]))
    v1 = round(float(r.integers(200, 500)) / 10, 1)
    v2 = round(v1 + float(r.integers(15, 120)) / 10, 1)
    sabit.append(_secim(r, f"Mezürde {_sayi_tr(v1)} mL su varken içine küçük bir taş atılıyor ve seviye {_sayi_tr(v2)} mL'ye "
                           "çıkıyor. Taşın hacmi kaç cm³'tür?", f"{_sayi_tr(round(v2 - v1, 1))} cm³",
                        [f"{_sayi_tr(v2)} cm³", f"{_sayi_tr(round(v2 + v1, 1))} cm³", f"{_sayi_tr(round((v2 - v1) * 1000, 1))} cm³"],
                        ["Yer değiştiren su = taşın hacmi; 1 mL = 1 cm³."]))
    havuz = _ek(r, [
        ("Su ve sulu çözeltilerde menisküs nereden okunur?", "Alt kenarından", ["Üst kenarından", "Ortasından",
                                                                                "Cam kenarındaki en yüksek noktadan"],
         ["Su camı ıslatır, yüzey çukur olur."]),
        ("Cıvada menisküs nasıldır ve nereden okunur?", "Tümsek; üst kenarından", ["Çukur; alt kenarından",
                                                                                   "Düz; herhangi bir yerinden", "Çukur; üst kenarından"],
         ["Cıva camı ıslatmaz."]),
        ("Koyu renkli (ör. permanganat) çözeltide okuma nereden yapılır?", "Üst kenarından", ["Alt kenarından",
                                                                                              "Okunamaz", "Ortasından"],
         ["Alt kenar görünmez."]),
        ("Okuma sırasında göz nerede olmalıdır?", "Menisküs ile aynı hizada", ["Biraz yukarıda", "Biraz aşağıda", "Fark etmez"],
         ["Aksi hâlde paralaks hatası olur."]),
        ("Mezüre yukarıdan bakılırsa okunan değer nasıl olur?", "Gerçeğinden büyük", ["Gerçeğinden küçük", "Doğru",
                                                                                     "Sıfır"], ["Mezürde değer yukarı artar."]),
        ("Bürete yukarıdan bakılırsa okunan değer nasıl olur?", "Gerçeğinden küçük", ["Gerçeğinden büyük", "Doğru",
                                                                                     "Sıfır"], ["Bürette değer aşağı doğru artar; ters etki."]),
        ("Büretin ölçeği hangi yönde artar?", "Yukarıdan aşağıya (0 üstte)", ["Aşağıdan yukarıya", "Soldan sağa",
                                                                              "Ortadan dışarıya"], ["Akıtılan hacmi doğrudan okumak için."]),
        ("0,1 mL bölmeli bir bürette okuma kaç ondalıkla yazılır?", "İki ondalık (ör. 23,47 mL)", ["Hiç ondalık yok",
                                                                                                 "Bir ondalık", "Dört ondalık"],
         ["En küçük bölmenin onda biri tahmin edilir."]),
        ("1 mL bölmeli bir mezürde okuma kaç ondalıkla yazılır?", "Bir ondalık (ör. 46,4 mL)", ["İki ondalık", "Hiç ondalık yok",
                                                                                              "Üç ondalık"], ["Bölmenin onda biri tahmin edilir."]),
        ("Okuma kartı ne işe yarar?", "Menisküsün alt kenarını koyu ve keskin gösterir", ["Sıvıyı ısıtır",
                                                                                          "Kalibrasyon yapar", "Sıvıyı karıştırır"],
         ["Menisküsün arkasına, biraz altına tutulan siyah kart."]),
        ("Pipet üzerindeki “Ex” (TD) ne demektir?", "Akıttığı hacme göre ayarlanmıştır", ["İçerdiği hacme göre ayarlanmıştır",
                                                                                         "Patlayıcıdır", "Plastiktir"], ["Ex = akıtmak için."]),
        ("Balon jojenin üzerindeki “In” (TC) ne demektir?", "İçerdiği hacme göre ayarlanmıştır", ["Akıttığı hacme göre",
                                                                                                 "İçi boyalıdır", "Isıtılabilir"],
         ["Çizgiye kadar dolu balon tam hacmi içerir."]),
        ("“Ex” tam pipetin ucunda kalan son damla ne yapılır?", "Üflenmez, orada kalır", ["Puarla üflenir", "Parmakla silinip eklenir",
                                                                                         "Pipet çalkalanır"],
         ["Pipet bu damla hesaba katılarak ayarlanmıştır (üflemeli işaretliler hariç)."]),
        ("Hacim ölçen cam malzeme hangi sıcaklıkta ayarlanmıştır?", "20 °C", ["0 °C", "37 °C", "100 °C"], ["Etikette yazar."]),
        ("Balon jojede çözelti çizgiye nasıl tamamlanır?", "Damla damla, menisküsün alt kenarı çizgiye teğet olana kadar",
         ["Hızla taşırarak", "Çizginin 1 cm üstüne kadar", "Göz kararı"], ["Göz hizasında."]),
        ("Sıcak bir çözelti balon jojede neden hemen çizgiye tamamlanmaz?", "Soğuyunca hacmi küçülür, derişim yanlış olur",
         ["Balon erir", "Renk değişir", "Hiçbir sakıncası yoktur"], ["Önce 20 °C'ye gelmesi beklenir."]),
        ("Büreti doldurmadan önce neden çözeltiyle çalkalanır?", "İçteki su damlaları çözeltiyi seyreltmesin diye",
         ["Büret soğusun diye", "Musluk yağlansın diye", "Gerek yoktur"], ["2–3 kez çalkalanır."]),
        ("Büretin ucundaki hava kabarcığı neden giderilir?", "Kabarcık çıkınca harcanan hacim yanlış okunur",
         ["Renk değiştirir", "Çözelti donar", "Musluk kırılır"], ["Kabarcık hacmi okumaya eklenir."]),
        ("Büret doldurulduktan sonra huni neden çıkarılır?", "Huniden damlayan sıvı okumayı bozar", ["Huni kırılır",
                                                                                                  "Huni ağırdır", "Gerek yoktur"], ["Kural."]),
        ("Mikropipette sıvı çekerken piston nereye kadar bastırılır?", "Birinci durağa", ["İkinci durağa", "Hiç bastırılmaz",
                                                                                         "Yarıya kadar"], ["Normal (ileri) pipetleme."]),
        ("Mikropipette sıvıyı tamamen boşaltmak için ne yapılır?", "Önce birinci, sonra ikinci durağa bastırılır",
         ["Yalnızca birinci durağa", "Pipet sallanır", "Uç ağızla üflenir"], ["İkinci durak son damlayı üfler."]),
        ("Mikropipet ucu sıvıya ne kadar daldırılır?", "2–3 mm", ["Uç tamamen", "Hiç değdirilmez", "2–3 cm"],
         ["Çok derine daldırmak ucun dışına sıvı bulaştırır."]),
        ("Yapışkan ya da köpüren sıvılarda hangi teknik kullanılır?", "Ters pipetleme", ["Ağızla pipetleme",
                                                                                         "Pipeti yatırma", "Ucu kesme"],
         ["Çekerken 2. durak, boşaltırken 1. durak."]),
        ("Mikropipet neden yatay bırakılmaz?", "Uçtaki sıvı gövdeye kaçabilir", ["Ekran kapanır", "Ayar bozulur her zaman",
                                                                                 "Uç ısınır"], ["Dik askıda saklanır."]),
        ("8 mL sıvı ölçmek için hangi mezür seçilmelidir?", "10 mL'lik", ["100 mL'lik", "500 mL'lik", "1000 mL'lik"],
         ["Ölçülecek hacme en yakın boyutta mezür daha hassastır."]),
        ("A sınıfı 10 mL tam pipetin hata payı yaklaşık ne kadardır?", "±0,02 mL", ["±1 mL", "±0,5 mL", "±2 mL"],
         ["Tam pipet en hassas hacim ölçerlerdendir."]),
        ("Hangi malzeme ile ölçülen hacim en AZ hassastır?", "Beher", ["Tam pipet", "Büret", "Balon joje"],
         ["Beher çizgileri yaklaşıktır."]),
    ])
    return _tamamla(r, sabit, havuz)


# ===========================================================================
# Gezinme
# ===========================================================================
SAYFALAR = [
    st.Page(sayfa_giris, title="Giriş", icon="🏠", url_path="giris", default=True),
    st.Page(sayfa_guvenlik, title="1 · Laboratuvar güvenliği", url_path="guvenlik"),
    st.Page(sayfa_isaretler, title="2 · Güvenlik ve tehlike işaretleri", url_path="isaretler"),
    st.Page(sayfa_kimyasal, title="3 · Kimyasallar ve kazalar", url_path="kimyasallar"),
    st.Page(sayfa_metrik, title="4 · Metrik sistem ve birimler", url_path="metrik-sistem"),
    st.Page(sayfa_cam, title="5 · Cam, plastik ve diğer malzemeler", url_path="malzemeler"),
    st.Page(sayfa_okuma, title="6 · Okuma ve kullanım", url_path="okuma-kullanim"),
    st.Page(sayfa_olcum, title="7 · Ölçümün temelleri", url_path="olcum"),
    st.Page(sayfa_terazi, title="8 · Terazi ve nem", url_path="terazi-nem"),
    st.Page(sayfa_elektro, title="9 · pH, EC ve su cihazları", url_path="ph-ec"),
    st.Page(sayfa_optik, title="10 · Optik cihazlar", url_path="optik"),
    st.Page(sayfa_ileri, title="11 · İleri analiz cihazları", url_path="ileri-cihazlar"),
    st.Page(sayfa_lablar, title="12 · Laboratuvar türleri", url_path="laboratuvar-turleri"),
    st.Page(sayfa_numune, title="13 · Örnek alma", url_path="ornek-alma"),
    st.Page(sayfa_kalite, title="14 · Kalite ve terimler", url_path="kalite-terimler"),
    st.Page(sayfa_tekrar, title="15 · Genel tekrar", url_path="genel-tekrar"),
]
gezinme = st.navigation(SAYFALAR)

with st.sidebar:
    tohum = st.number_input("Rastgele tohum (0 = rastgele)", 0, 999999, 0,
                            help="Sınıfta herkes aynı sayıyı girerse aynı soruları görür.")
    if st.session_state.get("tohum") != tohum:
        st.session_state.tohum = tohum
        st.session_state.rng = (np.random.default_rng(tohum) if tohum
                                else np.random.default_rng())
    st.divider()
    st.caption(TELIF)

basliklar = [p.title for p in SAYFALAR]
simdiki = basliklar.index(gezinme.title) if gezinme.title in basliklar else 0
secilen = st.selectbox("📚 Bölüm", basliklar, index=simdiki)
if secilen != gezinme.title:
    st.switch_page(SAYFALAR[basliklar.index(secilen)])

gezinme.run()

st.divider()
c1, _, c3 = st.columns([1, 0.2, 1])
if simdiki > 0:
    c1.page_link(SAYFALAR[simdiki - 1], label=f"◀ {basliklar[simdiki - 1]}")
if simdiki < len(SAYFALAR) - 1:
    c3.page_link(SAYFALAR[simdiki + 1], label=f"{basliklar[simdiki + 1]} ▶")

st.markdown(f'<div style="text-align:center;color:gray;font-size:0.85rem;'
            f'margin-top:24px">{TELIF}</div>', unsafe_allow_html=True)

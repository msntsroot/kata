"""Janela do kata, integrada ao sway: tiles com gaps e uma statusline no rodapé.

Editor à esquerda; à direita, o enunciado em cima e os critérios de aceite embaixo.
Sem barra de título própria: o sway cuida da janela.
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import timedelta

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango  # noqa: E402

try:
    gi.require_version("GtkSource", "5")
    from gi.repository import GtkSource  # noqa: E402
except (ValueError, ImportError):
    GtkSource = None

from . import criterios as C  # noqa: E402
from . import progresso as P  # noqa: E402
from .avaliar import avaliar  # noqa: E402
from .db import Desafios, Progresso  # noqa: E402
from .lint import lint  # noqa: E402

APP_ID = "local.kata"
SINAL_WAYBAR = 11
PALETA = os.path.expanduser("~/.config/sway/palette.json")
PALETA_PADRAO = {"bg": "#0a0f12", "pill": "#131c22", "surface": "#0f171d", "fg": "#c6ccd2",
                 "fg_bright": "#dce1e5", "dim": "#535c65", "accent": "#558dbe", "soft": "#99b4cc",
                 "selection": "#202f3c", "border": "#2e3e4c"}
FONTE = "Terminess Nerd Font Mono"
ARCOS = ["condicionais", "laços", "strings", "listas", "dicionários", "recursão",
         "busca e ordenação", "dois ponteiros", "pilhas e grades", "guloso e DP"]
# cores fixas do design (independentes do wallpaper)
VERDE, VERMELHO, AMARELO, CORAL, ROXO = "#98c379", "#e06c75", "#e5c07b", "#e88a7f", "#c792ea"
# ícones da Nerd Font
I_OK, I_FALHA, I_PENDENTE, I_CADEADO, I_MAIS, I_MENOS, I_AVISO, I_PLAY = (
    "\uf00c", "\uf00d", "\uf10c", "\uf023", "\uf067", "\uf068", "\uf071", "\uf04b")

COR_CODIGO = PALETA_PADRAO["soft"]


def md(texto):
    """Markdown mínimo para Pango: `código` e **negrito**."""
    t = GLib.markup_escape_text(texto)
    t = re.sub(r"`([^`]+)`", lambda m: f'<span foreground="{COR_CODIGO}">{m[1]}</span>', t)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)


def curto(texto, limite=160):
    """Casos grandes (listas de 1 milhão) não cabem na tela: mostra o começo e o tamanho."""
    return texto if len(texto) <= limite else f"{texto[:limite]}…  ({len(texto)} caracteres)"


def py(json_txt):
    """JSON canônico → repr Python (True, None, aspas simples): é o que o usuário escreveria."""
    return curto(repr(json.loads(json_txt)))


def chamada(entrada):
    return curto("resolver(" + ", ".join(repr(a) for a in entrada) + ")")


def rgba(hexa, alfa):
    h = hexa.lstrip("#")
    return f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, {alfa})"


def css(p):
    tile = rgba(p["bg"], .93)
    return f"""
    :root {{ --accent-bg-color: {p['accent']}; --accent-color: {p['soft']};
             --window-bg-color: {p['bg']}; --view-bg-color: {p['surface']}; --popover-bg-color: {p['pill']}; }}
    @define-color accent_bg_color {p['accent']};
    @define-color accent_color {p['soft']};
    @define-color window_bg_color {p['bg']};
    @define-color view_bg_color {p['surface']};
    @define-color popover_bg_color {p['pill']};
    window.kata {{ background: transparent; }}
    window.kata, window.config {{ color: {p['fg']}; font-family: "{FONTE}"; font-size: 16px; }}
    window.config {{ background: {p['bg']}; }}
    .tile {{ background: {tile}; border: 1px solid rgba(255, 255, 255, .08); }}
    .tile.editor-tile {{ border-color: {p['accent']}; }}
    .tile.falhou {{ border-color: {VERMELHO}; }}
    .tile.passou {{ border-color: {VERDE}; }}
    .faixa {{ padding: 8px 16px; font-size: 14px; color: {p['dim']}; }}
    .faixa.topo {{ border-bottom: 1px solid rgba(255, 255, 255, .06); }}
    .faixa.base {{ border-top: 1px solid rgba(255, 255, 255, .06); }}
    .editor, .editor text {{ font-family: "{FONTE}"; font-size: 16px; background: transparent; }}
    .editor .line-numbers {{ background: transparent; }}
    .painel {{ padding: 22px 26px; }}
    .meta {{ font-size: 14px; color: {p['dim']}; }}
    .titulo {{ font-size: 24px; font-weight: 700; color: {p['fg_bright']}; }}
    .enunciado {{ font-size: 16px; }}
    .dim {{ color: {p['dim']}; }}
    .claro {{ color: {p['fg_bright']}; }}
    .ok {{ color: {VERDE}; }}
    .falha {{ color: {VERMELHO}; }}
    .aviso {{ color: {AMARELO}; }}
    .coral {{ color: {CORAL}; }}
    .acento {{ color: {p['soft']}; }}
    .separador {{ border-top: 1px solid rgba(255, 255, 255, .06); padding-top: 12px; }}
    .badge {{ min-width: 22px; min-height: 22px; padding: 0; font-weight: 700; font-size: 14px;
              background: {AMARELO}; color: #14100f; }}
    .badge-mais {{ min-width: 22px; min-height: 22px; padding: 0; border-radius: 0; font-size: 12px;
                   background: transparent; color: {p['dim']}; border: 1px dashed {p['dim']}; box-shadow: none; }}
    .badge-mais:hover {{ color: {AMARELO}; border-color: {AMARELO}; }}
    .chip-usa {{ padding: 1px 8px; min-height: 0; border-radius: 0; font-size: 14px; color: {p['soft']};
                 background: rgba(255, 255, 255, .04); box-shadow: none; }}
    .play {{ padding: 0 6px; min-height: 0; min-width: 0; border-radius: 0; background: transparent;
              box-shadow: none; color: {VERDE}; }}
    .play:hover {{ background: rgba(152, 195, 121, .15); }}
    .toggle-ocultos {{ padding: 0; min-height: 0; min-width: 0; border-radius: 0; background: transparent;
                       box-shadow: none; color: {p['fg']}; font-weight: 400; }}
    .toggle-ocultos:hover {{ color: {p['fg_bright']}; }}
    .criterio {{ padding: 6px 0; border-top: 1px solid rgba(255, 255, 255, .05); }}
    .icone {{ min-width: 18px; }}
    .detalhe {{ font-size: 14px; }}
    .statusline {{ min-height: 30px; font-size: 14px; }}
    .seg {{ background: {tile}; padding: 0 12px; min-height: 30px; border-radius: 0; box-shadow: none; color: {p['fg']}; }}
    button.seg {{ color: #9aa3b0; }}
    button.seg:hover {{ color: {p['fg_bright']}; background: {rgba(p['bg'], .98)}; }}
    .modo {{ font-weight: 700; color: #14100f; padding: 0 12px; min-height: 30px; }}
    .modo.kata {{ background: {CORAL}; }}
    .modo.falhou {{ background: {VERMELHO}; }}
    .modo.passou {{ background: {VERDE}; }}
    .modo.rodando {{ background: {p['soft']}; }}
    .modo.treino {{ background: {p['accent']}; }}
    .grande {{ font-size: 32px; font-weight: 700; color: {p['fg_bright']}; }}
    .dia {{ min-width: 12px; min-height: 12px; background: {p['pill']}; }}
    .dia.feito {{ background: {p['accent']}; }}
    .dia.congelado {{ background: #7fb4d6; opacity: .5; }}
    .dia.hoje {{ box-shadow: inset 0 0 0 1px {p['soft']}; }}
    .conquista.nao {{ opacity: .25; }}
    .codigo-bloco {{ background: {p['pill']}; padding: 8px 12px; }}
    entry {{ border-radius: 0; font-family: "{FONTE}"; }}
    """


def label(texto="", classes=(), markup=False, **kw):
    kw.setdefault("xalign", 0)
    lb = Gtk.Label(css_classes=list(classes), **kw)
    lb.set_markup(texto) if markup else lb.set_label(texto)
    return lb


class Janela(Adw.ApplicationWindow):
    def __init__(self, app, treino=None):
        super().__init__(application=app, title="kata")
        self.set_default_size(1500, 880)
        self.add_css_class("kata")
        self.desafios = Desafios()
        self.prog = Progresso()
        self.dia = P.hoje()
        self.treino = treino is not None
        self.rodando = False
        self.rodou = False
        self.copia_interna = None
        self.inicio = time.monotonic()
        self._lint_id = 0
        self._rascunho_id = 0
        self._carregando = False

        if self.treino:
            self.id, self.status = treino, "pendente"
        else:
            self.id, self.status = P.desafio_do_dia(self.prog.resolvidos(), self.desafios.total(), self.dia)

        self.toasts = Adw.ToastOverlay(child=self._layout())
        self.set_content(self.toasts)
        self._atalhos()
        self.carregar()
        self.connect("close-request", lambda *_: self._salvar_rascunho() or False)
        GLib.timeout_add_seconds(1, self._tique)

    # ---------- montagem ----------

    def _layout(self):
        grade = Gtk.Grid(column_homogeneous=True, row_homogeneous=True, column_spacing=10, row_spacing=10,
                         vexpand=True)
        # editor : direita = 1,25 : 1  →  5 colunas : 4 colunas
        grade.attach(self._tile_editor(), 0, 0, 5, 2)
        self.box_enun = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, css_classes=["painel"])
        sw = Gtk.ScrolledWindow(child=self.box_enun, css_classes=["tile"])
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grade.attach(sw, 5, 0, 4, 1)
        grade.attach(self._tile_criterios(), 5, 1, 4, 1)

        raiz = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        raiz.append(grade)
        raiz.append(self._statusline())
        return raiz

    def _tile_editor(self):
        if GtkSource:
            self.buf = GtkSource.Buffer()
            self.buf.set_language(GtkSource.LanguageManager.get_default().get_language("python3"))
            esquemas = GtkSource.StyleSchemeManager.get_default()
            esquema = esquemas.get_scheme("Adwaita-dark") or esquemas.get_scheme("oblivion")
            if esquema:
                self.buf.set_style_scheme(esquema)
            self.view = GtkSource.View(buffer=self.buf, show_line_numbers=True, auto_indent=True,
                                       indent_on_tab=True, tab_width=4, insert_spaces_instead_of_tabs=True,
                                       highlight_current_line=True, smart_backspace=True)
        else:
            self.buf = Gtk.TextBuffer()
            self.view = Gtk.TextView(buffer=self.buf)
        self.view.add_css_class("editor")
        self.view.set_monospace(True)
        self.view.set_top_margin(14)
        self.view.set_left_margin(10)
        self.view.set_wrap_mode(Gtk.WrapMode.NONE)
        self.tag_lint = self.buf.create_tag("lint", underline=Pango.Underline.ERROR)
        self.buf.connect("changed", self._mudou)
        self.buf.connect("notify::cursor-position", lambda *_: self._cursor())
        self._bloquear_colar()

        topo = Gtk.Box(css_classes=["faixa", "topo"])
        self.lbl_arquivo = label("", markup=True, hexpand=True)
        topo.append(self.lbl_arquivo)
        topo.append(label(f"python {sys.version_info.major}.{sys.version_info.minor}"))

        base = Gtk.Box(spacing=10, css_classes=["faixa", "base"])
        base.append(label(I_CADEADO, tooltip_text="colar de fora está bloqueado: digite, é aí que se aprende"))
        self.lbl_lint = label("", ["aviso"], hexpand=True, ellipsize=Pango.EllipsizeMode.END)
        base.append(self.lbl_lint)
        play = Gtk.Button(label=I_PLAY, css_classes=["play"], focusable=False, tooltip_text="rodar · ctrl+enter")
        play.connect("clicked", lambda *_: self.rodar())
        base.append(play)
        self.lbl_cursor = label("1:1")
        base.append(self.lbl_cursor)

        caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, css_classes=["tile", "editor-tile"])
        caixa.append(topo)
        caixa.append(Gtk.ScrolledWindow(child=self.view, vexpand=True))
        caixa.append(base)
        return caixa

    def _tile_criterios(self):
        self.tile_crit = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, css_classes=["tile"])
        topo = Gtk.Box(css_classes=["faixa", "topo"])
        self.lbl_crit_titulo = label("critérios de aceite", hexpand=True)
        self.lbl_placar = label("", ["claro"], use_markup=True)
        topo.append(self.lbl_crit_titulo)
        topo.append(self.lbl_placar)
        self.box_crit = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=20, margin_end=20,
                                margin_top=6, margin_bottom=6)
        sw = Gtk.ScrolledWindow(child=self.box_crit, vexpand=True)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.box_msg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, css_classes=["faixa", "base"])
        self.tile_crit.append(topo)
        self.tile_crit.append(sw)
        self.tile_crit.append(self.box_msg)
        return self.tile_crit

    def _statusline(self):
        barra = Gtk.Box(spacing=8, css_classes=["statusline"])
        esq = Gtk.Box(spacing=8, hexpand=True)
        self.lbl_modo = label("KATA", ["modo", "kata"])
        self.lbl_ofensiva = label("", ["seg"])
        self.lbl_xp = label("", ["seg"])
        self.lbl_tempo = label("", ["seg", "acento"])
        for w in (self.lbl_modo, self.lbl_ofensiva, self.lbl_xp, self.lbl_tempo):
            esq.append(w)
        barra.append(esq)
        for texto, fn in (("ctrl+enter roda", self.rodar), ("ctrl+h dica", self.dica),
                          ("ctrl+, config", self.abrir_config), ("esc fecha", self.close)):
            bt = Gtk.Button(label=texto, css_classes=["seg"], focusable=False)
            bt.connect("clicked", lambda _b, f=fn: f())
            barra.append(bt)
        return barra

    def _atalhos(self):
        ctl = Gtk.ShortcutController(scope=Gtk.ShortcutScope.GLOBAL)
        ctl.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)  # antes do editor engolir o Ctrl+Enter
        for gatilho, fn in (("<Control>Return", self.rodar), ("<Control>h", self.dica),
                            ("<Control>comma", self.abrir_config), ("<Control>s", self._salvar_rascunho),
                            ("Escape", self.close)):
            ctl.add_shortcut(Gtk.Shortcut(trigger=Gtk.ShortcutTrigger.parse_string(gatilho),
                                          action=Gtk.CallbackAction.new(lambda *_, f=fn: (f(), True)[1])))
        self.add_controller(ctl)

    def _bloquear_colar(self):
        """Colar de fora fica bloqueado (é o que mantém a IA longe); copiar/colar dentro do editor funciona."""
        def copiou(*_):
            b = self.buf.get_selection_bounds()
            if b:
                self.copia_interna = self.buf.get_text(*b, True)

        def colou(view):
            view.stop_emission_by_name("paste-clipboard")
            view.get_clipboard().read_text_async(None, recebeu)

        def recebeu(cb, res):
            try:
                txt = cb.read_text_finish(res)
            except GLib.Error:
                return
            if txt is not None and txt == self.copia_interna:
                self.buf.delete_selection(True, True)
                self.buf.insert_interactive_at_cursor(txt, -1, True)
            else:
                self.toast(f"{I_CADEADO}  colar de fora está bloqueado")

        self.view.connect("copy-clipboard", copiou)
        self.view.connect("cut-clipboard", copiou)
        self.view.connect("paste-clipboard", colou)
        meio = Gtk.GestureClick(button=2)  # colar com o botão do meio (seleção primária)
        meio.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        meio.connect("pressed", lambda g, *_: g.set_state(Gtk.EventSequenceState.CLAIMED))
        self.view.add_controller(meio)
        drop = Gtk.DropTarget.new(str, Gdk.DragAction.COPY)
        drop.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        drop.connect("drop", lambda *_: True)  # arrastar texto pra dentro também não vale
        self.view.add_controller(drop)

    # ---------- estado ----------

    def carregar(self):
        if self.status == "fim":
            self._tela_fim()
            return
        self.d = self.desafios.get(self.id)
        self.casos = self.desafios.casos(self.id)
        self.est = self.prog.estado(self.id)
        res = self.prog.resolucao(self.id)
        self._carregando = True
        if self.status == "feito":
            self.buf.set_text(res["codigo"])
        elif self.treino:
            self.buf.set_text(self.d["esqueleto"])
        else:
            self.buf.set_text(self.est["rascunho"] or self.d["esqueleto"])
        self._carregando = False
        self.view.set_editable(self.status == "pendente")
        self._arquivo("resolvido" if self.status == "feito" else "rascunho salvo")
        self._montar_enunciado()
        self._montar_criterios()
        if self.status == "feito":
            self._pintar_tudo("ok")
            self._msg_resolvido(res)
            self._modo("passou")
        else:
            self._modo("treino" if self.treino else "kata")
            self._checar_estatico()
        self._atualizar_status()
        self._agendar_lint()
        self.view.grab_focus()

    def _modo(self, modo):
        self.modo = modo
        for m in ("kata", "falhou", "passou", "rodando", "treino"):
            self.lbl_modo.remove_css_class(m)
            self.tile_crit.remove_css_class(m)
        self.lbl_modo.add_css_class(modo)
        self.lbl_modo.set_label(modo.upper())
        if modo in ("falhou", "passou"):
            self.tile_crit.add_css_class(modo)

    def _atualizar_status(self):
        of = P.ofensiva(set(self.prog.resolvidos().values()), self.dia)
        neve = f"  {'❄' * of['congelamentos']}" if of["congelamentos"] else ""
        self.lbl_ofensiva.set_label(f"ofensiva {of['atual']}{neve}")
        self.lbl_xp.set_label(f"{self.prog.xp_total()} xp")

    def _arquivo(self, estado):
        self.lbl_arquivo.set_markup(f'<span foreground="#c8ccd4">resolver.py</span> · {estado}')

    def _cursor(self):
        it = self.buf.get_iter_at_mark(self.buf.get_insert())
        self.lbl_cursor.set_label(f"{it.get_line() + 1}:{it.get_line_offset() + 1}")

    # ---------- enunciado ----------

    def _montar_enunciado(self):
        b = self.box_enun
        self._limpar(b)
        topo = Gtk.Box()
        topo.append(label(f"#{self.id} · arco {self.d['arco']} · {ARCOS[self.d['arco'] - 1]}", ["meta"], hexpand=True))
        n = self.d["nivel"]
        topo.append(label(f'<span foreground="{CORAL}">{"■" * n}</span>{"□" * (10 - n)}', ["meta"], markup=True,
                          tooltip_text=f"nível {n}"))
        b.append(topo)
        b.append(label(self.d["titulo"], ["titulo"], wrap=True))
        b.append(label(md(self.d["enunciado"]), ["enunciado"], markup=True, wrap=True))

        ex = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        for c in self.casos:
            if c["visivel"]:
                ex.append(label(f'<span foreground="#5c6470">›</span>  {GLib.markup_escape_text(chamada(c["entrada"]))}'
                                f'  <span foreground="#5c6470">→</span>  '
                                f'<span foreground="{VERDE}">{GLib.markup_escape_text(py(c["esperado"]))}</span>',
                                markup=True, wrap=True, wrap_mode=Pango.WrapMode.CHAR))
        b.append(ex)

        if self.d["usa"]:
            chips = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, column_spacing=6, row_spacing=6,
                                max_children_per_line=6)
            chips.append(label("usa", ["meta"]))
            for u in self.d["usa"]:
                bt = Gtk.Button(label=f"#{u} {self.desafios.get(u)['titulo']}", css_classes=["chip-usa"],
                                tooltip_text="ver a sua solução daquele dia", focusable=False)
                bt.connect("clicked", lambda _b, u=u: self._ver_solucao(u))
                chips.append(bt)
            b.append(chips)

        # dicas: badge com o número + texto; o "+" revela a próxima
        self.box_dicas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, css_classes=["separador"])
        b.append(self.box_dicas)
        self._montar_dicas()

        if self.status == "feito":
            self._montar_conceito()

    def _montar_dicas(self):
        self._limpar(self.box_dicas)
        vistas = 3 if self.status == "feito" else self.est["dicas"]
        for i in range(vistas):
            linha = Gtk.Box(spacing=12)
            linha.append(Gtk.Label(label=str(i + 1), css_classes=["badge"], valign=Gtk.Align.START))
            linha.append(label(md(self.d["dicas"][i]), ["aviso"], markup=True, wrap=True, hexpand=True))
            self.box_dicas.append(linha)
        if vistas < 3 and self.status == "pendente":
            custo = "" if self.treino else f" (−{3 * self.d['nivel']} xp)"
            bt = Gtk.Button(label=I_MAIS, css_classes=["badge-mais"], halign=Gtk.Align.START, focusable=False,
                            tooltip_text=f"dica {vistas + 1}{custo} · ctrl+h")
            bt.connect("clicked", lambda *_: self.dica())
            self.box_dicas.append(bt)
        self.box_dicas.set_visible(self.box_dicas.get_first_child() is not None)

    def _montar_conceito(self):
        b = self.box_enun
        caixa = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, css_classes=["separador"])
        caixa.append(label(md(self.d["conceito"]), markup=True, wrap=True))
        for r in self.d["referencias"]:
            caixa.append(Gtk.LinkButton(uri=r["url"], label=r["titulo"], halign=Gtk.Align.START))
        res = self.prog.resolucao(self.id)
        if res and not self.treino:
            e = Gtk.Entry(text=res["nota"] or "", placeholder_text="o que aprendi hoje, numa linha")
            e.connect("activate", lambda en: (self.prog.anotar(self.id, en.get_text()), self.toast("anotado no caderno")))
            e.connect("notify::has-focus", lambda en, _p: self.prog.anotar(self.id, en.get_text()))
            caixa.append(e)
        b.append(caixa)

    # ---------- critérios de aceite ----------

    def _montar_criterios(self):
        """Uma linha por critério: cinza = ainda não atendido, verde = passou, vermelho = falhou."""
        self._limpar(self.box_crit)
        self.linhas = []
        crit = self.d["criterios"]
        if crit.get("proibido"):
            self._nova_linha("proibido", "sem " + ", ".join(f"`{x}`" for x in crit["proibido"]))
        if crit.get("recursivo"):
            self._nova_linha("recursivo", "usa recursão")
        for i, c in enumerate(self.casos):
            if c["visivel"]:
                self._nova_linha(("caso", i), f"`{chamada(c['entrada'])}` → `{py(c['esperado'])}`")
        # ocultos: uma linha-resumo; o "+" abre um por um
        ocultos = [i for i, c in enumerate(self.casos) if not c["visivel"]]
        if ocultos:
            n = len(ocultos)
            bt = Gtk.Button(css_classes=["toggle-ocultos"], focusable=False, hexpand=True)
            bt.set_child(label(f"{I_MAIS}  {n} casos de teste ocultos"))
            self._nova_linha("ocultos", widget=bt)
            self.box_ocultos = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=28, visible=False)
            self.box_crit.append(self.box_ocultos)
            for k, i in enumerate(ocultos, 1):
                self._nova_linha(("caso", i), f"oculto {k}", pai=self.box_ocultos)

            def alternar(b):
                aberto = not self.box_ocultos.get_visible()
                self.box_ocultos.set_visible(aberto)
                b.get_child().set_label(f"{I_MENOS if aberto else I_MAIS}  {n} casos de teste ocultos")
            bt.connect("clicked", alternar)
        if "tempo" in crit:
            self._nova_linha("tempo", f"termina em até {crit['tempo']}s")
        self._limpar(self.box_msg)
        self.box_msg.set_visible(False)
        self.lbl_placar.set_label("")
        self.lbl_crit_titulo.set_label("critérios de aceite")

    def _nova_linha(self, chave, texto="", widget=None, pai=None):
        linha = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, css_classes=["criterio"])
        topo = Gtk.Box(spacing=10)
        icone = label(I_PENDENTE, ["icone", "dim"])
        topo.append(icone)
        topo.append(widget or label(md(texto), markup=True, wrap=True, wrap_mode=Pango.WrapMode.CHAR, hexpand=True))
        linha.append(topo)
        detalhe = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_start=28, visible=False)
        linha.append(detalhe)
        (pai or self.box_crit).append(linha)
        self.linhas.append({"chave": chave, "icone": icone, "detalhe": detalhe})

    def _linha(self, chave):
        return next((l for l in self.linhas if l["chave"] == chave), None)

    def _pintar(self, l, estado, detalhes=()):
        """estado: 'pendente' | 'ok' | 'falha'. detalhes: [(rotulo, valor, classe)]."""
        if l is None:
            return
        icone = {"ok": I_OK, "falha": I_FALHA}.get(estado, I_PENDENTE)
        for c in ("ok", "falha", "dim"):
            l["icone"].remove_css_class(c)
        l["icone"].add_css_class(estado if estado != "pendente" else "dim")
        l["icone"].set_label(icone)
        self._limpar(l["detalhe"])
        for rotulo, valor, classe in detalhes:
            g = Gtk.Box(spacing=10)
            if rotulo:
                g.append(label(rotulo, ["dim", "detalhe"], width_chars=9))
            g.append(label(valor, [classe, "detalhe"], wrap=True, wrap_mode=Pango.WrapMode.CHAR, hexpand=True,
                           selectable=True))
            l["detalhe"].append(g)
        l["detalhe"].set_visible(bool(detalhes))

    def _pintar_tudo(self, estado):
        for l in self.linhas:
            self._pintar(l, estado)

    def _checar_estatico(self):
        """Critérios de código (proibido/recursão) atualizam enquanto você digita."""
        if self.status != "pendente" or not hasattr(self, "linhas"):
            return
        codigo = self._codigo()
        crit = self.d["criterios"]
        erros = C.checar(codigo, {"proibido": crit.get("proibido", [])}) if crit.get("proibido") else []
        if crit.get("proibido"):
            self._pintar(self._linha("proibido"), "falha" if erros else ("ok" if self.rodou else "pendente"),
                         [("", e, "falha") for e in erros])
        if crit.get("recursivo"):
            tem = not C.checar(codigo, {"recursivo": True})
            self._pintar(self._linha("recursivo"), "ok" if tem else ("falha" if self.rodou else "pendente"))

    def _mensagem(self, linhas):
        """Rodapé do tile de critérios: [(texto, classe)]."""
        self._limpar(self.box_msg)
        for texto, classe in linhas:
            self.box_msg.append(label(texto, [classe], wrap=True, selectable=True))
        self.box_msg.set_visible(bool(linhas))

    def _msg_resolvido(self, res):
        if not res or self.treino:
            self._mensagem([("treino concluído · esc fecha", "coral")])
            return
        extras = []
        if res["tentativas"] == 1:
            extras.append("de primeira")
        if res["dicas"] == 0:
            extras.append("sem dica")
        of = P.ofensiva(set(self.prog.resolvidos().values()), self.dia)
        self._mensagem([(" · ".join([f"+{res['xp']} xp"] + extras), "coral"),
                        (f"ofensiva → {of['atual']} dia{'s' if of['atual'] != 1 else ''} · volte amanhã · esc fecha", "dim")])
        self.lbl_placar.set_markup(f'<span foreground="{VERDE}">{len(self.casos)}/{len(self.casos)}</span>')

    def _tela_fim(self):
        self.d = None
        self.view.set_editable(False)
        self.buf.set_text("# você fez todos os desafios.\n# kata treino N refaz qualquer um.\n")
        self.box_enun.append(label("os 100", ["titulo"]))
        self._modo("passou")
        self._atualizar_status()

    # ---------- ações ----------

    def _codigo(self):
        return self.buf.get_text(self.buf.get_start_iter(), self.buf.get_end_iter(), True)

    def rodar(self):
        if self.rodando or self.status != "pendente":
            return
        codigo = self._codigo()
        self.rodando = True
        self._modo("rodando")
        self._salvar_rascunho()
        t0 = time.monotonic()

        def trabalho():
            r = avaliar(self.d, self.casos, codigo)
            GLib.idle_add(self._resultado, r, codigo, time.monotonic() - t0)

        threading.Thread(target=trabalho, daemon=True).start()

    def _resultado(self, r, codigo, dt):
        self.rodando = False
        self.rodou = True
        self.lbl_crit_titulo.set_label(f"critérios de aceite · {dt:.2f}s")
        sintaxe = r["carga"] and "SyntaxError" in r["carga"]
        if not self.treino and not r["erros_criterio"] and not sintaxe:
            self.prog.tentou(self.id)
        if r["aprovado"]:
            self._pintar_tudo("ok")
            self._venceu(codigo)
            return

        self._modo("falhou")
        self._pintar_tudo("pendente")
        self._checar_estatico()
        if r["erros_criterio"]:
            self.lbl_placar.set_label("")
            self._mensagem([("corrija os critérios de código antes: os casos nem rodaram", "dim")])
            return
        if r["carga"]:
            for l in self.linhas:
                if isinstance(l["chave"], tuple) or l["chave"] == "ocultos":
                    self._pintar(l, "falha")
            self.lbl_placar.set_markup(f'<span foreground="{VERMELHO}">0/{len(self.casos)}</span>')
            self._mensagem([("não rodou", "falha"), (r["carga"], "dim")])
            return

        casos = r["casos"]
        ok = sum(c["ok"] for c in casos)
        self.lbl_placar.set_markup(f'<span foreground="{VERMELHO}">{ok}/{len(self.casos)}</span>')
        det_ocultos, estados_ocultos, k = [], [], 0
        for i, caso in enumerate(self.casos):
            l = self._linha(("caso", i))
            if not caso["visivel"]:
                k += 1
            if i >= len(casos):
                estado = "falha" if r["tempo_esgotado"] and i == len(casos) else "pendente"
                self._pintar(l, estado)
                if not caso["visivel"]:
                    estados_ocultos.append(estado)
                continue
            c = casos[i]
            if not c["visivel"]:
                estados_ocultos.append("ok" if c["ok"] else "falha")
            if c["ok"]:
                self._pintar(l, "ok")
                continue
            det = []
            if c["erro"]:
                det.append(("erro", c["erro"], "falha"))
            else:
                if c["visivel"]:
                    det.append(("esperado", py(c["esperado"]), "ok"))
                det.append(("você", py(c["obtido"]), "falha"))
            if c["print"]:
                det.append(("print", curto(c["print"].rstrip(), 300), "dim"))
            if c["visivel"]:
                self._pintar(l, "falha", det)
            else:
                # oculto: só a entrada e o seu retorno, nunca o esperado; o resumo mostra os 2 primeiros
                self._pintar(l, "falha")
                if sum(1 for e in estados_ocultos if e == "falha") <= 2:
                    det_ocultos += [(f"oculto {k}", chamada(c["entrada"]), "dim")] + det
        if estados_ocultos:
            resumo = "falha" if "falha" in estados_ocultos else "ok" if all(e == "ok" for e in estados_ocultos) else "pendente"
            self._pintar(self._linha("ocultos"), resumo, det_ocultos)
        if "tempo" in self.d["criterios"]:
            self._pintar(self._linha("tempo"), "falha" if r["tempo_esgotado"] else "ok")

        msgs = []
        rodados = [c for c in casos if not c["erro"]]
        if r["tempo_esgotado"]:
            msgs.append((f"{I_AVISO}  tempo esgotado: laço infinito ou lento demais?", "aviso"))
        elif rodados and all(c["obtido"] == "null" for c in rodados):
            msgs.append(("sua função não retorna nada — falta um return?", "dim"))
        elif any(c["erro"] for c in casos):
            msgs.append(("o código quebrou em algum caso: veja o erro na linha vermelha", "dim"))
        self._mensagem(msgs)

    def _venceu(self, codigo):
        if self.treino:
            self.status = "feito_treino"
            self.view.set_editable(False)
            self._modo("passou")
            self._msg_resolvido(None)
            return
        est = self.prog.estado(self.id)
        antes = P.conquistas(self.prog.historico(), P.ofensiva(set(self.prog.resolvidos().values()), self.dia)["recorde"])
        ganho = P.xp(self.d["nivel"], max(est["tentativas"] - 1, 0), est["dicas"])
        self.prog.resolver(self.id, self.dia, ganho, max(est["tentativas"], 1), est["dicas"], codigo)
        self.status = "feito"
        of = P.ofensiva(set(self.prog.resolvidos().values()), self.dia)
        depois = P.conquistas(self.prog.historico(), of["recorde"])
        subprocess.Popen(["pkill", f"-RTMIN+{SINAL_WAYBAR}", "waybar"])
        self.carregar()
        for (em, nome, tem), (_, _, tinha) in zip(depois, antes):
            if tem and not tinha:
                self.toast(f"{em} conquista: {nome}")

    def dica(self):
        if self.status != "pendente" or self.est["dicas"] >= 3:
            return
        if not self.treino:
            self.prog.pediu_dica(self.id)
        self.est["dicas"] += 1
        self._montar_dicas()

    def _salvar_rascunho(self):
        if self.treino or self.status != "pendente":
            return
        self.prog.salvar_rascunho(self.id, self._codigo())
        self._arquivo("rascunho salvo")

    def _mudou(self, *_):
        if self._carregando:
            return
        self._arquivo("editando")
        self._agendar_lint()
        self._checar_estatico()
        if self._rascunho_id:
            GLib.source_remove(self._rascunho_id)

        def salvar():
            self._rascunho_id = 0
            self._salvar_rascunho()
            return False
        self._rascunho_id = GLib.timeout_add(1500, salvar)

    # ---------- lint ----------

    def _agendar_lint(self):
        if self._lint_id:
            GLib.source_remove(self._lint_id)
        self._lint_id = GLib.timeout_add(700, self._rodar_lint)

    def _rodar_lint(self):
        self._lint_id = 0
        codigo = self._codigo()
        threading.Thread(target=lambda: GLib.idle_add(self._aplicar_lint, codigo, lint(codigo)), daemon=True).start()
        return False

    def _aplicar_lint(self, codigo, itens):
        if codigo != self._codigo():
            return  # o texto mudou enquanto o lint rodava
        self.buf.remove_tag(self.tag_lint, self.buf.get_start_iter(), self.buf.get_end_iter())
        msgs = []
        for linha, _col, _cod, msg in itens:
            ok, ini = self.buf.get_iter_at_line(linha - 1)
            if not ok:
                continue
            fim = ini.copy()
            fim.forward_to_line_end()
            if ini.equal(fim):
                fim.forward_char()
            self.buf.apply_tag(self.tag_lint, ini, fim)
            msgs.append(f"linha {linha}: {msg}")
        self.view.set_tooltip_text("\n".join(msgs) or None)
        self.lbl_lint.set_label(f"{I_AVISO}  {msgs[0]}" + (f"  (+{len(msgs) - 1})" if len(msgs) > 1 else "")
                                if msgs and self.status == "pendente" else "")

    # ---------- config ----------

    def abrir_config(self):
        """Progresso, conquistas, caderno e preferências: tudo que não é o desafio fica aqui."""
        win = Adw.Window(transient_for=self, modal=True, title="kata · config", default_width=720,
                         default_height=640, css_classes=["config"])
        resolvidos = self.prog.resolvidos()
        of = P.ofensiva(set(resolvidos.values()), self.dia)
        xp_total = self.prog.xp_total()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, css_classes=["painel"])

        box.append(label("progresso", ["meta"]))
        topo = Gtk.Box(spacing=36)
        for valor, nome in ((str(of["atual"]), f"ofensiva · recorde {of['recorde']}"),
                            (str(P.nivel_jogador(xp_total)), f"nível · {xp_total} xp"),
                            (str(len(resolvidos)), P.titulo(len(resolvidos)).lower())):
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            col.append(label(valor, ["grande"]))
            col.append(label(nome, ["dim"]))
            topo.append(col)
        box.append(topo)
        if of["congelamentos"]:
            box.append(label("❄" * of["congelamentos"] + "  protegem a ofensiva se você perder um dia", ["dim"]))

        grade = Gtk.Grid(row_spacing=3, column_spacing=3)
        dias = set(resolvidos.values())
        semanas = 20
        inicio = self.dia - timedelta(days=self.dia.weekday() + 7 * (semanas - 1))
        for s in range(semanas):
            for d in range(7):
                dia = inicio + timedelta(days=7 * s + d)
                if dia > self.dia:
                    continue
                cl = ["dia"] + (["feito"] if dia in dias else ["congelado"] if dia in of["congelados"] else [])
                if dia == self.dia:
                    cl.append("hoje")
                grade.attach(Gtk.Box(css_classes=cl, tooltip_text=dia.strftime("%d/%m")), s, d, 1, 1)
        box.append(grade)

        box.append(label("conquistas", ["meta", "separador"]))
        conq = Gtk.FlowBox(max_children_per_line=4, selection_mode=Gtk.SelectionMode.NONE, row_spacing=8,
                           column_spacing=12)
        for em, nome, tem in P.conquistas(self.prog.historico(), of["recorde"]):
            conq.append(label(f"{em} {nome}", ["conquista"] + ([] if tem else ["nao"])))
        box.append(conq)

        box.append(label("preferências", ["meta", "separador"]))
        linha = Gtk.Box(spacing=12)
        sw = Gtk.Switch(active=self.prog.config("cronometro", True), valign=Gtk.Align.CENTER)
        sw.connect("notify::active", lambda s, _p: (self.prog.set_config("cronometro", s.get_active()), self._tique()))
        linha.append(sw)
        linha.append(label("cronômetro na statusline"))
        box.append(linha)

        bt = Gtk.Button(label="abrir o caderno", css_classes=["seg"], halign=Gtk.Align.START)
        bt.connect("clicked", lambda *_: (win.close(), self._caderno()))
        box.append(bt)

        esc = Gtk.ShortcutController()
        esc.add_shortcut(Gtk.Shortcut(trigger=Gtk.ShortcutTrigger.parse_string("Escape"),
                                      action=Gtk.CallbackAction.new(lambda *_: (win.close(), True)[1])))
        win.add_controller(esc)
        win.set_content(Gtk.ScrolledWindow(child=box))
        win.present()

    def _janela_texto(self, titulo, conteudo):
        win = Adw.Window(transient_for=self, modal=True, title=titulo, default_width=820, default_height=680,
                         css_classes=["config"])
        esc = Gtk.ShortcutController()
        esc.add_shortcut(Gtk.Shortcut(trigger=Gtk.ShortcutTrigger.parse_string("Escape"),
                                      action=Gtk.CallbackAction.new(lambda *_: (win.close(), True)[1])))
        win.add_controller(esc)
        win.set_content(Gtk.ScrolledWindow(child=conteudo))
        win.present()

    def _caderno(self):
        """Suas soluções e notas, do mais recente para o mais antigo."""
        lista = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14, css_classes=["painel"])
        lista.append(label("caderno", ["meta"]))
        hist = self.prog.historico()
        for id_, dia, _t, _k in reversed(hist):
            d = self.desafios.get(id_)
            r = self.prog.resolucao(id_)
            lista.append(label(f"#{id_} {d['titulo']}  ·  {dia.strftime('%d/%m')}", ["claro", "separador"]))
            if r["nota"]:
                lista.append(label(f"“{r['nota']}”", ["aviso"], wrap=True))
            lista.append(label(r["codigo"].rstrip(), ["codigo-bloco"], selectable=True))
        if not hist:
            lista.append(label("vazio por enquanto", ["dim"]))
        self._janela_texto("kata · caderno", lista)

    def _ver_solucao(self, id_):
        d = self.desafios.get(id_)
        r = self.prog.resolucao(id_)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, css_classes=["painel"])
        box.append(label(f"#{id_}", ["meta"]))
        box.append(label(d["titulo"], ["titulo"]))
        box.append(label(md(d["enunciado"]), markup=True, wrap=True))
        box.append(label((r["codigo"] if r else "(ainda não resolvido)").rstrip(), ["codigo-bloco"], selectable=True))
        if r and r["nota"]:
            box.append(label(f"“{r['nota']}”", ["aviso"], wrap=True))
        self._janela_texto(f"kata · #{id_}", box)

    # ---------- utilidades ----------

    def _tique(self):
        ligado = self.prog.config("cronometro", True) and self.status == "pendente"
        if ligado:
            s = int(time.monotonic() - self.inicio)
            self.lbl_tempo.set_label(f"{s // 60:02d}:{s % 60:02d}")
        self.lbl_tempo.set_visible(ligado)
        return True

    def toast(self, msg):
        self.toasts.add_toast(Adw.Toast(title=msg, timeout=3))

    @staticmethod
    def _limpar(box):
        while (f := box.get_first_child()) is not None:
            box.remove(f)


class App(Adw.Application):
    def __init__(self, treino=None):
        super().__init__(application_id=APP_ID if treino is None else APP_ID + "_treino",
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.treino = treino
        self.dnd_antes = None

    def do_startup(self):
        Adw.Application.do_startup(self)
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        try:
            with open(PALETA) as f:
                paleta = {**PALETA_PADRAO, **json.load(f)}
        except (OSError, json.JSONDecodeError):
            paleta = PALETA_PADRAO
        global COR_CODIGO
        COR_CODIGO = paleta["soft"]
        prov = Gtk.CssProvider()
        prov.load_from_string(css(paleta))
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), prov,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self._foco(True)
        # morto por SIGTERM/SIGINT ainda passa pelo shutdown e devolve o não perturbe
        for sig in (2, 15):
            GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, sig, lambda *_: self.quit() or False)

    def do_activate(self):
        win = self.props.active_window or Janela(self, self.treino)
        win.present()

    def do_shutdown(self):
        self._foco(False)
        Adw.Application.do_shutdown(self)

    def _foco(self, ligar):
        if os.environ.get("KATA_SEM_DND"):
            return
        """Não perturbe do swaync enquanto a janela estiver aberta (se ele já estava ligado, fica como estava)."""
        try:
            if ligar:
                self.dnd_antes = subprocess.run(["swaync-client", "-D"], capture_output=True, text=True,
                                                timeout=2).stdout.strip() == "true"
                if not self.dnd_antes:
                    subprocess.run(["swaync-client", "-dn"], capture_output=True, timeout=2)
            elif self.dnd_antes is False:
                subprocess.run(["swaync-client", "-df"], capture_output=True, timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            pass


def main(treino=None):
    sys.exit(App(treino).run([sys.argv[0]]))

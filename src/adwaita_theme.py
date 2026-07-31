"""
adwaita_theme.py

PySide6 / Qt6 uygulamalarina libadwaita (GNOME) gorunumu kazandiran QSS temasi.

Kullanim:
    from adwaita_theme import apply_theme

    app = QApplication(sys.argv)
    apply_theme(app, dark=False)   # acik tema
    apply_theme(app, dark=True)    # koyu tema

"Suggested action" (vurgulu / accent renkli buton) ve "destructive action"
(kirmizi / tehlikeli islem butonu) gibi libadwaita'ya ozgu buton siniflarini
Qt'de dynamic property ile taklit ediyoruz:

    btn = QPushButton("Kaydet")
    btn.setProperty("class", "suggested-action")
    btn.style().unpolish(btn)
    btn.style().polish(btn)

    btn2 = QPushButton("Sil")
    btn2.setProperty("class", "destructive-action")
    btn2.style().unpolish(btn2)
    btn2.style().polish(btn2)

Not: setProperty sonrasi style().unpolish()+polish() cagirmazsan Qt,
stylesheet'i yeniden degerlendirmez ve buton eski gorunumde kalir.
"""

from __future__ import annotations

from string import Template


# ---------------------------------------------------------------------------
# Renk paletleri (GNOME 44+ / libadwaita yaklasik degerleri)
# ---------------------------------------------------------------------------

LIGHT_PALETTE: dict[str, str] = {
    "window_bg":        "#fafafa",
    "view_bg":          "#ffffff",
    "card_bg":          "#ffffff",
    "headerbar_bg":     "#ebebeb",
    "sidebar_bg":       "#ebebeb",
    "popover_bg":       "#ffffff",

    "text":             "#1e1e1e",
    "secondary_text":   "rgba(0, 0, 0, 140)",
    "disabled_text":    "rgba(0, 0, 0, 90)",

    "border":           "rgba(0, 0, 0, 25)",
    "border_strong":    "rgba(0, 0, 0, 70)",

    "accent":           "#3584e4",
    "accent_hover":     "#1c71d8",
    "accent_pressed":   "#1a5fb4",
    "accent_text":      "#ffffff",

    "destructive":         "#e01b24",
    "destructive_hover":   "#c01c28",
    "destructive_pressed": "#a51d2d",

    "success":          "#2ec27e",
    "warning":          "#e5a50a",

    "button_bg":        "#e9e9e9",
    "button_hover":     "#dedede",
    "button_pressed":   "#d0d0d0",
    "disabled_bg":      "#f2f2f2",

    "hover_overlay":    "rgba(0, 0, 0, 15)",

    "scrollbar_handle":       "rgba(0, 0, 0, 60)",
    "scrollbar_handle_hover": "rgba(0, 0, 0, 100)",
    "track_bg":               "rgba(0, 0, 0, 15)",

    "tooltip_bg":       "#2e3436",
    "tooltip_text":     "#ffffff",
}

DARK_PALETTE: dict[str, str] = {
    "window_bg":        "#242424",
    "view_bg":          "#1e1e1e",
    "card_bg":          "#303030",
    "headerbar_bg":     "#2d2d2d",
    "sidebar_bg":       "#2a2a2a",
    "popover_bg":       "#383838",

    "text":             "#ffffff",
    "secondary_text":   "rgba(255, 255, 255, 140)",
    "disabled_text":    "rgba(255, 255, 255, 90)",

    "border":           "rgba(255, 255, 255, 25)",
    "border_strong":    "rgba(255, 255, 255, 70)",

    "accent":           "#3584e4",
    "accent_hover":     "#5e9ce6",
    "accent_pressed":   "#1c71d8",
    "accent_text":      "#ffffff",

    "destructive":         "#e01b24",
    "destructive_hover":   "#ed333b",
    "destructive_pressed": "#c01c28",

    "success":          "#2ec27e",
    "warning":          "#e5a50a",

    "button_bg":        "#383838",
    "button_hover":     "#414141",
    "button_pressed":   "#4a4a4a",
    "disabled_bg":      "#2a2a2a",

    "hover_overlay":    "rgba(255, 255, 255, 15)",

    "scrollbar_handle":       "rgba(255, 255, 255, 60)",
    "scrollbar_handle_hover": "rgba(255, 255, 255, 100)",
    "track_bg":               "rgba(255, 255, 255, 15)",

    "tooltip_bg":       "#1e1e1e",
    "tooltip_text":     "#ffffff",
}


# ---------------------------------------------------------------------------
# QSS Sablonu  ($degisken -> string.Template; QSS'in { } ile catismaz)
# ---------------------------------------------------------------------------

_QSS_TEMPLATE = Template(r"""
/* ===================== Genel ===================== */
QWidget {
    background-color: $window_bg;
    color: $text;
    font-family: "Cantarell", "Inter", "Segoe UI", sans-serif;
    font-size: 10.5pt;
}

QMainWindow, QDialog {
    background-color: $window_bg;
}

QWidget:disabled {
    color: $disabled_text;
}

/* ===================== Etiketler ===================== */
QLabel {
    background: transparent;
}
QLabel[class="dim-label"] {
    color: $secondary_text;
}
QLabel[class="title"] {
    font-size: 15pt;
    font-weight: 600;
}
QLabel[class="heading"] {
    font-size: 12pt;
    font-weight: 600;
}

/* ===================== Butonlar ===================== */
QPushButton, QToolButton {
    background-color: $button_bg;
    border: 1px solid $border;
    border-radius: 6px;
    padding: 6px 14px;
    color: $text;
}
QPushButton:hover, QToolButton:hover {
    background-color: $button_hover;
}
QPushButton:pressed, QToolButton:pressed {
    background-color: $button_pressed;
}
QPushButton:disabled, QToolButton:disabled {
    background-color: $disabled_bg;
    border-color: $border;
    color: $disabled_text;
}
QPushButton:focus, QToolButton:focus {
    border: 1px solid $accent;
}

/* libadwaita "suggested-action" -> setProperty("class", "suggested-action") */
QPushButton[class="suggested-action"] {
    background-color: $accent;
    border: 1px solid $accent_pressed;
    color: $accent_text;
    font-weight: 600;
}
QPushButton[class="suggested-action"]:hover {
    background-color: $accent_hover;
}
QPushButton[class="suggested-action"]:pressed {
    background-color: $accent_pressed;
}

/* libadwaita "destructive-action" -> setProperty("class", "destructive-action") */
QPushButton[class="destructive-action"] {
    background-color: $destructive;
    border: 1px solid $destructive_pressed;
    color: #ffffff;
    font-weight: 600;
}
QPushButton[class="destructive-action"]:hover {
    background-color: $destructive_hover;
}
QPushButton[class="destructive-action"]:pressed {
    background-color: $destructive_pressed;
}

/* Duz / cerceveisiz buton -> setProperty("class", "flat") */
QPushButton[class="flat"], QToolButton[class="flat"] {
    background: transparent;
    border: 1px solid transparent;
}
QPushButton[class="flat"]:hover, QToolButton[class="flat"]:hover {
    background-color: $hover_overlay;
}

QToolButton {
    padding: 6px;
}

/* ===================== Girdi alanlari ===================== */
QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox {
    background-color: $view_bg;
    border: 1px solid $border;
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: $accent;
    selection-color: $accent_text;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QAbstractSpinBox:focus, QComboBox:focus {
    border: 1px solid $accent;
}
QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled,
QAbstractSpinBox:disabled, QComboBox:disabled {
    background-color: $disabled_bg;
    color: $disabled_text;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: $popover_bg;
    border: 1px solid $border;
    border-radius: 8px;
    padding: 4px;
    outline: none;
    selection-background-color: $accent;
    selection-color: $accent_text;
}

QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
    width: 18px;
    border: none;
    background: transparent;
}

/* ===================== Onay kutusu / Radyo ===================== */
QCheckBox, QRadioButton {
    spacing: 8px;
    background: transparent;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1.5px solid $border_strong;
    background-color: $view_bg;
}
QCheckBox::indicator {
    border-radius: 5px;
}
QRadioButton::indicator {
    border-radius: 9px;
}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: $accent;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: $accent;
    border-color: $accent;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
    background-color: $disabled_bg;
    border-color: $border;
}

/* ===================== Sekmeler (ViewSwitcher benzeri) ===================== */
QTabWidget::pane {
    border: 1px solid $border;
    border-radius: 8px;
    top: -1px;
    background-color: $card_bg;
}
QTabBar {
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: $secondary_text;
    padding: 6px 16px;
    margin: 3px 2px;
    border-radius: 6px;
}
QTabBar::tab:selected {
    background-color: $card_bg;
    color: $text;
    font-weight: 600;
}
QTabBar::tab:hover:!selected {
    background-color: $hover_overlay;
}

/* ===================== Listeler / Agac (kenar cubugu) ===================== */
QListView, QTreeView, QTableView {
    background-color: $view_bg;
    border: 1px solid $border;
    border-radius: 8px;
    outline: none;
    alternate-background-color: transparent;
}
QListView::item, QTreeView::item {
    padding: 8px 10px;
    border-radius: 6px;
    margin: 1px 4px;
    color: $text;
}
QListView::item:hover:!selected, QTreeView::item:hover:!selected {
    background-color: $hover_overlay;
}
QListView::item:selected, QTreeView::item:selected {
    background-color: $accent;
    color: $accent_text;
}

QListView[class="sidebar"], QTreeView[class="sidebar"] {
    background-color: $sidebar_bg;
    border: none;
    border-radius: 0px;
}

QHeaderView::section {
    background-color: $headerbar_bg;
    color: $secondary_text;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid $border;
    border-right: 1px solid $border;
}
QHeaderView::section:last {
    border-right: none;
}

/* ===================== Kaydirma cubuklari ===================== */
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: $scrollbar_handle;
    border-radius: 4px;
    min-height: 28px;
}
QScrollBar::handle:vertical:hover {
    background: $scrollbar_handle_hover;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: transparent;
    height: 12px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: $scrollbar_handle;
    border-radius: 4px;
    min-width: 28px;
}
QScrollBar::handle:horizontal:hover {
    background: $scrollbar_handle_hover;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* ===================== Menuler ===================== */
QMenuBar {
    background-color: $headerbar_bg;
    border-bottom: 1px solid $border;
    padding: 2px;
}
QMenuBar::item {
    padding: 6px 10px;
    border-radius: 6px;
    background: transparent;
}
QMenuBar::item:selected {
    background-color: $hover_overlay;
}

QMenu {
    background-color: $popover_bg;
    border: 1px solid $border;
    border-radius: 10px;
    padding: 6px;
}
QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 6px;
    color: $text;
}
QMenu::item:selected {
    background-color: $accent;
    color: $accent_text;
}
QMenu::item:disabled {
    color: $disabled_text;
}
QMenu::separator {
    height: 1px;
    background: $border;
    margin: 4px 8px;
}

/* ===================== Arac cubugu / Baslik cubugu ===================== */
QToolBar {
    background-color: $headerbar_bg;
    border: none;
    border-bottom: 1px solid $border;
    padding: 6px;
    spacing: 6px;
}
QToolBar::separator {
    background-color: $border;
    width: 1px;
    margin: 4px 6px;
}

QStatusBar {
    background-color: $headerbar_bg;
    border-top: 1px solid $border;
    color: $secondary_text;
}

/* ===================== Grup kutusu (Preferences Group benzeri) ===================== */
QGroupBox {
    background-color: $card_bg;
    border: 1px solid $border;
    border-radius: 12px;
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: -2px;
    padding: 0 4px;
    color: $secondary_text;
    background-color: $window_bg;
}

/* ===================== Kaydirici ===================== */
QSlider::groove:horizontal {
    height: 6px;
    background: $track_bg;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: $accent;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: $view_bg;
    border: 1px solid $border_strong;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}
QSlider::handle:horizontal:hover {
    border-color: $accent;
}

/* ===================== Ilerleme cubugu ===================== */
QProgressBar {
    background-color: $track_bg;
    border: none;
    border-radius: 6px;
    min-height: 10px;
    max-height: 10px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: $accent;
    border-radius: 6px;
}

/* ===================== Ayirici ===================== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    background-color: $border;
    border: none;
    max-height: 1px;
}

/* ===================== Ipucu (Tooltip) ===================== */
QToolTip {
    background-color: $tooltip_bg;
    color: $tooltip_text;
    border: 1px solid $border_strong;
    border-radius: 6px;
    padding: 5px 9px;
}

/* ===================== Kaydirma alani (Splitter) ===================== */
QSplitter::handle {
    background-color: $border;
}
QSplitter::handle:horizontal {
    width: 1px;
}
QSplitter::handle:vertical {
    height: 1px;
}
""")


# ---------------------------------------------------------------------------
# Genel API
# ---------------------------------------------------------------------------

def build_stylesheet(dark: bool = False, overrides: dict[str, str] | None = None) -> str:
    """Verilen temaya (acik/koyu) gore tam QSS metnini uretir.

    overrides: paletteki belirli anahtarlari degistirmek icin (orn. farkli
    bir accent rengi kullanmak istersen) {"accent": "#9141ac"} gibi bir sozluk.
    """
    palette = dict(DARK_PALETTE if dark else LIGHT_PALETTE)
    if overrides:
        palette.update(overrides)
    return _QSS_TEMPLATE.substitute(palette)


def apply_theme(app, dark: bool = False, overrides: dict[str, str] | None = None) -> None:
    """QApplication (veya QWidget) uzerine temayi dogrudan uygular."""
    app.setStyleSheet(build_stylesheet(dark=dark, overrides=overrides))


def set_widget_class(widget, class_name: str) -> None:
    """Bir widget'a libadwaita-tarzi 'class' dynamic property'sini uygular
    ve stili yeniden degerlendirir (setProperty tek basina yeterli degildir).

    Ornek:
        set_widget_class(save_button, "suggested-action")
        set_widget_class(delete_button, "destructive-action")
        set_widget_class(some_label, "dim-label")
    """
    widget.setProperty("class", class_name)
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()

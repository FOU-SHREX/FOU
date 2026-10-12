import customtkinter as ctk
import threading
import tkinter as tk
import queue
import requests
import webbrowser
from datetime import datetime
from main import load_portfolio, get_portfolio_data, remove_coin_portfolio, save_portfolio, get_coin_list, add_coin_portfolio
from pathlib import Path
from PIL import Image, ImageOps, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageTk, ImageFont
from math import ceil
from io import BytesIO

app = ctk.CTk()

app.title("FOU")

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

BASE_WIDTH = 1280
BASE_HEIGHT = 760

ui_scale = min(
    screen_width / 1920,
    screen_height / 1080
)

ui_scale = max(
    0.85,
    min(ui_scale, 1.35)
)

window_width = min(
    int(BASE_WIDTH * ui_scale),
    int(screen_width * 0.90)
)

window_height = min(
    int(BASE_HEIGHT * ui_scale),
    int(screen_height * 0.88)
)

x= (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

app.geometry(f"{window_width}x{window_height}+{x}+{y}")

ctk.set_appearance_mode("dark")

ctk.set_widget_scaling(ui_scale)

app.grid_columnconfigure(0, weight= 1)
app.grid_rowconfigure(1, weight= 1)

portfolio = load_portfolio()

portfolio_queue = queue.Queue()
add_queue = queue.Queue()
last_rows = []
selected_symbol = None
last_updated_time = "--:--:--"
HELP_VIDEO_URL = "https://github.com/FOU-SHREX/FOU/blob/main/readme.md"

coin_logo_source_cache = {}
coin_logo_cache = {}
coin_logo_loading = set()
coin_logo_waiters = {}

UI_DIR = Path(__file__).resolve().parent / "assets" / "ui"
REACTION_DIR = Path(__file__).resolve().parent / "assets" / "reactions"
FOU_DEFAULT_UI_DIR = UI_DIR / "fou_default"
FOOL_UI_DIR = UI_DIR / "the_fool"
VOID_UI_DIR = UI_DIR / "void"

FOU_DEFAULT_BG_PATH = (
    FOU_DEFAULT_UI_DIR / "fou_default_bg.png"
)

FOOL_BG_PATH = (
    FOOL_UI_DIR / "the_fool_bg.png"
)

VOID_BG_PATH = (
    VOID_UI_DIR / "void_bg.png"
)

FOOL_COMPANION_FRAME_PATH = (
    FOOL_UI_DIR / "companion_frame.png"
)

FOOL_PORTFOLIO_FRAME_PATH = (
    FOOL_UI_DIR / "portfolio_frame.png"
)

VOID_PORTFOLIO_FRAME_PATH = (
    VOID_UI_DIR / "portfolio_frame.png"
)

VOID_COMPANION_FRAME_PATH = (
    VOID_UI_DIR / "companion_frame.png"
)

VOID_BUTTON_FRAME_PATH = (
    VOID_UI_DIR / "button_frame.png"
)

fool_companion_frame_pil = None
fool_portfolio_frame_pil = None
void_portfolio_frame_pil = None
void_companion_frame_pil = None
void_button_frame_pil = None

if FOOL_COMPANION_FRAME_PATH.exists():
    fool_companion_frame_pil = Image.open(
        FOOL_COMPANION_FRAME_PATH
    ).convert("RGBA")

if FOOL_PORTFOLIO_FRAME_PATH.exists():
    fool_portfolio_frame_pil = Image.open(
        FOOL_PORTFOLIO_FRAME_PATH
    ).convert("RGBA")

    alpha = fool_portfolio_frame_pil.getchannel("A")
    bounds = alpha.getbbox()

    if bounds is not None:
        fool_portfolio_frame_pil = (
            fool_portfolio_frame_pil.crop(bounds)
        )

if VOID_PORTFOLIO_FRAME_PATH.is_file():
    with Image.open(VOID_PORTFOLIO_FRAME_PATH) as source:
        void_portfolio_frame_pil = source.convert("RGBA")

    void_bounds = void_portfolio_frame_pil.getchannel("A").getbbox()

    if void_bounds is not None:
        void_portfolio_frame_pil = void_portfolio_frame_pil.crop(
            void_bounds
        )
    
    else:
        void_portfolio_frame_pil = None

if VOID_COMPANION_FRAME_PATH.is_file():
    with Image.open(VOID_COMPANION_FRAME_PATH) as source:
        void_companion_frame_pil = source.convert("RGBA")

    alpha = void_companion_frame_pil.getchannel("A")

    visible_alpha = alpha.point(
        lambda value: 255 if value >= 16 else 0
    )

    bounds = visible_alpha.getbbox()

    if bounds is not None:
        void_companion_frame_pil = (
            void_companion_frame_pil.crop(bounds)
        )
    
    else:
        void_companion_frame_pil = None
        print("[FOU] VOID Companion frame is empty.")

if VOID_BUTTON_FRAME_PATH.is_file():
    with Image.open(VOID_BUTTON_FRAME_PATH) as source:
        void_button_frame_pil = source.convert("RGBA")

    button_bounds = void_button_frame_pil.getchannel("A").getbbox()

    if button_bounds is not None:
        void_button_frame_pil = void_button_frame_pil.crop(
            button_bounds
        )
    
else:
    print(
        "[FOU] VOID Button frame not found:",
        VOID_BUTTON_FRAME_PATH
    )

title_icon_pil = Image.open(
    UI_DIR / "fou_logo.png"
).convert("RGBA")

ICON_PATH = UI_DIR / "fou_icon.ico"

if not ICON_PATH.exists():
    title_icon_pil.save(
        ICON_PATH,
        format= "ICO",
        sizes= [
            (16, 16),
            (32, 32),
            (48, 48),
            (64, 64)
        ]
    )

app.after(
    250,
    lambda: app.iconbitmap(str(ICON_PATH))
)

reaction_image_cache = {}

current_reaction_state = "idle"

REACTION_WIDTH = 470
REACTION_HEIGHT = 560

current_reaction_width = REACTION_WIDTH
current_reaction_height = REACTION_HEIGHT

responsive_job = None
reaction_render_job = None


REACTION_THEME_DIRS = {
    "FOU DEFAULT": "fou_default",
    "THE FOOL": "the_fool",
    "VOID": "void",
    "TERMINAL": "terminal",
    "FROST": "frost",
    "NEON": "neon"
}

COMPANION_NAMES = {
    "FOU DEFAULT": "FOU",
    "THE FOOL": "MR. FOOL",
    "VOID": "NØXAR",
    "TERMINAL": "NULL-7",
    "FROST": "CRYØN",
    "NEON": "VYREX"
}

THEME_NAMES = [
    "FOU DEFAULT",
    "THE FOOL",
    "VOID"
]

THEMES = {
    "FOU DEFAULT": {
        "app_bg": "#080B0F",
        "panel_bg": "#101317",
        "row_bg": "#101316",
        "text": "#F5F4F1",
        "muted_text": "#C6C5CC",
        "accent": "#EAE4DA",
        "border": "#484D53",
        "card_border": "#363C42",
        "row_separator": "#292E33",
        "button_bg": "#0D1013",
        "button_hover": "#1B1F23",
        "entry_bg": "#0C0F12",
        "entry_border": "#62656A",
        "selected_row_bg": "#282928",
        "selected_border": "#66686B",
        "reaction_bg": "transparent",
        "coin_logo_mode": "theme",
        "coin_logo_color": "#F2E8D5",
        "coin_logo_dark_color": "#5E5A54",
        "status_divider": "#555A60",
        "scrollbar_track": "#101317",
        "scrollbar_thumb": "#B9B2A8",
        "scrollbar_hover": "#EAE4DA"
    },

    "THE FOOL": {
        "app_bg": "#070A0B",
        "panel_bg": "#090D0E",
        "row_bg": "#090D0E",

        "text": "#F2EADB",
        "muted_text": "#B8B5B0",
        "numeric_text": "#F0F0ED",

        "accent": "#C49B60",
        "accent_highlight": "#E8C998",
        "accent_shadow": "#705332",

        "border": "#AA8754",
        "card_border": "#B8955F",
        "row_separator": "#343737",

        "button_bg": "#090B0B",
        "button_hover": "#18130D",

        "entry_bg": "#080C0D",
        "entry_border": "#77716A",

        "selected_row_bg": "#2A2825",
        "selected_border": "#A78C61",
        "selected_strip": "#D7AE75",

        "status_dot": "#E5CBA5",
        "status_divider": "#9B7D4D",

        "reaction_bg": "#070A0B",

        "coin_logo_mode": "theme",
        "coin_logo_color": "#E8D7B9",
        "coin_logo_dark_color": "#8D7858",

        "scrollbar_track": "#181613",
        "scrollbar_thumb": "#D7AC74",
        "scrollbar_hover": "#E8C998",

        "parchment_bg": "#EBD8B7",
        "parchment_highlight": "#F5E8D1",
        "parchment_shadow": "#D4BE99",
        "parchment_text": "#100D09",

        "deep_red": "#4A2020"

    },

    "VOID": {
        "app_bg": "#08070C",
        "panel_bg": "#100F14",
        "row_bg": "#121116",

        "text": "#E9E4EC",
        "muted_text": "#ADA3B8",

        "accent": "#C0ABD8",
        "accent_highlight": "#DCCCF3",

        "border": "#746586",
        "card_border": "#51475D",
        "row_separator": "#34303C",

        "button_bg": "#121019",
        "button_hover": "#261D31",

        "entry_bg": "#0D0B12",
        "entry_border": "#746586",

        "selected_row_bg": "#2A2332",
        "selected_border": "#A18BB7",
        "selected_strip": "#D2B5F2",

        "status_dot": "#D2B5F2",
        "status_divider": "#6E5D84",

        "reaction_bg": "#0B0A10",

        "coin_logo_mode": "theme",
        "coin_logo_color": "#D8C6ED",
        "coin_logo_dark_color": "#685A78",

        "scrollbar_track": "#14111A",
        "scrollbar_thumb": "#B89DD4",
        "scrollbar_hover": "#D9C4F1"
    }
}


def create_database_icon(color, size= (18, 18)):
    scale = 4

    image = Image.new(
        "RGBA",
        (20 * scale, 20 * scale),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)
    stroke = scale

    draw.ellipse(
        (3 * scale, 2 * scale, 17 * scale, 8 * scale),
        outline= color,
        width= stroke
    )

    for x in (3, 17):
        draw.line(
            (x * scale, 5 * scale, x * scale, 15 * scale),
            fill= color,
            width= stroke
        )

    draw.arc(
        (3 * scale, 7 * scale, 17 * scale, 13 * scale),
        start= 0,
        end= 180,
        fill= color,
        width= stroke
    )

    draw.arc(
        (3 * scale, 12 * scale, 17 * scale, 18 * scale),
        start= 0,
        end= 180,
        fill= color,
        width= stroke
    )

    image = image.resize(
        size,
        Image.Resampling.LANCZOS
    )

    return ctk.CTkImage(
        light_image= image,
        dark_image= image,
        size= size
    )


def create_search_icon(color, size= (18, 18)):
    scale= 4

    large_size = (
        size[0] * scale,
        size[1] * scale
    )

    image = Image.new(
        "RGBA",
        large_size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    draw.ellipse(
        (
            2 * scale,
            2 * scale,
            11 * scale,
            11 * scale
        ),
        outline= color,
        width= 2 * scale
    )

    draw.line(
        (
            10 * scale,
            10 * scale,
            16 * scale,
            16 * scale
        ),
        fill= color,
        width= 2 * scale
    )

    image = image.resize(
        size,
        Image.Resampling.LANCZOS
    )

    return ctk.CTkImage(
        light_image= image,
        dark_image= image,
        size= size
    )


def create_remove_icon(color, size= (18, 18)):
    scale = 4

    image = Image.new(
        "RGBA",
        (
            size[0] * scale,
            size[1] * scale
        ),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    padding = 4 * scale
    end = (size[0] - 4) * scale

    draw.line(
    (
        padding,
        padding,
        end,
        end
    ),
    fill= color,
    width= 2 * scale

    )

    draw.line(
        (
            end,
            padding,
            padding,
            end
        ),
        fill= color,
        width= 2 * scale
    )

    image = image.resize(
        size,
        Image.Resampling.LANCZOS
    )

    return ctk.CTkImage(
        light_image= image,
        dark_image= image,
        size= size
    )


def create_clock_icon(color, size=(20, 20)):
    scale = 4

    large_size = (
        size[0] * scale,
        size[1] * scale
    )

    image = Image.new(
        "RGBA",
        large_size,
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    center = 10 * scale

    draw.ellipse(
        (
            2 * scale,
            2 * scale,
            18 * scale,
            18 * scale
        ),
        outline= color,
        width= 2 * scale
    )

    draw.line(
        (
            center,
            center,
            center,
            5 * scale
        ),
        fill = color,
        width= 2 * scale
    )

    draw.line(
        (
            center,
            center,
            14 * scale,
            12 * scale
        ),
        fill = color,
        width= 2 * scale
    )

    image = image.resize(
        size,
        Image.Resampling.LANCZOS
    )

    return ctk.CTkImage(
        light_image= image,
        dark_image= image,
        size= size
    )


def create_activity_icon(state, circle_color, symbol_color, size= (32, 32)):
    scale = 4

    image = Image.new(
        "RGBA",
        (
            size[0] * scale,
            size[1] * scale
        ),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(image)

    draw.ellipse(
        (
            1 * scale,
            1 * scale,
            31 * scale,
            31 * scale
        ),
        fill = circle_color
    )

    if state == "loading":
        draw.arc(
            (
                8 * scale,
                8 * scale,
                24 * scale,
                24 * scale
            ),
            start= 30,
            end= 300,
            fill= symbol_color,
            width= 3 * scale
        )

    elif state in ("confused", "angry"):
        draw.line(
            (
                16 * scale,
                8 * scale,
                16 * scale,
                19 * scale
            ),
            fill= symbol_color,
            width= 3 * scale
        )

        draw.ellipse(
            (
                14 * scale,
                22 * scale,
                18 * scale,
                26 * scale
            ),
            fill= symbol_color
        )

    else:
        draw.line(
            (
                8 * scale,
                16 * scale,
                13 * scale,
                21 * scale
            ),
            fill = symbol_color,
            width= 3 * scale
        )

        draw.line(
            (
                13 * scale,
                21 * scale,
                24 * scale,
                10 * scale
            ),
            fill= symbol_color,
            width= 3 * scale
        )

    image = image.resize(
        size,
        Image.Resampling.LANCZOS
    )

    return ctk.CTkImage(
        light_image= image,
        dark_image= image,
        size= size
    )


def create_tinted_icon(path, color, size= (20, 20)):
    image = Image.open(path).convert("RGBA")

    alpha = image.getchannel("A")

    tinted = Image.new(
        "RGBA",
        image.size,
        color
    )

    tinted.putalpha(alpha)

    return ctk.CTkImage(
        light_image=tinted,
        dark_image= tinted,
        size= size
    )

current_theme = "FOU DEFAULT"

search_icon = create_search_icon(
    THEMES[current_theme]["muted_text"]
)

clock_icon = create_clock_icon(
    THEMES[current_theme]["muted_text"]
)

activity_status_icon = create_activity_icon(
    current_reaction_state,
    THEMES[current_theme]["accent"],
    THEMES[current_theme]["app_bg"]
)

refresh_icon = create_tinted_icon(
    UI_DIR / "refresh.png",
    THEMES[current_theme]["text"]
)

save_icon = create_tinted_icon(
    UI_DIR / "save.png",
    THEMES[current_theme]["text"]
)

background_pil = Image.open(
    FOU_DEFAULT_BG_PATH
)

background_image = ctk.CTkImage(
    light_image= background_pil,
    dark_image= background_pil,
    size= (
        int(window_width / ui_scale),
        int(window_height / ui_scale)
    )
)

logo_pil = Image.open(
    UI_DIR / "fou_logo.png"
).convert("RGBA")

logo_bbox = logo_pil.getbbox()

if logo_bbox:
    logo_pil = logo_pil.crop(logo_bbox)

logo_height = 56

logo_ratio = (
    logo_pil.width /
    logo_pil.height
)

logo_width = int(
    logo_height * logo_ratio
)

logo_image = ctk.CTkImage(
    light_image= logo_pil,
    dark_image= logo_pil,
    size= (logo_width, logo_height)
)

fool_logo_height = 64
fool_logo_width = int(
    fool_logo_height * logo_ratio
)

fool_logo_image = ctk.CTkImage(
    light_image= logo_pil,
    dark_image= logo_pil,
    size= (fool_logo_width, fool_logo_height)
)

background_label = ctk.CTkLabel(
    app,
    text = "",
    image= background_image
)

background_label.place(
    x= 0,
    y= 0,
    relwidth = 1,
    relheight = 1
)

background_label.lower()

header_frame = ctk.CTkFrame(
    app,
    fg_color= "transparent"
)
header_frame.grid(
    row= 0,
    column= 0,
    sticky= "ew",
    padx= 30,
    pady= (18, 10)
)

header_frame.grid_columnconfigure(0, weight= 1)

header_art_label = tk.Label(
    header_frame,
    bd= 0,
    highlightthickness= 0
)

brand_art_label = tk.Label(
    header_frame,
    bd= 0,
    highlightthickness= 0
)

brand_frame = ctk.CTkFrame(
    header_frame,
    fg_color= "transparent"
)
brand_frame.grid(
    row= 0,
    column= 0,
    sticky= "w",
    padx= 5,
    pady= 5
)

logo_label = ctk.CTkLabel(
    brand_frame,
    text= "",
    image= logo_image
)
logo_label.grid(
    row= 0,
    column= 0,
    padx= (0, 8)
)

header_lable = ctk.CTkLabel(
    brand_frame,
    text= "FOU",
    font= ("Segoe UI", 44, "bold")
)
header_lable.grid(
    row= 0,
    column= 1,
    sticky = "w",
    pady= 5
)

theme_card_pil = Image.new(
    "RGBA",
    (64, 64),
    (0, 0, 0, 0)
)

theme_card_draw = ImageDraw.Draw(theme_card_pil)

theme_card_draw.rounded_rectangle(
    (9, 16, 43, 57),
    radius= 4,
    outline= "#E8C998",
    width= 3
)

theme_card_draw.rounded_rectangle(
    (23, 8, 55, 49),
    radius= 4,
    outline= "#E8C998",
    width= 3
)

theme_card_icon = ctk.CTkImage(
    light_image = theme_card_pil,
    dark_image = theme_card_pil,
    size= (24, 24)
)

theme_selector_frame = ctk.CTkFrame(
    header_frame,
    fg_color = "transparent",
    corner_radius= 8,
    border_width= 0
)

theme_selector_frame.grid(
    row= 0,
    column= 1,
    padx= (10, 12),
    pady= 5
)

theme_card_label = ctk.CTkLabel(
    theme_selector_frame,
    text= "",
    image= theme_card_icon,
    width= 28,
    height= 38
)

theme_card_label.grid(
    row= 0,
    column= 0,
    padx= (10, 6),
    pady= 3
)

theme_prefix_label = ctk.CTkLabel(
    theme_selector_frame,
    text= "Theme:",
    font= ("Georgia", 15),
    text_color= "#E8C998"
)

theme_prefix_label.grid(
    row= 0,
    column= 1
)

theme_selector = ctk.CTkOptionMenu(
    theme_selector_frame,
    values= THEME_NAMES,
    width= 170,
    height= 38,
    corner_radius= 6,
    font= ("Segoe UI", 13)
)

theme_selector.set(current_theme)

theme_selector.grid(
    row= 0,
    column= 2
)

refresh_button = ctk.CTkButton(
    header_frame,
    text= "Refresh",
    image= refresh_icon,
    compound= "left",
    width= 145,
    height= 50,
    corner_radius= 9,
    border_width= 1,
    font= ("Consolas", 16)
)
refresh_button.grid(
    row= 0,
    column= 2,
    padx= (0, 10),
    pady= 5
)

refresh_button_art_label = tk.Label(
    header_frame,
    bd= 0,
    highlightthickness= 0
)

save_button = ctk.CTkButton(
    header_frame,
    text= "Save",
    image= save_icon,
    compound= "left",
    width= 130,
    height= 50,
    corner_radius= 9,
    border_width= 1,
    font= ("Consolas", 16)
)
save_button.grid(
    row= 0,
    column= 3,
    padx= (0, 5),
    pady= 5
)

content_frame = ctk.CTkFrame(
    app,
    fg_color= "transparent"
)
content_frame.grid(
    row= 1,
    column= 0,
    sticky= "nsew",
    padx= 20,
    pady= 10
)

content_frame.grid_rowconfigure(0, weight= 1)

content_frame.grid_columnconfigure(0, weight= 37)
content_frame.grid_columnconfigure(1, weight= 63)

activity_frame = ctk.CTkFrame(
    app,
    corner_radius= 10,
    border_width= 1,
    fg_color= "transparent"
)
activity_frame.grid(
    row= 2,
    column= 0,
    sticky= "ew",
    padx= 20,
    pady= (12, 10)
)

activity_frame.grid_columnconfigure(2, weight= 1)

activity_title = ctk.CTkLabel(
    activity_frame,
    text= "A C T I V I T Y",
    font= ("Segoe UI", 11, "bold")
)
activity_title.grid(
    row= 0,
    column= 0,
    padx= (20, 14),
    pady= 12
)

activity_icon = ctk.CTkLabel(
    activity_frame,
    text= "",
    image= activity_status_icon,
    width= 32,
    height= 32,
    fg_color= "transparent"
)
activity_icon.grid(
    row= 0,
    column= 1,
    padx= (0, 10)
)
activity_icon.grid_propagate(False)

activity_message = ctk.CTkLabel(
    activity_frame,
    text= "Standing by...",
    font= ("Segoe UI", 13)
)
activity_message.grid(
    row= 0,
    column= 2,
    sticky= "w"
)

activity_gold_top_line = tk.Frame(
    activity_frame,
    bg= "#AA8754",
    height= 1,
    bd= 0,
    highlightthickness= 0
)

activity_gold_bottom_line = tk.Frame(
    activity_frame,
    bg= "#AA8754",
    height= 1,
    bd= 0,
    highlightthickness= 0
)

activity_gold_ornament = tk.Label(
    activity_frame,
    text= "✦",
    font= ("Georgia", 11),
    fg= "#E8C998",
    bg= "#090B0B",
    bd= 0,
    highlightthickness= 0
)

footer_frame = ctk.CTkFrame(
    app,
    fg_color= "transparent",
    corner_radius= 0
)
footer_frame.grid(
    row= 3,
    column= 0,
    sticky= "ew",
    padx= 30,
    pady= (0, 10)
)
footer_frame.grid_columnconfigure(
    1,
    weight= 1
)

database_icon = create_database_icon(
    THEMES[current_theme].get(
        "accent_highlight",
        THEMES[current_theme]["accent"]
    ),
    size= (18, 18)
)

save_local_label = ctk.CTkLabel(
    footer_frame,
    text= "  Saved locally",
    image= database_icon,
    compound= "left",
    font= ("Consolas", 12),
    text_color= THEMES[current_theme]["muted_text"]
)
save_local_label.grid(
    row= 0,
    column= 0,
    sticky= "w"
)

help_button = ctk.CTkButton(
    footer_frame,
    text= "▶  Help",
    width= 88,
    height= 30,
    corner_radius= 7,
    border_width= 1,
    fg_color= "transparent",
    hover_color= THEMES[current_theme]["button_hover"],
    border_color= THEMES[current_theme]["border"],
    text_color= THEMES[current_theme]["text"],
    font= ("Consolas", 12)
)

help_button.grid(
    row= 0,
    column= 2,
    sticky= "e"
)

preview_frame = ctk.CTkFrame(
    content_frame,
    corner_radius= 12,
    border_width= 1,
    fg_color= THEMES[current_theme]["reaction_bg"],
    border_color= THEMES[current_theme]["card_border"]
)
preview_frame.grid(
    row= 0,
    column= 0,
    sticky= "nsew",
    padx= (0, 5)
)

preview_frame.grid_columnconfigure(0, weight= 1)
preview_frame.grid_rowconfigure(1, weight= 1)

void_companion_border_canvas = tk.Canvas(
    preview_frame,
    width= 1,
    height= 1,
    bd= 0,
    highlightthickness= 0,
    takefocus= 0,
    bg= THEMES["VOID"]["reaction_bg"]
)

void_companion_border_item = (
    void_companion_border_canvas.create_image(
        0,
        0,
        anchor= "nw"
    )
)

preview_inner = ctk.CTkFrame(
    preview_frame,
    fg_color= "transparent",
    corner_radius = 11
)
preview_inner.pack(
    fill= "both",
    expand= True,
    padx= 0,
    pady= 0
)

preview_inner.grid_columnconfigure(0, weight= 1)
preview_inner.grid_columnconfigure(1, weight= 0)

preview_inner.grid_rowconfigure(0, weight= 0)
preview_inner.grid_rowconfigure(1, weight= 1)

portfolio_frame = ctk.CTkFrame(
    content_frame,
    corner_radius= 12,
    border_width= 1
)
portfolio_frame.grid(
    row= 0,
    column= 1,
    sticky= "nsew",
    padx= (5, 0)
)

portfolio_frame.grid_columnconfigure(0, weight= 1)
portfolio_frame.grid_rowconfigure(3, weight= 1)

portfolio_border_canvas = tk.Canvas(
    portfolio_frame,
    width= 1,
    height= 1,
    highlightthickness= 0,
    borderwidth= 0,
    takefocus= 0,
    bg= THEMES[current_theme]["panel_bg"]
)

portfolio_border_item = portfolio_border_canvas.create_image(
    0,
    0,
    anchor= "nw"
)

reaction_stage = ctk.CTkFrame(
    preview_inner,
    fg_color= "transparent",
    corner_radius= 0
)
reaction_stage.grid(
    row= 1,
    column= 0,
    columnspan= 2,
    sticky= "nsew",
    padx= 6,
    pady= (0, 6)
)

companion_header = ctk.CTkFrame(
    preview_inner,
    fg_color= "transparent",
    corner_radius= 6,
    border_width= 0
)
companion_header.grid(
    row= 0,
    column= 0,
    columnspan= 2,
    sticky= "ew",
    padx= 8,
    pady= (5, 4)
)

companion_header.grid_columnconfigure(0, weight= 1)

reaction_title = ctk.CTkLabel(
    companion_header,
    text= "C O M P A N I O N",
    font= ("Segoe UI", 11, "bold"),
    text_color= THEMES[current_theme]["muted_text"]
)
reaction_title.grid(
    row= 0,
    column= 0,
    sticky= "w",
    padx= (8, 0),
    pady= (4, 3)
)

reaction_state_label = ctk.CTkLabel(
    companion_header,
    text= "●  Idle",
    font= ("Segoe UI", 13),
    text_color= THEMES[current_theme]["muted_text"],
    fg_color= "transparent",
    width= 78,
    height= 30,
    corner_radius= 13,
    border_width= 0
)
reaction_state_label.grid(
    row= 0,
    column= 1,
    sticky= "e",
    padx= (8, 14),
    pady= 3
)

reaction_image = ctk.CTkLabel(
    reaction_stage,
    text= "",
    width= REACTION_WIDTH,
    height= REACTION_HEIGHT,
    fg_color= "transparent"
)
reaction_image.place(
    relx= 0.5,
    rely= 0.5,
    anchor= "center"
)

portfolio_header = ctk.CTkFrame(
    portfolio_frame,
    fg_color= "transparent"
)
portfolio_header.grid(
    row= 0,
    column= 0,
    sticky= "ew",
    padx= 20,
    pady= (16, 8)
)

portfolio_header.grid_columnconfigure(2, weight= 1)

portfolio_title = ctk.CTkLabel(
    portfolio_header,
    text= "Portfolio",
    font= ("Segoe UI", 28, "bold")
)
portfolio_title.grid(
    row= 0,
    column= 0,
    sticky= "w",
)

coin_count_badge = ctk.CTkFrame(
    portfolio_header,
    width= 86,
    height= 34,
    fg_color= "transparent",
    corner_radius= 17,
    border_width= 1
)
coin_count_badge.grid(
    row= 0,
    column= 1,
    padx= (12, 0)
)
coin_count_badge.grid_propagate(False)

coin_count = ctk.CTkLabel(
    coin_count_badge,
    text= "0 coins",
    font= ("Segoe UI", 11),
    height= 26
)
coin_count.place(
    relx= 0.5,
    rely= 0.5,
    anchor= "center"
)

currency_badge = ctk.CTkFrame(
    portfolio_header,
    width= 64,
    height= 34,
    fg_color= "transparent",
    corner_radius= 17,
    border_width= 1
)
currency_badge.grid(
    row= 0,
    column= 3
)

currency_badge.grid_propagate(False)

currency_label = ctk.CTkLabel(
    currency_badge,
    text= "USD",
    font= ("Segoe UI", 12),
    height= 26
)
currency_label.place(
    relx= 0.5,
    rely= 0.5,
    anchor= "center"
)

search_frame = ctk.CTkFrame(
    portfolio_frame,
    fg_color= "transparent"
)
search_frame.grid(
    row= 1,
    column= 0,
    sticky= "ew",
    padx= 20,
    pady= 10
)

search_frame.grid_columnconfigure(0, weight= 1)

search_box = ctk.CTkFrame(
    search_frame,
    height= 44,
    fg_color= "transparent",
    corner_radius= 0
)
search_box.grid(
    row= 0,
    column= 0,
    sticky= "ew",
    padx= (0, 10)
)
search_box.grid_propagate(False)

coin_entry = ctk.CTkEntry(
    search_box,
    placeholder_text= "Enter symbol, e.g. BTC",
    height= 44,
    corner_radius= 9,
    border_width= 2,
    fg_color= THEMES[current_theme]["entry_bg"],
    border_color= THEMES[current_theme]["entry_border"],
    font= ("Segoe UI", 14)
)
coin_entry.place(
    x= 0,
    y= 0,
    relwidth= 1,
    relheight= 1
)
coin_entry._entry.grid_configure(
    padx= (42, 10)
)

search_icon_label = ctk.CTkLabel(
    search_box,
    text= "",
    image= search_icon,
    width= 24,
    height= 24,
    fg_color= THEMES[current_theme]["entry_bg"]
)
search_icon_label.place(
    x= 10,
    rely= 0.5,
    anchor= "w"
)
search_icon_label.lift()

search_icon_label.bind(
    "<Button-1>",
    lambda event: coin_entry.focus_set()
)

add_button = ctk.CTkButton(
    search_frame,
    text= "+ Add Coin",
    width = 130,
    height= 44,
    corner_radius= 8,
    font= ("Segoe UI", 14, "bold")
)
add_button.grid(
    row= 0,
    column= 1
)

column_header = ctk.CTkFrame(
    portfolio_frame,
    fg_color= "transparent"
)
column_header.grid(
    row= 2,
    column= 0,
    sticky= "ew",
    padx= 20,
    pady= (10, 5)
)

column_header.grid_columnconfigure(0, weight= 1)

asset_label = ctk.CTkLabel(
    column_header,
    text= "ASSET"
)
asset_label.grid(
    row= 0,
    column= 0,
    sticky= "w"
)

price_label = ctk.CTkLabel(
    column_header,
    text= "PRICE (USD)"
)
price_label.grid(
    row= 0,
    column= 1,
    padx= (10, 40)
)

rows_frame = ctk.CTkScrollableFrame(
    portfolio_frame,
    fg_color= THEMES[current_theme]["panel_bg"],
    scrollbar_fg_color= THEMES[current_theme]["scrollbar_track"],
    scrollbar_button_color= THEMES[current_theme]["scrollbar_thumb"],
    scrollbar_button_hover_color= THEMES[current_theme]["scrollbar_hover"]
)
rows_frame._scrollbar.configure(
    width= 18,
    corner_radius= 10,
    border_spacing= 2
)
rows_frame.grid(
    row= 3,
    column= 0,
    sticky= "nsew",
    padx= 20,
    pady= (5, 0)
)

rows_frame.grid_columnconfigure(0, weight= 1)

portfolio_status_frame = ctk.CTkFrame(
    portfolio_frame,
    fg_color= "transparent",
    corner_radius= 0
)
portfolio_status_frame.grid(
    row= 4,
    column= 0,
    sticky= "ew",
    padx= 20,
    pady= (0, 10)
)
portfolio_status_frame.grid_columnconfigure(0, weight= 1)
portfolio_status_frame.grid_columnconfigure(2, weight= 1)

portfolio_status_separator = ctk.CTkFrame(
    portfolio_status_frame,
    height= 1,
    corner_radius= 0,
    fg_color= THEMES[current_theme]["border"]
)
portfolio_status_separator.grid(
    row= 0,
    column= 0,
    columnspan= 3,
    sticky= "ew"
)

updated_label = ctk.CTkLabel(
    portfolio_status_frame,
    text= "  Updated --:--:--",
    image= clock_icon,
    compound= "left",
    font= ("Consolas", 14),
    text_color= THEMES[current_theme]["muted_text"]
)
updated_label.grid(
    row= 1,
    column= 0,
    sticky= "w",
    padx= (4, 15),
    pady= (10, 6)
)

portfolio_status_divider = ctk.CTkFrame(
    portfolio_status_frame,
    width= 2,
    height= 30,
    corner_radius= 0,
    fg_color= THEMES[current_theme].get(
        "status_divider",
        THEMES[current_theme]["border"]
    )
)
portfolio_status_divider.grid(
    row= 1,
    column= 1,
    padx= 15,
    pady= (8, 4)
)

selected_coin_label = ctk.CTkLabel(
    portfolio_status_frame,
    text= "No coin selected",
    font= ("Consolas", 14),
    text_color= THEMES[current_theme]["muted_text"]
)
selected_coin_label.grid(
    row= 1,
    column= 2,
    sticky= "e",
    padx= (15, 4),
    pady= (10, 6)
)

portfolio_status_ornament = ctk.CTkFrame(
    portfolio_status_frame,
    width= 176,
    height= 24,
    corner_radius= 0,
    fg_color= "transparent"
)

portfolio_status_ornament.grid(
    row= 1,
    column= 1,
    padx= 10,
    pady= (8, 4)
)

portfolio_status_ornament.grid_propagate(False)
portfolio_status_ornament.grid_columnconfigure(0, weight= 1)
portfolio_status_ornament.grid_columnconfigure(2, weight= 1)
portfolio_status_ornament.grid_rowconfigure(0, weight= 1)

portfolio_ornament_left = tk.Frame(
    portfolio_status_ornament,
    bg= "#9B7D4D",
    height= 1,
    bd= 0,
    highlightthickness= 0
)
portfolio_ornament_left.grid(
    row= 0,
    column= 0,
    sticky= "ew",
    padx= (0, 6)
)

portfolio_ornament_star = ctk.CTkLabel(
    portfolio_status_ornament,
    text= "✦",
    font= ("Georgia", 14),
    text_color= "#E8C998",
    width= 20,
    height= 22
)
portfolio_ornament_star.grid(
    row= 0,
    column= 1
)

portfolio_ornament_right = tk.Frame(
    portfolio_status_ornament,
    bg= "#9B7D4D",
    height= 1,
    bd= 0,
    highlightthickness= 0
)

portfolio_ornament_right.grid(
    row= 0,
    column= 2,
    sticky= "ew",
    padx= (6, 0)
)

portfolio_status_ornament.grid_remove()

def update_portfolio_status():
    updated_label.configure(
        text= f"  Updated {last_updated_time}"
    )

    if selected_symbol:
        selected_coin_label.configure(
            text= f"{selected_symbol} selected"
        )

    else:
        selected_coin_label.configure(
            text= "No coin selected"
        )

def remove_coin_logo_background(image):
    image = image.convert("RGBA")

    width, height = image.size

    if width < 3 or height < 3:
        return image

    border_pixels = []

    for x in range(width):
        border_pixels.append(
            image.getpixel((x, 0))
        )

        border_pixels.append(
            image.getpixel((x, height - 1))
        )

    for y in range(1, height -1):
        border_pixels.append(
            image.getpixel((0, y))
        )

        border_pixels.append(
            image.getpixel((width - 1, y))
        )
    
    opaque_border = [
        pixel
        for pixel in border_pixels
        if pixel[3] >= 180
    ]

    if len(opaque_border) < len(border_pixels) * 0.25:
        return image

    color_groups = {}

    for r, g, b, a in opaque_border:
        key= (
            r // 16,
            g // 16,
            b // 16
        )

        color_groups.setdefault(
            key,
            []
        ).append(
            (r, g, b)
        )

    largest_group = max(
        color_groups.values(),
        key= len
    )

    if len(largest_group) < len(opaque_border) * 0.45:
        return image

    bg_r = sum(
        pixel[0]
        for pixel in largest_group
    ) // len(largest_group)

    bg_g = sum(
        pixel[1]
        for pixel in largest_group
    ) // len(largest_group)

    bg_b = sum(
        pixel[2]
        for pixel in largest_group
    ) // len(largest_group)

    cleaned_pixels = []

    for r, g, b, a in image.get_flattened_data():

        if a == 0:
            cleaned_pixels.append(
                (r, g, b, 0)
            )
            continue

        difference = max(
            abs(r - bg_r),
            abs(g - bg_g),
            abs(b - bg_b)
        )

        if difference <= 24:
            new_alpha = 0

        elif difference < 60:
            fade = (
                difference - 24
            ) / (
                60 - 24
            )

            new_alpha = int(
                a * fade
            )

        else:
            new_alpha = a
        
        cleaned_pixels.append(
            (
                r,
                g,
                b,
                new_alpha
            )
        )

    cleaned_image = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0)
    )

    cleaned_image.putdata(
        cleaned_pixels
    )

    return cleaned_image
     

def normalize_coin_logo(image):
    image = image.convert("RGBA")

    alpha = image.getchannel("A")
    bounds = alpha.getbbox()

    if bounds is not None:
        image = image.crop(bounds)

    image= remove_coin_logo_background(image)

    alpha = image.getchannel("A")
    bounds = alpha.getbbox()

    if bounds is not None:
        image = image.crop(bounds)

    image = ImageOps.contain(
        image,
        (38, 38),
        method= Image.Resampling.LANCZOS
    )

    corners = [
        image.getpixel((0, 0))[3],
        image.getpixel((image.width - 1, 0))[3],
        image.getpixel((0, image.height - 1))[3],
        image.getpixel((image.width - 1, image.height - 1))[3]
    ]

    if all(alpha >= 230 for alpha in corners):
        circle_mask = Image.new(
            "L",
            image.size,
            0
        )

        draw = ImageDraw.Draw(circle_mask)

        draw.ellipse(
            (0, 0, image.width - 1, image.height - 1),
            fill = 255
        )

        original_alpha = image.getchannel("A")

        image.putalpha(
            ImageChops.multiply(original_alpha, circle_mask)
        )

    canvas = Image.new(
        "RGBA",
        (40, 40),
        (0, 0, 0, 0)
    )

    x = (40 - image.width) // 2
    
    y = (40 - image.height) // 2

    canvas.alpha_composite(
        image,
        (x, y)
    )

    return canvas


def tint_coin_logo(image, color, dark_color):
    rgba = image.convert("RGBA")

    alpha = rgba.getchannel("A")

    greyscale = ImageOps.grayscale(rgba)

    visible_pixels = [
        grey
        for grey, alpha_value
        in zip(
            greyscale.get_flattened_data(),
            alpha.get_flattened_data()
        )
        if alpha_value >= 80
    ]

    if visible_pixels:
        average_brightness = (
            sum(visible_pixels)
            / len(visible_pixels)
        )

    else:
        average_brightness = 128

    greyscale = ImageOps.autocontrast(
        greyscale
    )

    if average_brightness > 145:
        greyscale = ImageOps.invert(
            greyscale
        )

    tinted = ImageOps.colorize(
        greyscale,
        black= dark_color,
        white= color
    ).convert("RGBA")

    tinted.putalpha(alpha)

    return tinted


def build_coin_logo(image, theme_name):
    theme = THEMES[theme_name]

    if theme.get("coin_logo_mode", "original") == "theme":
        return tint_coin_logo(
            image,
            theme.get(
                "coin_logo_color",
                theme["text"]
            ),
            theme.get(
                "coin_logo_dark_color",
                theme["row_bg"]
            )
        )

    return image.copy()


def apply_coin_logo(image_url, source_image, logo_label, theme_name):
    cache_key = (
        image_url,
        theme_name
    )

    if cache_key not in coin_logo_cache:
        processed_image = build_coin_logo(
            source_image,
            theme_name
        )

        coin_logo_cache[cache_key] = ctk.CTkImage(
            light_image= processed_image,
            dark_image= processed_image,
            size= (44, 44)
        )

    if logo_label.winfo_exists():
        logo_label.configure(
            image= coin_logo_cache[cache_key],
            text= ""
        )


def finish_coin_logo_download(image_url, source_image):
    coin_logo_source_cache[image_url] = source_image

    coin_logo_loading.discard(
        image_url
    )

    waiting_label = coin_logo_waiters.pop(
        image_url,
        []
    )

    for logo_label, theme_name in waiting_label:
        apply_coin_logo(
            image_url,
            source_image,
            logo_label,
            theme_name
        )


def request_coin_logo(image_url, logo_label):
    if not image_url:
        return

    theme_name = current_theme

    cache_key = (
        image_url,
        theme_name
    )

    if cache_key in coin_logo_cache:
        logo_label.configure(
            image= coin_logo_cache[cache_key],
            text = ""
        )
        return
    
    if image_url in coin_logo_source_cache:
        apply_coin_logo(
            image_url,
            coin_logo_source_cache[image_url],
            logo_label,
            theme_name
        )
        return

    coin_logo_waiters.setdefault(
        image_url,
        []
    ).append(
        (
            logo_label,
            theme_name
        )
    )

    if image_url in coin_logo_loading:
        return

    coin_logo_loading.add(
        image_url
    )

    def worker():
        try:
            response = requests.get(
                image_url,
                timeout= 10
            )

            response.raise_for_status()

            downloaded_image = Image.open(
                BytesIO(response.content)
            ).convert("RGBA")

            normalize_image = normalize_coin_logo(
                downloaded_image
            )

            app.after(
                0,
                lambda: finish_coin_logo_download(
                    image_url,
                    normalize_image
                )
            )

        except Exception:
            coin_logo_loading.discard(
                image_url
            )

            coin_logo_waiters.pop(
                image_url,
                None
            )

    threading.Thread(
        target= worker,
        daemon= True
    ).start()


def create_coin_row(row_number, symbol, name, price_text, image_url, multiplier_text= ""):
    theme = THEMES[current_theme]

    is_selected = symbol == selected_symbol

    row_color = (
        theme["selected_row_bg"]
        if is_selected
        else theme["row_bg"]
    )
    
    coin_row = ctk.CTkFrame(
        rows_frame,
        corner_radius= 8,
        fg_color= row_color,
        border_width=1 if is_selected else 0,
        border_color= theme["selected_border"]
        )
    coin_row.grid(
        row= row_number * 2,
        column= 0,
        sticky= "ew",
        pady= 0
    )

    if is_selected:
        selection_strip = ctk.CTkFrame(
            coin_row,
            width= 4,
            corner_radius= 2,
            fg_color= theme.get("selected_strip", theme["accent"])
        )

        selection_strip.place(
            x= 2,
            rely= 0.10,
            relheight= 0.80
        )

        bind_coin_selector(
            selection_strip,
            symbol,
            name
        )

    coin_row.grid_columnconfigure(2, weight= 1)

    indicator = ctk.CTkLabel(
        coin_row,
        text= "●",
        width= 20,
        text_color= theme["accent"],
        font= ("Segoe UI", 16)
    )
    indicator.grid(
        row= 0,
        column= 0,
        sticky = "n",
        padx =(8, 3),
        pady= (9, 0)
    )

    logo_frame = ctk.CTkFrame(
        coin_row,
        width= 50,
        height= 50,
        corner_radius= 25,
        fg_color= "transparent",
        border_width= 1,
        border_color= theme["border"]
    )
    logo_frame.grid(
        row= 0,
        column= 1,
        padx= (3, 10),
        pady= 7
    )

    logo_frame.grid_propagate(False)

    logo_label = ctk.CTkLabel(
        logo_frame,
        text= symbol[:1],
        width= 44,
        height= 44,
        font= ("Segoe UI", 16, "bold"),
        text_color= theme["text"]
    )
    logo_label.place(
        relx= 0.5,
        rely= 0.5,
        anchor= "center"
    )

    request_coin_logo(
        image_url,
        logo_label
    )

    asset_info = ctk.CTkFrame(
        coin_row,
        fg_color= "transparent"
    )
    asset_info.grid(
        row= 0,
        column= 2,
        sticky= "w",
        padx= (0, 5),
        pady= 5
    )

    symbol_label = ctk.CTkLabel(
        asset_info,
        text= symbol,
        font= ("Consolas", 19, "bold"),
        height= 22,
        text_color= theme["text"]
    )
    symbol_label.grid(
        row= 0,
        column= 0,
        sticky= "w"
    )

    if multiplier_text:
    
        multiplier_label = ctk.CTkLabel(
            asset_info,
            text= multiplier_text,
            font= ("Consolas", 12, "bold"),
            height= 22,
            text_color= theme["muted_text"]
        )

        multiplier_label.grid(
            row= 0,
            column= 1,
            sticky= "w",
            padx= (6, 0)
        )

        bind_coin_selector(multiplier_label, symbol, name)

    name_label = ctk.CTkLabel(
        asset_info,
        text= name,
        font= ("Consolas", 12),
        height= 16,
        text_color= theme["muted_text"]
    )
    name_label.grid(
        row= 1,
        column= 0,
        sticky = "w"
    )

    price = ctk.CTkLabel(
        coin_row,
        text= price_text,
        font= ("Consolas", 20),
        text_color= theme["text"]
    )
    price.grid(
        row= 0,
        column= 3,
        sticky= "e",
        padx= 15
    )

    remove_icon = create_remove_icon(
        theme["text"],
        size= (18, 18)
    )

    remove_button = ctk.CTkButton(
        coin_row,
        text= "",
        image= remove_icon,
        width= 44,
        height= 44,
        corner_radius= 9,
        border_width= 1,
        fg_color= "transparent",
        hover_color= theme["button_hover"],
        border_color= theme["border"],
        command= lambda: remove_coin_gui(symbol)
    )
    remove_button.grid(
        row= 0,
        column= 4,
        padx= (5, 10)
    )

    if not is_selected:
        separator = tk.Frame(
            rows_frame,
            bg= theme.get(
                "row_separator",
                theme["border"]
            ),
            height= 2,
            bd= 0,
        highlightthickness= 0
        )
        separator.grid(
            row= (row_number * 2) + 1,
            column= 0,
            sticky= "ew",
            padx= (12, 12)
        )

        separator.grid_propagate(False)

    bind_coin_selector(coin_row, symbol, name)
    bind_coin_selector(indicator, symbol, name)
    bind_coin_selector(logo_frame, symbol, name)
    bind_coin_selector(logo_label, symbol, name)
    bind_coin_selector(asset_info, symbol, name)
    bind_coin_selector(symbol_label, symbol, name)
    bind_coin_selector(name_label, symbol, name)
    bind_coin_selector(price, symbol, name)


def bind_coin_selector(widget, symbol, name):
    widget.bind(
        "<Button-1>",
        lambda event: select_coin(symbol, name)
    )


def force_rows_full_width():
    try:
        canvas_width = rows_frame._parent_canvas.winfo_width()

        if canvas_width > 1:
            rows_frame._parent_canvas.itemconfigure(
                rows_frame._create_window_id,
                width= canvas_width
            )

    except Exception:
        pass


def draw_coin_rows(rows):
    for widget in rows_frame.winfo_children():
        widget.destroy()

    for row_number, row in enumerate(rows):
        symbol, name, price_text, image_url, multiplier_text = row

        create_coin_row(
            row_number,
            symbol,
            name,
            price_text,
            image_url,
            multiplier_text
        )

    if rows:
        bottom_spacer = ctk.CTkFrame(
            rows_frame,
            height= 14,
            corner_radius= 0,
            fg_color= "transparent"
        )

        bottom_spacer.grid(
            row= len(rows) * 2,
            column= 0,
            sticky= "ew"
        )

    app.after(
        30,
        force_rows_full_width
    )


def get_reaction_image(state, target_width= None, target_height= None):
    theme_folder = REACTION_THEME_DIRS.get(current_theme)

    if theme_folder is None:
        return None
    
    if target_width is None:
        target_width = REACTION_WIDTH

    if target_height is None:
        target_height = REACTION_HEIGHT
    
    cache_key = (
        current_theme,
        state,
        target_width,
        target_height
    )

    if cache_key in reaction_image_cache:
        return reaction_image_cache[cache_key]

    image_path = REACTION_DIR / theme_folder / f"{state}.png"

    if not image_path.exists():
        return None

    pil_image = Image.open(image_path).convert("RGBA")

    background_color = THEMES[current_theme]["reaction_bg"]

    if background_color == "transparent":
        background_color = THEMES[current_theme]["app_bg"]

    padding_x = int(pil_image.width * 0.08)
    padding_y = int(pil_image.height * 0.08)

    padded_image = ImageOps.expand(
        pil_image,
        border= (
            padding_x,
            padding_y,
            padding_x,
            padding_y
        ),
        fill= background_color
    )

    if ( current_theme == "THE FOOL" and fool_companion_frame_pil is not None):

        frame_margin = max(
            14,
            int(
                min(
                    target_width,
                    target_height
                ) * 0.022
            )
        )

        inner_width = max(
            1,
            target_width - (frame_margin * 2)
        )

        inner_height = max(
            1,
            target_height - (frame_margin * 2)
        )

        reaction_fit = ImageOps.fit(
            padded_image,
            (
                inner_width,
                inner_height
            ),
            method= Image.Resampling.LANCZOS,
            centering= (0.5, 0.42)
        ).convert("RGBA")

        fitted_image = Image.new(
            "RGBA",
            (
                target_width,
                target_height
            ),
            background_color
        )

        fitted_image.alpha_composite(
            reaction_fit,
            (
                frame_margin,
                frame_margin
            )
        )

        frame_inset_x = max(
            4,
            int(target_width * 0.006)
        )

        frame_inset_y = max(
            12,
            int(target_height * 0.018)
        )

        frame_width = max(
            1,
            target_width - (frame_inset_x * 2)
        )

        frame_height = max(
            1,
            target_height - (frame_inset_y * 2)
        )

        frame_image = fool_companion_frame_pil.resize(
            (
                frame_width,
                frame_height
            ),
            Image.Resampling.LANCZOS
        )

        fitted_image.alpha_composite(
            frame_image,
            (
                frame_inset_x,
                frame_inset_y
            )
        )


    else:
        fitted_image = ImageOps.fit(
            padded_image,
            (
                target_width,
                target_height
            ),
            method= Image.Resampling.LANCZOS,
            centering= (0.5, 0.42)
        )

    image = ctk.CTkImage(
        light_image= fitted_image,
        dark_image= fitted_image,
        size= (
            fitted_image.width,
            fitted_image.height
        )
    )

    reaction_image_cache[cache_key] = image

    return image


def render_reaction():
    global current_reaction_width
    global current_reaction_height
    global reaction_render_job

    reaction_render_job = None

    if app.state() == "iconic":
        return
    
    stage_width = max(
        1,
        int(
            reaction_stage.winfo_width()
            / ui_scale
        )
    )

    stage_height = max(
        1,
        int(
            reaction_stage.winfo_height()
            / ui_scale
        )
    )

    if stage_width < 200 or stage_height < 250:
        return
    

    available_width = stage_width
    available_height = stage_height


    current_reaction_width = available_width
    current_reaction_height = available_height

    image = get_reaction_image(
        current_reaction_state,
        current_reaction_width,
        current_reaction_height
    )

    if image is None and current_theme == "VOID":
        image = get_reaction_image(
            "idle", current_reaction_width, current_reaction_height
        )

    if image is None:
        reaction_image.configure(
            image= None,
            text= ""
        )
        return
    
    reaction_image.configure(
        image= image,
        text= "",
        width= current_reaction_width,
        height= current_reaction_height
    )


def schedule_reaction_render(event= None):
    global reaction_render_job

    if reaction_render_job is not None:
        app.after_cancel(
            reaction_render_job
        )
    
    reaction_render_job = app.after(
        140,
        render_reaction
    )


portfolio_frame_render_job = None
portfolio_border_image = None
portfolio_border_geometry = None

void_companion_border_job = None
void_companion_border_image = None
void_companion_border_geometry = None


def render_void_companion_border():
    global void_companion_border_job
    global void_companion_border_image
    global void_companion_border_geometry

    void_companion_border_job = None

    if(current_theme != "VOID" or void_companion_frame_pil is None):
        return

    if app.state() == "iconic":
        return
    
    width = preview_frame.winfo_width()
    height = preview_frame.winfo_height()

    if width < 150 or height < 150:
        return
    
    geometry = (width, height)

    if geometry == void_companion_border_geometry:
        return

    border, _ = build_portfolio_border(
        width,
        height,
        source= void_companion_frame_pil
    )

    void_companion_border_image = ImageTk.PhotoImage(
        border,
        master= app
    )

    void_companion_border_canvas.configure(
        bg= THEMES["VOID"]["reaction_bg"]
    )

    void_companion_border_canvas.itemconfigure(
        void_companion_border_item,
        image= void_companion_border_image
    )

    void_companion_border_canvas.place(
        x= 0,
        y= 0,
        relwidth= 1,
        relheight= 1
    )

    tk.Misc.lower(
        void_companion_border_canvas,
        preview_inner
    )

    void_companion_border_geometry = geometry


def schedule_void_companion_border(event= None):
    global void_companion_border_job

    if void_companion_border_job is not None:
        app.after_cancel(void_companion_border_job)
        void_companion_border_job = None

    if(current_theme == "VOID" and void_companion_frame_pil is not None):
        
        void_companion_border_job = app.after(
            120,
            render_void_companion_border
        )


def hide_void_companion_border():
    global void_companion_border_job
    global void_companion_border_image
    global void_companion_border_geometry

    if void_companion_border_job is not None:
        app.after_cancel(void_companion_border_job)
        void_companion_border_job = None

    void_companion_border_canvas.place_forget()

    void_companion_border_canvas.itemconfigure(
        void_companion_border_item,
        image= ""
    )

    void_companion_border_image = None
    void_companion_border_geometry = None


def hide_portfolio_border():
    global portfolio_frame_render_job
    global portfolio_border_image
    global portfolio_border_geometry

    if portfolio_frame_render_job is not None:
        app.after_cancel(portfolio_frame_render_job)
        portfolio_frame_render_job = None
    
    portfolio_border_canvas.place_forget()
    portfolio_border_canvas.itemconfigure(portfolio_border_item, image= "")
    portfolio_border_image= None
    portfolio_border_geometry= None


def build_portfolio_border(width, height, ornament_scale= None, source= None):
    if source is None:
        source = fool_portfolio_frame_pil

    sw, sh = source.size

    xs = (0, round(sw * 0.08), round(sw * 0.44),
            round(sw * 0.57), round(sw * 0.92), sw)

    ys = (0, round(sh * 0.16), round(sh * 0.44),
            round(sh * 0.56), round(sh * 0.82), sh)

    scale = min(width / sw, height / sh)

    if ornament_scale is not None:
        scale = min(scale, ornament_scale)
    
    def destination_cuts(cuts, extent):
        middle = (cuts[3] - cuts[2]) * scale

        return (0, round(cuts[1] * scale),
                round((extent - middle) / 2),
                round((extent + middle) / 2),
                extent - round((cuts[5] - cuts[4]) * scale), extent)

    dx = destination_cuts(xs, width)
    dy = destination_cuts(ys, height)
    frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    for row in range(5):
        for column in range(5):
            tile_width = dx[column + 1] - dx[column]
            tile_height = dy[row + 1] - dy[row]
            if tile_width <= 0 or tile_height <= 0:
                continue

            tile = source.crop((xs[column], ys[row], xs[column + 1], ys[row + 1]))

            tile = tile.resize((tile_width, tile_height), Image.Resampling.LANCZOS)

            frame.alpha_composite(tile, (dx[column], dy[row]))

    alpha = frame.getchannel("A")
    top_ink = alpha.crop((dx[1], 0, dx[4], dy[1])).getbbox()
    bottom_ink = alpha.crop((dx[1], dy[4], dx[4], height)).getbbox()
    top = top_ink[3] if top_ink else 0
    bottom = height - (dy[4] + bottom_ink[1]) if bottom_ink else 0
    return frame, (dx[1], top, width - dx[4], bottom)


def get_frame_horizontal_rails(frame):

    width, height = frame.size
    alpha = frame.getchannel("A")
    left = alpha.crop((width // 4, 0, max(width // 4 + 1, width * 2 // 5), height))
    right = alpha.crop((width * 3 // 5, 0, max(width * 3 // 5 + 1, width * 3 // 4), height))
    profile = ImageChops.add(
        left.resize((1, height), Image.Resampling.BOX),
        right.resize((1, height), Image.Resampling.BOX), scale= 2
    ).tobytes()

    def rail_center(start, stop, fallback):
        peak = max(profile[start:stop], default= 0)

        if not peak:
            return fallback
        
        rows = [y for y in range(start, stop) if profile[y] >= peak * 0.8]
        return sum(y * profile[y] for y in rows) / sum(profile[y] for y in rows)

    return (rail_center(0, height // 2, 0), rail_center(height // 2, height, height - 1))


def get_portfolio_border_vertical_bounds(panel_height):

    panel_y = portfolio_frame.winfo_rooty()
    stage_top = reaction_stage.winfo_rooty() - panel_y
    stage_bottom = stage_top + reaction_stage.winfo_height() - 1
    top, bottom = stage_top, stage_bottom
    displayed = reaction_image.cget("image")

    if displayed is not None and fool_companion_frame_pil is not None:
        if fool_companion_frame_pil.getchannel("A").getbbox() is not None:
            rail_top, rail_bottom = get_frame_horizontal_rails(fool_companion_frame_pil)
            _, image_height = displayed.cget("size")
            photo_height = round(image_height * reaction_image._get_widget_scaling())
            label = reaction_image._label
            image_top = (label.winfo_rooty() - panel_y
                         + (label.winfo_height() - photo_height) / 2)

            inset = max(12, int(image_height * 0.018))
            frame_height = max(1, image_height - 2 * inset)
            
            pixel_scale = photo_height / image_height
            
            top = image_top + (inset + frame_height * (rail_top + 0.5) / fool_companion_frame_pil.height) * pixel_scale - 0.5

            bottom = image_top + (inset + frame_height * (rail_bottom + 0.5) / fool_companion_frame_pil.height) * pixel_scale - 0.5

            top = max(stage_top, top)
            bottom = min(stage_bottom, bottom)

    top = max(0, min(panel_height - 2, top))
    bottom = max(top + 1, min(panel_height - 1, bottom))
    return top, bottom


def fit_portfolio_border_to_rails(width, panel_height, top, bottom):

    sw, sh = fool_portfolio_frame_pil.size
    
    source_top, source_bottom = get_frame_horizontal_rails(fool_portfolio_frame_pil)
    
    span = bottom - top

    scale = min(width / sw, span / max(1, source_bottom - source_top),
                (top + 0.5) / (source_top + 0.5),
                (panel_height - 0.5 - bottom) / (sh - 0.5 - source_bottom))
    
    height = max(2, min(panel_height, round(
        span + 1 + (source_top + sh - 1 - source_bottom) * scale
    )))

    for attempt in range(3):
        frame, _ = build_portfolio_border(width, height, ornament_scale= scale)
        
        actual_top, actual_bottom = get_frame_horizontal_rails(frame)
        
        next_height = max(2, min(panel_height, round(
            height + span - (actual_bottom - actual_top)
        )))

        if next_height == height or attempt == 2:
            break
        
        height = next_height
    
    image_y = max(0, min(panel_height - height, round(top - actual_top)))
    
    return frame, image_y


def get_portfolio_content_box(frame, widget_scale):
    width, height = frame.size

    alpha = frame.getchannel("A")
    gap = max(1, ceil(8 * widget_scale))

    top_ink = alpha.crop((width // 4, 0, width * 3 // 4, height // 2)).getbbox()
    bottom_ink = alpha.crop((width // 4, height // 2, width * 3 // 4, height)).getbbox()
    top = min(height - 1, (top_ink[3] if top_ink else 0) + gap)
    bottom = max(top + 1, (height // 2 + bottom_ink[1] if bottom_ink else height) - gap)
    left_ink = alpha.crop((0, top, width // 2, bottom)).getbbox()
    right_ink = alpha.crop((width // 2, top, width, bottom)).getbbox()
    left = min(width - 1, (left_ink[2] if left_ink else 0) + gap)
    right = max(left + 1, (width // 2 + right_ink[0] if right_ink else width) - gap)
    return left, top, right, bottom


def render_portfolio_border():
    global portfolio_frame_render_job
    global portfolio_border_image
    global portfolio_border_geometry

    portfolio_frame_render_job = None

    is_fool = (
        current_theme == "THE FOOL"
        and  fool_portfolio_frame_pil is not None
    )

    is_void = (
        current_theme == "VOID"
        and void_portfolio_frame_pil is not None
    )

    if not (is_fool or is_void):
        hide_portfolio_border()
        return
    
    if app.state() == "iconic":
        return

    width = portfolio_frame.winfo_width()
    height = portfolio_frame.winfo_height()

    if (width < 2 or height < 2 or reaction_stage.winfo_height() < 2):
        return

    if is_fool:
        top, bottom = get_portfolio_border_vertical_bounds(height)
    
    else:
        top, bottom = 0, height - 1
    
    widget_scale = portfolio_frame._get_widget_scaling()

    geometry = (
        current_theme,
        width,
        height,
        top,
        bottom,
        widget_scale
    )

    if geometry == portfolio_border_geometry:
        return

    if is_fool:
        frame, image_y = fit_portfolio_border_to_rails(
            width,
            height,
            top,
            bottom
        )
    
    else:
        frame, _ = build_portfolio_border(
            width,
            height,
            source= void_portfolio_frame_pil
        ) 
        image_y = 0
    
    portfolio_border_image = ImageTk.PhotoImage(
        frame,
        master= app
    )

    portfolio_border_canvas.configure(
        bg= THEMES[current_theme]["panel_bg"]
    )

    portfolio_border_canvas.itemconfigure(
        portfolio_border_item,
        image= portfolio_border_image
    )

    portfolio_border_canvas.coords(
        portfolio_border_item,
        0,
        image_y
    )

    portfolio_border_canvas.place(
        x= 0,
        y= 0,
        relwidth= 1,
        relheight= 1
    )

    tk.Misc.lower(
        portfolio_border_canvas,
        portfolio_header
    )

    if is_fool:
        left, inner_top, right, inner_bottom = (
            get_portfolio_content_box(frame, widget_scale)
        )

        padx = (
            ceil(left / widget_scale),
            ceil((width - right) / widget_scale)
        )

        header_top = ceil(
            (image_y + inner_top) / widget_scale
        )

        status_bottom = ceil(
            (height - image_y - inner_bottom) / widget_scale
        )

    else:

        side_inset = max(42, round(width * 0.065))
        top_inset = max(42, round(height * 0.075))
        bottom_inset = max(35, round(height * 0.072))

        padx = (
            ceil(side_inset / widget_scale),
            ceil(side_inset / widget_scale)
        )

        header_top = ceil(top_inset / widget_scale)
        status_bottom = ceil(bottom_inset / widget_scale)

    portfolio_header.grid_configure(
        padx= padx,
        pady= (header_top, 8)
    )

    search_frame.grid_configure(
        padx= padx,
        pady= (0, 8)
    )

    column_header.grid_configure(
        padx= padx,
        pady= (0, 4)
    )

    rows_frame.grid(
        row= 3,
        column=0,
        sticky= "nsew",
        padx= padx,
        pady= (0, 0)
    )

    portfolio_status_frame.grid_configure(
        padx= padx,
        pady= (0, status_bottom)
    )

    portfolio_border_geometry = geometry


def schedule_portfolio_border_render(event= None):
    global portfolio_frame_render_job

    if portfolio_frame_render_job is not None:
        app.after_cancel(portfolio_frame_render_job)
        portfolio_frame_render_job = None
    
    if (
        (current_theme == "THE FOOL" and fool_portfolio_frame_pil is not None)
        or (current_theme == "VOID" and void_portfolio_frame_pil is not None)
    ):
        portfolio_frame_render_job = app.after(120, render_portfolio_border)


def set_reaction(state):
    global current_reaction_state

    current_reaction_state = state

    reaction_state_label.configure(
        text= f"●  {state.capitalize()}"
    )

    schedule_reaction_render()


def add_fool_outer_border(background):
    width, height = background.size

    if width < 300 or height < 300:
        return background

    overlay = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(overlay)

    margin = 4

    gold = (197, 154, 92, 235)
    soft_gold = (122, 89, 48, 160)
    highlight = (232, 195, 136, 235)

    draw.rounded_rectangle(
        (
            margin,
            margin,
            width - margin - 1,
            height - margin -1
        ),
        radius= 14,
        outline= gold,
        width= 1
    )

    draw.rounded_rectangle(
        (
            margin + 4,
            margin + 4,
            width - margin - 5,
            height - margin - 5
        ),
        radius= 12,
        outline= soft_gold,
        width= 1
    )

    for flip_x in (-1, 1):
        for flip_y in (1, -1):

            origin_x = margin if flip_x == 1 else width - margin - 1
            origin_y = margin if flip_y == 1 else height - margin - 1

            def point(dx, dy):
                return (
                    origin_x + dx * flip_x,
                    origin_y + dy * flip_y
                )

            draw.line(
                [
                    point(0, 30),
                    point(5, 21),
                    point(13, 13),
                    point(21, 5),
                    point(30, 0)
                ],
                fill= gold,
                width= 2
            )

            cx, cy = point(19, 19)

            draw.polygon(
                [
                    (cx, cy - 5),
                    (cx + 4, cy),
                    (cx, cy + 5),
                    (cx - 4, cy)
                ],
                fill= highlight
            )

    return Image.alpha_composite(
        background.convert("RGBA"),
        overlay
    ).convert("RGB")


def render_void_button_frame(widget, pad=8, background=None, fill=None, square=False):
    if current_theme != "VOID" or void_button_frame_pil is None:
        return

    parent = widget.master
    w, h = widget.winfo_width(), widget.winfo_height()

    if w < 2 or h < 2:
        return

    x = widget.winfo_rootx() - parent.winfo_rootx()
    y = widget.winfo_rooty() - parent.winfo_rooty()

    frame_w = w + 2 * pad
    frame_h = h + 2 * pad

    if background is None:
        layer = Image.new(
            "RGBA",
            (frame_w, frame_h),
            fill or THEMES["VOID"]["panel_bg"]
        )
    else:
        left = widget.winfo_rootx() - app.winfo_rootx() - pad
        top = widget.winfo_rooty() - app.winfo_rooty() - pad

        layer = background.crop(
            (left, top, left + frame_w, top + frame_h)
        ).convert("RGBA")

    if square:
        frame, _ = build_portfolio_border(
            frame_w, frame_h,
            source=void_button_frame_pil
        )
    else:
        frame = void_button_frame_pil.resize(
            (frame_w, frame_h),
            Image.Resampling.LANCZOS
        )

    layer.alpha_composite(frame)
    photo = ImageTk.PhotoImage(layer, master=app)

    label = getattr(widget, "_void_button_art", None)

    if label is None or not label.winfo_exists():
        label = tk.Label(parent, bd=0, highlightthickness=0)
        widget._void_button_art = label

    label.configure(image=photo)
    label.image = photo

    label.place(
        x=x-pad, y=y-pad,
        width=frame_w, height=frame_h
    )

    label.lift()
    widget.lift()


def apply_responsive_art():
    global background_image
    global responsive_job

    responsive_job = None

    if app.state() == "iconic":
        return

    window_w = max(
        app.winfo_width(),
        1
    )

    window_h = max(
        app.winfo_height(),
        1
    )

    fitted_background = ImageOps.fit(
        background_pil,
        (window_w, window_h),
        method= Image.Resampling.LANCZOS,
        centering= (0.5, 0.25)
    )

    background_image = ctk.CTkImage(
        light_image= fitted_background,
        dark_image= fitted_background,
        size= (
            max(
                1,
                int(window_w / ui_scale)
            ),
            max(
                1,
                int(window_h / ui_scale)
            )
        )
    )

    background_label.configure(
        image= background_image
    )

    for widget in (theme_selector_frame, save_button, add_button, help_button):
        label = getattr(widget, "_void_button_art", None)
        if label is not None:
            label.place_forget()

    refresh_button_art_label.place_forget()
    refresh_button_art_label.configure(image= "")
    refresh_button_art_label.image = None

    if current_theme == "THE FOOL":
        header_x = header_frame.winfo_x()
        header_y = header_frame.winfo_y()
        header_width = header_frame.winfo_width()
        header_height = header_frame.winfo_height()

        if header_width > 1 and header_height > 1:
            header_crop = fitted_background.crop(
                (
                    header_x,
                    header_y,
                    header_x + header_width,
                    header_y + header_height
                )
            )

            header_photo = ImageTk.PhotoImage(header_crop)

            header_art_label.configure(
                image= header_photo
            )

            header_art_label.image = header_photo

            header_art_label.place(
                x= 0, 
                y= 0,
                relwidth= 1,
                relheight= 1
            )

            header_art_label.lift()
            brand_frame.lift()

            brand_x = brand_frame.winfo_x()
            brand_y = brand_frame.winfo_y()
            brand_w = brand_frame.winfo_width()
            brand_h = brand_frame.winfo_height()

            if brand_w > 1 and brand_h > 1:

                brand_background = header_crop.crop(
                    (
                        brand_x,
                        brand_y,
                        brand_x + brand_w,
                        brand_y + brand_h
                    )
                ).convert("RGBA")

                gold_logo = logo_pil.resize(
                    (
                        max(1, int(fool_logo_width * ui_scale)),
                        max(1, int(fool_logo_height * ui_scale))
                    ),
                    Image.Resampling.LANCZOS
                )

                gold_layer = Image.new(
                    "RGBA",
                    gold_logo.size,
                    "#DDB578"
                )

                gold_layer.putalpha(gold_logo.getchannel("A"))

                logo_x = 5
                logo_y = (brand_h - gold_logo.height) // 2

                brand_background.alpha_composite(
                    gold_layer,
                    (logo_x, logo_y)
                )

                font_size = max(20, int(48 * ui_scale))

                try:
                    brand_font = ImageFont.truetype(
                        "C:/Windows/Fonts/georgiab.ttf",
                        font_size
                    )
                
                except OSError:
                    brand_font = ImageFont.load_default()
                
                draw = ImageDraw.Draw(brand_background)

                draw.text(
                    (
                        logo_x + gold_logo.width + int(8 * ui_scale),
                        brand_h // 2
                    ),
                    "FOU",
                    font= brand_font,
                    fill= "#E8C998",
                    anchor= "lm"
                )

                brand_photo = ImageTk.PhotoImage(brand_background)

                brand_art_label.configure(image= brand_photo)
                brand_art_label.image = brand_photo

                brand_art_label.place(
                    x= brand_x,
                    y= brand_y,
                    width= brand_w,
                    height= brand_h
                )

                brand_art_label.lift()

            theme_selector_frame.lift()
            refresh_button.lift()
            save_button.lift()

    elif current_theme == "VOID":

        brand_art_label.place_forget()
        brand_art_label.configure(image= "")
        brand_art_label.image = None

        header_x = header_frame.winfo_x()
        header_y = header_frame.winfo_y()
        header_width = header_frame.winfo_width()
        header_height = header_frame.winfo_height()

        if header_width > 1 and header_height > 1:

            void_header_crop = fitted_background.crop(
                (
                    header_x,
                    header_y,
                    header_x + header_width,
                    header_y + header_height
                )
            )

            void_header_photo = ImageTk.PhotoImage(
                void_header_crop,
                master= app
            )

            header_art_label.configure(
                image= void_header_photo
            )
            header_art_label.image = void_header_photo

            header_art_label.place(
                x= 0,
                y=0,
                relwidth= 1,
                relheight= 1
            )
            header_art_label.lift()

            brand_x = brand_frame.winfo_x()
            brand_y = brand_frame.winfo_y()
            brand_w = max(brand_frame.winfo_width(), int(320 * ui_scale))
            brand_h = brand_frame.winfo_height()

            if brand_w > 1 and brand_h > 1:

                brand_background = void_header_crop.crop(
                    (
                        brand_x,
                        brand_y,
                        brand_x + brand_w,
                        brand_y + brand_h
                    )
                ).convert("RGBA")

                void_logo_h = max(
                    1,
                    min(
                        brand_h - 4,
                        int(78 * ui_scale)
                    )
                )

                void_logo_w = max(
                    1,
                    int(void_logo_h * logo_ratio)
                )

                void_logo = logo_pil.resize(
                    (void_logo_w, void_logo_h),
                    Image.Resampling.LANCZOS
                )

                logo_color = Image.new(
                    "RGBA",
                    void_logo.size,
                    "#CBB3EE"
                )

                logo_color.putalpha(
                    void_logo.getchannel("A")
                )

                brand_background.alpha_composite(
                    logo_color,
                    (
                        5,
                        max(
                            0,
                            (brand_h - void_logo_h) // 2
                        )
                    )
                )

                try:
                    void_font = ImageFont.truetype(
                        str(VOID_UI_DIR / "NewRocker-Regular.ttf"),
                        max(20, int(62 * ui_scale))
                    )
                except OSError:
                    void_font = ImageFont.load_default()

                ImageDraw.Draw(brand_background).text(
                    (
                        5 + void_logo_w + int(8 * ui_scale),
                        brand_h // 2
                    ),
                    "FOU",
                    font= void_font,
                    fill= "#D9C2F5",
                    anchor= "lm"
                )

                void_brand_photo = ImageTk.PhotoImage(
                    brand_background,
                    master= app
                )

                brand_art_label.configure(
                    image= void_brand_photo
                )
                brand_art_label.image = void_brand_photo

                brand_art_label.place(
                    x= brand_x,
                    y= brand_y,
                    width= brand_w,
                    height= brand_h
                )
                
                brand_art_label.lift()
            
            refresh_x = refresh_button.winfo_x()
            refresh_y = refresh_button.winfo_y()
            refresh_w = refresh_button.winfo_width()
            refresh_h = refresh_button.winfo_height()

            frame_pad = 14
            frame_w = refresh_w + 2 * frame_pad
            frame_h = refresh_h + 2 * frame_pad

            if (
            void_button_frame_pil is not None
            and refresh_w > 1
            and refresh_h > 1
            ):
                refresh_bg = void_header_crop.crop(
                    (
                        refresh_x - frame_pad,
                        refresh_y - frame_pad,
                        refresh_x + refresh_w + frame_pad,
                        refresh_y + refresh_h + frame_pad
                    )
                ).convert("RGBA")

                refresh_frame_pil = void_button_frame_pil.resize(
                    (frame_w, frame_h),
                    Image.Resampling.LANCZOS
                )

                refresh_bg.alpha_composite(
                    refresh_frame_pil,
                    (0, 0)
                )

                refresh_button_frame_photo = ImageTk.PhotoImage(
                    refresh_bg,
                    master= app
                )

                refresh_button_art_label.configure(
                    image= refresh_button_frame_photo
                )
                refresh_button_art_label.image = (
                    refresh_button_frame_photo
                )

                refresh_button_art_label.place(
                    x= refresh_x - frame_pad,
                    y= refresh_y - frame_pad,
                    width= frame_w,
                    height= frame_h
                )
            
            refresh_button_art_label.lift()

            render_void_button_frame(theme_selector_frame, 10, background=fitted_background)
            render_void_button_frame(save_button, 9, background=fitted_background)
            render_void_button_frame(add_button, 8, fill=THEMES["VOID"]["panel_bg"])
            render_void_button_frame(help_button, 7, background=fitted_background)            

            theme_selector_frame.lift()
            refresh_button.lift()
            save_button.lift()
        
    else:
        header_art_label.place_forget()
        brand_art_label.place_forget()
        brand_art_label.configure(image= "")
        brand_art_label.image = None
        header_art_label.configure(image= "")
        header_art_label.image = None


def schedule_responsive_art(event= None):
    global responsive_job

    if event is not None:
        if event.widget is not app:
            return
    
    if responsive_job is not None:
        app.after_cancel(
            responsive_job
        )

    responsive_job = app.after(
        100,
        apply_responsive_art
    )


def set_activity(message, state= "idle"):
    global activity_status_icon

    theme = THEMES[current_theme]

    activity_status_icon = create_activity_icon(
        state,
        theme["accent"],
        theme["app_bg"]
    )

    activity_icon.configure(
        image= activity_status_icon
    )

    activity_message.configure(
        text= message
    )

    set_reaction(state)


def select_coin(symbol, name):
    global selected_symbol

    selected_symbol = symbol

    draw_coin_rows(last_rows)

    update_portfolio_status()


def remove_coin_gui(symbol):
    if refresh_button.cget("state") == "disabled":
        return

    result = remove_coin_portfolio(portfolio, symbol)

    if result == "removed":
        refresh_portfolio(f"{symbol} removed from portfolio",
        "happy"
    )


def save_portfolio_gui():
    result = save_portfolio(portfolio)

    if result == "saved":
       set_activity(
            "Portfolio saved successfully",
            "proud"
        )


def add_coin_gui():
    if add_button.cget("state") == "disabled":
        return


    symbol = coin_entry.get().strip().upper()

    if not symbol:
        set_activity(
            "Enter a coin symbol",
            "confused"
        )
        
        return
    
    add_button.configure(state= "disabled")
    refresh_button.configure(state= "disabled")
    
    set_activity(
        f"Checking {symbol}....",
        "loading"
    )

    worker = threading.Thread(
        target= add_coin_worker,
        args= (symbol,),
        daemon= True
    )

    worker.start()
    app.after(100, check_add_queue)


def check_add_queue():
    try:
        result, symbol = add_queue.get_nowait()
    
    except queue.Empty:
        app.after(100, check_add_queue)
        return
    
    add_button.configure(state= "normal")
    refresh_button.configure(state= "normal")

    if result == "added":
        coin_entry.delete(0, "end")
        coin_entry.focus_set()
        refresh_portfolio(f"{symbol} added to portfolio",
        "happy"
    )
        return
    
    if result == "already_exists":
        set_activity(
            f"{symbol} is already in portfolio",
            "angry"
       )
        return

    if result == "not_found":
        set_activity(
            f"{symbol} not found",
            "confused"
        )
        return
    
    if result == "network_error":
        set_activity(
            "Unable to add coin",
            "confused"
        )
        return


def add_coin_worker(symbol):
    coin_list = get_coin_list()

    if coin_list is None:
        add_queue.put(("network_error", symbol))
        return
    
    result = add_coin_portfolio(portfolio, coin_list, symbol)

    add_queue.put((result, symbol))


def load_portfolio_worker(success_message, success_state):
    status, coins = get_portfolio_data(portfolio)

    portfolio_queue.put((status, coins, success_message, success_state))


def check_portfolio_queue():
    try:
        status, coins, success_message, success_state = portfolio_queue.get_nowait()

    except queue.Empty:
        app.after(100, check_portfolio_queue)
        return
    
    refresh_button.configure(state= "normal")
    add_button.configure(state= "normal")
    
    render_portfolio(status, coins, success_message, success_state)

    
def refresh_portfolio(success_message= "Portfolio loaded", success_state= "idle"):
    refresh_button.configure(state= "disabled")
    add_button.configure(state= "disabled")
    
    set_activity(
        "Connecting to Fou server....",
        "loading"
    )

    worker= threading.Thread(
        target= load_portfolio_worker,
        args= (success_message, success_state),
        daemon= True
    )

    worker.start()
    app.after(100, check_portfolio_queue)


def open_help_video():
    if not HELP_VIDEO_URL:
        set_activity(
            "Help tutorial coming soon",
            "confused"
        )
        return
    
    webbrowser.open_new_tab(
        HELP_VIDEO_URL
    )


def render_portfolio(status, coins, success_message, success_state):
    global last_rows
    global selected_symbol
    global last_updated_time

    if status == "network_error":
        set_activity(
            "Unable to refresh the data",
            "confused"
        )
        return

    if status in ("ok", "empty_portfolio"):
        last_updated_time = datetime.now().strftime(
            "%H:%M:%S"
        )

    for widget in rows_frame.winfo_children():
        widget.destroy()

    if status == "empty_portfolio":
        last_rows = []

        selected_symbol = None

        coin_count.configure(text= "0 coins")

        update_portfolio_status()

        set_activity(
            "Portfolio is empty",
            "confused"
        )
        return
    
    if status == "ok":
        count = len(coins)

        if count == 1:
            coin_count.configure(text= "1 coin")
        else:
            coin_count.configure(text= f"{count} coins")

    last_rows = []

    for row_number, coin in enumerate(coins):
        price = coin["current_price"]

        multiplier = 1
        display_price = price

        while 0 < display_price < 0.00000001:
            multiplier *= 1000
            display_price = price * multiplier

        multiplier_text = (
            f"×{multiplier:,}" if multiplier > 1 else ""
        )

        if price == 0:
            price_text = "Price unavailable"
        elif display_price >= 1:
            price_text = f"${display_price:,.2f}"
        elif display_price >= 0.01:
            price_text = f"${display_price:,.4f}"
        else:
            price_text = f"${display_price:,.8f}"

        last_rows.append(
            (
                coin["symbol"].upper(),
                coin["name"],
                price_text,
                coin.get("image"),
                multiplier_text
            )
        )

    available_symbols = {
        row[0]
        for row in last_rows
    }

    if selected_symbol not in available_symbols:
        selected_symbol = None
    
    draw_coin_rows(last_rows)

    update_portfolio_status()

    set_activity(
        success_message,
        success_state
    )


def change_theme(selected_theme):
    global current_theme
    global background_pil
    global refresh_icon
    global save_icon
    global search_icon
    global clock_icon
    global activity_status_icon
    global theme_card_icon
    global database_icon

    if selected_theme not in THEMES:
        theme_selector.set(
            "The Fool" if current_theme == "THE FOOL"
            else current_theme
        )

        set_activity(
            f"{selected_theme} theme coming soon",
            "confused"
        )
        return

    current_theme = selected_theme

    if current_theme == "THE FOOL" and FOOL_BG_PATH.is_file():
        background_path = FOOL_BG_PATH

    elif current_theme == "VOID" and VOID_BG_PATH.is_file():
        background_path = VOID_BG_PATH
    
    else:
        background_path = FOU_DEFAULT_BG_PATH

    with Image.open(background_path) as source:
        background_pil = source.convert("RGB")
    
    schedule_responsive_art()

    theme = THEMES[current_theme]

    activity_status_icon = create_activity_icon(
        current_reaction_state,
        theme["accent"],
        theme["app_bg"]
    )

    activity_icon.configure(
        image= activity_status_icon,
        fg_color= "transparent"
    )

    clock_icon = create_clock_icon(
        theme["muted_text"]
    )

    updated_label.configure(
        image= clock_icon
    )

    search_icon = create_search_icon(
        theme["muted_text"]
    )

    search_icon_label.configure(
        image= search_icon
    )

    refresh_icon = create_tinted_icon(
        UI_DIR / "refresh.png",
        theme["text"]
    )

    save_icon = create_tinted_icon(
        UI_DIR / "save.png",
        theme["text"]
    )

    refresh_button.configure(
        image= refresh_icon
    )

    save_button.configure(
        image= save_icon
    )

    reaction_title.configure(
        text= "C O M P A N I O N",
        text_color= theme["muted_text"]
    )

    reaction_state_label.configure(
        text_color= theme["muted_text"]
    )

    reaction_image.configure(
        text_color= theme["text"] 
    )

    app.configure(
        fg_color= theme["app_bg"]
    )

    preview_frame.configure(
        fg_color= theme["reaction_bg"],
        border_color= theme.get(
            "card_border",
            theme["border"]
        ),
        border_width= 0 if (
            current_theme == "VOID"
            and void_companion_frame_pil is not None
        ) else 1
    )

    if (current_theme == "VOID" and void_companion_frame_pil is not None):
        preview_inner.pack_configure(
            padx= 48,
            pady= (42, 44)
        )

        schedule_void_companion_border()

    else:
        preview_inner.pack_configure(
            padx= 0,
            pady= 0
        )

        hide_void_companion_border()

    portfolio_frame.configure(
        fg_color= theme["panel_bg"],
        border_color= theme.get(
            "card_border",
            theme["border"]
        )
    )

    if (
        (current_theme == "THE FOOL" and fool_portfolio_frame_pil is not None)
        or (current_theme == "VOID" and void_portfolio_frame_pil is not None)
    ):

        portfolio_frame.configure(
            border_width= 0
        )
        schedule_portfolio_border_render()

    else:

        portfolio_frame.configure(
            border_width = 1
        )

        portfolio_header.grid_configure(
            padx= 20,
            pady= (16, 8)
        )

        search_frame.grid_configure(
            padx= 20,
            pady= 10
        )

        column_header.grid_configure(
            padx= 20,
            pady= (10, 5)
        )

        rows_frame.grid(
            padx= 20,
            pady= (5, 0)
        )

        portfolio_status_frame.grid_configure(
            padx= 20,
            pady= (0, 10)
        )

        hide_portfolio_border()

    portfolio_status_separator.configure(
        fg_color= theme["border"]
    )

    portfolio_status_divider.configure(
        fg_color= theme.get(
            "status_divider",
            theme["border"]
        )
    )

    if current_theme == "THE FOOL":

        portfolio_status_divider.grid_remove()

        portfolio_status_ornament.grid()

        portfolio_ornament_left.configure(
            bg= theme["status_divider"]
        )

        portfolio_ornament_right.configure(
            bg= theme["status_divider"]
        )

        portfolio_ornament_star.configure(
            text_color= theme["accent_highlight"]
        )

    else:

        portfolio_status_ornament.grid_remove()
        portfolio_status_divider.grid()

    updated_label.configure(
        text_color= theme["muted_text"]
    )

    selected_coin_label.configure(
        text_color= theme["muted_text"]
    )

    reaction_title.configure(
        text= "C O M P A N I O N",
        text_color= theme["muted_text"]
    )

    reaction_state_label.configure(
        text_color= theme["muted_text"],
        width= 78,
        height= 30
    )

    if current_theme == "THE FOOL":

        companion_header.configure(
            fg_color= theme["panel_bg"],
            border_width= 1,
            border_color= theme["border"]
        )

        reaction_title.configure(
            text_color= theme["text"]
        )

        reaction_state_label.configure(
            fg_color= theme["panel_bg"],
            text_color= theme["text"],
            border_width= 1,
            border_color= theme["border"],
            corner_radius= 13
        )

    else:

        companion_header.configure(
            fg_color= "transparent",
            border_width= 0
        )

        reaction_state_label.configure(
            fg_color= "transparent",
            text_color= theme["muted_text"],
            border_width= 0
        )

    activity_frame.configure(
        fg_color= theme["button_bg"],
        border_color= theme.get(
            "card_border",
            theme["border"]
        )
    )

    if current_theme == "THE FOOL":

        activity_gold_top_line.configure(
            bg= theme["border"]
        )

        activity_gold_bottom_line.configure(
            bg= theme["border"]
        )

        activity_gold_ornament.configure(
            fg= theme.get("accent_highlight", theme["accent"]),
            bg= theme["button_bg"]
        )

        activity_gold_top_line.place(
            x= 14,
            y= 12,
            relwidth= 1.0,
            width= -28,
            height= 1
        )

        activity_gold_bottom_line.place(
            x= 14,
            rely= 1.0,
            y= -5,
            relwidth= 1.0,
            width= -28,
            height= 1
        )

        activity_gold_ornament.place(
            relx= 0.5,
            y= 12,
            anchor= "center"
        )

    else:

        activity_gold_top_line.place_forget()
        activity_gold_bottom_line.place_forget()
        activity_gold_ornament.place_forget()

    activity_title.configure(
        text_color= theme["muted_text"]
    )

    activity_message.configure(
        text_color= theme["text"]
    )

    header_lable.configure(
        text_color= theme["text"]
    )

    portfolio_title.configure(
        text_color= theme["text"]
    )

    coin_count_badge.configure(
        border_color= theme["border"]
    )

    coin_count.configure(
        text_color= theme["muted_text"]
    )

    currency_badge.configure(
        border_color= theme["border"]
    )

    currency_label.configure(
        text_color= theme["text"]
    )

    asset_label.configure(
        text_color= theme["muted_text"]
    )

    price_label.configure(
        text_color= theme["muted_text"]
    )

    refresh_button.configure(
        fg_color= "transparent",
        hover_color= theme["button_hover"],
        border_color= theme["border"],
        text_color= theme["text"],
        border_width= 1
    )

    save_button.configure(
        fg_color= "transparent",
        hover_color= theme["button_hover"],
        border_color= theme["border"],
        text_color= theme["text"],
        border_width= 1
    )

    if current_theme == "THE FOOL":
        add_button.configure(
            fg_color= theme["parchment_bg"],
            hover_color= theme["parchment_highlight"],
            text_color= theme["parchment_text"],
            border_color= theme["parchment_shadow"],
            border_width= 2,
            corner_radius= 8,
        )

    else:
        add_button.configure(
            fg_color= theme["accent"],
            hover_color= theme["text"],
            text_color= theme["app_bg"],
            border_width= 0,
            corner_radius= 8,
        )

    search_box.configure(
        fg_color= "transparent"
    )

    coin_entry.configure(
        fg_color= theme["entry_bg"],
        border_color= theme["entry_border"],
        text_color= theme["text"],
        placeholder_text_color= theme["muted_text"]
    )

    search_icon_label.configure(
        fg_color= theme["entry_bg"],
        image= search_icon
    )

    theme_selector.configure(
        fg_color= theme["button_bg"],
        button_color= theme["button_bg"],
        button_hover_color= theme["button_hover"],
        text_color= theme["text"]
    )

    icon_color = theme.get(
        "accent_highlight",
        theme["accent"]
    )

    recolored_card = Image.new(
        "RGBA",
        theme_card_pil.size,
        icon_color
    )

    recolored_card.putalpha(
        theme_card_pil.getchannel("A")
    )

    theme_card_icon = ctk.CTkImage(
        light_image= recolored_card,
        dark_image= recolored_card,
        size= (24, 24)
    )

    theme_card_label.configure(
        image= theme_card_icon
    )

    theme_card_label.grid()
    theme_prefix_label.grid()

    theme_prefix_label.configure(
        text_color= icon_color,
        font= ("Georgia", 15)
        if current_theme == "THE FOOL"
        else ("Segoe UI", 13)
    )

    theme_selector_frame.configure(
        fg_color= theme["button_bg"],
        border_color= theme["border"],
        border_width= 1
    )

    theme_selector.configure(
        width= 155 if current_theme == "FOU DEFAULT" else 130,
        height= 40
    )

    theme_selector.grid_configure(
        padx= (0, 5),
        pady= 3
    )

    theme_selector.set(
        "The Fool" if current_theme == "THE FOOL"
        else current_theme
    )

    if current_theme == "THE FOOL":

        logo_label.configure(
            image= fool_logo_image
        )

        header_lable.configure(
            font= ("Georgia", 42, "bold")
        )

        theme_selector.configure(
            font= ("Georgia", 15)
        )

        refresh_button.configure(
            font= ("Georgia", 16)
        )

        save_button.configure(
            font= ("Georgia", 16)
        )

        reaction_title.configure(
            font= ("Georgia", 13, "bold")
        )

        reaction_state_label.configure(
            font= ("Georgia", 13)
        )

        portfolio_title.configure(
            font= ("Georgia", 31, "bold")
        )

        coin_count.configure(
            font= ("Georgia", 11)
        )

        currency_label.configure(
            font= ("Georgia", 13)
        )

        coin_entry.configure(
            font= ("Georgia", 15)
        )

        add_button.configure(
            font= ("Georgia", 16, "bold")
        )

        asset_label.configure(
            font= ("Georgia", 13)
        )

        price_label.configure(
            font= ("Georgia", 13)
        )

        activity_title.configure(
            font= ("Georgia", 12, "bold")
        )

        activity_message.configure(
            font= ("Georgia", 14)
        )

        save_local_label.configure(
            font= ("Georgia", 12)
        )

        help_button.configure(
            font= ("Georgia", 12)
        )

    else:

        logo_label.configure(
            image= logo_image
        )

        header_lable.configure(
            font= ("Segoe UI", 38, "bold")
        )

        theme_selector.configure(
            font= ("Segoe UI", 13)
        )

        refresh_button.configure(
            font= ("Consolas", 16)
        )

        save_button.configure(
            font= ("Consolas", 16)
        )

        reaction_title.configure(
            font= ("Segoe UI", 11, "bold")
        )

        reaction_state_label.configure(
            font= ("Segoe UI", 13)
        )

        portfolio_title.configure(
            font= ("Segoe UI", 28, "bold")
        )

        coin_count.configure(
            font= ("Segoe UI", 11)
        )

        currency_label.configure(
            font= ("Segoe UI", 12)
        )

        coin_entry.configure(
            font= ("Segoe UI", 14)
        )

        add_button.configure(
            font= ("Segoe UI", 14, "bold")
        )

        asset_label.configure(
            font= ("Segoe UI", 13)
        )

        price_label.configure(
            font= ("Segoe UI", 13)
        )

        activity_title.configure(
            font= ("Segoe UI", 11, "bold")
        )

        activity_message.configure(
            font= ("Segoe UI", 13)
        )

        save_local_label.configure(
            font= ("Consolas", 12)
        )

        help_button.configure(
            font= ("Consolas", 12)
        )

    if current_theme == "VOID":
        
        reaction_title.configure(
            text= "COMPANION",
            font= ("New Rocker", 23, "bold"),
            text_color= theme["text"]
        )

        reaction_state_label.configure(
            fg_color= theme["panel_bg"],
            text_color= theme["accent_highlight"],
            border_width= 1,
            border_color= theme["border"],
            corner_radius= 13,
            width= 94,
            height= 32
        )

        portfolio_title.configure(
            font= ("New Rocker", 45, "bold"),
            text_color= theme["text"]
        )

        refresh_button.configure(
            fg_color= "transparent",
            border_width= 0
        )

        save_button.configure(border_width= 0)
        help_button.configure(border_width= 0)
        theme_selector_frame.configure(border_width= 0)

        coin_entry.configure(font= ("Georgia", 16))

        add_button.configure(font= ("Georgia", 16, "bold"))

        theme_prefix_label.configure(font= ("Georgia", 16))

        theme_selector.configure(font= ("Georgia", 14))

        refresh_button.configure(font= ("Georgia", 16))
        
        save_button.configure(font= ("Georgia", 16))

    rows_frame.configure(
        fg_color= theme["panel_bg"],
        scrollbar_fg_color= theme.get(
            "scrollbar_track",
            theme["panel_bg"]
        ),
        scrollbar_button_color= theme.get(
            "scrollbar_thumb",
            theme["border"]
        ),
        scrollbar_button_hover_color= theme.get(
            "scrollbar_hover",
            theme["accent"]
        )
    )

    rows_frame._scrollbar.configure(
        width= 20 if current_theme == "THE FOOL" else 18,
        corner_radius= 10,
        border_spacing= 2
    )

    draw_coin_rows(last_rows)

    set_activity(
        f"Theme selected: {selected_theme}",
        "idle"
    )

    save_local_label.configure(
        text_color= theme["muted_text"]
    )

    database_icon = create_database_icon(
        theme.get(
            "accent_highlight",
            theme["accent"]
        ),
        size= (18, 18)
    )

    save_local_label.configure(
        image= database_icon,
        compound= "left"
    )

    help_button.configure(
        fg_color= "transparent",
        hover_color= theme["button_hover"],
        border_color= theme["border"],
        text_color= theme["text"],
        border_width= 0 if current_theme == "VOID" else 1
    )

    if current_theme == "THE FOOL":

        footer_frame.configure(
            fg_color= theme["button_bg"],
            corner_radius= 8,
            border_width= 1,
            border_color= theme["border"]
        )

        footer_frame.grid_configure(
            padx= 20
        )

        save_local_label.configure(
            text_color= theme["text"]
        )

        save_local_label.grid_configure(
            padx= (14, 0),
            pady= (4, 4)
        )

        help_button.grid_configure(
            padx= (0, 8),
            pady= (4, 4)
        )
    
    else:

        footer_frame.configure(
            fg_color= "transparent",
            corner_radius= 0,
            border_width= 0
        )

        footer_frame.grid_configure(
            padx= 30
        )

        save_local_label.configure(
            text_color= theme["muted_text"]
        )

        save_local_label.grid_configure(
            padx= 0,
            pady= 0
        )

        help_button.grid_configure(
            padx= 0,
            pady= 0
        )


refresh_button.configure(
    command= refresh_portfolio
)

save_button.configure(
    command= save_portfolio_gui
)

add_button.configure(
    command= add_coin_gui
)

theme_selector.configure(
    command= change_theme
)

help_button.configure(
    command= open_help_video
)

coin_entry.bind(
    "<Return>",
    lambda event: add_coin_gui()
)

search_icon_label.bind(
    "<Button-1>",
    lambda event: coin_entry.focus_set()
)

preview_frame.bind(
    "<Configure>",
    schedule_void_companion_border
)

reaction_stage.bind(
    "<Configure>",
    schedule_reaction_render
)

rows_frame._parent_canvas.bind(
    "<Configure>",
    lambda event: force_rows_full_width(),
    add= "+"
)

reaction_stage.bind(
    "<Configure>",
    schedule_portfolio_border_render,
    add= "+"
)

reaction_image.bind(
    "<Configure>",
    schedule_portfolio_border_render,
    add= "+"
)

portfolio_frame.bind(
    "<Configure>",
    schedule_portfolio_border_render
)

app.bind(
    "<Configure>",
    schedule_responsive_art
)

app.after(
    150,
    apply_responsive_art
)

change_theme(current_theme)
set_activity("standing by.... ", "idle")
refresh_portfolio()

app.mainloop()
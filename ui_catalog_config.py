# -*- coding: utf-8 -*-
from __future__ import annotations

import copy

from i18n import tr

# Tabovi palete - svaki template tacno u jednom tabu (bez duplikata)
PALETTE_TABS = [
    {
        "key": "donji",
        "label": "Donji",
        "subgroups": [
            {"label": "1 / 2 vrata", "tids": ["BASE_NARROW", "BASE_1DOOR", "BASE_2DOOR", "BASE_OPEN"]},
            {"label": "Fioke", "tids": ["BASE_DRAWERS_3", "BASE_DOOR_DRAWER"]},
            {"label": "Funkcionalni", "tids": ["SINK_BASE", "BASE_TRASH"]},
            {"label": "Paneli", "tids": ["FILLER_PANEL", "END_PANEL"]},
        ],
    },
    {
        "key": "gornji",
        "label": "Gornji",
        "subgroups": [
            {"label": "1 / 2 vrata", "tids": ["WALL_NARROW", "WALL_1DOOR", "WALL_2DOOR", "WALL_GLASS", "WALL_LIFTUP"]},
            {"label": "Otvoreni", "tids": ["WALL_OPEN"]},
            {"label": "Iznad visokih", "tids": ["WALL_UPPER_1DOOR", "WALL_UPPER_2DOOR", "WALL_UPPER_OPEN"]},
        ],
    },
    {
        "key": "visoki",
        "label": "Visoki",
        "subgroups": [
            {"label": "Standardni", "tids": ["TALL_PANTRY", "TALL_GLASS", "TALL_DOORS", "TALL_OPEN"]},
            {"label": "Frizider ugradni", "tids": ["TALL_FRIDGE", "TALL_FRIDGE_FREEZER"]},
            {"label": "Frizider samostojeci", "tids": ["TALL_FRIDGE_FREESTANDING"]},
            {"label": "Gornja dopuna", "tids": ["TALL_TOP_DOORS", "TALL_TOP_OPEN"]},
        ],
    },
    {
        "key": "ormari",
        "label": "Ugradni",
        "subgroups": [
            {"label": "Kuvanje", "tids": ["BASE_COOKING_UNIT", "TALL_OVEN", "TALL_OVEN_MICRO"]},
            {"label": "Kuhinjski", "tids": ["BASE_DISHWASHER", "WALL_MICRO", "WALL_HOOD"]},
            {"label": "Samostojeci uredjaji", "tids": ["BASE_OVEN_HOB_FREESTANDING", "BASE_DISHWASHER_FREESTANDING"]},
        ],
    },
    {
        "key": "garderoba",
        "label": "Ormari",
        "subgroups": [
            {"label": "Krilna i klizna", "tids": ["TALL_WARDROBE_2DOOR", "TALL_WARDROBE_DRAWERS", "TALL_WARDROBE_2DOOR_SLIDING"]},
            {"label": "Američki plakar", "tids": ["TALL_WARDROBE_AMERICAN"]},
            {"label": "Unutrašnje sekcije", "tids": ["TALL_WARDROBE_INT_SHELVES", "TALL_WARDROBE_INT_DRAWERS", "TALL_WARDROBE_INT_HANG"]},
            {"label": "Ugaoni ormari", "tids": ["TALL_WARDROBE_CORNER", "TALL_WARDROBE_CORNER_SLIDING"]},
        ],
    },
]

_FRONT_COLOR_PRESETS = [
    {"hex": "#FDFDFB", "name": "Beli dekor", "swatch": "linear-gradient(145deg,#ffffff,#f0f1ee)"},
    {"hex": "#E7D9BF", "name": "Svetli drvni dekor", "swatch": "linear-gradient(145deg,#f3ead7,#d8c49e)"},
    {"hex": "#CFAE84", "name": "Bukva", "swatch": "linear-gradient(145deg,#e7c89d,#bb8f63)"},
    {"hex": "#B8A079", "name": "Jela", "swatch": "linear-gradient(145deg,#d6c4a2,#9f865f)"},
    {"hex": "#B98A55", "name": "Hrast", "swatch": "linear-gradient(145deg,#d6ab76,#996a3f)"},
    {"hex": "#D3B17F", "name": "Bor", "swatch": "linear-gradient(145deg,#e4c89b,#b88d59)"},
    {"hex": "#C49368", "name": "Aris", "swatch": "linear-gradient(145deg,#ddb58a,#a47347)"},
    {"hex": "#7D3F2D", "name": "Mahagoni", "swatch": "linear-gradient(145deg,#9a5842,#5d2c1f)"},
    {"hex": "#A85A42", "name": "Tresnja", "swatch": "linear-gradient(145deg,#bf7257,#8f4633)"},
    {"hex": "#8C5C3C", "name": "Kesten", "swatch": "linear-gradient(145deg,#a9744e,#6d452f)"},
    {"hex": "#B97A44", "name": "Tik", "swatch": "linear-gradient(145deg,#cf9760,#9d6232)"},
    {"hex": "#5D3E35", "name": "Palisander", "swatch": "linear-gradient(145deg,#7a554a,#452d27)"},
    {"hex": "#6F4B33", "name": "Orah", "swatch": "linear-gradient(145deg,#8d6648,#543825)"},
    {"hex": "#6C7A4E", "name": "Maslina", "swatch": "linear-gradient(145deg,#889865,#55603d)"},
    {"hex": "#2D5A3D", "name": "Zelena", "swatch": "linear-gradient(145deg,#3f7a54,#20442d)"},
    {"hex": "#A67F45", "name": "Bagrem", "swatch": "linear-gradient(145deg,#c49c60,#8b6736)"},
    {"hex": "#1E1B1A", "name": "Ebanovina", "swatch": "linear-gradient(145deg,#3a3532,#121010)"},
]


_TV_ZONE_TABS = [
    {
        "key": "donji",
        "label": "TV Komode",
        "subgroups": [
            {"label": "TV moduli", "tids": ["BASE_TV_2DOOR", "BASE_TV_DRAWERS", "BASE_TV_OPEN"]},
            {"label": "Komode", "tids": ["BASE_1DOOR", "BASE_2DOOR", "BASE_DRAWERS_3", "BASE_DOOR_DRAWER", "BASE_OPEN"]},
            {"label": "Paneli", "tids": ["FILLER_PANEL", "END_PANEL"]},
        ],
    },
    {
        "key": "gornji",
        "label": "Police",
        "subgroups": [
            {"label": "TV zid", "tids": ["WALL_TV_OPEN"]},
            {"label": "Zidni elementi", "tids": ["WALL_OPEN", "WALL_GLASS", "WALL_1DOOR", "WALL_2DOOR", "WALL_LIFTUP"]},
            {"label": "Gornja dopuna", "tids": ["WALL_UPPER_1DOOR", "WALL_UPPER_2DOOR", "WALL_UPPER_OPEN"]},
        ],
    },
]

# Ugaoni tab — vidljiv samo za L/U kuhinje
UGAONI_TAB = {
    "key": "ugaoni",
    "label": "Ugaoni",
    "subgroups": [
        {"label": "Donji ugaoni", "tids": ["BASE_CORNER", "BASE_CORNER_DIAGONAL"]},
        {"label": "Gornji ugaoni", "tids": ["WALL_CORNER", "WALL_CORNER_DIAGONAL"]},
    ],
}

# Layouts koji aktiviraju ugaoni tab
_CORNER_LAYOUTS = {"l_oblik", "u_oblik"}


_PALETTE_LABELS_EN = {
    "Donji": "Base",
    "Gornji": "Wall",
    "Visoki": "Tall",
    "Ugradni": "Built-in",
    "Ormari": "Wardrobes",
    "1 / 2 vrata": "1 / 2 doors",
    "Fioke": "Drawers",
    "Funkcionalni": "Functional",
    "Paneli": "Panels",
    "Otvoreni": "Open",
    "Iznad visokih": "Above tall units",
    "Standardni": "Standard",
    "Frizider ugradni": "Integrated fridge",
    "Frizider samostojeci": "Freestanding fridge",
    "Gornja dopuna": "Top extension",
    "Kuvanje": "Cooking",
    "Kuhinjski": "Kitchen appliances",
    "Samostojeci uredjaji": "Freestanding appliances",
    "Krilna i klizna": "Hinged and sliding",
    "AmeriÄki plakar": "American wardrobe",
    "Američki plakar": "American wardrobe",
    "UnutraÅ¡nje sekcije": "Interior sections",
    "Unutrašnje sekcije": "Interior sections",
    "Ugaoni ormari": "Corner wardrobes",
    "TV Komode": "TV units",
    "TV moduli": "TV modules",
    "Komode": "Sideboards",
    "Police": "Shelves",
    "TV zid": "TV wall",
    "Zidni elementi": "Wall units",
    "Ugaoni": "Corner",
    "Donji ugaoni": "Base corner",
    "Gornji ugaoni": "Wall corner",
}

_PALETTE_LABELS_ES = {
    "Donji": "Bajos",
    "Gornji": "Altos",
    "Visoki": "Altos de suelo",
    "Ugradni": "Integrados",
    "Ormari": "Armarios",
    "1 / 2 vrata": "1 / 2 puertas",
    "Fioke": "Cajones",
    "Funkcionalni": "Funcionales",
    "Paneli": "Paneles",
    "Otvoreni": "Abiertos",
    "Iznad visokih": "Sobre altos",
    "Standardni": "Estándar",
    "Frizider ugradni": "Frigorífico integrado",
    "Frizider samostojeci": "Frigorífico independiente",
    "Gornja dopuna": "Extensión superior",
    "Kuvanje": "Cocción",
    "Kuhinjski": "Electrodomésticos de cocina",
    "Samostojeci uredjaji": "Electrodomésticos independientes",
    "Ugaoni": "Esquina",
    "Donji ugaoni": "Bajo de esquina",
    "Gornji ugaoni": "Alto de esquina",
}

_PALETTE_LABELS_PTBR = {
    "Donji": "Inferiores",
    "Gornji": "Superiores",
    "Visoki": "Altos",
    "Ugradni": "Embutidos",
    "Ormari": "Armários",
    "1 / 2 vrata": "1 / 2 portas",
    "Fioke": "Gavetas",
    "Funkcionalni": "Funcionais",
    "Paneli": "Painéis",
    "Otvoreni": "Abertos",
    "Iznad visokih": "Acima dos altos",
    "Standardni": "Padrão",
    "Frizider ugradni": "Geladeira embutida",
    "Frizider samostojeci": "Geladeira independente",
    "Gornja dopuna": "Complemento superior",
    "Kuvanje": "Cozimento",
    "Kuhinjski": "Eletros de cozinha",
    "Samostojeci uredjaji": "Aparelhos independentes",
    "Ugaoni": "Canto",
    "Donji ugaoni": "Inferior de canto",
    "Gornji ugaoni": "Superior de canto",
}

_PALETTE_LABELS_RU = {
    "Donji": "Нижние",
    "Gornji": "Верхние",
    "Visoki": "Высокие",
    "Ugradni": "Встраиваемые",
    "Ormari": "Шкафы",
    "1 / 2 vrata": "1 / 2 двери",
    "Fioke": "Ящики",
    "Funkcionalni": "Функциональные",
    "Paneli": "Панели",
    "Otvoreni": "Открытые",
    "Iznad visokih": "Над высокими",
    "Standardni": "Стандартные",
    "Frizider ugradni": "Встроенный холодильник",
    "Frizider samostojeci": "Отдельностоящий холодильник",
    "Gornja dopuna": "Верхнее доборное",
    "Kuvanje": "Приготовление",
    "Kuhinjski": "Кухонные приборы",
    "Samostojeci uredjaji": "Отдельностоящие приборы",
    "Ugaoni": "Угловые",
    "Donji ugaoni": "Нижний угловой",
    "Gornji ugaoni": "Верхний угловой",
}

_PALETTE_LABELS_ZHCN = {
    "Donji": "地柜",
    "Gornji": "吊柜",
    "Visoki": "高柜",
    "Ugradni": "嵌入式",
    "Ormari": "柜体",
    "1 / 2 vrata": "1 / 2 门",
    "Fioke": "抽屉",
    "Funkcionalni": "功能型",
    "Paneli": "面板",
    "Otvoreni": "开放式",
    "Iznad visokih": "高柜上方",
    "Standardni": "标准",
    "Frizider ugradni": "嵌入式冰箱",
    "Frizider samostojeci": "独立式冰箱",
    "Gornja dopuna": "上部补柜",
    "Kuvanje": "烹饪",
    "Kuhinjski": "厨房电器",
    "Samostojeci uredjaji": "独立式电器",
    "Ugaoni": "转角",
    "Donji ugaoni": "转角地柜",
    "Gornji ugaoni": "转角吊柜",
}

_PALETTE_LABELS_HI = {
    "Donji": "निचले",
    "Gornji": "ऊपरी",
    "Visoki": "ऊँचे",
    "Ugradni": "बिल्ट-इन",
    "Ormari": "अलमारियाँ",
    "1 / 2 vrata": "1 / 2 दरवाज़े",
    "Fioke": "दराज़",
    "Funkcionalni": "कार्यात्मक",
    "Paneli": "पैनल",
    "Otvoreni": "खुले",
    "Iznad visokih": "ऊँचों के ऊपर",
    "Standardni": "मानक",
    "Frizider ugradni": "बिल्ट-इन फ्रिज",
    "Frizider samostojeci": "फ्रीस्टैंडिंग फ्रिज",
    "Gornja dopuna": "ऊपरी विस्तार",
    "Kuvanje": "कुकिंग",
    "Kuhinjski": "रसोई उपकरण",
    "Samostojeci uredjaji": "फ्रीस्टैंडिंग उपकरण",
    "Ugaoni": "कोना",
    "Donji ugaoni": "निचला कोना",
    "Gornji ugaoni": "ऊपरी कोना",
}

_TEMPLATE_LABELS_EN = {
    "Donji (1 vrata)": "Base (1 door)",
    "Donji (2 vrata)": "Base (2 doors)",
    "Donji (fioke 2-4)": "Base (drawers 2-4)",
    "Donji (fioke)": "Base (drawers)",
    "Donji (vrata + fioka)": "Base (doors + drawer)",
    "Donji (ugradna rerna + fioka) [HIDDEN]": "Base (built-in oven + drawer) [HIDDEN]",
    "Donji (mašina za sudove)": "Base (dishwasher)",
    "Donji (mašina za sudove - samostojeća)": "Base (dishwasher - freestanding)",
    "Donji (masina za sudove)": "Base (dishwasher)",
    "Donji (masina za sudove - samostojeca)": "Base (dishwasher - freestanding)",
    "Donji (kuhinjska jedinica: rerna + ploca za kuvanje)": "Built-in oven + hob + drawer",
    "Donji (sporet - samostojeci)": "Base (freestanding cooker - no drawer/front)",
    "Donji (sudopera)": "Base (sink)",
    "Donji uski (flase/ulja/zacini)": "Base narrow (bottles/oils/spices)",
    "Donji coskasti (L-oblik)": "Base corner (L-shape)",
    "Donji coskasti (dijagonalni front)": "Base corner (diagonal front)",
    "Donji otvoreni (bez vrata)": "Base open (no doors)",
    "Donji (vrata)": "Base (doors)",
    "Gornji (1 vrata)": "Wall (1 door)",
    "Gornji (2 vrata)": "Wall (2 doors)",
    "Gornji (staklena vrata)": "Wall (glass doors)",
    "Gornji otvoreni (police)": "Wall open (shelves)",
    "Gornji (podizna vrata / klapna)": "Wall (lift-up door / flap)",
    "Gornji coskasti": "Wall corner",
    "Gornji coskasti (dijagonalni front)": "Wall corner (diagonal front)",
    "Gornji uski (zacini)": "Wall narrow (spices)",
    "Gornji (aspirator / napa)": "Wall (hood)",
    "Gornji (mikrotalasna)": "Wall (microwave)",
    "Gornji (vrata)": "Wall (doors)",
    "Visoki (frizider integrisani)": "Tall (integrated fridge)",
    "Visoki (frizider - samostojeci)": "Tall (freestanding fridge)",
    "Visoki (frizider + zamrzivac)": "Tall (fridge + freezer)",
    "Visoki kolona (rerna + mikrotalasna)": "Tall column (oven + microwave)",
    "Visoki ostava / spajz (police)": "Tall pantry (shelves)",
    "Visoki (vrata)": "Tall (doors)",
    "Visoki (ugradna rerna)": "Tall (built-in oven)",
    "Visoki otvoreni (police)": "Tall open (shelves)",
    "Gornji 2. red (1 vrata)": "Upper wall 2nd row (1 door)",
    "Gornji 2. red (2 vrata)": "Upper wall 2nd row (2 doors)",
    "Gornji 2. red (otvoreno / police)": "Upper wall 2nd row (open / shelves)",
    "Visoki (staklena vrata - vitrina)": "Tall (glass doors - display cabinet)",
    "Donji (sortirnik / kante za otpad)": "Base (waste sorting / bins)",
    "Donji (ploča za kuvanje - samostalna)": "Base (hob - standalone)",
    "Filer panel (popunjač prostora)": "Filler panel (space infill)",
    "Zavrsna bocna ploca": "End side panel",
}

_TEMPLATE_LABELS_ES = {
    "Donji (1 vrata)": "Bajo (1 puerta)",
    "Donji (2 vrata)": "Bajo (2 puertas)",
    "Donji (fioke 2-4)": "Bajo (cajones 2-4)",
    "Donji (fioke)": "Bajo (cajones)",
    "Donji (vrata + fioka)": "Bajo (puertas + cajón)",
    "Donji (masina za sudove)": "Bajo (lavavajillas)",
    "Donji (masina za sudove - samostojeca)": "Bajo (lavavajillas independiente)",
    "Donji (kuhinjska jedinica: rerna + ploca za kuvanje)": "Horno + placa + cajón",
    "Donji (sporet - samostojeci)": "Bajo (cocina independiente)",
    "Donji (sudopera)": "Bajo (fregadero)",
    "Donji uski (flase/ulja/zacini)": "Bajo estrecho (botellas/especias)",
    "Donji coskasti (L-oblik)": "Bajo de esquina (L)",
    "Donji coskasti (dijagonalni front)": "Bajo de esquina (frente diagonal)",
    "Donji otvoreni (bez vrata)": "Bajo abierto (sin puertas)",
    "Gornji (1 vrata)": "Alto (1 puerta)",
    "Gornji (2 vrata)": "Alto (2 puertas)",
    "Gornji (staklena vrata)": "Alto (puertas de vidrio)",
    "Gornji otvoreni (police)": "Alto abierto (estantes)",
    "Gornji (podizna vrata / klapna)": "Alto (puerta elevable)",
    "Gornji coskasti": "Alto de esquina",
    "Gornji coskasti (dijagonalni front)": "Alto de esquina (frente diagonal)",
    "Gornji uski (zacini)": "Alto estrecho (especias)",
    "Gornji (aspirator / napa)": "Alto (campana)",
    "Gornji (mikrotalasna)": "Alto (microondas)",
    "Visoki (frizider integrisani)": "Alto (frigorífico integrado)",
    "Visoki (frizider - samostojeci)": "Alto (frigorífico independiente)",
    "Visoki (frizider + zamrzivac)": "Alto (frigorífico + congelador)",
    "Visoki kolona (rerna + mikrotalasna)": "Columna alta (horno + microondas)",
    "Visoki ostava / spajz (police)": "Despensa alta (estantes)",
    "Visoki (vrata)": "Alto (puertas)",
    "Visoki (ugradna rerna)": "Alto (horno empotrado)",
    "Visoki otvoreni (police)": "Alto abierto (estantes)",
    "Gornji 2. red (1 vrata)": "Fila alta 2 (1 puerta)",
    "Gornji 2. red (2 vrata)": "Fila alta 2 (2 puertas)",
    "Gornji 2. red (otvoreno / police)": "Fila alta 2 (abierto / estantes)",
    "Visoki (staklena vrata - vitrina)": "Alto (vitrina de vidrio)",
    "Donji (sortirnik / kante za otpad)": "Bajo (clasificador / cubos)",
    "Filer panel (popunjaÄ prostora)": "Panel de relleno",
    "Zavrsna bocna ploca": "Panel lateral final",
}

_TEMPLATE_LABELS_PTBR = {
    "Donji (1 vrata)": "Inferior (1 porta)",
    "Donji (2 vrata)": "Inferior (2 portas)",
    "Donji (fioke 2-4)": "Inferior (gavetas 2-4)",
    "Donji (fioke)": "Inferior (gavetas)",
    "Donji (vrata + fioka)": "Inferior (portas + gaveta)",
    "Donji (masina za sudove)": "Inferior (lava-louças)",
    "Donji (masina za sudove - samostojeca)": "Inferior (lava-louças independente)",
    "Donji (kuhinjska jedinica: rerna + ploca za kuvanje)": "Forno + cooktop + gaveta",
    "Donji (sporet - samostojeci)": "Inferior (fogão independente)",
    "Donji (sudopera)": "Inferior (pia)",
    "Donji uski (flase/ulja/zacini)": "Inferior estreito (garrafas/especiarias)",
    "Donji coskasti (L-oblik)": "Inferior de canto (L)",
    "Donji coskasti (dijagonalni front)": "Inferior de canto (frente diagonal)",
    "Donji otvoreni (bez vrata)": "Inferior aberto (sem portas)",
    "Gornji (1 vrata)": "Superior (1 porta)",
    "Gornji (2 vrata)": "Superior (2 portas)",
    "Gornji (staklena vrata)": "Superior (portas de vidro)",
    "Gornji otvoreni (police)": "Superior aberto (prateleiras)",
    "Gornji (podizna vrata / klapna)": "Superior (porta basculante)",
    "Gornji coskasti": "Superior de canto",
    "Gornji coskasti (dijagonalni front)": "Superior de canto (frente diagonal)",
    "Gornji uski (zacini)": "Superior estreito (especiarias)",
    "Gornji (aspirator / napa)": "Superior (coifa)",
    "Gornji (mikrotalasna)": "Superior (micro-ondas)",
    "Visoki (frizider integrisani)": "Alto (geladeira embutida)",
    "Visoki (frizider - samostojeci)": "Alto (geladeira independente)",
    "Visoki (frizider + zamrzivac)": "Alto (geladeira + freezer)",
    "Visoki kolona (rerna + mikrotalasna)": "Coluna alta (forno + micro-ondas)",
    "Visoki ostava / spajz (police)": "Despensa alta (prateleiras)",
    "Visoki (vrata)": "Alto (portas)",
    "Visoki (ugradna rerna)": "Alto (forno embutido)",
    "Visoki otvoreni (police)": "Alto aberto (prateleiras)",
    "Gornji 2. red (1 vrata)": "2ª fileira superior (1 porta)",
    "Gornji 2. red (2 vrata)": "2ª fileira superior (2 portas)",
    "Gornji 2. red (otvoreno / police)": "2ª fileira superior (aberto / prateleiras)",
    "Visoki (staklena vrata - vitrina)": "Alto (vitrine de vidro)",
    "Donji (sortirnik / kante za otpad)": "Inferior (separador / lixeiras)",
    "Filer panel (popunjaÄ prostora)": "Painel de preenchimento",
    "Zavrsna bocna ploca": "Painel lateral final",
}

_TEMPLATE_LABELS_RU = {
    "Donji (1 vrata)": "Нижний (1 дверь)",
    "Donji (2 vrata)": "Нижний (2 двери)",
    "Donji (fioke 2-4)": "Нижний (ящики 2-4)",
    "Donji (fioke)": "Нижний (ящики)",
    "Donji (vrata + fioka)": "Нижний (дверцы + ящик)",
    "Donji (masina za sudove)": "Нижний (посудомоечная машина)",
    "Donji (masina za sudove - samostojeca)": "Нижний (отдельностоящая ПММ)",
    "Donji (kuhinjska jedinica: rerna + ploca za kuvanje)": "Духовка + варочная панель + ящик",
    "Donji (sporet - samostojeci)": "Нижний (отдельностоящая плита)",
    "Donji (sudopera)": "Нижний (мойка)",
    "Donji uski (flase/ulja/zacini)": "Нижний узкий (бутылки/специи)",
    "Donji coskasti (L-oblik)": "Нижний угловой (L)",
    "Donji coskasti (dijagonalni front)": "Нижний угловой (диагональный фасад)",
    "Donji otvoreni (bez vrata)": "Нижний открытый (без дверей)",
    "Gornji (1 vrata)": "Верхний (1 дверь)",
    "Gornji (2 vrata)": "Верхний (2 двери)",
    "Gornji (staklena vrata)": "Верхний (стеклянные двери)",
    "Gornji otvoreni (police)": "Верхний открытый (полки)",
    "Gornji (podizna vrata / klapna)": "Верхний (подъемный фасад)",
    "Gornji coskasti": "Верхний угловой",
    "Gornji coskasti (dijagonalni front)": "Верхний угловой (диагональный фасад)",
    "Gornji uski (zacini)": "Верхний узкий (специи)",
    "Gornji (aspirator / napa)": "Верхний (вытяжка)",
    "Gornji (mikrotalasna)": "Верхний (микроволновка)",
    "Visoki (frizider integrisani)": "Высокий (встроенный холодильник)",
    "Visoki (frizider - samostojeci)": "Высокий (отдельностоящий холодильник)",
    "Visoki (frizider + zamrzivac)": "Высокий (холодильник + морозильник)",
    "Visoki kolona (rerna + mikrotalasna)": "Высокая колонна (духовка + микроволновка)",
    "Visoki ostava / spajz (police)": "Высокая кладовая (полки)",
    "Visoki (vrata)": "Высокий (дверцы)",
    "Visoki (ugradna rerna)": "Высокий (встроенная духовка)",
    "Visoki otvoreni (police)": "Высокий открытый (полки)",
    "Gornji 2. red (1 vrata)": "Верхний 2-й ряд (1 дверь)",
    "Gornji 2. red (2 vrata)": "Верхний 2-й ряд (2 двери)",
    "Gornji 2. red (otvoreno / police)": "Верхний 2-й ряд (открытый / полки)",
    "Visoki (staklena vrata - vitrina)": "Высокий (стеклянная витрина)",
    "Donji (sortirnik / kante za otpad)": "Нижний (сортировка / ведра)",
    "Filer panel (popunjaÄ prostora)": "Доборная панель",
    "Zavrsna bocna ploca": "Боковая завершающая панель",
}

_TEMPLATE_LABELS_ZHCN = {
    "Donji (1 vrata)": "地柜（1门）",
    "Donji (2 vrata)": "地柜（2门）",
    "Donji (fioke 2-4)": "地柜（抽屉 2-4）",
    "Donji (fioke)": "地柜（抽屉）",
    "Donji (vrata + fioka)": "地柜（门 + 抽屉）",
    "Donji (masina za sudove)": "地柜（洗碗机）",
    "Donji (masina za sudove - samostojeca)": "地柜（独立式洗碗机）",
    "Donji (kuhinjska jedinica: rerna + ploca za kuvanje)": "烤箱 + 灶台 + 抽屉",
    "Donji (sporet - samostojeci)": "地柜（独立式炉灶）",
    "Donji (sudopera)": "地柜（水槽）",
    "Donji uski (flase/ulja/zacini)": "窄地柜（瓶罐/香料）",
    "Donji coskasti (L-oblik)": "转角地柜（L形）",
    "Donji coskasti (dijagonalni front)": "转角地柜（斜面门板）",
    "Donji otvoreni (bez vrata)": "开放地柜（无门）",
    "Gornji (1 vrata)": "吊柜（1门）",
    "Gornji (2 vrata)": "吊柜（2门）",
    "Gornji (staklena vrata)": "吊柜（玻璃门）",
    "Gornji otvoreni (police)": "开放吊柜（层板）",
    "Gornji (podizna vrata / klapna)": "吊柜（上翻门）",
    "Gornji coskasti": "转角吊柜",
    "Gornji coskasti (dijagonalni front)": "转角吊柜（斜面门板）",
    "Gornji uski (zacini)": "窄吊柜（香料）",
    "Gornji (aspirator / napa)": "吊柜（油烟机）",
    "Gornji (mikrotalasna)": "吊柜（微波炉）",
    "Visoki (frizider integrisani)": "高柜（嵌入式冰箱）",
    "Visoki (frizider - samostojeci)": "高柜（独立式冰箱）",
    "Visoki (frizider + zamrzivac)": "高柜（冰箱 + 冷冻柜）",
    "Visoki kolona (rerna + mikrotalasna)": "高柜柱（烤箱 + 微波炉）",
    "Visoki ostava / spajz (police)": "高储物柜（层板）",
    "Visoki (vrata)": "高柜（门板）",
    "Visoki (ugradna rerna)": "高柜（嵌入式烤箱）",
    "Visoki otvoreni (police)": "开放高柜（层板）",
    "Gornji 2. red (1 vrata)": "第2排吊柜（1门）",
    "Gornji 2. red (2 vrata)": "第2排吊柜（2门）",
    "Gornji 2. red (otvoreno / police)": "第2排吊柜（开放 / 层板）",
    "Visoki (staklena vrata - vitrina)": "高柜（玻璃展示门）",
    "Donji (sortirnik / kante za otpad)": "地柜（垃圾分类桶）",
    "Filer panel (popunjaÄ prostora)": "填充板",
    "Zavrsna bocna ploca": "侧封板",
}

_TEMPLATE_LABELS_HI = {
    "Donji (1 vrata)": "निचला (1 दरवाज़ा)",
    "Donji (2 vrata)": "निचला (2 दरवाज़े)",
    "Donji (fioke 2-4)": "निचला (दराज़ 2-4)",
    "Donji (fioke)": "निचला (दराज़)",
    "Donji (vrata + fioka)": "निचला (दरवाज़े + दराज़)",
    "Donji (masina za sudove)": "निचला (डिशवॉशर)",
    "Donji (masina za sudove - samostojeca)": "निचला (फ्रीस्टैंडिंग डिशवॉशर)",
    "Donji (kuhinjska jedinica: rerna + ploca za kuvanje)": "ओवन + हॉब + दराज़",
    "Donji (sporet - samostojeci)": "निचला (फ्रीस्टैंडिंग स्टोव)",
    "Donji (sudopera)": "निचला (सिंक)",
    "Donji uski (flase/ulja/zacini)": "संकरा निचला (बोतलें/मसाले)",
    "Donji coskasti (L-oblik)": "कोना निचला (L आकार)",
    "Donji coskasti (dijagonalni front)": "कोना निचला (तिरछा फ्रंट)",
    "Donji otvoreni (bez vrata)": "खुला निचला (बिना दरवाज़े)",
    "Gornji (1 vrata)": "ऊपरी (1 दरवाज़ा)",
    "Gornji (2 vrata)": "ऊपरी (2 दरवाज़े)",
    "Gornji (staklena vrata)": "ऊपरी (काँच के दरवाज़े)",
    "Gornji otvoreni (police)": "खुला ऊपरी (शेल्फ)",
    "Gornji (podizna vrata / klapna)": "ऊपरी (लिफ्ट-अप दरवाज़ा)",
    "Gornji coskasti": "कोना ऊपरी",
    "Gornji coskasti (dijagonalni front)": "कोना ऊपरी (तिरछा फ्रंट)",
    "Gornji uski (zacini)": "संकरा ऊपरी (मसाले)",
    "Gornji (aspirator / napa)": "ऊपरी (हुड)",
    "Gornji (mikrotalasna)": "ऊपरी (माइक्रोवेव)",
    "Visoki (frizider integrisani)": "ऊँचा (बिल्ट-इन फ्रिज)",
    "Visoki (frizider - samostojeci)": "ऊँचा (फ्रीस्टैंडिंग फ्रिज)",
    "Visoki (frizider + zamrzivac)": "ऊँचा (फ्रिज + फ्रीज़र)",
    "Visoki kolona (rerna + mikrotalasna)": "ऊँचा कॉलम (ओवन + माइक्रोवेव)",
    "Visoki ostava / spajz (police)": "ऊँचा पैंट्री (शेल्फ)",
    "Visoki (vrata)": "ऊँचा (दरवाज़े)",
    "Visoki (ugradna rerna)": "ऊँचा (बिल्ट-इन ओवन)",
    "Visoki otvoreni (police)": "खुला ऊँचा (शेल्फ)",
    "Gornji 2. red (1 vrata)": "ऊपरी दूसरी पंक्ति (1 दरवाज़ा)",
    "Gornji 2. red (2 vrata)": "ऊपरी दूसरी पंक्ति (2 दरवाज़े)",
    "Gornji 2. red (otvoreno / police)": "ऊपरी दूसरी पंक्ति (खुला / शेल्फ)",
    "Visoki (staklena vrata - vitrina)": "ऊँचा (काँच शोकेस)",
    "Donji (sortirnik / kante za otpad)": "निचला (कचरा वर्गीकरण / डिब्बे)",
    "Filer panel (popunjaÄ prostora)": "फिलर पैनल",
    "Zavrsna bocna ploca": "अंतिम साइड पैनल",
}

_PALETTE_LABELS_SR = {str(v): str(k) for k, v in _PALETTE_LABELS_EN.items()}
_TEMPLATE_LABELS_SR = {str(v): str(k) for k, v in _TEMPLATE_LABELS_EN.items()}
_TEMPLATE_LABELS_SR.update({
    "Base (cooker - freestanding)": "Donji (sporet - samostojeci)",
    "Base (cooking unit: oven + hob)": "Donji (kuhinjska jedinica: rerna + ploca za kuvanje)",
    "Built-in oven + hob + drawer": "Donji (kuhinjska jedinica: rerna + ploca za kuvanje)",
})


def translate_palette_label(label: str, lang: str = "sr") -> str:
    _lang = str(lang or "sr").lower().strip()
    txt = str(label)
    _maps = {
        "en": _PALETTE_LABELS_EN,
        "es": _PALETTE_LABELS_ES,
        "pt-br": _PALETTE_LABELS_PTBR,
        "ru": _PALETTE_LABELS_RU,
        "zh-cn": _PALETTE_LABELS_ZHCN,
        "hi": _PALETTE_LABELS_HI,
    }
    if _lang in _maps:
        return _maps[_lang].get(txt, _PALETTE_LABELS_EN.get(txt, txt))
    return _PALETTE_LABELS_SR.get(txt, txt)


def translate_template_label(label: str, lang: str = "sr", label_i18n: dict | None = None) -> str:
    _lang = str(lang or "sr").lower().strip()
    txt = str(label)
    if isinstance(label_i18n, dict):
        _localized = label_i18n.get(_lang) or label_i18n.get(_lang.replace("_", "-"))
        if _localized:
            return str(_localized)
    _maps = {
        "en": _TEMPLATE_LABELS_EN,
        "es": _TEMPLATE_LABELS_ES,
        "pt-br": _TEMPLATE_LABELS_PTBR,
        "ru": _TEMPLATE_LABELS_RU,
        "zh-cn": _TEMPLATE_LABELS_ZHCN,
        "hi": _TEMPLATE_LABELS_HI,
    }
    if _lang in _maps:
        return _maps[_lang].get(txt, _TEMPLATE_LABELS_EN.get(txt, txt))
    return _TEMPLATE_LABELS_SR.get(txt, txt)


def get_palette_tabs(
    project_type: str,
    wardrobe_profile: str = "standard",
    kitchen_layout: str = "",
) -> list[dict]:
    _ = str(project_type or "kitchen").lower().strip()
    # Scope odluka 12.03.2026:
    # `krojna_lista_pro` je kitchen-only aplikacija.
    # TV / wardrobe / hallway / bathroom / office scenariji ostaju van aktivnog kataloga.
    base_tabs = copy.deepcopy(PALETTE_TABS[:4])
    if str(kitchen_layout or "").lower().strip() in _CORNER_LAYOUTS:
        base_tabs.append(copy.deepcopy(UGAONI_TAB))
    return base_tabs



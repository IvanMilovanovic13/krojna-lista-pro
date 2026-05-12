# -*- coding: utf-8 -*-
from __future__ import annotations

from io import BytesIO
import base64
import re
from pathlib import Path
import math
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from i18n import normalize_language_code, tr


_PDF_PHRASES: dict[str, dict[str, str]] = {
    "de": {
        "Cut List": "Zuschnittliste",
        "Summary - all cut parts": "Zusammenfassung - alle Zuschnittteile",
        "Project data": "Projektdaten",
        "Field": "Feld",
        "Value": "Wert",
        "What you take to the workshop - cutting": "Was du in die Werkstatt mitnimmst: Zuschnitt",
        "What you take to the workshop - edging": "Was du in die Werkstatt mitnimmst: Kanten",
        "What you take to the workshop - processing": "Was du in die Werkstatt mitnimmst: Bearbeitung",
        "Workshop instructions": "Werkstattanweisungen",
        "Material": "Material",
        "Thk.": "Stärke",
        "Length [mm]": "Länge [mm]",
        "Width [mm]": "Breite [mm]",
        "Edge": "Kante",
        "Qty": "Menge",
        "Wall": "Wand",
        "Module": "Modul",
        "Part": "Teil",
        "Note": "Hinweis",
        "Processing type": "Bearbeitungsart",
        "Operations": "Vorgänge",
        "Execution basis": "Ausführungsgrundlage",
        "Processing / note": "Bearbeitung / Hinweis",
        "Carcass (sides, bottom, top)": "Korpus (Seiten, Boden, Deckel)",
        "Back panels": "Rückwände",
        "Fronts": "Fronten",
        "Worktop and supports": "Arbeitsplatte und Stützen",
        "Plinth / toe kick": "Sockel",
        "By unit - details and assembly": "Nach Element - Details und Montage",
        "Label": "PartCode",
        "Where it goes": "Wo es hingehört",
        "Step": "Schritt",
        "Note for beginners": "Hinweis für Einsteiger",
        "Important part notes": "Wichtige Teilehinweise",
        "Check before assembly": "Vor der Montage prüfen",
        "Assembly parts map": "Montage-Teileplan",
        "Cut parts": "Zuschnittteile",
        "Required tools and hardware": "Benötigte Werkzeuge und Beschläge",
        "Assembly instructions": "Montageanleitung",
        "What you buy separately": "Was separat gekauft wird",
        "Ready-made products - not included in cutting": "Fertige Produkte — nicht im Zuschnitt enthalten",
        "Workflow order": "Ablauf",
        "What you do": "Eintrag",
        "Checklist before workshop": "Checkliste vor der Werkstatt",
        "Checklist before home assembly": "Checkliste vor der Montage",
        "Status": "Status",
        "Group": "Gruppe",
        "Name": "Name",
        "Type / Code": "Typ / Code",
        "Wall L": "Wandlänge",
        "Required": "Erforderlich",
        "Purchase": "Einkauf",
        "Field cut": "Bauseitiger Schnitt",
        "Joint": "Verbindung",
        "Cut-outs": "Ausschnitte",
        "Cut length": "Schnittlänge",
        "Cut width": "Schnittbreite",
        "Item": "Eintrag",
        "The labels in the 2D view use the same short label as the table and assembly steps.": "Die Beschriftungen im Bild sind aus dem echten PartCode gekürzt und stimmen deshalb direkt mit Tabelle und Montageschritten überein.",
        "The part label is the same in the image, table and text. Sort the parts by label first, then start assembly.": "Die Teilebezeichnung ist im Bild, in der Tabelle und im Text identisch. Sortiere die Teile zuerst nach Bezeichnung und beginne dann mit der Montage.",
        "Drill-driver or screwdriver": "Akkuschrauber oder Schraubendreher",
        "Tape measure": "Maßband",
        "Spirit level": "Wasserwaage",
        "Wall brackets / hanging hardware": "Wandhalter / Aufhängebeschläge",
        "Door hinges": "Topfscharniere",
        "Drawer runners": "Schubladenauszüge",
        "Lift-up mechanism": "Klappenbeschlag",
        "Glass-door hinges": "Scharniere für Glastüren",
        "Dishwasher front mounting kit": "Montageset für Geschirrspülerfront",
        "Wall plugs / screws according to wall type": "Dübel / Schrauben passend zur Wand",
        "Check that the number of parts matches the table.": "Prüfe, ob die Teileanzahl mit der Tabelle übereinstimmt.",
        "Separate carcass parts, fronts, backs and hardware before assembly.": "Trenne Korpusteile, Fronten, Rückwände und Beschläge vor der Montage.",
        "Check the edged sides so the front of the unit is oriented correctly.": "Prüfe die bekanteten Seiten, damit die Front des Elements korrekt ausgerichtet ist.",
        "Before drilling, check the wall type and choose suitable plugs and screws.": "Vor dem Bohren den Wandtyp prüfen und passende Dübel und Schrauben wählen.",
        "Before assembly, verify the service positions and appliance opening.": "Vor der Montage Installationspositionen und Geräteöffnung prüfen.",
        "A tall unit must always be planned for wall fixing.": "Ein Hochschrank muss immer für die Wandbefestigung vorgesehen werden.",
        "Checklist before workshop and assembly": "Checkliste vor Werkstatt und Montage",
    },
    "es": {
        "Cut List": "Lista de corte",
        "Summary - all cut parts": "Resumen - todas las piezas de corte",
        "Project data": "Datos del proyecto",
        "Field": "Campo",
        "Value": "Valor",
        "What you take to the workshop - cutting": "Qué llevas al taller - corte",
        "What you take to the workshop - edging": "Qué llevas al taller - canteado",
        "What you take to the workshop - processing": "Qué llevas al taller - mecanizado",
        "Workshop instructions": "Instrucciones para el taller",
        "Material": "Material",
        "Thk.": "Esp.",
        "Length [mm]": "Longitud [mm]",
        "Width [mm]": "Ancho [mm]",
        "Edge": "Canto",
        "Qty": "Cant.",
        "Wall": "Pared",
        "Module": "Módulo",
        "Part": "Pieza",
        "Note": "Nota",
        "Processing type": "Tipo de mecanizado",
        "Operations": "Operaciones",
        "Execution basis": "Base de ejecución",
        "Processing / note": "Mecanizado / nota",
        "Carcass (sides, bottom, top)": "Carcasa (laterales, base, tapa)",
        "Back panels": "Paneles traseros",
        "Fronts": "Frentes",
        "Worktop and supports": "Encimera y soportes",
        "Plinth / toe kick": "Zócalo",
        "By unit - details and assembly": "Por módulo - detalles y montaje",
        "Label": "Etiqueta",
        "Where it goes": "Dónde va",
        "Step": "Paso",
        "Note for beginners": "Nota para principiantes",
        "Important part notes": "Notas importantes sobre las piezas",
        "Check before assembly": "Revisar antes del montaje",
        "Assembly parts map": "Mapa de piezas para montaje",
        "Cut parts": "Piezas de corte",
        "Required tools and hardware": "Herramientas y herrajes necesarios",
        "Assembly instructions": "Instrucciones de montaje",
        "What you buy separately": "Qué compras por separado",
        "Ready-made products - not included in cutting": "Productos terminados - no entran en el corte",
        "Workflow order": "Orden de trabajo",
        "What you do": "Qué haces",
        "Checklist before workshop": "Checklist antes del taller",
        "Checklist before home assembly": "Checklist antes del montaje en casa",
        "Status": "Estado",
        "Drill-driver or screwdriver": "Atornillador o destornillador",
        "Tape measure": "Cinta métrica",
        "Spirit level": "Nivel",
        "Wall brackets / hanging hardware": "Soportes de pared / herrajes de colgado",
        "Door hinges": "Bisagras para puertas",
        "Drawer runners": "Guías de cajón",
        "Lift-up mechanism": "Mecanismo elevable",
        "Glass-door hinges": "Bisagras para puertas de vidrio",
        "Dishwasher front mounting kit": "Kit de montaje del frente de lavavajillas",
        "Wall plugs / screws according to wall type": "Tacos / tornillos según el tipo de pared",
        "Check that the number of parts matches the table.": "Comprueba que el número de piezas coincide con la tabla.",
        "Separate carcass parts, fronts, backs and hardware before assembly.": "Separa carcasa, frentes, traseras y herrajes antes del montaje.",
        "Check the edged sides so the front of the unit is oriented correctly.": "Comprueba los cantos para orientar correctamente el frente del módulo.",
        "Before drilling, check the wall type and choose suitable plugs and screws.": "Antes de taladrar, revisa el tipo de pared y elige tacos y tornillos adecuados.",
        "Before assembly, verify the service positions and appliance opening.": "Antes del montaje, verifica las posiciones de instalaciones y el hueco del aparato.",
        "A tall unit must always be planned for wall fixing.": "Un módulo alto siempre debe planificarse con fijación a pared.",
    },
    "pt-br": {
        "Cut List": "Lista de corte",
        "Summary - all cut parts": "Resumo - todas as peças de corte",
        "Project data": "Dados do projeto",
        "Field": "Campo",
        "Value": "Valor",
        "What you take to the workshop - cutting": "O que levar à marcenaria - corte",
        "What you take to the workshop - edging": "O que levar à marcenaria - orla",
        "What you take to the workshop - processing": "O que levar à marcenaria - usinagem",
        "Workshop instructions": "Instruções para a marcenaria",
        "Material": "Material",
        "Thk.": "Esp.",
        "Length [mm]": "Comprimento [mm]",
        "Width [mm]": "Largura [mm]",
        "Edge": "Orla",
        "Qty": "Qtd.",
        "Wall": "Parede",
        "Module": "Módulo",
        "Part": "Peça",
        "Note": "Nota",
        "Processing type": "Tipo de usinagem",
        "Operations": "Operações",
        "Execution basis": "Base de execução",
        "Processing / note": "Usinagem / nota",
        "Carcass (sides, bottom, top)": "Carcaça (laterais, fundo, topo)",
        "Back panels": "Painéis traseiros",
        "Fronts": "Frentes",
        "Worktop and supports": "Tampo e suportes",
        "Plinth / toe kick": "Soco",
        "By unit - details and assembly": "Por módulo - detalhes e montagem",
        "Label": "Etiqueta",
        "Where it goes": "Onde vai",
        "Step": "Passo",
        "Note for beginners": "Nota para iniciantes",
        "Important part notes": "Notas importantes das peças",
        "Check before assembly": "Verificar antes da montagem",
        "Assembly parts map": "Mapa de peças para montagem",
        "Cut parts": "Peças de corte",
        "Required tools and hardware": "Ferramentas e ferragens necessárias",
        "Assembly instructions": "Instruções de montagem",
        "What you buy separately": "O que comprar separadamente",
        "Ready-made products - not included in cutting": "Produtos prontos - não entram no corte",
        "Workflow order": "Ordem de trabalho",
        "What you do": "O que fazer",
        "Checklist before workshop": "Checklist antes da marcenaria",
        "Checklist before home assembly": "Checklist antes da montagem em casa",
        "Status": "Status",
        "Drill-driver or screwdriver": "Parafusadeira ou chave de fenda",
        "Tape measure": "Trena",
        "Spirit level": "Nível",
        "Wall brackets / hanging hardware": "Suportes de parede / ferragens de fixação",
        "Door hinges": "Dobradiças para portas",
        "Drawer runners": "Corrediças de gaveta",
        "Lift-up mechanism": "Mecanismo basculante",
        "Glass-door hinges": "Dobradiças para portas de vidro",
        "Dishwasher front mounting kit": "Kit de montagem da frente da lava-louças",
        "Wall plugs / screws according to wall type": "Buchas / parafusos conforme o tipo de parede",
        "Check that the number of parts matches the table.": "Verifique se o número de peças corresponde à tabela.",
        "Separate carcass parts, fronts, backs and hardware before assembly.": "Separe carcaça, frentes, fundos e ferragens antes da montagem.",
        "Check the edged sides so the front of the unit is oriented correctly.": "Verifique as bordas para orientar corretamente a frente do módulo.",
        "Before drilling, check the wall type and choose suitable plugs and screws.": "Antes de furar, verifique o tipo de parede e escolha buchas e parafusos adequados.",
        "Before assembly, verify the service positions and appliance opening.": "Antes da montagem, verifique as posições das instalações e o vão do aparelho.",
        "A tall unit must always be planned for wall fixing.": "Um módulo alto deve sempre ser planejado com fixação na parede.",
    },
    "ru": {
        "Cut List": "Карта раскроя",
        "Summary - all cut parts": "Сводка - все детали раскроя",
        "Project data": "Данные проекта",
        "Field": "Поле",
        "Value": "Значение",
        "What you take to the workshop - cutting": "Что передать в мастерскую - распил",
        "What you take to the workshop - edging": "Что передать в мастерскую - кромкование",
        "What you take to the workshop - processing": "Что передать в мастерскую - обработка",
        "Workshop instructions": "Инструкции для мастерской",
        "Material": "Материал",
        "Thk.": "Толщ.",
        "Length [mm]": "Длина [мм]",
        "Width [mm]": "Ширина [мм]",
        "Edge": "Кромка",
        "Qty": "Кол.",
        "Wall": "Стена",
        "Module": "Модуль",
        "Part": "Деталь",
        "Note": "Примечание",
        "Processing type": "Тип обработки",
        "Operations": "Операции",
        "Execution basis": "Основание выполнения",
        "Processing / note": "Обработка / примечание",
        "Carcass (sides, bottom, top)": "Корпус (боковины, дно, верх)",
        "Back panels": "Задние панели",
        "Fronts": "Фасады",
        "Worktop and supports": "Столешница и опоры",
        "Plinth / toe kick": "Цоколь",
        "By unit - details and assembly": "По модулям - детали и сборка",
        "Label": "Метка",
        "Where it goes": "Куда ставится",
        "Step": "Шаг",
        "Note for beginners": "Примечание для новичка",
        "Important part notes": "Важные примечания по деталям",
        "Check before assembly": "Проверить перед сборкой",
        "Assembly parts map": "Карта деталей для сборки",
        "Cut parts": "Детали раскроя",
        "Required tools and hardware": "Необходимые инструменты и фурнитура",
        "Assembly instructions": "Инструкция по сборке",
        "What you buy separately": "Что покупается отдельно",
        "Ready-made products - not included in cutting": "Готовые изделия - не входят в распил",
        "Workflow order": "Порядок работ",
        "What you do": "Что делать",
        "Checklist before workshop": "Чеклист перед мастерской",
        "Checklist before home assembly": "Чеклист перед домашней сборкой",
        "Status": "Статус",
        "Drill-driver or screwdriver": "Шуруповерт или отвертка",
        "Tape measure": "Рулетка",
        "Spirit level": "Уровень",
        "Wall brackets / hanging hardware": "Настенные крепления / подвесная фурнитура",
        "Door hinges": "Петли для дверей",
        "Drawer runners": "Направляющие для ящиков",
        "Lift-up mechanism": "Подъемный механизм",
        "Glass-door hinges": "Петли для стеклянных дверей",
        "Dishwasher front mounting kit": "Монтажный комплект фасада ПММ",
        "Wall plugs / screws according to wall type": "Дюбели / шурупы по типу стены",
        "Check that the number of parts matches the table.": "Проверьте, что количество деталей соответствует таблице.",
        "Separate carcass parts, fronts, backs and hardware before assembly.": "Перед сборкой отделите детали корпуса, фасады, задние панели и фурнитуру.",
        "Check the edged sides so the front of the unit is oriented correctly.": "Проверьте кромкованные стороны, чтобы правильно ориентировать перед модуля.",
        "Before drilling, check the wall type and choose suitable plugs and screws.": "Перед сверлением проверьте тип стены и выберите подходящие дюбели и шурупы.",
        "Before assembly, verify the service positions and appliance opening.": "Перед сборкой проверьте позиции коммуникаций и проем для прибора.",
        "A tall unit must always be planned for wall fixing.": "Высокий модуль обязательно должен крепиться к стене.",
    },
    "zh-cn": {
        "Cut List": "切割清单",
        "Summary - all cut parts": "汇总 - 所有切割件",
        "Project data": "项目数据",
        "Field": "字段",
        "Value": "值",
        "What you take to the workshop - cutting": "交给车间 - 切割",
        "What you take to the workshop - edging": "交给车间 - 封边",
        "What you take to the workshop - processing": "交给车间 - 加工",
        "Workshop instructions": "车间说明",
        "Material": "材料",
        "Thk.": "厚度",
        "Length [mm]": "长度 [mm]",
        "Width [mm]": "宽度 [mm]",
        "Edge": "封边",
        "Qty": "数量",
        "Wall": "墙",
        "Module": "模块",
        "Part": "部件",
        "Note": "备注",
        "Processing type": "加工类型",
        "Operations": "操作",
        "Execution basis": "执行依据",
        "Processing / note": "加工 / 备注",
        "Carcass (sides, bottom, top)": "柜体（侧板、底板、顶板）",
        "Back panels": "背板",
        "Fronts": "门板",
        "Worktop and supports": "台面和支撑",
        "Plinth / toe kick": "踢脚板",
        "By unit - details and assembly": "按模块 - 细节和组装",
        "Label": "标记",
        "Where it goes": "安装位置",
        "Step": "步骤",
        "Note for beginners": "新手提示",
        "Important part notes": "重要部件说明",
        "Check before assembly": "组装前检查",
        "Assembly parts map": "组装部件图",
        "Cut parts": "切割件",
        "Required tools and hardware": "所需工具和五金",
        "Assembly instructions": "组装说明",
        "What you buy separately": "需另行购买",
        "Ready-made products - not included in cutting": "成品 - 不包含在切割中",
        "Workflow order": "工作顺序",
        "What you do": "操作内容",
        "Checklist before workshop": "车间前检查表",
        "Checklist before home assembly": "家庭组装前检查表",
        "Status": "状态",
        "Drill-driver or screwdriver": "电动螺丝刀或螺丝刀",
        "Tape measure": "卷尺",
        "Spirit level": "水平仪",
        "Wall brackets / hanging hardware": "墙面支架 / 吊挂五金",
        "Door hinges": "门铰链",
        "Drawer runners": "抽屉滑轨",
        "Lift-up mechanism": "上翻机构",
        "Glass-door hinges": "玻璃门铰链",
        "Dishwasher front mounting kit": "洗碗机门板安装套件",
        "Wall plugs / screws according to wall type": "按墙体类型选择膨胀塞 / 螺丝",
        "Check that the number of parts matches the table.": "检查部件数量是否与表格一致。",
        "Separate carcass parts, fronts, backs and hardware before assembly.": "组装前分开柜体件、门板、背板和五金。",
        "Check the edged sides so the front of the unit is oriented correctly.": "检查封边侧，确保模块正面方向正确。",
        "Before drilling, check the wall type and choose suitable plugs and screws.": "钻孔前检查墙体类型，并选择合适的膨胀塞和螺丝。",
        "Before assembly, verify the service positions and appliance opening.": "组装前确认管线位置和电器开口。",
        "A tall unit must always be planned for wall fixing.": "高柜必须规划墙面固定。",
    },
    "hi": {
        "Cut List": "कट सूची",
        "Summary - all cut parts": "सारांश - सभी कटिंग भाग",
        "Project data": "प्रोजेक्ट डेटा",
        "Field": "फ़ील्ड",
        "Value": "मान",
        "What you take to the workshop - cutting": "कार्यशाला में ले जाने वाली चीज़ें - कटिंग",
        "What you take to the workshop - edging": "कार्यशाला में ले जाने वाली चीज़ें - एज बैंडिंग",
        "What you take to the workshop - processing": "कार्यशाला में ले जाने वाली चीज़ें - प्रोसेसिंग",
        "Workshop instructions": "कार्यशाला निर्देश",
        "Material": "सामग्री",
        "Thk.": "मोटाई",
        "Length [mm]": "लंबाई [mm]",
        "Width [mm]": "चौड़ाई [mm]",
        "Edge": "एज",
        "Qty": "मात्रा",
        "Wall": "दीवार",
        "Module": "मॉड्यूल",
        "Part": "भाग",
        "Note": "नोट",
        "Processing type": "प्रोसेसिंग प्रकार",
        "Operations": "ऑपरेशन",
        "Execution basis": "निष्पादन आधार",
        "Processing / note": "प्रोसेसिंग / नोट",
        "Carcass (sides, bottom, top)": "ढांचा (साइड, नीचे, ऊपर)",
        "Back panels": "पीछे के पैनल",
        "Fronts": "फ्रंट",
        "Worktop and supports": "वर्कटॉप और सपोर्ट",
        "Plinth / toe kick": "सोकल",
        "By unit - details and assembly": "मॉड्यूल अनुसार - विवरण और असेंबली",
        "Label": "लेबल",
        "Where it goes": "कहाँ लगेगा",
        "Step": "चरण",
        "Note for beginners": "शुरुआती उपयोगकर्ता के लिए नोट",
        "Important part notes": "भागों के महत्वपूर्ण नोट",
        "Check before assembly": "असेंबली से पहले जाँचें",
        "Assembly parts map": "असेंबली भागों का नक्शा",
        "Cut parts": "कटिंग भाग",
        "Required tools and hardware": "ज़रूरी औज़ार और हार्डवेयर",
        "Assembly instructions": "असेंबली निर्देश",
        "What you buy separately": "अलग से क्या खरीदना है",
        "Ready-made products - not included in cutting": "तैयार उत्पाद - कटिंग में शामिल नहीं",
        "Workflow order": "काम का क्रम",
        "What you do": "क्या करना है",
        "Checklist before workshop": "कार्यशाला से पहले चेकलिस्ट",
        "Checklist before home assembly": "घर पर असेंबली से पहले चेकलिस्ट",
        "Status": "स्थिति",
        "Drill-driver or screwdriver": "ड्रिल-driver या screwdriver",
        "Tape measure": "माप टेप",
        "Spirit level": "लेवल",
        "Wall brackets / hanging hardware": "दीवार ब्रैकेट / हैंगिंग हार्डवेयर",
        "Door hinges": "दरवाज़े के हिंग",
        "Drawer runners": "दराज़ स्लाइड",
        "Lift-up mechanism": "लिफ्ट-up मैकेनिज़्म",
        "Glass-door hinges": "काँच के दरवाज़े के हिंग",
        "Dishwasher front mounting kit": "डिशवॉशर फ्रंट mounting kit",
        "Wall plugs / screws according to wall type": "दीवार के प्रकार के अनुसार plug / screw",
        "Check that the number of parts matches the table.": "जाँचें कि भागों की संख्या तालिका से मेल खाती है।",
        "Separate carcass parts, fronts, backs and hardware before assembly.": "असेंबली से पहले ढांचा, फ्रंट, पीछे के पैनल और हार्डवेयर अलग रखें।",
        "Check the edged sides so the front of the unit is oriented correctly.": "एज लगी तरफ़ों की जाँच करें ताकि मॉड्यूल का फ्रंट सही दिशा में रहे।",
        "Before drilling, check the wall type and choose suitable plugs and screws.": "ड्रिलिंग से पहले दीवार का प्रकार जाँचें और सही plug/screw चुनें।",
        "Before assembly, verify the service positions and appliance opening.": "असेंबली से पहले service positions और appliance opening की जाँच करें।",
        "A tall unit must always be planned for wall fixing.": "लंबे मॉड्यूल को हमेशा दीवार से fix करने की योजना रखें।",
    },
}

_PDF_PHRASES["es"].update({
    "Cut length": "Longitud de corte",
    "Cut width": "Ancho de corte",
    "Cut-outs": "Recortes",
    "Depth": "Profundidad",
    "Field cut": "Corte en obra",
    "Group": "Grupo",
    "Image labels match the parts table: C = carcass, B = back, F = front, D = drawer.": "Las etiquetas de la imagen coinciden con la tabla: C = carcasa, B = trasera, F = frente, D = cajón.",
    "Instruction": "Instrucción",
    "Item": "Ítem",
    "Joint": "Unión",
    "Length": "Longitud",
    "Name": "Nombre",
    "Purchase": "Compra",
    "Required": "Necesario",
    "The labels in the 2D view use the same short label as the table and assembly steps.": "Las etiquetas de la vista 2D usan la misma marca corta que la tabla y los pasos de montaje.",
    "The part label is the same in the image, table and text. Sort the parts by label first, then start assembly.": "La etiqueta de la pieza es la misma en la imagen, la tabla y el texto. Ordena primero las piezas por etiqueta y luego inicia el montaje.",
    "Type / Code": "Tipo / código",
    "Wall L": "Long. pared",
    "Width": "Ancho",
    "How to use": "Cómo usar",
    "How to use this document": "Cómo usar este documento",
    "First check the main dimensions and materials": "Primero revisa las medidas principales y los materiales",
    "If you see an error here, do not order cutting yet.": "Si ves un error aquí, no encargues el corte todavía.",
    "If you see an error here, do not send the document to the workshop.": "Si ves un error aquí, no envíes el documento al taller.",
    "Use only the cutting, edging and machining sheets for the workshop": "Para el taller usa solo las hojas de corte, canto y mecanizado",
    "The workshop works by CUT dimensions and notes from those sheets.": "El taller trabaja con las medidas CUT y las notas de esas hojas.",
    "Take only the 'For workshop' section to the workshop": "Lleva al taller solo la sección 'Para el taller'",
    "The workshop works by CUT dimensions and notes from that section.": "El taller trabaja con las medidas CUT y las notas de esa sección.",
    "Use the 'For assembly' section during assembly": "Usa la sección 'Para montaje' durante el montaje",
    "Purchase ready-made appliances, hardware and tools separately": "Compra por separado electrodomésticos, herrajes y herramientas",
    "These items are not cut from board material.": "Estos elementos no se cortan de tablero.",
    "Use the guide and checklists during assembly": "Usa la guía y las listas de control durante el montaje",
    "Follow the order: carcasses, fronts, drawers, appliances, final check.": "Sigue el orden: cuerpos, frentes, cajones, electrodomésticos, revisión final.",
    "Overview": "Resumen",
    "Overview of all panels": "Resumen de todos los paneles",
    "Summary cut list of panels": "Lista de corte resumida de paneles",
    "Summary cut list - panels": "Lista de corte resumida - paneles",
    "Dimensions are finished sizes. CUT dimensions include edging allowances and workshop rules.": "Las medidas indicadas son finales. Las medidas CUT incluyen holguras de canto y reglas del taller.",
    "Dimensions are finished sizes, after edging.": "Las medidas son finales, después del canto.",
    "Cutting": "Corte",
    "By units": "Por módulos",
    "Detailed cut list by units": "Lista de corte detallada por módulos",
    "Detailed cut list - by units": "Lista de corte detallada por módulos",
    "Each part is shown by unit. Dimensions are finished sizes, after edging.": "Cada pieza se muestra por módulo. Las medidas son finales, después del canto.",
    "Carcass": "Cuerpo",
    "Carcass — sides, bottom, top": "Cuerpo — laterales, base y tapa",
    "Backs": "Fondos",
    "Back panels": "Paneles traseros",
    "Drawers": "Cajones",
    "Drawer box": "Caja de cajón",
    "Worktop": "Encimera",
    "Worktop spec": "Especificación de encimera",
    "WORKTOP SPECIFICATION": "ESPECIFICACIÓN DE ENCIMERA",
    "Plinth": "Zócalo",
    "Plinths and trims": "Zócalos y remates",
    "Hardware": "Herrajes",
    "Hardware and consumables": "Herrajes y consumibles",
    "Work order": "Orden de trabajo",
    "Workshop cutting": "Corte - taller",
    "Workshop edging": "Cantos - taller",
    "Workshop machining": "Mecanizado - taller",
    "Workshop packet - cutting": "Paquete de taller - corte",
    "Workshop packet - edging": "Paquete de taller - cantos",
    "Workshop packet - machining": "Paquete de taller - mecanizado",
    "Workshop note": "Nota para el taller",
    "Workshop packet for board material": "Paquete de taller para tableros",
    "Shopping": "Compras",
    "Shopping list": "Lista de compras",
    "Ready-made": "Comprado listo",
    "Purchased ready-made": "Comprado listo",
    "Guide": "Guía",
    "Quick user guide": "Guía rápida del usuario",
    "Home checklist": "Checklist de casa",
    "Checklist before assembly": "Checklist antes del montaje",
    "Checklist before home assembly": "Checklist antes del montaje en casa",
    "FOR CUSTOMER": "PARA EL CLIENTE",
    "FOR WORKSHOP": "PARA EL TALLER",
    "FOR ASSEMBLY": "PARA MONTAJE",
    "Beginner legend": "Leyenda para principiantes",
    "The name of the panel or unit part.": "Nombre del panel o pieza del módulo.",
    "How many pieces of that part are needed.": "Cantidad necesaria de esa pieza.",
    "Panel thickness in millimeters.": "Espesor del panel en milímetros.",
    "Finished part dimensions.": "Medidas finales de la pieza.",
    "What the part is made of.": "Material de la pieza.",
    "Orientation": "Orientación",
    "Board or grain direction.": "Dirección de veta o tablero.",
    "Which edges get edge banding.": "Qué cantos reciben tapacanto.",
    "L1/L2 are long edges, K1/K2 are short edges.": "L1/L2 son cantos largos, K1/K2 son cantos cortos.",
    "1 = edged, 0 = not edged.": "1 = con canto, 0 = sin canto.",
    "Workshop size before final processing, where applicable.": "Medida de taller antes del mecanizado final, cuando aplica.",
    "Size used by the workshop before final processing.": "Medida que usa el taller antes del mecanizado final.",
    "Edge that receives edge banding.": "Canto que recibe tapacanto.",
    "How many pieces the workshop should prepare.": "Cuántas piezas debe preparar el taller.",
    "Extra instruction for cutting, edging or machining.": "Instrucción adicional para corte, canto o mecanizado.",
    "Project coordinates": "Coordenadas del proyecto",
    "Wall (L x H)": "Pared (L x H)",
    "Legs": "Patas",
    "Base carcass height": "Altura del cuerpo bajo",
    "Worktop thickness": "Espesor de encimera",
    "Working height (total)": "Altura de trabajo total",
    "Use this section to review the main dimensions, important panels and overall project readiness.": "Usa esta sección para revisar medidas principales, paneles importantes y preparación general del proyecto.",
    "Image labels use the same labels as the table and steps.": "Las etiquetas de la imagen usan las mismas marcas que la tabla y los pasos.",
    "Materials": "Materiales",
    "Generated": "Generado",
    "Workshop checklist": "Checklist antes del taller",
    "Grain": "Veta",
    "CUT Length": "Longitud CUT",
    "CUT Width": "Ancho CUT",
    "FIN Length": "Longitud final",
    "FIN Width": "Ancho final",
    "Check that the material and thickness values are correct for carcass, fronts and backs": "Revisa que los materiales y espesores sean correctos para cuerpo, frentes y fondos",
    "Check that all CUT dimensions and quantities are listed": "Revisa que todas las medidas CUT y cantidades estén indicadas",
    "Check edge banding on every edge before sending to the workshop": "Revisa el canto de cada borde antes de enviar al taller",
    "Check that fronts, backs, plinths and special panels are included": "Revisa que estén incluidos frentes, fondos, zócalos y paneles especiales",
    "Check that all ready-made purchased items are separated from cut parts": "Revisa que todos los elementos comprados listos estén separados de las piezas de corte",
    "Check all openings and special machining for services and ventilation": "Revisa todos los huecos y mecanizados especiales para instalaciones y ventilación",
    "Check that the shopping list includes hardware, consumables and tools": "Revisa que la lista de compras incluya herrajes, consumibles y herramientas",
    "Before home assembly": "Antes del montaje en casa",
    "Count all cut panels and compare them against the list": "Cuenta todos los paneles cortados y compáralos con la lista",
    "Sort parts by unit before starting assembly": "Ordena las piezas por módulo antes de empezar el montaje",
    "Check that all hardware, appliances and tools have been purchased": "Revisa que se hayan comprado todos los herrajes, electrodomésticos y herramientas",
    "Assemble the carcasses first, then doors and drawers, and only then the appliances": "Monta primero los cuerpos, luego puertas y cajones, y solo después los electrodomésticos",
    "Sort parts by unit on site": "Ordena las piezas por módulo en obra",
    "Separate carcass parts first, then fronts, then hardware": "Separa primero piezas de cuerpo, luego frentes y después herrajes",
    "Assemble the carcasses first, then doors, drawers and appliances": "Monta primero los cuerpos, luego puertas, cajones y electrodomésticos",
    "Always secure tall and wall units to the wall": "Fija siempre a la pared los módulos altos y colgantes",
})

_PDF_PHRASES["de"].update({
    "How to use": "Verwendung",
    "How to use this document": "So verwendest du dieses Dokument",
    "First check the main dimensions and materials": "Prüfe zuerst die Hauptmaße und Materialien",
    "If you see an error here, do not order cutting yet.": "Wenn du hier einen Fehler siehst, bestelle den Zuschnitt noch nicht.",
    "If you see an error here, do not send the document to the workshop.": "Wenn du hier einen Fehler siehst, sende das Dokument noch nicht in die Werkstatt.",
    "Use only the cutting, edging and machining sheets for the workshop": "Für die Werkstatt nur die Tabellen für Zuschnitt, Kanten und Bearbeitung verwenden",
    "The workshop works by CUT dimensions and notes from those sheets.": "Die Werkstatt arbeitet nach CUT-Maßen und den Hinweisen aus diesen Tabellen.",
    "Take only the 'For workshop' section to the workshop": "Nimm nur den Abschnitt 'Für die Werkstatt' mit in die Werkstatt",
    "The workshop works by CUT dimensions and notes from that section.": "Die Werkstatt arbeitet nach den CUT-Maßen und Hinweisen aus diesem Abschnitt.",
    "Use the 'For assembly' section during assembly": "Verwende den Abschnitt 'Für die Montage' während der Montage",
    "Purchase ready-made appliances, hardware and tools separately": "Fertiggeräte, Beschläge und Werkzeuge separat beschaffen",
    "These items are not cut from board material.": "Diese Teile werden nicht aus Plattenmaterial zugeschnitten.",
    "Use the guide and checklists during assembly": "Verwende Anleitung und Checklisten während der Montage",
    "Follow the order: carcasses, fronts, drawers, appliances, final check.": "Reihenfolge: Korpusse, Fronten, Schubladen, Geräte, Endkontrolle.",
    "Overview": "Überblick",
    "Overview of all panels": "Überblick aller Platten",
    "Summary cut list of panels": "Zusammengefasste Zuschnittliste der Platten",
    "Summary cut list - panels": "Zuschnitt-Übersicht - Platten",
    "Dimensions are finished sizes. CUT dimensions include edging allowances and workshop rules.": "Die Maße sind Fertigmaße. CUT-Maße enthalten Kantenzugaben und Werkstattregeln.",
    "Dimensions are finished sizes, after edging.": "Die Maße sind Fertigmaße nach dem Bekanten.",
    "Cutting": "Zuschnitt",
    "By units": "Nach Elementen",
    "Detailed cut list by units": "Detaillierte Zuschnittliste nach Elementen",
    "Detailed cut list - by units": "Detaillierte Zuschnittliste - nach Elementen",
    "Each part is shown by unit. Dimensions are finished sizes, after edging.": "Jedes Teil wird je Element gezeigt. Die Maße sind Fertigmaße nach dem Bekanten.",
    "Carcass": "Korpus",
    "Carcass — sides, bottom, top": "Korpus — Seiten, Boden, Deckel",
    "Backs": "Rückwände",
    "Back panels": "Rückwandplatten",
    "Drawers": "Schubladen",
    "Drawer box": "Schubladenkasten",
    "Worktop": "Arbeitsplatte",
    "Worktop spec": "Arbeitsplatten-Spezifikation",
    "WORKTOP SPECIFICATION": "ARBEITSPLATTEN-SPEZIFIKATION",
    "Plinth": "Sockel",
    "Plinths and trims": "Sockel und Abschlussleisten",
    "Hardware": "Beschläge",
    "Hardware and consumables": "Beschläge und Verbrauchsmaterial",
    "Work order": "Arbeitsauftrag",
    "Workshop cutting": "Werkstatt - Zuschnitt",
    "Workshop edging": "Werkstatt - Kanten",
    "Workshop machining": "Werkstatt - Bearbeitung",
    "Workshop packet - cutting": "Werkstattpaket - Zuschnitt",
    "Workshop packet - edging": "Werkstattpaket - Kanten",
    "Workshop packet - machining": "Werkstattpaket - Bearbeitung",
    "Workshop note": "Werkstatt-Hinweis",
    "Workshop packet for board material": "Werkstattpaket für Plattenmaterial",
    "Shopping": "Einkauf",
    "Shopping list": "Einkaufsliste",
    "Ready-made": "Fertig gekauft",
    "Purchased ready-made": "Fertig gekauft",
    "Guide": "Anleitung",
    "Quick user guide": "Kurzanleitung",
    "Workshop checklist": "Checkliste für die Werkstatt",
    "Home checklist": "Checkliste für zu Hause",
    "Checklist before assembly": "Checkliste vor der Montage",
    "Checklist before home assembly": "Checkliste vor der Montage zu Hause",
    "FOR CUSTOMER": "FÜR DEN KUNDEN",
    "FOR WORKSHOP": "FÜR DIE WERKSTATT",
    "FOR ASSEMBLY": "FÜR DIE MONTAGE",
    "Beginner legend": "Legende für Einsteiger",
    "The name of the panel or unit part.": "Name der Platte oder des Elementteils.",
    "How many pieces of that part are needed.": "Wie viele Stück von diesem Teil benötigt werden.",
    "Panel thickness in millimeters.": "Plattenstärke in Millimetern.",
    "Finished part dimensions.": "Fertigmaße des Teils.",
    "What the part is made of.": "Material des Teils.",
    "Orientation": "Ausrichtung",
    "Board or grain direction.": "Platten- oder Faserrichtung.",
    "Which edges get edge banding.": "Welche Kanten bekantet werden.",
    "L1/L2 are long edges, K1/K2 are short edges.": "L1/L2 sind lange Kanten, K1/K2 kurze Kanten.",
    "1 = edged, 0 = not edged.": "1 = bekantet, 0 = nicht bekantet.",
    "Workshop size before final processing, where applicable.": "Werkstattmaß vor der Endbearbeitung, falls anwendbar.",
    "Size used by the workshop before final processing.": "Maß, das die Werkstatt vor der Endbearbeitung verwendet.",
    "Edge that receives edge banding.": "Kante, die eine Bekantung erhält.",
    "How many pieces the workshop should prepare.": "Wie viele Stück die Werkstatt vorbereiten soll.",
    "Extra instruction for cutting, edging or machining.": "Zusätzliche Anweisung für Zuschnitt, Kanten oder Bearbeitung.",
    "Project coordinates": "Projektkoordinaten",
    "Wall (L x H)": "Wand (L x H)",
    "Legs": "Füße",
    "Base carcass height": "Höhe Unterkorpus",
    "Worktop thickness": "Arbeitsplattenstärke",
    "Working height (total)": "Arbeitshöhe (gesamt)",
    "Use this section to review the main dimensions, important panels and overall project readiness.": "In diesem Abschnitt prüfst du Hauptmaße, wichtige Platten und die allgemeine Projektbereitschaft.",
    "Image labels use the same labels as the table and steps.": "Bildkennzeichnungen verwenden dieselben Kürzel wie Tabelle und Montageschritte.",
    "Materials": "Materialien",
    "Generated": "Erstellt",
    "Grain": "Faserrichtung",
    "CUT Length": "CUT-Länge",
    "CUT Width": "CUT-Breite",
    "FIN Length": "FIN-Länge",
    "FIN Width": "FIN-Breite",
    "Check that the material and thickness values are correct for carcass, fronts and backs": "Prüfe, ob Material und Stärken für Korpus, Fronten und Rückwände korrekt sind",
    "Check that all CUT dimensions and quantities are listed": "Prüfe, ob alle CUT-Maße und Mengen aufgeführt sind",
    "Check edge banding on every edge before sending to the workshop": "Prüfe jede Bekantung, bevor das Projekt in die Werkstatt geht",
    "Check that fronts, backs, plinths and special panels are included": "Prüfe, ob Fronten, Rückwände, Sockel und Sonderplatten enthalten sind",
    "Check that all ready-made purchased items are separated from cut parts": "Prüfe, ob alle Fertigprodukte von den Zuschnittteilen getrennt sind",
    "Check all openings and special machining for services and ventilation": "Prüfe alle Öffnungen und Sonderbearbeitungen für Installationen und Belüftung",
    "Check that the shopping list includes hardware, consumables and tools": "Prüfe, ob die Einkaufsliste Beschläge, Verbrauchsmaterial und Werkzeuge enthält",
    "Before home assembly": "Vor der Montage zu Hause",
    "Count all cut panels and compare them against the list": "Zähle alle zugeschnittenen Platten und vergleiche sie mit der Liste",
    "Sort parts by unit before starting assembly": "Sortiere die Teile nach Elementen, bevor du mit der Montage beginnst",
    "Check that all hardware, appliances and tools have been purchased": "Prüfe, ob alle Beschläge, Geräte und Werkzeuge beschafft wurden",
    "Assemble the carcasses first, then doors and drawers, and only then the appliances": "Montiere zuerst die Korpusse, dann Türen und Schubladen und erst danach die Geräte",
    "Sort parts by unit on site": "Sortiere die Teile vor Ort nach Elementen",
    "Separate carcass parts first, then fronts, then hardware": "Trenne zuerst Korpusteile, dann Fronten, dann Beschläge",
    "Assemble the carcasses first, then doors, drawers and appliances": "Montiere zuerst die Korpusse, dann Türen, Schubladen und Geräte",
    "Always secure tall and wall units to the wall": "Hochschränke und Hängeschränke immer an der Wand sichern",
})

_PDF_PHRASES["pt-br"].update({
    "How to use": "Como usar",
    "How to use this document": "Como usar este documento",
    "First check the main dimensions and materials": "Primeiro confira as medidas principais e os materiais",
    "If you see an error here, do not order cutting yet.": "Se encontrar um erro aqui, ainda não encomende o corte.",
    "If you see an error here, do not send the document to the workshop.": "Se encontrar um erro aqui, não envie o documento à marcenaria.",
    "Use only the cutting, edging and machining sheets for the workshop": "Use apenas as abas de corte, bordas e usinagem para a marcenaria",
    "The workshop works by CUT dimensions and notes from those sheets.": "A marcenaria trabalha pelas medidas CUT e pelas notas dessas abas.",
    "Take only the 'For workshop' section to the workshop": "Leve à marcenaria apenas a seção 'Para a marcenaria'",
    "The workshop works by CUT dimensions and notes from that section.": "A marcenaria trabalha pelas medidas CUT e pelas notas dessa seção.",
    "Use the 'For assembly' section during assembly": "Use a seção 'Para montagem' durante a montagem",
    "Purchase ready-made appliances, hardware and tools separately": "Compre separadamente eletrodomésticos prontos, ferragens e ferramentas",
    "These items are not cut from board material.": "Esses itens não são cortados em chapa.",
    "Use the guide and checklists during assembly": "Use o guia e as listas durante a montagem",
    "Follow the order: carcasses, fronts, drawers, appliances, final check.": "Siga a ordem: corpos, frentes, gavetas, eletrodomésticos, conferência final.",
    "Overview": "Visão geral",
    "Overview of all panels": "Visão geral de todos os painéis",
    "Summary cut list of panels": "Lista de corte resumida dos painéis",
    "Summary cut list - panels": "Lista de corte resumida - painéis",
    "Dimensions are finished sizes. CUT dimensions include edging allowances and workshop rules.": "As medidas finais estão indicadas. As medidas CUT incluem as regras de borda e de marcenaria.",
    "Dimensions are finished sizes, after edging.": "As medidas são finais, depois da aplicação de borda.",
    "Cutting": "Corte",
    "By units": "Por módulos",
    "Detailed cut list by units": "Lista de corte detalhada por módulos",
    "Detailed cut list - by units": "Lista de corte detalhada por módulos",
    "Each part is shown by unit. Dimensions are finished sizes, after edging.": "Cada peça é mostrada por módulo. As medidas são finais, depois da aplicação de borda.",
    "Carcass": "Corpo",
    "Backs": "Fundos",
    "Drawers": "Gavetas",
    "Drawer box": "Caixa da gaveta",
    "Worktop": "Bancada",
    "Worktop spec": "Especificação da bancada",
    "Plinth": "Rodapé",
    "Plinths and trims": "Rodapés e perfis",
    "Hardware": "Ferragens",
    "Hardware and consumables": "Ferragens e consumíveis",
    "Work order": "Ordem de serviço",
    "Workshop cutting": "Corte - marcenaria",
    "Workshop edging": "Bordas - marcenaria",
    "Workshop machining": "Usinagem - marcenaria",
    "Workshop packet - cutting": "Pacote da marcenaria - corte",
    "Workshop packet - edging": "Pacote da marcenaria - bordas",
    "Workshop packet - machining": "Pacote da marcenaria - usinagem",
    "Workshop note": "Nota para a marcenaria",
    "Shopping": "Compras",
    "Shopping list": "Lista de compras",
    "Ready-made": "Comprado pronto",
    "Purchased ready-made": "Comprado pronto",
    "Guide": "Guia",
    "Quick user guide": "Guia rápido do usuário",
    "Workshop checklist": "Lista da marcenaria",
    "Home checklist": "Lista de montagem em casa",
    "Checklist before assembly": "Lista de conferência antes da montagem",
    "Checklist before workshop and assembly": "Lista de conferência antes da marcenaria e montagem",
    "Before going to the workshop": "Antes de ir à marcenaria",
    "Before home assembly": "Antes da montagem em casa",
    "FOR CUSTOMER": "PARA O CLIENTE",
    "FOR WORKSHOP": "PARA A MARCENARIA",
    "FOR ASSEMBLY": "PARA MONTAGEM",
    "Use this section to review the main dimensions, important panels and overall project readiness.": "Use esta seção para conferir as medidas principais, os painéis importantes e se o projeto está pronto para os próximos passos.",
    "Take this section to the workshop. The workshop works by CUT dimensions, edging notes and machining notes from these tables.": "Leve esta seção à marcenaria. A marcenaria trabalha pelas medidas CUT, notas de borda e notas de usinagem destas tabelas.",
    "Workshop packet for board material": "Pacote da marcenaria para material em chapa",
    "This goes to the workshop: cutting by CUT dimensions, edging by table, and machining by notes.": "Isto vai para a marcenaria: corte pelas medidas CUT, bordas pela tabela e usinagens pelas notas.",
    "Cutting table": "Tabela de corte",
    "Edging table": "Tabela de bordas",
    "Machining table": "Tabela de usinagem",
    "Worktop specification": "Especificação da bancada",
    "WORKTOP SPECIFICATION": "ESPECIFICAÇÃO DA BANCADA",
    "The workshop works strictly by CUT dimensions. Final trimming and fitting are done on site.": "A marcenaria trabalha estritamente pelas medidas CUT. O corte final e o ajuste são feitos na obra.",
    "Note: appliances, sink, tap, trap, and similar items are purchased as ready-made products and are not part of the cutting list.": "Nota: eletrodomésticos, pia, torneira, sifão e itens semelhantes são comprados prontos e não fazem parte da lista de corte.",
    "Use this section for assembly order, part orientation and final checklists.": "Use esta seção para a ordem de montagem, orientação das peças e listas finais de conferência.",
    "Assembly map by unit (part orientation)": "Mapa de montagem por módulo (orientação das peças)",
    "Each unit links the image, part labels, table and assembly order.": "Cada módulo liga a imagem, as etiquetas das peças, a tabela e a ordem de montagem.",
    "Image labels use the same labels as the table and steps.": "As etiquetas da imagem usam as mesmas etiquetas da tabela e dos passos.",
    "Label legend": "Legenda das etiquetas",
    "Beginner legend": "Legenda para iniciantes",
    "C = carcass, B = back, F = front, D = drawer": "C = corpo, B = fundo, F = frente, D = gaveta",
    "Critical warnings before production": "Alertas críticos antes da produção",
    "These are items you purchase separately and they are not part of cutting.": "Estes são itens comprados separadamente e não fazem parte do corte.",
    "Purchased ready-made - not included in cutting": "Comprado pronto - não entra no corte",
    "Cut length": "Comprimento de corte",
    "Cut width": "Largura de corte",
    "CUT Length": "Comprimento CUT",
    "CUT Width": "Largura CUT",
    "FIN Length": "Comprimento final",
    "FIN Width": "Largura final",
    "Cut-outs": "Recortes",
    "Depth": "Profundidade",
    "Field cut": "Corte em obra",
    "Group": "Grupo",
    "Image labels match the parts table: C = carcass, B = back, F = front, D = drawer.": "As etiquetas da imagem correspondem à tabela: C = carcaça, B = fundo, F = frente, D = gaveta.",
    "Instruction": "Instrução",
    "Item": "Item",
    "Joint": "Emenda",
    "Length": "Comprimento",
    "Name": "Nome",
    "Purchase": "Compra",
    "Required": "Necessário",
    "The labels in the 2D view use the same short label as the table and assembly steps.": "As etiquetas na vista 2D usam a mesma marca curta da tabela e dos passos de montagem.",
    "The part label is the same in the image, table and text. Sort the parts by label first, then start assembly.": "A etiqueta da peça é a mesma na imagem, na tabela e no texto. Separe primeiro as peças por etiqueta e depois inicie a montagem.",
    "Type / Code": "Tipo / código",
    "Wall L": "Comp. parede",
    "Width": "Largura",
    "Generated": "Gerado",
    "What you do": "O que fazer",
    "Step": "Passo",
    "Qty": "Qtd.",
    "Part": "Peça",
    "Position": "Posição",
    "Module": "Módulo",
    "Wall": "Parede",
    "Material": "Material",
    "Edge": "Borda",
    "Grain": "Veio",
    "Note": "Nota",
    "Value": "Valor",
    "Field": "Campo",
    "Category": "Categoria",
    "Processing type": "Tipo de usinagem",
    "Operations": "Operações",
    "Execution basis": "Base de execução",
    "Processing / note": "Usinagem / nota",
    "Project coordinates": "Coordenadas do projeto",
    "Wall (L x H)": "Parede (C x A)",
    "Legs": "Pés",
    "Base carcass height": "Altura do corpo inferior",
    "Worktop thickness": "Espessura da bancada",
    "Working height (total)": "Altura de trabalho (total)",
    "The name of the panel. Use the same name when sorting parts.": "Nome do painel. Use o mesmo nome ao separar as peças.",
    "Panel thickness in millimetres.": "Espessura do painel em milímetros.",
    "Finished visible length after edging and trimming.": "Comprimento final visível após borda e ajuste.",
    "Finished visible width after edging and trimming.": "Largura final visível após borda e ajuste.",
    "Quantity of identical panels.": "Quantidade de painéis iguais.",
    "Edge banding required on the marked edges.": "Fita de borda necessária nas bordas marcadas.",
    "Extra note for workshop or assembly.": "Nota adicional para a marcenaria ou montagem.",
    "Part label used in the drawing and assembly steps.": "Etiqueta da peça usada no desenho e nos passos de montagem.",
    "The name of the panel or unit part.": "Nome do painel ou da peça do módulo.",
    "How many pieces of that part are needed.": "Quantidade necessária dessa peça.",
    "Panel thickness.": "Espessura do painel.",
    "Panel thickness in millimeters.": "Espessura do painel em milímetros.",
    "Final visible length.": "Comprimento final visível.",
    "Final visible width.": "Largura final visível.",
    "Finished part dimensions.": "Medidas finais da peça.",
    "Length / Width": "Comprimento / Largura",
    "What the part is made of.": "Material usado na peça.",
    "Orientation": "Orientação",
    "How many pieces the workshop should prepare.": "Quantas peças a marcenaria deve preparar.",
    "Board or grain direction.": "Sentido do veio ou do padrão da chapa.",
    "Which edges get edge banding.": "Quais bordas recebem fita de borda.",
    "L1/L2 are long edges, K1/K2 are short edges.": "L1/L2 são bordas longas; K1/K2 são bordas curtas.",
    "1 = edged, 0 = not edged.": "1 = com borda, 0 = sem borda.",
    "Workshop size before final processing, where applicable.": "Medida de marcenaria antes do acabamento final, quando aplicável.",
    "Extra instruction for cutting, edging or machining.": "Instrução extra para corte, borda ou usinagem.",
    "Profile": "Perfil",
    "Materials": "Materiais",
    "Standard": "Padrão",
})

_PDF_PHRASES["ru"].update({
    "Cut length": "Длина реза",
    "Cut width": "Ширина реза",
    "Cut-outs": "Вырезы",
    "Depth": "Глубина",
    "Field cut": "Подрезка на месте",
    "Group": "Группа",
    "Image labels match the parts table: C = carcass, B = back, F = front, D = drawer.": "Метки на изображении соответствуют таблице: C = корпус, B = задняя панель, F = фасад, D = ящик.",
    "Instruction": "Инструкция",
    "Item": "Позиция",
    "Joint": "Стык",
    "Length": "Длина",
    "Name": "Название",
    "Purchase": "Закупка",
    "Required": "Требуется",
    "The labels in the 2D view use the same short label as the table and assembly steps.": "Метки на 2D-виде используют ту же короткую маркировку, что таблица и шаги сборки.",
    "The part label is the same in the image, table and text. Sort the parts by label first, then start assembly.": "Метка детали одинакова на изображении, в таблице и в тексте. Сначала разложите детали по меткам, затем начинайте сборку.",
    "Type / Code": "Тип / код",
    "Wall L": "Длина стены",
    "Width": "Ширина",
    "How to use": "Как использовать",
    "How to use this document": "Как использовать этот документ",
    "First check the main dimensions and materials": "Сначала проверьте основные размеры и материалы",
    "If you see an error here, do not order cutting yet.": "Если здесь есть ошибка, пока не заказывайте раскрой.",
    "If you see an error here, do not send the document to the workshop.": "Если здесь есть ошибка, не отправляйте документ в мастерскую.",
    "Use only the cutting, edging and machining sheets for the workshop": "Для мастерской используйте только листы раскроя, кромления и обработки",
    "The workshop works by CUT dimensions and notes from those sheets.": "Мастерская работает по размерам CUT и примечаниям из этих листов.",
    "Take only the 'For workshop' section to the workshop": "В мастерскую передайте только раздел 'Для мастерской'",
    "The workshop works by CUT dimensions and notes from that section.": "Мастерская работает по размерам CUT и примечаниям из этого раздела.",
    "Use the 'For assembly' section during assembly": "Во время сборки используйте раздел 'Для сборки'",
    "Purchase ready-made appliances, hardware and tools separately": "Готовую технику, фурнитуру и инструменты купите отдельно",
    "These items are not cut from board material.": "Эти позиции не вырезаются из плитного материала.",
    "Use the guide and checklists during assembly": "Во время сборки используйте руководство и чек-листы",
    "Follow the order: carcasses, fronts, drawers, appliances, final check.": "Соблюдайте порядок: корпуса, фасады, ящики, техника, финальная проверка.",
    "Overview": "Обзор",
    "Overview of all panels": "Обзор всех панелей",
    "Summary cut list of panels": "Сводная карта раскроя панелей",
    "Summary cut list - panels": "Сводная карта раскроя - панели",
    "Dimensions are finished sizes. CUT dimensions include edging allowances and workshop rules.": "Указаны готовые размеры. Размеры CUT учитывают кромку и правила мастерской.",
    "Dimensions are finished sizes, after edging.": "Размеры указаны готовыми, после кромления.",
    "Cutting": "Раскрой",
    "By units": "По модулям",
    "Detailed cut list by units": "Детальная карта раскроя по модулям",
    "Detailed cut list - by units": "Детальная карта раскроя по модулям",
    "Each part is shown by unit. Dimensions are finished sizes, after edging.": "Каждая деталь показана по модулю. Размеры готовые, после кромления.",
    "Carcass": "Корпус",
    "Carcass — sides, bottom, top": "Корпус — боковины, низ и верх",
    "Backs": "Задники",
    "Back panels": "Задние панели",
    "Fronts": "Фасады",
    "Drawers": "Ящики",
    "Drawer box": "Короб ящика",
    "Worktop": "Столешница",
    "Worktop spec": "Спецификация столешницы",
    "WORKTOP SPECIFICATION": "СПЕЦИФИКАЦИЯ СТОЛЕШНИЦЫ",
    "Plinth": "Цоколь",
    "Plinths and trims": "Цоколи и планки",
    "Hardware": "Фурнитура",
    "Hardware and consumables": "Фурнитура и расходники",
    "Work order": "Рабочий заказ",
    "Workshop cutting": "Раскрой - мастерская",
    "Workshop edging": "Кромление - мастерская",
    "Workshop machining": "Обработка - мастерская",
    "Workshop packet - cutting": "Пакет мастерской - раскрой",
    "Workshop packet - edging": "Пакет мастерской - кромление",
    "Workshop packet - machining": "Пакет мастерской - обработка",
    "Workshop note": "Примечание для мастерской",
    "Workshop packet for board material": "Пакет мастерской для плитного материала",
    "Shopping": "Покупки",
    "Shopping list": "Список покупок",
    "Ready-made": "Готовые изделия",
    "Purchased ready-made": "Покупается готовым",
    "Guide": "Руководство",
    "Quick user guide": "Краткое руководство пользователя",
    "Workshop checklist": "Чек-лист мастерской",
    "Home checklist": "Чек-лист дома",
    "Checklist before assembly": "Чек-лист перед сборкой",
    "Checklist before home assembly": "Чек-лист перед домашней сборкой",
    "Checklist before workshop and assembly": "Чек-лист перед мастерской и сборкой",
    "Before going to the workshop": "Перед передачей в мастерскую",
    "Before home assembly": "Перед домашней сборкой",
    "FOR CUSTOMER": "ДЛЯ КЛИЕНТА",
    "FOR WORKSHOP": "ДЛЯ МАСТЕРСКОЙ",
    "FOR ASSEMBLY": "ДЛЯ СБОРКИ",
    "Beginner legend": "Легенда для новичка",
    "The name of the panel or unit part.": "Название панели или детали модуля.",
    "How many pieces of that part are needed.": "Сколько таких деталей требуется.",
    "Panel thickness in millimeters.": "Толщина панели в миллиметрах.",
    "Finished part dimensions.": "Готовые размеры детали.",
    "What the part is made of.": "Материал детали.",
    "Orientation": "Ориентация",
    "Board or grain direction.": "Направление плиты или текстуры.",
    "Which edges get edge banding.": "Какие кромки оклеиваются.",
    "L1/L2 are long edges, K1/K2 are short edges.": "L1/L2 — длинные кромки, K1/K2 — короткие кромки.",
    "1 = edged, 0 = not edged.": "1 = кромится, 0 = не кромится.",
    "Workshop size before final processing, where applicable.": "Размер для мастерской до финальной обработки, где применимо.",
    "Size used by the workshop before final processing.": "Размер, который мастерская использует до финальной обработки.",
    "Edge that receives edge banding.": "Кромка, на которую наносится кромочная лента.",
    "How many pieces the workshop should prepare.": "Сколько деталей должна подготовить мастерская.",
    "Extra instruction for cutting, edging or machining.": "Дополнительная инструкция для раскроя, кромления или обработки.",
    "Project coordinates": "Координаты проекта",
    "Wall (L x H)": "Стена (Д x В)",
    "Legs": "Ножки",
    "Base carcass height": "Высота нижнего корпуса",
    "Worktop thickness": "Толщина столешницы",
    "Working height (total)": "Рабочая высота (общая)",
    "Use this section to review the main dimensions, important panels and overall project readiness.": "Используйте этот раздел для проверки основных размеров, важных панелей и готовности проекта.",
    "Image labels use the same labels as the table and steps.": "Метки на изображении совпадают с таблицей и шагами.",
    "Materials": "Материалы",
    "Generated": "Создано",
    "Profile": "Профиль",
    "Standard": "Стандарт",
    "Grain": "Волокно",
    "CUT Length": "Длина CUT",
    "CUT Width": "Ширина CUT",
    "FIN Length": "Финальная длина",
    "FIN Width": "Финальная ширина",
    "Check that the material and thickness values are correct for carcass, fronts and backs": "Проверьте, что материалы и толщины корпуса, фасадов и задников указаны верно",
    "Check that all CUT dimensions and quantities are listed": "Проверьте, что указаны все размеры CUT и количества",
    "Check edge banding on every edge before sending to the workshop": "Проверьте кромление каждой кромки перед отправкой в мастерскую",
    "Check that fronts, backs, plinths and special panels are included": "Проверьте, что фасады, задники, цоколи и специальные панели включены",
    "Check that all ready-made purchased items are separated from cut parts": "Проверьте, что готовые покупные позиции отделены от деталей раскроя",
    "Check all openings and special machining for services and ventilation": "Проверьте все проёмы и специальную обработку для коммуникаций и вентиляции",
    "Check that the shopping list includes hardware, consumables and tools": "Проверьте, что список покупок включает фурнитуру, расходники и инструменты",
    "Count all cut panels and compare them against the list": "Пересчитайте все раскроенные панели и сравните со списком",
    "Sort parts by unit before starting assembly": "Разложите детали по модулям перед началом сборки",
    "Check that all hardware, appliances and tools have been purchased": "Проверьте, что куплены вся фурнитура, техника и инструменты",
    "Assemble the carcasses first, then doors and drawers, and only then the appliances": "Сначала соберите корпуса, затем двери и ящики, и только потом технику",
    "Sort parts by unit on site": "На месте разложите детали по модулям",
    "Separate carcass parts first, then fronts, then hardware": "Сначала отделите детали корпуса, затем фасады, затем фурнитуру",
    "Assemble the carcasses first, then doors, drawers and appliances": "Сначала соберите корпуса, затем двери, ящики и технику",
    "Always secure tall and wall units to the wall": "Высокие и навесные модули обязательно крепите к стене",
})

_PDF_PHRASES["zh-cn"].update({
    "How to use": "如何使用",
    "How to use this document": "如何使用此文档",
    "First check the main dimensions and materials": "先检查主要尺寸和材料",
    "If you see an error here, do not order cutting yet.": "如果这里有错误，请先不要下单切割。",
    "If you see an error here, do not send the document to the workshop.": "如果这里有错误，请不要把文档发到车间。",
    "Use only the cutting, edging and machining sheets for the workshop": "给车间只使用切割、封边和加工页",
    "The workshop works by CUT dimensions and notes from those sheets.": "车间按 CUT 尺寸和这些页里的备注执行。",
    "Take only the 'For workshop' section to the workshop": "带到车间的只有“给车间”这一部分",
    "The workshop works by CUT dimensions and notes from that section.": "车间按该部分中的 CUT 尺寸和备注执行。",
    "Use the 'For assembly' section during assembly": "安装时使用“安装”部分",
    "Purchase ready-made appliances, hardware and tools separately": "成品电器、五金和工具需单独购买",
    "These items are not cut from board material.": "这些项目不属于板材切割。",
    "Use the guide and checklists during assembly": "安装时使用指南和检查表",
    "Follow the order: carcasses, fronts, drawers, appliances, final check.": "顺序为：柜体、门板、抽屉、电器、最终检查。",
    "Overview": "总览",
    "Overview of all panels": "所有板件总览",
    "Summary cut list of panels": "板件汇总裁切清单",
    "Summary cut list - panels": "汇总裁切清单 - 板件",
    "Dimensions are finished sizes. CUT dimensions include edging allowances and workshop rules.": "标注尺寸为成品尺寸。CUT 尺寸已包含封边余量和车间规则。",
    "Dimensions are finished sizes, after edging.": "标注尺寸为封边后的成品尺寸。",
    "Cutting": "裁切",
    "By units": "按模块",
    "Detailed cut list by units": "按模块的详细裁切清单",
    "Detailed cut list - by units": "详细裁切清单 - 按模块",
    "Each part is shown by unit. Dimensions are finished sizes, after edging.": "每个部件按模块显示，尺寸为封边后的成品尺寸。",
    "Carcass": "柜体",
    "Backs": "背板",
    "Fronts": "门板",
    "Drawers": "抽屉",
    "Drawer box": "抽屉箱体",
    "Worktop": "台面",
    "Worktop spec": "台面规格",
    "WORKTOP SPECIFICATION": "台面规格",
    "Plinth": "踢脚板",
    "Plinths and trims": "踢脚板和收口条",
    "Hardware": "五金",
    "Hardware and consumables": "五金和耗材",
    "Work order": "工单",
    "Workshop cutting": "车间 - 切割",
    "Workshop edging": "车间 - 封边",
    "Workshop machining": "车间 - 加工",
    "Workshop packet - cutting": "车间资料包 - 切割",
    "Workshop packet - edging": "车间资料包 - 封边",
    "Workshop packet - machining": "车间资料包 - 加工",
    "Workshop note": "车间备注",
    "Workshop packet for board material": "板材车间资料包",
    "Shopping": "采购",
    "Shopping list": "采购清单",
    "Ready-made": "成品购买",
    "Purchased ready-made": "成品购买",
    "Guide": "指南",
    "Quick user guide": "快速使用指南",
    "Workshop checklist": "车间检查清单",
    "Home checklist": "现场安装检查清单",
    "Checklist before assembly": "安装前检查清单",
    "Checklist before home assembly": "现场安装前检查清单",
    "Checklist before workshop and assembly": "车间与安装前检查清单",
    "Before going to the workshop": "去车间前",
    "Before home assembly": "现场安装前",
    "FOR CUSTOMER": "给客户",
    "FOR WORKSHOP": "给车间",
    "FOR ASSEMBLY": "给安装",
    "Beginner legend": "新手说明",
    "Generated": "生成时间",
    "Materials": "材料",
    "Profile": "配置",
    "Standard": "标准",
    "Grain": "纹理",
    "The name of the panel or unit part.": "面板或模块部件的名称。",
    "How many pieces of that part are needed.": "该部件需要多少件。",
    "Finished part dimensions.": "部件成品尺寸。",
    "What the part is made of.": "该部件所用材料。",
    "Board or grain direction.": "板材或纹理方向。",
    "Which edges get edge banding.": "哪些边需要封边。",
    "L1/L2 are long edges, K1/K2 are short edges.": "L1/L2 是长边，K1/K2 是短边。",
    "1 = edged, 0 = not edged.": "1 = 封边，0 = 不封边。",
    "Panel thickness in millimeters.": "面板厚度，单位为毫米。",
    "Workshop size before final processing, where applicable.": "如适用，这是最终加工前的车间尺寸。",
    "CUT Length": "CUT 长度",
    "CUT Width": "CUT 宽度",
    "FIN Length": "成品长度",
    "FIN Width": "成品宽度",
    "Project coordinates": "项目坐标",
    "Wall (L x H)": "墙面 (长 x 高)",
    "Legs": "柜脚",
    "Base carcass height": "下柜柜体高度",
    "Worktop thickness": "台面厚度",
    "Working height (total)": "总工作高度",
    "Use this section to review the main dimensions, important panels and overall project readiness.": "使用本部分检查主要尺寸、关键板件以及项目是否已准备好进入下一步。",
    "Check that the material and thickness values are correct for carcass, fronts and backs": "检查柜体、门板和背板的材料与厚度是否正确",
    "Check that all CUT dimensions and quantities are listed": "检查所有 CUT 尺寸和数量是否齐全",
    "Check edge banding on every edge before sending to the workshop": "送车间前检查每一条需要封边的边",
    "Check that fronts, backs, plinths and special panels are included": "检查门板、背板、踢脚板和特殊板件是否都已包含",
    "Check that all ready-made purchased items are separated from cut parts": "检查所有成品购买项是否已与切割件分开",
    "Check all openings and special machining for services and ventilation": "检查所有开孔以及管线和通风相关的特殊加工",
    "Check that the shopping list includes hardware, consumables and tools": "检查采购清单是否包含五金、耗材和工具",
    "Count all cut panels and compare them against the list": "清点所有切割板件，并与清单核对",
    "Sort parts by unit before starting assembly": "安装前先按模块整理部件",
    "Check that all hardware, appliances and tools have been purchased": "检查五金、电器和工具是否都已购买",
    "Assemble the carcasses first, then doors and drawers, and only then the appliances": "先装柜体，再装门板和抽屉，最后再装电器",
    "Sort parts by unit on site": "现场按模块整理部件",
    "Separate carcass parts first, then fronts, then hardware": "先分柜体件，再分门板，最后分五金",
    "Assemble the carcasses first, then doors, drawers and appliances": "先装柜体，再装门板、抽屉和电器",
    "Always secure tall and wall units to the wall": "高柜和吊柜必须固定在墙上",
    "Cut length": "切割长度",
    "Cut width": "切割宽度",
    "Cut-outs": "开孔",
    "Depth": "深度",
    "Field cut": "现场切割",
    "Group": "组",
    "Image labels match the parts table: C = carcass, B = back, F = front, D = drawer.": "图片标签与部件表一致：C = 柜体，B = 背板，F = 门板，D = 抽屉。",
    "Instruction": "说明",
    "Item": "项目",
    "Joint": "接缝",
    "Length": "长度",
    "Name": "名称",
    "Purchase": "采购",
    "Required": "需要",
    "The labels in the 2D view use the same short label as the table and assembly steps.": "2D 视图中的标签使用与表格和组装步骤相同的短标签。",
    "The part label is the same in the image, table and text. Sort the parts by label first, then start assembly.": "图片、表格和文本中的部件标签一致。先按标签整理部件，再开始组装。",
    "Type / Code": "类型 / 编码",
    "Wall L": "墙长",
    "Width": "宽度",
})

_PDF_PHRASES["hi"].update({
    "How to use": "कैसे उपयोग करें",
    "How to use this document": "इस दस्तावेज़ का उपयोग कैसे करें",
    "First check the main dimensions and materials": "पहले मुख्य माप और सामग्री जाँचें",
    "If you see an error here, do not order cutting yet.": "अगर यहाँ गलती दिखे तो अभी कटिंग ऑर्डर न करें।",
    "If you see an error here, do not send the document to the workshop.": "अगर यहाँ गलती दिखे तो दस्तावेज़ वर्कशॉप को न भेजें।",
    "Use only the cutting, edging and machining sheets for the workshop": "वर्कशॉप के लिए केवल कटिंग, एजिंग और प्रोसेसिंग शीटें उपयोग करें",
    "The workshop works by CUT dimensions and notes from those sheets.": "वर्कशॉप CUT माप और उन्हीं शीटों के नोट के अनुसार काम करती है।",
    "Take only the 'For workshop' section to the workshop": "वर्कशॉप में केवल 'वर्कशॉप के लिए' वाला सेक्शन ले जाएँ",
    "The workshop works by CUT dimensions and notes from that section.": "वर्कशॉप उसी सेक्शन के CUT माप और नोट के अनुसार काम करती है।",
    "Use the 'For assembly' section during assembly": "असेंबली के समय 'असेंबली के लिए' सेक्शन उपयोग करें",
    "Purchase ready-made appliances, hardware and tools separately": "तैयार उपकरण, हार्डवेयर और औज़ार अलग से खरीदें",
    "These items are not cut from board material.": "ये आइटम बोर्ड मटेरियल से नहीं काटे जाते।",
    "Use the guide and checklists during assembly": "असेंबली के दौरान गाइड और चेकलिस्ट का उपयोग करें",
    "Follow the order: carcasses, fronts, drawers, appliances, final check.": "क्रम रखें: कार्कस, फ्रंट, दराज़, उपकरण, अंतिम जांच।",
    "Overview": "सारांश",
    "Overview of all panels": "सभी पैनलों का सारांश",
    "Summary cut list of panels": "पैनलों की सारांश कट लिस्ट",
    "Summary cut list - panels": "सारांश कट लिस्ट - पैनल",
    "Dimensions are finished sizes. CUT dimensions include edging allowances and workshop rules.": "दिए गए माप फिनिश्ड साइज हैं। CUT माप में एजिंग अलाउंस और वर्कशॉप नियम शामिल हैं।",
    "Dimensions are finished sizes, after edging.": "दिए गए माप एजिंग के बाद के फिनिश्ड साइज हैं।",
    "Cutting": "कटिंग",
    "By units": "मॉड्यूल अनुसार",
    "Detailed cut list by units": "मॉड्यूल अनुसार विस्तृत कट लिस्ट",
    "Detailed cut list - by units": "विस्तृत कट लिस्ट - मॉड्यूल अनुसार",
    "Each part is shown by unit. Dimensions are finished sizes, after edging.": "हर भाग मॉड्यूल अनुसार दिखाया गया है। माप एजिंग के बाद के फिनिश्ड साइज हैं।",
    "Carcass": "कार्कस",
    "Backs": "बैक पैनल",
    "Fronts": "फ्रंट",
    "Drawers": "दराज़",
    "Drawer box": "दराज़ बॉक्स",
    "Worktop": "वर्कटॉप",
    "Worktop spec": "वर्कटॉप विनिर्देश",
    "WORKTOP SPECIFICATION": "वर्कटॉप विनिर्देश",
    "Plinth": "सोकल",
    "Plinths and trims": "सोकल और ट्रिम",
    "Hardware": "हार्डवेयर",
    "Hardware and consumables": "हार्डवेयर और कंज़्यूमेबल",
    "Work order": "वर्क ऑर्डर",
    "Workshop cutting": "वर्कशॉप - कटिंग",
    "Workshop edging": "वर्कशॉप - एजिंग",
    "Workshop machining": "वर्कशॉप - प्रोसेसिंग",
    "Workshop packet - cutting": "वर्कशॉप पैकेट - कटिंग",
    "Workshop packet - edging": "वर्कशॉप पैकेट - एजिंग",
    "Workshop packet - machining": "वर्कशॉप पैकेट - प्रोसेसिंग",
    "Workshop note": "वर्कशॉप नोट",
    "Workshop packet for board material": "बोर्ड मटेरियल के लिए वर्कशॉप पैकेट",
    "Shopping": "खरीद",
    "Shopping list": "खरीद सूची",
    "Ready-made": "तैयार खरीदा",
    "Purchased ready-made": "तैयार खरीदा",
    "Guide": "गाइड",
    "Quick user guide": "त्वरित उपयोग गाइड",
    "Workshop checklist": "वर्कशॉप चेकलिस्ट",
    "Home checklist": "असेंबली चेकलिस्ट",
    "Checklist before assembly": "असेंबली से पहले चेकलिस्ट",
    "Checklist before home assembly": "घर पर असेंबली से पहले चेकलिस्ट",
    "Checklist before workshop and assembly": "वर्कशॉप और असेंबली से पहले चेकलिस्ट",
    "Before going to the workshop": "वर्कशॉप जाने से पहले",
    "Before home assembly": "घर पर असेंबली से पहले",
    "FOR CUSTOMER": "ग्राहक के लिए",
    "FOR WORKSHOP": "वर्कशॉप के लिए",
    "FOR ASSEMBLY": "असेंबली के लिए",
    "Beginner legend": "शुरुआती नोट",
    "Generated": "जनरेट किया गया",
    "Materials": "सामग्री",
    "Profile": "प्रोफाइल",
    "Standard": "मानक",
    "Grain": "ग्रेन",
    "The name of the panel or unit part.": "पैनल या मॉड्यूल भाग का नाम।",
    "How many pieces of that part are needed.": "उस भाग के कितने पीस चाहिए।",
    "Finished part dimensions.": "भाग के फिनिश्ड माप।",
    "What the part is made of.": "यह भाग किस सामग्री से बना है।",
    "Board or grain direction.": "बोर्ड या ग्रेन की दिशा।",
    "Which edges get edge banding.": "किन एज पर एज बैंडिंग लगेगी।",
    "L1/L2 are long edges, K1/K2 are short edges.": "L1/L2 लंबी एज हैं, K1/K2 छोटी एज हैं।",
    "1 = edged, 0 = not edged.": "1 = एज लगी है, 0 = एज नहीं लगी।",
    "Panel thickness in millimeters.": "पैनल की मोटाई मिलीमीटर में।",
    "Workshop size before final processing, where applicable.": "जहाँ लागू हो, यह अंतिम प्रोसेसिंग से पहले का वर्कशॉप माप है।",
    "CUT Length": "CUT लंबाई",
    "CUT Width": "CUT चौड़ाई",
    "FIN Length": "फिनिश लंबाई",
    "FIN Width": "फिनिश चौड़ाई",
    "Project coordinates": "प्रोजेक्ट निर्देशांक",
    "Wall (L x H)": "दीवार (लंबाई x ऊंचाई)",
    "Legs": "पैर",
    "Base carcass height": "निचले कार्कस की ऊंचाई",
    "Worktop thickness": "वर्कटॉप मोटाई",
    "Working height (total)": "कुल कार्य ऊंचाई",
    "Use this section to review the main dimensions, important panels and overall project readiness.": "इस भाग का उपयोग मुख्य माप, महत्वपूर्ण पैनल और प्रोजेक्ट की तैयारी जांचने के लिए करें।",
    "Check that the material and thickness values are correct for carcass, fronts and backs": "जाँचें कि कार्कस, फ्रंट और बैक के लिए सामग्री और मोटाई सही हैं",
    "Check that all CUT dimensions and quantities are listed": "जाँचें कि सभी CUT माप और मात्राएँ दी गई हैं",
    "Check edge banding on every edge before sending to the workshop": "वर्कशॉप भेजने से पहले हर एज की एजिंग जांचें",
    "Check that fronts, backs, plinths and special panels are included": "जाँचें कि फ्रंट, बैक, सोकल और विशेष पैनल शामिल हैं",
    "Check that all ready-made purchased items are separated from cut parts": "जाँचें कि सभी तैयार खरीदे आइटम कटिंग भागों से अलग हैं",
    "Check all openings and special machining for services and ventilation": "जाँचें कि सभी ओपनिंग और सर्विस/वेंटिलेशन प्रोसेसिंग सही हैं",
    "Check that the shopping list includes hardware, consumables and tools": "जाँचें कि खरीद सूची में हार्डवेयर, कंज़्यूमेबल और औज़ार शामिल हैं",
    "Count all cut panels and compare them against the list": "सभी कटे पैनल गिनें और सूची से मिलाएँ",
    "Sort parts by unit before starting assembly": "असेंबली शुरू करने से पहले भागों को मॉड्यूल अनुसार अलग करें",
    "Check that all hardware, appliances and tools have been purchased": "जाँचें कि सभी हार्डवेयर, उपकरण और औज़ार खरीदे गए हैं",
    "Assemble the carcasses first, then doors and drawers, and only then the appliances": "पहले कार्कस जोड़ें, फिर दरवाज़े और दराज़, और अंत में उपकरण",
    "Sort parts by unit on site": "साइट पर भागों को मॉड्यूल अनुसार अलग करें",
    "Separate carcass parts first, then fronts, then hardware": "पहले कार्कस भाग अलग करें, फिर फ्रंट, फिर हार्डवेयर",
    "Assemble the carcasses first, then doors, drawers and appliances": "पहले कार्कस जोड़ें, फिर दरवाज़े, दराज़ और उपकरण",
    "Always secure tall and wall units to the wall": "ऊँचे और दीवार वाले मॉड्यूल हमेशा दीवार से फिक्स करें",
    "Cut length": "कट लंबाई",
    "Cut width": "कट चौड़ाई",
    "Cut-outs": "कट-आउट",
    "Depth": "गहराई",
    "Field cut": "साइट पर कट",
    "Group": "समूह",
    "Image labels match the parts table: C = carcass, B = back, F = front, D = drawer.": "चित्र के लेबल भागों की तालिका से मेल खाते हैं: C = ढांचा, B = पीछे, F = फ्रंट, D = दराज़।",
    "Instruction": "निर्देश",
    "Item": "आइटम",
    "Joint": "जोड़",
    "Length": "लंबाई",
    "Name": "नाम",
    "Purchase": "खरीद",
    "Required": "आवश्यक",
    "The labels in the 2D view use the same short label as the table and assembly steps.": "2D दृश्य में लेबल वही छोटे लेबल इस्तेमाल करते हैं जो तालिका और असेंबली चरणों में हैं।",
    "The part label is the same in the image, table and text. Sort the parts by label first, then start assembly.": "भाग का लेबल चित्र, तालिका और टेक्स्ट में समान है। पहले भागों को लेबल के अनुसार अलग करें, फिर असेंबली शुरू करें।",
    "Type / Code": "प्रकार / कोड",
    "Wall L": "दीवार लंबाई",
    "Width": "चौड़ाई",
})


def _pdf_t(sr: str, en: str, lang: str) -> str:
    lang_key = normalize_language_code(lang)
    if lang_key == "sr":
        return sr
    if lang_key == "en":
        return en
    return _PDF_PHRASES.get(lang_key, {}).get(en, en)


def _pdf_localize_text(value, lang: str = "sr") -> str:
    txt = str(value or "").strip()
    lang_key = normalize_language_code(lang)
    if not txt or lang_key != "de":
        return txt
    exact = {
        "FOR CUSTOMER": "FÜR DEN KUNDEN",
        "FOR WORKSHOP": "FÜR DIE WERKSTATT",
        "FOR ASSEMBLY": "FÜR DIE MONTAGE",
        "Project coordinates": "Projektkoordinaten",
        "Summary cut list - panels": "Zuschnitt-Übersicht - Platten",
        "Detailed cut list - by units": "Detaillierte Zuschnittliste - nach Elementen",
        "Detailed cut list by units": "Detaillierte Zuschnittliste nach Elementen",
        "Summary cut list of panels": "Zusammengefasste Zuschnittliste der Platten",
        "Workshop packet for board material": "Werkstattpaket für Plattenmaterial",
        "Cutting table": "Zuschnitt-Tabelle",
        "Edging table": "Kanten-Tabelle",
        "Machining table": "Bearbeitungs-Tabelle",
        "Worktop specification": "Arbeitsplatten-Spezifikation",
        "Assembly map by unit (part orientation)": "Montageplan nach Elementen (Teilorientierung)",
        "Image labels use the same labels as the table and steps.": "Bildkennzeichnungen verwenden dieselben Kürzel wie Tabelle und Montageschritte.",
        "Each part is shown by unit. Dimensions are finished sizes, after edging.": "Jedes Teil wird je Element gezeigt. Die Maße sind Fertigmaße nach dem Bekanten.",
        "Use this section to review the main dimensions, important panels and overall project readiness.": "In diesem Abschnitt prüfst du Hauptmaße, wichtige Platten und die allgemeine Projektbereitschaft.",
        "Take this section to the workshop. The workshop works by CUT dimensions, edging notes and machining notes from these tables.": "Nimm diesen Abschnitt mit in die Werkstatt. Die Werkstatt arbeitet nach CUT-Maßen sowie Kanten- und Bearbeitungshinweisen aus diesen Tabellen.",
        "This goes to the workshop: cutting by CUT dimensions, edging by table, and machining by notes.": "Dieser Abschnitt geht in die Werkstatt: Zuschnitt nach CUT-Maßen, Kanten nach Tabelle und Bearbeitung nach Hinweisen.",
        "The workshop works strictly by CUT dimensions. Final trimming and fitting are done on site.": "Die Werkstatt arbeitet strikt nach CUT-Maßen. Endanpassung und Einbau erfolgen vor Ort.",
        "Note: appliances, sink, tap, trap, and similar items are purchased as ready-made products and are not part of the cutting list.": "Hinweis: Geräte, Spüle, Armatur, Siphon und ähnliche Teile werden als Fertigprodukte gekauft und gehören nicht zur Zuschnittliste.",
        "Use this section for assembly order, part orientation and final checklists.": "Verwende diesen Abschnitt für Montagereihenfolge, Teilausrichtung und finale Checklisten.",
        "Each unit links the image, part labels, table and assembly order.": "Jedes Element verbindet Bild, Teilekennzeichnungen, Tabelle und Montagereihenfolge.",
        "BASE UNIT PARTS LIST": "LISTE DER UNTERSCHRANK-TEILE",
        "SINK BASE UNIT": "SPÜLEN-UNTERSCHRANK",
        "Project": "Projekt",
        "Customer": "Kunde",
        "Room": "Raum",
        "Wall": "Wand",
        "Wall size": "Wandgröße",
        "Version": "Version",
        "Generated": "Erstellt",
        "Measured by": "Gemessen von",
        "Designed by": "Geplant von",
        "Workshop note": "Werkstatt-Hinweis",
        "Kitchen": "Küche",
        "Wall A": "Wand A",
        "Wall B": "Wand B",
        "Wall C": "Wand C",
        "Cutting": "Zuschnitt",
        "Edging": "Kanten",
        "Machining": "Bearbeitung",
        "Worktop": "Arbeitsplatte",
        "Who performs it": "Wer es ausführt",
        "Execution basis": "Ausführungsgrundlage",
        "Services": "Installationen",
        "Final check": "Endkontrolle",
        "Purchased ready-made": "Fertig gekauft",
        "Consumables by unit": "Verbrauchsmaterial je Element",
        "Hardware and mechanisms by unit": "Beschläge und Mechanismen je Element",
        "Project consumables": "Projekt-Verbrauchsmaterial",
        "Purchased ready-made - not included in cutting": "Fertigprodukte — nicht im Zuschnitt enthalten",
        "Workshop": "Werkstatt",
        "Workshop + on site": "Werkstatt + vor Ort",
        "On site": "Vor Ort",
        "According to project dimensions": "Nach Projektmaßen",
        "According to wall geometry and template": "Nach Wandgeometrie und Schablone",
        "According to the manufacturer's template": "Nach Herstellerschablone",
        "Ruckvande": "Rückwände",
        "Cut strictly by the CUT dimensions from the workshop packet.": "Schneide strikt nach den CUT-Maßen aus dem Werkstattpaket.",
        "Apply edging only to the edges marked in the edging table and verify the ABS type.": "Bekante nur die in der Kantentabelle markierten Kanten und prüfe den ABS-Typ.",
        "Make special openings, grooves and ventilation cuts only where they are explicitly specified.": "Sonderöffnungen, Nuten und Lüftungsausschnitte nur dort ausführen, wo sie ausdrücklich angegeben sind.",
        "Cut the sink or hob opening according to the manufacturer's template, not by estimation.": "Den Ausschnitt für Spüle oder Kochfeld nach Herstellerschablone ausführen, nicht nach Schätzung.",
        "The 'Operations' column clearly shows whether the workshop performs the job or whether it must be confirmed on site.": "Die Spalte „Vorgänge“ zeigt klar, ob die Werkstatt die Arbeit ausführt oder ob sie vor Ort bestätigt werden muss.",
        "The 'Execution basis' column shows whether the work follows project dimensions or the appliance manufacturer's template.": "Die Spalte „Ausführungsgrundlage“ zeigt, ob nach Projektmaßen oder nach Herstellerschablone gearbeitet wird.",
        "If the service positions differ from the project, confirm all machining before cutting or on site.": "Wenn die Installationspositionen vom Projekt abweichen, alle Bearbeitungen vor dem Zuschnitt oder vor Ort bestätigen.",
        "Before delivery, verify the piece count, part labels and that all panels/fronts are included.": "Vor der Auslieferung Stückzahl, Teilekennzeichnungen und Vollständigkeit aller Platten und Fronten prüfen.",
        "Check that the material and thickness values are correct for carcass, fronts and backs": "Prüfe, ob Material- und Dickenangaben für Korpus, Fronten und Rückwände korrekt sind",
        "Check that all CUT dimensions and quantities are listed": "Prüfe, ob alle CUT-Maße und Mengen aufgeführt sind",
        "Check edge banding on every edge before sending to the workshop": "Prüfe die Kantenbearbeitung an jeder Kante, bevor es in die Werkstatt geht",
        "Check that fronts, backs, plinths and special panels are included": "Prüfe, ob Fronten, Rückwände, Sockel und Sonderplatten enthalten sind",
        "Check that all ready-made purchased items are separated from cut parts": "Prüfe, ob alle fertig gekauften Teile von den Zuschnittteilen getrennt sind",
        "Check all openings and special machining for services and ventilation": "Prüfe alle Öffnungen und Sonderbearbeitungen für Installationen und Belüftung",
        "Check that the shopping list includes hardware, consumables and tools": "Prüfe, ob die Einkaufsliste Beschläge, Verbrauchsmaterial und Werkzeuge enthält",
        "Count all cut panels and compare them against the list": "Zähle alle Zuschnittteile und vergleiche sie mit der Liste",
        "Sort parts by unit before starting assembly": "Sortiere die Teile nach Elementen, bevor du mit der Montage beginnst",
        "Check that all hardware, appliances and tools have been purchased": "Prüfe, ob alle Beschläge, Geräte und Werkzeuge vorhanden sind",
        "Assemble the carcasses first, then doors and drawers, and only then the appliances": "Montiere zuerst die Korpusse, dann Türen und Schubladen und erst danach die Geräte",
        "Always secure tall and wall units to the wall": "Hochschränke und Hängeschränke immer an der Wand sichern",
    }
    if txt in exact:
        return exact[txt]
    replacements = [
        ("Purchased ready-made", "Fertig gekauft"),
        ("Consumables by unit", "Verbrauchsmaterial je Element"),
        ("Hardware and mechanisms by unit", "Beschläge und Mechanismen je Element"),
        ("Project consumables", "Projekt-Verbrauchsmaterial"),
        ("Kitchen", "Küche"),
        ("Wall A", "Wand A"),
        ("Wall B", "Wand B"),
        ("Wall C", "Wand C"),
        ("Leva strana", "Linke Korpusseite"),
        ("Desna strana", "Rechte Korpusseite"),
        ("Leđa", "Rückwand"),
        ("Ledja", "Rückwand"),
        ("Leđna ploča", "Rückwand"),
        ("Ledjna ploca", "Rückwand"),
        ("Dno sanduka fioke", "Schubladenkastenboden"),
        ("Prednja strana sanduka fioke", "Schubladenkasten vorne"),
        ("Zadnja strana sanduka fioke", "Schubladenkasten hinten"),
        ("Bočna stranica sanduka fioke", "Schubladenkastenseite"),
        ("Bocna stranica sanduka fioke", "Schubladenkastenseite"),
        ("Front fioke", "Schubladenfront"),
        ("Vrata (ispod sudopere)", "Türfront unter der Spüle"),
        ("Vrata rerne", "Backofenfront"),
        ("Polica (podesiva)", "Verstellbarer Boden"),
        ("Vrata", "Türfront"),
        ("Nosač radne ploče", "Arbeitsplattenträger"),
        ("Nosac radne ploce", "Arbeitsplattenträger"),
        ("Sokla (lajsna)", "Sockel"),
        ("Sokla", "Sockel"),
        ("Leva stranica korpusa", "Linke Korpusseite"),
        ("Desna stranica korpusa", "Rechte Korpusseite"),
        ("Donja ploča korpusa", "Korpusboden"),
        ("Donja ploca korpusa", "Korpusboden"),
        ("Gornja ploča korpusa", "Korpusdeckel"),
        ("Gornja ploca korpusa", "Korpusdeckel"),
        ("Front vrata", "Türfront"),
        ("Front za rernu", "Backofenfront"),
        ("LEVO", "LINKS"),
        ("LEVA", "LINKS"),
        ("DESNO", "RECHTS"),
        ("DESNA", "RECHTS"),
        ("POZADI", "HINTEN"),
        ("ZADNJA", "HINTEN"),
        ("NAPRED", "VORNE"),
        ("PREDNJA", "VORNE"),
        ("GORE", "OBEN"),
        ("DOLE", "UNTEN"),
        ("Gore", "Oben"),
        ("Dole", "Unten"),
        ("Transparentni / sivi", "Transparent / grau"),
        ("Kupuje se kao gotov proizvod, otvor se reže u radnoj ploči prema šablonu", "Wird als Fertigprodukt gekauft; der Ausschnitt in der Arbeitsplatte wird nach Schablone geschnitten"),
        ("Kupuje se kao gotov proizvod, otvor se reze u radnoj ploci prema sablonu", "Wird als Fertigprodukt gekauft; der Ausschnitt in der Arbeitsplatte wird nach Schablone geschnitten"),
        ("Kupuje se posebno prema izboru korisnika", "Wird separat nach Wahl des Nutzers gekauft"),
        ("Kupovni vodoinstalaterski set za sudoperu", "Gekauftes Sanitärset für die Spüle"),
        ("Za zaptivanje ruba sudopere i spojeva uz radnu ploču", "Zum Abdichten des Spülenrandes und der Fugen an der Arbeitsplatte"),
        ("Za zaptivanje ruba sudopere i spojeva uz radnu plocu", "Zum Abdichten des Spülenrandes und der Fugen an der Arbeitsplatte"),
        ("Osnovni set po elementu", "Grundsatz je Element"),
        ("Po jedna klipsa po stopici za prihvat sokle", "Je Fuß eine Sockelklammer"),
        ("Osnovno 2 spojnice po spoju susednih korpusa u istoj ravni", "Standardmäßig 2 Verbinder je Verbindung benachbarter Korpusse in einer Ebene"),
        ("Radna ploča - Zid A", "Arbeitsplatte - Wand A"),
        ("Radna ploca - Zid A", "Arbeitsplatte - Wand A"),
        ("Zid A", "Wand A"),
        ("Zid B", "Wand B"),
        ("Zid C", "Wand C"),
        ("Deo", "Teil"),
        ("Kom", "Menge"),
        ("Dužina [mm]", "Länge [mm]"),
        ("Duzina [mm]", "Länge [mm]"),
        ("Širina [mm]", "Breite [mm]"),
        ("Sirina [mm]", "Breite [mm]"),
        ("Deb.", "Stärke"),
        ("Napomena", "Hinweis"),
        ("Stavka", "Eintrag"),
        ("Instrukcija", "Anweisung"),
        ("Pozicija", "Position"),
        ("SklopKorak", "Montage-Schritt"),
        ("Tip obrade", "Bearbeitungsart"),
        ("Izvodi", "Vorgänge"),
        ("Osnov izvode", "Ausführungsgrundlage"),
        ("Osnov izvođenja", "Ausführungsgrundlage"),
        ("Obrada / napomena", "Bearbeitung / Hinweis"),
        ("Montažni plan", "Montage-Teileplan"),
        ("Montazni plan", "Montage-Teileplan"),
        ("Montažna uputstva", "Montageanleitung"),
        ("Montazna uputstva", "Montageanleitung"),
        ("Potrebni alati i okovi", "Benötigte Werkzeuge und Beschläge"),
        ("Leva bočna ploča", "Linke Seitenwand"),
        ("Leva bocna ploca", "Linke Seitenwand"),
        ("Desna bočna ploča", "Rechte Seitenwand"),
        ("Desna bocna ploca", "Rechte Seitenwand"),
        ("Gornji vez", "Oberer Verbinder"),
        ("pričvršćuje radnu ploču", "befestigt die Arbeitsplatte"),
        ("pricvrscuje radnu plocu", "befestigt die Arbeitsplatte"),
        ("utor 8mm", "Nut 8 mm"),
        ("Slavina", "Armatur"),
        ("Sifon i odvodni set", "Siphon und Ablaufset"),
        ("Podesiva h=100 mm", "Verstellbar h=100 mm"),
        ("Pojam", "Begriff"),
        ("objašnjenje", "Erklärung"),
        ("objasnjenje", "Erklärung"),
        ("Zid", "Wand"),
        ("Modul", "Modul"),
        ("Materijal", "Material"),
        ("Kol.", "Menge"),
        ("Kant", "Kante"),
        ("Vrednost", "Wert"),
        ("Polica", "Boden"),
        ("Leđna ploča", "Rückwand"),
        ("Ledjna ploča", "Rückwand"),
        ("Leđna ploča / prolaz", "Rückwand / Öffnung"),
        ("Ledjna ploca / prolaz", "Rückwand / Öffnung"),
    ]
    for src, dst in replacements:
        txt = txt.replace(src, dst)
    return txt


def _friendly_part_name(value, lang: str = "sr") -> str:
    txt = str(value or "").strip()
    txt = (
        txt.replace("LeÄ‘a", "Ledja")
        .replace("LeÃ„â€˜a", "Ledja")
        .replace("BoÄna ploÄa", "Bocna ploca")
        .replace("BoÃ„Âna ploÃ„Âa", "Bocna ploca")
        .replace("ploÄa", "ploca")
        .replace("ploÃ„Âa", "ploca")
    )
    txt = re.sub(r"^[A-Z]\d+\s*[—-]\s*", "", txt)
    mapping = {
        "Leva strana": "Leva stranica korpusa",
        "Desna strana": "Desna stranica korpusa",
        "Dno": "Donja ploča korpusa",
        "Plafon": "Gornja ploča korpusa",
        "Vrata": "Front vrata",
        "Front fioke": "Front fioke",
        "Leđa": "Leđna ploča",
        "Ledja": "Leđna ploča",
    }
    mapping.update({
        "Front fioke (unif.)": "Front fioke",
        "Front fioke (kuhinjska jedinica)": "Front fioke ispod rerne",
        "Front fioke (ispod rerne)": "Front fioke ispod rerne",
        "Vrata (ispod sudopere)": "Front vrata ispod sudopere",
        "Vrata rerne": "Front za rernu",
        "Polica (podesiva)": "Polica (podesiva)",
        "Prednja strana sanduka": "Prednja strana sanduka fioke",
        "Zadnja strana sanduka": "Zadnja strana sanduka fioke",
        "Dno sanduka": "Dno sanduka fioke",
        "Bočna ploča": "Bočna stranica sanduka fioke",
        "Ledja / prolaz": "Leđna ploča / prolaz",
    })
    mapping["Dno"] = "Donja ploča korpusa"
    mapping["LeÄ‘a"] = "Leđna ploča"
    mapping["Plafon"] = "Gornja ploča korpusa"
    mapping["LeÄ‘a"] = "Leđna ploča"
    mapping["Ledja"] = "Leđna ploča"
    mapping["BoÄna ploÄa"] = "Bočna stranica sanduka fioke"
    mapping["BoÄna ploÄa"] = "Bočna stranica sanduka fioke"
    if str(lang or "sr").lower().strip() == "en":
        mapping_en = {
            "Leva strana": "Left carcass side",
            "Desna strana": "Right carcass side",
            "Dno": "Bottom carcass panel",
            "LeÄ‘a": "Back panel",
            "Plafon": "Top carcass panel",
            "Vrata": "Door front",
            "Front fioke": "Drawer front",
            "LeÄ‘a": "Back panel",
            "Ledja": "Back panel",
            "Front fioke (unif.)": "Drawer front",
            "Front fioke (kuhinjska jedinica)": "Drawer front below oven",
            "Front fioke (ispod rerne)": "Drawer front below oven",
            "Vrata (ispod sudopere)": "Door front below sink",
            "Vrata rerne": "Oven front",
            "Prednja strana sanduka": "Drawer box front",
            "Zadnja strana sanduka": "Drawer box back",
            "Dno sanduka": "Drawer box bottom",
            "BoÄna ploÄa": "Drawer box side",
            "BoÄna ploÄa": "Drawer box side",
            "Ledja / prolaz": "Back panel / opening",
        }
        mapping_en["Leva stranica korpusa"] = "Left carcass side"
        mapping_en["Desna stranica korpusa"] = "Right carcass side"
        mapping_en["Donja ploča korpusa"] = "Bottom carcass panel"
        mapping_en["Gornja ploča korpusa"] = "Top carcass panel"
        mapping_en["Front vrata"] = "Door front"
        mapping_en["Front vrata ispod sudopere"] = "Door front below sink"
        mapping_en["Front za rernu"] = "Oven front"
        mapping_en["Prednja strana sanduka fioke"] = "Drawer box front"
        mapping_en["Zadnja strana sanduka fioke"] = "Drawer box back"
        mapping_en["Dno sanduka fioke"] = "Drawer box bottom"
        mapping_en["Bočna stranica sanduka fioke"] = "Drawer box side"
        mapping_en["Leđna ploča"] = "Back panel"
        mapping_en["Leđna ploča / prolaz"] = "Back panel / opening"
        return mapping_en.get(txt, txt)
    mapping.update({
        "Left carcass side": "Leva stranica korpusa",
        "Right carcass side": "Desna stranica korpusa",
        "Bottom carcass panel": "Donja ploča korpusa",
        "Top carcass panel": "Gornja ploča korpusa",
        "Door front": "Front vrata",
        "Drawer front": "Front fioke",
        "Back panel": "Leđna ploča",
        "Door front below sink": "Front vrata ispod sudopere",
        "Oven front": "Front za rernu",
        "Drawer box front": "Prednja strana sanduka fioke",
        "Drawer box back": "Zadnja strana sanduka fioke",
        "Drawer box bottom": "Dno sanduka fioke",
        "Drawer box side": "Bočna stranica sanduka fioke",
        "Back panel / opening": "Leđna ploča / prolaz",
    })
    return mapping.get(txt, txt)


def _friendly_position_name(value, lang: str = "sr") -> str:
    txt = str(value or "").strip()
    lang_key = normalize_language_code(lang)
    mapping = {
        "LEVO": "Levo",
        "LEVA": "Levo",
        "DESNO": "Desno",
        "DESNA": "Desno",
        "GORE": "Gore",
        "DOLE": "Dole",
        "CENTAR": "Sredina",
        "NAPRED": "Napred",
        "PREDNJA": "Napred",
        "POZADI": "Pozadi",
        "ZADNJA": "Pozadi",
    }
    localized = {
        "en": {
            "LEVO": "Left",
            "LEVA": "Left",
            "DESNO": "Right",
            "DESNA": "Right",
            "GORE": "Top",
            "DOLE": "Bottom",
            "CENTAR": "Center",
            "NAPRED": "Front",
            "PREDNJA": "Front",
            "POZADI": "Back",
            "ZADNJA": "Back",
        },
        "de": {
            "LEVO": "Links",
            "LEVA": "Links",
            "DESNO": "Rechts",
            "DESNA": "Rechts",
            "GORE": "Oben",
            "DOLE": "Unten",
            "CENTAR": "Mitte",
            "NAPRED": "Vorne",
            "PREDNJA": "Vorne",
            "POZADI": "Hinten",
            "ZADNJA": "Hinten",
        },
        "es": {
            "LEVO": "Izquierda",
            "DESNO": "Derecha",
            "GORE": "Arriba",
            "DOLE": "Abajo",
            "CENTAR": "Centro",
            "NAPRED": "Frente",
            "POZADI": "Atrás",
        },
        "pt-br": {
            "LEVO": "Esquerda",
            "DESNO": "Direita",
            "GORE": "Acima",
            "DOLE": "Abaixo",
            "CENTAR": "Centro",
            "NAPRED": "Frente",
            "POZADI": "Atrás",
        },
        "ru": {
            "LEVO": "Слева",
            "DESNO": "Справа",
            "GORE": "Сверху",
            "DOLE": "Снизу",
            "CENTAR": "Центр",
            "NAPRED": "Спереди",
            "POZADI": "Сзади",
        },
        "zh-cn": {
            "LEVO": "左",
            "DESNO": "右",
            "GORE": "上",
            "DOLE": "下",
            "CENTAR": "中间",
            "NAPRED": "前",
            "POZADI": "后",
        },
        "hi": {
            "LEVO": "बाएँ",
            "DESNO": "दाएँ",
            "GORE": "ऊपर",
            "DOLE": "नीचे",
            "CENTAR": "केंद्र",
            "NAPRED": "आगे",
            "POZADI": "पीछे",
        },
    }.get(lang_key)
    if localized:
        return localized.get(txt.upper(), txt)
    mapping.update({
        "Left": "Levo",
        "Right": "Desno",
        "Top": "Gore",
        "Bottom": "Dole",
        "Center": "Sredina",
        "Front": "Napred",
        "Back": "Pozadi",
    })
    return mapping.get(txt.upper(), txt)


def _short_part_code(value: str) -> str:
    txt = str(value or "").strip()
    m = re.search(r'([A-Z]\d{2})$', txt)
    return m.group(1) if m else txt


_LABEL_NORMALIZATION = {
    # Ispravni oblici — ostaju nepromenjeni
    "Le\u0111a": "Le\u0111a",
    "Le\u0111na plo\u010da": "Le\u0111na plo\u010da",
    "Le\u0111na plo\u010da / prolaz": "Le\u0111na plo\u010da / prolaz",
    "Bo\u010dna plo\u010da": "Bo\u010dna plo\u010da",
    "Bo\u010dna stranica sanduka fioke": "Bo\u010dna stranica sanduka fioke",
    "Zavr\u0161na bo\u010dna plo\u010da": "Zavr\u0161na bo\u010dna plo\u010da",
    "plo\u010da": "plo\u010da",
    # Mojibake varijante → ispravni srpski
    "Le\u00c4\u2018a": "Le\u0111a",
    "Le\u00c3\u201e\u20ac\u02dca": "Le\u0111a",
    "Le\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u00a2\u00e2\u201a\u00ac\u00cb\u0153a": "Le\u0111a",
    "Bo\u00c4\u008dna plo\u00c4\u008da": "Bo\u010dna plo\u010da",
    "Bo\u00c3\u201e\u00c2\u008dna plo\u00c3\u201e\u00c2\u008da": "Bo\u010dna plo\u010da",
    "Bo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008dna plo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008da": "Bo\u010dna plo\u010da",
    "plo\u00c4\u008da": "plo\u010da",
    "plo\u00c3\u201e\u00c2\u008da": "plo\u010da",
    "plo\u00c3\u0192\u00e2\u20ac\u017e\u00c3\u201a\u00c2\u008da": "plo\u010da",
}


def _normalize_label_text(value) -> str:
    txt = str(value or "").strip()
    for src, dst in _LABEL_NORMALIZATION.items():
        txt = txt.replace(src, dst)
    return re.sub(r"\s+", " ", txt).strip()


def _friendly_part_name(value, lang: str = "sr") -> str:
    txt = _normalize_label_text(value)
    txt = re.sub(r"^[A-Z]\d+\s*[\u2014-]\s*", "", txt)
    mapping_sr = {
        "Leva strana": "Leva stranica korpusa",
        "Desna strana": "Desna stranica korpusa",
        "Dno": "Donja plo\u010da korpusa",
        "Plafon": "Gornja plo\u010da korpusa",
        "Vrata": "Front vrata",
        "Front fioke": "Front fioke",
        "Front fioke (unif.)": "Front fioke",
        "Front fioke (kuhinjska jedinica)": "Front fioke ispod rerne",
        "Front fioke (ispod rerne)": "Front fioke ispod rerne",
        "Vrata (ispod sudopere)": "Front vrata ispod sudopere",
        "Vrata rerne": "Front za rernu",
        "Prednja strana sanduka": "Prednja strana sanduka fioke",
        "Zadnja strana sanduka": "Zadnja strana sanduka fioke",
        "Dno sanduka": "Dno sanduka fioke",
        "Bo\u010dna plo\u010da": "Bo\u010dna stranica sanduka fioke",
        "Bocna ploca": "Bo\u010dna stranica sanduka fioke",
        "Le\u0111a": "Le\u0111na plo\u010da",
        "Ledja": "Le\u0111na plo\u010da",
        "Le\u0111a / prolaz": "Le\u0111na plo\u010da / prolaz",
        "Ledja / prolaz": "Le\u0111na plo\u010da / prolaz",
    }
    mapping_en = {
        "Leva strana": "Left carcass side",
        "Desna strana": "Right carcass side",
        "Dno": "Bottom carcass panel",
        "Plafon": "Top carcass panel",
        "Vrata": "Door front",
        "Front fioke": "Drawer front",
        "Front fioke (unif.)": "Drawer front",
        "Front fioke (kuhinjska jedinica)": "Drawer front below oven",
        "Front fioke (ispod rerne)": "Drawer front below oven",
        "Vrata (ispod sudopere)": "Door front below sink",
        "Vrata rerne": "Oven front",
        "Polica (podesiva)": "Adjustable shelf",
        "Prednja strana sanduka": "Drawer box front",
        "Zadnja strana sanduka": "Drawer box back",
        "Dno sanduka": "Drawer box bottom",
        "Bo\u010dna plo\u010da": "Drawer box side",
        "Bocna ploca": "Drawer box side",
        "Le\u0111a": "Back panel",
        "Ledja": "Back panel",
        "Le\u0111a / prolaz": "Back panel / opening",
        "Ledja / prolaz": "Back panel / opening",
    }
    mapping_sr.update({str(v): str(k) for k, v in mapping_en.items()})
    lang_key = normalize_language_code(lang)
    if lang_key == "en":
        return mapping_en.get(txt, txt)
    if lang_key == "sr":
        return mapping_sr.get(txt, txt)

    english_label = mapping_en.get(txt)
    if not english_label:
        if txt in set(mapping_en.values()):
            english_label = txt
        else:
            sr_label = mapping_sr.get(txt, txt)
            english_label = {
                "Leva stranica korpusa": "Left carcass side",
                "Desna stranica korpusa": "Right carcass side",
                "Donja ploča korpusa": "Bottom carcass panel",
                "Gornja ploča korpusa": "Top carcass panel",
                "Front vrata": "Door front",
                "Front fioke": "Drawer front",
                "Front fioke ispod rerne": "Drawer front below oven",
                "Front vrata ispod sudopere": "Door front below sink",
                "Front za rernu": "Oven front",
                "Polica (podesiva)": "Adjustable shelf",
                "Prednja strana sanduka fioke": "Drawer box front",
                "Zadnja strana sanduka fioke": "Drawer box back",
                "Dno sanduka fioke": "Drawer box bottom",
                "Bočna stranica sanduka fioke": "Drawer box side",
                "Leđna ploča": "Back panel",
                "Leđna ploča / prolaz": "Back panel / opening",
            }.get(sr_label, sr_label)
    translated = {
        "de": {
            "Left carcass side": "Linke Korpusseite",
            "Right carcass side": "Rechte Korpusseite",
            "Bottom carcass panel": "Korpusboden",
            "Top carcass panel": "Korpusdeckel",
            "Door front": "Türfront",
            "Drawer front": "Schubladenfront",
            "Drawer front below oven": "Schubladenfront unter dem Backofen",
            "Door front below sink": "Türfront unter der Spüle",
            "Oven front": "Backofenfront",
            "Adjustable shelf": "Verstellbarer Boden",
            "Drawer box front": "Schubladenkasten vorne",
            "Drawer box back": "Schubladenkasten hinten",
            "Drawer box bottom": "Schubladenkastenboden",
            "Drawer box side": "Schubladenkastenseite",
            "Back panel": "Rückwand",
            "Back panel / opening": "Rückwand / Öffnung",
        },
        "es": {
            "Left carcass side": "Lateral izquierdo de carcasa",
            "Right carcass side": "Lateral derecho de carcasa",
            "Bottom carcass panel": "Panel inferior de carcasa",
            "Top carcass panel": "Panel superior de carcasa",
            "Door front": "Frente de puerta",
            "Drawer front": "Frente de cajón",
            "Drawer front below oven": "Frente de cajón bajo horno",
            "Door front below sink": "Frente de puerta bajo fregadero",
            "Oven front": "Frente de horno",
            "Drawer box front": "Frente de caja de cajón",
            "Drawer box back": "Trasera de caja de cajón",
            "Drawer box bottom": "Fondo de caja de cajón",
            "Drawer box side": "Lateral de caja de cajón",
            "Back panel": "Panel trasero",
            "Back panel / opening": "Panel trasero / paso",
        },
        "pt-br": {
            "Left carcass side": "Lateral esquerda da carcaça",
            "Right carcass side": "Lateral direita da carcaça",
            "Bottom carcass panel": "Painel inferior da carcaça",
            "Top carcass panel": "Painel superior da carcaça",
            "Door front": "Frente de porta",
            "Drawer front": "Frente de gaveta",
            "Drawer front below oven": "Frente de gaveta sob o forno",
            "Door front below sink": "Frente de porta sob a pia",
            "Oven front": "Frente do forno",
            "Drawer box front": "Frente da caixa da gaveta",
            "Drawer box back": "Traseira da caixa da gaveta",
            "Drawer box bottom": "Fundo da caixa da gaveta",
            "Drawer box side": "Lateral da caixa da gaveta",
            "Back panel": "Painel traseiro",
            "Back panel / opening": "Painel traseiro / passagem",
        },
        "ru": {
            "Left carcass side": "Левая боковина корпуса",
            "Right carcass side": "Правая боковина корпуса",
            "Bottom carcass panel": "Нижняя панель корпуса",
            "Top carcass panel": "Верхняя панель корпуса",
            "Door front": "Дверной фасад",
            "Drawer front": "Фасад ящика",
            "Drawer front below oven": "Фасад ящика под духовкой",
            "Door front below sink": "Фасад двери под мойкой",
            "Oven front": "Фасад духовки",
            "Drawer box front": "Передняя стенка ящика",
            "Drawer box back": "Задняя стенка ящика",
            "Drawer box bottom": "Дно ящика",
            "Drawer box side": "Боковина ящика",
            "Back panel": "Задняя панель",
            "Back panel / opening": "Задняя панель / проход",
        },
        "zh-cn": {
            "Left carcass side": "左侧柜体板",
            "Right carcass side": "右侧柜体板",
            "Bottom carcass panel": "柜体底板",
            "Top carcass panel": "柜体顶板",
            "Door front": "门板",
            "Drawer front": "抽屉面板",
            "Drawer front below oven": "烤箱下抽屉面板",
            "Door front below sink": "水槽下门板",
            "Oven front": "烤箱面板",
            "Drawer box front": "抽屉盒前板",
            "Drawer box back": "抽屉盒后板",
            "Drawer box bottom": "抽屉盒底板",
            "Drawer box side": "抽屉盒侧板",
            "Back panel": "背板",
            "Back panel / opening": "背板 / 开口",
        },
        "hi": {
            "Left carcass side": "बायाँ ढांचा साइड",
            "Right carcass side": "दायाँ ढांचा साइड",
            "Bottom carcass panel": "ढांचा नीचे का पैनल",
            "Top carcass panel": "ढांचा ऊपर का पैनल",
            "Door front": "दरवाज़ा फ्रंट",
            "Drawer front": "दराज़ फ्रंट",
            "Drawer front below oven": "ओवन के नीचे दराज़ फ्रंट",
            "Door front below sink": "सिंक के नीचे दरवाज़ा फ्रंट",
            "Oven front": "ओवन फ्रंट",
            "Drawer box front": "दराज़ बॉक्स फ्रंट",
            "Drawer box back": "दराज़ बॉक्स बैक",
            "Drawer box bottom": "दराज़ बॉक्स नीचे",
            "Drawer box side": "दराज़ बॉक्स साइड",
            "Back panel": "पीछे का पैनल",
            "Back panel / opening": "पीछे का पैनल / ओपनिंग",
        },
    }
    return translated.get(lang_key, {}).get(english_label, english_label)


def _kant_legend(lang: str = "sr") -> str:
    lang_key = normalize_language_code(lang)
    if lang_key == "en":
        return "Edge legend: T = top edge, B = bottom edge, L = left edge, R = right edge, F = front edge."
    if lang_key == "de":
        return "Kanten-Legende: T = obere Kante, B = untere Kante, L = linke Kante, R = rechte Kante, F = Vorderkante."
    if lang_key == "es":
        return "Leyenda de canto: T = canto superior, B = canto inferior, L = canto izquierdo, R = canto derecho, F = canto frontal."
    if lang_key == "pt-br":
        return "Legenda de orla: T = borda superior, B = borda inferior, L = borda esquerda, R = borda direita, F = borda frontal."
    if lang_key == "ru":
        return "Легенда кромки: T = верхняя кромка, B = нижняя кромка, L = левая кромка, R = правая кромка, F = передняя кромка."
    if lang_key == "zh-cn":
        return "封边图例：T = 上边，B = 下边，L = 左边，R = 右边，F = 前边。"
    if lang_key == "hi":
        return "एज लेजेंड: T = ऊपर की एज, B = नीचे की एज, L = बाईं एज, R = दाईं एज, F = सामने की एज।"
    return "Legenda kanta: T = gornja ivica, B = donja ivica, L = leva ivica, R = desna ivica, F = prednja ivica."


def _format_material_role_pdf(material: str, role: str, lang: str = "sr") -> str:
    mat = str(material or "").strip()
    if not mat:
        return ""
    lang_key = normalize_language_code(lang)
    if lang_key == "en":
        role_map = {
            "carcass": "Carcass",
            "front": "Front",
            "back": "Back",
            "drawer_box": "Drawer box",
            "worktop": "Worktop",
            "plinth": "Plinth",
        }
    elif lang_key == "de":
        role_map = {
            "carcass": "Korpus",
            "front": "Front",
            "back": "Rückwand",
            "drawer_box": "Schubladenkasten",
            "worktop": "Arbeitsplatte",
            "plinth": "Sockel",
        }
    elif lang_key == "es":
        role_map = {
            "carcass": "Carcasa",
            "front": "Frente",
            "back": "Trasera",
            "drawer_box": "Caja de cajón",
            "worktop": "Encimera",
            "plinth": "Zócalo",
        }
    elif lang_key == "pt-br":
        role_map = {
            "carcass": "Carcaça",
            "front": "Frente",
            "back": "Traseiro",
            "drawer_box": "Caixa da gaveta",
            "worktop": "Tampo",
            "plinth": "Soco",
        }
    elif lang_key == "ru":
        role_map = {
            "carcass": "Корпус",
            "front": "Фасад",
            "back": "Задняя панель",
            "drawer_box": "Короб ящика",
            "worktop": "Столешница",
            "plinth": "Цоколь",
        }
    elif lang_key == "zh-cn":
        role_map = {
            "carcass": "柜体",
            "front": "门板",
            "back": "背板",
            "drawer_box": "抽屉盒",
            "worktop": "台面",
            "plinth": "踢脚板",
        }
    elif lang_key == "hi":
        role_map = {
            "carcass": "ढांचा",
            "front": "फ्रंट",
            "back": "पीछे का पैनल",
            "drawer_box": "दराज़ बॉक्स",
            "worktop": "वर्कटॉप",
            "plinth": "सोकल",
        }
    else:
        role_map = {
            "carcass": "Korpus",
            "front": "Front",
            "back": "Leđa",
            "drawer_box": "Sanduk fioke",
            "worktop": "Radna ploča",
            "plinth": "Sokla",
        }
    role_label = role_map.get(str(role or "").strip().lower(), "")
    return f"{mat} {role_label}".strip() if role_label else mat


def _summary_material_label(section_key: str, material: str, lang: str = "sr") -> str:
    skey = str(section_key or "").strip().lower()
    role = {
        "carcass": "carcass",
        "fronts": "front",
        "backs": "back",
        "drawer_boxes": "drawer_box",
        "worktop": "worktop",
        "plinth": "plinth",
    }.get(skey, "carcass")
    return _format_material_role_pdf(material, role, lang=lang)


def _part_role_note(part_name: str, material: str, thickness: str, lang: str = "sr") -> str:
    lang_key = normalize_language_code(lang)
    part = str(part_name or "").lower()
    mat = str(material or "").upper()
    thk = str(thickness or "").strip()
    if "leđ" in part or "ledj" in part or "back panel" in part:
        if mat.startswith("MDF"):
            return {
                "sr": "Tanja zadnja ploča elementa.",
                "en": "Thin back panel of the unit.",
                "de": "Dünne Rückwand des Elements.",
                "es": "Panel trasero fino del módulo.",
                "pt-br": "Painel traseiro fino do módulo.",
                "ru": "Тонкая задняя панель модуля.",
                "zh-cn": "模块的薄背板。",
                "hi": "मॉड्यूल का पतला पीछे का पैनल।",
            }.get(lang_key, "Thin back panel of the unit.")
        if mat.startswith("HDF") or "LESONIT" in mat:
            return {
                "sr": "Zadnja ploča elementa.",
                "en": "Back panel of the unit.",
                "de": "Rückwand des Elements.",
                "es": "Panel trasero del módulo.",
                "pt-br": "Painel traseiro do módulo.",
                "ru": "Задняя панель модуля.",
                "zh-cn": "模块背板。",
                "hi": "मॉड्यूल का पीछे का पैनल।",
            }.get(lang_key, "Back panel of the unit.")
    if "front" in part or "vrata" in part:
        if mat.startswith("MDF"):
            return {
                "sr": f"MDF front {thk} mm.",
                "en": f"MDF front {thk} mm.",
                "de": f"MDF-Front {thk} mm.",
                "es": f"Frente MDF {thk} mm.",
                "pt-br": f"Frente MDF {thk} mm.",
                "ru": f"Фасад MDF {thk} мм.",
                "zh-cn": f"MDF 门板 {thk} mm。",
                "hi": f"MDF फ्रंट {thk} mm.",
            }.get(lang_key, f"MDF front {thk} mm.")
    return ""


def _module_tool_hardware_lines(tid: str, zone: str, lang: str = "sr") -> list[str]:
    _lang = str(lang or "sr").lower().strip()
    FONT_REGULAR, FONT_BOLD = _register_pdf_fonts()
    def _t(sr: str, en: str) -> str:
        return _pdf_t(sr, en, _lang)
    tid_u = str(tid or "").upper()
    lines = [
        _t("Aku-odvijač ili šrafciger", "Drill-driver or screwdriver"),
        _t("Metar", "Tape measure"),
        _t("Libela", "Spirit level"),
    ]
    if zone == "wall":
        lines.append(_t("Nosači za zid / kačenje", "Wall brackets / hanging hardware"))
    if "DOOR" in tid_u or "2DOOR" in tid_u or "1DOOR" in tid_u or "SINK" in tid_u:
        lines.append(_t("Šarke za vrata", "Door hinges"))
    if "DRAWER" in tid_u or "COOKING_UNIT" in tid_u or "TRASH" in tid_u:
        lines.append(_t("Klizači za fioku", "Drawer runners"))
    if "LIFTUP" in tid_u:
        lines.append(_t("Lift-up mehanizam", "Lift-up mechanism"))
    if "GLASS" in tid_u:
        lines.append(_t("Šarke za staklena vrata", "Glass-door hinges"))
    if tid_u == "BASE_DISHWASHER":
        lines.append(_t("Montažni set za front MZS", "Dishwasher front mounting kit"))
    if "WALL" in tid_u:
        lines.append(_t("Tipli / vijci za zid prema podlozi", "Wall plugs / screws according to wall type"))
    return lines


def _module_preassembly_lines(tid: str, zone: str, lang: str = "sr") -> list[str]:
    _lang = str(lang or "sr").lower().strip()
    def _t(sr: str, en: str) -> str:
        return _pdf_t(sr, en, _lang)
    tid_u = str(tid or "").upper()
    lines = [
        _t("Proveri da li broj delova odgovara tabeli.", "Check that the number of parts matches the table."),
        _t("Odvoji korpus, frontove, leđa i okov pre početka sklapanja.", "Separate carcass parts, fronts, backs and hardware before assembly."),
        _t("Pregledaj kantovane ivice da prednja strana elementa bude pravilno okrenuta.", "Check the edged sides so the front of the unit is oriented correctly."),
    ]
    if zone in ("wall", "wall_upper"):
        lines.append(_t("Pre bušenja proveri zid i odaberi odgovarajuće tiple i vijke.", "Before drilling, check the wall type and choose suitable plugs and screws."))
    if "DISHWASHER" in tid_u or "SINK" in tid_u or "HOB" in tid_u or "OVEN" in tid_u:
        lines.append(_t("Pre sklapanja proveri položaj instalacija i otvora za uređaj.", "Before assembly, verify the service positions and appliance opening."))
    if "TALL" in tid_u:
        lines.append(_t("Visoki element obavezno planiraj za pričvršćenje u zid.", "A tall unit must always be planned for wall fixing."))
    return lines

def _find_font_file(filename: str) -> str | None:
    here = Path(__file__).resolve().parent
    cwd = Path.cwd()
    for p in (here / "fonts" / filename, here / filename, cwd / "fonts" / filename, cwd / filename):
        if p.exists():
            return str(p)
    return None


def _register_pdf_fonts() -> tuple[str, str]:
    try:
        pdfmetrics.getFont("DejaVuSans")
        pdfmetrics.getFont("DejaVuSans-Bold")
        return "DejaVuSans", "DejaVuSans-Bold"
    except Exception:
        pass
    reg_file = _find_font_file("DejaVuSans.ttf")
    bold_file = _find_font_file("DejaVuSans-Bold.ttf")
    try:
        if reg_file:
            pdfmetrics.registerFont(TTFont("DejaVuSans", reg_file))
        if bold_file:
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold_file))
        if reg_file and bold_file:
            return "DejaVuSans", "DejaVuSans-Bold"
    except Exception:
        pass
    return "Helvetica", "Helvetica-Bold"


def build_pdf_bytes(
    kitchen: dict,
    *,
    build_cutlist_sections,
    wall_len_h,
    render_fn,
    pd,
    plt,
    render_element_preview,
    assembly_instructions,
    logger,
    lang: str = "sr",
) -> bytes:
    from cutlist import build_service_packet
    """Generiše kompletan PDF krojna liste i vraća ga kao bytes."""
    import re, datetime
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        Image as RLImage, PageBreak, HRFlowable, KeepTogether,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    _lang = str(lang or "sr").lower().strip()

    def _t(sr: str, en: str) -> str:
        return _pdf_t(sr, en, _lang)

    # ── Fonts i helpers ───────────────────────────────────────────────────────
    FONT_REGULAR, FONT_BOLD = _register_pdf_fonts()
    import struct as _struct

    def _safe(text: str) -> str:
        """Ukloni Unicode znakove van Latin-1 opsega (emoji, ①-⑧ → cifre)."""
        _MAP = {'①':'1.','②':'2.','③':'3.','④':'4.',
                '⑤':'5.','⑥':'6.','⑦':'7.','⑧':'8.'}
        for k, v in _MAP.items():
            text = text.replace(k, v)
        return re.sub(r'[^\x00-\xFF]', '', text)

    def _normalize_pdf_text(text: str) -> str:
        txt = str(text or "")
        replacements = {
            "KORAK 1 - BOCNE PLOCE": "KORAK 1 - BOČNE PLOČE",
            "KORAK 2 - DNO I GORNJA PLOCA": "KORAK 2 - DNO I GORNJA PLOČA",
            "KORAK 2 - LEDJA I OTVORI": "KORAK 2 - LEĐA I OTVORI",
            "KORAK 3 - MONTAZA NA ZID": "KORAK 3 - MONTAŽA NA ZID",
            "KORAK 4 - RADNA PLOCA I SUDOPERA": "KORAK 4 - RADNA PLOČA I SUDOPERA",
            "KORAK 5 - ZAVRSNA PROVERA": "KORAK 5 - ZAVRŠNA PROVERA",
            "Ledjna ploča": "Leđna ploča",
            "Ledjna ploca": "Leđna ploča",
            "Sta radis": "Šta radiš",
            "bocne stranice": "bočne stranice",
            "bocnu stranicu": "bočnu stranicu",
            "gornju plocu": "gornju ploču",
            "izmedju bocnih": "između bočnih",
            "izmedju": "između",
            "Pre sledeceg koraka": "Pre sledećeg koraka",
            "busenjima": "bušenjima",
            "okaci vrata": "okači vrata",
            "Obelezi tacnu visinu": "Obeležite tačnu visinu",
            "nosac ili sinu": "nosač ili šinu",
            "Pre zavrsnog stezanja": "Pre završnog stezanja",
            "cvrsto vezan": "čvrsto vezan",
            "sledeci zidni": "sledeći zidni",
            "sledeci element": "sledeći element",
            "sledeci modul": "sledeći modul",
            "Sastavi bocne": "Sastavite bočne",
            "duzina": "dužina",
            "Zastita": "Zaštita",
            "iskljucivo": "isključivo",
            "pricvrscenje": "pričvršćenje",
            "nosace i": "nosače i",
            "nosace": "nosače",
            "nosaca": "nosača",
            "klizaca": "klizača",
            "busenje:": "bušenje:",
            "O35mm dubina": "Ø35mm dubina",
            "Zavrsno": "Završno",
            "ukljuceni": "uključeni",
            "montazna ploca": "montažna ploča",
            "radne ploce": "radne ploče",
            "ploce na nosace": "ploče na nosače",
            "vijak za rucku": "vijak za ručku",
            "po rucki": "po ručki",
            "sinu ili": "šinu ili",
            "za pricvrscenje": "za pričvršćenje",
            "Nosac radne ploce": "Nosač radne ploče",
        }
        for src, dst in replacements.items():
            txt = txt.replace(src, dst)
        return txt

    def _safe(text: str) -> str:
        return re.sub(r"[\x00-\x08\x0B-\x1F\x7F]", '', _normalize_pdf_text(text))

    def _safe_val(v: object, default: str = "-") -> str:
        if v is None:
            return default
        if isinstance(v, float) and math.isnan(v):
            return default
        txt = str(v).strip()
        if txt.lower() in {'', 'nan', 'none', 'null'}:
            return default
        return _safe(txt)

    def _rl_image(uri: str, width: float) -> RLImage:
        """Kreira RLImage iz base64 data URI sa tačnim odnosom visine i širine.

        ReportLab nekad ne skalira visinu automatski (samo siri na zadanu sirinu),
        pa visinu računamo sami iz pixel dimenzija PNG zaglavlja.
        """
        raw  = base64.b64decode(uri.split(',', 1)[1])
        pw   = _struct.unpack('>I', raw[16:20])[0]  # pixel width
        ph   = _struct.unpack('>I', raw[20:24])[0]  # pixel height
        h    = width * ph / max(pw, 1)
        return RLImage(BytesIO(raw), width=width, height=h)

    # ── Page geometry ──────────────────────────────────────────────────────────
    PDF_BUF = BytesIO()
    PW  = A4[0] - 30 * mm           # usable width  ≈ 165 mm
    DOC = SimpleDocTemplate(
        PDF_BUF, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )

    # ── Stilovi ────────────────────────────────────────────────────────────────
    SS  = getSampleStyleSheet()
    C_BLUE  = colors.HexColor('#1E3A5F')
    C_GREEN = colors.HexColor('#2D6A4F')
    C_HDR   = colors.HexColor('#1E3A5F')
    C_ODD   = colors.HexColor('#F0F4F8')

    ST  = ParagraphStyle('KL_T',  parent=SS['Title'],   fontSize=20, spaceAfter=3*mm, fontName=FONT_BOLD)
    H1  = ParagraphStyle('KL_H1', parent=SS['Heading1'],fontSize=13, spaceBefore=6*mm, spaceAfter=2*mm, textColor=C_BLUE, fontName=FONT_BOLD)
    H2  = ParagraphStyle('KL_H2', parent=SS['Heading2'],fontSize=10, spaceBefore=4*mm, spaceAfter=1*mm, textColor=C_GREEN, fontName=FONT_BOLD)
    NRM = ParagraphStyle('KL_N',  parent=SS['Normal'],  fontSize=8, fontName=FONT_REGULAR)
    SB  = ParagraphStyle('KL_SB', parent=SS['Normal'],  fontSize=8,  fontName=FONT_BOLD)
    STP = ParagraphStyle('KL_ST', parent=SS['Normal'],  fontSize=7,  leading=10, fontName=FONT_REGULAR)
    STEP = ParagraphStyle('KL_STEP', parent=SS['Normal'], fontSize=7, leading=10, fontName=FONT_BOLD, textColor=C_BLUE, spaceBefore=1.5*mm)

    def _tbl_style():
        return TableStyle([
            ('BACKGROUND',    (0, 0), (-1,  0), C_HDR),
            ('TEXTCOLOR',     (0, 0), (-1,  0), colors.white),
            ('FONTNAME',      (0, 0), (-1,  0), FONT_BOLD),
            ('FONTSIZE',      (0, 0), (-1,  0), 7),
            ('FONTNAME',      (0, 1), (-1, -1), FONT_REGULAR),
            ('FONTSIZE',      (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, C_ODD]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.grey),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',    (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING',   (0, 0), (-1, -1), 3),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 3),
        ])

    def _tbl_style_compact():
        return TableStyle([
            ('BACKGROUND',    (0, 0), (-1,  0), C_HDR),
            ('TEXTCOLOR',     (0, 0), (-1,  0), colors.white),
            ('FONTNAME',      (0, 0), (-1,  0), FONT_BOLD),
            ('FONTSIZE',      (0, 0), (-1,  0), 6.5),
            ('FONTNAME',      (0, 1), (-1, -1), FONT_REGULAR),
            ('FONTSIZE',      (0, 1), (-1, -1), 6.5),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, C_ODD]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.grey),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',    (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 1.5),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 1.5),
        ])

    story = []

    # ── 1. Naslov ──────────────────────────────────────────────────────────────
    story.append(Paragraph(_t('Krojna Lista', 'Cut List'), ST))
    wl_k  = kitchen.get('wall', {}).get('length_mm', 0)
    wh_k  = kitchen.get('wall', {}).get('height_mm', 0)
    today = datetime.date.today().strftime('%d.%m.%Y')
    story.append(Paragraph(_safe(_t(f'Datum: {today}  |  Zid: {wl_k} x {wh_k} mm', f'Date: {today}  |  Wall: {wl_k} x {wh_k} mm')), NRM))
    story.append(Spacer(1, 4*mm))

    # ── 2. Slika kuhinje ───────────────────────────────────────────────────────
    try:
        _wl_v, _wh_v = wall_len_h(kitchen)
        # Granice koje _setup_view() postavlja u katalog (dizajn) modu:
        #   left_pad=170, right_pad=620, bottom_pad=420, top_pad=150
        _x_total = 170 + _wl_v + 620
        _y_total = 420 + _wh_v + 150
        _aspect  = _x_total / max(_y_total, 1)   # data width / data height

        # Figura: tačne proporcije, 6" visina za jasnu sliku
        _fig_h_in = 6.0
        _fig_w_in = max(_fig_h_in * _aspect, 4.0)

        _fig_k = plt.figure(figsize=(_fig_w_in, _fig_h_in))
        _ax_k  = _fig_k.add_subplot(111)
        # Katalog/dizajn prikaz — lepši izgled u PDF-u, bez tehničkih linija i indikatora
        render_fn(ax=_ax_k, kitchen=kitchen, view_mode='Katalog',
                show_grid=False, grid_mm=10, show_bounds=False,
                kickboard=True, ceiling_filler=False,
                show_free_space=False)
        _fig_k.tight_layout(pad=0.1)
        _kbuf  = BytesIO()
        # bbox_inches='tight' uklanja prazan prostor oko slike
        _fig_k.savefig(_kbuf, format='png', dpi=150, bbox_inches='tight')
        plt.close(_fig_k)
        _kbuf.seek(0)
        # Čitaj stvarne pixel dimenzije iz PNG headera — bbox_inches='tight'
        # menja stvarnu veličinu slike pa se virtuelni ratio ne sme koristiti.
        _raw_png = _kbuf.read()
        _pw_px   = _struct.unpack('>I', _raw_png[16:20])[0]   # pixel width
        _ph_px   = _struct.unpack('>I', _raw_png[20:24])[0]   # pixel height
        _hw_ratio = _ph_px / max(_pw_px, 1)
        _kbuf.seek(0)
        story.append(RLImage(_kbuf, width=PW, height=PW * _hw_ratio))
    except Exception as _ek:
        story.append(Paragraph(_safe(f'Slika nije dostupna: {_ek}'), NRM))
    story.append(Spacer(1, 5*mm))

    # ── 3. Sumarni pregled ─────────────────────────────────────────────────────
    sections = build_cutlist_sections(kitchen)
    service_packet = build_service_packet(kitchen, sections, lang=_lang)
    mods     = kitchen.get('modules', []) or []
    _summary_frames = []
    # Sve sekcije sa ID kolonom — koristi se za prikaz po elementima (sekcija 5)
    all_dfs: list = [
        df for df in (sections or {}).values()
        if df is not None and not df.empty and 'ID' in df.columns
    ]
    for _sec_key, _sec_df in (sections or {}).items():
        if _sec_df is None or _sec_df.empty:
            continue
        _tmp = _sec_df.copy()
        _tmp['__summary_material'] = _tmp['Materijal'].apply(
            lambda _m: _summary_material_label(_sec_key, _m, _lang)
        )
        _summary_frames.append(_tmp)

    if _summary_frames:
        story.append(Paragraph(_t('Sumarni pregled — svi rezovi', 'Summary - all cut parts'), H1))
        _comb = pd.concat(_summary_frames, ignore_index=True)
        _summ = (
            _comb
            .groupby(['__summary_material', 'Deb.', 'CUT_W [mm]', 'CUT_H [mm]', 'Kant'], as_index=False)
            .agg({'Kol.': 'sum'})
            .sort_values(['__summary_material', 'CUT_W [mm]', 'CUT_H [mm]'])
        )
        _sh = [[_t('Materijal', 'Material'), _t('Deb.', 'Thk.'), _t('Dužina [mm]', 'Length [mm]'), _t('Širina [mm]', 'Width [mm]'), _t('Kant', 'Edge'), _t('Kol.', 'Qty')]]
        _sr = [
            [_safe(str(r['__summary_material'])), str(r['Deb.']),
             _safe_val(r.get('CUT_W [mm]')), _safe_val(r.get('CUT_H [mm]')),
             _safe_val(r.get('Kant')), str(int(r['Kol.']))]
            for _, r in _summ.iterrows()
        ]
        _st = Table(_sh + _sr,
                    colWidths=[PW*0.25, PW*0.07, PW*0.14, PW*0.14, PW*0.32, PW*0.08],
                    repeatRows=1)
        _st.setStyle(_tbl_style_compact())
        story.append(_st)
        story.append(Spacer(1, 4*mm))

    _hdr_df = service_packet.get("project_header", pd.DataFrame())
    if _hdr_df is not None and not _hdr_df.empty:
        story.append(Paragraph(_t('Podaci o projektu', 'Project data'), H1))
        _hd = [[_t('Polje', 'Field'), _t('Vrednost', 'Value')]]
        _hd += [[
            _safe(_pdf_localize_text(r.get('Polje', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Vrednost', ''), _lang)),
        ] for r in _hdr_df.to_dict('records')]
        _ht = Table(_hd, colWidths=[PW * 0.22, PW * 0.78], repeatRows=1)
        _ht.setStyle(_tbl_style())
        story.append(_ht)
        story.append(Spacer(1, 4*mm))

    _svc_cuts = service_packet.get("service_cuts", pd.DataFrame())
    if _svc_cuts is not None and not _svc_cuts.empty:
        story.append(Paragraph(_t('Šta nosiš u servis - sečenje', 'What you take to the workshop - cutting'), H1))
        _sh = [['RB', _t('Zid', 'Wall'), _t('Materijal', 'Material'), _t('Deb.', 'Thk.'), _t('CUT Duž.', 'Cut length'), _t('CUT Šir.', 'Cut width'), _t('Kant', 'Edge'), _t('Kol.', 'Qty')]]
        _sr = [[
            str(r.get('RB', '')),
            _safe_val(_pdf_localize_text(r.get('Zid', ''), _lang), '-'),
            _safe(_pdf_localize_text(r.get('Materijal', ''), _lang)),
            str(r.get('Deb.', '')),
            _safe_val(r.get('CUT_W [mm]', '')),
            _safe_val(r.get('CUT_H [mm]', '')),
            _safe_val(r.get('Kant', ''), '-'),
            str(r.get('Kol.', '')),
        ] for r in _svc_cuts.to_dict('records')]
        _st = Table(_sh + _sr,
                    colWidths=[PW*0.05, PW*0.09, PW*0.17, PW*0.07, PW*0.11, PW*0.11, PW*0.24, PW*0.08],
                    repeatRows=1)
        _st.setStyle(_tbl_style())
        story.append(_st)
        story.append(Spacer(1, 3*mm))

    _svc_edge = service_packet.get("service_edge", pd.DataFrame())
    if _svc_edge is not None and not _svc_edge.empty:
        story.append(Paragraph(_t('Šta nosiš u servis - kantovanje', 'What you take to the workshop - edging'), H1))
        _eh = [['PartCode', _t('Zid', 'Wall'), _t('Modul', 'Module'), _t('Deo', 'Part'), _t('Kol.', 'Qty'), _t('Kant', 'Edge'), _t('Napomena', 'Note')]]
        _er = [[
            _safe(str(r.get('PartCode', ''))),
            _safe_val(_pdf_localize_text(r.get('Zid', ''), _lang), '-'),
            _safe(_pdf_localize_text(r.get('Modul', ''), _lang)),
            _safe(_friendly_part_name(r.get('Deo', ''), _lang)),
            str(r.get('Kol.', '')),
            _safe_val(r.get('Kant', ''), '-'),
            _safe(_pdf_localize_text(r.get('Napomena', ''), _lang)),
        ] for r in _svc_edge.to_dict('records')]
        _et = Table(_eh + _er,
                    colWidths=[PW*0.10, PW*0.08, PW*0.16, PW*0.15, PW*0.06, PW*0.18, PW*0.27],
                    repeatRows=1)
        _et.setStyle(_tbl_style())
        story.append(_et)
        story.append(Spacer(1, 3*mm))

    _svc_proc = service_packet.get("service_processing", pd.DataFrame())
    if _svc_proc is not None and not _svc_proc.empty:
        story.append(Paragraph(_t('Šta nosiš u servis - obrada', 'What you take to the workshop - processing'), H1))
        _ph = [['PartCode', _t('Modul', 'Module'), _t('Deo', 'Part'), _t('Tip obrade', 'Processing type'), _t('Izvodi', 'Operations'), _t('Osnov izvođenja', 'Execution basis'), _t('Kol.', 'Qty'), _t('Obrada / napomena', 'Processing / note')]]
        _pr = [[
            _safe(str(r.get('PartCode', ''))),
            _safe(_pdf_localize_text(r.get('Modul', ''), _lang)),
            _safe(_friendly_part_name(r.get('Deo', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Tip obrade', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Izvodi', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Osnov izvođenja', ''), _lang)),
            str(r.get('Kol.', '')),
            _safe(_pdf_localize_text(r.get('Obrada / napomena', ''), _lang)),
        ] for r in _svc_proc.to_dict('records')]
        _pt = Table(_ph + _pr,
                    colWidths=[PW*0.07, PW*0.11, PW*0.10, PW*0.12, PW*0.10, PW*0.16, PW*0.05, PW*0.29],
                    repeatRows=1)
        _pt.setStyle(_tbl_style())
        story.append(_pt)
        story.append(Spacer(1, 4*mm))

    _svc_instr = service_packet.get("service_instructions", pd.DataFrame())
    if _svc_instr is not None and not _svc_instr.empty:
        story.append(Paragraph(_t('Instrukcije za servis', 'Workshop instructions'), H1))
        _ih = [['RB', _t('Stavka', 'Item'), _t('Instrukcija', 'Instruction')]]
        _ir = [[
            str(r.get('RB', '')),
            _safe(_pdf_localize_text(r.get('Stavka', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Instrukcija', ''), _lang)),
        ] for r in _svc_instr.to_dict('records')]
        _it = Table(_ih + _ir,
                    colWidths=[PW*0.06, PW*0.20, PW*0.74],
                    repeatRows=1)
        _it.setStyle(_tbl_style())
        story.append(_it)
        story.append(Spacer(1, 4*mm))

    # ── 4. Detalji po sekcijama ────────────────────────────────────────────────
    _SEC_TITLES = {
        'carcass':      _t('Korpus (stranice, dno, plafon)', 'Carcass (sides, bottom, top)'),
        'backs':        _t('Leđne ploče', 'Back panels'),
        'fronts':       _t('Frontovi', 'Fronts'),
        'drawer_boxes': _t('Sanduk fioke (iverica)', 'Drawer box (chipboard)'),
        'worktop':      _t('Radna ploča i nosači', 'Worktop and supports'),
        'plinth':       _t('Sokla / Lajsna', 'Plinth / toe kick'),
        'hardware':     _t('Okovi (šarke, klizači, mehanizmi)', 'Hardware (hinges, slides, mechanisms)'),
    }
    for _sk, _df in sections.items():
        if _df is None or _df.empty:
            continue
        story.append(Paragraph(_SEC_TITLES.get(_sk, _sk.capitalize()), H1))
        if _sk == 'worktop':
            _sdh = [[
                _t('Modul', 'Module'),
                _t('Duž. zida', 'Wall L'),
                _t('Potrebno', 'Required'),
                _t('Nabavno', 'Purchase'),
                _t('Dub.', 'Depth'),
                _t('Field cut', 'Field cut'),
                _t('Spoj', 'Joint'),
                _t('Izrezi', 'Cut-outs'),
                _t('Napomena', 'Note'),
            ]]
            _sdr = [[
                _safe(_pdf_localize_text(str(r.get('Modul', ''))[:24], _lang)),
                str(int(float(r.get('Wall length [mm]', 0) or 0))) if str(r.get('Wall length [mm]', '')).strip() else '',
                str(int(float(r.get('Required length [mm]', 0) or 0))) if str(r.get('Required length [mm]', '')).strip() else '',
                str(int(float(r.get('Purchase length [mm]', 0) or 0))) if str(r.get('Purchase length [mm]', '')).strip() else '',
                str(int(float(r.get('Širina [mm]', 0) or 0))) if str(r.get('Širina [mm]', '')).strip() else '',
                _safe(_pdf_localize_text(r.get('Field cut', ''), _lang)),
                _safe(_pdf_localize_text(r.get('Joint type', ''), _lang)),
                _safe(_pdf_localize_text(r.get('Cutouts', ''), _lang)),
                _safe(_pdf_localize_text(r.get('Napomena', ''), _lang)),
            ] for r in _df.to_dict('records')]
            _sdt = Table(
                _sdh + _sdr,
                colWidths=[PW*0.15, PW*0.07, PW*0.08, PW*0.08, PW*0.06, PW*0.08, PW*0.07, PW*0.16, PW*0.25],
                repeatRows=1,
            )
        else:
            _rows = []
            for r in _df.to_dict('records'):
                _len_v = r.get('Dužina [mm]', '')
                if str(_len_v).strip() == '':
                    _len_v = r.get('CUT_W [mm]', '')
                _wid_v = r.get('Širina [mm]', '')
                if str(_wid_v).strip() == '':
                    _wid_v = r.get('CUT_H [mm]', '')
                _rows.append([
                    _safe(_pdf_localize_text(str(r.get('Modul', ''))[:22], _lang)),
                    _safe(_friendly_part_name(r.get('Deo', ''), _lang)),
                    _safe_val(_len_v), _safe_val(_wid_v),
                    _safe_val(r.get('Deb.', ''), '-'), str(int(float(r.get('Kol.', 0) or 0))),
                    _safe_val(r.get('Kant', ''), '-'), _safe(_pdf_localize_text(r.get('Napomena', ''), _lang))
                ])
            _sdh = [[_t('Modul', 'Module'), _t('Deo', 'Part'), _t('Duž.', 'Length'), _t('Šir.', 'Width'), _t('Deb.', 'Thk.'), _t('Kol.', 'Qty'), _t('Kant', 'Edge'), _t('Napomena', 'Note')]]
            _sdr = _rows
            _sdt = Table(_sdh + _sdr,
                         colWidths=[PW*0.20, PW*0.13, PW*0.08, PW*0.08,
                                    PW*0.06, PW*0.05, PW*0.20, PW*0.20],
                         repeatRows=1)
        _sdt.setStyle(_tbl_style())
        story.append(_sdt)
        story.append(Spacer(1, 3*mm))

    # ── 5. Po elementima ───────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph(_t('Po elementima - detalji i montaža', 'By unit - details and assembly'), H1))

    _comb_e  = pd.concat(all_dfs, ignore_index=True) if all_dfs else None
    _comb_has_id = (
        _comb_e is not None
        and not _comb_e.empty
        and "ID" in _comb_e.columns
    )
    # Column widths: left = images (2D stacked above 3D), right = cuts + instructions
    IMG_COL  = 50 * mm
    TBL_W    = PW - IMG_COL - 4 * mm   # ≈ 111 mm
    IMG_2D_W = 47 * mm                  # 2D portrait image width in PDF
    IMG_3D_W = 47 * mm                  # 3D landscape image width in PDF

    for _m in mods:
        _mid_e = int(_m.get('id', 0))
        _mlbl  = _safe(_pdf_localize_text(_m.get('label', ''), _lang))
        _mz    = str(_m.get('zone', 'base')).lower()
        _mw    = int(_m.get('w_mm', 0))
        _mh    = int(_m.get('h_mm', 0))
        _md    = int(_m.get('d_mm', 0))
        _mtid  = str(_m.get('template_id', ''))
        _wall  = _safe(_pdf_localize_text(_m.get('wall_key', '') or '', _lang))
        _mparts = _comb_e[_comb_e['ID'] == _mid_e] if _comb_has_id else pd.DataFrame()
        story.append(Paragraph(_t(f"#{_mid_e} – {_mlbl}", f"#{_mid_e} - {_mlbl}"), H2))
        story.append(Paragraph(
            _t(
                f"Tip: {_mtid}  |  Dimenzije: {_mw} × {_mh} × {_md} mm" + (f"  |  Zid: {_wall}" if _wall else ""),
                f"Type: {_mtid}  |  Dimensions: {_mw} × {_mh} × {_md} mm" + (f"  |  Wall: {_wall}" if _wall else ""),
            ),
            NRM,
        ))
        story.append(Spacer(1, 1.5*mm))

        # ── Generate 2D and 3D preview images for PDF ─────────────────────────
        _eimg_2d = None
        _eimg_3d = None
        try:
            _uri_2d, _uri_3d = render_element_preview(
                _m,
                kitchen,
                label_mode="part_codes",
                part_rows=_mparts.to_dict('records') if _mparts is not None and not _mparts.empty else None,
            )
            # _rl_image() reads pixel dims from PNG header to compute correct height
            _eimg_2d = _rl_image(_uri_2d, IMG_2D_W)
            _eimg_3d = _rl_image(_uri_3d, IMG_3D_W)
        except Exception as ex:
            logger.debug("Element preview render failed for id=%s: %s", _mid_e, ex)

        # ── Tabela rezova ──────────────────────────────────────────────────────
        _ptbl = None
        _mtbl = None
        if _mparts is not None and not _mparts.empty:
                _map_parts = _mparts[["PartCode", "Deo", "Pozicija", "SklopKorak", "Kol."]].copy()
                _map_parts["Oznaka"] = _map_parts["PartCode"].map(_short_part_code)
                _map_parts["Deo"] = _map_parts["Deo"].map(lambda v: _friendly_part_name(v, _lang))
                _map_parts["Pozicija"] = _map_parts["Pozicija"].map(lambda v: _friendly_position_name(v, _lang))
                _map_parts = _map_parts.sort_values(["SklopKorak", "PartCode"]).reset_index(drop=True)
                _mhdr = [[_t('Oznaka', 'Label'), _t('Deo', 'Part'), _t('Gde ide', 'Where it goes'), _t('Korak', 'Step'), _t('Kom.', 'Qty')]]
                _mrows = [[
                    _safe(str(r.get('Oznaka', ''))),
                    _safe(str(r.get('Deo', ''))),   # već prevedeno u _map_parts
                    _safe(str(r.get('Pozicija', ''))),
                    str(r.get('SklopKorak', '')),
                    str(r.get('Kol.', '')),
                ] for r in _map_parts.to_dict('records')]
                _mtbl = Table(
                    _mhdr + _mrows,
                    colWidths=[TBL_W*0.14, TBL_W*0.30, TBL_W*0.24, TBL_W*0.10, TBL_W*0.10],
                    repeatRows=1,
                )
                _mtbl.setStyle(_tbl_style())
                _ph = [[_t('Oznaka', 'Label'), _t('Deo', 'Part'), _t('Duž.', 'Length'), _t('Šir.', 'Width'), _t('Deb.', 'Thk.'), _t('Kol.', 'Qty'), _t('Kant', 'Edge')]]
                _pr = [
                    [_safe(_short_part_code(r.get('PartCode', ''))),
                     _safe(_friendly_part_name(r.get('Deo', ''), _lang)),
                     _safe_val((r.get('Dužina [mm]', '') if str(r.get('Dužina [mm]', '')).strip().lower() not in {'', 'nan', 'none', 'null'} else r.get('CUT_W [mm]', ''))),
                     _safe_val((r.get('Širina [mm]', '') if str(r.get('Širina [mm]', '')).strip().lower() not in {'', 'nan', 'none', 'null'} else r.get('CUT_H [mm]', ''))),
                     _safe_val(r.get('Deb.', ''), '-'), str(int(float(r.get('Kol.', 0) or 0))),
                     _safe_val(r.get('Kant', ''), '-')]
                    for r in _mparts.to_dict('records')
                ]
                _ptbl = Table(
                    _ph + _pr,
                    colWidths=[TBL_W*0.12, TBL_W*0.26, TBL_W*0.11, TBL_W*0.11,
                               TBL_W*0.08, TBL_W*0.08, TBL_W*0.24],
                    repeatRows=1,
                )
                _ptbl.setStyle(_tbl_style())

        # ── Uputstvo za montažu ────────────────────────────────────────────────
        _steps = assembly_instructions(_mtid, _mz, m=_m, kitchen=kitchen, lang=lang)
        _step_paras = []
        for s in _steps:
            _txt = _safe(s)
            if str(_txt).strip().startswith("--"):
                _step_paras.append(Paragraph(_txt.replace("--", "").strip(), STEP))
            elif str(_txt).strip():
                _step_paras.append(Paragraph(_txt, STP))
            else:
                _step_paras.append(Spacer(1, 1*mm))

        _tool_lines = _module_tool_hardware_lines(_mtid, _mz, _lang)
        _tool_paras = [Paragraph(_safe(f"• {x}"), STP) for x in _tool_lines]
        _preassembly_lines = _module_preassembly_lines(_mtid, _mz, _lang)
        _preassembly_paras = [Paragraph(_safe(f"• {x}"), STP) for x in _preassembly_lines]
        _role_notes: list[str] = []
        if _mparts is not None and not _mparts.empty:
            for _, _pr in _mparts.iterrows():
                _note = _part_role_note(
                    _friendly_part_name(_pr.get('Deo', ''), _lang),
                    _pr.get('Materijal', ''),
                    _pr.get('Deb.', ''),
                    _lang,
                )
                if _note and _note not in _role_notes:
                    _role_notes.append(_note)
        _role_note_paras = [Paragraph(_safe(f"• {x}"), STP) for x in _role_notes]

        # ── Desna kolona: rezovi + uputstvo ────────────────────────────────────
        _right: list = []
        _right.append(Paragraph(_t('Napomena za početnika', 'Note for beginners'), SB))
        _right.append(Paragraph(
            _t(
                'Oznaka dela na slici, u tabeli i u tekstu je ista. Prvo razvrstaj delove po oznaci, pa tek onda kreni na sklapanje.',
                'The part label is the same in the image, table and text. Sort the parts by label first, then start assembly.',
            ),
            STP,
        ))
        _right.append(Spacer(1, 2*mm))
        if _role_note_paras:
            _right.append(Paragraph(_t('Važne napomene o delovima', 'Important part notes'), SB))
            _right.extend(_role_note_paras)
            _right.append(Spacer(1, 2*mm))
        _right.append(Paragraph(_t('Proveri pre sklapanja', 'Check before assembly'), SB))
        _right.extend(_preassembly_paras)
        _right.append(Spacer(1, 2*mm))
        if _mtbl:
            _right.append(Paragraph(_t('Mapa delova za sklapanje', 'Assembly parts map'), SB))
            _right.append(_mtbl)
            _right.append(Paragraph(_t('Oznake na 2D slici koriste istu kratku oznaku kao i tabela i koraci sklapanja.', 'The labels in the 2D view use the same short label as the table and assembly steps.'), STP))
            _right.append(Spacer(1, 2*mm))
        if _ptbl:
            _right.append(Paragraph(_t('Rezovi', 'Cut parts'), SB))
            _right.append(_ptbl)
            _right.append(Paragraph(_safe(_kant_legend(_lang)), STP))
            _right.append(Spacer(1, 2*mm))
        _right.append(Paragraph(_t('Potreban alat i okov', 'Required tools and hardware'), SB))
        _right.extend(_tool_paras)
        _right.append(Spacer(1, 2*mm))
        _right.append(Paragraph(_t('Uputstvo za montažu', 'Assembly instructions'), SB))
        _right.extend(_step_paras)

        # ── Leva kolona: 2D iznad, 3D ispod — nested Table ────────────────────
        # ReportLab ne podrzava listu flowable-a direktno u celiji Table-a;
        # koristimo nested Table (1 kolona, vise redova) da slazemo slike.
        _img_nested_rows = []
        if _eimg_2d:
            _img_nested_rows.append([Paragraph('2D', STP)])
            _img_nested_rows.append([_eimg_2d])
            _img_nested_rows.append([Paragraph(_t('Oznake na slici prate tabelu dela: C = korpus, B = leđa, F = front, D = fioka.', 'Image labels match the parts table: C = carcass, B = back, F = front, D = drawer.'), STP)])
            _img_nested_rows.append([Spacer(1, 2 * mm)])
        if _eimg_3d:
            _img_nested_rows.append([Paragraph('3D', STP)])
            _img_nested_rows.append([_eimg_3d])

        _img_cell = None
        if _img_nested_rows:
            _inner_tbl = Table(
                _img_nested_rows,
                colWidths=[IMG_COL - 2 * mm],
            )
            _inner_tbl.setStyle(TableStyle([
                ('ALIGN',         (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING',    (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('LEFTPADDING',   (0, 0), (-1, -1), 0),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
            ]))
            _img_cell = _inner_tbl

        # ── Složeni red: [slike | desna kolona] ───────────────────────────────
        _hdr_para = Paragraph(f'#{_mid_e}  {_mlbl}  •  {_mw}x{_mh}x{_md} mm', H2)
        _hr_line  = HRFlowable(width='100%', thickness=0.5, color=C_GREEN)

        if _img_cell is not None:
            _layout = Table(
                [[_img_cell, _right]],
                colWidths=[IMG_COL, TBL_W],
            )
            _layout.setStyle(TableStyle([
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING',   (0, 0), (-1, -1), 2),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
                ('TOPPADDING',    (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            _block = [_hdr_para, _hr_line, Spacer(1, 2*mm), _layout, Spacer(1, 4*mm)]
        else:
            _block = [_hdr_para, _hr_line, Spacer(1, 2*mm)] + _right + [Spacer(1, 4*mm)]

        try:
            story.append(KeepTogether(_block))
        except Exception as ex:
            logger.debug("PDF KeepTogether fallback triggered for module id=%s: %s", _mid_e, ex)
            story.extend(_block)

    _shop_df = service_packet.get("shopping_list", pd.DataFrame())
    if _shop_df is not None and not _shop_df.empty:
        story.append(PageBreak())
        story.append(Paragraph(_t('Šta kupuješ posebno', 'What you buy separately'), H1))
        _hh = [[_t('Grupa', 'Group'), _t('Naziv', 'Name'), _t('Tip / Sifra', 'Type / Code'), _t('Kol.', 'Qty'), _t('Napomena', 'Note')]]
        _rr = [[
            _safe(_pdf_localize_text(r.get('Grupa', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Naziv', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Tip / Šifra', ''), _lang)),
            str(r.get('Kol.', '')),
            _safe(_pdf_localize_text(r.get('Napomena', ''), _lang)),
        ] for r in _shop_df.to_dict('records')]
        _tt = Table(_hh + _rr,
                    colWidths=[PW*0.18, PW*0.22, PW*0.20, PW*0.07, PW*0.33],
                    repeatRows=1)
        _tt.setStyle(_tbl_style())
        story.append(_tt)
        story.append(Spacer(1, 4*mm))

    _ready_df = service_packet.get("ready_made_items", pd.DataFrame())
    if _ready_df is not None and not _ready_df.empty:
        story.append(Paragraph(_t('Gotovi proizvodi - ne ulaze u sečenje', 'Ready-made products - not included in cutting'), H1))
        _rh = [[_t('Grupa', 'Group'), _t('Naziv', 'Name'), _t('Tip / Sifra', 'Type / Code'), _t('Kol.', 'Qty'), _t('Napomena', 'Note')]]
        _rr2 = [[
            _safe(_pdf_localize_text(r.get('Grupa', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Naziv', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Tip / Šifra', ''), _lang)),
            str(r.get('Kol.', '')),
            _safe(_pdf_localize_text(r.get('Napomena', ''), _lang)),
        ] for r in _ready_df.to_dict('records')]
        _rt = Table(_rh + _rr2,
                    colWidths=[PW*0.18, PW*0.22, PW*0.20, PW*0.07, PW*0.33],
                    repeatRows=1)
        _rt.setStyle(_tbl_style())
        story.append(_rt)
        story.append(Spacer(1, 4*mm))

    _guide_df = service_packet.get("user_guide", pd.DataFrame())
    if _guide_df is not None and not _guide_df.empty:
        story.append(Paragraph(_t('Kako ideš redom', 'Workflow order'), H1))
        _gh = [[_t('Korak', 'Step'), _t('Šta radiš', 'What you do'), _t('Napomena', 'Note')]]
        _gr = [[
            str(r.get('Korak', '')),
            _safe(_pdf_localize_text(r.get('Šta radiš', r.get('Sta radis', '')), _lang)),
            _safe(_pdf_localize_text(r.get('Napomena', ''), _lang)),
        ] for r in _guide_df.to_dict('records')]
        _gt = Table(_gh + _gr,
                    colWidths=[PW*0.08, PW*0.30, PW*0.62],
                    repeatRows=1)
        _gt.setStyle(_tbl_style())
        story.append(_gt)
        story.append(Spacer(1, 4*mm))

    for _title, _key in (
        (_t('Checklist pre servisa', 'Checklist before workshop'), 'workshop_checklist'),
        (_t('Checklist pre kucnog sklapanja', 'Checklist before home assembly'), 'home_checklist'),
    ):
        _cdf = service_packet.get(_key, pd.DataFrame())
        if _cdf is None or _cdf.empty:
            continue
        story.append(Paragraph(_title, H1))
        _ch = [['RB', _t('Stavka', 'Item'), _t('Status', 'Status')]]
        _cr = [[
            str(r.get('RB', '')),
            _safe(_pdf_localize_text(r.get('Stavka', ''), _lang)),
            _safe(_pdf_localize_text(r.get('Status', ''), _lang)),
        ] for r in _cdf.to_dict('records')]
        _ct = Table(_ch + _cr,
                    colWidths=[PW*0.06, PW*0.78, PW*0.16],
                    repeatRows=1)
        _ct.setStyle(_tbl_style())
        story.append(_ct)
        story.append(Spacer(1, 3*mm))

    # ── Build ──────────────────────────────────────────────────────────────────
    DOC.build(story)
    PDF_BUF.seek(0)
    return PDF_BUF.read()

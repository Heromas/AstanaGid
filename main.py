import asyncio
import logging
import os
from typing import Any

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8774944807:AAE-VR0XjTXeI7iZ_qdOYpkI2tRnUks0OPM")


ADMIN_IDS: list[int] = []


DEFAULT_LANG: str = "ru"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)



class UserStates(StatesGroup):

    choosing_language = State()
    main_menu = State()
    viewing_places = State()
    viewing_place = State()



TEXTS: dict[str, dict[str, str]] = {

    "ru": {
        "choose_language":  "🌐 Выберите язык / Choose language / Тілді таңдаңыз:",
        "main_menu":        "🏙 <b>Главное меню</b>\nВыберите, чем хотите заняться:",
        "cat_active":       "🎯 Активный отдых",
        "cat_active_desc":  "(ТРЦ, картинг, лошади...)",
        "cat_passive":      "🌿 Пассивный отдых",
        "cat_passive_desc": "(парки, музеи, скверы)",
        "cat_food":         "🍽 Покушать",
        "cat_food_desc":    "(кафе, рестораны, фастфуд)",
        "places_title":     "📍 <b>{category}</b>\nВыберите место:",
        "back_to_menu":     "◀️ Назад к категориям",
        "avg_check":        "💳 Средний чек",
        "cuisine":          "🍴 Кухня",
        "map_link":         "🗺 Открыть на 2GIS",
        "free":             "Бесплатно",
        "not_found":        "⚠️ Извините, информация временно недоступна.",
        "error":            "❌ Произошла ошибка. Попробуйте /start.",
    },

    "en": {
        "choose_language":  "🌐 Выберите язык / Choose language / Тілді таңдаңыз:",
        "main_menu":        "🏙 <b>Main Menu</b>\nWhat would you like to do?",
        "cat_active":       "🎯 Active Recreation",
        "cat_active_desc":  "(malls, karting, horse riding...)",
        "cat_passive":      "🌿 Passive Recreation",
        "cat_passive_desc": "(parks, museums, gardens)",
        "cat_food":         "🍽 Eat Out",
        "cat_food_desc":    "(cafés, restaurants, fast food)",
        "places_title":     "📍 <b>{category}</b>\nChoose a place:",
        "back_to_menu":     "◀️ Back to categories",
        "avg_check":        "💳 Average bill",
        "cuisine":          "🍴 Cuisine",
        "map_link":         "🗺 Open in 2GIS",
        "free":             "Free",
        "not_found":        "⚠️ Sorry, this information is temporarily unavailable.",
        "error":            "❌ An unexpected error occurred. Try /start.",
    },

    "kz": {
        "choose_language":  "🌐 Выберите язык / Choose language / Тілді таңдаңыз:",
        "main_menu":        "🏙 <b>Басты мәзір</b>\nНе істегіңіз келеді?",
        "cat_active":       "🎯 Белсенді демалыс",
        "cat_active_desc":  "(сауда орталықтары, картинг...)",
        "cat_passive":      "🌿 Белсенді емес демалыс",
        "cat_passive_desc": "(парктер, мұражайлар)",
        "cat_food":         "🍽 Тамақтану",
        "cat_food_desc":    "(мейрамхана, кафе)",
        "places_title":     "📍 <b>{category}</b>\nОрынды таңдаңыз:",
        "back_to_menu":     "◀️ Санаттарға оралу",
        "avg_check":        "💳 Орташа шот",
        "cuisine":          "🍴 Асхана",
        "map_link":         "🗺 2GIS-те ашу",
        "free":             "Тегін",
        "not_found":        "⚠️ Кешіріңіз, ақпарат уақытша қолжетімді емес.",
        "error":            "❌ Күтпеген қате орын алды. /start арқылы қайталаңыз.",
    },
}


CATEGORY_NAMES: dict[str, dict[str, str]] = {
    "ru": {"active": "Активный отдых",    "passive": "Пассивный отдых",       "food": "Покушать"},
    "en": {"active": "Active Recreation", "passive": "Passive Recreation",    "food": "Eat Out"},
    "kz": {"active": "Белсенді демалыс",  "passive": "Белсенді емес демалыс", "food": "Тамақтану"},
}



places_data: dict[str, dict[str, dict[str, Any]]] = {


    "active": {
        "khan_shatyr": {
            "name": {"ru": "Хан Шатыр",     "en": "Khan Shatyr",    "kz": "Хан Шатыр"},
            "desc": {
                "ru": (
                    "Крупнейший в мире шатёр-ТРЦ по проекту Нормана Фостера. "
                    "Внутри — аквапарк, монорельс, кинотеатры, ледовый каток, "
                    "детские аттракционы и сотни магазинов."
                ),
                "en": (
                    "The world's largest tent-shaped shopping center by Norman Foster. "
                    "Features an indoor beach resort, monorail, cinemas, ice rink, "
                    "and hundreds of stores."
                ),
                "kz": (
                    "Норман Фостер жобалаған дүниедегі ең үлкен шатыр-сауда орталығы. "
                    "Ішінде аквапарк, монорельс, кинотеатрлар, мұз айдыны бар."
                ),
            },
            "avg_check": {
                "ru": "~3 000 ₸ (развлечения)",
                "en": "~3,000 ₸ (attractions)",
                "kz": "~3 000 ₸ (ойын-сауық)",
            },
            "cuisine": None,
            "gis_url": "https://2gis.kz/astana/firm/70000001018125368?m=71.40356%2C51.132528%2F16",
        },
        "karting_formula": {
            "name": {"ru": "Картинг Formula", "en": "Formula Karting", "kz": "Formula Картинг"},
            "desc": {
                "ru": (
                    "Закрытый картодром с профессиональными картами для взрослых и детей. "
                    "Проводятся корпоративные заезды и турниры. Расположен в ТРЦ Мега Астана."
                ),
                "en": (
                    "Indoor karting track with professional karts for adults and children. "
                    "Corporate events and tournaments available. Located in Mega Astana mall."
                ),
                "kz": (
                    "Мега Астана сауда орталығындағы жабық картодром. "
                    "Ересектер мен балаларға арналған кәсіби карттар."
                ),
            },
            "avg_check": {
                "ru": "~2 500 ₸ / 10 мин",
                "en": "~2,500 ₸ / 10 min",
                "kz": "~2 500 ₸ / 10 мин",
            },
            "cuisine": None,
            "gis_url": "https://2gis.kz/astana/search/%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%B3%20%D0%B0%D1%81%D1%82%D0%B0%D0%BD%D0%B0/firm/70000001038414748?m=71.484142%2C51.133844%2F12.6",
        },
        "horses_ak_bulak": {
            "name": {
                "ru": "Конный клуб «Ак Булак»",
                "en": "Ak Bulak Horse Club",
                "kz": "«Ақ Бұлақ» ат клубы",
            },
            "desc": {
                "ru": (
                    "Конный клуб на окраине Астаны. Предлагает прогулки верхом по степи, "
                    "уроки верховой езды для начинающих и детей, фотосессии с лошадьми."
                ),
                "en": (
                    "Horse club on the outskirts of Astana. Offers horseback rides across "
                    "the steppe, riding lessons for beginners and children, and photo sessions."
                ),
                "kz": (
                    "Астана шетіндегі ат клубы. Дала бойынша серуен, "
                    "жаңадан бастаушыларға сабақ, фотосессия."
                ),
            },
            "avg_check": {
                "ru": "~5 000 ₸ / час",
                "en": "~5,000 ₸ / hour",
                "kz": "~5 000 ₸ / сағат",
            },
            "cuisine": None,
            "gis_url": "https://2gis.kz/astana/firm/70000001090621510/71.489581%2C51.262211?m=71.490068%2C51.260813%2F15.58",
        },
        "mega_astana": {
            "name": {"ru": "ТРЦ Мега Астана", "en": "Mega Astana Mall", "kz": "Мега Астана СОО"},
            "desc": {
                "ru": (
                    "Один из крупнейших ТРЦ Казахстана. Более 200 магазинов, "
                    "фуд-корт, кинотеатр IMAX, детский развлекательный центр и боулинг."
                ),
                "en": (
                    "One of Kazakhstan's largest malls. Over 200 stores, food court, "
                    "IMAX cinema, children's entertainment center, and bowling alley."
                ),
                "kz": (
                    "Қазақстандағы ең ірі сауда орталықтарының бірі. "
                    "200-ден астам дүкен, IMAX кинотеатры, боулинг."
                ),
            },
            "avg_check": {
                "ru": "~2 000 ₸ (развлечения)",
                "en": "~2,000 ₸ (attractions)",
                "kz": "~2 000 ₸ (ойын-сауық)",
            },
            "cuisine": None,
            "gis_url": "https://2gis.kz/astana/firm/70000001026995330?m=71.405441%2C51.089347%2F16",
        },
    },


    "passive": {
        "baiterek": {
            "name": {
                "ru": "Монумент «Байтерек»",
                "en": "Baiterek Monument",
                "kz": "«Бәйтерек» монументі",
            },
            "desc": {
                "ru": (
                    "Символ Астаны — башня высотой 105 м со смотровой площадкой "
                    "в золотом шаре диаметром 22 м. Панорамный вид на весь город."
                ),
                "en": (
                    "The symbol of Astana — a 105-metre tower with an observation deck "
                    "inside a 22-metre golden sphere. Panoramic city views."
                ),
                "kz": (
                    "Астана символы — биіктігі 105 м мұнара. "
                    "22 м алтын шарда бақылау алаңы бар."
                ),
            },
            "avg_check": {
                "ru": "~500 ₸ (вход)",
                "en": "~500 ₸ (entry)",
                "kz": "~500 ₸ (кіру)",
            },
            "cuisine": None,
            "gis_url": "https://2gis.kz/astana/firm/70000001021365759/71.430456%2C51.128301?m=71.430456%2C51.128301%2F16",
        },
        "central_park": {
            "name": {
                "ru": "Центральный парк Астаны",
                "en": "Central Park of Astana",
                "kz": "Астананың орталық паркі",
            },
            "desc": {
                "ru": (
                    "Большой городской парк с аллеями, фонтанами, детскими площадками "
                    "и прогулочными дорожками вдоль реки Есиль. "
                    "Популярное место для семейного отдыха."
                ),
                "en": (
                    "Large city park with alleys, fountains, playgrounds, and walking "
                    "paths along the Yesil River. A popular family destination."
                ),
                "kz": (
                    "Есіл өзені жағасындағы үлкен қала паркі. "
                    "Фонтандар, балалар алаңдары, серуен жолдары."
                ),
            },

            "avg_check": {"ru": None, "en": None, "kz": None},
            "cuisine": None,
            "gis_url": "https://2gis.kz/astana/search/центральный%20парк%20астана",
        },
        "national_museum": {
            "name": {
                "ru": "Национальный музей РК",
                "en": "National Museum of Kazakhstan",
                "kz": "ҚР Ұлттық мұражайы",
            },
            "desc": {
                "ru": (
                    "Крупнейший музей страны площадью 74 000 м². "
                    "Постоянные экспозиции: история Казахстана, Золотой человек, "
                    "зал президента, современное искусство."
                ),
                "en": (
                    "The country's largest museum at 74,000 m². Permanent exhibitions: "
                    "history of Kazakhstan, the Golden Man, presidential hall, "
                    "contemporary art."
                ),
                "kz": (
                    "74 000 м² аумақтағы елдің ең ірі мұражайы. "
                    "Алтын адам, Қазақстан тарихы, президент залы."
                ),
            },
            "avg_check": {
                "ru": "~500 ₸ (вход)",
                "en": "~500 ₸ (entry)",
                "kz": "~500 ₸ (кіру)",
            },
            "cuisine": None,
            "gis_url": "https://2gis.kz/astana/firm/70000001018608940?m=71.469471%2C51.118023%2F16",
        },
        "expo_nur_alem": {
            "name": {
                "ru": "Парк EXPO / «Нур Алем»",
                "en": "EXPO Park / Nur Alem",
                "kz": "EXPO паркі / «Нұр Әлем»",
            },
            "desc": {
                "ru": (
                    "Территория бывшей выставки EXPO-2017. «Нур Алем» — "
                    "самое большое сферическое здание в мире (диаметр 80 м), "
                    "теперь музей будущей энергетики."
                ),
                "en": (
                    "Former EXPO-2017 grounds featuring Nur Alem, the world's largest "
                    "spherical building (80 m diameter), now a museum of future energy."
                ),
                "kz": (
                    "EXPO-2017 аумағы. «Нұр Әлем» — диаметрі 80 м, "
                    "болашақ энергетикасы мұражайы."
                ),
            },
            "avg_check": {
                "ru": "~1 500 ₸ (музей)",
                "en": "~1,500 ₸ (museum)",
                "kz": "~1 500 ₸ (мұражай)",
            },
            "cuisine": None,
            "gis_url": "https://2gis.kz/astana/geo/9570836402930131/71.413807%2C51.090877?m=71.422406%2C51.091256%2F15.62",
        },
    },


    "food": {
        "qazaq_gourmet": {
            "name": {"ru": "Qazaq Gourmet", "en": "Qazaq Gourmet", "kz": "Qazaq Gourmet"},
            "desc": {
                "ru": (
                    "Ресторан авторской казахской кухни в центре Астаны. "
                    "Изысканная подача традиционных блюд: бешбармак, куырдак, казы. "
                    "Интерьер в национальном стиле."
                ),
                "en": (
                    "Upscale Kazakh cuisine restaurant in central Astana. "
                    "Creative takes on traditional dishes: beshbarmak, kuirdak, kazy. "
                    "National-style interior."
                ),
                "kz": (
                    "Астана орталығындағы авторлық қазақ асханасы. "
                    "Бесбармақ, қуырдақ, қазы — дәстүрлі тағамдар."
                ),
            },
            "avg_check": {
                "ru": "~5 000–8 000 ₸",
                "en": "~5,000–8,000 ₸",
                "kz": "~5 000–8 000 ₸",
            },
            "cuisine": {"ru": "Казахская", "en": "Kazakh", "kz": "Қазақ"},
            "gis_url": "https://2gis.kz/astana/search/qazaq%20gourmet",
        },
        "tandyr": {
            "name": {
                "ru": "Ресторан «Тандыр»",
                "en": "Tandyr Restaurant",
                "kz": "«Тандыр» мейрамханасы",
            },
            "desc": {
                "ru": (
                    "Уютный ресторан восточной кухни с живой музыкой по выходным. "
                    "Фирменные блюда: самса из тандыра, лагман, плов по-фергански. "
                    "Большие порции, домашняя атмосфера."
                ),
                "en": (
                    "Cosy Eastern cuisine restaurant with live music on weekends. "
                    "Signature dishes: tandoor samsa, lagman, Fergana-style plov. "
                    "Generous portions, homely atmosphere."
                ),
                "kz": (
                    "Демалыс күндері тірі музыка бар шығыс асханасы. "
                    "Тандыр самсасы, лагман, плов."
                ),
            },
            "avg_check": {
                "ru": "~2 500–4 000 ₸",
                "en": "~2,500–4,000 ₸",
                "kz": "~2 500–4 000 ₸",
            },
            "cuisine": {
                "ru": "Восточная / Узбекская",
                "en": "Eastern / Uzbek",
                "kz": "Шығыс / Өзбек",
            },
            "gis_url": "https://2gis.kz/astana/search/тандыр%20ресторан%20астана",
        },
        "wine_kitchen": {
            "name": {"ru": "Wine & Kitchen", "en": "Wine & Kitchen", "kz": "Wine & Kitchen"},
            "desc": {
                "ru": (
                    "Стильный европейский ресторан с обширной винной картой. "
                    "Меню: паста, стейки, морепродукты. "
                    "Популярен для бизнес-ланчей и романтических ужинов."
                ),
                "en": (
                    "Stylish European restaurant with an extensive wine list. "
                    "Menu: pasta, steaks, seafood. "
                    "Popular for business lunches and romantic dinners."
                ),
                "kz": (
                    "Кең шарап картасы бар стильді еуропалық мейрамхана. "
                    "Паста, стейк, теңіз өнімдері."
                ),
            },
            "avg_check": {
                "ru": "~6 000–12 000 ₸",
                "en": "~6,000–12,000 ₸",
                "kz": "~6 000–12 000 ₸",
            },
            "cuisine": {"ru": "Европейская", "en": "European", "kz": "Еуропалық"},
            "gis_url": "https://2gis.kz/astana/firm/70000001088097597?m=71.424567%2C51.120736%2F16",
        },
        "dastarkhan": {
            "name": {"ru": "Дастархан", "en": "Dastarkhan", "kz": "Дастархан"},
            "desc": {
                "ru": (
                    "Сеть кафе казахской кухни — быстро, сытно, недорого. "
                    "Идеально для обеда: шурпа, манты, бешбармак. "
                    "Несколько точек по всему городу."
                ),
                "en": (
                    "Kazakh food chain — fast, hearty, affordable. "
                    "Perfect for lunch: shurpa, manti, beshbarmak. "
                    "Multiple locations across the city."
                ),
                "kz": (
                    "Жылдам, қанағаттанарлық, арзан қазақ асханасы желісі. "
                    "Шұрпа, манты, бесбармақ."
                ),
            },
            "avg_check": {
                "ru": "~1 200–2 000 ₸",
                "en": "~1,200–2,000 ₸",
                "kz": "~1 200–2 000 ₸",
            },
            "cuisine": {"ru": "Казахская", "en": "Kazakh", "kz": "Қазақ"},
            "gis_url": "https://2gis.kz/astana/search/дастархан%20астана",
        },
    },
}



def kb_language() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский",  callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English",  callback_data="lang_en"),
            InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz"),
        ]
    ])


def kb_main_menu(lang: str) -> InlineKeyboardMarkup:

    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{t['cat_active']} {t['cat_active_desc']}",
            callback_data="cat_active",
        )],
        [InlineKeyboardButton(
            text=f"{t['cat_passive']} {t['cat_passive_desc']}",
            callback_data="cat_passive",
        )],
        [InlineKeyboardButton(
            text=f"{t['cat_food']} {t['cat_food_desc']}",
            callback_data="cat_food",
        )],
    ])


def kb_places(category: str, lang: str) -> InlineKeyboardMarkup:

    buttons = [
        [InlineKeyboardButton(
            text=place["name"][lang],
            callback_data=f"place_{category}_{place_id}",
        )]
        for place_id, place in places_data.get(category, {}).items()
    ]
    buttons.append([InlineKeyboardButton(
        text=TEXTS[lang]["back_to_menu"],
        callback_data="back_to_menu",
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def kb_back_to_menu(lang: str) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=TEXTS[lang]["back_to_menu"],
            callback_data="back_to_menu",
        )]
    ])




def build_place_card(place: dict[str, Any], lang: str, category: str) -> str:

    t = TEXTS[lang]

    lines: list[str] = [
        f"<b>{place['name'][lang]}</b>\n",
        place["desc"][lang],
        "",
    ]


    check_value: str | None = place["avg_check"].get(lang)
    check_label: str = check_value if check_value else t["free"]
    lines.append(f"{t['avg_check']}: <b>{check_label}</b>")


    if category == "food":
        cuisine_data: dict | None = place.get("cuisine")
        if cuisine_data:
            lines.append(f"{t['cuisine']}: <b>{cuisine_data[lang]}</b>")


    lines.append(f"\n<a href=\"{place['gis_url']}\">{t['map_link']}</a>")

    return "\n".join(lines)




async def cmd_start(message: Message, state: FSMContext) -> None:

    await state.clear()  # сбрасываем предыдущий диалог, если он был
    await state.set_state(UserStates.choosing_language)
    await message.answer(
        text=TEXTS["ru"]["choose_language"],  # строка содержит все три языка
        reply_markup=kb_language(),
    )


async def cb_language(callback: CallbackQuery, state: FSMContext) -> None:

    lang: str = callback.data.split("_")[1]  # "lang_ru" → "ru"

    # Валидация кода языка
    if lang not in TEXTS:
        lang = DEFAULT_LANG

    await state.update_data(lang=lang)
    await state.set_state(UserStates.main_menu)

    await callback.message.edit_text(
        text=TEXTS[lang]["main_menu"],
        reply_markup=kb_main_menu(lang),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


async def cb_category(callback: CallbackQuery, state: FSMContext) -> None:

    data = await state.get_data()
    lang: str = data.get("lang", DEFAULT_LANG)

    category: str = callback.data.split("_", 1)[1]


    if category not in places_data:
        logger.warning("Неизвестная категория в callback: %s", category)
        await callback.answer(TEXTS[lang]["not_found"], show_alert=True)
        return

    await state.update_data(current_category=category)
    await state.set_state(UserStates.viewing_places)

    category_title = CATEGORY_NAMES[lang][category]
    await callback.message.edit_text(
        text=TEXTS[lang]["places_title"].format(category=category_title),
        reply_markup=kb_places(category, lang),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


async def cb_place(callback: CallbackQuery, state: FSMContext) -> None:

    data = await state.get_data()
    lang: str = data.get("lang", DEFAULT_LANG)


    parts = callback.data.split("_", 2)
    if len(parts) != 3:
        logger.error("Некорректный callback_data: %s", callback.data)
        await callback.answer(TEXTS[lang]["not_found"], show_alert=True)
        return

    _, category, place_id = parts


    category_data = places_data.get(category)
    if category_data is None:
        logger.warning("Категория не найдена: %s", category)
        await callback.answer(TEXTS[lang]["not_found"], show_alert=True)
        return

    place = category_data.get(place_id)
    if place is None:
        logger.warning("Место не найдено: %s / %s", category, place_id)
        await callback.answer(TEXTS[lang]["not_found"], show_alert=True)
        return

    card_text = build_place_card(place, lang, category)

    await state.set_state(UserStates.viewing_place)
    await callback.message.edit_text(
        text=card_text,
        reply_markup=kb_back_to_menu(lang),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    await callback.answer()


async def cb_back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:

    data = await state.get_data()
    lang: str = data.get("lang", DEFAULT_LANG)

    await state.set_state(UserStates.main_menu)
    await callback.message.edit_text(
        text=TEXTS[lang]["main_menu"],
        reply_markup=kb_main_menu(lang),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()



async def main() -> None:

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError(
            "BOT_TOKEN не задан. "
            "Укажите токен в файле .env или переменной окружения."
        )

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)


    dp.message.register(cmd_start, CommandStart())

    dp.callback_query.register(cb_language,     F.data.startswith("lang_"))
    dp.callback_query.register(cb_category,     F.data.startswith("cat_"))
    dp.callback_query.register(cb_place,        F.data.startswith("place_"))
    dp.callback_query.register(cb_back_to_menu, F.data == "back_to_menu")

    logger.info("✅ Бот запущен. Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot, skip_updates=True)


import nest_asyncio

if __name__ == "__main__":

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    try:

        loop.create_task(main())
        print("Бот запущен! Отправьте /start в Telegram.")
    except Exception as e:
        logger.critical(f"Ошибка при запуске: {e}")
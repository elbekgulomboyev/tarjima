import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from deep_translator import GoogleTranslator
# asdfafasdfsdf
# Windows ulanish xatoligini oldini olish uchun
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.INFO)

TOKEN = "7989031508:AAF7WWqRdcwgVK2iEdqcnJ8U_KnvcD_7-9A"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Bot bosqichlari (Holatlar)
class TranslateStates(StatesGroup):
    choosing_lang = State()  # Til tanlash bosqichi
    waiting_for_text = State() # Matn kutish bosqichi

LANGUAGES = {
    "uz": "🇺🇿 O'zbek",
    "en": "🇺🇸 English",
    "ru": "🇷🇺 Русский",
    "tr": "🇹🇷 Türkçe",
    "ar": "🇸🇦 العربية",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "zh-CN": "🇨🇳 中文",
    "ko": "🇰🇷 한국어"
}

def get_translation_keyboard():
    builder = InlineKeyboardBuilder()
    for code, name in LANGUAGES.items():
        builder.add(types.InlineKeyboardButton(text=name, callback_data=f"to_{code}"))
    builder.adjust(2)
    return builder.as_markup()

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear() # Har safar start bosilganda eski ma'lumotlarni o'chirish
    await message.answer(
        "✨ **Aqlli Tarjimon Botga xush kelibsiz!**\n\n"
        "Avval matnni qaysi tilga tarjima qilishni tanlang:",
        reply_markup=get_translation_keyboard(),
        parse_mode="Markdown"
    )
    # Holatni "Til tanlash"ga o'tkazamiz
    await state.set_state(TranslateStates.choosing_lang)

@dp.callback_query(F.data.startswith("to_"), TranslateStates.choosing_lang)
async def language_chosen(callback: types.CallbackQuery, state: FSMContext):
    target_lang = callback.data.split("_")[1]
    lang_name = LANGUAGES.get(target_lang)
    
    # Tanlangan tilni xotiraga saqlab qo'yamiz
    await state.update_data(target_lang=target_lang, lang_name=lang_name)
    
    await callback.message.edit_text(
        f"✅ Tanlangan til: **{lang_name}**\n\nEndi tarjima qilinishi kerak bo'lgan **matnni yuboring**:",
        parse_mode="Markdown"
    )
    # Holatni "Matn kutish"ga o'tkazamiz
    await state.set_state(TranslateStates.waiting_for_text)
    await callback.answer()

@dp.message(TranslateStates.waiting_for_text)
async def translate_text(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, faqat matn yuboring.")
        return

    # Xotiradan til ma'lumotlarini olamiz
    data = await state.get_data()
    target_lang = data.get("target_lang")
    lang_name = data.get("lang_name")

    wait_msg = await message.answer(f"🔄 **{lang_name}** tiliga tarjima qilinmoqda...")

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(message.text)
        
        await message.answer(
            f"✅ **Natija ({lang_name}):**\n\n`{translated}`",
            parse_mode="Markdown"
        )
        
        # Tarjima tugagach, foydalanuvchiga yana til tanlash imkonini beramiz
        await message.answer("Yana tarjima qilishni xohlaysizmi? Yangi tilni tanlang:", reply_markup=get_translation_keyboard())
        await state.set_state(TranslateStates.choosing_lang)

    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
    finally:
        await wait_msg.delete()

async def main():
    print("FSM Tarjimon bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
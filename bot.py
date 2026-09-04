import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")


# =========================
# MENU PRINCIPAL
# =========================

def menu_principal():
    keyboard = [
        [
            InlineKeyboardButton("📄 Criar meu CV", callback_data="criar_cv"),
            InlineKeyboardButton("✏️ Editar CV", callback_data="editar_cv"),
        ],
        [
            InlineKeyboardButton("🎨 Modelos de CV", callback_data="modelos"),
            InlineKeyboardButton("📝 Carta de Apresentação", callback_data="carta"),
        ],
        [
            InlineKeyboardButton("💼 Dicas de Emprego", callback_data="emprego"),
            InlineKeyboardButton("❓ Ajuda", callback_data="ajuda"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = (
        "👋 *Bem-vindo ao CV Pro!*\n\n"
        "O teu assistente para criar documentos profissionais "
        "e aumentar as tuas chances de conseguir um emprego.\n\n"
        "Escolhe uma opção abaixo:"
    )

    await update.message.reply_text(
        texto,
        parse_mode="Markdown",
        reply_markup=menu_principal()
    )


# =========================
# BOTÃO VOLTAR
# =========================

def botao_voltar():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Voltar ao menu", callback_data="menu")]
    ])


# =========================
# BOTÕES
# =========================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "menu":

        texto = (
            "🏠 *Menu Principal*\n\n"
            "O que queres fazer?"
        )

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=menu_principal()
        )


    elif query.data == "criar_cv":

        texto = (
            "📄 *Criar CV Profissional*\n\n"
            "Vamos criar o teu currículo passo a passo.\n\n"
            "Em breve vou pedir informações como:\n"
            "• Nome\n"
            "• Contacto\n"
            "• Formação académica\n"
            "• Experiência profissional\n"
            "• Competências\n"
            "• Idiomas\n"
            "• Objetivo profissional\n\n"
            "🚀 Esta função está a ser preparada."
        )

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=botao_voltar()
        )


    elif query.data == "editar_cv":

        texto = (
            "✏️ *Editar CV*\n\n"
            "Aqui poderás modificar um CV que já criaste.\n\n"
            "🚀 Função em desenvolvimento."
        )

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=botao_voltar()
        )


    elif query.data == "modelos":

        texto = (
            "🎨 *Modelos de CV*\n\n"
            "Escolhe o estilo que combina contigo:\n\n"
            "1️⃣ Profissional\n"
            "2️⃣ Moderno\n"
            "3️⃣ Minimalista\n"
            "4️⃣ Executivo\n"
            "5️⃣ Primeiro emprego\n\n"
            "🚀 Os modelos estarão disponíveis em breve."
        )

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=botao_voltar()
        )


    elif query.data == "carta":

        texto = (
            "📝 *Carta de Apresentação*\n\n"
            "Cria uma carta profissional personalizada "
            "para acompanhar o teu CV.\n\n"
            "🚀 Função em desenvolvimento."
        )

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=botao_voltar()
        )


    elif query.data == "emprego":

        texto = (
            "💼 *Dicas de Emprego*\n\n"
            "Aqui vais encontrar dicas sobre:\n\n"
            "• Como fazer um bom CV\n"
            "• Como preparar uma entrevista\n"
            "• Como procurar emprego\n"
            "• Como escrever uma carta de apresentação\n"
            "• Como destacar as tuas competências\n\n"
            "🚀 Conteúdo em desenvolvimento."
        )

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=botao_voltar()
        )


    elif query.data == "ajuda":

        texto = (
            "❓ *Ajuda — CV Pro*\n\n"
            "Usa /start para abrir o menu principal.\n\n"
            "Se precisares de criar um CV, escolhe "
            "\"📄 Criar meu CV\".\n\n"
            "🚀 Mais funcionalidades serão adicionadas."
        )

        await query.edit_message_text(
            texto,
            parse_mode="Markdown",
            reply_markup=botao_voltar()
        )


# =========================
# INICIAR BOT
# =========================

if not TOKEN:
    raise ValueError("BOT_TOKEN não foi configurado.")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(botoes))

print("CV Pro iniciado...")

app.run_polling()

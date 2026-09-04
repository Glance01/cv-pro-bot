import os
from io import BytesIO

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
)

TOKEN = os.getenv("BOT_TOKEN")

# Estados da criação do CV
(
    NOME,
    CONTACTO,
    EMAIL,
    LOCALIDADE,
    OBJETIVO,
    FORMACAO,
    EXPERIENCIA,
    COMPETENCIAS,
    IDIOMAS,
) = range(9)


# =========================================================
# MENU PRINCIPAL
# =========================================================

def menu_principal():
    keyboard = [
        [
            InlineKeyboardButton("📄 Criar meu CV", callback_data="criar_cv"),
        ],
        [
            InlineKeyboardButton("🎨 Modelos de CV", callback_data="modelos"),
            InlineKeyboardButton("📝 Carta", callback_data="carta"),
        ],
        [
            InlineKeyboardButton("💼 Dicas de Emprego", callback_data="emprego"),
            InlineKeyboardButton("❓ Ajuda", callback_data="ajuda"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    texto = (
        "👋 *Bem-vindo ao CV Pro!*\n\n"
        "Cria um currículo profissional diretamente pelo Telegram.\n\n"
        "Escolhe uma opção:"
    )

    await update.message.reply_text(
        texto,
        parse_mode="Markdown",
        reply_markup=menu_principal(),
    )


# =========================================================
# FUNÇÃO PARA VOLTAR
# =========================================================

def teclado_voltar():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Voltar ao menu", callback_data="menu")]
    ])


async def mostrar_menu_query(query):
    await query.edit_message_text(
        "🏠 *Menu Principal*\n\nO que queres fazer?",
        parse_mode="Markdown",
        reply_markup=menu_principal(),
    )


# =========================================================
# INICIAR CRIAÇÃO DO CV
# =========================================================

async def iniciar_cv(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    await query.edit_message_text(
        "📄 *Vamos criar o teu CV!*\n\n"
        "Vou fazer algumas perguntas.\n"
        "Responde normalmente a cada uma delas.\n\n"
        "1/9 — Qual é o teu *nome completo*?",
        parse_mode="Markdown",
    )

    return NOME


async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["nome"] = update.message.text

    await update.message.reply_text(
        "2/9 — Qual é o teu *número de telefone*?",
        parse_mode="Markdown",
    )

    return CONTACTO


async def receber_contacto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["contacto"] = update.message.text

    await update.message.reply_text(
        "3/9 — Qual é o teu *email*?\n\n"
        "Se não tiveres, escreve: Não tenho",
        parse_mode="Markdown",
    )

    return EMAIL


async def receber_email(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["email"] = update.message.text

    await update.message.reply_text(
        "4/9 — Em que *cidade/província* resides?",
        parse_mode="Markdown",
    )

    return LOCALIDADE


async def receber_localidade(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["localidade"] = update.message.text

    await update.message.reply_text(
        "5/9 — Qual é o teu *objetivo profissional*?\n\n"
        "Exemplo:\n"
        "Procuro uma oportunidade na área de eletricidade industrial.",
        parse_mode="Markdown",
    )

    return OBJETIVO


async def receber_objetivo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["objetivo"] = update.message.text

    await update.message.reply_text(
        "6/9 — Fala sobre a tua *formação académica/profissional*.\n\n"
        "Exemplo:\n"
        "Técnico de Eletricidade Industrial — Nível V — 2026",
        parse_mode="Markdown",
    )

    return FORMACAO


async def receber_formacao(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["formacao"] = update.message.text

    await update.message.reply_text(
        "7/9 — Descreve a tua *experiência profissional*.\n\n"
        "Se ainda não tens experiência, escreve:\n"
        "Sem experiência profissional.",
        parse_mode="Markdown",
    )

    return EXPERIENCIA


async def receber_experiencia(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["experiencia"] = update.message.text

    await update.message.reply_text(
        "8/9 — Quais são as tuas principais *competências*?\n\n"
        "Exemplo:\n"
        "Instalações elétricas, manutenção, leitura de esquemas, trabalho em equipa.",
        parse_mode="Markdown",
    )

    return COMPETENCIAS


async def receber_competencias(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["competencias"] = update.message.text

    await update.message.reply_text(
        "9/9 — Quais são os teus *idiomas*?\n\n"
        "Exemplo:\n"
        "Português — Excelente\n"
        "Inglês — Básico",
        parse_mode="Markdown",
    )

    return IDIOMAS


async def receber_idiomas(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["idiomas"] = update.message.text

    await update.message.reply_text(
        "⏳ *A preparar o teu CV...*",
        parse_mode="Markdown",
    )

    pdf = gerar_cv_pdf(context.user_data)

    await update.message.reply_document(
        document=pdf,
        filename="CV_Profissional.pdf",
        caption=(
            "✅ *CV criado com sucesso!*\n\n"
            "Guarda este documento e utiliza-o nas tuas candidaturas."
        ),
        parse_mode="Markdown",
    )

    await update.message.reply_text(
        "🏠 Queres fazer outra coisa?",
        reply_markup=menu_principal(),
    )

    return ConversationHandler.END


# =========================================================
# GERAR PDF
# =========================================================

def gerar_cv_pdf(dados):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    nome_style = ParagraphStyle(
        "Nome",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    contacto_style = ParagraphStyle(
        "Contacto",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        spaceAfter=18,
    )

    titulo_style = ParagraphStyle(
        "Titulo",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=7,
    )

    texto_style = ParagraphStyle(
        "Texto",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=6,
    )

    story = []

    nome = dados.get("nome", "")
    contacto = dados.get("contacto", "")
    email = dados.get("email", "")
    localidade = dados.get("localidade", "")

    story.append(Paragraph(nome.upper(), nome_style))

    contacto_texto = (
        f"{contacto} | {email} | {localidade}"
    )

    story.append(
        Paragraph(contacto_texto, contacto_style)
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.black,
            spaceAfter=10,
        )
    )

    # PERFIL
    story.append(
        Paragraph("OBJETIVO PROFISSIONAL", titulo_style)
    )

    story.append(
        Paragraph(
            dados.get("objetivo", ""),
            texto_style,
        )
    )

    # FORMAÇÃO
    story.append(
        Paragraph("FORMAÇÃO", titulo_style)
    )

    story.append(
        Paragraph(
            dados.get("formacao", ""),
            texto_style,
        )
    )

    # EXPERIÊNCIA
    story.append(
        Paragraph("EXPERIÊNCIA PROFISSIONAL", titulo_style)
    )

    story.append(
        Paragraph(
            dados.get("experiencia", ""),
            texto_style,
        )
    )

    # COMPETÊNCIAS
    story.append(
        Paragraph("COMPETÊNCIAS", titulo_style)
    )

    competencias = dados.get("competencias", "")

    for item in competencias.split(","):
        item = item.strip()

        if item:
            story.append(
                Paragraph(
                    "• " + item,
                    texto_style,
                )
            )

    # IDIOMAS
    story.append(
        Paragraph("IDIOMAS", titulo_style)
    )

    story.append(
        Paragraph(
            dados.get("idiomas", ""),
            texto_style,
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Currículo criado com CV Pro",
            ParagraphStyle(
                "Rodape",
                parent=styles["Normal"],
                fontSize=8,
                alignment=TA_CENTER,
            ),
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer


# =========================================================
# OUTRAS OPÇÕES
# =========================================================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "menu":

        await mostrar_menu_query(query)

    elif query.data == "modelos":

        await query.edit_message_text(
            "🎨 *Modelos de CV*\n\n"
            "Em breve poderás escolher entre vários modelos:\n\n"
            "1️⃣ Profissional\n"
            "2️⃣ Moderno\n"
            "3️⃣ Minimalista\n"
            "4️⃣ Executivo\n"
            "5️⃣ Primeiro emprego\n\n"
            "A geração atual utiliza o modelo profissional.",
            parse_mode="Markdown",
            reply_markup=teclado_voltar(),
        )

    elif query.data == "carta":

        await query.edit_message_text(
            "📝 *Carta de Apresentação*\n\n"
            "Em breve poderás criar uma carta de apresentação "
            "personalizada para acompanhar o teu CV.",
            parse_mode="Markdown",
            reply_markup=teclado_voltar(),
        )

    elif query.data == "emprego":

        await query.edit_message_text(
            "💼 *Dicas de Emprego*\n\n"
            "• Mantém o teu CV atualizado.\n"
            "• Usa um email profissional.\n"
            "• Adapta o CV à vaga.\n"
            "• Prepara-te para entrevistas.\n"
            "• Destaca competências relevantes.\n"
            "• Revê o CV antes de enviar.",
            parse_mode="Markdown",
            reply_markup=teclado_voltar(),
        )

    elif query.data == "ajuda":

        await query.edit_message_text(
            "❓ *Ajuda*\n\n"
            "Usa /start para abrir o menu.\n\n"
            "Escolhe 'Criar meu CV' e responde às perguntas. "
            "No final receberás o teu CV em PDF.",
            parse_mode="Markdown",
            reply_markup=teclado_voltar(),
        )


# =========================================================
# CANCELAR
# =========================================================

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "❌ Criação cancelada.\n\n"
        "Quando quiseres começar novamente, usa /start."
    )

    return ConversationHandler.END


# =========================================================
# CONFIGURAÇÃO
# =========================================================

if not TOKEN:
    raise ValueError("BOT_TOKEN não foi configurado.")


app = Application.builder().token(TOKEN).build()


# Conversação para criação do CV
cv_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            iniciar_cv,
            pattern="^criar_cv$"
        )
    ],

    states={

        NOME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_nome
            )
        ],

        CONTACTO: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_contacto
            )
        ],

        EMAIL: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_email
            )
        ],

        LOCALIDADE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_localidade
            )
        ],

        OBJETIVO: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_objetivo
            )
        ],

        FORMACAO: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_formacao
            )
        ],

        EXPERIENCIA: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_experiencia
            )
        ],

        COMPETENCIAS: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_competencias
            )
        ],

        IDIOMAS: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                receber_idiomas
            )
        ],
    },

    fallbacks=[
        CommandHandler("cancelar", cancelar)
    ],
)


app.add_handler(CommandHandler("start", start))

app.add_handler(cv_conversation)

app.add_handler(
    CallbackQueryHandler(botoes)
)


print("CV Pro iniciado...")

app.run_polling()

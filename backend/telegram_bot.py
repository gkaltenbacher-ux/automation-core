"""
Telegram Bot — Conversational Control via Telegram.
Webhook-basiert (kein Polling). Nutzt den Orchestrator fuer Antworten.

Konfiguration ueber client.json:
    "telegram": {
        "enabled": true,
        "help_text": "...",
        "start_text": "...",
        "commands": [
            {"command": "stats", "description": "Statistiken", "message": "Zeig mir Statistiken"}
        ]
    }
"""
import logging
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes,
)

logger = logging.getLogger(__name__)

DEFAULT_START_TEXT = (
    "Ich bin dein AgentCore24 Bot.\n"
    "Schreib mir was du brauchst!\n\n"
    "/help fuer mehr"
)

DEFAULT_HELP_TEXT = (
    "*AgentCore24 Bot Hilfe*\n\n"
    "*Befehle:*\n"
    "/start -- Bot starten\n"
    "/help -- Diese Hilfe\n\n"
    "Schreib mir einfach was du brauchst."
)


class TelegramBot:
    def __init__(self, bot_token: str, orchestrator, allowed_user_ids: list[int] = None, config: dict = None):
        self.bot_token = bot_token
        self.orchestrator = orchestrator
        self.allowed_user_ids = allowed_user_ids or []
        self.config = config or {}

        self.start_text = self.config.get("start_text", DEFAULT_START_TEXT)
        self.help_text = self.config.get("help_text", DEFAULT_HELP_TEXT)

        self.app = Application.builder().token(bot_token).build()

        # Standard-Commands
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))

        # Dynamische Commands aus Config
        for cmd_def in self.config.get("commands", []):
            cmd_name = cmd_def["command"]
            cmd_message = cmd_def.get("message", cmd_name)
            self.app.add_handler(
                CommandHandler(cmd_name, self._make_command_handler(cmd_message))
            )

        # Message Handlers
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_message))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.on_document))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.on_photo))
        self.app.add_handler(CallbackQueryHandler(self.on_callback))

    def _allowed(self, user_id: int) -> bool:
        if not self.allowed_user_ids:
            return True
        return user_id in self.allowed_user_ids

    def _make_command_handler(self, message_to_orchestrator: str):
        async def handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            if not self._allowed(update.effective_user.id):
                return
            await update.message.chat.send_action("typing")
            response = await self.orchestrator.chat(
                message_to_orchestrator,
                user_id=str(update.effective_user.id),
            )
            await update.message.reply_text(response)
        return handler

    # === COMMANDS ===

    async def cmd_start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not self._allowed(update.effective_user.id):
            await update.message.reply_text("Kein Zugriff.")
            return
        await update.message.reply_text(self.start_text)

    async def cmd_help(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not self._allowed(update.effective_user.id):
            return
        await update.message.reply_text(self.help_text, parse_mode="Markdown")

    # === MESSAGE HANDLERS ===

    async def on_message(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not self._allowed(update.effective_user.id):
            return
        await update.message.chat.send_action("typing")
        try:
            response = await self.orchestrator.chat(
                update.message.text,
                user_id=str(update.effective_user.id),
            )
            buttons = _extract_buttons(response)
            clean_text = _clean_button_tags(response)

            if buttons:
                await update.message.reply_text(clean_text, reply_markup=InlineKeyboardMarkup(buttons))
            else:
                await update.message.reply_text(clean_text)
        except Exception as e:
            logger.error(f"Telegram Fehler: {e}")
            await update.message.reply_text(f"Fehler: {e}")

    async def on_document(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not self._allowed(update.effective_user.id):
            return
        doc = update.message.document
        await update.message.reply_text(f"Datei erhalten: {doc.file_name}\nWas soll ich damit machen?")

    async def on_photo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not self._allowed(update.effective_user.id):
            return
        await update.message.reply_text("Bild erhalten! Was soll ich damit tun?")

    async def on_callback(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.chat.send_action("typing")

        response = await self.orchestrator.chat(
            f"[BUTTON_CLICK] {query.data}",
            user_id=str(update.effective_user.id),
        )
        await query.message.reply_text(_clean_button_tags(response))

    # === WEBHOOK ===

    async def setup_webhook(self, webhook_url: str):
        await self.app.bot.set_webhook(webhook_url)
        logger.info(f"Telegram Webhook: {webhook_url}")

    async def process_update(self, update_data: dict):
        async with self.app:
            update = Update.de_json(update_data, self.app.bot)
            await self.app.process_update(update)


# === HELPER ===

def _extract_buttons(text: str) -> list[list[InlineKeyboardButton]]:
    matches = re.findall(r"\[BUTTON:([^|]+)\|([^\]]+)\]", text)
    if not matches:
        return []
    rows = []
    row = []
    for action, label in matches:
        row.append(InlineKeyboardButton(label, callback_data=action[:64]))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return rows


def _clean_button_tags(text: str) -> str:
    return re.sub(r"\[BUTTON:[^\]]+\]", "", text).strip()

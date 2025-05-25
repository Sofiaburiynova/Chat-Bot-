import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Состояния
ASK_ROOMS, ASK_PARTICIPANTS = range(2)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def generate_schedule(participant_count, rooms):
    participants = list(range(1, participant_count + 1))
    num_rooms = len(rooms)

    if participant_count < num_rooms * 2:
        raise ValueError("Слишком мало участников для распределения!")

    schedule = []

    for _ in range(3):  # 3 тура
        random.shuffle(participants)
        room_assignments = {}

        for i, room in enumerate(rooms):
            start = i * (participant_count // num_rooms)
            end = (i + 1) * (participant_count // num_rooms)
            room_participants = participants[start:end]

            if i == num_rooms - 1:
                room_participants += participants[end:]

            room_assignments[room] = room_participants

        schedule.append(room_assignments)

    return schedule


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет команда brainz 💚! Введите номера аудиторий через запятую (например: 101, 205, 310):")
    return ASK_ROOMS


async def get_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rooms = [r.strip() for r in update.message.text.split(',')]
    context.user_data['rooms'] = rooms
    await update.message.reply_text("Введите количество участников:")
    return ASK_PARTICIPANTS


async def get_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rooms = context.user_data['rooms']
        participant_count = int(update.message.text)

        schedule = generate_schedule(participant_count, rooms)

        response = []
        for round_num, assignments in enumerate(schedule, 1):
            response.append(f"🏁 *Тур {round_num}*\\:")
            for room, people in assignments.items():
                people_str = ', '.join(map(str, people))
                response.append(f"*Аудитория {room}*\\: {people_str}")
            response.append("")

        await update.message.reply_text(
            text='\n'.join(response),
            parse_mode='MarkdownV2'
        )

    except Exception as e:
        error_message = str(e).replace('!', '\!').replace('.', '\.').replace('-', '\-')
        logging.error(f"Ошибка: {error_message}")
        await update.message.reply_text(
            text=f"*Ошибка\\:* {error_message}\n\nПопробуйте ещё раз\!",
            parse_mode='MarkdownV2'
        )

    await update.message.reply_text(
        text="🔁 Для нового распределения введите /start\n"
             "❗ Если что\-то пошло не так \- начните сначала командой /start",
        parse_mode='MarkdownV2'
    )
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token("7562272916:AAF_A_RZYDAbwkq4y8ldAvwZ1fDdtPYAo1k").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_rooms)],
            ASK_PARTICIPANTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_participants)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == '__main__':
    main()

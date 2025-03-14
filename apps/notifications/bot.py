import logging
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, Updater
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.questions.models import Question, Answer
from django.contrib.contenttypes.models import ContentType
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

def ustaz_required(func):
    def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        try:
            user = User.objects.get(profile__telegram_id=user_id, profile__is_ustaz=True)
            return func(update, context, user, *args, **kwargs)
        except User.DoesNotExist:
            update.message.reply_text("У вас нет прав устаза для этой команды.")
            return None

    return wrapper

def login_required(func):
    def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        try:
            user = User.objects.get(profile__telegram_id=user_id)
            return func(update, context, user, *args, **kwargs)
        except User.DoesNotExist:
            update.message.reply_text("Вы не привязали свой Telegram к аккаунту на сайте. "
                                      "Авторизуйтесь на сайте и заполните профиль.")
            return None

    return wrapper

def start(update, context):
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    user_id = update.effective_user.id

    welcome_message = f"Ассаламу алейкум, {first_name}!\n\n"

    try:
        user = User.objects.get(profile__telegram=username)

        if user.profile.is_ustaz:
            welcome_message += "Вы зарегистрированы как устаз. Вы будете получать уведомления о новых вопросах.\n\n"
            welcome_message += "Доступные команды:\n"
            welcome_message += "/questions - показать неотвеченные вопросы\n"
            welcome_message += "/events - показать предстоящие встречи\n"
            welcome_message += "/lessons - показать последние уроки\n"
        else:
            welcome_message += "Вы успешно привязали свой Telegram к аккаунту на сайте.\n"
            welcome_message += "Теперь вы будете получать уведомления об ответах на ваши вопросы, новых уроках и встречах.\n\n"
            welcome_message += "Доступные команды:\n"
            welcome_message += "/myquestions - показать ваши вопросы\n"
            welcome_message += "/events - показать предстоящие встречи\n"
            welcome_message += "/lessons - показать последние уроки\n"

        user.profile.telegram_id = user_id
        user.profile.save()

    except User.DoesNotExist:
        welcome_message += "Ваш Telegram не привязан к аккаунту на сайте.\n"
        welcome_message += "Для получения уведомлений об ответах на вопросы, пожалуйста:\n"
        welcome_message += "1. Войдите на сайт\n"
        welcome_message += "2. Заполните свой профиль, указав Telegram: @" + str(username) + "\n"

    update.message.reply_text(welcome_message)

@ustaz_required
def list_unanswered_questions(update, context, user):
    questions = Question.objects.filter(is_answered=False).order_by('-created_at')[:5]

    if questions:
        for question in questions:
            keyboard = [
                [InlineKeyboardButton("Ответить", callback_data=f"answer_{question.id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            from_user = question.user.username if question.user else question.telegram
            message = f"Вопрос #{question.id} от {from_user}:\n\n{question.clean_content()[:300]}"

            if len(question.clean_content()) > 300:
                message += "...\n\nНажмите 'Ответить' для просмотра полного вопроса."

            update.message.reply_text(message, reply_markup=reply_markup)
    else:
        update.message.reply_text("Нет неотвеченных вопросов.")


@login_required
def list_my_questions(update, context, user):
    questions = Question.objects.filter(user=user).order_by('-created_at')
    page = context.user_data.get('my_questions_page', 0)
    per_page = 3
    total_pages = (questions.count() + per_page - 1) // per_page
    questions_page = questions[page * per_page:(page + 1) * per_page]

    if not questions.exists():
        update.message.reply_text("📝 У вас пока нет заданных вопросов.")
        return

    for i, question in enumerate(questions_page):
        if question.is_answered:
            status_emoji = "✅"
            status_text = "ОТВЕЧЕН"
        else:
            status_emoji = "⏳"
            status_text = "В ОЖИДАНИИ"
        message = f"<b>🔷 ВОПРОС #{question.id}</b>\n"
        message += f"<i>{status_emoji} Статус: {status_text}</i>\n\n"
        message += f"{question.clean_content()[:200]}"

        if len(question.clean_content()) > 200:
            message += "..."
        keyboard = []
        if question.is_answered:
            keyboard.append([
                InlineKeyboardButton("📖 Показать ответ", callback_data=f"show_answer_{question.id}"),
                InlineKeyboardButton("🌐 Открыть на сайте", url=f"https://al-hanafiyah.com/questions/{question.id}")
            ])
        nav_buttons = []
        if total_pages > 1:
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️ Предыдущие", callback_data="prev_my_questions"))

            nav_buttons.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="page_info"))

            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("Следующие ➡️", callback_data="next_my_questions"))

        if nav_buttons:
            keyboard.append(nav_buttons)
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    if page == 0 and total_pages > 1:
        nav_help = "⚠️ <i>У вас есть еще вопросы. Используйте кнопки навигации для просмотра.</i>"
        update.message.reply_text(nav_help, parse_mode='HTML')

def list_events(update, context):
    from django.utils import timezone
    from apps.events.models import OfflineEvent
    events = OfflineEvent.objects.filter(event_date__gte=timezone.now()).order_by('event_date')[:5]

    if events:
        for event in events:
            event_date = event.event_date.strftime('%d.%m.%Y %H:%M') if event.event_date else 'Дата не указана'
            message = f"📅 <b>{event.title}</b>\n\n"
            message += f"📆 Дата: {event_date}\n"
            message += f"📍 Место: {event.location}\n\n"
            message += f"ℹ️ {event.description[:200]}..."

            update.message.reply_text(message, parse_mode='HTML')
    else:
        update.message.reply_text("Нет предстоящих мероприятий.")

def list_lessons(update, context):
    from apps.lessons.models import Lesson
    lessons = Lesson.objects.all().order_by('-created_at')[:5]

    if lessons:
        for lesson in lessons:
            message = f"🎓 <b>Урок</b>\n\n"
            message += f"📚 Модуль: {lesson.module.name}\n"
            message += f"📖 Тема: {lesson.module.topic.name}\n"
            message += f"🏛 Категория: {lesson.module.topic.category.name}\n"
            message += f"🎬 Тип: {lesson.get_media_type_display()}\n"

            keyboard = [
                [InlineKeyboardButton("Открыть урок", url=f"https://al-hanafiyah.com/lessons/{lesson.slug}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')
    else:
        update.message.reply_text("Уроки не найдены.")

@ustaz_required
def answer_callback(update, context, user):
    query = update.callback_query
    query.answer()

    question_id = query.data.split('_')[1]

    try:
        question = Question.objects.get(id=question_id)

        context.user_data['answering_question'] = question_id
        from_user = question.user.username if question.user else question.telegram
        message = f"Вопрос #{question.id} от {from_user}:\n\n{question.clean_content()}"
        message += "\n\nОтветьте, отправив сообщение."

        query.edit_message_text(message)
    except Question.DoesNotExist:
        query.edit_message_text("Вопрос не найден.")


@ustaz_required
def process_answer(update, context, user):
    question_id = context.user_data.get('answering_question')

    if not question_id:
        update.message.reply_text("❗️ Выберите вопрос для ответа сначала с помощью /questions")
        return

    try:
        question = Question.objects.get(id=question_id)
        answer_text = update.message.text

        with transaction.atomic():
            answer, created = Answer.objects.update_or_create(
                question=question,
                defaults={'content': answer_text}
            )

            question.is_answered = True
            question.save()

        if question.user and question.user.profile.telegram_id:
            try:
                notification_message = (
                    f"<b>🔔 УВЕДОМЛЕНИЕ</b>\n\n"
                    f"Ассаламу алейкум! Устаз ответил на ваш вопрос.\n\n"
                    f"<b>📝 ВАШ ВОПРОС:</b>\n"
                    f"<i>{question.clean_content()[:150]}...</i>\n\n"
                    f"<b>✅ ОТВЕТ УСТАЗА:</b>\n"
                    f"{answer_text[:200]}...\n\n"
                )

                keyboard = [
                    [InlineKeyboardButton("📖 Прочитать полный ответ",
                                          url=f"https://al-hanafiyah.com/questions/{question.id}")],
                    [
                        InlineKeyboardButton("👍 Благодарить", callback_data=f"thank_{question.id}"),
                        InlineKeyboardButton("❓ Задать ещё", callback_data="ask_new")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                bot.send_message(
                    chat_id=question.user.profile.telegram_id,
                    text=notification_message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )

                content_type = ContentType.objects.get_for_model(question)
                Notification.objects.create(
                    user=question.user,
                    title="Ответ на ваш вопрос",
                    message=f"Устаз ответил на ваш вопрос: {question.clean_content()[:100]}...",
                    notification_type="question_answer",
                    content_type=content_type,
                    object_id=question.id,
                    url=f"/questions/{question.id}",
                    sent_to_telegram=True
                )

                confirmation = (
                    f"<b>✅ ОТВЕТ ОТПРАВЛЕН</b>\n\n"
                    f"Ваш ответ успешно отправлен пользователю. "
                    f"Уведомление доставлено.\n\n"
                    f"<i>Награда за ваш труд ожидает вас у Аллаха</i> 🕌"
                )
                update.message.reply_text(confirmation, parse_mode='HTML')

            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
                update.message.reply_text(
                    f"⚠️ <b>Ответ сохранен</b>, но возникла проблема при отправке уведомления: {e}",
                    parse_mode='HTML'
                )
        else:
            update.message.reply_text(
                "✅ <b>Ответ сохранен</b>, но пользователь не получит уведомление, "
                "так как не привязал Telegram к своему аккаунту.",
                parse_mode='HTML'
            )

        context.user_data.pop('answering_question', None)

    except Question.DoesNotExist:
        update.message.reply_text("❌ Вопрос не найден.")


def run_bot():
    updater = Updater(token=settings.TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("questions", list_unanswered_questions))
    dp.add_handler(CommandHandler("myquestions", list_my_questions))
    dp.add_handler(CommandHandler("events", list_events))
    dp.add_handler(CommandHandler("lessons", list_lessons))
    dp.add_handler(CallbackQueryHandler(answer_callback, pattern=r'^answer_'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_answer))
    updater.start_polling()
    updater.idle()

def start_bot():
    try:
        updater = Updater(token=settings.TELEGRAM_BOT_TOKEN, use_context=True)

        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("questions", list_unanswered_questions))
        dp.add_handler(CommandHandler("myquestions", list_my_questions))
        dp.add_handler(CommandHandler("events", list_events))
        dp.add_handler(CommandHandler("lessons", list_lessons))
        dp.add_handler(CallbackQueryHandler(answer_callback, pattern=r'^answer_'))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_answer))
        updater.start_polling(drop_pending_updates=True)
        print("Telegram бот запущен!")
    except Exception as e:
        print(f"Ошибка запуска бота: {e}")
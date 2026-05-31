# bot.py
import configparser
import datetime
import numpy as np
from telethon import TelegramClient, events
from predictor import ZonePredictator
from visualizer import plot_zones  # или plot_simple_zones

# Access credentials
config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('default', 'api_id')
api_hash = config.get('default', 'api_hash')
BOT_TOKEN = config.get('default', 'BOT_TOKEN')

# Create the client
client = TelegramClient('sessions/session_master', api_id, api_hash).start(bot_token=BOT_TOKEN)

# Загрузка модели
print("Загрузка модели...")
predictor = ZonePredictator()
print("Модель загружена!")


# Define the /start command - исправлено: флаг (?i) убран, используем case-insensitive через функцию
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    SENDER = sender.id
    text = (
        "🤖 Docker Bot Ready!\n\n"
        "Я предсказываю зоны нарушения сплошности по трем перемещениям и помогаю определить каким образом их лучше крепить.\n\n"
        "<b>Как использовать:</b>\n"
        "Отправьте три числа через пробел:\n"
        "<code>перемещение_кровли перемещение_бока перемещение_подошвы</code>\n\n"
        "<b>Пример:</b>\n"
        "<code>15 10 5</code>\n\n"
        "Замечание: перемещение кровли принадлежит промежутку [0, 25], боков - [0, 100], попошвы - [0, 25]\n"
        "Доступные команды:\n"
        "/start\n"
    )
    await client.send_message(SENDER, text, parse_mode='html')

# Обработка текстовых сообщений (три числа через пробел)
@client.on(events.NewMessage)
async def handle_message(event):
    # Пропускаем команды
    if event.message.text.startswith('/'):
        return
    
    sender = await event.get_sender()
    text = event.message.text.strip()
    
    # Пробуем распарсить три числа
    try:
        parts = text.split()
        if len(parts) != 3 or float(parts[0]) > 25 or float(parts[1]) > 100 or float(parts[2]) > 25 or min([float(parts[0]), float(parts[1]), float(parts[2])]) < 0:
            await client.send_message(
                sender.id, 
                "❌ Ошибка: нужно отправить <b>ровно три числа</b> через пробел и в верном интервале.\n"
                "Пример: <code>7.5 5 3.236</code>\n\n",
                parse_mode='html'
            )
            return
        
        # Преобразуем в float
        displacements = np.array([-1*float(parts[0]), -1*float(parts[1]), float(parts[2])], dtype=np.float32)
        
        # Отправляем сообщение о начале обработки
        processing_msg = await client.send_message(sender.id, "⏳ Обработка запроса...")
        
        num_zones, pred_data = predictor.get_real_zones(displacements)

        print('ok_0')

        ima, add_data = plot_zones(num_zones, pred_data, displacements)
        
        print('ok_1')

        # Формируем ответ
        if float(parts[0]) ==0 and float(parts[1]) ==0 and float(parts[2]) ==0:
            reply = (
                "⚠️ <b>Результат предсказания</b>\n\n"
                "Не предсказано ни одной зоны нарушения сплошности.\n"
                "Перемещения слишком малы"
            )
        else:
            reply = "🔍 <b>Появившиеся области нарушения сплошности лучше всего закрепить следующим образом:</b>\n\n"
            for i, zone in enumerate(add_data):
                reply += (
                    f"<b>Анкер {i+1}</b>\n"
                    f"  • Координата X начала крепления: <code>{zone[0]:.2f}</code>\n"
                    f"  • Координата Y начала крепления: <code>{zone[1]:.2f}</code>\n"
                    f"  • Длина анкера: <code>{zone[2]:.1f}</code>\n\n"
                )
        print('ok_3')
        try:
            img_buf = ima
            img_buf.name = 'prediction.png'
            img_buf.seek(0)
            # Отправляем изображение
            await client.send_file(
                sender.id,
                img_buf,
                caption=reply,
                parse_mode='html',
                force_document=False,  # КЛЮЧЕВОЙ параметр: не отправлять как файл
                supports_streaming=True  # Для изображений
                )
        except Exception as img_error:
            # Если не удалось создать изображение, отправляем только текст
            print(f"Image error: {img_error}")
            await client.send_message(sender.id, reply, parse_mode='html')
        
        # Удаляем сообщение о процессе и отправляем результат
        await processing_msg.delete()
        #await client.send_message(sender.id, reply, parse_mode='html')
        
    except ValueError:
        await client.send_message(
            sender.id,
            "❌ <b>Ошибка формата</b>\n\n"
            "Не удалось распознать числа. Убедитесь, что вы отправляете три числа через пробел.\n"
            "Используйте точку (.) как десятичный разделитель.\n\n"
            "Пример: <code>0.275 -0.191 0.415</code>",
            parse_mode='html'
        )
    except Exception as e:
        await client.send_message(
            sender.id,
            f"❌ <b>Внутренняя ошибка</b>\n\n"
            f"Произошла ошибка при обработке запроса:\n"
            f"<code>{str(e)}</code>",
            parse_mode='html'
        )
        print(f"Error: {e}")

### MAIN
if __name__ == '__main__':
    print("🤖 Bot Started!")
    print("Waiting for messages...")
    client.run_until_disconnected()
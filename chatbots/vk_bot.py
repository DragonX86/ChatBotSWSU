from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from backend.search_engine import SearchEngine
from chatbots.common.abs_bot import AbstractBot
from chatbots.common.abs_keyboard import AbstractKeyboard


class VkKeyBoard(AbstractKeyboard):
    @staticmethod
    def get_standard_keyboard():
        keyboard = VkKeyboard(one_time=False)

        keyboard.add_button("Поиск по идиомам", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Поиск по аббревиатурам", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Перевести текст", color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button("Завершить работу", color=VkKeyboardColor.NEGATIVE)

        return keyboard

    @staticmethod
    def get_initial_keyboard():
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button("Начать", color=VkKeyboardColor.PRIMARY)
        return keyboard

    @staticmethod
    def get_mode_keyboard():
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)
        return keyboard


class VkontakteBot(AbstractBot):
    def __init__(self, token: str):
        self.vk_session = VkApi(token=token)
        self.long_poll = VkBotLongPoll(self.vk_session, '210776300')
        self.engine = SearchEngine()
        self.working_mode = None

    def handle_idiom(self, message):
        result = self.engine.find_idiom(message.text)
        self.send_reply(message.from_id, result)

    def handle_abbreviations(self, message):
        result = self.engine.find_abbreviations(message.text)
        self.send_reply(message.from_id, result)

    def handle_translate(self, message):
        result = self.engine.get_translate(message.text)
        self.send_reply(message.from_id, result)

    def route_messages(self, message):
        if message.text == "Начать":
            keyboard = VkKeyBoard.get_standard_keyboard()
            self.send_keyboard(message.from_id, "Привет.", keyboard)
        if message.text == "Назад":
            keyboard = VkKeyBoard.get_standard_keyboard()
            self.send_keyboard(message.from_id, "Выход в главное меню", keyboard)
            self.working_mode = None
        elif message.text == "Поиск по идиомам":
            keyboard = VkKeyBoard.get_mode_keyboard()
            self.send_keyboard(message.from_id, "Режим поиска по идиомам", keyboard)
            self.working_mode = "idiom_mode"
        elif message.text == "Поиск по аббревиатурам":
            keyboard = VkKeyBoard.get_mode_keyboard()
            self.send_keyboard(message.from_id, "Режим поиска по аббревиатурам", keyboard)
            self.working_mode = "abbreviations_mode"
        elif message.text == "Перевести текст":
            keyboard = VkKeyBoard.get_mode_keyboard()
            self.send_keyboard(message.from_id, "Введите то, что хотите перевести", keyboard)
            self.working_mode = "translate_mode"
        elif message.text == "Завершить работу":
            keyboard = VkKeyBoard.get_initial_keyboard()
            self.send_keyboard(message.from_id, "Пока.", keyboard)
        else:
            if self.working_mode == "idiom_mode":
                self.handle_idiom(message)
            elif self.working_mode == "abbreviations_mode":
                self.handle_abbreviations(message)
            elif self.working_mode == "translate_mode":
                self.handle_translate(message)

    def send_keyboard(self, user_id, message, keyboard):
        self.vk_session.method("messages.send", {
            "user_id": user_id,
            "message": message,
            "keyboard": keyboard.get_keyboard(),
            "random_id": 0
        })

    def send_reply(self, user_id, message):
        self.vk_session.method("messages.send", {
            "user_id": user_id,
            "message": message,
            "random_id": 0
        })

    def run(self):
        def _handle(event):
            if event.type == VkBotEventType.MESSAGE_NEW:
                self.route_messages(event.message)

        list(map(
            lambda event: _handle(event),
            self.long_poll.listen()
        ))

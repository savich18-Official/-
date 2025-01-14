English version:
How to run
All the libraries required for the bot are provided in the requirements.txt file. To run the program, clone the repository and install the listed libraries: pip install -r requirements.txt.

The values ​​of the telegram bot tokens and the API used are stored in the project environment variables .env. The bot is launched with the python main.py or python bot.py command from the terminal.

How to use
When running the bot, the user has access to the following commands:

/start and /help - display a welcome message to the user
/low - displays the category selected by the user in ascending order of rating (Lowest rating)
/hight - displays the category selected by the user in descending order of rating (Highest rating)
/custom - displays the selected category in the rating range specified by the user
/history - displays brief information about the last 10 user requests
/cancel - cancels the previously selected command /low, /hight or /custom

Русская версия:
Как запустить
Все необходимые библиотеки для работы бота представлены в файле requirements.txt. Для запуска программы клонируйте репозиторий и установите перечисленные библиотеки: pip install -r requirements.txt.

Значения токенов телеграм-бота и используемой API хранятся в переменных окружения проекта .env. Запуск бота осуществляется командой python main.py или python bot.py из терминала.

Как пользоваться
При запуске бота пользователю доступны следующие команды:

/start и /help - выводят приветственное сообщение пользователю
/low - выводит выбранную пользователем категорию в порядке возрастания рейтинга (Самый низкий рейтинг)
/hight - выводит выбранную пользователем категорию в порядке убывания рейтинга (Самый высокий рейтинг)
/custom - выводит выбранную категорию в диапазоне рейтинга, указанного пользователем
/history - отображает краткую информацию о последних 10 запросах пользователя
/cancel - отменяет работу ранее выбранной команды /low, /hight или /custom

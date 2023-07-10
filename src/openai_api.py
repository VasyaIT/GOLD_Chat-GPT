import openai
from openai.error import ServiceUnavailableError, RateLimitError

from config import API_KEY, logger
# from translation import translation

openai.api_key = API_KEY


async def generate_answer(text: str, user_id: int) -> str:
    # prompt, language = translation(text)
    # print(language)

    try:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}],
            max_tokens=2000
        )
    except ServiceUnavailableError:
        logger.warning('OpenAI сервер перегружен')
        return 'Ошибка на сервере\nПопробуй ещё раз'
    except RateLimitError:
        logger.warning(f'{user_id} сделал больше трёх запросов в минуту')
        return 'Нельзя делать больше 3 запросов в минуту, ️сорян 🤷‍♂️'

    return completion['choices'][0]['message']['content']

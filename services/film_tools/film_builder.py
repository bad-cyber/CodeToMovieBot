from .helper import emoji


def build_film(name: str, duration: str, score: float, genre: str, year: int, country: str, desc: str):
  str_film = (f'──────────────────────────'
            f'\n| 🎥 {name}'
            f'\n| ⌛️ Длительность: {duration}'
            f'\n| ⭐️ Рейтинг: {score} IMdb'
            f'\n| 🎭 Жанр: {genre}'
            f'\n| 🗓️ Год: {year}'
            f'\n| {emoji(country)} Страна: {country}'
            f'\n| 📝 Описание: '
            f'\n {desc}')
  return str_film

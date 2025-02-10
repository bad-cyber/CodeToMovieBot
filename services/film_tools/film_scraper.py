import requests
from bs4 import BeautifulSoup
import logging
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_session():
    """Create a session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

async def get_filminfo(url):
    """
    Получает информацию о фильме с сайта film.ru
    
    Args:
        url (str): URL страницы фильма на film.ru
        
    Returns:
        dict: Словарь с информацией о фильме
        
    Raises:
        ValueError: Если не удалось получить или обработать данные
    """
    # Проверка URL
    if not url or not isinstance(url, str):
        raise ValueError("Некорректный URL")
    
    if not url.startswith('https://www.film.ru/movies/'):
        raise ValueError("URL должен быть с сайта film.ru")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    }

    session = create_session()

    try:
        logger.info(f"Fetching data from URL: {url}")
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        page = response.text

        soup = BeautifulSoup(page, 'html.parser')

        # Получаем название фильма
        title = soup.find('h1')
        if not title:
            logger.error("Title element not found in HTML")
            raise ValueError("Не удалось найти название фильма")
        name = title.text.strip()
        logger.info(f"Found film title: {name}")

        # Получаем постер
        meta_image = soup.find('meta', property='og:image')
        if not meta_image:
            logger.error("Image meta tag not found in HTML")
            raise ValueError("Не удалось найти изображение фильма")
        img = meta_image['content']

        # Получаем описание
        meta_desc = soup.find('meta', property='og:description')
        if not meta_desc:
            logger.error("Description meta tag not found in HTML")
            raise ValueError("Не удалось найти описание фильма")
        description = meta_desc['content']

        # Получаем информацию из блока
        block_info = soup.find('div', class_='block_info')
        if not block_info:
            logger.error("Info block not found in HTML")
            raise ValueError("Не удалось найти информацию о фильме")

        # Получаем жанр, страну и год из блока информации
        info_links = block_info.find_all('a')
        genre = "Не указан"
        country = "Не указана"
        year = "Не указан"

        for link in info_links:
            href = link.get('href', '')
            if '/a-z/movies/' in href:
                if 'movies/20' in href or 'movies/19' in href:  # год
                    year = link.text.strip()
                elif any(country_name in href for country_name in ['united_states', 'russia', 'france', 'united_kingdom', 'germany']):  # страна
                    country = link.text.strip()
                else:  # жанр
                    genre = link.text.strip()

        # Получаем продолжительность
        duration_block = soup.find('div', class_='block_table')
        duration = "Не указана"
        if duration_block and 'время' in duration_block.text.lower():
            duration = duration_block.find_all('div')[1].text.strip()

        # Получаем рейтинг
        score = "0.0"
        scores_block = soup.find('div', class_='wrapper_movies_scores')
        if scores_block:
            score_divs = scores_block.find_all('div', class_='wrapper_movies_scores_score')
            if score_divs:
                for score_div in score_divs:
                    if 'IMDb' in score_div.text:
                        score = score_div.find('div').text.strip()
                        break

        data = {
            'name': name,
            'image': img,
            'genre': genre,
            'country': country,
            'year': year,
            'desc': description,
            'duration': duration,
            'score': score
        }

        logger.info(f"Successfully parsed film data for: {name}")
        return data

    except requests.Timeout:
        logger.error(f"Timeout error while fetching URL: {url}")
        raise ValueError("Превышено время ожидания ответа от сайта. Попробуйте позже.")
    
    except requests.ConnectionError:
        logger.error(f"Connection error while fetching URL: {url}")
        raise ValueError("Не удалось подключиться к сайту. Проверьте подключение к интернету.")
    
    except requests.RequestException as e:
        logger.error(f"Request error while fetching URL {url}: {str(e)}")
        raise ValueError(f"Не удалось получить данные с сайта: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error while parsing film data: {str(e)}")
        raise ValueError(f"Ошибка при обработке данных фильма: {str(e)}")
    
    finally:
        session.close()

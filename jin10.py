import requests
import json
import time
import logging
import mysql.connector
from datetime import datetime
from functools import wraps

# éç½®æ¥å¿
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jin10_crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# è¯·æ±çç®æ  URL
url = "https://flash-api.jin10.com/get_flash_list"
# ä»ç¨æ·è¾å¥ä¸­æåçè¯·æ±å¤´
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "x-app-id": "bVBF4FyRTn5NJF5n",
    "x-version": "1.0.0"
}

# æ°æ®åºéç½®
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'btc_ai'
}

# éè¯è£é¥°å¨
def retry(max_attempts=3, delay=2):
    """
    éè¯è£é¥°å¨ï¼ç¨äºå¨å½æ°å¤±è´¥æ¶è¿è¡éè¯
    
    Args:
        max_attempts: æå¤§éè¯æ¬¡æ°
        delay: éè¯é´éï¼ç§ï¼
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay  # å¨åé¨åå»ºä¸ä¸ªå±é¨åé
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logger.error(f"å½æ° {func.__name__} å¨ {max_attempts} æ¬¡å°è¯åå¤±è´¥: {e}")
                        raise
                    logger.warning(f"å½æ° {func.__name__} å¤±è´¥ï¼å°è¯ {attempts}/{max_attempts}ï¼éè¯¯: {e}ï¼{current_delay} ç§åéè¯")
                    time.sleep(current_delay)
                    current_delay *= 2  # ææ°éé¿ç­ç¥
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def get_db_connection():
    """åå»ºå¹¶è¿åæ°æ®åºè¿æ¥"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"æ°æ®åºè¿æ¥éè¯¯: {err}")
        raise

@retry(max_attempts=3, delay=2)
def get_latest_timestamp():
    """ä»æ°æ®åºè·åææ°çæ¶é´æ³"""
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT latest_time FROM latest_timestamp ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return result[0]
        return None
    except mysql.connector.Error as err:
        logger.error(f"è·åæ¶é´æ³éè¯¯: {err}")
        if conn.is_connected():
            conn.close()
        raise

@retry(max_attempts=3, delay=2)
def update_latest_timestamp(timestamp):
    """æ´æ°æ°æ®åºä¸­çææ°æ¶é´æ³"""
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO latest_timestamp (latest_time) VALUES (%s)", (timestamp,))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"æ´æ°æ¶é´æ³æå: {timestamp}")
        return True
    except mysql.connector.Error as err:
        logger.error(f"æ´æ°æ¶é´æ³éè¯¯: {err}")
        if conn.is_connected():
            conn.close()
        raise

@retry(max_attempts=3, delay=2)
def save_single_data(item, cursor):
    """ä¿å­åæ¡æ°æ®å°æ°æ®åº"""
    try:
        # æ£æ¥è®°å½æ¯å¦å·²å­å¨
        cursor.execute("SELECT 1 FROM data_sources WHERE source = 'jin10' AND url = %s", (str(item['id']),))
        if cursor.fetchone():
            logger.debug(f"è®°å½ {item['id']} å·²å­å¨ï¼è·³è¿")
            return False
        
        # åå¤æ°æ®
        data_obj = item.get('data', {})
        
        # æ å°å°æ°è¡¨å­æ®µ
        data_type = 'æ°é»'  # åºå®ä¸ºæ°é»ç±»å
        title = data_obj.get('title', '')
        content = data_obj.get('content', '')
        source = 'jin10'  # åºå®æ¥æºä¸ºjin10
        author = data_obj.get('source', '')  # å°åæ¥çsourceå­æ®µæ å°ä¸ºauthor
        
        # å¤çpublish_time
        time_str = item.get('time')
        if time_str:
            try:
                # å°è¯å°å­ç¬¦ä¸²è§£æä¸ºdatetimeå¯¹è±¡
                publish_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # å¦æè§£æå¤±è´¥ï¼ä½¿ç¨å½åæ¶é´
                publish_time = datetime.now()
        else:
            publish_time = datetime.now()
        
        fetch_time = datetime.now()
        url = str(item['id'])  # æ²¡æçå®URLï¼ç¨IDä»£æ¿
        
        # æå»ºmetadata
        metadata = {
            'pic': data_obj.get('pic', ''),
            'source_link': data_obj.get('source_link', ''),
            'important': item.get('important', 0),
            'tags': item.get('tags', []),
            'channel': item.get('channel', []),
            'remark': item.get('remark', []),
            'original_type': item.get('type', '')
        }
        
        # æå¥æ°æ®
        sql = """
        INSERT INTO data_sources 
        (data_type, title, content, source, author, publish_time, fetch_time, url, metadata, is_processed) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (data_type, title, content, source, author, publish_time, fetch_time, url, json.dumps(metadata), 0)
        
        cursor.execute(sql, values)
        logger.info(f"ä¿å­æ°æ®æå: ID={item['id']}, æ¶é´={publish_time}, åå®¹={content[:50]}...")
        return True
    except mysql.connector.Error as err:
        logger.error(f"ä¿å­åæ¡æ°æ®éè¯¯, ID={item['id']}: {err}")
        raise

def save_data_to_db(data_items):
    """å°æ°æ®ä¿å­å°æ°æ®åº"""
    if not data_items:
        logger.info("æ²¡ææ°æ®éè¦ä¿å­")
        return 0
    
    logger.info(f"å¼å§ä¿å­ {len(data_items)} æ¡æ°æ®å°æ°æ®åº")
    conn = get_db_connection()
    
    saved_count = 0
    try:
        cursor = conn.cursor()
        
        for item in data_items:
            try:
                if save_single_data(item, cursor):
                    saved_count += 1
            except Exception as e:
                logger.error(f"ä¿å­åæ¡æ°æ®æ¶åºé, ID={item['id']}: {e}")
                # ç»§ç»­å¤çä¸ä¸æ¡æ°æ®
        
        conn.commit()
        logger.info(f"æäº¤äºå¡å®æï¼æåä¿å­ {saved_count} æ¡æ°æ®")
        cursor.close()
        conn.close()
        return saved_count
    except mysql.connector.Error as err:
        logger.error(f"ä¿å­æ°æ®éè¯¯: {err}")
        if conn.is_connected():
            try:
                conn.rollback()
                logger.warning("æ°æ®åºäºå¡å·²åæ»")
            except:
                pass
            conn.close()
        return saved_count

@retry(max_attempts=3, delay=5)
def fetch_jin10_data():
    """
    åæå®ç URL åé GET è¯·æ±ï¼å¹¶éå¸¦ç»å®çè¯·æ±å¤´ï¼
    ç¶åå¤çè¿åç JSON æ°æ®å¹¶ä¿å­å°æ°æ®åºã
    """
    try:
        logger.info("å¼å§è·åéåæ°æ®")
        # åé GET è¯·æ±ï¼è®¾ç½®10ç§è¶æ¶
        params = {
            "channel": "-8200",
            "vip": "1"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        logger.info(f"è·åæ°æ®ååºç¶æç : {response.status_code}")
        
        if response.status_code == 200:
            # è§£æ JSON ååº
            json_data = response.json()
            
            if json_data.get('status') == 200:
                data_items = json_data.get('data', [])
                
                if data_items:
                    # è®°å½ææ°çæ¶é´æ³
                    latest_time = data_items[0]['time']
                    update_latest_timestamp(latest_time)
                    
                    # ä¿å­æ°æ®å°æ°æ®åº
                    saved_count = save_data_to_db(data_items)
                    logger.info(f"æ¬æ¬¡æåå®æï¼æåä¿å­ {saved_count} æ¡æ°æ°æ®")
                else:
                    logger.info("æ²¡æè·åå°æ°æ°æ®")
            else:
                error_msg = f"API è¿åéè¯¯: {json_data.get('message')}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            error_msg = f"è¯·æ±å¤±è´¥ï¼ç¶æç : {response.status_code}"
            logger.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg)

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTPéè¯¯: {http_err}")
        raise
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"è¿æ¥éè¯¯: {conn_err}")
        raise
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"è¶æ¶éè¯¯: {timeout_err}")
        raise
    except requests.exceptions.RequestException as req_err:
        logger.error(f"è¯·æ±åçéè¯¯: {req_err}")
        raise
    except json.JSONDecodeError as json_err:
        logger.error(f"æ æ³ä»ååºä¸­è§£ç JSON: {json_err}")
        logger.debug(f"ååºææ¬: {response.text[:500]}...")
        raise
    except Exception as e:
        logger.error(f"è·åæ°æ®æ¶åçæªç¥éè¯¯: {e}")
        raise

def run_periodic_fetch(interval=60):
    """
    å®æè¿è¡æ°æ®æåå½æ°
    
    Args:
        interval: æåé´éï¼åä½ä¸ºç§ï¼é»è®¤60ç§
    """
    logger.info(f"å¼å§å®ææåæ°æ®ï¼é´éæ¶é´: {interval}ç§")
    
    try:
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while True:
            try:
                logger.info(f"å¼å§ç¬¬{consecutive_errors + 1}æ¬¡æåæ°æ®...")
                fetch_jin10_data()
                # æåè·åæ°æ®ï¼éç½®éè¯¯è®¡æ°
                consecutive_errors = 0
                logger.info(f"ç­å¾ {interval} ç§åè¿è¡ä¸ä¸æ¬¡æå...")
                time.sleep(interval)
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"æåæ°æ®å¤±è´¥ ({consecutive_errors}/{max_consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical(f"è¿ç»­ {max_consecutive_errors} æ¬¡æåå¤±è´¥ï¼ç¨åºåæ­¢")
                    break
                
                # åçéè¯¯åï¼ç­å¾æ¶é´å¢å ï¼ææ°éé¿ï¼
                wait_time = interval * (2 ** (consecutive_errors - 1))
                logger.warning(f"ç­å¾ {wait_time} ç§åéè¯...")
                time.sleep(wait_time)
    except KeyboardInterrupt:
        logger.info("æåä»»å¡è¢«æå¨åæ­¢")

if __name__ == "__main__":
    try:
        logger.info("éåæ°æ®ç¬è«ç¨åºå¯å¨")
        run_periodic_fetch(60)  # é»è®¤60ç§æåä¸æ¬¡
    except Exception as e:
        logger.critical(f"ç¨åºåçä¸¥ééè¯¯: {e}")

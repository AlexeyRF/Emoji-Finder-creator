import json
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import itertools

# Configuration for multiple LM Studio instances
# Add your machine URLs here. For example: ["http://localhost:1234/v1/chat/completions", "http://192.168.1.50:1234/v1/chat/completions"]
DEFAULT_URLS = ["http://localhost:1234/v1/chat/completions"]
MAX_THREADS_PER_INSTANCE = 4

results_lock = Lock()

def get_tags_from_llm(emoji_char, name, extra_lang, api_url):
    lang_instruction = f"русском, английском и {extra_lang}" if extra_lang.lower() != "нет" else "русском и английском"
    json_structure = "{\"ru\": [...], \"en\": [...], \"extra\": [...]}" if extra_lang.lower() != "нет" else "{\"ru\": [...], \"en\": [...]}"
    
    system_prompt = (
        "Вы - ассистент, который создает облака слов (теги) для поиска эмодзи. "
        f"Для каждого предоставленного эмодзи вы должны вернуть список тегов на {lang_instruction}.\n"
        "ДЛЯ НЕЙТРАЛЬНЫХ КАРТИНОК ИСПОЛЬЗУЙТЕ НЕЙТРАЛЬНЫЕ ТЕГИ.\n"
        f"Ответ должен быть СТРОГО в формате JSON: {json_structure}"
    )
    
    user_prompt = f"Эмодзи: {emoji_char}, Название: {name}"
    
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=60)
        if response.status_code == 400:
            if "response_format" in payload:
                del payload["response_format"]
                response = requests.post(api_url, json=payload, timeout=60)
            
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        return None

def main():
    if not os.path.exists("emoji_data.json"):
        print("emoji_data.json not found. Run fetch_emojis.py first.")
        return
   
    api_urls = ["http://localhost:1234/v1/chat/completions", "http://192.168.0.101:1234/v1/chat/completions"]

    with open("emoji_data.json", "r", encoding="utf-8") as f:
        emojis = json.load(f)

    extra_lang = input("Введите дополнительный язык для тегов или 'нет': ")
    
    results = {}
    if os.path.exists("emoji_tags.json"):
        try:
            with open("emoji_tags.json", "r", encoding="utf-8") as f:
                results = json.load(f)
            print(f"Loaded {len(results)} existing tags. Resuming...")
        except:
            pass

    items = [(char, info) for char, info in emojis.items() if char not in results]
    total = len(emojis)
    processed_in_session = 0
    
    total_threads = len(api_urls) * MAX_THREADS_PER_INSTANCE
    print(f"Starting processing with {len(api_urls)} instances and {total_threads} total threads...")

    # Cycle through URLs for load balancing
    url_cycle = itertools.cycle(api_urls)

    with ThreadPoolExecutor(max_workers=total_threads) as executor:
        future_to_emoji = {
            executor.submit(get_tags_from_llm, char, info['name'], extra_lang, next(url_cycle)): char 
            for char, info in items
        }
        
        for future in as_completed(future_to_emoji):
            char = future_to_emoji[future]
            try:
                tags = future.result()
                if tags:
                    with results_lock:
                        results[char] = {
                            "name": emojis[char].get("name", ""),
                            "tags": tags
                        }
                        processed_in_session += 1
                        
                        if processed_in_session % 20 == 0:
                            with open("emoji_tags.json", "w", encoding="utf-8") as f:
                                json.dump(results, f, ensure_ascii=False, indent=4)
                            print(f"Progress: {len(results)}/{total} saved. (Last: {char})")
                else:
                    # Optional: print(f"Failed to get tags for {char}")
                    pass
            except Exception as e:
                print(f"Exception for {char}: {e}")

    with open("emoji_tags.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    print(f"Done! Total emojis with tags: {len(results)}")

if __name__ == "__main__":
    main()

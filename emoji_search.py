import json
import os

class EmojiSearcher:
    def __init__(self, tags_file="emoji_tags_refined.json"):
        self.tags_file = tags_file
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.tags_file):
            print(f"Warning: {self.tags_file} not found. Search will return no results.")
            return {}
        with open(self.tags_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def search(self, query_text):
        """
        Search for emojis matching all words in the query text.
        Words can match partially and are case-insensitive.
        """
        if not query_text:
            return []
            
        # Split query into words and lowercase them
        query_words = query_text.lower().split()
        
        matches = []
        
        for emoji_char, info in self.data.items():
            # Combine all tags into a single flat list of lowercased strings
            all_tags = []
            tags_dict = info.get("tags", {})
            for lang_tags in tags_dict.values():
                if isinstance(lang_tags, list):
                    all_tags.extend([t.lower() for t in lang_tags])
            
            # Add emoji name as well
            all_tags.append(info.get("name", "").lower())
            
            # Check if EVERY query word matches at least one tag (partially)
            all_words_match = True
            for qw in query_words:
                word_found = False
                for tag in all_tags:
                    if qw in tag:
                        word_found = True
                        break
                if not word_found:
                    all_words_match = False
                    break
            
            if all_words_match:
                matches.append(emoji_char)
                
        return matches

def main():
    searcher = EmojiSearcher()
    while True:
        query = input("\nВведите слова для поиска (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break
            
        results = searcher.search(query)
        if results:
            print(f"Найдено {len(results)} эмодзи:")
            print(" ".join(results))
        else:
            print("Ничего не найдено.")

if __name__ == "__main__":
    main()

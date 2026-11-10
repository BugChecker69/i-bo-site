import os
import json
import re
from html.parser import HTMLParser

POSTS_DIR = 'blog/posts'
OUTPUT_JSON = 'blog/posts.json'

class ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.summary = ''
        self.date = ''
        self.category = 'その他'
        self.in_title = False
        self.in_time = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'title':
            self.in_title = True
        elif tag == 'meta' and attrs_dict.get('name') == 'description':
            self.summary = attrs_dict.get('content', '')
        elif tag == 'time':
            self.in_time = True
            if 'datetime' in attrs_dict:
                self.date = attrs_dict['datetime'].replace('-', '.')

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'time':
            self.in_time = False

    def handle_data(self, data):
        if self.in_title and not self.title:
            self.title = data.split('|')[0].strip()
        elif self.in_time and not self.date:
            self.date = data.strip()

def main():
    posts = []
    if not os.path.exists(POSTS_DIR):
        return

    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith('.html') or filename == 'template.html':
            continue

        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parser = ArticleParser()
        parser.feed(content)

        cat_match = re.search(r'<span[^>]*class="[^"]*rounded[^"]*"[^>]*>([^<]+)</span>', content)
        category = cat_match.group(1).strip() if cat_match else 'お知らせ'

        posts.append({
            'id': filename.replace('.html', ''),
            'date': parser.date or '2026.01.01',
            'title': parser.title or filename,
            'category': category,
            'summary': parser.summary,
            'url': f'posts/{filename}'
        })

    posts.sort(key=lambda x: x['date'], reverse=True)

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()

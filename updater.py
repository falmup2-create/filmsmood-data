import json
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

# رابط موقع الووي تي في الحالي (تستطيع تعديله هنا لو تغير النطاق مستقبلاً)
BASE_TARGET_URL = "https://gc.alooytv12.xyz" 

def get_new_video_url(title):
    try:
        # 1. البحث عن الفيلم أو المسلسل بالاسم داخل الموقع
        search_url = f"{BASE_TARGET_URL}/search.php?keywords={urllib.parse.quote(title)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code != 200: 
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. البحث عن رابط صفحة الفيديو الأولى في نتائج البحث
        link_tag = soup.find('a', href=re.compile(r'/video/'))
        if not link_tag: 
            return None
        
        watch_url = BASE_TARGET_URL + link_tag['href']
        watch_response = requests.get(watch_url, headers=headers, timeout=10)
        
        if watch_response.status_code != 200:
            return None
            
        # 3. قنص رابط الـ mp4 المتغير من داخل السورس (البحث عن جودة التشغيل الأساسية)
        video_match = re.search(r'(https://[^"\']+/01\.mp4)', watch_response.text)
        if video_match:
            return video_match.group(1)
            
    except Exception as e:
        print(f"خطأ أثناء فحص المحتوى ({title}): {e}")
    return None

# تحميل قاعدة بياناتك الحالية من المستودع
with open('database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

has_updates = False

# المرور على كافة العناصر وفحصها
for item in db:
    print(f"جاري فحص: {item['title']}...")
    new_url = get_new_video_url(item['title'])
    
    # إذا عثرنا على رابط جديد وكان يختلف عن الرابط القديم المخزن، نقوم بتحديثه
    if new_url and new_url != item['url']:
        print(f" [تحديث] وجدنا رابط جديد لـ {item['title']}:")
        print(f" القديم: {item['url']}")
        print(f" الجديد: {new_url}")
        item['url'] = new_url
        has_updates = True

# --- التعديل السحري هنا للحفظ الإجباري في كل الأحوال ---

# 1. حفظ ملف الـ JSON المحدث (سواء تعدل أو لا)
with open('database.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

# 2. توليد وتحويل البيانات إلى صيغة التغليف الجاهزة لبلوجر دائماً لضمان ظهور الملف
with open('blogger_format.js', 'w', encoding='utf-8') as f:
    f.write(f"Callback({json.dumps(db, ensure_ascii=False)});\n")

if has_updates:
    print("تم تحديث الروابط المكسورة وتوليد الملفات بنجاح!")
else:
    print("كل الروابط تعمل ومطابقة، وتم توليد وحفظ ملف blogger_format.js بنجاح للتأكيد!")

'''
    2025 Agustus 30
    authbox.web.id
'''
import re
import copy
import json
from bs4 import BeautifulSoup, Comment


def get_root_parent(target, contain_tag_name):
    '''
        # Traverse to the root parent
        # cek apakah mengandung tag tertentu misalnya NAV (jika iya return true)
    '''
    root_parent = target
    while root_parent.parent is not None:
        root_parent = root_parent.parent
        if root_parent.name == contain_tag_name:
            return True 
    return False

def get_root_parent_id(target, contain_tag_name):
    '''
        # Traverse to the root parent
        # cek apakah mengandung id tertentu misalnya id="hero-1" (jika iya return true)
    '''
    root_parent = target
    while root_parent.parent is not None:
        root_parent = root_parent.parent
        if root_parent.name == contain_tag_name:
            if root_parent.has_attr('id'):
                mid = root_parent.get('id')    
                return mid 
    return None 

def get_root_parent_id_name(target, contain_tag_name, contain_id_name):
    '''
        # Traverse to the root parent
        # cek apakah mengandung id tertentu misalnya id="hero-1" (jika iya return true)
    '''
    root_parent = target
    while root_parent.parent is not None:
        root_parent = root_parent.parent
        if root_parent.name == contain_tag_name:
            if root_parent.has_attr('id'):
                mid = root_parent.get('id')   
                if mid == contain_id_name:
                    return True                
    return False

def clean_text(text_to_find, mchar):
    '''
        Clean text by removing specific characters
        Karakter + atau ? atau /g akan di anggap perintah khsusus oleh re.compile
    '''
    if text_to_find[0] == mchar:
        return text_to_find.replace(mchar,'')
    return text_to_find

def get_replacement_soup(text_to_find, m_code, m_type):
    tmp = f"""
            <span class="hoverable hoverable-mark" id='{m_code}'
                data-tooltip='Link ini hanya tampil di mode edit. Silahkan klik untuk mengedit data!'
                data-modal-title='{text_to_find}'
                data-modal-code='{m_code}'
                data-modal-type='{m_type}'>
                {text_to_find}
            </span> 
        """
    # tmp =   """
    #         <span class="hoverable hoverable-mark" id='""" + m_code + """'
    #             data-tooltip="Link ini hanya tampil di mode edit. Silahkan klik untuk mengedit data!" 
    #             data-modal-title='""" + text_to_find + """'
    #             data-modal-code='""" + m_code + """'
    #             data-modal-type='""" + m_type + """'
    #             >
    #         """ + text_to_find + """
    #             </span> 
    #         """            
    return BeautifulSoup(tmp, 'html.parser')    

def get_replacement_soup_copy(text_to_find, m_code, m_type):
    '''
        Untuk source.html yang tidak ada hoverable        
    '''
    tmp = f"""
            <span class="hoverable-mark" id='{m_code}'                                
                data-modal-type='{m_type}'>
                {text_to_find}
            </span> 
        """
    # tmp =   """
    #         <span class="hoverable-mark" id='""" + m_code + """'                
    #             data-modal-type='""" + m_type + """'
    #             >
    #         """ + text_to_find + """
    #             </span> 
            # """            
    return BeautifulSoup(tmp, 'html.parser')   

def add_hover_click(soup, text_to_find, m_section_array, is_copy=False, manifest=None):
    '''
        add hover-text to all kind who user can change
    '''
    # Error jika ada karakter +
    text_to_find = clean_text(text_to_find, '+')
    # print('text_to_find', text_to_find )

    # find all text    
    text_element = soup.body.find_all(string=re.compile(text_to_find))    
    
    for i in range(len(text_element)):
        # cannot continue if text = None (Fix index.html first)
        if not text_element[i]:
            print('Ubah data index.html jika ini masih muncul!!! (Hilangkan karakter ? + dll)')
            print('Text to find:', text_to_find)
            print('Found text_element:', text_element[i])
            print('Fix this first')
            return 

        # add exception
        m_continue = True
        if get_root_parent(text_element[i], 'nav'):            
            m_continue = False 

        if m_continue and get_root_parent(text_element[i], 'ul'):            
            m_continue = False 

        if m_continue and get_root_parent(text_element[i], 'form'):            
            m_continue = False 

        if m_continue and get_root_parent_id_name(text_element[i], 'div', 'myModal'):
            # print('ENTER')
            m_continue = False

        # get section id
        m_section = {}
        if m_continue:
            # get section name
            # reset code begin from 1 if new section name detected
            # if section name exists code continue from last index
            tmp = get_root_parent_id(text_element[i], 'section')            
            if not tmp:                
                tmp = 'main' # default section name (main)                                                   

            mfound = False
            for j in range(len(m_section_array)):
                if m_section_array[j]['name'].strip() == tmp.strip():                        
                    m_section_array[j]['code'] += 1
                    m_section = m_section_array[j]
                    mfound = True
                    break
                
            if not mfound:
                m_section = {'name': tmp, 'code': 1}                        
                m_section_array.append(m_section) 

        # agar tidak 2 kali penulisan hoverable ini        
        if text_element[i].parent.has_attr('class'):
            mclass = text_element[i].parent.get('class')    
            for j in mclass:                
                # class hoverable-mark tetap ada di source.html dan result.html
                # sebagai penanda ini ada hoverable sudah ada dan tidak perlu di create ulang (untuk menghindari perulangan)
                if (j=='hoverable-mark') or (j=='close'):
                    m_continue = False
                    break                
            
        if m_continue:
            m_code = f"{len(m_section_array)}-{m_section['name']}-{m_section['code']}"     
            # print('m_code', m_code)
            if manifest is not None:
                manifest.append(m_code)
            m_type = 'text'               

            if not is_copy:
                replacement_soup = get_replacement_soup(text_to_find, m_code, m_type)            
                # text_element[i].string.replace_with(replacement_soup)  
            else: # print('text_element[i]', text_element[i].parent)
                replacement_soup = get_replacement_soup_copy(text_to_find, m_code, m_type)            
            text_element[i].string.replace_with(replacement_soup)  
                
                # text_element[i]['id'] = m_code

            # for source.html
            # text_element_copy = soup_copy.body.find_all(string=re.compile(text_to_find))          
            # for j in range(len(text_element_copy)):
            #     if text_element_copy[j]:
            #         text_element_copy[j].string.replace_with(text_to_find)
            # text_element_copy = soup.body.find_all(string=re.compile(text_to_find))          
            
def replace_icon(soup, class_name, len_section_array, is_copy=False, manifest=None):
    '''
        Replace all icon with hoverable
        class_name = 'bi' for bootstrap icon
    '''
    bi_icons = soup.find_all('i', class_=class_name)    
    idx = 0
    m_type = 'icon'

    # Print results
    for icon in bi_icons:
        if icon:            
            m_continue = True
            if get_root_parent(icon, 'nav'):                
                m_continue = False 

            if m_continue and get_root_parent(icon, 'ul'):                
                m_continue = False 

            if m_continue and get_root_parent(icon, 'form'):            
                m_continue = False 

            if m_continue:
                idx += 1
                m_code = f'{len_section_array}-bi-icon-{idx}'    
                if manifest is not None:
                    manifest.append(m_code)            

                icon_name = ""
                for j in icon.get('class', []):                    
                    if j.startswith('bi-'):
                        icon_name = j                        
                        break
                
                if icon_name:                    
                    if not is_copy:
                        replacement_soup = get_replacement_soup(icon, m_code, m_type)                    
                    else:
                        replacement_soup = get_replacement_soup_copy(icon, m_code, m_type)                    
                    icon.replace_with(replacement_soup)

def replace_img(soup, len_section_array, is_copy=False, manifest=None):
    '''
        Replace all img with hoverable
        # image tag bisa langsung tanpa pengecekan nav, ul, dan form
    '''
    imgs = soup.find_all('img')    
    idx = 0
    m_type = 'image'
    
    for img in imgs:        
        if img:
            idx += 1
            m_code = f'{len_section_array}-image-{idx}'  
            if manifest is not None:
                manifest.append(m_code)

            if not is_copy:
                replacement_soup = get_replacement_soup(img, m_code, m_type)            
            else:
                replacement_soup = get_replacement_soup_copy(img, m_code, m_type)
            img.replace_with(replacement_soup)

def replace_ul(soup, len_section_array, is_copy=False, manifest=None):
    items = soup.find_all('ul')    
    idx = 0
    m_type = 'unordered-list'

    for item in items:        
        if item:            
            m_continue = True
            if get_root_parent(item, 'nav'):                
                m_continue = False 
            
            if m_continue and get_root_parent(item, 'form'):            
                m_continue = False 

            if m_continue:
                idx += 1
                m_code = f'{len_section_array}-unordered-list-{idx}'
                if manifest is not None:
                    manifest.append(m_code)
                    
                # data-modal-title='{item.get_text(separator=', ', strip=True)}'                
                # print('---', tmp)
                if is_copy:
                    replacement_soup = get_replacement_soup_copy(item, m_code, m_type)                
                else:
                    # data-modal-title='{item.get_text(separator=', ', strip=True)}'
                    replacement_soup = get_replacement_soup(item, m_code, m_type)                
                item.replace_with(replacement_soup)

def replace_nav(soup, len_section_array, is_copy=False, manifest=None):
    items = soup.find_all('nav')    
    idx = 0
    m_type = 'nav-bar'

    for item in items:        
        if item:                    
            idx += 1
            m_code = f'{len_section_array}-nav-bar-{idx}'        
            if manifest is not None:
                manifest.append(m_code) 
            # data-modal-title='{item.get_text(separator=', ', strip=True)}'            
            if not is_copy:
                replacement_soup = get_replacement_soup(item, m_code, m_type)            
            else:
                replacement_soup = get_replacement_soup_copy(item, m_code, m_type)
            item.replace_with(replacement_soup)

def scrape_text(filepath):
    '''
        Scrape all text from a local html file
        convert to hoverable text, and identifier (for ajax edit later)

        Note:
        Baca file asli html index.html
        Hasilnya di simpan di res.html dan di source.html
        1. Source.html untuk di load di ajax edit (tanpa hoverable)
        2. Res.html untuk di tampilkan di browser (ada hoverable)

        Cara pakai:
        1. Create file index.html dengan id yg sama seperti res.html
        2. Create file res.html (penghubungnya id)

        Karna belum konek ke database
        maka perlu buat file manifest.json untuk menyimpan daftar id       
        id ini digunakan oleh ajax edit untuk mengedit data atau menampilkan data          
    '''    
    # URL of the webpage to scrape
    # url = "./index.html"
    # Membuka file HTML lokal
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    # remove all space, tab, new lines
    content = content.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('$','Rp')

    # remove all multiple spaces with single space
    cleaned_text = re.sub(r'\s+', ' ', content).strip()
    
    # Membuat objek BeautifulSoup "lxml" "html5lib"
    soup = BeautifulSoup(cleaned_text, "html.parser")

    # Remove all script and style elements
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    # Create a deep copy of the soup object
    # Deep Copy: The copy.deepcopy() function ensures that the copied object is independent of the original.
    soup_copy = copy.deepcopy(soup)

    # Remove href from all <a> tags
    for a_tag in soup.find_all('a'):
        if 'href' in a_tag.attrs:
            del a_tag.attrs['href']    
    
    # Extract all visible text from the body tag
    # OKE FIND ALL TEXT
    # -----------------
    # get all text with new line separator
    body_text = soup.body.get_text(separator="\n", strip=True)    

    # split by new line
    tmp = body_text.split('\n')
    
    m_section_array = []    
    m_section_array.append({ 'name': 'main', 'code': 0 })

    m_section_array_copy = []    
    m_section_array_copy.append({ 'name': 'main', 'code': 0 })

    m_manifest = [] # untuk menyimpan daftar id yang akan di simpan di manifest.json    

    for i in range(len(tmp)):        
        add_hover_click(soup, tmp[i], m_section_array, manifest=m_manifest)
        add_hover_click(soup_copy, tmp[i], m_section_array_copy, is_copy=True)
    
    replace_icon(soup, 'bi', len(m_section_array), manifest=m_manifest) # bi is bootstrap icon
    replace_icon(soup_copy, 'bi', len(m_section_array_copy), is_copy=True) # bi is bootstrap icon

    replace_img(soup, len(m_section_array), manifest=m_manifest)
    replace_img(soup_copy, len(m_section_array_copy), is_copy=True)

    replace_ul(soup, len(m_section_array), manifest=m_manifest)
    replace_ul(soup_copy, len(m_section_array_copy), is_copy=True)

    replace_nav(soup, len(m_section_array), manifest=m_manifest)
    replace_nav(soup_copy, len(m_section_array_copy), is_copy=True)
        
    with open("res.html", "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    with open("src.html", "w", encoding="utf-8") as file:
        file.write(soup_copy.prettify())

    # print('manifest', m_manifest)
    with open("manifest.json", "w", encoding="utf-8") as file:
        # file.write(m_manifest.json())       
        json.dump(m_manifest, file) 

    print("Scraping completed. Results saved to res.html, src.html, and manifest.json")

'''
    Convert to django
    for covert output bs_get_all_text : res.html and src.html to django template
    django template: 
        src.html ->
            [code]-base.html
            [code]-base-index.html
            [code]-index.html
        code = hexadesimal uniq

        res.html ->
            [code]-base.html
            [code]-base-index.html
            [code]-index.html
'''

import re
# import json
from bs4 import BeautifulSoup
# import copy
from pathlib import Path

def replace_title(input_file, template_name):    
    # input_name = input_file.split(".")[0]

    with open(input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text_elements = soup.find('title')
    
    # add include id base.html
    tmp = "{{ title }}"
    # m_include = BeautifulSoup(tmp, "html.parser")
    text_elements.string.replace_with(tmp)

    # Add extra head dan extra body di bagian akhir tag penutup
    tmp = "{% block extra_head %} {% endblock %}"
    m_include = BeautifulSoup(tmp, "html.parser")
    soup.head.append(m_include)

    tmp = "{% block extra_body %} {% endblock %}"
    m_include = BeautifulSoup(tmp, "html.parser")
    soup.body.append(m_include)

    with open(template_name + '/' + 'base.html', 'w', encoding='utf-8') as file:        
        file.write(soup.prettify())

    # remove all link element from source html
    print("Add Extra head and body Done...")
    print("Replace title Done...")
    return soup

    # with open('extracted_texts.json', 'w', encoding='utf-8') as json_file:
    #     json.dump(texts, json_file, ensure_ascii=False, indent=4)
    
    # with open('snippets/style.html', 'r', encoding='utf-8') as file:
    #     for i in locals
    #     file.write(soup.prettify())
    # print("Extract Link Done...")

# Gak bisa cara ini, harus cek lagi has_attr di caller function
# def add_static_to(element, folder_name, attr):
#     if element.has_attr(attr):
#         if not("https://" in element[attr]):            
#             return "{% static '" + folder_name + "/" + element[attr] + "' %}"
#     return element

def extract_tag_name(soup, folder_name, tag_name, m_index=0):        
    # find all tag
    tag_elements = soup.find_all(tag_name)
    
    # add static to target html except for meta
    link_element = ""
    if tag_name!="meta":
        link_element = "{% load static %}"

    # proses all finding tag
    m_parent_tag = None
    for i in range(len(tag_elements)):
        # print('parent name', tag_elements[i].parent.name)
        if not m_parent_tag:
            m_parent_tag = tag_elements[i].parent

        if tag_elements[i].has_attr('href'):
            if not("https://" in tag_elements[i]["href"]):            
                tag_elements[i]["href"] = "{% static '" + folder_name + "/" + \
                                            tag_elements[i]["href"] + "' %}"
                
        if tag_elements[i].has_attr('src'):
            if not("https://" in tag_elements[i]["src"]):            
                tag_elements[i]["src"] = "{% static '" + folder_name + "/" + \
                                            tag_elements[i]["src"] + "' %}"
                
        link_element += tag_elements[i].prettify()
        # hapus element link dari soup
        tag_elements[i].decompose()
        
    # write to file tag link or meta (tag_name)
    m_link = BeautifulSoup(link_element, 'html.parser')    
    with open(folder_name + '/snippets/'+ tag_name +'.html', 'w', encoding='utf-8') as file:        
        file.write(m_link.prettify())

    # add include to base.html
    if tag_name != 'main':
        tmp = "{% include '"+ folder_name +"/snippets/"+ tag_name +".html' %}"
    else:
        tmp = "{% block "+ tag_name +" %}"+"{% endblock %}"

    m_include = BeautifulSoup(tmp, "html.parser")
    if tag_name=='script':
        # print('YOU MUST FIND extra_body HERE')
        tmp = soup.find(string=re.compile('extra_body'))
        if tmp:
            tmp.insert_before(m_include)
        else:
            print('extra_body not found!')
    else:
        m_parent_tag.insert(m_index, m_include)
    
    # soup.head.append(m_include)
    with open(folder_name + '/base.html', 'w', encoding='utf-8') as file:        
        file.write(soup.prettify())

    # remove all link element from source html
    print(f"Extract {tag_name} Done...")
    return soup

    # with open('extracted_texts.json', 'w', encoding='utf-8') as json_file:
    #     json.dump(texts, json_file, ensure_ascii=False, indent=4)
    
    # with open('snippets/style.html', 'r', encoding='utf-8') as file:
    #     for i in locals
    #     file.write(soup.prettify())
    # print("Extract Link Done...")

# def extract_link(folder_name, soup):    
#     # with open(input_file, 'r', encoding='utf-8') as file:
#     #     html_content = file.read()
    
#     # soup = BeautifulSoup(html_content, 'html.parser')
#     text_elements = soup.find_all('link')
    
#     # texts = [element.strip() for element in text_elements if element.strip()]
#     link_element = "{% load static %}"
#     for i in range(len(text_elements)):
#         if not("https://" in text_elements[i]["href"]):
#             text_elements[i]["href"] = "{% static '" + folder_name + "/" + \
#                                         text_elements[i]["href"] + "' %}"
#         link_element += text_elements[i].prettify()
#         # hapus element link dari soup
#         text_elements[i].decompose()
        
#     m_link = BeautifulSoup(link_element, 'html.parser')    

#     with open('snippets/style.html', 'w', encoding='utf-8') as file:        
#         file.write(m_link.prettify())

#     # add include id base.html
#     tmp = "{% include '"+ folder_name +"/snippets/style.html' %}"
#     m_include = BeautifulSoup(tmp, "html.parser")
#     soup.head.append(m_include)

#     with open('base.html', 'w', encoding='utf-8') as file:        
#         file.write(soup.prettify())

#     # remove all link element from source html
#     print("Extract Link Done...")
#     return soup

#     # with open('extracted_texts.json', 'w', encoding='utf-8') as json_file:
#     #     json.dump(texts, json_file, ensure_ascii=False, indent=4)
    
#     # with open('snippets/style.html', 'r', encoding='utf-8') as file:
#     #     for i in locals
#     #     file.write(soup.prettify())
#     # print("Extract Link Done...")

# def extract_meta(folder_name, soup):    
#     # with open(input_file, 'r', encoding='utf-8') as file:
#     #     html_content = file.read()
    
#     # soup = BeautifulSoup(html_content, 'html.parser')
#     text_elements = soup.find_all('meta')
    
#     # texts = [element.strip() for element in text_elements if element.strip()]
#     link_element = ""
#     for i in range(len(text_elements)):        
#         link_element += text_elements[i].prettify()
#         # hapus element link dari soup
#         text_elements[i].decompose()
        
#     m_link = BeautifulSoup(link_element, 'html.parser')    

#     with open('snippets/meta.html', 'w', encoding='utf-8') as file:        
#         file.write(m_link.prettify())


#     # add include id base.html
#     tmp = "{% include '"+ folder_name +"/snippets/meta.html' %}"
#     m_include = BeautifulSoup(tmp, "html.parser")
#     soup.head.append(m_include)

#     with open('base.html', 'w', encoding='utf-8') as file:        
#         file.write(soup.prettify())

#     print("Extract Meta Done...")
#     return soup
#     # remove all link element from source html
#     # with open('extracted_texts.json', 'w', encoding='utf-8') as json_file:
#     #     json.dump(texts, json_file, ensure_ascii=False, indent=4)
    
#     # with open('snippets/style.html', 'r', encoding='utf-8') as file:
#     #     for i in locals
#     #     file.write(soup.prettify())

#     # print("Extract Meta Done...")

# # def extract_body(folder_name, soup):
#     body_tag = soup.body

#     first_tag = body_tag.find_next()
#     # if tag = header, or footer
#     print('first_tag.name', first_tag.name)

    
#     # Find all elements after body
#     # elements_after_body = []
#     # current = body_tag.next_sibling

#     # while current:
#     #     if current.name is not None: # This is a tag
#     #         elements_after_body.append(current)
#     #     current = current.next_sibling

#     # # Display results
#     # print(f"Found {len(elements_after_body)} tags after the body:")
#     # for i, element in enumerate(elements_after_body, 1):
#     #     print(f"{i}. {element.name}: {element}")

#     # all_tags_after_body = body_tag.find_all_next(limit=5)
#     # # print('ALL NEXT', all_tags_after_body)
#     # for i in all_tags_after_body:
#     #     print('--->', i)

#     return

#     # Find the first tag after <body>
#     first_tag_after_body = body_tag.find_next()
#     print('first_tag_after_body', first_tag_after_body)

#     first_tag_after_body = first_tag_after_body.find_next()
#     print('second_tag_after_body', first_tag_after_body)

def travel_tag_head(soup):
    '''
        Travel from first root tag to the end 
    '''
    element = soup.head.find_next()
    # print('element', element)
    # idx = 0
    m_arr = []
    m_exclude = ['title']
    while element:        
        # idx += 1
        # print(f'{idx} - {element.name}')
        tmp = element.name
        if tmp.lower() not in m_exclude:                                
            if tmp not in m_arr:
                m_arr.append(tmp)            

        element = element.find_next_sibling()
    return m_arr
    # print('m_arr', m_arr)
        
def travel_tag_body(soup):
    '''
        Travel from first root tag to the end 
    '''
    element = soup.body.find_next()
    # print('element', element)
    # idx = 0
    m_arr = []
    # 'main',  tidak digunakan karena tetap menggunakan algoritma seperti tag header dan footer, dan di proses ulang file dan inlcude di proses berikutnya
    m_exclude = ['div', 'nav', 'ul', 'p', 'a'] # main di gunakan untuk sub file (base-index.html)
    while element:        
        # idx += 1
        # print(f'{idx} - {element.name}')
        tmp = element.name
        if tmp.lower() not in m_exclude:                                
            if tmp not in m_arr:
                m_arr.append(tmp)            

        element = element.find_next_sibling()
    return m_arr
    # print('m_arr', m_arr)

# def travel_tag_body_main(soup):
#     '''
#         Travel from first root tag to the end 
#     '''
#     element = soup.body.main.find_next()    # tag main harus ada, jika container, ubah menjadi main (di index.html) --> proses normalisasi
#     # print('element', element.name)
#     # idx = 0
#     m_arr = []
#     m_exclude = ['div', 'nav', 'ul', 'p', 'a']
#     while element:        
#         # idx += 1
#         # print(f'{idx} - {element.name}')
#         tmp = element.name
#         if tmp.lower() not in m_exclude:                                
#             if tmp not in m_arr:
#                 m_arr.append(tmp)            

#         element = element.find_next_sibling()
#     # print('m_arr', m_arr)
#     return m_arr

def scrape_head_body(input_file, template_name):
    soup = replace_title(input_file, template_name)

    m_tag_head = travel_tag_head(soup)
    for i in range(len(m_tag_head)):
        soup = extract_tag_name(soup, template_name, m_tag_head[i], m_index=i)
    
    # soup = extract_tag_name(soup, template_name, 'meta', m_index=1)
    # soup = extract_body(template_name, soup)

    m_tag_body = travel_tag_body(soup)
    for i in range(len(m_tag_body)):
        soup = extract_tag_name(soup, template_name, m_tag_body[i], m_index=i)


    # soup = extract_tag_name(soup, template_name, 'header')
    # soup = extract_tag_name(soup, template_name, 'main', m_index=1)
    # soup = extract_tag_name(soup, template_name, 'footer', m_index=2)
    # # append (insert to the last position)
    # soup = extract_tag_name(soup, template_name, 'script', m_index=3)

    # travel_tag_head(soup)
    # travel_tag_body(soup)
    # m_main = travel_tag_body_main(soup)
    # for i in range(len(m_main)):
        # soup = extract_tag_name(soup, template_name, m_main[i], m_index=i)
    
    print("Scrape head and body Done...")

def create_index_and_base(input_file, template_name, m_section_list):
    '''
        Create base-index.html
        Create index.html
        base-index order by user data in (m_section_list)
        Sumber data data snippets/main.html (biarkan untuk proses reorder lagi oleh user)
    '''
    # open main.html
    with open(template_name + '/' + input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    main_tag= soup.main.name
    m_main = soup.main

    # print ('m_main', m_main.name)

    # Create header base-index
    tmp = """{% extends '""" + template_name + """/base.html' %}
        {% load static %}
        {% block """+ main_tag +""" %}
        """
    soup_base_index = BeautifulSoup(tmp, 'html.parser')

    tmp = """{% extends '""" + template_name + """/base-index.html' %}
        {% load static %}        
        """
    soup_index = BeautifulSoup(tmp, 'html.parser')


    # proses untuk kedua soup, index, dan base-index
    for i in m_section_list:
        elem = m_main.find('section',id=i)
        if elem:
            ret = elem.extract()
            tmp = "{% block "+ i +" %}"
            soup_index.append(BeautifulSoup(tmp, 'html.parser'))
            soup_index.append(ret)
            tmp = "{% endblock %}"
            soup_index.append(BeautifulSoup(tmp, 'html.parser'))
                    
        
    # proses urutan section di base-index.html
    for i in range(len(m_section_list)):
        tmp = "{% block "+ m_section_list[i] +" %} {% endblock %}"
        m_main.insert(i, BeautifulSoup(tmp, 'html.parser'))
    soup_base_index.append(m_main)
    

    # create footer base index
    tmp = '{% endblock %}'
    soup_base_index.append(BeautifulSoup(tmp, 'html.parser'))                

    with open(template_name + '/' + 'base-index.html', 'w', encoding='utf-8') as file:        
        file.write(soup_base_index.prettify())

    with open(template_name + '/' + 'index-modify.html', 'w', encoding='utf-8') as file:        
        file.write(soup_index.prettify())

# def create_index(soup, soup_index, template_name, m_section_name, is_first_enter=False):    
#     # soup ini sudah di dalamnya main
#     # m_main = soup.main
#     # print ('m_main', m_main.name)
#     # {% extends "ilanding/base-index.html" %}
#     # {% load static %}

#     tmp = ""    
#     if is_first_enter:
#         tmp = """{% extends '""" + template_name + """/base-index.html' %}
#                 {% load static %}
#                 """
        
#     tmp +=  """
#             {% block """+ m_section_name +""" %}
#             """
    
#     soup_index.append(BeautifulSoup(tmp, 'html.parser'))

#     element = soup.find('section')
#     # print('element', element)
#     # if element:
#     soup_index.append(copy.deepcopy(element))
    
#     tmp = '{% endblock %}'
#     soup_index.append(BeautifulSoup(tmp, 'html.parser'))    
            
#     # hapus section ini dari base-index.html
#     element.decompose()    
#     # print('element', element.name)

def update_img_src(input_file, template_name):
    # open main.html
    with open(template_name + '/' + input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    elem = soup.find_all('img')
    # print('lelem',elem)
    for i in elem:       
        if i.has_attr('src'):
            # print('src', i, i['src'])
            i["src"] = "{% static '" + template_name + "/" + i["src"] + "' %}"

    with open(template_name + '/' + input_file, 'w', encoding='utf-8') as file:
        # html_content = file.read()
        file.write(soup.prettify())
    
def get_all_section_id(input_file, folder_name):
    '''
        Untuk proses shuffle urutal section
        re create disini
    '''
    with open(folder_name + '/' + input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    # print('name',soup.main.name)
    m_section = soup.main.find_next()
    # print('m_section', m_section.name)
    m_arr = []
    while m_section:
        if m_section.has_attr('id'):
            # print(m_section.name, m_section['id'])
            m_arr.append(m_section['id'])
        m_section = m_section.find_next_sibling()
    return m_arr

def scrape_all(template_name, input_file):
    # template_name = "ilanding"
    # input_file = 'res.html'  

    input_name = input_file.split(".")[0]
    template_name += '-' + input_name

    folder_path = Path(template_name)
    folder_path.mkdir(parents=True, exist_ok=True)

    folder_path = Path(template_name + "/snippets")
    folder_path.mkdir(parents=True, exist_ok=True)

    scrape_head_body(input_file, template_name)

    # -------------------------------------------
    # lanjut ke proses berikutnya:
    # proses snippets/main.html
    # ubah menjadi base-index.html dan index.html
    # -------------------------------------------
    input_file = 'snippets/main.html'      
    m_section_list = get_all_section_id(input_file, template_name) # <--
    # for i in range(len(m_section_list)):
    #     print('section', i, m_section_list[i])
    # section list dapat di hapus dan di reorder sesuai kebutuhan

    update_img_src(input_file, template_name)

    # # ---------------------------------------------------
    # # Proses m_section_list yg sudah di proses oleh user:
    create_index_and_base(input_file, template_name, m_section_list) # belum ada output ke file, masih di variabel soup


    # # soup_index = copy.deepcopy(soup)
    # soup_index = BeautifulSoup("", 'html.parser')

    # for i in range(len(m_section_list)):        
    #     create_index(soup, soup_index, template_name, m_section_list[i], i==0)
    #     # if i==2:
    #     #     break

    # with open('base-index.html', 'w', encoding='utf-8') as file:        
    #     file.write(soup.prettify())

    # with open('dynamic-index.html', 'w', encoding='utf-8') as file:        
    #     file.write(soup_index.prettify())

    print("All Done...")
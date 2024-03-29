'''
Created on 7 июня 2019 г.

@author: macko_sa
'''

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import logging
import queue
import threading 


start_time = datetime.now()
s = requests.Session() 
#Login=os.getenv('Login')
#passw=os.getenv('password')
Login = input('Login: ')
passw=input("password: ")
s.max_redirects = 29

k1=datetime.time(start_time).strftime('%H.%M')
k=datetime.date(start_time)
logging.basicConfig(filename="log_Podruzka_info({} {}).txt".format(k,k1), level=logging.INFO)# логирование

url = 'https://www.podrygka.ru' #Сайт
proxies = {'http': r''.format(Login,passw),
           'https': r''.format(Login,passw)
           } 

user_agents = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0' # можно узнать в браузере
dfS = pd.DataFrame(columns=['city_id', 'city_name', 'whs_id','whs_adress']) #датафрейм для магазинов
dfArt = pd.DataFrame(columns=['art_name','arts_ssilk'])# Датафрейм для позиция\ссылка 
dfg=pd.DataFrame(columns=['gr0_name', 'gr0_ssilk'])# Датафрейм для конечная ТГ\ссылка
dfart_info=pd.DataFrame(columns=['art_id','art_name','grp20_name','grp21_name','grp22_name','vendor','line','country_KA','price','price_sale'])# Датафрейм для инфы по ТП
city_list_1 = pd.DataFrame(columns=['city_id', 'city_name'])# Датафрейм для городов
part=1
num_worker_threads = 1 # количество потоков при парсинге страниц
num_worker_threads1 = 1 # количество общих потоков 
q = queue.Queue() #Переменная очереди
threads = []  # Треды
kref=0



def Logging(mess,text):
    '''
    logging module;
    variables:
    mess - message sent from the module
    text - error or action for the logger
    '''
    global kref
    end_time = datetime.now()
    logging.info('time: {} \n\tdebug:{} '.format(end_time,mess))
    if text != 'text':
        k1=datetime.time(end_time).strftime('%H.%M')
        k=datetime.date(end_time)
        f = open(r'E:\SVN\Skraping\LOG_podruzka\text_error{}({} {}) .txt'.format(kref,k,k1), 'wb')
        f.write(text.encode("utf-8"))
        kref=kref+1
        
        

mess='start_PO'
Logging(mess,'text')

try:
    class Scraping():
        '''
        The scraping class is responsible for full data scraping within several threads, 
        the class uses variables: 
        1) html_itog - variable responsible for where the calculation is redirected. 
        2) city_id - city code on the site. 
        3) city_name - the Name of the city on the site 
        4) glob_t-part of the URL to build the correct URL of the page 
        5) glob_ - dummy variables to facilitate navigation through the pages on the site
        '''
        def __init__(self,html_itog,city_id,city_name,glob_t,glob_):
            self.city_list_ = []
            self.art_grp_list=[]
            self.arts_reference=[]
            self.stores_list_all=[]
            self.iskl=[]
            self.queu = queue.Queue()
            self.threads = []
            self.tg20_url=''
        
        def get_text(self,page,proxies,headers):
            r=s.get(
                  page,
                  verify=False,
                  proxies=proxies,
                  headers=headers)
            return r
            
        #модуль получения html   
        def get_html(self,html_itog,city_id,city_name,glob_t,glob_):
            '''    
            Module for obtaining HTML pages from sites according to the specified parameters
            ''' 
            name_=html_itog
            cookie='rrpvid=71646954272168; _gcl_au=1.1.177305826.1559886754; rcuid=5cf9fb851d99b800014fba28; _ga=GA1.2.235368668.1559886762; uxs_uid=7711b470-88e8-11e9-a64e-17f6f54232ed; r7k12_ci=255457358929446.1559886754000; banner_top=0; BITRIX_SM_SALE_UID=205530329; flocktory-uuid=d9a90139-3c42-4ad8-a2fd-98f46ac4b934-6; rrlevt=1560155285908; PHPSESSID=38efe2069a0967fc92c8557ca87d97bd; _gid=GA1.2.78053390.1560839902; r7k12_si=1805129415; r7k12_source=Google SEO; tmr_detect=0%7C1560839915863; _dc_gtm_UA-46690290-1=1; _gat_UA-46690290-1=1'
            headers  = ({
                    'Host': 'www.podrygka.ru',
                    'User-Agent': user_agents
                    ,'Cookie':cookie})
            if  name_ =='catalog' :
                page=url 
            elif name_ =='arts' :
                
                page=url+glob_t
                #input(page)
            elif name_ =='pages' :
                page=url+glob_t
            elif name_ =='arts_info' :
                art_url =glob_t
                page=url+art_url
            else:
                page=url+html_itog+'//'
            text=self.get_text(page,proxies,headers).text
            if  name_ =='arts': 
                self.get_arts(text,city_id,city_name,glob_t,page)
            elif  name_ =='pages': 
                self.get_pages(text,city_id,city_name,glob_t,page)
            elif name_ =='catalog':
                self.get_art_grp(text,city_name)
            elif name_ =='arts_info' :
                self.get_arts_info (text,city_name,page)
    
        
        def get_art_grp (self,text,city_name):
            ttt=[]
            global dfg#
            soup = BeautifulSoup(text.encode("utf-8"))
            dfg1=pd.DataFrame(columns=['gr0_name', 'gr0_ssilk'])
            k=soup.find('ul', {'class': 'top-menu'}).find_all('li', {'class': 'top-menu__item'})[1].find_all("div",{'class':'child-menu-group'})#
            for i in k:
                tg_lists_=i.find_all('div', {'class': 'child-menu'})
                for tg_list_ in tg_lists_:
                    ik = tg_list_.find_all('li')
                    if len(ik)<2:
                        ttt.append(tg_list_.find('a'))
                    for k in ik:
                        ttt.append(k.find('a'))
                        #input(k.find('a'))
            i=0
            #
            for items in  ttt :
                try:
                    #
                    TG=items.text.strip()
                    TG_ssilk=items.get('href')
                except :
                    True
                self.art_grp_list.append({TG:{TG_ssilk}})
                dfg1.loc[i] = [TG,TG_ssilk]
                i=i+1
            dfg = dfg.append(dfg1)



        def get_pages(self,text,city_id,city_name,grp_id,page):
            tg20_url1= self.tg20_url 
            soup = BeautifulSoup(text.encode("utf-8"))
            try:
                list_div= soup.find('div', {'class':'pagination__pages'}).find('div', {'class':'pagination__items'}).find_all('a', {'class':'item'})
            except:
                list_div=None
            if list_div  is not None:
                if list_div  is not None:
                    t=1
                    try :
                        k=len(list_div)+1
                    except :
                        k=1
                    while t<=k:
                        art_url_s=tg20_url1+'?PAGEN_1={}/'.format(str(t))
                        self.get_html('arts',city_id,city_name,art_url_s,t)
                        t=t+1
            else :
                pages=page.split('/')
                page = '/{}/{}/{}/{}/'.format(pages[3],pages[4],pages[5],pages[6])
                self.get_html('arts',city_id,city_name,page,0)
        
        
        
        def get_arts(self,text,city_id,city_name,grp_id,page):
            global dfArt
            soup = BeautifulSoup(text.encode("utf-8"))
            dfArt_a=pd.DataFrame(columns=['art_name','arts_ssilk'])
            po=len(dfArt_a.index)
            try:
                art_list_= soup.find('div', {'id':'catalog-items'}).find('div', {'class': 'products-list row'}) 
                items_all = art_list_.find_all('div', {'class': 'col-md-3'})
                for i in items_all:
                    k=i.find('div',{'class': 'products-list-item__header'})
                    if k!= None:
                        for i in k.find_all('a'):
                            if i.find('div',{'class':'products-list-item__title'})!=None:
                                arts_ssilk=i.get('href')
                                arts_name=i.find('div',{'class':'products-list-item__title'}).get('title')
                    dfArt_a.loc[po] = [arts_name,arts_ssilk]
                    self.arts_reference.append({arts_name:arts_ssilk})
                    po=po+1
                    str_id=0
            except Exception as err:
                mess='ERROR({}): get_arts в городе: {} \n\tвыпала  ошибка: {}\n\t\t URL: {}'.format(kref,city_name,err,page)
                Logging(mess,text)
            dfArt= dfArt.append(dfArt_a)
        
             
        def get_arts_info (self,text,city_name,page):
            '''
            this module collects all information on TP in the context specified by the customer 
            '''
            kttkt='https://www.podrygka.ru/catalog/makiyazh/litso/korrektor/147804-konsiler_dlya_litsa_maybelline_the_eraser_eye_ton_01_slonovaya_kost/'
            a=pd.DataFrame(columns=['art_id','art_name','grp20_name','grp21_name','grp22_name','vendor','line','country_KA','price','price_sale'])
            global dfart_info
            po=len(a.index)
            price_sale=None
            country_KA=None 
            grp20_name=None 
            grp21_name=None
            grp22_name =None
            try:
                soup = BeautifulSoup(text.encode("utf-8"))
                art_list_= soup.find('section', {'class':'page-content-header'}).find('section', {'class':'breadcrumbs'})
                grp_list=art_list_.find_all('a', {'class':'breadcrumbs-item'}) #Ищем все блоки групп
                try:
                    grp20_name=grp_list[1].text.strip()
                except : True
                try:
                    grp21_name=grp_list[2].text.strip()
                except: True
                try:
                    grp22_name=art_list_.find('span', {'class':'breadcrumbs-item'}).text.strip()
                except: True
                art_name= soup.find('section', {'class':'product-detail'}).find('div',{'class':'product-detail__top'}).find('h1').text.strip()
                art_info_html = soup.find('section', {'class':'product-detail'}).find('div',{'class':'product-detail__top'})
                art_id = art_info_html.find('div',{'class':'product-detail__articul'}).find('span',{'class':'value'}).text.strip()
                vendor=art_info_html.find('div',{'class':'product-detail__brand'}).find('div',{'class':'image'}).find('img').get('alt')
                line =art_info_html.find('div',{'class':'product-detail__desc'}).find('span').text.strip()
                country_KA=art_info_html.find('div',{'class':'product-detail__country'}).find('span',{'class':'value'}).text.strip()

                try:
                    price=art_info_html.find('div',{'class':'product-detail__panel'}).find('div',{'class':'price'}).find('span',{'class':'price__item price__item--old'}).find('span',{'class':'price_value'}).text.strip()
                    price_sale=art_info_html.find('div',{'class':'product-detail__panel'}).find('div',{'class':'price'}).find('span',{'class':'price__item price__item--current'}).find('span',{'class':'price_value'}).text.strip()
                except:
                    price=art_info_html.find('div',{'class':'product-detail__panel'}).find('div',{'class':'price'}).find('span',{'class':'price__item price__item--current'}).find('span',{'class':'price_value'}).text.strip()
                try:
                    art_all =art_info_html.find('div',{'class':'product-detail__panel'}).find_all('div',{'class':'item'})
                    for i in art_all:
                        art_id= i.find('span').text.strip().split(' ')[1]
                        art_name = i.find('img').get('title')
                        a.loc[po]=[art_id,art_name,grp20_name,grp21_name,grp22_name,vendor,line,country_KA,price,price_sale]  
                        po+=1
                    if po<1:
                        a.loc[po]=[art_id,art_name,grp20_name,grp21_name,grp22_name,vendor,line,country_KA,price,price_sale]
                except:
                    a.loc[po]=[art_id,art_name,grp20_name,grp21_name,grp22_name,vendor,country_KA,price,price_sale]     
            except Exception as err:
                mess='ERROR({}): Art_info в городе: {}  \n\tвыпала  ошибка: {}'.format(kref,city_name,err)
                Logging(mess,text)
            dfart_info= dfart_info.append(a)
            
 
        def do_work(self,i,city_id,city_name):
            art_url=list(i.values())[0]
            self.get_html('arts_info',city_id,city_name,art_url,0)
     
     
        def worker(self,city_id,city_name):
            while True:
                item = self.queu.get()
                print('я обрабатываю:'+str(item))
                if item is None:
                    break
                self.do_work(item,city_id,city_name)
                
                self.queu.task_done()
    
        
        def main(self,city_id,city_name):
            print(str(city_id)+":"+str(city_name))
            self.get_html('catalog',city_id,city_name,0,0)
            for i in self.art_grp_list:
                tg20_name=list(i.keys())[0]
                self.tg20_url = list(list(i.values())[0])[0]
                tg20_url = list(list(i.values())[0])[0]
                self.get_html('pages',city_id,city_name,tg20_url,0)
            
            for item in self.arts_reference:
                #input(item)
                self.queu.put(item)
            for i in range(num_worker_threads):
                print(i)
                print(num_worker_threads)
                t = threading.Thread(target=self.worker,args=[city_id,city_name])
                t.start()
                self.threads.append(t)
            self.queu.join() 
            for i in range(num_worker_threads):
                self.queu.put(None)
            for t in self.threads:
                t.join()   
            print(self.iskl)
except : 
    print('Error')


def do_work(i):
    city_id=int(list(i.keys())[0])
    city_name=list(i.values())[0]
    mess='start_city: {}'.format(city_name)
    Logging(mess,'text')
    app=Scraping('city',city_id,city_name,0,0)
    app.main(city_id,city_name)
    import_to_excel('info',city_name)
    import_to_excel('dfg',city_name)
    import_to_excel('dfs',city_name)
    import_to_excel('dfArt',city_name)
    mess='finish_city: {}'.format(city_name)
    Logging(mess,'text')
 
         
def worker():
    while True:
        item = q.get()
        if item is None:
            break
        do_work(item)
        q.task_done()

def import_to_excel(prem, city):
    #===========================================================================
    # Модуль заливки данных в EXCEL он работает и работает хорошо
    #===========================================================================
    if prem=='info':
        print('я заливаю: info')
        po=len(dfart_info.index)
        i=0
        while i<=po:
            if  int(po)-(i+1000000)>=1000000:
                file_name='E:\\SVN\\Skraping\\All_podruzka\\art_info_from_{} {}_{}.xlsx'.format(str(city),str(i),str(i+1000000)) # 
                dfart_info[i:i+1000001].to_excel(file_name, sheet_name='sheet1', index=False)
                i+=1000000
            else: 
                file_name='E:\\SVN\\Skraping\\All_podruzka\\art_info_from_{} {}_{} .xlsx'.format(str(city),str(i),str(i+1000000)) 
                dfart_info[i:po].to_excel(file_name, sheet_name='sheet1', index=False)
                i+=1000000
    elif prem=='dfs':
        print('я заливаю: dfs')
        po=len(dfS.index)
        i=0
        while i<=po:
            if  int(po)-1000000>=1000000:
                file_name='E:\\SVN\\Skraping\\All_podruzka\\MH_from_{}_potok {}_{}.xlsx'.format(str(city),str(i),str(i+1000000)) 
                dfS[i:i+1000001].to_excel(file_name, sheet_name='sheet1', index=False)
                i+=1000000
            else: 
                file_name='E:\\SVN\\Skraping\\All_podruzka\\MH_from_{}_potok {}_{}.xlsx'.format(str(city),str(i),str(i+1000000)) 
                dfS[i:po].to_excel(file_name, sheet_name='sheet1', index=False)
                i+=1000000
    elif prem=='dfg':
        print('я заливаю: dfg')
        po=len(dfg.index)
        i=0
        while i<=po:
            if  int(po)-1000000>=1000000:
                file_name='E:\\SVN\\Skraping\\All_podruzka\\group_from_{} {}_{} .xlsx'.format(str(city),str(i),str(i+1000000)) 
                dfg[i:i+1000001].to_excel(file_name, sheet_name='sheet1', index=False)
                i+=1000000
            else: 
                file_name='E:\\SVN\\Skraping\\All_podruzka\\group_from_{} {}_{} .xlsx'.format(str(city),str(i),str(i+1000000)) 
                dfg[i:po].to_excel(file_name, sheet_name='sheet1', index=False)
                i+=1000000
    elif prem=='dfArt':
        print('я заливаю: dfArt')
        po=len(dfArt.index)
        i=0
        while i<=po:
            if  int(po)-1000000>=1000000:
                file_name='E:\\SVN\\Skraping\\All_podruzka\\arts_from_{} {}_{} .xlsx'.format(str(city),str(i),str(i+1000000)) 
                dfArt[i:i+1000001].to_excel(file_name, sheet_name='sheet1', index=False)
                i+=1000000
            else: 
                file_name='E:\\SVN\\Skraping\\All_podruzka\\arts_from_{}  {}_{} .xlsx'.format(str(city),str(i),str(i+1000000)) 
                dfArt[i:po].to_excel(file_name, sheet_name='sheet1', index=False)
                i+=1000000





def main():
    city_list_=[{'1':'г.Краснодар'}]
    for i in range(num_worker_threads1):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    for item in city_list_:
        q.put(item)
    q.join()   
    for i in range(num_worker_threads1):
        q.put(None)
    for t in threads:
        t.join()
 
  
    end_time = datetime.now()
    mess='Finish_PO: {}'.format(end_time)
    Logging(mess,'text')
    print('Duration: {}'.format(end_time - start_time))  
    mess='Duration_PO: {}'.format(end_time - start_time)
    Logging(mess,'text')  
    
main()

import requests
import os
from bs4 import BeautifulSoup
import random
import cv2
import shutil

# من اسم اسکریپت رو هانتر گذاشتم فکر کنم بدونید واسه چی
# this script written for treasure-hunt

# https://github.com/Haj4li

# یک لیست برای نگه داری محصولات لازم داریم
prdklist = []

# و باز کردن عکس مشترک داخل کد تخفیف ها
temp = cv2.imread("blk.jpg",1)
temp = cv2.cvtColor(temp, cv2.COLOR_RGB2GRAY) 


# این تابع میاد تصاویر پیدا شده رو با عکس blk.jpg مچ میکنه
def scan_image(src):
    global temp
    src = cv2.imread(src,1)
    src = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
    
    height, width =src.shape
    H, W = temp.shape
    trys = 0

    true_locs = []

    methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF]#, cv2.TM_SQDIFF_NORMED]
    
    for method in methods:
        src2 = src.copy()
        try:
            result = cv2.matchTemplate(src2, temp, method)
        except cv2.error:
            print("Error in scanning ")
            break
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if method in [cv2.TM_SQDIFF,cv2.TM_CCORR]:
            location = min_loc
        else:
            location = max_loc
        
        true_locs.append(min_loc)
        true_locs.append(max_loc)

        bottom_right = (location[0] + W, location[1] + H)

    loc = []
    rpt = 0
    for locs in true_locs:
        tmp = true_locs.count(locs)
        if (tmp > rpt):
            loc = locs
            rpt = tmp

    if (rpt >= 3):
        return 1 # اگه شبیه باشه یک رو برمیگردونه
    else:
        return 0 # وگرنه صفر

# این تابع تصاویر رو برای اسکن دانلود میکنه 
def downloadImages(path,src):
    if (not os.path.isdir("images\\"+path)):
        os.mkdir("images\\"+path) # اگر این مسیر وجود نداشت ایجادش میکنه
    response = requests.get(src)
    if response.status_code == 200:
        image_name = "pic_{1}_{0}.jpg".format(random.randint(0,9999999),path)
        with open("images\\"+path+"\\"+image_name, 'wb') as f:
            f.write(response.content)
    del response

    return image_name

# برای اینکه بدونیم کجا کار رو شروع کنیم و کجا تموم کنیم این دو متغییر رو از کاربر دریافت میکنیم
start = int(input("Enter Start point : "))
end = int(input("Enter End point : "))

# url مربوط به لیست محصولات دیجی کالا
# https://www.digikala.com/treasure-hunt/products/?pageno=1&sortby=4

errors = 0
for i in range(start,end):
    url = "https://www.digikala.com/treasure-hunt/products/?pageno={0}&sortby=4".format(i)
    # get products
    r = requests.get(url)
    print ("[+] Getting {0} ...".format(url))   
    page = str(r.content)
    pos = 0
    while ("/product/dkp-" in page):
        # find product
        page = str(page[pos:])
        pos = page.find("/product/dkp-")+len("/product/")
        prdname = page[pos:pos+35]
        prdname = prdname[:prdname.find("/")]
        pos += len("/product/")
        # اینجا بررسی میکنیم که آیا محصول قبلا اسکن شده یا نه
        if (not prdname in prdklist):
            prdklist.append(prdname)
            urls = "https://www.digikala.com/product/{0}/".format(prdname)
            pages = requests.get(urls)
            soup = BeautifulSoup(pages.content, "html.parser")
            results = soup.find_all(class_="c-remodal-gallery__main-img")
            print ("[+] Scaning images ( {0}/{1} )".format(i,prdname))
            # تمام تصاویر موجود در صفحه محصول اسکن میشن
            for res in results:
                try:
                    img_name = downloadImages(prdname,res.find("img")["data-src"])                    
                    if (scan_image("images\\"+prdname+"\\"+img_name) == 1):
                        # قسمت شیرین بحث اینجا بود که بعد پیدا کردن بهم اطلاع میداد
                        print("High chance for : {0} , prd : {1} , page {2}".format(img_name,prdname,i))
                        shutil.copy2("images\\"+prdname+"\\"+img_name,".")
                except TypeError:
                    errors += 1










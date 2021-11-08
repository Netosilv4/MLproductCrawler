from dotenv import load_dotenv

load_dotenv()

import requests 
import time
from datetime import datetime
from parsel import Selector
from pymongo import MongoClient
import os



databaseUri = os.getenv("DATABASE")

database = MongoClient(
   databaseUri
)

db = database.tryCommerce

# Paste initial url search link here

initialUrl = "https://lista.mercadolivre.com.br/30-seconds-to-mars#D[A:30%20seconds%20to%20mars]"

def get_products(url):
    crawlerUrl = url
    while crawlerUrl:

        response = requests.get(crawlerUrl)

        selector = Selector(text=response.text)
        
        titles = selector.css("a.ui-search-item__group__element::attr(href)").getall()

        for title in titles:
            currentTitle = requests.get(title)
            currentTitle = Selector(text=currentTitle.text)
            print("Nome produto - " + currentTitle.css("h1.ui-pdp-title::text").get())
            print("Preço - R$ " + currentTitle.css("span.price-tag-fraction::text").get())
            print(currentTitle.css("h2.ui-pdp-specs__title::text").get())
            specs = currentTitle.css("tr.andes-table__row")
            productSpecs = []
            productImages = []
            productSubSpecs = []
            for spec in specs:
                try:
                    print(spec.css("th.andes-table__header::text").get() + " " + spec.css("span.andes-table__column--value::text").get())
                    name = spec.css("th.andes-table__header::text").get()
                    value = spec.css("span.andes-table__column--value::text").get()
                    productSpecs.append({"name": name, "value": value})
                except:
                    pass
            
            for subSpec in currentTitle.css("p.ui-pdp-list__text"):
                try:
                    productSubSpecs.append({"name": subSpec.css("span.ui-pdp-family--BOLD::text").get(), "value": subSpec.css("p::text").get()[2:]})
                except:
                    pass

            for image in currentTitle.css(".ui-pdp-gallery__figure__image::attr(data-zoom)").getall():
                try:
                    productImages.append(image)
                except:
                    pass

            createdAt = datetime.now()
            createdAt = createdAt.strftime("%m/%d/%Y %H:%M:%S")
            db.placas.update_one(
                {
                    "productName": currentTitle.css("h1.ui-pdp-title::text").get(),
                    "productPrice": round(int(currentTitle.css("span.price-tag-fraction::text").get()), 2),
                    "description": currentTitle.css("p.ui-pdp-description__content::text").getall(),
                },
                {  
                    "$setOnInsert": {
                    "productName": currentTitle.css("h1.ui-pdp-title::text").get(),
                    "productPrice": round(int(currentTitle.css("span.price-tag-fraction::text").get()), 2),
                    "description": currentTitle.css("p.ui-pdp-description__content::text").getall(),
                    "productSpecs": productSpecs,
                    "otherSpecs": productSubSpecs,
                    "productImages": productImages,
                    "quantity": 5,
                    "category": currentTitle.css("a.andes-breadcrumb__link::text").get(),
                    "createdAt": datetime.now()
                    }
                },
                    upsert=True
            )

            print("-----------------------------------------------------")


        nextLi = selector.css("li.andes-pagination__button--next")
        nextLink = nextLi.css("a.andes-pagination__link::attr(href)").get()
        print(nextLink)
        print("--------------------------------------------------")
        crawlerUrl = nextLink
        time.sleep(10)


try:
    get_products(initialUrl)
except:
    time.sleep(10)
    get_products(initialUrl)
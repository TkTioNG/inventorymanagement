from django.shortcuts import render
import requests
import json


HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Token 0bd31960612fe660d71c5ea164e5606f1328dee9'
}


def index(request):
    context = {'latest_question_list': 'latest_question_list'}
    return render(request, 'inventory/index.html', context)


def products(request):
    req = requests.get(
        'http://localhost:8000/api/v1/product/',
        headers=HEADERS
    )
    print(req.json())
    context = {'products': req.json()}
    return render(request, 'inventory/products.html', context)


def materials(request):
    req = requests.get(
        'http://localhost:8000/api/v1/material/',
        headers=HEADERS
    )
    print(req.json())
    context = {'materials': req.json()}
    return render(request, 'inventory/materials.html', context)


def material_stocks(request):
    req = requests.get(
        'http://localhost:8000/api/v1/material-stock/',
        headers=HEADERS
    )
    print(req.json())
    context = {'material_stocks': req.json()}
    return render(request, 'inventory/material_stocks.html', context)


def restock(request):
    req = requests.get(
        'http://localhost:8000/api/v1/restock/',
        headers=HEADERS
    )
    print(req.json())
    data_json = req.json()
    context = {
        'materials': data_json.get('materials', []),
        'total_price': data_json.get('total_price', 0.00)
    }
    return render(request, 'inventory/restock.html', context)


def inventory(request):
    req = requests.get(
        'http://localhost:8000/api/v1/inventory/',
        headers=HEADERS
    )
    print(req.json())
    data_json = req.json()
    context = {
        'materials': data_json.get('materials', []),
    }
    return render(request, 'inventory/inventory.html', context)


def productCapacity(request):
    req = requests.get(
        'http://localhost:8000/api/v1/product-capacity/',
        headers=HEADERS
    )
    print(req.json())
    data_json = req.json()
    context = {
        'remaining_capacities': data_json.get('remaining_capacities', [])
    }
    return render(request, 'inventory/product_capacity.html', context)


def sales(request):
    context = {
        "success": False,
        "data": None,
        "error": None,
    }
    if request.method == "POST":
        post_data = request.POST
        counter = 0
        checker = post_data.__contains__("product"+str(counter)) \
            and post_data.__contains__("quantity"+str(counter))
        sale = []
        while checker:
            sale.append({
                "product": post_data.get("product"+str(counter)),
                "quantity": int(post_data.get("quantity"+str(counter)))
            })
            counter += 1
            checker = post_data.__contains__("product"+str(counter)) \
                and post_data.__contains__("quantity"+str(counter))

        sales_data = {
            "sale": sale
        }
        post_req = requests.post(
            'http://localhost:8000/api/v1/sales/',
            json=sales_data,
            headers=HEADERS
        )
        print(post_req.status_code)
        if post_req.status_code == 200:
            context["success"] = True
            context["data"] = post_req.json().get("sale", [])
        else:
            context["error"] = post_req.json()

    req = requests.get(
        'http://localhost:8000/api/v1/product/',
        headers=HEADERS
    )
    context['products'] = req.json()
    print(context)
    return render(request, 'inventory/sales.html', context)

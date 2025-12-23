from django.shortcuts import render, redirect
from firebase_admin import db
from django.http import JsonResponse
from django.http import HttpResponse

def home(request):
    return render(request, 'main/home.html')

def manage_coin(request):
    ref = db.reference('driver')
    drivers = ref.get()

    coins = []
    total_coin = 0

    if drivers:
        for key, d in drivers.items():
            name = d.get('name')
            phone = d.get('phone')
            coin = int(d.get('coins', 0))

            coins.append({
                'name': name,
                'phone': phone,
                'coin': coin
            })

            total_coin += coin

    return render(request, "main/manage_coin.html", {
        'coins': coins,
        'total_coin': total_coin
    })

def calculate_payout(request, phone):
    drivers_ref = db.reference('driver')
    drivers_data = drivers_ref.get()
    if not drivers_data:
        return HttpResponse("Danh sách tài xế rỗng")
    driver_key = None
    driver_data = None
    # 🔎 Tìm tài xế theo phone
    for key, data in drivers_data.items():
        if str(data.get('phone')) == str(phone):
            driver_key = key
            driver_data = data
            break
    if not driver_data:
        return HttpResponse("Không tìm thấy tài xế")
    current_coin = int(driver_data.get('coins', 0))
    driver_name = driver_data.get('name', 'Tài xế')
    if current_coin <= 100:
        return HttpResponse("Coin không hợp lệ")
    payout_coin = current_coin - 100

    # 👉 XỬ LÝ FORM POST
    # ==========================
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "confirm":
            # ✅ Xác nhận: reset coin về 100
            drivers_ref.child(driver_key).update({
                'coins': 100
            })
            return redirect('manage_coin')

        elif action == "reject":
            # ❌ Từ chối: không thay đổi dữ liệu
            return redirect('manage_coin')
        
    return render(request, "main/calculate_payout.html", {
        "driver_name": driver_name,
        "payout_coin": payout_coin
        })

def calculate_payment(request, phone):
    drivers_ref = db.reference('driver')
    drivers_data = drivers_ref.get()
    if not drivers_data:
        return HttpResponse("Danh sách tài xế rỗng")
    driver_key = None
    driver_data = None
    # 🔎 Tìm tài xế theo phone
    for key, data in drivers_data.items():
        if str(data.get('phone')) == str(phone):
            driver_key = key
            driver_data = data
            break
    if not driver_data:
        return HttpResponse("Không tìm thấy tài xế")
    current_coin = int(driver_data.get('coins', 0))
    driver_name = driver_data.get('name', 'Tài xế')
    if current_coin >= 100:
        return HttpResponse("Coin không hợp lệ")
    payment_coin = 100 - current_coin

    # 👉 XỬ LÝ FORM POST
    # ==========================
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "confirm":
            # ✅ Xác nhận: reset coin về 100
            drivers_ref.child(driver_key).update({
                'coins': 100
            })
            return redirect('manage_coin')

        elif action == "reject":
            # ❌ Từ chối: không thay đổi dữ liệu
            return redirect('manage_coin')
        
    return render(request, "main/calculate_payment.html", {
        "driver_name": driver_name,
        "payment_coin": payment_coin
        })
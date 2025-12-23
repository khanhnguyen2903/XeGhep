from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_config
from firebase_admin import credentials, db

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # số điện thoại
        password = request.POST.get('password')
       
        # Truy cập node 'driver' trong Realtime Database
        ref = db.reference('driver')
        drivers = ref.get()

        # Kiểm tra dữ liệu
        user_found = False
        is_admin = False

        if drivers:
            for key, driver in drivers.items():
                phone = driver.get('phone')
                pwd = driver.get('password')
                name = driver.get('name')
               
                if phone == username and pwd == password:
                    user_found = True
                    # Lưu session
                    request.session['driver_phone'] = phone
                    request.session['driver_name'] = name
                    break
                if name == username and pwd == password:
                    is_admin = True
                    # Lưu session
                    request.session['driver_phone'] = phone
                    request.session['driver_name'] = name

        if user_found:
            return redirect('list_trip')  # tên URL đến trang danh sách tài xế
        elif is_admin:
            return redirect('home')
        else:
            messages.error(request, "Bạn hãy nhập lại !")

    return render(request, 'users/login.html')

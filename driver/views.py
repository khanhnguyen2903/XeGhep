from django.shortcuts import render, redirect
from firebase_admin import db
import firebase_config

def add_driver_view(request):
    if request.method == 'POST':
        data = {
            "name": request.POST.get('name'),
            "phone": request.POST.get('phone'),
            "password": request.POST.get('password'),
            "car_model": request.POST.get('car_model'),
            "seat_count": int(request.POST.get('seat_count')),
            "license_plate": request.POST.get('license_plate'),
            "owner_name": request.POST.get('owner_name'),
            "coins": int(request.POST.get('coins')),
            "is_active": True if request.POST.get('is_active') == "True" else False
        }
        ref = db.reference('driver')
        ref.push(data)
        return redirect('list_driver')
    return render(request, 'driver/add_driver.html')

def list_driver_view(request):
    ref = db.reference('driver')
    data = ref.get()
    drivers = []
    if data:
        for key, val in data.items():
            val['id'] = key
            drivers.append(val)
    return render(request, 'driver/list_driver.html', {'drivers': drivers})

def edit_driver(request, id):
    """
    Chỉnh sửa thông tin tài xế theo ID trong Firebase.
    """
    ref = db.reference(f'driver/{id}')
    driver = ref.get()

    if not driver:
        return redirect('list_driver')  # Nếu không có ID này thì quay về danh sách

    if request.method == 'POST':
        updated_data = {
            "name": request.POST.get('name'),
            "phone": request.POST.get('phone'),
            "password": request.POST.get('password'),
            "car_model": request.POST.get('car_model'),
            "seat_count": int(request.POST.get('seat_count')),
            "license_plate": request.POST.get('license_plate'),
            "owner_name": request.POST.get('owner_name'),
            "coins": int(request.POST.get('coins')),
            "is_active": True if request.POST.get('is_active') == "True" else False
        }
        ref.update(updated_data)
        return redirect('list_driver')

    # Hiển thị form với dữ liệu hiện tại
    return render(request, 'driver/edit_driver.html', {'driver': driver, 'id': id})


def delete_driver(request, id):
    """
    Xóa tài xế khỏi Firebase theo ID.
    """
    ref = db.reference(f'driver/{id}')
    driver = ref.get()

    if not driver:
        return redirect('list_driver')

    if request.method == 'POST':
        ref.delete()
        return redirect('list_driver')

    # Hiển thị trang xác nhận xóa
    return render(request, 'driver/list_driver.html', {'driver': driver, 'id': id})
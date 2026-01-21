from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_config
from firebase_admin import credentials, db


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")  # số điện thoại
        password = request.POST.get("password")

        # Truy cập node 'driver' trong Realtime Database
        ref = db.reference("driver")
        drivers = ref.get()

        # Kiểm tra dữ liệu
        user_found = False
        is_admin = False

        if drivers:
            for key, driver in drivers.items():
                phone = driver.get("phone")
                pwd = driver.get("password")
                name = driver.get("name")

                if phone == username and pwd == password:
                    user_found = True
                    # Lưu session
                    request.session["driver_phone"] = phone
                    request.session["driver_name"] = name
                    break
                if name == username and pwd == password:
                    # Lưu session
                    is_admin = True
                    request.session["driver_phone"] = phone
                    request.session["driver_name"] = name

        if user_found:
            return redirect("home")  # tên URL đến trang danh sách tài xế
        elif is_admin:
            return redirect("home")
        else:
            messages.error(request, "Bạn hãy nhập lại !")

    return render(request, "users/login.html")


def reset_pass(request):
    # 🔒 Kiểm tra đăng nhập
    if "driver_phone" not in request.session or "driver_name" not in request.session:
        return redirect("login")

    driver_phone = request.session["driver_phone"]
    driver_name = request.session["driver_name"]
    # print("driver_name: " + driver_name)
    # print("driver_phone: " + driver_phone)

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")

        # Lấy dữ liệu drivers từ Firebase
        ref = db.reference("driver")
        ref_drivers = ref.get()

        if not ref_drivers:
            messages.error(request, "Không tìm thấy dữ liệu người dùng.")
            return redirect("reset_pass")
        # Tìm user theo name + phone
        for key, user in ref_drivers.items():
            name = user.get("name")
            phone = user.get("phone")
            password = user.get("password")
            # print(len(ref_drivers))
            # print("name: " + name)
            # print("phone: " + phone)
            if name == driver_name and phone == driver_phone:
                # So sánh mật khẩu hiện tại
                if current_password != password:
                    messages.error(request, "Mật khẩu hiện tại không đúng.")
                    return redirect("reset_pass")
                # Cập nhật mật khẩu mới
                ref.child(key).update({"password": new_password})
                messages.success(request, "Đổi mật khẩu thành công.")
                return redirect("list_trip")

        # Không tìm thấy user phù hợp
        messages.error(request, "Không xác định được người dùng.")
        return redirect("reset_pass")

    return render(request, "users/reset_pass.html")

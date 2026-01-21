from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import db  # dùng db đã khởi tạo trong firebase_config.py
import datetime


def create_trip(request):
    # 🔹 Lấy thông tin tài xế từ session
    driver_name = request.session.get("driver_name", "Tài xế")
    driver_phone = request.session.get("driver_phone", "Số điện thoại")

    if request.method == "POST":
        # Lấy dữ liệu từ form
        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("phone")
        num_passengers = request.POST.get("num_people")
        pickup_location = request.POST.get("pickup_location")
        dropoff_location = request.POST.get("dropoff_location")
        pickup_time = request.POST.get("pickup_time")
        status = request.POST.get("status")

        # Tạo dictionary chứa dữ liệu chuyến đi
        trip_data = {
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "num_passengers": num_passengers,
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "pickup_time": pickup_time,
            "driver_name_create_trip": driver_name,
            "driver_phone_create_trip": driver_phone,
            "driver_name_assigned_trip": "",
            "driver_phone_assigned_trip": "",
            "status": status,
            "created_at": datetime.datetime.now().isoformat(),
        }

        try:
            # 1. Lưu chuyến đi vào node 'trips'
            ref = db.reference("trips")
            new_trip = ref.push(trip_data)

            return redirect("list_trip")

        except Exception as e:
            messages.error(request, f"❌ Lỗi khi gửi dữ liệu: {e}")

    return render(request, "trips/create_trip.html", {"driver_name": driver_name})


def list_trip(request):
    # 🔹 Lấy thông tin tài xế từ session
    driver_name = request.session.get("driver_name", "Tài xế")
    driver_phone = request.session.get("driver_phone", "Số điện thoại")

    # 🔹 Lấy thông tin số điểm của tài xế
    # ======================================
    driver_coins = 0
    drivers_ref = db.reference("driver")
    drivers_data = drivers_ref.get()

    if drivers_data:
        for key, driver in drivers_data.items():
            if driver.get("phone") == driver_phone:
                driver_coins = driver.get("coins", 0)
                break

    # 🔹 Lấy danh sách chuyến đi
    ref = db.reference("trips")
    data = ref.get()
    trips = []

    if data:
        for trip_id, info in data.items():
            # ⚠️ Chỉ lấy chuyến có trạng thái "Đang chờ tài xế"
            if info.get("status") != "Đang chờ tài xế":
                continue

            dt = datetime.datetime.fromisoformat(info["pickup_time"])
            trips.append(
                {
                    "id": trip_id,
                    "customer_name": info.get("customer_name"),
                    "customer_phone": info.get("customer_phone"),
                    "num_passengers": info.get("num_passengers"),
                    "pickup_location": info.get("pickup_location"),
                    "dropoff_location": info.get("dropoff_location"),
                    "pickup_time": dt.strftime("%d/%m/%Y %H:%M"),
                    "driver_name_create_trip": info.get("driver_name_create_trip"),
                    "driver_phone_create_trip": info.get("driver_phone_create_trip"),
                    "driver_name_assigned_trip": info.get("driver_name_assigned_trip"),
                    "driver_phone_assigned_trip": info.get(
                        "driver_phone_assigned_trip"
                    ),
                    "status": info.get("status"),
                }
            )

    return render(
        request,
        "trips/list_trip.html",
        {"trips": trips, "driver_name": driver_name, "driver_coins": driver_coins},
    )


def accept_trip(request, trip_id):
    driver_name_accept = request.session.get("driver_name", "Tài xế")
    driver_phone_accept = request.session.get("driver_phone", "Số điện thoại")

    if request.method == "POST":
        try:
            # 🔹 Cập nhật thông tin chuyến đi: tài xế nhận chuyến
            trip_ref = db.reference(f"trips/{trip_id}")
            trip_data = trip_ref.get()
            # 🔹 Cập nhật: tài xế nhận chuyến
            trip_ref.update(
                {
                    "status": "Đã nhận tài xế",
                    "driver_name_assigned_trip": driver_name_accept,
                    "driver_phone_assigned_trip": driver_phone_accept,
                }
            )

            # messages.success(request, "✅ Bạn đã nhận chuyến. Điểm đã được cập nhật!")
            return redirect("list_trip_receiving")

        except Exception as e:
            messages.error(request, f"❌ Lỗi khi cập nhật dữ liệu: {e}")
            return redirect("list_trip")

    return redirect("list_trip")


def finish_trip(request, trip_id):
    driver_phone_accept = request.session.get("driver_phone", "Số điện thoại")

    if request.method == "POST":

        # Tham chiếu đến chuyến đi trong Firebase
        trip_ref = db.reference(f"trips/{trip_id}")
        trip_data = trip_ref.get()

        if trip_data:
            # Cập nhật trạng thái
            trip_ref.update({"status": "Kết thúc chuyến đi"})
        # 🔹 Truy cập node driver để tìm đúng tài xế theo số điện thoại
        drivers_ref = db.reference("driver")
        drivers_data = drivers_ref.get()

        # 1️⃣ TRỪ 10 ĐIỂM TÀI XẾ NHẬN CHUYẾN
        if drivers_data:
            for key, driver in drivers_data.items():
                if driver.get("phone") == driver_phone_accept:
                    current_coins = driver.get("coins", 0)
                    new_coins = max(current_coins - 10, 0)  # tránh âm điểm
                    drivers_ref.child(key).update({"coins": new_coins})
                    break

        # 2️⃣ CỘNG 10 ĐIỂM CHO TÀI XẾ TẠO CHUYẾN
        if trip_data:
            driver_phone_create_trip = trip_data.get("driver_phone_create_trip")

            if driver_phone_create_trip:
                for key, driver in drivers_data.items():
                    if driver.get("phone") == driver_phone_create_trip:
                        current_coins_create = driver.get("coins", 0)
                        new_coins_create = current_coins_create + 10
                        drivers_ref.child(key).update({"coins": new_coins_create})
                        break
        # Quay lại trang danh sách các chuyến đang nhận
        return redirect("list_trip_receiving")

    # Nếu người dùng truy cập GET → quay về danh sách
    return redirect("list_trip_receiving")


def cancel_trip(request, trip_id):
    if request.method == "POST":
        # 🔹 Tham chiếu đến chuyến đi trong Firebase
        trip_ref = db.reference(f"trips/{trip_id}")
        trip_data = trip_ref.get()

        if trip_data:
            # Cập nhật status và xóa thông tin tài xế nhận chuyến
            trip_ref.update(
                {
                    "status": "Đang chờ tài xế",
                    "driver_phone_assigned_trip": "",
                    "driver_name_assigned_trip": "",
                }
            )

        # Quay lại trang danh sách chuyến đang nhận
        return redirect("list_trip")

    # Nếu truy cập GET → quay lại danh sách
    return redirect("list_trip")


def list_trip_receiving(request):
    # 🔹 Lấy thông tin tài xế đang đăng nhập
    driver_name = request.session.get("driver_name", "Tài xế")
    driver_phone = request.session.get("driver_phone", "")

    # 🔹 Lấy số điểm tài xế
    driver_coins = 0
    drivers_ref = db.reference("driver")
    drivers_data = drivers_ref.get()

    if drivers_data:
        for key, driver in drivers_data.items():
            if driver.get("phone") == driver_phone:
                driver_coins = driver.get("coins", 0)
                break

    # 🔹 Lấy danh sách chuyến đi đã nhận bởi tài xế này
    ref = db.reference("trips")
    data = ref.get()

    trips = []

    if data:
        for trip_id, info in data.items():

            # Chỉ lấy chuyến tài xế này đã nhận
            if (
                info.get("driver_phone_assigned_trip") == driver_phone
                and info.get("status") == "Đã nhận tài xế"
            ):
                dt = datetime.datetime.fromisoformat(info["pickup_time"])
                trips.append(
                    {
                        "id": trip_id,
                        "customer_name": info.get("customer_name"),
                        "customer_phone": info.get("customer_phone"),
                        "num_passengers": info.get("num_passengers"),
                        "pickup_location": info.get("pickup_location"),
                        "dropoff_location": info.get("dropoff_location"),
                        "pickup_time": dt.strftime("%d/%m/%Y %H:%M"),
                        "driver_name_create_trip": info.get("driver_name_create_trip"),
                        "driver_phone_create_trip": info.get(
                            "driver_phone_create_trip"
                        ),
                        "driver_name_assigned_trip": info.get(
                            "driver_name_assigned_trip"
                        ),
                        "driver_phone_assigned_trip": info.get(
                            "driver_phone_assigned_trip"
                        ),
                        "status": info.get("status"),
                    }
                )

    # 🔹 Render lại đúng giao diện list_trip.html
    return render(
        request,
        "trips/list_trip.html",
        {"trips": trips, "driver_name": driver_name, "driver_coins": driver_coins},
    )


def list_trip_completed(request):
    # Lấy thông tin tài xế đang đăng nhập
    driver_phone = request.session.get("driver_phone", "")
    driver_name = request.session.get("driver_name", "Tài xế")

    # 🔹 Lấy số điểm tài xế
    driver_coins = 0
    drivers_ref = db.reference("driver")
    drivers_data = drivers_ref.get()

    if drivers_data:
        for key, driver in drivers_data.items():
            if driver.get("phone") == driver_phone:
                driver_coins = driver.get("coins", 0)
                break

    if not driver_phone:
        return redirect("login")

    # 🔹 Truy vấn danh sách chuyến đi từ Firebase
    trips_ref = db.reference("trips")
    all_trips = trips_ref.get()

    trip_list = []

    if all_trips:
        for trip_id, info in all_trips.items():

            # Lọc chuyến có trạng thái "Kết thúc chuyến đi"
            # và số điện thoại tài xế nhận chuyến trùng với tài xế đang đăng nhập
            if (
                info.get("status") == "Kết thúc chuyến đi"
                and info.get("driver_phone_assigned_trip") == driver_phone
            ):
                dt = datetime.datetime.fromisoformat(info["pickup_time"])
                trip_list.append(
                    {
                        "id": trip_id,
                        "customer_name": info.get("customer_name"),
                        "customer_phone": info.get("customer_phone"),
                        "num_passengers": info.get("num_passengers"),
                        "pickup_location": info.get("pickup_location"),
                        "dropoff_location": info.get("dropoff_location"),
                        "pickup_time": dt.strftime("%d/%m/%Y %H:%M"),
                        "driver_name_create_trip": info.get("driver_name_create_trip"),
                        "driver_phone_create_trip": info.get(
                            "driver_phone_create_trip"
                        ),
                        "driver_name_assigned_trip": info.get(
                            "driver_name_assigned_trip"
                        ),
                        "driver_phone_assigned_trip": info.get(
                            "driver_phone_assigned_trip"
                        ),
                        "status": info.get("status"),
                    }
                )

    # Trả về trang hiển thị
    return render(
        request,
        "trips/list_trip.html",
        {
            "trips": trip_list,
            "driver_name": driver_name,
            "driver_coins": driver_coins,
        },
    )


def list_trip_created(request):
    # 🔹 Lấy thông tin tài xế từ session
    driver_name = request.session.get("driver_name", "Tài xế")
    driver_phone = request.session.get("driver_phone", "Số điện thoại")

    # 🔹 Lấy số điểm của tài xế
    driver_coins = 0
    drivers_ref = db.reference("driver")
    drivers_data = drivers_ref.get()

    if drivers_data:
        for key, driver in drivers_data.items():
            if driver.get("phone") == driver_phone:
                driver_coins = driver.get("coins", 0)
                break

    # 🔹 Lấy danh sách chuyến đi từ Firebase
    ref = db.reference("trips")
    data = ref.get()
    trips = []

    if data:
        for trip_id, info in data.items():

            # ✅ Điều kiện 1: chỉ lấy chuyến do tài xế đang đăng nhập tạo
            if info.get("driver_name_create_trip") != driver_name:
                continue

            # ✅ Điều kiện 2: chỉ lấy chuyến "Đang chờ tài xế"
            if info.get("status") != "Đang chờ tài xế":
                continue

            dt = datetime.datetime.fromisoformat(info["pickup_time"])

            trips.append(
                {
                    "id": trip_id,
                    "customer_name": info.get("customer_name"),
                    "customer_phone": info.get("customer_phone"),
                    "num_passengers": info.get("num_passengers"),
                    "pickup_location": info.get("pickup_location"),
                    "dropoff_location": info.get("dropoff_location"),
                    "pickup_time": dt.strftime("%d/%m/%Y %H:%M"),
                    "driver_name_create_trip": info.get("driver_name_create_trip"),
                    "driver_phone_create_trip": info.get("driver_phone_create_trip"),
                    "driver_name_assigned_trip": info.get("driver_name_assigned_trip"),
                    "driver_phone_assigned_trip": info.get(
                        "driver_phone_assigned_trip"
                    ),
                    "status": info.get("status"),
                }
            )

    return render(
        request,
        "trips/list_trip.html",
        {
            "trips": trips,
            "driver_name": driver_name,
            "driver_coins": driver_coins,
        },
    )


def logout(request):
    # Xóa toàn bộ dữ liệu session (bao gồm thông tin driver)
    request.session.flush()
    return redirect("login_view")

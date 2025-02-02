import cv2
import serial
import time
import tkinter as tk
import threading
import random
import sys

# STM32 ile iletişim için seri port
stm32 = serial.Serial(port="COM6", baudrate=9600, timeout=1)  # STM32'nin bağlı olduğu portu kontrol edin
time.sleep(2)  # Seri portun bağlanması için bekleme süresi

# LED'lerin durumu
led1_state = False
led2_state = False
led3_state = False

# STM32'ye komut gönderme fonksiyonu
def send_command_to_stm32(command):
    try:
        stm32.write(command.encode())  # Komutu STM32'ye gönder
        print(f"STM32'ye gönderildi: {command}")
    except Exception as e:
        print(f"STM32'ye veri gönderilemedi: {e}")

# GUI'de LED'lerin durumunu güncelleme
def update_leds_state(led_state):
    global led1_state, led2_state, led3_state
    
    if led_state == '0':
        # 2 LED'i aç (PC0, PC1) ve 3. LED'i kapalı tut
        led1_state = True
        led2_state = True
        led3_state = False
        send_command_to_stm32("0")
    elif led_state == '1':
        # 3 LED'i aç (PC0, PC1, PC2)
        led1_state = True
        led2_state = True
        led3_state = True
        send_command_to_stm32("1")
    elif led_state == 's':
        # Gözler kapalı olduğunda LED'leri tamamen kapat
        led1_state = False
        led2_state = False
        led3_state = False
        send_command_to_stm32("s")
    
    # LED'lerin durumunu güncelle
    led1_label.config(bg="green" if led1_state else "red")
    led2_label.config(bg="green" if led2_state else "red")
    led3_label.config(bg="green" if led3_state else "red")
    
    # Durum etiketlerini güncelle
    led1_status_label.config(text="Yandı" if led1_state else "Yanmadı", bg="green" if led1_state else "red")
    led2_status_label.config(text="Yandı" if led2_state else "Yanmadı", bg="green" if led2_state else "red")
    led3_status_label.config(text="Yandı" if led3_state else "Yanmadı", bg="green" if led3_state else "red")

# OpenCV ile yüz ve göz tanıma fonksiyonu
def detect_face_and_smile():
    # OpenCV'nin Haar-Cascade sınıflandırıcılarını yükleme
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    # Kamerayı aç
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Yüzü çerçeve içine al
            roi_gray = gray[y:y + h, x:x + w]
            
            # Gözleri algılama
            eyes = eye_cascade.detectMultiScale(roi_gray)
            
            if len(eyes) == 0:
                # Gözler kapalı
                print("Gözler Kapalı")
                update_leds_state('s')  # LED'leri kapat
            else:
                # Gülümseme algılama
                smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
                if len(smiles) > 0:
                    # Gülümseme algılandı
                    update_leds_state('1')  # 3 LED'i aç
                else:
                    # Gülümseme algılanmadı (üzgün yüz)
                    update_leds_state('0')  # 2 LED'i aç

        # OpenCV penceresinde görüntüyü göster
        cv2.imshow('Görünüm', frame)
        
        # 'q' tuşuna basarak çıkış
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Tkinter GUI ayarları
root = tk.Tk()
root.title("LED Kontrol Arayüzü")

# LED gösterge etiketleri
led1_label = tk.Label(root, text="LED 1", width=12, height=3, font=("Helvetica", 12), bg="red")
led1_label.grid(row=0, column=0, padx=10, pady=10)

led2_label = tk.Label(root, text="LED 2", width=12, height=3, font=("Helvetica", 12), bg="red")
led2_label.grid(row=0, column=1, padx=10, pady=10)

led3_label = tk.Label(root, text="LED 3", width=12, height=3, font=("Helvetica", 12), bg="red")
led3_label.grid(row=0, column=2, padx=10, pady=10)

# LED'lerin durumunu gösteren etiketler
led1_status_label = tk.Label(root, text="Yanmadı", width=12, height=2, font=("Helvetica", 10), bg="red")
led1_status_label.grid(row=1, column=0, padx=10, pady=10)

led2_status_label = tk.Label(root, text="Yanmadı", width=12, height=2, font=("Helvetica", 10), bg="red")
led2_status_label.grid(row=1, column=1, padx=10, pady=10)

led3_status_label = tk.Label(root, text="Yanmadı", width=12, height=2, font=("Helvetica", 10), bg="red")
led3_status_label.grid(row=1, column=2, padx=10, pady=10)

# Başlatma butonu
start_button = tk.Button(root, text="Yüz Tanıma Başlat", command=lambda: threading.Thread(target=detect_face_and_smile, daemon=True).start(), font=("Helvetica", 12), bg="blue", fg="white", height=2, width=15)
start_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Sonlandırma butonu
stop_button = tk.Button(root, text="Sonlandır", command=lambda: [send_command_to_stm32('s'), sys.exit()], font=("Helvetica", 12), bg="red", fg="white", height=2, width=15)
stop_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# GUI sürekli güncellenmesi için after kullanma
def update_gui():
    root.after(100, update_gui)

# Arayüzü başlat
update_gui()
root.mainloop()

🖐️ Gesture Volume Control Pro
Windows sistem sesini el hareketleriyle kontrol etmeyi sağlayan, yapay zeka tabanlı bir bilgisayarlı görü projesidir. MediaPipe ve OpenCV kullanılarak geliştirilen bu sistem, parmak uçlarınız arasındaki mesafeyi matematiksel olarak analiz eder ve Pycaw kütüphanesi üzerinden sistem sesini gerçek zamanlı olarak günceller.

Kullanılan Teknolojiler
Python 3.12+
OpenCV: Kamera yönetimi ve görüntü işleme.
MediaPipe: Yüksek hassasiyetli el landmark tespiti.
Pycaw: Windows Core Audio API erişimi.
NumPy: Matematiksel haritalama (interpolation) işlemleri.

📦 Kurulum
Proje dizininde aşağıdaki komutu çalıştırarak gerekli bağımlılıkları yükleyebilirsiniz:

pip install opencv-python mediapipe pycaw comtypes numpy

Programı başlatmak için:

python main.py

Kontroller
Sesi Artırma: Baş parmak ve işaret parmağınızı birbirinden uzaklaştırın.

Sesi Azaltma: İki parmağınızı birbirine yaklaştırın.

Çıkış: Pencere odaklıyken klavyeden 'q' tuşuna basın.

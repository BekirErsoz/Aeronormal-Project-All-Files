import airsim
import cv2
import numpy as np

# AirSim'e bağlan
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

# Dronu kalkışa geçirin
client.takeoffAsync().join()

# Canlı video akışı
while True:
    # Kameradan görüntü alın
    response = client.simGetImage("0", airsim.ImageType.Scene)
    if response is not None:
        # Görüntüyü işleyin
        img = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        img = img.reshape(response.height, response.width, 3)
        cv2.imshow("Drone Camera", img)

    # Kullanıcı inputunu kontrol edin
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# Dronu indirin ve bağlantıyı kapatın
client.landAsync().join()
client.armDisarm(False)
client.enableApiControl(False)
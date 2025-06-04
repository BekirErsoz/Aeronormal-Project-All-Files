import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from datetime import datetime, timedelta

# Rastgele veri oluşturma
np.random.seed(42)

# Zaman verisi oluşturma (1 saatlik veri, her saniye için bir veri noktası)
start_time = datetime.now()
time = [start_time + timedelta(seconds=i) for i in range(3600)]

# Rastgele hız verisi (0 ile 10 m/s arasında)
speed = np.random.uniform(0, 10, len(time))

# GPS koordinatları (başlangıç noktası olarak belirli bir koordinat)
lat_start = 40.7128
lon_start = -74.0060

# Küçük değişikliklerle rastgele GPS verileri oluşturma
latitude = [lat_start + np.random.uniform(-0.0005, 0.0005) for _ in time]
longitude = [lon_start + np.random.uniform(-0.0005, 0.0005) for _ in time]

# Verileri DataFrame'e koyma
df = pd.DataFrame({'time': time, 'speed': speed, 'latitude': latitude, 'longitude': longitude})

# İlk birkaç satırı gösterme
print(df.head())

# Veriyi kaydetme
df.to_excel('simulated_drone_data.xlsx', index=False)

# Zaman ve hız sütunlarını seçme
time = df['time']
speed = df['speed']

# Hızın zaman içindeki değişimi
plt.figure(figsize=(12, 6))
plt.plot(time, speed, label='Speed')
plt.xlabel('Time')
plt.ylabel('Speed (m/s)')
plt.title('Speed over Time')
plt.legend()
plt.show()

# Harita oluşturma
map_drone = folium.Map(location=[latitude[0], longitude[0]], zoom_start=14)

# Drone rotasını çizme
for lat, lon in zip(latitude, longitude):
    folium.Marker(location=[lat, lon]).add_to(map_drone)

# Haritayı kaydetme
map_drone.save('simulated_drone_route.html')
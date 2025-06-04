#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// Donanım başlatma işlevleri
void hardware_init(void) {
    // Buraya donanım başlatma kodlarını ekleyin
}

// LED kontrol işlevleri
void led_on(void) {
    // LED'i yak
}

void led_off(void) {
    // LED'i söndür
}

// Görevler
void led_task(void *pvParameters) {
    while (1) {
        led_on();
        vTaskDelay(pdMS_TO_TICKS(500)); // 500ms LED açık
        led_off();
        vTaskDelay(pdMS_TO_TICKS(500)); // 500ms LED kapalı
    }
}

void counter_task(void *pvParameters) {
    int counter = 0;
    while (1) {
        counter++;
        // Sayacı güncelle
        vTaskDelay(pdMS_TO_TICKS(1000)); // Her 1 saniyede bir sayacı artır
    }
}

int main() {
    hardware_init(); // Donanımı başlat

    // Görevleri oluşturma
    xTaskCreate(led_task, "LED Task", configMINIMAL_STACK_SIZE, NULL, 1, NULL);
    xTaskCreate(counter_task, "Counter Task", configMINIMAL_STACK_SIZE, NULL, 1, NULL);

    // RTOS'u başlatma
    vTaskStartScheduler();

    // Sistem buraya ulaşmamalı
    while (1);
    return 0;
}
#include "FreeRTOS.h"
#include "task.h"
#include "web_server.h"
#include "led_control.h"

void hardware_init(void) {
    // Donanım başlatma kodları
}

void led_task(void *pvParameters) {
    while (1) {
        // LED durumunu kontrol et
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

int main() {
    hardware_init();

    xTaskCreate(led_task, "LED Task", configMINIMAL_STACK_SIZE, NULL, 1, NULL);
    xTaskCreate(web_server_task, "Web Server Task", configMINIMAL_STACK_SIZE * 4, NULL, 2, NULL);

    vTaskStartScheduler();

    while (1);
    return 0;
}
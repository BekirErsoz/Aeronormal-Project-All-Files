#include "web_server.h"
#include "led_control.h"
#include "lwip/tcp.h"

static err_t http_recv(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
    if (p != NULL) {
        // HTTP isteğini işleyin
        if (strstr(p->payload, "GET /led/on")) {
            led_on();
        } else if (strstr(p->payload, "GET /led/off")) {
            led_off();
        } else if (strstr(p->payload, "GET /led/toggle")) {
            toggle_led();
        }

        // HTTP yanıtını gönderin
        const char *response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nLED state changed";
        tcp_write(tpcb, response, strlen(response), 1);

        pbuf_free(p);
    } else if (err == ERR_OK && p == NULL) {
        tcp_close(tpcb);
    }
    return ERR_OK;
}

void web_server_task(void *pvParameters) {
    struct tcp_pcb *pcb;
    pcb = tcp_new();
    tcp_bind(pcb, IP_ADDR_ANY, 80);
    pcb = tcp_listen(pcb);
    tcp_accept(pcb, http_recv);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 12345
#define BUFFER_SIZE 1024

int main() {
    int sock = 0;
    struct sockaddr_in serv_addr;
    
    // Создаем сокет
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("\n Socket creation error \n");
        return -1;
    }
    
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(SERVER_PORT);
    
    // Преобразуем IP адрес из текстового в бинарный формат
    if (inet_pton(AF_INET, SERVER_IP, &serv_addr.sin_addr) <= 0) {
        printf("\nInvalid address/ Address not supported \n");
        return -1;
    }
    
    // Подключаемся к серверу
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        printf("\nConnection Failed \n");
        return -1;
    }
    
    printf("Подключение к серверу установлено\n");
    
    // Отправляем данные серверу
    char *message = "Hello from client!";
    int message_len = strlen(message);
    
    // Явно отправляем все данные
    int total_sent = 0;
    while (total_sent < message_len) {
        int sent = send(sock, message + total_sent, message_len - total_sent, 0);
        if (sent < 0) {
            perror("send failed");
            close(sock);
            return -1;
        }
        total_sent += sent;
    }
    
    printf("Сообщение отправлено: %s\n", message);
    
    // Ждем немного, чтобы сервер успел получить данные
    sleep(1);
    
    // Закрываем соединение для записи (отправляем FIN)
    shutdown(sock, SHUT_WR);
    
    // Читаем возможный ответ от сервера
    char buffer[BUFFER_SIZE] = {0};
    int valread = read(sock, buffer, BUFFER_SIZE - 1);
    if (valread > 0) {
        printf("Ответ от сервера: %s\n", buffer);
    }
    
    // Полностью закрываем соединение
    close(sock);
    
    return 0;
}
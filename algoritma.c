#include "stm32f4xx.h"

// UART ve GPIO yapilandirmalari
void UART_Init(void) {
    RCC->APB1ENR |= (1 << 17);  // USART2 için saat aç
    RCC->AHB1ENR |= (1 << 0);   // GPIOA için saat aç

    GPIOA->MODER &= ~((0x3 << 2 * 2) | (0x3 << 2 * 3));
    GPIOA->MODER |= (0x2 << 2 * 2) | (0x2 << 2 * 3);  // PA2 ve PA3 alternatif fonksiyon
    GPIOA->AFR[0] |= (0x7 << 8) | (0x7 << 12);        // PA2 ve PA3 USART2 için ayarlandi

    USART2->BRR = 0x0683;  // Baud rate = 9600
    USART2->CR1 |= (1 << 3) | (1 << 2) | (1 << 13);  // TX, RX ve USART etkin
}

void UART_SendString(char *str) {
    while (*str) {
        while (!(USART2->SR & (1 << 7)));  // TXE bekle
        USART2->DR = *str++;
    }
}

void GPIO_Init(void) {
    RCC->AHB1ENR |= (1 << 2);  // GPIOC saat aç
    GPIOC->MODER |= (0x1 << 2 * 0) | (0x1 << 2 * 1) | (0x1 << 2 * 2);  // PC0, PC1, PC2 output
}

void GPIO_Set(uint8_t command) {
    if (command == '1') {
        GPIOC->ODR |= (1 << 0) | (1 << 1) | (1 << 2);  // PC0, PC1, PC2 HIGH
        UART_SendString("All LEDs ON\n");
    } else if (command == '0') {
        GPIOC->ODR |= (1 << 0) | (1 << 1);  // PC0, PC1 HIGH
        GPIOC->ODR &= ~(1 << 2);            // PC2 LOW
        UART_SendString("Only LED1 and LED2 ON\n");
    } else if (command == 's') {
        // 's' komutu geldiginde tüm LED'leri kapat
        GPIOC->ODR &= ~(1 << 0);  // PC0 LOW
        GPIOC->ODR &= ~(1 << 1);  // PC1 LOW
        GPIOC->ODR &= ~(1 << 2);  // PC2 LOW
        UART_SendString("All LEDs OFF\n");
    } else {
        UART_SendString("Unknown Command\n");
    }
}

int main(void) {
    GPIO_Init();
    UART_Init();

    uint8_t received;

    while (1) {
        while (!(USART2->SR & (1 << 5)));  // RXNE bekle
        received = USART2->DR;             // Gelen veriyi oku
        GPIO_Set(received);                // LED'leri kontrol et
    }
}


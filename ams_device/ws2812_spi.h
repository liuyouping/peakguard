/*
 * Copyright (C) 2026 PeakGuard Team
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef __WS2812_SPI_H__
#define __WS2812_SPI_H__
 
// WS2812初始化 
void ws2812_spi_init(void);   
void ws2812_spi_bright(int level);

void ws2812_close(void); 
void ws2812_low(void);
void ws2812_middle(void);
void ws2812_high(void); 
void ws2812_sos(void);

void ws2812_format_new(uint8_t red, uint8_t green, uint8_t blue, uint8_t *buff);

//void ws2812_flash(int index);

void set_color(uint8_t r, uint8_t g, uint8_t b);
void breath_loop(void);
 

#endif  // __WS2812_SPI_H__
/*
 * Copyright (C) 2026 PeakGuard Team
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
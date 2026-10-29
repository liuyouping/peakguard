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

#ifndef __BLOOD_FUNC_H__
#define __BLOOD_FUNC_H__
  

void ProcessClient(uint8_t *data, uint16_t length);

void SendToClient(uint8_t *data, uint16_t length);

// 同步时钟给 sle client
void SendClock(void);

#endif  // __BLOOD_FUNC_H__
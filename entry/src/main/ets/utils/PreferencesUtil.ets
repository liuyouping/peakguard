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

import dataPreferences from '@ohos.data.preferences'
import GlobalContext from './GlobalContext'

const PREFERENCES_NAME = 'user_data_name'
const KEY_PREFERENCES = "user_data_key"

let context = getContext(this);

type ValueType = number | string | boolean | Array<number> | Array<string> | Array<boolean> | Uint8Array | object | bigint

export class PreferencesUtil {
  // preferences的文件名
  private preferencesName: string = PREFERENCES_NAME
  // 用于获取preferences实例的key值，保存到单例中
  private keyPreferences: string = KEY_PREFERENCES

  constructor(name: string = PREFERENCES_NAME, keyP: string = KEY_PREFERENCES) {
    this.preferencesName = name
    this.keyPreferences = keyP
  }

  createPreferences(context: Context): Promise<dataPreferences.Preferences> {
    let preferences = dataPreferences.getPreferences(context, this.preferencesName)
    GlobalContext.getContext().setObject(this.keyPreferences, preferences)
    return preferences
  }

  getPreferences(): Promise<dataPreferences.Preferences> {
    return GlobalContext.getContext().getObject(KEY_PREFERENCES) as Promise<dataPreferences.Preferences>
  }

  async get(key: string, def?: ValueType): Promise<ValueType> {
    return (await this.getPreferences()).get(key, def)
  }

  async getAll(): Promise<Object> {
    let  preferences = await this.getPreferences()
    return preferences.getAll()
  }

  async put(key: string, value: ValueType): Promise<void> {
    let promise = await this.getPreferences().then(async (p) => {
      await p.put(key, value)
      await p.flush();
    }).catch((err: Error)=>{
      console.log(String(err))
    })
    return promise
  }

  async delete(key: string): Promise<void> {
    return (await this.getPreferences()).delete(key).finally(async () => {
      (await this.getPreferences()).flush()
    })
  }

  async clear(): Promise<void> {
    return (await this.getPreferences()).clear().finally(async () => {
      (await this.getPreferences()).flush()
    })
  }

}

export default new PreferencesUtil()


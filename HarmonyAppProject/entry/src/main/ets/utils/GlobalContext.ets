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

export default  class GlobalContext {
    private constructor() {}
    private static  instance: GlobalContext;
    private _objects = new Map<string, Object>();

    public static getContext(): GlobalContext {
        if( !GlobalContext.instance) {
            GlobalContext.instance = new GlobalContext();
        }
        return GlobalContext.instance;
    }

    getObject(value: string): Object | undefined {
        return this._objects.get(value);
    }

    setObject(key: string, objectClass: Object): void {
        this._objects.set(key, objectClass);
    }

}
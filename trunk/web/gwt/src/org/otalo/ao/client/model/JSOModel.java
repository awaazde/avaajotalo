/*
 * Copyright (c) 2009 Regents of the University of California, Stanford University, and others
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
package org.otalo.ao.client.model;

import java.util.HashSet;
import java.util.Set;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.core.client.JsArrayString;

/**
 * Java overlay of a JavaScriptObject.
 */
public abstract class JSOModel extends JavaScriptObject {

    // Overlay types always have protected, zero-arg constructors
    protected JSOModel() {
    }

    /**
     * Create an empty instance.
     * 
     * @return new Object
     */
    public static native JSOModel create() /*-{
        return new Object();
    }-*/;

    public static native boolean isArray(String jsonString) /*-{
        return jsonString.indexOf('[') === 0;
    }-*/;
    
    /**
     * Convert a JSON encoded string into a JSOModel instance.
     * <p/>
     * Expects a JSON string structured like '{"foo":"bar","number":123}'
     *
     * @return a populated JSOModel object
     */
    public static native JSOModel fromJson(String jsonString) /*-{
        return eval('(' + jsonString + ')');
    }-*/;

    /**
     * Convert a JSON encoded string into an array of JSOModel instance.
     * <p/>
     * Expects a JSON string structured like '[{"foo":"bar","number":123}, {...}]'
     *
     * @return a populated JsArray
     */
    public static native JsArray<JSOModel> arrayFromJson(String jsonString) /*-{
        return eval('(' + jsonString + ')');
    }-*/;

    public final native boolean hasKey(String key) /*-{
        return this[key] != undefined;
    }-*/;

    public final native JsArrayString keys() /*-{
        var a = new Array();
        for (var p in this) { a.push(p); }
        return a;
    }-*/;

    @Deprecated
    public final Set<String> keySet() {
        JsArrayString array = keys();
        Set<String> set = new HashSet<String>();
        for (int i = 0; i < array.length(); i++) {
            set.add(array.get(i));
        }
        return set;
    }

    public final native String get(String key) /*-{
        return "" + this[key];
    }-*/;

    public final native String get(String key, String defaultValue) /*-{
        return this[key] ? ("" + this[key]) : defaultValue;
    }-*/;

    public final native void set(String key, String value) /*-{
        this[key] = value;
    }-*/;

    public final int getInt(String key) {
        return Integer.parseInt(get(key));
    }

    public final boolean getBoolean(String key) {
        return Boolean.parseBoolean(get(key));
    }

    public final native JSOModel getObject(String key) /*-{
        return this[key];
    }-*/;

    public final native JsArray<JSOModel> getArray(String key) /*-{
        return this[key] ? this[key] : new Array();
    }-*/;
}

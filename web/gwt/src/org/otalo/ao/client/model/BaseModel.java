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

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.JsArray;
import com.google.gwt.core.client.JsArrayString;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Element;

public class BaseModel {

    protected JSOModel data;

    public BaseModel(JSOModel data) {
        this.data = data;
    }

    protected JSOModel getData()
    {
    	return data;
    }
    
    public String get(String field) {
        String val = this.data.get(field);
        if (val != null && "null".equals(val) || "undefined".equals(val)) {
            return null;
        } else {
            return escapeHtml(val);
        }
    }
    
    public JSOModel getObject(String key) {
      JSOModel obj = this.data.getObject(key);
      if (obj != null && "null".equals(obj) || "undefined".equals(obj)) {
          return null;
      } else {
          return obj;
      }
  }

    public Map<String, String> getFields() {
        Map<String, String> fieldMap = new HashMap<String, String>();

        if (data != null) {
            JsArrayString array = data.keys();

            for (int i = 0; i < array.length(); i++) {
                fieldMap.put(array.get(i), data.get(array.get(i)));
            }
        }
        return fieldMap;
    }

    private static String escapeHtml(String maybeHtml) {
        final Element div = DOM.createDiv();
        DOM.setInnerText(div, maybeHtml);
        return DOM.getInnerHTML(div);
    }
    
    public String getId() {
  		return get("pk");
  	}
    
    public String getField(String field)
    {
    	return getObject("fields").get(field);
    }
    
    public JsArray<JSOModel> getArray(String key)
    {
    	return this.data.getArray(key);
    }
}

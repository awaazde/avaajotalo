/*
 * Copyright 2007 Google Inc.
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
package org.otalo.ao.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONException;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.TreeItem;

import java.util.ArrayList;
import java.util.List;

import org.otalo.ao.client.model.JSOModel;

/**
 * Class that acts as a client to a JSON service. 
 */
public final class JSONRequest {
  /**
   * Class for handling the response text associated with a request for a JSON
   * object.
   */
	public final class AoAPI {
		public static final String USER = "user/";
		public static final String THREAD = "thread/";
		public static final String FORUM = "forum/";
		public static final String MESSAGES = "messages/";
		public static final String UPDATE_MESSAGE = "update/message/";
		public static final String MOVE = "move/";
		public static final String UPLOAD = "upload/";
		public static final String APPROVE = "approve/";
		public static final String REJECT = "reject/";
		public static final String UPDATE_STATUS = "update/status/";
		
		public static final String POSTS_TOP = "top";
		public static final String POSTS_ALL = "all";
		public static final String POSTS_RESPONSES = "responses";
	}
	public static List<JSOModel> getModels(String jsonStr)
	{
		 jsonStr = jsonStr.replaceAll("\\n","");
		 List<JSOModel> models = new ArrayList<JSOModel>();
		 if (JSOModel.isArray(jsonStr))
		 {
			 JsArray<JSOModel> data = JSOModel.arrayFromJson(jsonStr);

			 for (int i = 0; i < data.length(); i++) {
         models.add(data.get(i));
			 }

		 }
		 else
		 {
			 JSOModel data = JSOModel.fromJson(jsonStr); 
			 models.add(data);
		 }
		 
		 return models;
	}
  private class JSONResponseTextHandler implements RequestCallback {
    public void onError(Request request, Throwable exception) {
      // TODO
    }

    public void onResponseReceived(Request request, Response response) 
    {
    	 if (response.getStatusCode() == 200) 
    	 {
    		 List<JSOModel> models = getModels(response.getText());
	      
    		 requester.dataReceived(models);
    	 } 
    	 else
    	 {
    		 onError(request, new RequestException(response.getText()));
    	 }
      
    }

  }

  public static final String BASE_URL = "/AO/";
  private JSONRequester requester;
  
  /*
   * Fetch the requested URL.
   */
  public void doFetchURL(String fetchURL, JSONRequester requester) {
  	this.requester = requester;
  	// RequestBuilder used to issue HTTP GET requests.
  	RequestBuilder requestBuilder = new RequestBuilder(
	      RequestBuilder.GET, URL.encode(BASE_URL + fetchURL));
    try {
      requestBuilder.sendRequest(null, new JSONResponseTextHandler());
    } catch (RequestException ex) {
    	// TODO
    }
  }
  
}

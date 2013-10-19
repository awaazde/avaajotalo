/*
 * Copyright 2007 Google Inc.
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
package org.otalo.ao.client;


import java.util.ArrayList;
import java.util.List;

import org.otalo.ao.client.model.JSOModel;

import com.google.gwt.core.client.JsArray;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;

/**
 * Class that acts as a client to a JSON service. 
 */
public final class JSONRequest {
  /**
   * Class for handling the response text associated with a request for a JSON
   * object.
   */
	public static final class AoAPI {
		public static final String USER = "user/";
		public static final String THREAD = "thread/";
		public static final String FORUM = "forum/";
		public static final String MESSAGES = "messages/";
		public static final String UPDATE_MESSAGE = "update/message/";
		public static final String MOVE = "move/";
		public static final String RECORD_OR_UPLOAD = "recordorupload/";
		public static final String APPROVE = "approve/";
		public static final String REJECT = "reject/";
		public static final String UPDATE_STATUS = "update/status/";
		public static final String LOGOUT = "/logout/";
		public static final String TAGS = "tags/";
		public static final String TAGS_BY_LINE = "tagsbyline/";
		public static final String MESSAGE_TAGS = "messagetag/";
		public static final String RESPONDERS = "responders/";
		public static final String MESSAGE_RESPONDERS = "messageresponder/";
		public static final String MODERATOR = "moderator/";
		public static final String LINE = "line/";
		public static final String DOWNLOAD = "download/mf/";
		public static final String DOWNLOAD_SURVEY_INPUT = "download/si/";
		public static final String SURVEY = "survey/";
		public static final String BCAST_MESSAGE = "bcast/";
		public static final String FORWARD_THREAD = "fwdthread/";
		public static final String SURVEY_INPUT = "surveyinput/";
		public static final String PROMPT_RESPONSES = "promptresponses/";
		public static final String CANCEL_SURVEY = "cancelsurvey/";
		public static final String SURVEY_DETAILS = "surveydetails/";
		public static final String REGULAR_BCAST = "regularbcast/";
		public static final String SMS = "sms/";
		public static final String SMS_RECIPIENTS = "smsrecipients/";
		public static final String SEND_SMS = "sendsms/";
		public static final String CREATE_GROUP = "s/creategroup/";
		public static final String GROUP = "group/";
		public static final String MEMBERS = "s/members/";
		public static final String UPDATE_MEMBER = "s/update/member/";
		public static final String ADD_MEMBERS = "s/addmembers/";
		public static final String UPDATE_GROUP_SETTINGS = "s/update/groupsettings/";
		public static final String UPDATE_MEMBER_STATUS = "s/update/memberstatus/";
		public static final String DELETE_GROUP = "s/deletegroup/";
		public static final String BROADCAST_REPORTS = "s/broadcastreports/";
		public static final String DOWNLOAD_BCAST_REPORT = "s/download/bcastreport/";
		public static final String DOWNLOAD_STREAM_REPORT = "s/download/streamreport/";
		public static final String BALANCE = "s/balance/";
		
		public static final String POSTS_TOP = "top";
		public static final String POSTS_ALL = "all";
		public static final String POSTS_RESPONSES = "responses";
		
		@Deprecated
		public static final String TAG_TYPE_CROP = "agri-crop";
		@Deprecated
		public static final String TAG_TYPE_TOPIC = "agri-topic";
		
		public static final String MSG_METADATA = "MESSAGE_METADATA";
		public static final String MEMBER_METADATA = "MEMBER_METADATA";
		
		/**
		 * Should be consistent with views.py validation codes
		 * @author neil
		 *
		 */
		public enum ValidationError {  
	  	INVALID_NUMBER(1), NO_CONTENT(2), INVALID_GROUPNAME(3), MEMBER_CREDITS_EXCEEDED(4), INVALID_DATE(5), INVALID_GROUP_SETTING(6), INVALID_FILE_FORMAT(7);
	  
	    private int code;  
	  
	    private ValidationError(int code) {  
	        this.code = code;  
	    }  
	  
	    public int getCode() {  
	        return code;  
	    }  
	    
	    public static ValidationError getError(int code) {
	    	for (ValidationError s : values())
	    	{
	    		if (s.getCode() == code)
	    			return s;
	    	}
	    	
	    	return null;
	    }
	  }  
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
  
  public static void doPost(String url, String postData) {
    RequestBuilder builder = new RequestBuilder(RequestBuilder.POST, url);

    try {
      builder.setHeader("Content-Type", "application/x-www-form-urlencoded");
      Request response = builder.sendRequest(postData, new RequestCallback() {

        public void onError(Request request, Throwable exception) {
          // code omitted for clarity
        }

        public void onResponseReceived(Request request, Response response) {
          // code omitted for clarity
        }
      });
    } catch (RequestException e) {
    }
  }
  
}

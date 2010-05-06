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
import java.util.Date;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

/**
 * A simple client-side generator of fake email messages.
 */
public class MessageItems {

  private static final int NUM_ITEMS = 37;
  
  private static JSONArray fora;
  

  private static final Date[] dates = new Date[] {
      new Date(), new Date(), new Date(), new Date(),
      new Date(), new Date(), new Date(), new Date(),
      new Date(), new Date(), new Date(), new Date(), 
      new Date(), new Date(), new Date(), new Date(), 
      new Date(), new Date(), new Date(), new Date(), 
      new Date(), new Date(), new Date(), new Date(), 
      new Date(), new Date(), new Date(), new Date(), 
      new Date(), new Date(), new Date(), new Date(), 
      new Date(), new Date(), new Date(), new Date(), 
      new Date(), };
  
  private static final String[] statuses = new String[] {
      "new", "old", "live", "old",
      "new", "old", "live", "old",
      "new", "old", "live", "old",
      "new", "old", "live", "old",
      "new", "old", "live", "old",
      "new", "old", "live", "old",
      "new", "old", "live", "old",
      "new", "old", "live", "old",
      "new", "old", "live", "old",
      "new"};
  
  private static final String[] callers = new String[] {
      "markboland05", "Hollie Voss", "boticario", "Emerson Milton",
      "Healy Colette", "Brigitte Cobb", "Elba Lockhart", "Claudio Engle",
      "Dena Pacheco", "Brasil s.p", "Parker", "derbvktqsr", "qetlyxxogg",
      "antenas.sul", "Christina Blake", "Gail Horton", "Orville Daniel",
      "PostMaster", "Rae Childers", "Buster misjenou", "user31065",
      "ftsgeolbx", "aqlovikigd", "user18411", "Mildred Starnes",
      "Candice Carson", "Louise Kelchner", "Emilio Hutchinson",
      "Geneva Underwood", "Residence Oper?", "fpnztbwag", "tiger",
      "Heriberto Rush", "bulrush Bouchard", "Abigail Louis", "Chad Andrews",
      "bjjycpaa", "Terry English", "Bell Snedden", "huang", "hhh",
      "(unknown sender)", "Kent", "Dirk Newman", "Equipe Virtual Cards",
      "wishesundmore", "Benito Meeks"};
  
  private static final String[] questionFiles = new String[] {
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1", "~/Development/otalo/audio/q2", "~/Development/otalo/audio/q3", "~/Development/otalo/audio/q4",
      "~/Development/otalo/audio/q1"};
  
  private static final String[] responseFiles = new String[] {
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1", "~/Development/otalo/audio/a2", "~/Development/otalo/audio/a3", "~/Development/otalo/audio/a4",
      "~/Development/otalo/audio/a1"};


  private static int dateIdx = 0, statusIdx = 0, callerIdx = 0, questionFileIdx = 0, responseFileIdx = 0;
  private static ArrayList<MessageItem> items = new ArrayList<MessageItem>();

  static {
    for (int i = 0; i < NUM_ITEMS; ++i) {
      items.add(createFakeMessages());
    }
    
    fora = new JSONArray();
    JSONObject f1 = new JSONObject();
    f1.put("name", new JSONString("qna"));
    JSONObject f2 = new JSONObject();
    f2.put("name", new JSONString("radio"));
    JSONObject f3 = new JSONObject();
    f3.put("name", new JSONString("anubhav"));
    JSONObject f4 = new JSONObject();
    f4.put("name", new JSONString("announcements"));
    fora.set(0, f1);
    fora.set(1, f2);
    fora.set(2, f3);
    fora.set(3, f4);
  }
  
  public static JSONArray getFora()
  {
  	return fora;
  }

  public static MessageItem getMessageItem(int index) {
    if (index >= items.size()) {
      return null;
    }
    return items.get(index);
  }

  public static int getMessageItemCount() {
    return items.size();
  }

  private static MessageItem createFakeMessages() {
    Date date = dates[dateIdx++];
    if (dateIdx == callers.length) {
      dateIdx = 0;
    }
    
//    String status = statuses[statusIdx++];
//    if (statusIdx == callers.length) {
//    	statusIdx = 0;
//    }
    
    String caller = callers[callerIdx++];
    if (callerIdx == callers.length) {
    	callerIdx = 0;
    }
    
    String questionFile = questionFiles[questionFileIdx++];
    if (questionFileIdx == callers.length) {
    	questionFileIdx = 0;
    }
    
//    String responseFile = responseFiles[responseFileIdx++];
//    if (responseFileIdx == callers.length) {
//    	responseFileIdx = 0;
//    }

    return new MessageItem(date, caller, questionFile);
  }
}

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

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.core.client.JsArray;


public class Forum extends BaseModel {
	private static final String METADATA_MODEL_TYPE = "GROUP_METADATA";
	// make this consistent with ao:models.py
  public enum ForumStatus {  
  	BCAST_CALL_SMS(1), BCAST_SMS(2), INACTIVE(3), BCAST_CALL(4);
  
    private int code;  
  
    private ForumStatus(int code) {  
        this.code = code;  
    }  
  
    public int getCode() {  
        return code;  
    }  
    
    public static ForumStatus getStatus(int code) {
    	for (ForumStatus s : values())
    	{
    		if (s.getCode() == code)
    			return s;
    	}
    	
    	return null;
    }
  }  
  
	
	public Forum(JSOModel data) 
	{
		super(data);
	}
	
	public String getName() {
		return getField("name");
	}
	
	public boolean postingAllowed()
	{
		return getField("posting_allowed").equals("y");
	}
	
	public boolean responsesAllowed()
	{
		return getField("responses_allowed").equals("y");
	}
	
	public boolean moderated()
	{
		return getField("moderated").equals("y");
	}
	
	public boolean routeable()
	{
		return getField("routeable").equals("y");
	}
	
	public static boolean isForum(JSOModel data)
	{
		return data.get("model").equals("ao.forum");
	}

	public ForumStatus getStatus()
	{
		return ForumStatus.getStatus(Integer.valueOf(getField("status")));
	}
	
	public String getNameFile()
	{
		return getField("name_file");
	}
	
	public String getSenderName()
	{
		return getField("sendername");
	}
	
	public String getAddMemberCredits()
	{
		return getField("add_member_credits");
	}
	
	public static boolean isGroupMetadata(JSOModel model)
	{
		return model.get("model").equals(METADATA_MODEL_TYPE);
	}
	
	public List<User> getResponders()
	{
		List<User> users = new ArrayList<User>();
		JsArray<JSOModel> arr = getObject("fields").getArray("responders");
		
		JSOModel m;
		for (int i=0; i<arr.length(); i++)
		{
			m = arr.get(i);
			users.add(new User(m));
		}
		return users;
	}
	
	public String getBackups()
	{
		return getField("backup_calls");
	}
	
	public int getMaxInputLength()
	{
		String len = getField("max_responder_len");
		if ("null".equals(len))
			// return default
			return 1;
		else
			return Integer.valueOf(len);
	}
	
}

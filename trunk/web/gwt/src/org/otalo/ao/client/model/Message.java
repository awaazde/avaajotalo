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

import org.otalo.ao.client.model.Forum.ForumStatus;


public class Message extends BaseModel {

	/* Order matters. The constants are mirrored in 
	 * server side code. The ordinal value of the first declared
	 * is 0 and then increases from there.
	 */
	public enum MessageStatus {
		PENDING(0), APPROVED(1), REJECTED(2),
		
		// this status is not a message status;
		// It is PURELY for display purposes on
		// forumwidget.setFolder()
		MANAGE(99);
		
		private int code;  
	  
    private MessageStatus(int code) {  
        this.code = code;  
    }  
  
    public int getCode() {  
        return code;  
    }  
    
    public static MessageStatus getStatus(int code) {
    	for (MessageStatus s : values())
    	{
    		if (s.getCode() == code)
    			return s;
    	}
    	
    	return null;
    }
	}
	
	public boolean read;
	
	public Message(JSOModel data) {
		super(data);
	}
	
	public String getDate()
	{
		return getObject("fields").get("date").replace("T", " ");
	}
	
	public User getAuthor()
	{
		return new User(getObject("fields").getObject("user"));
	}
	
	public String getContent()
	{
//	SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
//	return format.parse(dateStr);
		return getObject("fields").get("file");
	}
	
	public String getRgt()
	{
		return getObject("fields").get("rgt");
	}
	
	public String getLft()
	{
		return getObject("fields").get("lft");
	}
		
}

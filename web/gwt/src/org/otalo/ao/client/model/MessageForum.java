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

import java.text.DateFormat;
import java.util.Date;

import org.otalo.ao.client.model.Message.MessageStatus;

import com.google.gwt.i18n.client.DateTimeFormat;

public class MessageForum extends BaseModel {
	private Message m;
	private static final String MODEL_TYPE = "ao.message_forum";
	
	public MessageForum(JSOModel data) {
		super(data);
		
		m = new Message(getObject("fields").getObject("message"));
	}
	
	public MessageForum(BaseModel model)
	{
		this(model.getData());
	}

	public String getPosition()
	{
		return getObject("fields").get("position");
	}
	
	public MessageStatus getStatus()
	{
		return MessageStatus.getStatus(Integer.valueOf(getObject("fields").get("status")));
	}
	
	public boolean isResponse()
	{
		return Integer.valueOf(m.getLft()) > 1;
	}
	
	public Forum getForum()
	{
		return new Forum(getObject("fields").getObject("forum"));
	}
	
	/**
	 * Replicate the Message API here to make MessageForums more like messages
	 * @return
	 */
	public User getAuthor()
	{
		return m.getAuthor();
	}
	
	public String getDate()
	{
		return m.getDate();
	}
	
	public String getContent()
	{
		return m.getContent();
	}
	
	public String getLft()
	{
		return m.getLft();
	}
	
	public String getRgt()
	{
		return m.getRgt();
	}
	
	public static boolean isMessageForum(JSOModel data)
	{
		return data.get("model").equals(MODEL_TYPE);
	}
	
	public static boolean isMessageForum(BaseModel model)
	{
		return model != null && isMessageForum(model.getData());
	}
	
	/**
	 * Follow how it's generated in broadcast.py[thread]
	 * 
	 * "2012-03-02 16:13:54"
	 */
	public String getName()
	{
		DateTimeFormat df = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss");
		Date d = df.parse(getDate());
		String dString = DateTimeFormat.getFormat("MMM-dd-yyyy").format(d);
		User u = getAuthor();
		String username = u.getName().equals("null") ? u.getNumber() : u.getName();
		String nameStr = dString + "_" + username + "_" + getForum().getName() + "_(" + getId() + ")";
		
		return nameStr.substring(0,Math.min(nameStr.length(), 128));
	}
}

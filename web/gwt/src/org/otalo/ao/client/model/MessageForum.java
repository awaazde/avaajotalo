package org.otalo.ao.client.model;

import org.otalo.ao.client.model.Message.MessageStatus;

public class MessageForum extends BaseModel {
	private Message m;
	
	public MessageForum(JSOModel data) {
		super(data);
		
		m = new Message(getObject("fields").getObject("message"));
	}

	public String getPosition()
	{
		return getObject("fields").get("position");
	}
	
	public MessageStatus getStatus()
	{
		int statusCode = Integer.valueOf(getObject("fields").get("status"));
		
		if (statusCode == MessageStatus.PENDING.ordinal())
		{
			return MessageStatus.PENDING;
		}
		else if (statusCode == MessageStatus.APPROVED.ordinal())
		{
			return MessageStatus.APPROVED;
		}
		else if (statusCode == MessageStatus.REJECTED.ordinal())
		{
			return MessageStatus.REJECTED;
		}
		
		// This should never happen
		return null;
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
	 * Replicate the Message API hear to make MessageForums more like messages
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
}

package org.otalo.ao.client.model;

public class MessageResponder extends BaseModel {
	private User r;
	
	public MessageResponder(JSOModel data) {
		super(data);
		
		r = new User(getObject("fields").getObject("user"));
	}

	public User getResponder()
	{
		return r;
	}

	
}
